"""Zusagen rund um die Anschlussklemmen (Vertragsregel R1).

Warum diese Suite existiert. R1 ("Klemmenkoerper buendig zur
Platinenkante, Drahtoeffnung nach aussen") stand seit v2.1/Aufgabe B im
Vertrag, hatte aber keine Pruefung -- sie wurde beim Platzieren von Hand
befolgt. Bei den Lastklemmen der Dimmer ging das gut, bei der
Einspeiseklemme J90 auf allen vier Brettern und bei der Motorklemme J5
nicht: dort zeigte die Drahtoeffnung nach innen. Gefunden hat es ein
Mensch im 3D-Bild.

tools/pcb/klemmenprobe.py misst das jetzt an der gebauten Platine nach,
braucht dafuer aber pcbnew. Diese Suite prueft die beiden Stuecke, die
OHNE KiCad pruefbar sind und an denen der Fehler wirklich hing:

  1. Die Drehrechnung (stack_spec.KLEMME_OEFFNUNG_GLOBAL) -- die Stelle,
     an der man sich bei KiCads Achsenkonvention (y nach unten, Drehung
     gegen den Uhrzeigersinn) vertun kann.
  2. Die Vollstaendigkeit von KLEMME_OEFFNUNG -- jede Klemmenbauform,
     die eine Beschreibung wirklich verbaut, muss vermessen sein. Eine
     neue Bauform ohne Eintrag ist der Weg, auf dem genau dieser Fehler
     wiederkaeme.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "tools"))
sys.path.insert(0, os.path.join(HIER, "..", "tools", "pcb"))

import stack_spec as S   # noqa: E402

PT = "TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal"
MKDS = "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal"

fehler = []


def gleich(ist, soll, was):
    if tuple(round(v, 6) for v in ist) != tuple(round(v, 6) for v in soll):
        fehler.append("%s: %s statt %s" % (was, ist, soll))


# --- 1. Drehrechnung -------------------------------------------------
# Lokal zeigt die Oeffnung beider Bauformen auf +y (gemessen am
# STEP-Modell, s. Herleitung bei KLEMME_OEFFNUNG). In KiCads Aufsicht
# ist +y UNTEN. Drehung 180 muss sie also nach OBEN drehen -- das ist
# genau die Drehung, mit der J90 in Aufgabe D4 an die Oberkante kam.
gleich(S.KLEMME_OEFFNUNG_GLOBAL(PT, 0), (0.0, 1.0), "PT 0 Grad (unten)")
gleich(S.KLEMME_OEFFNUNG_GLOBAL(PT, 180), (0.0, -1.0), "PT 180 Grad (oben)")
gleich(S.KLEMME_OEFFNUNG_GLOBAL(PT, 90), (1.0, 0.0), "PT 90 Grad (rechts)")
gleich(S.KLEMME_OEFFNUNG_GLOBAL(PT, 270), (-1.0, 0.0), "PT 270 Grad (links)")
gleich(S.KLEMME_OEFFNUNG_GLOBAL(MKDS, 0), (0.0, 1.0), "MKDS 0 Grad (unten)")
gleich(S.KLEMME_OEFFNUNG_GLOBAL(MKDS, 180), (0.0, -1.0), "MKDS 180 Grad (oben)")

# Gespiegelt (Bestueckung auf der Rueckseite) wird ABGELEHNT, nicht
# geraten -- s. Herleitung in KLEMME_OEFFNUNG_GLOBAL. Kein Brett dieses
# Projekts hat eine solche Klemme.
try:
    S.KLEMME_OEFFNUNG_GLOBAL(PT, 90, True)
    fehler.append("gespiegelte Klemme wurde gerechnet statt abgelehnt -- "
                  "die Spiegelkonvention ist nie nachgemessen worden")
except NotImplementedError:
    pass

# Der voll qualifizierte Name (mit Bibliothek davor) muss genauso gehen
# -- klemmenprobe.py bekommt ihn von pcbnew in dieser Form.
gleich(S.KLEMME_OEFFNUNG_GLOBAL("TerminalBlock_Phoenix:" + PT, 180),
       (0.0, -1.0), "PT 180 mit Bibliotheksnamen")

# ROT-NACHWEIS: eine unvermessene Bauform muss knallen, nicht still
# durchgehen.
try:
    S.KLEMME_OEFFNUNG_GLOBAL("TerminalBlock_Irgendwas_Neu", 0)
    fehler.append("unvermessene Bauform ging still durch -- genau der "
                  "Weg, auf dem eine verdrehte Klemme wiederkaeme")
except KeyError:
    pass

# --- 2. Vollstaendigkeit --------------------------------------------
# Jede Klemmenbauform, die eine Beschreibung wirklich verbaut, ist
# vermessen. Geprueft gegen die FOOTPRINTS der echten Beschreibungen,
# nicht gegen eine von Hand gepflegte Liste.
import importlib   # noqa: E402

verbaut = {}
for modul in ("spec_motor", "spec_dimmer1", "spec_dimmer3", "spec_dimmer4"):
    b = importlib.import_module(modul)
    for ref, fp in getattr(b, "FOOTPRINTS", {}).items():
        if "TerminalBlock" in fp:
            verbaut.setdefault(fp.split(":")[-1], []).append(
                "%s.%s" % (modul, ref))

if not verbaut:
    fehler.append("keine einzige Klemmenbauform in den Beschreibungen "
                  "gefunden -- der Filter greift nicht mehr")
for fp, wo in sorted(verbaut.items()):
    if fp not in S.KLEMME_OEFFNUNG:
        fehler.append("Bauform %s (verbaut als %s) fehlt in "
                      "KLEMME_OEFFNUNG -- Oeffnungsrichtung ungemessen"
                      % (fp, ", ".join(wo)))

# --- 3. Die Zusagen selbst sind plausibel ---------------------------
for fp, v in S.KLEMME_OEFFNUNG.items():
    if round(v[0] ** 2 + v[1] ** 2, 6) != 1.0:
        fehler.append("%s: Oeffnungsvektor %s ist kein Einheitsvektor"
                      % (fp, v))
if not 0.0 <= S.KLEMME_KANTENABSTAND_MAX <= 0.5:
    fehler.append("KLEMME_KANTENABSTAND_MAX %.2f mm -- ueber 0,5 mm waere "
                  "keine Bauteiltoleranz mehr, sondern die stille "
                  "Erlaubnis, Klemmen nach innen zu ruecken"
                  % S.KLEMME_KANTENABSTAND_MAX)

if fehler:
    print("FEHLER:")
    for f in fehler:
        print("  -", f)
    raise SystemExit(1)
print("Klemmen: %d Bauformen vermessen, %d verbaut, Drehrechnung und "
      "Vollstaendigkeit gruen" % (len(S.KLEMME_OEFFNUNG), len(verbaut)))

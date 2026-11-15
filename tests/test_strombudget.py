"""Haelt das Strombudget der 24-V-Verteilung KiCad-frei fest.

Warum es diesen Test gibt (Aufgabe D3, v2.1). Das eigentliche Gate,
`tools/pcb/strombelastung.py`, braucht `pcbnew` und laeuft deshalb nur
ueber `tools/pcb/kipy` -- genau wie masseheiler.py, steckerprobe.py und
pcb_checks.py. Eine Pruefung, die man von Hand aufrufen muss, wird
irgendwann vergessen; die drei anderen sind deshalb in CONTRIBUTING.md
und README.md als Pflichtschritte beschrieben. Dieser Test sichert
DREIERLEI ab, was ohne KiCad pruefbar ist:

1. **Die Zusage selbst rechnet auf.** stack_spec.STROMBUDGET behauptet
   4,0 A je Modul. Der Test rechnet das Q90-Limit aus den ebenfalls im
   Vertrag stehenden Datenblattzahlen NEU aus (nicht aus
   strombelastung.py importiert -- eine zweite Implementierung, damit
   ein Fehler dort hier nicht mitwandert) und verlangt echte Reserve.
2. **Die Netzklassen passen zur Zusage.** In jeder committeten
   .kicad_pro muss /PWR_IN und /+24V die Stamm-Klasse tragen, und deren
   Bahnbreite muss den zugesagten Strom nach IPC-2221 wirklich fuehren.
   Genau hier lag der v2-Fehler: die Zusage stand nirgends, und die
   Netzklasse war die eines einzelnen Kanals.
3. **Das Gate bleibt im Ablauf verankert.** Wer strombelastung.py aus
   der dokumentierten Gate-Kette streicht, macht diesen Test rot.

Und ein ROT-Nachweis: dieselbe Rechnung wird gegen die frueheren
Annahmen (9 A / 12 A Summenstrom, 1,00 mm Stammbreite) laufen gelassen
und MUSS durchfallen -- sonst prueft sie nichts.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(WURZEL, "tools"))
sys.path.insert(0, os.path.join(WURZEL, "tools", "pcb"))

import fertigung
import stack_spec as S

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- Eigene, unabhaengige IPC-2221-Rechnung -------------------------
# Bewusst hier noch einmal ausgeschrieben statt aus strombelastung.py
# importiert: ein Vorzeichen- oder Exponentenfehler dort wuerde sonst in
# beiden Haelften stehen und sich gegenseitig bestaetigen.
def breite_fuer(strom_a, dt_k=20.0, dicke_mm=0.035):
    flaeche_mil2 = (strom_a / (0.048 * dt_k ** 0.44)) ** (1.0 / 0.725)
    return flaeche_mil2 / (dicke_mm / 0.0254) * 0.0254


def strom_bei(breite_mm, dt_k=20.0, dicke_mm=0.035):
    flaeche_mil2 = (breite_mm / 0.0254) * (dicke_mm / 0.0254)
    return 0.048 * dt_k ** 0.44 * flaeche_mil2 ** 0.725


# Eichpunkt gegen die veroeffentlichte Tabelle (KiCadRoutingTools
# docs/power-nets.md, Zeile "2-5A", Spalte "1oz Cu, 20C rise": 0,75 mm):
check("IPC-2221-Rechnung geeicht (0,75 mm traegt 2,5-2,7 A)",
      2.5 < strom_bei(0.75) < 2.8, True)

B = S.STROMBUDGET

# --- 1. Die Zusage rechnet gegen die Bauteile auf -------------------
q90_max = (B["q90_verlust_max_w"] / B["q90_rdson_ohm"]) ** 0.5
check("Q90-Grenzstrom 6,12 A (AOD409)", round(q90_max, 2), 6.12)
check("Modulbudget unter dem Q90-Grenzstrom",
      B["modul_gesamt_a"] < q90_max, True)
# Echte Reserve, keine Punktlandung: hoechstens 75 % der belegten
# Verlustleistung duerfen im Dauerbetrieb anfallen.
q90_verlust = B["q90_rdson_ohm"] * B["modul_gesamt_a"] ** 2
check("Q90-Verlust <= 75 % des Datenblattwerts",
      q90_verlust <= 0.75 * B["q90_verlust_max_w"], True)
# v3: AOD409 (40 mOhm) statt IRFR5305 (65 mOhm): 0,04 x 16 = 0,64 W.
check("Q90-Verlust bei Budget = 0,64 W", round(q90_verlust, 2), 0.64)

# Stapel-Durchleitung: hoechstens so viel, wie EIN Kontakt des
# Leistungssteckers allein traegt (s. Vertragskommentar: die
# 6-A-Parallelsumme ist dort selbst als nicht herstellerbelegt markiert).
check("Stapel-Durchleitung <= Einzelkontakt-Nennstrom",
      B["stapel_durchleitung_a"] <= S.STECKER_LEISTUNG["strom_pro_kontakt_a"],
      True)
check("Einspeiseklemme nicht der Engpass",
      B["klemme_a"] > B["modul_gesamt_a"], True)
# Der Kanalstrom bleibt der zugesagte -- gesenkt wurde die SUMME, nicht
# der einzelne Kanal.
check("Kanalstrom unveraendert 3,0 A", B["kanal_a"], 3.0)
check("Motorstrom unveraendert (DRV8876-Choppinglimit)",
      B["motor_a"], 2.538)
check("ein einzelner Kanal passt ins Modulbudget",
      B["kanal_a"] < B["modul_gesamt_a"], True)
# Die ehrliche Konsequenz, die auf dem Druck stehen muss: vier Kanaele
# gleichzeitig mit vollem Strom gehen NICHT.
check("vier Kanaele x Kanalstrom sprengen das Budget",
      4 * B["kanal_a"] > B["modul_gesamt_a"], True)

# --- 2. Fertigungsbreiten tragen die zugesagten Stroeme --------------
check("Stammbreite traegt das Modulbudget",
      strom_bei(fertigung.TRACK_STAMM) >= B["modul_gesamt_a"], True)
check("Leistungsbreite traegt einen Kanal",
      strom_bei(fertigung.TRACK_POWER) >= B["kanal_a"], True)
check("Leistungsbreite traegt den Motorstrom",
      strom_bei(fertigung.TRACK_POWER) >= B["motor_a"], True)
check("Signalbreite traegt den 5-V-Reglerstrom (1,0 A)",
      strom_bei(fertigung.TRACK_SIGNAL) >= 1.0, True)
# ROT-NACHWEIS: genau das, was v2 angenommen hat, muss durchfallen.
check("ROT-Nachweis: 1,00 mm traegt das Modulbudget NICHT",
      strom_bei(fertigung.TRACK_POWER) < B["modul_gesamt_a"], True)
check("ROT-Nachweis: 12 A brauchen mehr als 6 mm",
      breite_fuer(12.0) > 6.0, True)
check("ROT-Nachweis: 9 A brauchen mehr als 4 mm",
      breite_fuer(9.0) > 4.0, True)

# --- 3. Die committeten Projekte tragen diese Klassen ----------------
BRETTER = {
    "dimmer1/Dimmer1": ("/LED1",),
    "dimmer3/Dimmer3": ("/LED1", "/LED2", "/LED3"),
    "dimmer4/Dimmer4": ("/LED1", "/LED2", "/LED3", "/LED4"),
}
for brett, leistungsnetze in sorted(BRETTER.items()):
    pro = os.path.join(WURZEL, "hardware", "kicad", brett + ".kicad_pro")
    d = json.load(open(pro, encoding="utf-8"))
    klassen = {c["name"]: c for c in d["net_settings"]["classes"]}
    muster = {m["pattern"]: m["netclass"]
              for m in d["net_settings"]["netclass_patterns"]}
    check("%s hat eine Stamm-Netzklasse" % brett, "Stamm" in klassen, True)
    if "Stamm" in klassen:
        check("%s Stammbreite = fertigung.TRACK_STAMM" % brett,
              klassen["Stamm"]["track_width"], fertigung.TRACK_STAMM)
        check("%s Stammklasse traegt das Modulbudget" % brett,
              strom_bei(klassen["Stamm"]["track_width"]) >= B["modul_gesamt_a"],
              True)
    for netz in S.STROMBUDGET["stamm_netze"]:
        check("%s: %s ist Stamm" % (brett, netz), muster.get(netz), "Stamm")
    for netz in leistungsnetze:
        check("%s: %s ist Leistung" % (brett, netz), muster.get(netz),
              "Leistung")
    if "Leistung" in klassen:
        check("%s Leistungsklasse traegt einen Kanal/Motorausgang" % brett,
              strom_bei(klassen["Leistung"]["track_width"])
              >= max(B["kanal_a"], B["motor_a"]), True)

# --- 4. Das Gate bleibt im dokumentierten Ablauf ---------------------
# Wer strombelastung.py aus der Gate-Kette streicht, macht diesen Test
# rot -- das ist die einzige Verankerung, die ohne KiCad moeglich ist.
for datei in ("CONTRIBUTING.md", "README.md"):
    text = open(os.path.join(WURZEL, datei), encoding="utf-8").read()
    check("%s nennt strombelastung.py" % datei,
          "strombelastung.py" in text, True)
    check("%s nennt masseheiler.py (Gegenprobe)" % datei,
          "masseheiler.py" in text, True)

# --- 5. Das Gate selbst laesst sich ohne KiCad wenigstens LESEN ------
# Kein Import (pcbnew fehlt hier), aber die Zahlen, die es benutzt,
# duerfen nicht heimlich ein zweites Mal im Quelltext stehen.
gate = open(os.path.join(WURZEL, "tools", "pcb", "strombelastung.py"),
            encoding="utf-8").read()
check("Gate liest das Budget aus dem Vertrag",
      "S.STROMBUDGET" in gate, True)
check("Gate traegt das Budget nicht als eigene Zahl",
      "modul_gesamt_a\"] = " not in gate, True)
check("Gate rechnet Vias als Leiter mit",
      "via_ersatzbreite" in gate, True)

if fails:
    print("\n".join(fails))
    raise SystemExit("ROT: %d Pruefung(en)" % len(fails))
print("Strombudget gruen: %.1f A je Modul (Q90-Grenze %.2f A, "
      "Verlust %.2f W von %.1f W), %.1f A Stapel-Durchleitung, "
      "%.1f A je Kanal; Stamm %.2f mm traegt %.2f A"
      % (B["modul_gesamt_a"], q90_max, q90_verlust, B["q90_verlust_max_w"],
         B["stapel_durchleitung_a"], B["kanal_a"],
         fertigung.TRACK_STAMM, strom_bei(fertigung.TRACK_STAMM)))

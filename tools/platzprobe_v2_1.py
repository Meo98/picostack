"""Platzprobe fuer PicoStack v2.1: waechst ein bedienbares Layout aus 75x65?

WARUM DIESES SKRIPT (Aufgabe A, docs/superpowers/plans/
2026-09-10-picostack-v2-1-layout.md). Das Audit
(.superpowers/sdd/2026-09-07-picostack-v2/audit-layout-v2.md) fand einen
Blocker (B1: die Kanal-1-/Motor-Klemme sitzt im PICO_SCHATTEN, weil dort
schlicht kein anderer Platz mehr war) und mehrere Wichtig-Befunde (K3: nur
1,14 mm Luft zwischen J8 und dem Leistungsstecker; K4: die Randpads
liegen auf B.Cu und sind im Stapel nur am obersten Modul erreichbar). Der
Kern aller drei: das v2-Mass 75x65 hat keine Reserve fuer eine
kantenbuendige Klemmenreihe UND eine erreichbare Randpad-Zone gleich-
zeitig -- beide muessen NEU RESERVIERT werden, nicht nur umsortiert.

BINDENDER RAHMEN (vom Auftraggeber/Controller entschieden, hier nicht neu
verhandelt):
  1. STECKER_POS (stapel_links/rechts, kette, leistung), PIN_ROLLE,
     M3_HOLES und LANDEPUNKTE_VERDREHT behalten ihre HEUTIGEN Koordinaten
     -- nur der Umriss waechst. Das heisst: der Koordinatenursprung
     (0|0 = heutige linke obere Ecke) bleibt stehen, das Rechteck wird
     NUR nach rechts (+x) und nach unten (+y) groesser. Waechst der
     Umriss stattdessen nach links oder oben, muessten alle frozen
     Koordinaten um den Zuwachs verschoben werden -- genau das verbietet
     Punkt 1. Folge: neue Flaeche entsteht ausschliesslich als Streifen
     rechts von x=75 und unterhalb von y=65; das ist auch der Grund,
     warum dieses Skript (anders als platzprobe_v2.py) keine "links"-
     Kandidaten rechnet, obwohl "links" laut Aufgabenzettel geometrisch
     ebenfalls ein freier Streifen waere (der Pico sitzt bei x=29..50,
     Rest links davon ist bereits mit Kette/Nest/Notaus belegt UND
     duerfte wegen Punkt 1 ohnehin nicht wachsen, ohne alles zu
     verschieben).
  2. Klemmen an einer Plattenkante, Koerper buendig, Drahtoeffnung nach
     aussen; kein Klemmenhof schneidet PICO_SCHATTEN (R1).
  3. Alle Lastklemmen EINES Moduls in EINER Reihe auf EINER Kante, in
     Kanalreihenfolge (R2) -- Dimmer4 vier Klemmen, das Motormodul eine
     Klemme (J5) plus den 4-poligen Notaus-Stecker J3.
  4. Randpads wandern auf F.Cu, in eine Zone, die KEIN Landepunkt aus
     LANDEPUNKTE_VERDREHT() erreicht -- die 1,5-mm-Klausel (LANDE_
     SPERRRADIUS) bleibt ohne Ausnahmeliste erfuellbar.
  5. Kupfer >= 2,0 mm von der Plattenkante (R5) -- schaerfer als das
     bisherige EDGE_CLEARANCE=0,5 mm im Vertrag.

WARUM RECHTS+UNTEN UND NICHT AUCH LINKS. Die drei zu loesenden Befunde
(B1, K3, K4) liegen alle unten/rechts (Motor-Klemme in der Stapelluecke
Richtung unten, J8 unten rechts neben dem Leistungsstecker, Randpads am
unteren Rand). Links (x<27) ist im Audit an keiner Stelle als eng
bemaengelt -- dort sitzen Kette, MCU-Nest und (beim Motormodul) die
Notaus-Kette bereits kompakt und unauffaellig. Zusaetzliche Flaeche dort
haette keinen der drei Befunde adressiert und waere nur Ballast.

WIE GERECHNET WIRD. Wie in platzprobe_v2.py: jede Pflichtflaeche ist ein
achsenparalleles Rechteck. Die VIER schon bestehenden Pflichtflaechen
(Pico-Zone, Stecker-Zone, Versorgungszelle) werden UNVERAENDERT aus
platzprobe_v2.py uebernommen -- ihre Herleitung aendert sich mit v2.1
nicht, nur ZWEI NEUE Pflichtflaechen kommen hinzu (Klemmenzone,
Randpad-Zone) und wandern in den neu gewachsenen Rand. Kandidaten sind
Zuwaechse (delta_rechts, delta_unten) auf die heutigen 75x65 mm; fuer
jeden wird sowohl die GEOMETRIE (passt die Klemmenzone neben die
M3-Eckloecher? bleibt die Randpad-Zone 1,5 mm von jedem Landepunkt UND
2,0 mm von der neuen Kante weg?) als auch die FLAECHE (reicht der Rest
fuer die Elektronik-Nutzlast?) geprueft.

Rein aus Python, ohne KiCad-Import -- lauffaehig als
`python3 tools/platzprobe_v2_1.py`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "pcb")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S                       # noqa: E402
import spec_motor as MOTOR                   # noqa: E402
from spec_dimmer_basis import beschreibung   # noqa: E402

DIMMER4 = beschreibung(4)

BOARD_W0 = S.BOARD_W   # 75.0 -- heutiges v2-Mass, Ausgangspunkt des Wachstums
BOARD_H0 = S.BOARD_H   # 65.0


def _mass(flaeche):
    x0, y0, x1, y1 = flaeche
    return (round(x1 - x0, 3), round(y1 - y0, 3))


# === 1. Unveraendert aus platzprobe_v2.py uebernommene Pflichtflaechen ==
# Diese drei Zonen aendern sich mit v2.1 NICHT (der Auftrag verlangt nur
# Klemmenreihe + Randpad-Zone neu, s. Modul-Docstring) -- hier nur
# zitiert, damit die Flaechenbilanz unten vollstaendig ist.

PICO_REIHE_L = 50.8
PICO_REIHE_B = 5.1
PICO_REIHE_ABSTAND = 17.78
PICO_SCHATTEN_L, PICO_SCHATTEN_B = _mass(S.PICO_SCHATTEN)   # 21.0 x 51.0

PICO_ZONE_L = max(PICO_REIHE_L, PICO_SCHATTEN_L)
PICO_ZONE_B = max(PICO_SCHATTEN_B, PICO_REIHE_ABSTAND + PICO_REIHE_B)
PICO_ZONE_FLAECHE = round(PICO_ZONE_L * PICO_ZONE_B, 3)

_LEISTUNG_L, _LEISTUNG_B = _mass(S.STECKER_POS["leistung"]["flaeche"])
_KETTE_L, _KETTE_B = _mass(S.STECKER_POS["kette"]["flaeche"])
STECKER_ZONE_L = round(_LEISTUNG_L + 2 * _KETTE_L, 3)
STECKER_ZONE_B = max(_LEISTUNG_B, _KETTE_B)
STECKER_ZONE_FLAECHE = round(STECKER_ZONE_L * STECKER_ZONE_B, 3)

ZELLE_TEILE = {
    "Klemme": (8.0, 8.6), "Q-Schutz": (11.1, 7.0), "TVS": (9.8, 6.7),
    "Regler SIP-3": (10.0, 10.0), "Schottky": (9.8, 6.7), "Elko": (8.5, 8.5),
}
ZELLE_ZONE_L = round(sum(w for w, h in ZELLE_TEILE.values()), 3)
ZELLE_ZONE_B = max(h for w, h in ZELLE_TEILE.values())
ZELLE_ZONE_FLAECHE = round(ZELLE_ZONE_L * ZELLE_ZONE_B, 3)

M3_KEEPOUT = S.M3_KEEPOUT                 # 7,0 mm (Vertrag, unveraendert)
M3_ANZAHL = 4
M3_FLAECHE = round(M3_ANZAHL * M3_KEEPOUT * M3_KEEPOUT, 3)
M3_HALB = M3_KEEPOUT / 2.0                # 3,5 mm -- Reichweite je Seite
                                          # der Bohrmitte

# === 2. NEU: Klemmenzone (R1/R2/R4) ====================================
# Die Zone muss BEIDE Extremfaelle gleichzeitig fassen, weil sie EIN
# Rechteck im Vertrag ist, das jedes Modul unterschiedlich weit nutzt:
#   - Dimmer4: vier Lastklemmen in einer Reihe, Kanal 1..4 (breiteste
#     Reihe).
#   - Motormodul: eine Motorklemme (J5, groesserer 5,08-mm-Typ, hoehere
#     Strombelastung) PLUS der 4-polige Notaus-Stecker J3 in derselben
#     Reihe (hoechste Einzelklemme).
# Klemmenabstand R4 (IEC 60664, s. Recherche Abschnitt 3): 0,8 mm bei
# 50 V ist der einzige BELEGTE Zahlenwert, den die Recherche fand; er
# gilt konservativ auch fuer die 6-30-V-Versorgung dieses Projekts
# (Kriechstrecke bei 30 V ist hoechstens so gross wie bei 50 V). Das ist
# GROESSER als der generische COURTYARD_GAP von 0,6 mm, den spec_motor.py
# fuer Bauteile ohne eigene Spannungsfestigkeits-Anforderung benutzt --
# hier zaehlt die schaerfere, spezifische Regel.
KF350_HOF_L, KF350_HOF_B = 8.0, 8.6     # J90/J5..J8 Dimmer: TerminalBlock_
                                        # Phoenix_PT-1,5-2-3.5-H (spec_
                                        # motor.FOOTPRINTS["J90"], echter
                                        # Hof aus PLACEMENT)
MOTOR_KLEMME_L, MOTOR_KLEMME_B = 11.17, 12.20   # J5 Motor: TerminalBlock_
                                        # Phoenix_MKDS-3-2-5.08 (spec_
                                        # motor.PLACEMENT["J5"])
NOTAUS_L, NOTAUS_B = 11.16, 3.54        # J3: FP_HDR_1X04, gedreht 90 Grad
                                        # (spec_motor.PLACEMENT["J3"];
                                        # w/h sind bereits die Hof-
                                        # Ausdehnung IN Platinenachsen,
                                        # Drehung eingerechnet)
R4_KLEMMENABSTAND_MM = 0.8               # IEC 60664, 50 V (Recherche Abs. 3)

DIMMER4_REIHE_L = round(4 * KF350_HOF_L + 3 * R4_KLEMMENABSTAND_MM, 3)
DIMMER4_REIHE_B = KF350_HOF_B
MOTOR_REIHE_L = round(MOTOR_KLEMME_L + R4_KLEMMENABSTAND_MM + NOTAUS_L, 3)
MOTOR_REIHE_B = max(MOTOR_KLEMME_B, NOTAUS_B)

KLEMMENZONE_L = round(max(DIMMER4_REIHE_L, MOTOR_REIHE_L), 3)
KLEMMENZONE_B = round(max(DIMMER4_REIHE_B, MOTOR_REIHE_B), 3)
KLEMMENZONE_FLAECHE = round(KLEMMENZONE_L * KLEMMENZONE_B, 3)

# === 3. NEU: Randpad-Zone auf F.Cu (R4 Vertragsregel, K4) ==============
# 22 Loecher (18 GPIO + 2x 3V3 + 2x GND, stack_spec.RANDPADS) im
# 2,54-mm-Raster -- dieselbe Laenge wie in platzprobe_v2.py, aber jetzt
# auf F.Cu statt B.Cu, deshalb NEU gegen LANDEPUNKTE_VERDREHT() und
# gegen die neue Plattenkante zu pruefen (das war auf B.Cu nicht noetig,
# s. stack_spec.py RULING 2026-09-09).
RAND_LOECHER = 18 + 4
RAND_RASTER = S.RAND_RASTER
RANDPAD_LAUF = round(RAND_LOECHER * RAND_RASTER, 3)     # 55,88 mm
RANDPAD_TIEFE = 4.0     # mm quer zur Reihe -- Pad (0,90 mm,
                        # stack_spec.RAND_PAD_B) plus Silk-Label-Platz,
                        # dieselbe Groessenordnung wie RAND_SILK_TIEFE in
                        # platzprobe_v2.py
RANDPAD_PUFFER = 0.6    # mm Abstand zur alten Kante x=75 (COURTYARD_GAP-
                        # Groessenordnung; x=75 traegt heute nichts, der
                        # Puffer ist reine Uebersicht, keine harte Not-
                        # wendigkeit)
R5_KANTENABSTAND_MM = 2.0     # neue, schaerfere Vertragsregel (statt des
                              # alten EDGE_CLEARANCE=0,5 mm)

RANDPAD_ZONE_FLAECHE = round(RANDPAD_LAUF * RANDPAD_TIEFE, 3)

# Minimaler Rechts-Zuwachs, damit die Randpad-Zone (Puffer + Tiefe) UND
# der Kantenabstand (R5) hinter der neuen Kante Platz haben:
DELTA_RECHTS_MIN = round(
    RANDPAD_PUFFER + RANDPAD_TIEFE + R5_KANTENABSTAND_MM, 3)
# Minimaler Unten-Zuwachs: die Klemmenzone braucht ihre eigene Tiefe an
# der neuen Kante (Koerper buendig, R1 -- kein zusaetzlicher Puffer noetig,
# unterhalb y=65 liegt heute nichts).
DELTA_UNTEN_MIN = KLEMMENZONE_B


# === 4. Elektronik-Nutzlast: echte Hof-Summen aus den Spec-Dateien =====
# "Nutzlast" ist hier alles, was NICHT schon eine der obigen Zonen ist:
# die vier Vertragsstecker (Stapelreihen, Kette, Leistung), die
# Randpad-Bauteile (J95/J96 -- ihre Flaeche steht oben eigens als
# RANDPAD_ZONE_FLAECHE), die Versorgungszelle (J90/Q90/R90/R91/D90/D91/
# U90/C90/C91 -- steht oben als ZELLE_ZONE_FLAECHE) und die Lastklemmen
# selbst (J5/J6/J7/J8 bzw. J5+J3 -- stehen oben als KLEMMENZONE_FLAECHE)
# fallen aus der Summe heraus, sonst waere ihre Flaeche doppelt gezaehlt.
_CONN_REFS = {"J100", "J105", "J101", "J102", "J103", "J104"}
_RANDPAD_REFS = {"J95", "J96"}
_ZELLE_REFS = {"J90", "Q90", "R90", "R91", "D90", "D91", "U90", "C90", "C91"}
_TERM_MOTOR_REFS = {"J5", "J3"}
_TERM_DIMMER_REFS = {"J5", "J6", "J7", "J8"}


def _nutzlast(placement, klemmen_refs):
    ausgenommen = _CONN_REFS | _RANDPAD_REFS | _ZELLE_REFS | klemmen_refs
    return round(sum(p.w * p.h for ref, p in placement.items()
                     if ref not in ausgenommen), 4)


MOTOR_NUTZLAST = _nutzlast(MOTOR.PLACEMENT, _TERM_MOTOR_REFS)
DIMMER4_NUTZLAST = _nutzlast(DIMMER4["PLACEMENT"], _TERM_DIMMER_REFS)
NUTZLAST_WORST = max(MOTOR_NUTZLAST, DIMMER4_NUTZLAST)

PACKUNGS_RESERVE = 1.25    # dieselbe konservative Konstante wie in
                          # platzprobe_v2.py (Herleitung dort:
                          # BELEGUNGSGRAD_ERPROBT = 0,566 -> Faktor
                          # 1/0,566 = 1,77; 1,25 ist der kleinere,
                          # vorsichtigere Wert, weil dies nur die grobe
                          # Vorauswahl trifft)
NUTZLAST_BEDARF = round(NUTZLAST_WORST * PACKUNGS_RESERVE, 4)

MANDATORY_SUMME = round(
    PICO_ZONE_FLAECHE + STECKER_ZONE_FLAECHE + ZELLE_ZONE_FLAECHE
    + KLEMMENZONE_FLAECHE + RANDPAD_ZONE_FLAECHE, 3)


# === 5. Kandidaten: Zuwachs rechts + unten auf 75x65 ====================
KANDIDATEN = ((5.0, 10.0), (10.0, 15.0), (15.0, 20.0))


def _landepunkt_min_abstand(x0, x1, y0, y1):
    """Kleinster Abstand irgendeines der 46 Landepunkte zum Rechteck."""
    beste = None
    for px, py in S.LANDEPUNKTE_VERDREHT():
        dx = max(x0 - px, 0.0, px - x1)
        dy = max(y0 - py, 0.0, py - y1)
        d = (dx * dx + dy * dy) ** 0.5
        if beste is None or d < beste:
            beste = d
    return round(beste, 3)


def pruefe(delta_rechts, delta_unten):
    w = round(BOARD_W0 + delta_rechts, 3)
    h = round(BOARD_H0 + delta_unten, 3)

    # -- Randpad-Zone: rechter Streifen, mittig in y auf der vollen
    # neuen Hoehe platziert (nichts anderes steht dort, s. Docstring).
    rp_x0 = round(BOARD_W0 + RANDPAD_PUFFER, 3)
    rp_x1 = round(rp_x0 + RANDPAD_TIEFE, 3)
    rp_y0 = round((h - RANDPAD_LAUF) / 2.0, 3)
    rp_y1 = round(rp_y0 + RANDPAD_LAUF, 3)
    rp_kante_frei = round(w - rp_x1, 3)
    rp_kante_ok = rp_kante_frei >= R5_KANTENABSTAND_MM
    rp_landeabstand = _landepunkt_min_abstand(rp_x0, rp_x1, rp_y0, rp_y1)
    rp_lande_ok = rp_landeabstand >= S.LANDE_SPERRRADIUS
    rp_y_ok = rp_y0 >= 0.0 and rp_y1 <= h

    # -- Klemmenzone: unterer Streifen, mittig in x auf der ALTEN Breite
    # (75 mm) zentriert, damit sie unabhaengig vom Rechts-Zuwachs immer
    # mittig zwischen den beiden UNTEREN M3-Eckloechern liegt.
    kz_x0 = round((BOARD_W0 - KLEMMENZONE_L) / 2.0, 3)
    kz_x1 = round(kz_x0 + KLEMMENZONE_L, 3)
    kz_y1 = h
    kz_y0 = round(kz_y1 - KLEMMENZONE_B, 3)
    # M3-Eckloch-Freihaltequadrate (unveraendert bei x=4/x=71, y=61):
    m3_links_x1 = round(S.M3_HOLES[1][0] + M3_HALB, 3)      # (4,61) + 3,5
    m3_rechts_x0 = round(S.M3_HOLES[3][0] - M3_HALB, 3)     # (71,61) - 3,5
    kz_frei_links = round(kz_x0 - m3_links_x1, 3)
    kz_frei_rechts = round(m3_rechts_x0 - kz_x1, 3)
    kz_m3_ok = kz_frei_links >= 0.0 and kz_frei_rechts >= 0.0
    kz_y_ok = kz_y0 >= BOARD_H0    # darf die alte Platine nicht anschneiden

    geometrie_ok = rp_kante_ok and rp_lande_ok and rp_y_ok and kz_m3_ok and kz_y_ok

    flaeche = round(w * h, 3)
    frei = round(flaeche - MANDATORY_SUMME - M3_FLAECHE, 3)
    flaeche_reicht = frei >= NUTZLAST_BEDARF
    passt = geometrie_ok and flaeche_reicht

    return {
        "delta_rechts": delta_rechts, "delta_unten": delta_unten,
        "w": w, "h": h, "flaeche": flaeche, "frei": frei,
        "rp": (rp_x0, rp_y0, rp_x1, rp_y1), "rp_kante_frei": rp_kante_frei,
        "rp_kante_ok": rp_kante_ok, "rp_landeabstand": rp_landeabstand,
        "rp_lande_ok": rp_lande_ok, "rp_y_ok": rp_y_ok,
        "kz": (kz_x0, kz_y0, kz_x1, kz_y1),
        "kz_frei_links": kz_frei_links, "kz_frei_rechts": kz_frei_rechts,
        "kz_m3_ok": kz_m3_ok, "kz_y_ok": kz_y_ok,
        "geometrie_ok": geometrie_ok, "flaeche_reicht": flaeche_reicht,
        "passt": passt,
    }


def main():
    print("=== Unveraendert aus platzprobe_v2.py uebernommene Zonen ===")
    print("Pico-Zone           : %5.2f x %5.2f mm = %8.2f mm^2"
          % (PICO_ZONE_L, PICO_ZONE_B, PICO_ZONE_FLAECHE))
    print("Stecker-Zone        : %5.2f x %5.2f mm = %8.2f mm^2"
          % (STECKER_ZONE_L, STECKER_ZONE_B, STECKER_ZONE_FLAECHE))
    print("Versorgungszelle    : %5.2f x %5.2f mm = %8.2f mm^2"
          % (ZELLE_ZONE_L, ZELLE_ZONE_B, ZELLE_ZONE_FLAECHE))
    print("M3-Freihaltequadrate: 4 x %4.1f x %4.1f mm  = %8.2f mm^2"
          % (M3_KEEPOUT, M3_KEEPOUT, M3_FLAECHE))

    print()
    print("=== NEU: Klemmenzone (R1/R2/R4) ===")
    print("Dimmer4-Reihe (4x KF350 3,5mm): 4 x %.2f + 3 x %.2f = %.2f mm "
          "breit, %.2f mm tief"
          % (KF350_HOF_L, R4_KLEMMENABSTAND_MM, DIMMER4_REIHE_L,
             DIMMER4_REIHE_B))
    print("Motor-Reihe (J5 + Notaus J3)  : %.2f + %.2f + %.2f = %.2f mm "
          "breit, max(%.2f, %.2f) = %.2f mm tief"
          % (MOTOR_KLEMME_L, R4_KLEMMENABSTAND_MM, NOTAUS_L, MOTOR_REIHE_L,
             MOTOR_KLEMME_B, NOTAUS_B, MOTOR_REIHE_B))
    print("-> KLEMMENZONE = max(%.2f, %.2f) x max(%.2f, %.2f) = %.2f x "
          "%.2f mm = %.2f mm^2"
          % (DIMMER4_REIHE_L, MOTOR_REIHE_L, DIMMER4_REIHE_B, MOTOR_REIHE_B,
             KLEMMENZONE_L, KLEMMENZONE_B, KLEMMENZONE_FLAECHE))
    print("-> minimaler Zuwachs unten (delta_unten) = KLEMMENZONE-Tiefe "
          "= %.2f mm" % DELTA_UNTEN_MIN)

    print()
    print("=== NEU: Randpad-Zone auf F.Cu (R4-Vertragsregel/K4) ===")
    print("22 Loecher x %.2f mm Raster = %.2f mm Lauflaenge"
          % (RAND_RASTER, RANDPAD_LAUF))
    print("Zonentiefe %.2f mm + Puffer %.2f mm zur alten Kante + "
          "Kantenabstand R5 %.2f mm"
          % (RANDPAD_TIEFE, RANDPAD_PUFFER, R5_KANTENABSTAND_MM))
    print("-> minimaler Zuwachs rechts (delta_rechts) = %.2f + %.2f + "
          "%.2f = %.2f mm"
          % (RANDPAD_PUFFER, RANDPAD_TIEFE, R5_KANTENABSTAND_MM,
             DELTA_RECHTS_MIN))

    print()
    print("=== Elektronik-Nutzlast (echte Hof-Summen, Vertragsstecker/"
          "Zelle/Klemmen ausgenommen) ===")
    print("Motormodul-Rest   = %8.2f mm^2" % MOTOR_NUTZLAST)
    print("Dimmer4-Rest      = %8.2f mm^2  <- schlechtester Fall"
          % DIMMER4_NUTZLAST)
    print("-> mit Packungsreserve x%.2f = %8.2f mm^2"
          % (PACKUNGS_RESERVE, NUTZLAST_BEDARF))
    print("-> Pflichtflaechen-Summe (mit M3) = %8.2f mm^2"
          % (MANDATORY_SUMME + M3_FLAECHE))

    print()
    print("=== Kandidaten (delta_rechts, delta_unten auf 75x65) ===")
    ergebnisse = []
    for dr, db in KANDIDATEN:
        r = pruefe(dr, db)
        ergebnisse.append(r)
        print("delta_rechts=%.1f, delta_unten=%.1f -> %sx%s mm (%.0f mm^2)"
              % (dr, db, r["w"], r["h"], r["flaeche"]))
        rp_x0, rp_y0, rp_x1, rp_y1 = r["rp"]
        print("    Randpad-Zone (%.2f,%.2f)-(%.2f,%.2f): Kantenabstand "
              "%s - %s = %.2f mm (braucht >= %.1f) -> %s"
              % (rp_x0, rp_y0, rp_x1, rp_y1, r["w"], rp_x1,
                 r["rp_kante_frei"], R5_KANTENABSTAND_MM,
                 "ok" if r["rp_kante_ok"] else "R5 VERLETZT"))
        print("    Randpad-Zone Landepunkt-Mindestabstand = %.2f mm "
              "(braucht >= %.1f) -> %s"
              % (r["rp_landeabstand"], S.LANDE_SPERRRADIUS,
                 "ok" if r["rp_lande_ok"] else "1,5-mm-KLAUSEL VERLETZT"))
        print("    Randpad-Zone passt in y (%.2f..%.2f von 0..%.2f) -> %s"
              % (rp_y0, rp_y1, r["h"],
                 "ok" if r["rp_y_ok"] else "LAUFT UEBER DIE PLATTE"))
        kz_x0, kz_y0, kz_x1, kz_y1 = r["kz"]
        print("    Klemmenzone (%.2f,%.2f)-(%.2f,%.2f): Luft zum linken "
              "M3-Eckloch %.2f mm, zum rechten %.2f mm -> %s"
              % (kz_x0, kz_y0, kz_x1, kz_y1, r["kz_frei_links"],
                 r["kz_frei_rechts"],
                 "ok" if r["kz_m3_ok"] else "KOLLISION MIT M3-ECKE"))
        print("    Klemmenzone beginnt bei y=%.2f (>= altes BOARD_H "
              "%.2f) -> %s"
              % (kz_y0, BOARD_H0, "ok" if r["kz_y_ok"] else "SCHNEIDET DIE "
                 "ALTE PLATINE AN"))
        print("    Flaeche: frei = %.0f - %.2f - %.2f = %.2f mm^2, Bedarf "
              "%.2f mm^2 -> %s"
              % (r["flaeche"], MANDATORY_SUMME, M3_FLAECHE, r["frei"],
                 NUTZLAST_BEDARF,
                 "ok" if r["flaeche_reicht"] else "ZU KNAPP"))
        print("    => %s" % ("PASST" if r["passt"] else "nicht"))

    passende = [r for r in ergebnisse if r["passt"]]
    if not passende:
        print()
        print("KEIN Kandidat passt.")
        raise SystemExit(1)

    kleinster = min(passende, key=lambda r: r["flaeche"])
    print()
    print("EINHEITSMASS_V2_1: %dx%d" % (kleinster["w"], kleinster["h"]))

    print()
    print("=== Zonentabelle fuer den Vertrag (Aufgabe B) ===")
    kz_x0, kz_y0, kz_x1, kz_y1 = kleinster["kz"]
    rp_x0, rp_y0, rp_x1, rp_y1 = kleinster["rp"]
    print("BOARD_W = %.1f, BOARD_H = %.1f" % (kleinster["w"], kleinster["h"]))
    print("KLEMMENZONE  = (%.2f, %.2f, %.2f, %.2f)  # %.2f x %.2f mm, "
          "Kante unten, F.Silkscreen-Beschriftung je Klemme (R7)"
          % (kz_x0, kz_y0, kz_x1, kz_y1, KLEMMENZONE_L, KLEMMENZONE_B))
    print("RANDPAD_ZONE = (%.2f, %.2f, %.2f, %.2f)  # %.2f x %.2f mm, "
          "Kante rechts, F.Cu + F.Silkscreen (R8)"
          % (rp_x0, rp_y0, rp_x1, rp_y1, RANDPAD_TIEFE, RANDPAD_LAUF))
    print("PICO_SCHATTEN, ANTENNE_FREI, STECKER_POS, M3_HOLES: "
          "UNVERAENDERT aus dem v2-Vertrag (S. Modul-Docstring Punkt 1)")

    print()
    print("=== Rot-Nachweis gegen die Audit-Befunde ===")
    b1_frei = (kz_y0 >= S.PICO_SCHATTEN[3])
    print("B1 (Motor-/Kanal-1-Klemme im PICO_SCHATTEN): Klemmenzone "
          "beginnt bei y=%.2f, PICO_SCHATTEN endet bei y=%.2f -> %s"
          % (kz_y0, S.PICO_SCHATTEN[3],
             "GELOEST (Zone liegt vollstaendig ausserhalb)" if b1_frei
             else "NICHT geloest"))
    print("K1 (Q90 nur 0,10-0,20 mm zum M3-Freihaltequadrat): NICHT Teil "
          "dieser Aufgabe -- die Versorgungszelle bleibt unveraendert "
          "(s. Modul-Docstring). Der Zuwachs schafft dafuer keinen neuen "
          "Platz; das ist ein offener Punkt fuer Aufgabe C (Q90 innerhalb "
          "der bestehenden Zelle verschieben).")
    k3_abstand = round(kz_y0 - S.STECKER_POS["leistung"]["flaeche"][3], 2)
    print("K3 (J8 nur 1,14 mm zum Leistungsstecker): J8 zieht in die "
          "Klemmenzone (y=%.2f), Leistungsstecker endet bei y=%.2f -> "
          "Abstand jetzt %.2f mm -> %s"
          % (kz_y0, S.STECKER_POS["leistung"]["flaeche"][3], k3_abstand,
             "GELOEST" if k3_abstand > 1.14 else "NICHT verbessert"))
    print("K4 (Randpads nur am obersten Modul erreichbar, weil B.Cu): "
          "Randpad-Zone liegt jetzt auf F.Cu -> von der Oberseite jedes "
          "Moduls im Stapel erreichbar (STAPEL_ABSTAND=%.1f mm Luft zum "
          "Modul darueber), nicht nur am obersten -> GELOEST"
          % S.STAPEL_ABSTAND)


if __name__ == "__main__":
    main()

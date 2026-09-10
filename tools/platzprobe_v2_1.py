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

BINDENDER RAHMEN, KORRIGIERT (2026-09-10, Ruling des Controllers nach der
ersten Fassung dieses Skripts). Die erste Fassung fror M3_HOLES UND
LANDEPUNKTE_VERDREHT auf ihren heutigen ABSOLUTEN Koordinaten ein (Rechnung
"stapelkompatibel mit v2"). Das wurde zurueckgenommen: es existiert kein
gefertigtes v2-Board, gegen das echte Stapelkompatibilitaet noetig waere --
der Preis (Klemmenzone musste unterhalb der eingefrorenen Bohrung bei
y=61 ausweichen, trieb EINHEITSMASS_V2_1 auf 85x80) war real, der Nutzen
nicht. Jetzt gilt:

  1. STECKER_POS (stapel_links/rechts, kette, leistung) und PIN_ROLLE
     bleiben eingefroren -- das ist der eigentliche Stapelvertrag: alle
     Module im Stapel muessen ihre Stecker deckungsgleich haben, egal wie
     gross ihr Umriss ist. Der Koordinatenursprung (0|0 = heutige linke
     obere Ecke) bleibt stehen; das Rechteck waechst NUR nach rechts (+x)
     und nach unten (+y).
  2. M3_HOLES WANDERN mit dem Umriss: dieselbe Herleitung wie in v1/v2
     (stack_spec.py, Kommentar bei M3_HOLES: "4,0 mm Abstand von JEDER
     Kante", nicht von der Mitte) wird auf das NEUE Mass angewendet --
     M3_HOLES(w,h) = [(4,4), (4,h-4), (w-4,4), (w-4,h-4)]. Bei w=75,h=65
     reproduziert das exakt die heutigen vier Loecher; das ist der
     Rot-Nachweis, dass diese Funktion die alte Herleitung nur verallgemeinert,
     nicht ersetzt.
  3. LANDEPUNKTE_VERDREHT folgt zwangslaeufig aus 1+2: die Funktion in
     stack_spec.py spiegelt jeden Steckerkontakt an (BOARD_W, BOARD_H)
     -- `(round(BOARD_W - x, 3), round(BOARD_H - y, 3))`. Weil STECKER_POS
     (Punkt 1) fest bleibt, aber BOARD_W/H wachsen, WANDERN alle 46
     Landepunkte um genau (delta_rechts, delta_unten) nach aussen -- eine
     reine Verschiebung, keine Verzerrung (nachgerechnet in `_landepunkte_
     fuer()` unten, das dieselbe PAD_LAGEN-Funktion wie stack_spec.py
     benutzt, nicht die eingefrorene S.LANDEPUNKTE_VERDREHT()).
  4. Klemmen an einer Plattenkante, Koerper buendig, Drahtoeffnung nach
     aussen; kein Klemmenhof schneidet PICO_SCHATTEN (R1).
  5. Alle Lastklemmen EINES Moduls in EINER Reihe auf EINER Kante, in
     Kanalreihenfolge (R2).
  6. Randpads auf F.Cu, in einer Zone, die KEIN Landepunkt erreicht (die
     1,5-mm-Klausel bleibt ohne Ausnahmeliste erfuellbar) UND die keinen
     der (jetzt mitwachsenden) M3-Freihaltebereiche schneidet.
  7. Kupfer >= 2,0 mm von der Plattenkante (R5).

WAS SICH DADURCH AENDERT (der eigentliche Kern dieser Neufassung). Die
Randpad-Zone sitzt rechts, nahe der neuen Kante -- und GENAU DORT sitzen
jetzt auch die beiden rechten M3-Loecher (sie wandern ja mit, immer 4 mm
von der aktuellen rechten Kante). In der ERSTEN Fassung war das kein
Thema: das eingefrorene M3-Loch blieb bei x=71, weit hinter jeder
plausiblen Randpad-Zone. Jetzt ueberlappen sich Randpad-Zone und
M3-Freihaltequadrat in x fast zwangslaeufig (beide sitzen nah an der
Kante) -- die Trennung muss also ueber Y laufen: die Randpad-Zone muss
zwischen dem oberen und dem unteren rechten M3-Freihaltequadrat
hindurchpassen. Das treibt jetzt delta_unten (nicht mehr die
Klemmenzone!), s. Abschnitt 3 unten.

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
M3_RAND_ABSTAND = 4.0  # mm von jeder Kante -- dieselbe v1/v2-Herleitung
                       # (stack_spec.py, Kommentar bei M3_HOLES), jetzt als
                       # Funktion statt als vier feste Zahlen.


def _mass(flaeche):
    x0, y0, x1, y1 = flaeche
    return (round(x1 - x0, 3), round(y1 - y0, 3))


def m3_holes_fuer(w, h):
    """M3-Eckloecher fuer einen wxh-Umriss, 4,0 mm von jeder Kante.

    Rot-Nachweis der Herleitung: m3_holes_fuer(75, 65) muss exakt
    stack_spec.M3_HOLES reproduzieren (s. test unten in main()).
    """
    a = M3_RAND_ABSTAND
    return [(a, a), (a, h - a), (w - a, a), (w - a, h - a)]


def landepunkte_fuer(w, h):
    """LANDEPUNKTE_VERDREHT fuer einen wxh-Umriss.

    Identische Herleitung wie stack_spec.LANDEPUNKTE_VERDREHT() -- dort an
    das MODUL-globale BOARD_W/H gebunden (fest 75/65), hier parametrisiert,
    weil die Platzprobe mehrere Kandidatengroessen durchrechnen muss.
    STECKER_POS/PAD_LAGEN kommen unveraendert aus dem Vertrag (Punkt 1
    oben, frozen).
    """
    aus = []
    for eintrag in S.STECKER_POS.values():
        lagen = S.PAD_LAGEN(eintrag["footprints"][0], eintrag["pin1"],
                             eintrag["drehung"])
        for x, y in lagen.values():
            aus.append((round(w - x, 3), round(h - y, 3)))
    return tuple(aus)


# === 1. Unveraendert aus platzprobe_v2.py uebernommene Pflichtflaechen ==
# Diese drei Zonen aendern sich mit v2.1 NICHT (der Auftrag verlangt nur
# Klemmenreihe + Randpad-Zone neu) -- hier nur zitiert, damit die
# Flaechenbilanz unten vollstaendig ist.

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

STAPEL_BODEN = S.STECKER_POS["stapel_links"]["flaeche"][3]   # 52,3 mm --
# tiefster Punkt EINGEFRORENER Vertragsgeometrie (beide Stapelreihen enden
# hier, s. STECKER_POS-Kommentar "beide Hoefe belegen denselben
# Y-Bereich"). Das ist jetzt die massgebliche untere Grenze fuer alles,
# was ueber der Klemmenzone noch Platz braucht -- NICHT mehr "das alte
# BOARD_H0", das war in der ersten Fassung eine eigene, zu vorsichtige
# Annahme (s. Modul-Docstring).
GENERISCHER_ABSTAND = 0.6   # mm, COURTYARD_GAP-Groessenordnung, ueberall
                            # dort verwendet, wo kein spezifischerer Wert
                            # (R4/R5) bindet.

# === 2. Klemmenzone (R1/R2/R4) -- unveraendert gegenueber der ersten
# Fassung, die M3-Beweglichkeit aendert an DIESER Herleitung nichts (die
# Klemmenzone haengt an KLEMMENTYPEN, nicht an M3-Lage) =================
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
                                          # -- schaerfer als das generische
                                          # COURTYARD_GAP (0,6 mm); Aufgabe
                                          # C muss diesen Wert benutzen,
                                          # nicht auf COURTYARD_GAP
                                          # zurueckfallen.

DIMMER4_REIHE_L = round(4 * KF350_HOF_L + 3 * R4_KLEMMENABSTAND_MM, 3)
DIMMER4_REIHE_B = KF350_HOF_B
MOTOR_REIHE_L = round(MOTOR_KLEMME_L + R4_KLEMMENABSTAND_MM + NOTAUS_L, 3)
MOTOR_REIHE_B = max(MOTOR_KLEMME_B, NOTAUS_B)

KLEMMENZONE_L = round(max(DIMMER4_REIHE_L, MOTOR_REIHE_L), 3)
KLEMMENZONE_B = round(max(DIMMER4_REIHE_B, MOTOR_REIHE_B), 3)
KLEMMENZONE_FLAECHE = round(KLEMMENZONE_L * KLEMMENZONE_B, 3)

# === 3. Randpad-Zone auf F.Cu (R6-Vertragsregel/K4) --------------------
RAND_LOECHER = 18 + 4
RAND_RASTER = S.RAND_RASTER
RANDPAD_LAUF = round(RAND_LOECHER * RAND_RASTER, 3)     # 55,88 mm
RANDPAD_TIEFE = 4.0     # mm quer zur Reihe -- Pad (0,90 mm,
                        # stack_spec.RAND_PAD_B) plus Silk-Label-Platz
RANDPAD_PUFFER = 0.6    # mm Abstand zur alten Kante x=75 (reine
                        # Uebersicht -- x=75 traegt heute nichts)
R5_KANTENABSTAND_MM = 2.0     # neue, schaerfere Vertragsregel (statt des
                              # alten EDGE_CLEARANCE=0,5 mm)

RANDPAD_ZONE_FLAECHE = round(RANDPAD_LAUF * RANDPAD_TIEFE, 3)

# Minimaler Rechts-Zuwachs: Puffer + Zonentiefe + R5-Kantenabstand hinter
# der neuen Kante. Diese Zahl aendert sich durch die M3-Beweglichkeit
# NICHT -- sie folgt allein aus R5 und der Zonentiefe.
DELTA_RECHTS_MIN = round(
    RANDPAD_PUFFER + RANDPAD_TIEFE + R5_KANTENABSTAND_MM, 3)


# === 4. Elektronik-Nutzlast: echte Hof-Summen aus den Spec-Dateien =====
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
                          # platzprobe_v2.py
NUTZLAST_BEDARF = round(NUTZLAST_WORST * PACKUNGS_RESERVE, 4)

MANDATORY_SUMME = round(
    PICO_ZONE_FLAECHE + STECKER_ZONE_FLAECHE + ZELLE_ZONE_FLAECHE
    + KLEMMENZONE_FLAECHE + RANDPAD_ZONE_FLAECHE, 3)


# === 5. Kandidaten: Zuwachs rechts + unten auf 75x65 ====================
# Kleiner geraster als in der ersten Fassung: die Grobsuche oben (nicht im
# Skript, im Vorlauf dieser Aufgabe) zeigt den Umschlagpunkt bei
# delta_rechts=7/delta_unten=8 (ganzzahlige mm) -- die drei Kandidaten
# hier klammern ihn ein: einer scheitert klar, einer trifft ihn, einer
# hat spuerbar mehr Reserve.
KANDIDATEN = ((5.0, 5.0), (7.0, 8.0), (10.0, 10.0))


def _landepunkt_min_abstand(punkte, x0, x1, y0, y1):
    """Kleinster Abstand irgendeines Landepunkts zum Rechteck."""
    beste = None
    for px, py in punkte:
        dx = max(x0 - px, 0.0, px - x1)
        dy = max(y0 - py, 0.0, py - y1)
        d = (dx * dx + dy * dy) ** 0.5
        if beste is None or d < beste:
            beste = d
    return round(beste, 3)


def pruefe(delta_rechts, delta_unten):
    w = round(BOARD_W0 + delta_rechts, 3)
    h = round(BOARD_H0 + delta_unten, 3)
    m3 = m3_holes_fuer(w, h)
    m3_oben_rechts, m3_unten_rechts = m3[2], m3[3]
    m3_unten_links = m3[1]
    punkte = landepunkte_fuer(w, h)

    # -- Randpad-Zone: rechter Streifen, X-Lage fix (Puffer + Tiefe ab der
    # ALTEN Kante x=75), Y-Lage mittig -- aber jetzt MUSS sie zwischen dem
    # oberen und dem unteren rechten M3-Freihaltequadrat hindurchpassen
    # (beide wandern mit der Kante, liegen also im selben X-Bereich wie
    # die Randpad-Zone selbst -- der Docstring erklaert, warum das jetzt
    # so ist und vorher nicht war).
    rp_x0 = round(BOARD_W0 + RANDPAD_PUFFER, 3)
    rp_x1 = round(rp_x0 + RANDPAD_TIEFE, 3)
    y_frei_oben = round(m3_oben_rechts[1] + M3_HALB + GENERISCHER_ABSTAND, 3)
    y_frei_unten = round(m3_unten_rechts[1] - M3_HALB - GENERISCHER_ABSTAND,
                         3)
    y_verfuegbar = round(y_frei_unten - y_frei_oben, 3)
    rp_y0 = round((h - RANDPAD_LAUF) / 2.0, 3)
    rp_y1 = round(rp_y0 + RANDPAD_LAUF, 3)
    rp_m3_ok = rp_y0 >= y_frei_oben and rp_y1 <= y_frei_unten
    rp_kante_frei = round(w - rp_x1, 3)
    rp_kante_ok = rp_kante_frei >= R5_KANTENABSTAND_MM
    rp_landeabstand = _landepunkt_min_abstand(punkte, rp_x0, rp_x1, rp_y0,
                                              rp_y1)
    rp_lande_ok = rp_landeabstand >= S.LANDE_SPERRRADIUS

    # -- Klemmenzone: unterer Streifen, mittig in x auf der NEUEN
    # Gesamtbreite w zentriert (nicht mehr auf der alten 75 mm) -- so
    # bleibt sie symmetrisch zwischen den beiden UNTEREN M3-Eckloechern,
    # die jetzt ja ebenfalls mit w wachsen.
    kz_x0 = round((w - KLEMMENZONE_L) / 2.0, 3)
    kz_x1 = round(kz_x0 + KLEMMENZONE_L, 3)
    kz_y1 = h
    kz_y0 = round(kz_y1 - KLEMMENZONE_B, 3)
    kz_frei_links = round(kz_x0 - (m3_unten_links[0] + M3_HALB), 3)
    kz_frei_rechts = round((m3_unten_rechts[0] - M3_HALB) - kz_x1, 3)
    kz_m3_ok = kz_frei_links >= 0.0 and kz_frei_rechts >= 0.0
    # Untere Grenze ist jetzt STAPEL_BODEN (52,3, frozen Vertragsgeometrie)
    # + genereller Abstand -- nicht mehr "die alte Plattenkante bei 65".
    kz_boden_ok = kz_y0 >= round(STAPEL_BODEN + GENERISCHER_ABSTAND, 3)

    geometrie_ok = (rp_kante_ok and rp_m3_ok and rp_lande_ok and kz_m3_ok
                    and kz_boden_ok)

    flaeche = round(w * h, 3)
    frei = round(flaeche - MANDATORY_SUMME - M3_FLAECHE, 3)
    flaeche_reicht = frei >= NUTZLAST_BEDARF
    passt = geometrie_ok and flaeche_reicht

    return {
        "delta_rechts": delta_rechts, "delta_unten": delta_unten,
        "w": w, "h": h, "flaeche": flaeche, "frei": frei, "m3": m3,
        "rp": (rp_x0, rp_y0, rp_x1, rp_y1),
        "rp_kante_frei": rp_kante_frei, "rp_kante_ok": rp_kante_ok,
        "y_frei_oben": y_frei_oben, "y_frei_unten": y_frei_unten,
        "y_verfuegbar": y_verfuegbar, "rp_m3_ok": rp_m3_ok,
        "rp_landeabstand": rp_landeabstand, "rp_lande_ok": rp_lande_ok,
        "kz": (kz_x0, kz_y0, kz_x1, kz_y1),
        "kz_frei_links": kz_frei_links, "kz_frei_rechts": kz_frei_rechts,
        "kz_m3_ok": kz_m3_ok, "kz_boden_ok": kz_boden_ok,
        "geometrie_ok": geometrie_ok, "flaeche_reicht": flaeche_reicht,
        "passt": passt,
    }


def main():
    print("=== Rot-Nachweis: m3_holes_fuer(75,65) reproduziert den "
          "Vertrag ===")
    nachprobe = m3_holes_fuer(BOARD_W0, BOARD_H0)
    ok = nachprobe == S.M3_HOLES
    print("m3_holes_fuer(75,65) = %s" % (nachprobe,))
    print("stack_spec.M3_HOLES  = %s -> %s"
          % (S.M3_HOLES, "GLEICH" if ok else "ABWEICHUNG"))
    if not ok:
        raise SystemExit(1)

    print()
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
    print("=== Klemmenzone (R1/R2/R4, unveraendert durch M3-Beweglichkeit) "
          "===")
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
    print("STAPEL_BODEN (tiefster Punkt frozen Vertragsgeometrie, "
          "stapel_links/rechts) = %.2f mm" % STAPEL_BODEN)
    print("-> Klemmenzone braucht mindestens y >= %.2f + %.2f = %.2f mm "
          "Deckenhoehe, das treibt delta_unten kaum noch (s. Kandidaten)"
          % (STAPEL_BODEN, GENERISCHER_ABSTAND,
             STAPEL_BODEN + GENERISCHER_ABSTAND))

    print()
    print("=== Randpad-Zone auf F.Cu -- JETZT von den beweglichen "
          "M3-Loechern eingeklemmt ===")
    print("22 Loecher x %.2f mm Raster = %.2f mm Lauflaenge"
          % (RAND_RASTER, RANDPAD_LAUF))
    print("Rechter Streifen: X fix bei %.2f Puffer + %.2f Tiefe ab der "
          "alten Kante x=75, R5-Kantenabstand %.2f mm -> delta_rechts >= "
          "%.2f mm" % (RANDPAD_PUFFER, RANDPAD_TIEFE, R5_KANTENABSTAND_MM,
                        DELTA_RECHTS_MIN))
    print("Die beiden RECHTEN M3-Loecher wandern mit (immer 4,0 mm von "
          "der jeweils aktuellen Kante) -- ihre Freihaltequadrate liegen "
          "damit im SELBEN X-Bereich wie die Randpad-Zone. Trennung "
          "muss also ueber Y laufen: die Zone muss zwischen dem oberen "
          "und dem unteren Freihaltequadrat (je +-%.1f mm um die "
          "Lochmitte, plus %.1f mm Abstand) hindurchpassen -- das treibt "
          "jetzt delta_unten, nicht mehr die Klemmenzone."
          % (M3_HALB, GENERISCHER_ABSTAND))

    print()
    print("=== Elektronik-Nutzlast (echte Hof-Summen) ===")
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
        print("    M3-Loecher: %s" % (r["m3"],))
        rp_x0, rp_y0, rp_x1, rp_y1 = r["rp"]
        print("    Randpad-Zone (%.2f,%.2f)-(%.2f,%.2f)"
              % (rp_x0, rp_y0, rp_x1, rp_y1))
        print("      Kantenabstand %s - %s = %.2f mm (braucht >= %.1f) "
              "-> %s"
              % (r["w"], rp_x1, r["rp_kante_frei"], R5_KANTENABSTAND_MM,
                 "ok" if r["rp_kante_ok"] else "R5 VERLETZT"))
        print("      M3-Luecke oben->unten: frei ab y=%.2f bis y=%.2f "
              "(%.2f mm verfuegbar, braucht %.2f mm Lauf) -> %s"
              % (r["y_frei_oben"], r["y_frei_unten"], r["y_verfuegbar"],
                 RANDPAD_LAUF,
                 "ok" if r["rp_m3_ok"] else "KOLLISION MIT M3-ECKE"))
        print("      Landepunkt-Mindestabstand = %.2f mm (braucht >= "
              "%.1f) -> %s"
              % (r["rp_landeabstand"], S.LANDE_SPERRRADIUS,
                 "ok" if r["rp_lande_ok"] else "1,5-mm-KLAUSEL VERLETZT"))
        kz_x0, kz_y0, kz_x1, kz_y1 = r["kz"]
        print("    Klemmenzone (%.2f,%.2f)-(%.2f,%.2f)"
              % (kz_x0, kz_y0, kz_x1, kz_y1))
        print("      Luft zum linken M3-Eckloch %.2f mm, zum rechten "
              "%.2f mm -> %s"
              % (r["kz_frei_links"], r["kz_frei_rechts"],
                 "ok" if r["kz_m3_ok"] else "KOLLISION MIT M3-ECKE"))
        print("      Beginnt bei y=%.2f (braucht >= STAPEL_BODEN+%.1f = "
              "%.2f) -> %s"
              % (kz_y0, GENERISCHER_ABSTAND,
                 STAPEL_BODEN + GENERISCHER_ABSTAND,
                 "ok" if r["kz_boden_ok"] else "SCHNEIDET STECKERFLAECHE AN"))
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
    print("M3_HOLES = %s  # 4,0 mm von jeder Kante, dieselbe Herleitung "
          "wie v1/v2" % (kleinster["m3"],))
    print("KLEMMENZONE  = (%.2f, %.2f, %.2f, %.2f)  # %.2f x %.2f mm, "
          "Kante unten, F.Silkscreen-Beschriftung je Klemme (R7)"
          % (kz_x0, kz_y0, kz_x1, kz_y1, KLEMMENZONE_L, KLEMMENZONE_B))
    print("RANDPAD_ZONE = (%.2f, %.2f, %.2f, %.2f)  # %.2f x %.2f mm, "
          "Kante rechts, F.Cu + F.Silkscreen (R8)"
          % (rp_x0, rp_y0, rp_x1, rp_y1, RANDPAD_TIEFE, RANDPAD_LAUF))
    print("STECKER_POS, PIN_ROLLE: UNVERAENDERT aus dem v2-Vertrag "
          "(frozen, s. Modul-Docstring Punkt 1)")
    print("LANDEPUNKTE_VERDREHT: neu herzuleiten fuer BOARD_W/H = %.1f/"
          "%.1f (landepunkte_fuer() oben), NICHT mehr die alten 46 "
          "75x65-Werte" % (kleinster["w"], kleinster["h"]))

    print()
    print("=== Rot-Nachweis gegen die Audit-Befunde ===")
    b1_frei = (kz_y0 >= S.PICO_SCHATTEN[3])
    print("B1 (Motor-/Kanal-1-Klemme im PICO_SCHATTEN): Klemmenzone "
          "beginnt bei y=%.2f, PICO_SCHATTEN endet bei y=%.2f -> %s"
          % (kz_y0, S.PICO_SCHATTEN[3],
             "GELOEST (Zone liegt vollstaendig ausserhalb)" if b1_frei
             else "NICHT geloest"))

    q90 = MOTOR.PLACEMENT["Q90"]
    q90_x0, q90_y0 = q90.x, q90.y
    q90_x1, q90_y1 = q90.x + q90.w, q90.y + q90.h
    m3_or_alt = S.M3_HOLES[2]           # (71, 4), eingefrorener v2-Wert
    m3_or_neu = kleinster["m3"][2]      # (w-4, 4), jetzt gewandert
    keep_alt_x0, keep_alt_x1 = m3_or_alt[0] - M3_HALB, m3_or_alt[0] + M3_HALB
    keep_neu_x0 = m3_or_neu[0] - M3_HALB
    x_ueberlappt_alt = not (q90_x1 <= keep_alt_x0 or q90_x0 >= keep_alt_x1)
    x_frei_neu = round(keep_neu_x0 - q90_x1, 3)
    print("K1 (Q90 nur 0,10-0,20 mm zum M3-Freihaltequadrat der Bohrung "
          "(71|4)): Q90-Hof x=%.2f..%.2f, y=%.2f..%.2f."
          % (q90_x0, q90_x1, q90_y0, q90_y1))
    print("    Altes M3-Loch (71,4), Freihaltequadrat x=%.2f..%.2f: "
          "ueberlappt Q90 in x -> %s (deshalb reichte in y nur 0,1-0,2 mm)"
          % (keep_alt_x0, keep_alt_x1, "JA" if x_ueberlappt_alt else "nein"))
    print("    Neues M3-Loch %s (wandert mit der rechten Kante): Luft in "
          "x zwischen Q90-Ostkante und Freihaltequadrat = %.2f - %.2f = "
          "%.2f mm -> %s"
          % (m3_or_neu, keep_neu_x0, q90_x1, x_frei_neu,
             "GELOEST (x-getrennt, y-Naehe irrelevant)"
             if x_frei_neu > 0 else "weiterhin eng"))

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

"""Platinenbeschreibung der Dimmer-Module v3 (1, 3, 4 Kanaele).

Platzierung VON HAND nach Stromfluss (Vertrag P1-P5, Bericht 04 vom
2026-10-14), nicht nach Zonen. Alle Masse in mm, Hof-Ecke links oben.
Platine 74 x 58, Pico quer (USB links), Klemmen unten.

Das Bild (Dimmer4):

    y 0,5-7,6   D91 (ueber Pin 39) | LED90/R94 | J3 Stapel VIN | J4 Qwiic | J10 User
    y 8,2-11,8  J2  Pico-Reihe oben (Pins 21..40)
    y 12,4-21,6 unter dem Pico: L90, D93 | Slot-Matrix (4 Spalten x 4 Baenke)
    y 19,7-25,1 unter dem Pico, Reihe B: C93/R92/R93 | U90 | C91 C92
    y 26,0-29,6 J1  Pico-Reihe unten (Pins 1..20)
    y 30,2-36,9 Freilaufdioden D1..D4 + Gate-Widerstaende RG1..RG4
    y 37,5-48,6 FETs Q1..Q4 (Beine nach oben, Tab zur Klemme) + RP1..RP4
    y 49,4-58   Klemmen J5..J8 (LED1..4) und J90 (6-30 V), kantenbuendig
    x 61,2-73,5 Versorgungsspalte: Identitaet, C90, D90, Q90 (Tab unten), D92/R91, C94

Jede Zahl hier wird von tests/test_spec_dimmer.py gegen den Vertrag
und die Platzierungsregeln geprueft (Ueberlappung, Kanten, M3, Antenne,
P1-P4-Abstaende, Klemmenzone).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import stack_spec as S   # noqa: E402
from platz import (Platz, aus_vertrag, naehte, COURTYARD_GAP,  # noqa: E402
                   EDGE_CLEARANCE, STITCH_RASTER)

# --- Footprints (Hofmasse mit pcbnew gemessen, 2026-11-15) -----------------
FP = {
    "R0805": ("Resistor_SMD:R_0805_2012Metric", 3.36, 1.90),
    "R0603": ("Resistor_SMD:R_0603_1608Metric", 2.96, 1.46),
    "C0805": ("Capacitor_SMD:C_0805_2012Metric", 3.40, 1.96),
    "C1210": ("Capacitor_SMD:C_1210_3225Metric", 4.60, 3.20),
    "CP63": ("Capacitor_SMD:CP_Elec_6.3x7.7", 9.40, 7.10),
    "SMC": ("Diode_SMD:D_SMC", 9.80, 6.70),
    "SOD123": ("Diode_SMD:D_SOD-123", 4.70, 2.30),
    "L6045": ("Inductor_SMD:L_Sunlord_SWPA6045S", 6.70, 6.50),
    "SOIC8EP": ("Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", 7.40, 5.40),
    "TO252": ("Package_TO_SOT_SMD:TO-252-3_TabPin2", 11.10, 7.00),
    "LED0805": ("LED_SMD:LED_0805_2012Metric", 3.36, 1.90),
    "KLEMME": (S.FP_KLEMME_35, 8.00, 8.60),
    "QWIIC": (S.FP_QWIIC, 7.80, 6.56),
    "USER": (S.FP_USER, 3.54, 16.24),
    "STAPEL20": (S.FP_STAPEL_20, 3.54, 51.80),
    "STAPEL4": (S.FP_STAPEL_4, 3.54, 11.16),
}


def _p(ref, art, x, y, rot=0, tht=False):
    """Platz aus Footprint-Art; bei 90/270 Grad tauschen w und h."""
    name, w, h = FP[art]
    if rot in (90, 270):
        w, h = h, w
    return name, Platz(ref, x, y, w, h, rot, tht)


KANAL_PITCH = 13.7
# Slot-Matrix: je Signal EINE SPALTE aus vier liegenden 0603 (rot 0:
# Pin 1 = GP links, Pin 2 = Signal rechts), Reihenfolge von oben C, D
# (Baenke an der oberen Pico-Reihe J2), A, B (untere Reihe J1). So laeuft
# das Signal als gerade Bahn an der rechten Pad-Spalte herunter, und
# die GP-Bahnen kommen von oben bzw. unten an die linke Pad-Spalte,
# ohne einander zu kreuzen. Zwei fruehere Anordnungen (2 x 2 Gruppen
# liegend, Bank-abhaengig gedreht) liessen den Router S1 bzw. S3 auf
# 0,127 mm quetschen (DRC track_width, 2026-11-15).
_MATRIX_REIHEN = ("C", "D", "A", "B")
_MATRIX_PITCH_Y = 2.5          # 1,04 mm Luft je Reihe
_MATRIX_PITCH_X = 4.46         # 1,5 mm Luft zwischen den Spalten
_MATRIX_X0, _MATRIX_Y0 = 26.2, 12.6


def _matrix_platz(n, bank):
    """Hof-Ecke des 0603 fuer Signal n (Spalte) und Bank (Zeile)."""
    return (_MATRIX_X0 + _MATRIX_PITCH_X * (n - 1),
            _MATRIX_Y0 + _MATRIX_PITCH_Y * _MATRIX_REIHEN.index(bank))


def platzierung(kanaele):
    fp, pl = {}, {}

    def setze(ref, art, x, y, rot=0, tht=False):
        name, p = _p(ref, art, x, y, rot, tht)
        fp[ref] = name
        pl[ref] = p

    # Vertragsplaetze (Lage aus S.STECKER_POS, nicht hier erfunden)
    for ref, platz in VERTRAGSPLATZ.items():
        e = S.STECKER_POS[platz]
        fp[ref] = e["footprints"][0]
        pl[ref] = aus_vertrag(ref, e["flaeche"], e["drehung"])

    # Obere Kante: VSYS-Diode ueber Pin 39, LED, Qwiic (Oeffnung nach
    # oben = rot 180), User-Header
    setze("D91", "SMC", 8.0, 0.5)          # Pin 39 (VSYS) liegt bei (11,5|10)
    setze("LED90", "LED0805", 18.4, 0.5)
    setze("R94", "R0805", 18.4, 3.0)
    setze("J4", "QWIIC", 37.0, 0.5, 180)
    setze("J10", "USER", 45.4, 2.23, 90, tht=True)

    # Slot-Matrix: je Signal eine Spalte aus vier 0603 (s. _matrix_platz)
    for n in range(1, kanaele + 1):
        for bank in S.BAENKE:
            x, y = _matrix_platz(n, bank)
            setze(S.MATRIX_REF(n, bank), "R0603", x, y, 0)

    # Unter dem Pico, Reihe A (y 12,37): Buck-Ausgangsseite
    setze("L90", "L6045", 8.4, 12.47)
    setze("D93", "SMC", 15.7, 12.37)
    # Reihe B (y 19,67): Buck-IC mit Boot-, Eingangs- und Teilerteilen
    setze("U90", "SOIC8EP", 8.2, 19.67)
    setze("C93", "C0805", 4.0, 19.67)
    setze("R92", "R0603", 4.06, 22.23)
    setze("R93", "R0603", 0.5, 22.23)
    setze("C91", "C1210", 16.2, 19.67, 90)
    setze("C92", "C1210", 20.0, 19.67, 90)   # zweite Eingangskeramik, neben C91

    # Versorgungsspalte rechts (x 61,2), von oben nach unten; oben die
    # Board-Identitaet (IDENTITY_POS, zwei Zeilen bis y 11,2)
    setze("C90", "CP63", 61.2, 11.8)
    setze("D90", "SMC", 61.2, 19.5)
    # Q90 mit Beinen nach oben, Tab (Drain = PWR_IN) nach unten zur
    # Einspeiseklemme: so laeuft der 4-A-Stamm gerade von J90 hoch in
    # den Tab, statt um den Elko herum (erster Router-Lauf: 0,25-mm-
    # Engstelle bei (67|46,8), strombelastung ROT).
    setze("Q90", "TO252", 61.2, 26.8, 270)
    setze("D92", "SOD123", 61.2, 38.5)
    setze("R91", "R0805", 66.5, 38.5)
    setze("C94", "CP63", 61.2, 41.4)       # Buck-Ausgangselko (DC, darf weit weg)

    # Kanaele: Diode + RG in der Diodenreihe, FET + RP in der FET-Reihe,
    # Klemme darunter -- alles im selben KANAL_PITCH
    for n in range(1, kanaele + 1):
        dx = KANAL_PITCH * (n - 1)
        setze("D%d" % n, "SMC", 7.0 + dx, 30.15)
        setze("RG%d" % n, "R0603", 17.4 + dx, 32.0, 90)
        setze("Q%d" % n, "TO252", 8.4 + dx, 37.45, 270)
        setze("RP%d" % n, "R0603", 16.0 + dx, 39.0, 90)
        setze("J%d" % (4 + n), "KLEMME", 8.55 + dx, 49.4, 0, tht=True)
    setze("J90", "KLEMME", 58.5, 49.4, 0, tht=True)
    return fp, pl


VERTRAGSPLATZ = {"J1": "stapel_unten", "J2": "stapel_oben", "J3": "leistung"}

RULE_AREAS = (
    ("Antennenfreiheit (Pico W)", ("F.Cu", "B.Cu"), S.ANTENNE_FREI,
     frozenset(("bahnen", "vias", "guss"))),
)


def _funktions_labels(kanaele):
    # Stecker-Labels an der Oberkante UEBER den Steckern (y 1,3): unter
    # ihnen (y 7,0) sitzen die Referenzen J3/J10, die tidy_silkscreen setzt.
    aus = [("6-30V", 69.0, 50.6), ("VIN VIN GND GND", 31.5, 1.3),
           ("QWIIC", 40.9, 1.4), ("GP0 1 2 3 3V3 GND", 53.5, 1.3)]
    for n in range(1, kanaele + 1):
        aus.append(("LED%d" % n, 5.65 + KANAL_PITCH * (n - 1), 50.6))
    return tuple(aus)


# --- Der 4-A-Stamm von Hand -------------------------------------------------
# Der Router legte den Stamm zweimal um den Ausgangselko herum und
# verengte ihn an der Klemme auf 0,25 mm (strombelastung ROT, 2026-11-15).
# Was der Router nicht kann, wird vorverdrahtet, und zwar nur das:
#   * PWR_IN (F.Cu, 1,4 mm): J90.1 (60,75|53) -> hoch durch die Gasse
#     zwischen RP4 (bis x 58,3) und der Versorgungsspalte (ab 61,45) ->
#     in den Tab von Q90 (Mitte 64,7|34,45).
#   * VIN (B.Cu, 1,4 mm): Q90-Source (62,42|28,15) ueber ein Via in der
#     Gasse -> hinunter -> Bus entlang y 50,0 (zwischen FET-Tabs auf
#     F.Cu und Klemmenpads ab y 51,8) -> Stich auf jede Kanalklemme J.1.
# Pad-Koordinaten mit pcbnew am gebauten Board gelesen (scratch/pads.py).
STAMM_X = 59.6          # Gassenmitte, Bahn 58,9..60,3
STAMM_BREITE = 1.4
_Q90_TAB = (64.7, 34.45)
_Q90_SOURCE = (62.42, 28.15)
_BUS_Y = 50.0


def _stamm_vorverdrahtung(kanaele):
    j90 = (58.5 + 2.25, 53.0)
    pwr_in = ("/PWR_IN", "F.Cu",
              [j90, (j90[0], 51.85), (STAMM_X, 51.85 - (j90[0] - STAMM_X)),
               (STAMM_X, _Q90_TAB[1]), _Q90_TAB], STAMM_BREITE)
    via = (STAMM_X + 0.3, _Q90_SOURCE[1])
    vin_oben = ("/VIN", "F.Cu", [_Q90_SOURCE, via], STAMM_BREITE)
    # Bus als Kette von Segmenten, die an jedem Stich ENDEN: ein Stich,
    # der mitten auf einem Segment ansetzt, ist fuer KiCad verbunden,
    # fuer den Leitungsgraphen der Strombelastung aber kein Knoten --
    # der rechnete den 4-A-Pfad dann ueber die Diodenstummel (ROT).
    # Knoten auf dem Bus, von rechts nach links: je Kanal der Stich zur
    # Klemme J.1 (x 10,8 + Pitch) und der Stich zur Freilaufdiode D.1
    # (Via bei x 7,5 + Pitch, y 36,4 -- zwischen Diodenpad und FET-
    # Beinen). Ohne den Dioden-Stich baute der Router aus den Dioden-
    # Kathoden einen zweiten, 0,25 mm duennen VIN-Strang (ROT).
    x_kl = [8.55 + 2.25 + KANAL_PITCH * (n - 1) for n in range(kanaele, 0, -1)]
    x_di = [7.5 + KANAL_PITCH * (n - 1) for n in range(kanaele, 0, -1)]
    knoten = [(via[0], _BUS_Y)] + sorted([(x, _BUS_Y) for x in x_kl + x_di],
                                         key=lambda k: -k[0])
    teile = [("/VIN", "B.Cu", [via, knoten[0]], STAMM_BREITE)]
    for a, b in zip(knoten, knoten[1:]):
        teile.append(("/VIN", "B.Cu", [a, b], STAMM_BREITE))
    for x in x_kl:
        teile.append(("/VIN", "B.Cu", [(x, _BUS_Y), (x, 53.0)], STAMM_BREITE))
    for x in x_di:
        teile.append(("/VIN", "B.Cu", [(x, _BUS_Y), (x, 36.4)], STAMM_BREITE))
        # F.Cu: Diodenpad D.1 (x+1,0 | 33,5) -> 45 Grad -> Via (x | 36,4)
        teile.append(("/VIN", "F.Cu", [(x + 1.0, 33.5), (x + 1.0, 35.4), (x, 36.4)], 0.8))
    return tuple([pwr_in, vin_oben] + teile)


def _dioden_vias(kanaele):
    return tuple(("/VIN", 7.5 + KANAL_PITCH * (n - 1), 36.4) for n in range(1, kanaele + 1))


def beschreibung(kanaele):
    assert kanaele in (1, 3, 4)
    footprints, platz = platzierung(kanaele)
    typ = {1: 0x10, 3: 0x11, 4: 0x12}[kanaele]
    return {
        "BOARD_W": S.BOARD_W, "BOARD_H": S.BOARD_H, "CORNER_R": S.CORNER_R,
        "M3_DRILL": S.M3_DRILL, "M3_HOLES": S.M3_HOLES, "M3_KEEPOUT": S.M3_KEEPOUT,
        "COURTYARD_GAP": COURTYARD_GAP, "EDGE_CLEARANCE": EDGE_CLEARANCE,
        "IST_MODUL": True,
        "MODULNAME": S.MODULTYPEN[typ]["name"], "MODULTYP": typ,
        "BANK": S.BANK_VORGABE["Dimmer"],
        "FOOTPRINTS": footprints,
        "PLACEMENT": platz,
        "VERTRAGSPLATZ": dict(VERTRAGSPLATZ),
        "FUNKTIONS_LABELS": _funktions_labels(kanaele),
        "PRE_TRACKS": _stamm_vorverdrahtung(kanaele),
        # Zwei 0,3-mm-Waermevias im PowerPAD von U90 (Hofmitte 11,9|22,37,
        # EP 2,29 x 3,0 mm) -- ersetzen die 0,2-mm-Vias des _ThermalVias-
        # Footprints, die unter der Projekt-Bohrregel liegen. Dazu das
        # VIN-Via am Stammbeginn (s. _stamm_vorverdrahtung).
        "PRE_VIAS": (("GND", 11.9, 21.6), ("GND", 11.9, 23.1),
                     ("/VIN", STAMM_X + 0.3, 28.15)) + _dioden_vias(kanaele),
        "RULE_AREAS": RULE_AREAS,
        "STITCH_RASTER": STITCH_RASTER,
        "STITCH_VIAS": naehte(platz, RULE_AREAS),
        "PIN1_MARKE": (5.5, 27.78),
        "KLEMMEN_POS": (3.5, 57.0),
        "IDENTITY_POS": (61.4, 7.6),
        "POWER_NETS": tuple(["/PWR_IN", "/VIN", "/+5V_LOKAL", "/VSW", "/VSYS"]
                            + ["/LED%d" % n for n in range(1, kanaele + 1)]),
        "EDGE_FLUSH_REFS": frozenset(["J90"] + ["J%d" % (4 + n)
                                                for n in range(1, kanaele + 1)]),
    }

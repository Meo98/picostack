"""Platinenbeschreibung des Motormoduls: Umriss, Lochbild, Platzierung.

Gelesen von tools/pcb/geometry.py (Pruefung), tools/pcb/build.py
(Aufbau) und tools/pcb/netclasses.py (Bahnbreiten). Bewusst OHNE
KiCad-Abhaengigkeit -- `python3 tools/pcb/geometry.py spec_motor` muss
ohne pcbnew laufen.

WAS FESTSTEHT. Umriss, Lochbild und die Lage der Stecker kommen aus
dem Vertrag (tools/stack_spec.py) und werden ausgerechnet, nicht
abgeschrieben. Anders als die Sockelplatine traegt das Modul von
Ketten- und Leistungsstecker BEIDE Haelften: Buchse oben (J101/J103),
Stiftleiste gespiegelt unten (J102/J104), am selben Kontaktraster --
das ist der Normalfall, fuer den Platz.unten gebaut wurde.

DER WAERMEPFAD IST DER GRUND DIESER NEUAUFLAGE. Der DRV8876 (U1)
traegt in seinem Footprint zwoelf Waermevias unter dem Waermepad; sie
muenden in die Masseflaeche der Rueckseite. RULE_AREAS legt unter den
Treiber eine Regelflaeche, die dort Bahnen und fremde Vias verbietet,
den Guss aber erlaubt -- keine Bahn darf die Flaeche zerschneiden, und
der Router bekommt das als Sperrflaeche in die DSN.

DIE UEBERLEGUNG HINTER DER PLATZIERUNG (erst Topologie, dann Ort):

1. Der 24-V-Strang traegt bis 2,5 A und bleibt rechts unten kompakt:
   J103/J104 (Vertrag, x 50..62) -> Q1 (Verpolungsschutz, direkt
   darueber) -> D1 (TVS) und C12 (220 uF Stuetzung) -> U1 (Treiber,
   rechts der Mitte) -> J5 (Motorklemme, untere Kante). Die untere
   Kante ist die Klemmenkante des ganzen Stapels.

2. Der Kleinst-MCU (U100) sitzt links oben, direkt unter den
   Vertragspins des Stapelsteckers (FLASH/I2C/SEL_CLK/NOTAUS liegen
   auf Pin 1..10, also x 8..19). Sein Umfeld: Abblockung C14/C15/C16,
   Reset-Gatter U102, BOOT0-Gatter U103, Kennwiderstaende R100/R101/
   R104/R105, Vorwiderstaende R7..R10 zum Treiber.

3. Das Ketten-Flipflop U101 sitzt links am Rand unter dem
   Stapelstecker, auf kurzem Weg zwischen Kettenstecker (oben) und
   SEL_CLK; sein Loesch-RC (C101/R102) direkt daneben.

4. Der Notaus-Ruhestromkreis (J3 an der Klemmenkante, Optokoppler
   U4/U5, Speisung R16..R19 aus 24 V, Treiber U6/U7, UND-Gatter U3)
   liegt als Band ueber der unteren Kante -- die Kreise kommen als
   Kabel herein und gehen als NOTAUS/NSLEEP-Logik nach oben.

5. VERDREHT-LANDEPUNKTE (stack_spec.LANDEPUNKTE_VERDREHT, Kupferregel
   fuer Module): die 40 Stapel-Landepunkte liegen in zwei Reihen bei
   y = 47,00 und 49,54 -- deshalb traegt der Streifen y 45,5..51 KEINE
   freiliegenden Pads. J5 und J3 ueberspannen ihn nur mit ihrem Hof,
   ihre Pads liegen bei y = 53,65 bzw. 57,17. Die Kette landet bei
   (51,5|54,7) und (51,5|57,25) -- dort bleibt die Ecke frei --, die
   Leistung bei (6,8..9,3|15,5..18,0) -- dort sitzt kein Pad, U101
   beginnt erst bei y = 21. tools/pcb/steckerprobe.py misst das an der
   gebauten Platine nach.

ZUGENTLASTUNG DER SMD-STECKERPAARE (dritte Layout-Auflage): es gilt
das Fuegeverfahren aus stack_spec.MONTAGE_REGEL -- erst stecken, dann
auf die Abstandsbolzen schrauben. Keine zusaetzlichen
Befestigungspunkte auf der Platine.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S       # noqa: E402
from spec_sockel import Platz, _aus_vertrag   # noqa: E402  (gleiche Klasse,
# gleiche Bedeutung -- eine zweite Kopie liefe auseinander)

# --- Umriss, Lochbild, Regeln: alles aus dem Vertrag -----------------
BOARD_W = S.BOARD_W
BOARD_H = S.BOARD_H
CORNER_R = S.CORNER_R
M3_DRILL = S.M3_DRILL
M3_HOLES = S.M3_HOLES
M3_KEEPOUT = S.M3_KEEPOUT

COURTYARD_GAP = 0.6
EDGE_CLEARANCE = 0.5

# Das Motormodul ist ein MODUL: auf seine Oberseite druecken die Stifte
# eines verdreht aufgesteckten Aufbaus. Die Kupferregel des Vertrags
# gilt (steckerprobe.verdrehtprobe misst sie).
IST_MODUL = True

# --- Footprints (muessen zum Schaltplan passen; build.place meldet) --
FP_HDR_2X20 = "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical"
FP_SKT_1X02 = ("Connector_PinSocket_2.54mm:"
               "PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left")
FP_HDR_1X02 = ("Connector_PinHeader_2.54mm:"
               "PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left")
FP_SKT_2X02 = "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD"
FP_HDR_2X02 = "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD"
_C = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
_R = "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
_R1206 = "Resistor_SMD:R_1206_3216Metric"
_SOT353 = "Package_TO_SOT_SMD:SOT-353_SC-70-5"

FOOTPRINTS = {
    "C9": _C, "C10": _C, "C11": _C, "C13": _C, "C14": _C, "C15": _C,
    "C16": _C, "C100": _C, "C101": _C,
    "C12": "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
    "D1": "Diode_SMD:D_SMC_Handsoldering",
    "J3": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    "J5": ("TerminalBlock_Phoenix:"
           "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal"),
    "J100": FP_HDR_2X20,
    "J101": FP_SKT_1X02, "J102": FP_HDR_1X02,
    "J103": FP_SKT_2X02, "J104": FP_HDR_2X02,
    "Q1": "Package_TO_SOT_SMD:TO-252-3_TabPin2",
    "R5": _R, "R7": _R, "R8": _R, "R9": _R, "R10": _R, "R11": _R,
    "R12": _R, "R13": _R, "R15": _R, "R20": _R, "R21": _R,
    "R16": _R1206, "R17": _R1206, "R18": _R1206, "R19": _R1206,
    "R100": _R, "R101": _R, "R102": _R, "R104": _R, "R105": _R,
    "U1": "DRV8876PWPR:IC_DRV8876PWPR",
    "U3": _SOT353, "U6": _SOT353, "U7": _SOT353, "U103": _SOT353,
    "U4": "Optocoupler_PC817:PC817_SMT_Gullwing",
    "U5": "Optocoupler_PC817:PC817_SMT_Gullwing",
    "U100": "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
    "U101": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
    "U102": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
}

# --- Platzierung -----------------------------------------------------
# Vertragsteile ausgerechnet; die Buchsen (J101/J103) mit der
# VERTRAGSFLAECHE als Reservierung waere falsch -- jede Haelfte wird
# mit ihrem EIGENEN Hof am selben Kontaktanker platziert (s. Kommentar
# bei spec_sockel.PLACEMENT, warum die Vereinigungsflaeche als Anker
# das Bauteil verschieben wuerde).
_S = S.STECKER_POS
PLACEMENT = {
    "J100": _aus_vertrag("J100", _S["stapel"]["flaeche"],
                         _S["stapel"]["drehung"], True),
    "J101": _aus_vertrag("J101", S.HOF(FP_SKT_1X02, _S["kette"]["pin1"],
                                       _S["kette"]["drehung"]),
                         _S["kette"]["drehung"], False),
    "J102": _aus_vertrag("J102", S.HOF(FP_HDR_1X02, _S["kette"]["pin1"],
                                       _S["kette"]["drehung"]),
                         _S["kette"]["drehung"], False, unten=True),
    "J103": _aus_vertrag("J103", S.HOF(FP_SKT_2X02, _S["leistung"]["pin1"],
                                       _S["leistung"]["drehung"]),
                         _S["leistung"]["drehung"], False),
    "J104": _aus_vertrag("J104", S.HOF(FP_HDR_2X02, _S["leistung"]["pin1"],
                                       _S["leistung"]["drehung"]),
                         _S["leistung"]["drehung"], False, unten=True),

    # 2. MCU-Nest links oben, unter den Vertragspins des Stapelsteckers.
    "U100": Platz("U100", 15.00, 16.50, 7.70, 7.00, 0, False),
    "C14": Platz("C14", 23.70, 16.50, 3.76, 1.96, 0, False),
    "C15": Platz("C15", 28.40, 16.50, 3.76, 1.96, 0, False),
    "C16": Platz("C16", 23.70, 19.20, 3.76, 1.96, 0, False),
    "R15": Platz("R15", 28.40, 19.20, 3.70, 1.90, 0, False),
    "U102": Platz("U102", 15.00, 24.50, 4.56, 2.50, 0, False),
    "U103": Platz("U103", 20.60, 24.50, 2.90, 2.20, 0, False),
    "R7": Platz("R7", 15.00, 28.20, 3.70, 1.90, 0, False),
    "R8": Platz("R8", 19.70, 28.20, 3.70, 1.90, 0, False),
    "R9": Platz("R9", 24.40, 28.20, 3.70, 1.90, 0, False),
    "R10": Platz("R10", 29.10, 28.20, 3.70, 1.90, 0, False),
    "C13": Platz("C13", 15.00, 31.20, 3.76, 1.96, 0, False),
    "R5": Platz("R5", 19.70, 31.20, 3.70, 1.90, 0, False),
    "R20": Platz("R20", 24.40, 31.20, 3.70, 1.90, 0, False),
    "R21": Platz("R21", 29.10, 31.20, 3.70, 1.90, 0, False),

    # 3. Ketten-Flipflop links am Rand (Landepunkte der Leistung liegen
    # bei y 15,5..18 -- deshalb beginnt U101 erst bei y = 21).
    "U101": Platz("U101", 5.00, 21.00, 2.90, 2.20, 0, False),
    "C101": Platz("C101", 5.00, 24.20, 3.76, 1.96, 0, False),
    "R102": Platz("R102", 9.40, 24.20, 3.70, 1.90, 0, False),
    "C100": Platz("C100", 5.00, 27.10, 3.76, 1.96, 0, False),
    "R13": Platz("R13", 9.40, 27.10, 3.70, 1.90, 0, False),
    "R100": Platz("R100", 5.00, 30.00, 3.70, 1.90, 0, False),
    "R101": Platz("R101", 9.30, 30.00, 3.70, 1.90, 0, False),
    "R104": Platz("R104", 5.00, 32.90, 3.70, 1.90, 0, False),
    "R105": Platz("R105", 9.30, 32.90, 3.70, 1.90, 0, False),

    # 4. Notaus-Band ueber der unteren Kante.
    "R16": Platz("R16", 5.00, 35.80, 4.56, 2.26, 0, False),
    "R17": Platz("R17", 10.60, 35.80, 4.56, 2.26, 0, False),
    "R18": Platz("R18", 16.20, 35.80, 4.56, 2.26, 0, False),
    "R19": Platz("R19", 21.80, 35.80, 4.56, 2.26, 0, False),
    "U3": Platz("U3", 27.50, 35.80, 2.90, 2.20, 0, False),
    "U6": Platz("U6", 31.40, 35.80, 2.90, 2.20, 0, False),
    "U7": Platz("U7", 35.30, 35.80, 2.90, 2.20, 0, False),
    "U4": Platz("U4", 4.50, 38.90, 10.90, 7.20, 0, False),
    "U5": Platz("U5", 16.00, 38.90, 10.90, 7.20, 0, False),
    "D1": Platz("D1", 27.50, 38.90, 13.80, 6.70, 0, False),

    # 1. 24-V-Strang rechts.
    "U1": Platz("U1", 36.00, 22.00, 7.80, 5.50, 0, False),
    "C11": Platz("C11", 36.00, 18.90, 3.76, 1.96, 0, False),
    # C9/C10 GEDREHT als "Harfe" (2026-09-02): liegend zwangen beide
    # Caps alle vier Ladungspumpen-Anschluesse (VM/VCP/CPH/CPL, Pins
    # 11-14) kreuzend durch die 2,9-mm-Gasse zwischen U1 und den Caps
    # -- nachweislich unloesbar (VCP-Band kollidierte mit jeder
    # moeglichen 1,0-mm-Kappe des VM-Halses). Stehend, mit den
    # Ziel-Pads in derselben y-Reihenfolge wie die Pins (CPL oben,
    # dann CPH, VCP, VM), kreuzt keine der vier Bahnen eine andere.
    "C9": Platz("C9", 48.02, 22.7325, 1.96, 3.76, 90, False),
    # C10 NICHT hoeher schieben: der Versuch (y-0,4, fuer ein
    # breiteres VCP-Fenster) liess freerouting deterministisch in
    # Durchgang 3 endlos kreisen -- vierter Haenger-Fund, Ursache
    # unklar, Reproduktion: C10-Platz 45.32/20.2575. Das VCP-Fenster
    # schafft stattdessen die abgesenkte /+24V-Bahn (s. PRE_TRACKS).
    "C10": Platz("C10", 45.32, 20.6575, 1.96, 3.76, 90, False),
    "R11": Platz("R11", 44.20, 29.80, 3.70, 1.90, 0, False),
    "R12": Platz("R12", 48.60, 29.80, 3.70, 1.90, 0, False),
    "Q1": Platz("Q1", 44.80, 32.60, 11.10, 7.00, 0, False),

    # Klemmenkante. J3 liegt QUER (Drehung 90): senkrecht saesse direkt
    # ueber seinem obersten Pad ein Stapel-Landepunkt (Reihe y = 49,54).
    "J3": Platz("J3", 7.60, 55.40, 11.16, 3.54, 90, True),
    "J5": Platz("J5", 20.00, 47.20, 11.17, 12.20, 0, True),
    "C12": Platz("C12", 33.00, 50.00, 8.50, 8.50, 0, True),
}

# --- Pflicht-Kennzeichnung (stack_spec.LAYOUT_AUFLAGEN) --------------
# Dieselben Marken wie auf der Sockelplatine: links neben Pin 1 des
# Stapelsteckers, "KLEMMEN" an der unteren Kante -- dort ist rechts
# von C12 der Streifen x 43..58 frei.
PIN1_MARKE = (5.3, 11.8)
KLEMMEN_POS = (44.0, 58.6)

# --- Waermepfad des DRV8876 ------------------------------------------
# Der Grund dieser Neuauflage: unter dem Treiber bleibt die
# B.Cu-Masseflaeche durchgehend, dort muenden seine zwoelf Waermevias.
# U1-Hof plus 1 mm Rand; Bahnen und fremde Vias verboten, Guss erlaubt.
RULE_AREAS = (
    ("Waermepfad DRV8876", ("B.Cu",),
     (35.00, 21.00, 44.80, 28.50), frozenset(("bahnen", "vias"))),
)

# --- GND-Vorverdrahtung ----------------------------------------------
# Dieselben Stummel wie auf der Sockelplatine, aus demselben Grund:
# welcher Massepin des Stapelsteckers strandet, wechselt mit jedem
# Router-Lauf -- die Klasse wird vorab geschlossen (Herleitung bei
# spec_sockel.PRE_TRACKS; Geometrie gegen J101-Pads nachgerechnet:
# engster Punkt 0,71 mm gegen benoetigte 0,325).
_J100_LAGEN = S.PAD_LAGEN(_S["stapel"]["footprints"][0],
                          _S["stapel"]["pin1"], _S["stapel"]["drehung"])
_STUMMEL_ENDE_Y = 6.5


def _gnd_stummel():
    aus = []
    for pin in sorted(p for p, r in S.PIN_ROLLE.items() if r == "GND"):
        x, y = _J100_LAGEN[pin]
        if abs(y - 10.46) < 0.01:
            punkte = [(x, y), (x, _STUMMEL_ENDE_Y)]
        else:
            punkte = [(x, y), (x + 1.27, y - 1.27),
                      (x + 1.27, _STUMMEL_ENDE_Y)]
        aus.append(("GND", "F.Cu", punkte))
    return tuple(aus)


# Zusaetzlich zu den GND-Stummeln:
#
# * Die zusammengebundenen Eingaenge des Dual-NAND (U102, VSSOP-8,
#   0,5-mm-Raster): /SEL_OUT liegt auf Pad 1 UND 2, /NQ auf Pad 6 UND
#   7. freerouting kann benachbarte Pads in diesem Raster nicht
#   verbinden (Padluecke 0,20 mm laesst keine Bahn samt Abstand zu) --
#   die direkte Bindung wird deshalb vorab gelegt, als
#   Pad-zu-Pad-Segment, aufgeloest von build.pre_tracks().
#
# * Halsstuecke an den Leistungspins des DRV8876: die 1,0-mm-Bahnen
#   der Leistungsklasse passen nicht an die 0,45 mm schmalen Pads
#   (der Nachbarpin laege in der Bahn). Ein kurzes 0,40-mm-Halsstueck
#   (breiter geht nicht: Nachbarpad-Abstand 0,425 mm) fuehrt vom Pad
#   ins Freie; dort uebernimmt die volle Breite. Unterbreite je Netz
#   unter 2 mm halten (pcb_checks meldet ab 2 mm) -- die Laenge ist
#   der Kompromiss zwischen Engstelle und Waermeentwicklung.
#   Zwischenpunkte EXAKT auf die Pad-Mitten legen (25,725 statt
#   25,72): ein um 5 um schiefes Halsstueck liess freerouting vor
#   Durchgang 1 endlos haengen -- build.pre_tracks() weist schiefe
#   Segmente seither ab.
#
# * Fuenf Verbindungen blieben in JEDEM Router-Lauf offen (auch mit
#   99 Durchgaengen; der Router gibt vorher auf) -- sie werden wie die
#   GND-Stummel vorab reserviert, dann sind die Korridore garantiert:
#
#   - /+24V und /Out2 an U1: die Pads 10/11 liegen 0,65 mm auseinander,
#     zwei 1,0-mm-Fortsetzungen brauchen aber 1,2 mm Kappenabstand --
#     direkt nebeneinander ist das unerfuellbar, der Router fand nie
#     eine Loesung. Die Vorverdrahtung staffelt die Kappen schraeg
#     ((44,60|25,725) gegen (44,35|26,975) = 1,28 mm): /+24V laeuft
#     gerade in das VM-Pad des gedrehten C9 (Harfe, s. PLACEMENT),
#     /Out2 knickt nach unten ab und faellt im freien Streifen
#     zwischen D1 und der Naehvia-Spalte x=43,25 zur Klemme J5. Alle
#     Abstaende gegen U1-Pads (Kante 43,55), die gedrehten Caps,
#     R11 (Pad ab 44,45), D1 und die Naehvias nachgerechnet; engste
#     Stellen: Out2-Diagonale zu Pad 9 = 0,242, Vertikale x=42,2 zu
#     den Naehvias = 0,25 (Kante-Kante).
#   - das NAND-Nest: U102-3 -> U100-6 (/NRST) links um die Padspalte
#     herum (x=14,5), U102-8 -> U103-5 (3V3) oben ueber U103 hinweg
#     (y=23,8) und weiter bis zum Abblockkondensator C16, U102-5 ->
#     U103-1 (/FLASH_MODE) unten herum und durch die Gasse x=20,3
#     (Kante-Kante 0,277 zu U103). Die drei Routen kreuzen einander
#     nicht und lassen die Escapes der uebrigen U102/U103-Pads frei.
#     Die NRST-Ausfahrt am Pad ist 0,20 statt 0,25 breit: mit 0,25
#     waere der Abstand zu den Nachbarpads EXAKT 0,200 -- an solchen
#     Grenzwert-Draehten haengt sich freerouting beim Import auf
#     (zweiter Haenger-Fund nach dem Schiefstand); 0,20 breit bleiben
#     0,225 Luft.
_HALS = 0.40
_LEISTUNG = 1.00
PRE_TRACKS = _gnd_stummel() + (
    ("/SEL_OUT", "F.Cu", (("PAD", "U102", "1"), ("PAD", "U102", "2"))),
    ("/NQ", "F.Cu", (("PAD", "U102", "6"), ("PAD", "U102", "7"))),
    # U1 sitzt bei Hofmitte (39,90|24,75); Pads rechts x = 42,80,
    # links x = 37,00 (Padreihen +-2,90 von der Mitte).
    ("/+24V", "F.Cu", (("PAD", "U1", "11"), (44.60, 25.725)), _HALS),
    # Abgesenkt auf y=25,4 zwischen den Caps: so bleibt zwischen der
    # Bahn (Nordkante 24,9) und dem C10-1-Pad (Suedkante 24,17) ein
    # 0,73-mm-Fenster, durch das der Router /VCP nach Osten fuehrt.
    # Der letzte Knick liegt VOR der Pad-Westkante (48,275): ein
    # Drahtknick im Pad-Kupfer abseits des Zentrums war der naechste
    # freerouting-Import-Haenger.
    # Endhoehe 25,65 = VM-Pad des nach Sueden gerueckten C9: dessen
    # VCP-Pad liegt damit auf 23,575 -- GLEICHE Hoehe wie das
    # CPH-Pad von C10 (Spalten versetzt). Vorher lag das VCP-Ziel
    # UEBER dem CPH-Ziel, obwohl der VCP-Pin UNTER dem CPH-Pin sitzt:
    # die beiden Bahnen mussten sich kreuzen, und der Router liess in
    # jedem Lauf eine von beiden (oder ein Nachbarsignal) liegen.
    ("/+24V", "F.Cu", ((44.60, 25.725), (45.25, 25.725), (45.575, 25.40),
                       (47.775, 25.40), (48.025, 25.65),
                       ("PAD", "C9", "1")), _LEISTUNG),
    ("/Out2", "F.Cu", (("PAD", "U1", "10"),
                       (43.75, 26.375), (44.35, 26.975)), _HALS),
    ("/Out2", "F.Cu", ((44.35, 26.975), (44.35, 28.70), (42.20, 28.70),
                       (42.20, 48.50), (28.12, 48.50),
                       ("PAD", "J5", "2")), _LEISTUNG),
    ("/Out1", "F.Cu", (("PAD", "U1", "8"), (35.20, 27.025)), _HALS),
    # /+24V-Ast zur Notaus-Speisung R16/R17: blieb als letzte Kante
    # im Wuerfelspiel des Routers haengen. In Leistungsbreite ueber
    # die R-Zeile (y=35,0; Pads erst ab 36,055), durch die Gasse
    # R19/U3 (Pad-zu-Pad 1,52 -- fuer 1,0 mm plus 2x0,2 reicht es
    # mit 0,26 je Seite), suedlich an U5-4 vorbei zu D1-1.
    # y=35,3: das Fenster zwischen der Kennwiderstands-Zeile
    # R104/R105 (Pads bis y34,55 -- bei 35,0 lag die Bahn AUF
    # R105-2, Kurzschluss /+24V//ID1) und der R16-19-Zeile (ab
    # 36,055): 1,505 mm fuer 1,0 plus 2x0,25.
    ("/+24V", "F.Cu", (("PAD", "R17", "1"),
                       (11.418, 35.30), (26.86, 35.30), (26.86, 39.20),
                       (30.00, 39.20), ("PAD", "D1", "1")), _LEISTUNG),
    # /VCP war nach dem CPH/VCP-Ordnungsfix das letzte Gassen-Signal,
    # das der Router liegen liess: durch das 0,73-Fenster zwischen
    # C10-1 (Suedkante 24,17) und der /+24V-Bahn (Nordkante 24,9),
    # dann von Sueden in C9-2 (Knick ausserhalb des Pads).
    # CPH/CPL ebenfalls festgelegt: auch nach dem Ordnungsfix liess
    # der Router mal CPH, mal CPL liegen (die Gasse bleibt sein
    # schwerstes Gebiet). Beide Bahnen unter der VCP-Bahn hindurch,
    # alle Ecken gegen U1-Padecken (0,37/0,44) und das Naehvia
    # (43,25|22,5) gerechnet.
    ("/CPH", "F.Cu", (("PAD", "U1", "13"),
                      (43.75, 24.425), (44.45, 23.725), (45.20, 23.725),
                      (45.35, 23.575), ("PAD", "C10", "1"))),
    ("/CPL", "F.Cu", (("PAD", "U1", "14"),
                      (43.65, 23.775), (44.825, 22.60), (45.86, 22.60),
                      (46.30, 22.16), ("PAD", "C10", "2"))),
    ("/VCP", "F.Cu", (("PAD", "U1", "12"),
                      (43.90, 25.075), (44.475, 24.50), (49.00, 24.50),
                      ("PAD", "C9", "2"))),
    ("/NRST", "F.Cu", (("PAD", "U102", "3"), (14.50, 26.00)), 0.20),
    ("/NRST", "F.Cu", ((14.50, 26.00), (14.50, 20.325),
                       ("PAD", "U100", "6"))),
    # 3V3 U102-8 -> U103-5 auf der RUECKSEITE: die fruehere F.Cu-Bahn
    # quer durch die Nordschneise (y=23,8) sperrte dem Router die
    # einzige West-Ost-Passage des Nests -- FLASH-Stapelast, BOOT0
    # und ID-Signale strandeten reihum. Zwei Vias kosten weniger als
    # die Schneise.
    ("3V3", "F.Cu", (("PAD", "U102", "8"), (18.68, 24.10))),
    ("3V3", "B.Cu", ((18.68, 24.10), (23.35, 24.10), (23.90, 24.65),
                     (23.90, 24.95))),
    ("3V3", "F.Cu", ((23.90, 24.95), ("PAD", "U103", "5"))),
    # Anbindung des NAND-Abblock-C16 an die 3V3-Schiene: ohne sie
    # strandete C16-1 im verstopften Nest. Als EIGENER Zug von Pad zu
    # Pad (C16-1 -> R15-1, beide 3V3), nicht als T-Abzweig einer
    # vorhandenen Bahn: zwei Drahtzuege, die sich nur in einem Punkt
    # beruehren, sind der dritte gefundene freerouting-Haenger
    # (Import-Endlosschleife wie beim Schiefstand und beim
    # Grenzwert-Abstand). Pads als Treffpunkte sind unkritisch.
    # Der Knick vor R15-1 liegt SUEDLICH der Pad-Kante (20,85): ein
    # Drahtknick im Pad-Kupfer abseits des Zentrums haengt freerouting
    # auf (dieselbe Klasse wie beim /+24V-Knick vor C9-1).
    ("3V3", "F.Cu", (("PAD", "C16", "1"),
                     (24.5425, 21.30), (28.90, 21.30), (29.25, 20.95),
                     ("PAD", "R15", "1"))),
    # FLASH in der WESTSPUR der Gasse (x=19,68, Luft 0,25 zu den
    # U102-Pads dank Feinraster-Ausnahme): die Ostspur (x=20,35)
    # gehoert der /SEL_OUT-Abfahrt von U103-2 -- mit FLASH auf x=20,3
    # war U103-2 auf F.Cu vollstaendig eingemauert (westlich die
    # Bahn, drumherum Pads/Koerper) und blieb in jedem Lauf offen.
    ("/FLASH_MODE", "F.Cu", (("PAD", "U102", "5"),
                             (18.68, 27.20), (19.68, 27.20),
                             (19.68, 24.35), (21.212, 24.35),
                             ("PAD", "U103", "1"))),
    # /SEL_OUT von U103-2: westlich raus, in der Ostspur nach Sueden,
    # per Via auf die Rueckseite, quer unters Nest und noerdlich von
    # U102-1 zurueck nach oben -- der einzige kreuzungsfreie Weg
    # (jede F.Cu-Variante kreuzt eine andere Vorverdrahtung oder eine
    # TSSOP-Padreihe; Herleitung bei build.pre_vias).
    ("/SEL_OUT", "F.Cu", (("PAD", "U103", "2"),
                          (20.35, 25.60), (20.35, 27.60))),
    ("/SEL_OUT", "B.Cu", ((20.35, 27.60), (18.98, 27.60),
                          (15.88, 24.50), (15.88, 23.65))),
    ("/SEL_OUT", "F.Cu", ((15.88, 23.65), ("PAD", "U102", "1"))),
    # /NFAULT-Ast zum Treiber: U1-4 blieb in jedem Lauf offen (die
    # Westspalte von U1 ist von den Nachbarsignalen zugebaut). Die
    # Nordschneise y=22,275 ist frei: noerdlich der 3V3-Bahn (y23,8),
    # suedlich von C16/R15 (Pads bis y20,905), dann schraeg ans Pad.
    # Nach kurzem Zeilen-Exit auf y=22,925 absenken: auf der
    # Pad-Zeile (22,275) blieb zwischen dieser Bahn und dem
    # C16-R15-Zug (y=21,3) nur 0,075 mm -- die U100-13-Ausfahrt
    # (/IPROPI, y=21,625) war eingemauert.
    # y=23,2 statt 22,925: die erste Absenkung landete mit exakt
    # 0,425 Mittenabstand AUF dem Naehvia (28,25|22,5) -- Kurzschluss
    # GND//NFAULT, von der DRC gefangen. 0,7 ist frei.
    ("/NFAULT", "F.Cu", (("PAD", "U100", "12"),
                         (23.00, 22.275), (23.925, 23.20),
                         (33.65, 23.20), (34.875, 24.425),
                         ("PAD", "U1", "4"))),
    # /ID0: U100-7 sitzt hinter der NRST-Bahn (x=14,5) fest -- kein
    # Westausgang. Ostausgang unter den TSSOP-Koerper, per Via auf die
    # Rueckseite, diagonal am Nest vorbei (suedlich der Leistungs-
    # Steckerpads y15,5..18!) und bei R100-1 zurueck nach oben.
    ("/ID0", "F.Cu", (("PAD", "U100", "7"), (17.50, 20.975))),
    ("/ID0", "B.Cu", ((17.50, 20.975), (13.50, 20.975),
                      (5.85, 28.625), (5.85, 29.60))),
    ("/ID0", "F.Cu", ((5.85, 29.60), ("PAD", "R100", "1"))),
    # /ID1 sitzt einen Pad weiter (U100-8) in derselben Falle wie
    # /ID0 -- gleiche Loesung, parallel versetzt (Diagonale 0,83 vom
    # Naehvia (13,25|22,5) entfernt, ID0-Zuege 1,06 senkrecht).
    ("/ID1", "F.Cu", (("PAD", "U100", "8"), (18.10, 21.625))),
    ("/ID1", "B.Cu", ((18.10, 21.625), (15.30, 21.625),
                      (10.15, 26.775), (10.15, 29.65))),
    ("/ID1", "F.Cu", ((10.15, 29.65), ("PAD", "R101", "1"))),
    # /+24V-Ast zum Abblock-C11 (noerdlich von U1): auf F.Cu ist jede
    # Zufahrt von der 24-V-Schiene durch die CPH/VCP-Querbahnen der
    # Gasse versperrt. Rueckseite: noerdlich der Waermepfad-
    # Regelflaeche (y<21) nach Osten, oestlich von ihr (x>44,8) nach
    # Sueden, Via mitten auf die +24V-Fettbahn (y25,4; gleiches Netz).
    ("/+24V", "F.Cu", (("PAD", "C11", "2"), (39.50, 19.88))),
    ("/+24V", "B.Cu", ((39.50, 19.88), (45.20, 19.88), (46.50, 21.18),
                       (46.50, 25.40))),
)

# Lagenwechsel der /SEL_OUT-Vorverdrahtung (s. Kommentar dort).
PRE_VIAS = (
    ("/SEL_OUT", 20.35, 27.60),
    ("/SEL_OUT", 15.88, 23.65),
    ("/ID0", 17.50, 20.975),
    ("/ID0", 5.85, 29.60),
    ("/ID1", 18.10, 21.625),
    ("/ID1", 10.15, 29.65),
    ("3V3", 18.68, 24.10),
    ("3V3", 23.90, 24.95),
    # Das zweite /+24V-Via sitzt MITTEN AUF der Fettbahn (gleiches
    # Netz) -- das ist der Anschluss, kein Versehen.
    ("/+24V", 39.50, 19.88),
    ("/+24V", 46.50, 25.40),
)

# --- Masseflaechen vernaehen -----------------------------------------
# Dasselbe Raster wie auf der Sockelplatine, mit den Regeln dieser
# Platine: Kante, M3, Hoefe -- und die Waermepfad-Regelflaeche, die
# fremde Vias verbietet (die Naehte sind fremde Vias).
STITCH_RASTER = 7.5
_STITCH_VIA_R = 0.5


def _naht_erlaubt(vx, vy):
    rand = EDGE_CLEARANCE + _STITCH_VIA_R
    if not (rand <= vx <= BOARD_W - rand and rand <= vy <= BOARD_H - rand):
        return False
    for hx, hy in M3_HOLES:
        if (vx - hx) ** 2 + (vy - hy) ** 2 < (M3_KEEPOUT / 2.0) ** 2:
            return False
    for p in PLACEMENT.values():
        if (p.x - _STITCH_VIA_R < vx < p.x + p.w + _STITCH_VIA_R
                and p.y - _STITCH_VIA_R < vy < p.y + p.h + _STITCH_VIA_R):
            return False
    for _n, _l, (x0, y0, x1, y1), verbote in RULE_AREAS:
        if "vias" in verbote and (x0 - _STITCH_VIA_R < vx < x1 + _STITCH_VIA_R
                                  and y0 - _STITCH_VIA_R < vy
                                  < y1 + _STITCH_VIA_R):
            return False
    return True


def _naehte():
    aus = []
    n_x = int((BOARD_W - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    n_y = int((BOARD_H - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    ox = (BOARD_W - (n_x - 1) * STITCH_RASTER) / 2.0
    oy = (BOARD_H - (n_y - 1) * STITCH_RASTER) / 2.0
    for iy in range(n_y):
        for ix in range(n_x):
            vx = round(ox + ix * STITCH_RASTER, 3)
            vy = round(oy + iy * STITCH_RASTER, 3)
            if _naht_erlaubt(vx, vy):
                aus.append((vx, vy))
    return tuple(aus)


# Gezielte Zusatznaehte fuer die Gussfragmente der Oberseite: das
# 7,5er-Raster wird in der Brettmitte fast vollstaendig von den
# Hof-Filtern verschluckt, und die vielen Bahnen zerschneiden den
# F.Cu-Guss dort in ein Dutzend Stuecke ohne Anbindung (die DRC
# meldete sie als fehlende Verbindungen der Flaeche mit sich selbst).
# Punkte maschinell gesucht: im jeweiligen Fragment, mindestens
# 0,5 mm zu jedem Pad, 0,9 zu jedem Via, ausserhalb Waermepfad-
# Regelflaeche, M3-Hoefen und Randstreifen.
STITCH_EXTRA = (
    # (29,0|38,25) und (15,5|34,5) aus dem ersten Suchlauf kollidierten
    # mit der /+24V-Bahn nach R17 (die Suche prueft Pads und Vias,
    # nicht die eigene Vorverdrahtung): einmal 0,15 Abstand, einmal
    # Beruehrung. Ersatzpunkte von Hand gerechnet; (28,113|38,15)
    # bindet den U3-GND-Zwickel direkt unter dessen Massepad an.
    (21.50, 42.50), (32.25, 38.75), (28.113, 38.15), (15.50, 34.00),
    (24.00, 34.10), (7.00, 29.50), (19.25, 30.75), (26.00, 25.50),
    (15.25, 27.50), (18.75, 20.75), (16.75, 7.50), (18.00, 6.50),
)

STITCH_VIAS = _naehte() + STITCH_EXTRA

# --- Netzklassen -----------------------------------------------------
# /PWR24V (Einspeisung vor Q1), /+24V (Schiene nach Q1) und die beiden
# Motorausgaenge tragen den Motorstrom (bis 2,5 A, Chopping-Grenze des
# DRV8876 mit R5 = 1,3 k). autoroute.dsn_netzklassen() bricht ab, wenn
# eines davon in der DSN fehlt.
POWER_NETS = ("/PWR24V", "/+24V", "/Out1", "/Out2")

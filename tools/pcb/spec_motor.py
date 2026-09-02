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
    "C9": Platz("C9", 46.20, 22.00, 3.76, 1.96, 0, False),
    "C10": Platz("C10", 46.20, 24.60, 3.76, 1.96, 0, False),
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
#   ins Freie; dort uebernimmt der Router mit voller Breite. Kuerzer
#   als 2 mm, damit die Bahnbreitenpruefung (pcb_checks, meldet ab
#   2 mm Unterbreite je Netz) nicht anschlaegt -- die Laenge ist der
#   Kompromiss zwischen Engstelle und Waermeentwicklung.
_HALS = 0.40
PRE_TRACKS = _gnd_stummel() + (
    ("/SEL_OUT", "F.Cu", (("PAD", "U102", "1"), ("PAD", "U102", "2"))),
    ("/NQ", "F.Cu", (("PAD", "U102", "6"), ("PAD", "U102", "7"))),
    # U1 sitzt bei Hofmitte (39,90|24,75); Pads rechts x = 42,80,
    # links x = 37,00 (Padreihen +-2,90 von der Mitte).
    ("/+24V", "F.Cu", (("PAD", "U1", "11"), (44.60, 25.72)), _HALS),
    ("/Out2", "F.Cu", (("PAD", "U1", "10"), (44.60, 26.37)), _HALS),
    ("/Out1", "F.Cu", (("PAD", "U1", "8"), (35.20, 27.02)), _HALS),
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


STITCH_VIAS = _naehte()

# --- Netzklassen -----------------------------------------------------
# /PWR24V (Einspeisung vor Q1), /+24V (Schiene nach Q1) und die beiden
# Motorausgaenge tragen den Motorstrom (bis 2,5 A, Chopping-Grenze des
# DRV8876 mit R5 = 1,3 k). autoroute.dsn_netzklassen() bricht ab, wenn
# eines davon in der DSN fehlt.
POWER_NETS = ("/PWR24V", "/+24V", "/Out1", "/Out2")

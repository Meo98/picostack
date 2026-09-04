"""Gemeinsame Platinenbeschreibung der Dimmer-Module (1/3/4 Kanaele).

beschreibung(kanaele) liefert alle Attribute, die build.py/geometry.py/
autoroute.py von einem spec-Modul erwarten; spec_dimmer1/3/4.py sind
Dreizeiler, die das Ergebnis in ihren Modul-Namensraum heben.

WAS UEBERNOMMEN IST. Das MCU-Nest (U100/U101/U102/U103 samt RC-Glied,
Kennwiderstaenden und allen Steckern) steht WOERTLICH auf den
Motormodul-Plaetzen -- und mit ihm jede Nest-Vorverdrahtung, die dort
muehsam erkaempft wurde (NRST-Westbahn, SEL_OUT/ID0/ID1 ueber die
Rueckseite, 3V3-Querzug, U100-5-Masseausleitung; Herleitungen in
spec_motor.py). Ein Nest, das schon einmal vollstaendig verlegbar war,
wird nicht neu gewuerfelt.

WAS NEU IST. Der Leistungsteil sitzt rechts OBEN (der Platz des
DRV8876 ist frei), die Kanalzone unten: eine Zeile TO-252-FETs buendig
UEBER ihren Schraubklemmen (kuerzester Drain-Weg), die Freilaufdioden
darueber. Vier 2P-Klemmen fuellen die Klemmenkante fast vollstaendig
(4 x 11,17 mm Hof + Luecken = 47,1 mm); die Ketten-Landeecke rechts
unten bleibt frei, und die Klemmen-PADS liegen wie beim Motormodul
suedlich des Verdreht-Landepunktstreifens (y 45,5..51 -- die Hoefe
duerfen ihn ueberspannen, Kupfer nicht).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S                     # noqa: E402
from spec_sockel import Platz, _aus_vertrag   # noqa: E402
import spec_motor as M                     # noqa: E402  (Nest-Plaetze)

# 3,5-mm-Klemmen statt der 5,08er des Motormoduls: vier 11,17-mm-
# Hoefe passten nicht zwischen den M3-Freihaltekreis (bis x=7,5) und
# die Ketten-Landeecke (nutzbar 40,8 mm, noetig 46,5). Die
# PT-1,5/2-3,5-H traegt laut Phoenix 13,5 A -- fuer 3-A-LED-Kanaele
# mehr als genug. Hof 8,0 x 8,6, Pads bei rel (+2,245|+3,605).
FP_KLEMME_2 = ("TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal")
FP_TO252 = "Package_TO_SOT_SMD:TO-252-3_TabPin2"
# D_SMC (Standard-Padset, Hof 9,8 x 6,7) statt des Handloet-Padsets
# vom Motormodul (13,8 x 6,7): die Dimmer-Dioden werden maschinell
# bestueckt, und mit dem Handloet-Hof passten keine vier Freilauf-
# dioden mehr aufs Brett (geometry.check_all meldete jede Zeile).
FP_SMC = "Diode_SMD:D_SMC"
FP_CP = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"

#: x-Anker der vier Kanalspalten (Klemmen und FETs buendig).
_SPALTE = (1.70, 13.50, 25.30, 37.10)


def _nest_und_stecker():
    """Plaetze, die woertlich vom Motormodul uebernommen sind."""
    refs = ("J100", "J101", "J102", "J103", "J104",
            "U100", "U101", "U102", "U103",
            "C100", "C101", "R102",
            "R100", "R101", "R104", "R105")
    return {r: M.PLACEMENT[r] for r in refs}


def beschreibung(kanaele):
    assert kanaele in (1, 3, 4)
    platz = dict(_nest_und_stecker())

    # Leistungsteil in der rechten Spalte (beim Motormodul sass hier
    # der DRV8876-Strang): Gate-Teiler oben, Verpolungsschutz,
    # Stuetz-Elko; TVS D10 im Mittelfeld neben der Diodenzeile.
    platz["R11"] = Platz("R11", 44.00, 15.50, 3.70, 1.90, 0, False)
    platz["R12"] = Platz("R12", 48.70, 15.50, 3.70, 1.90, 0, False)
    platz["Q10"] = Platz("Q10", 45.00, 21.50, 11.10, 7.00, 0, False)
    platz["C12"] = Platz("C12", 49.00, 29.50, 8.50, 8.50, 0, True)
    platz["D10"] = Platz("D10", 24.20, 21.80, 9.80, 6.70, 0, False)

    # Gate-Vorwiderstaende und -Pulldowns in zwei Zeilen.
    for n in range(1, kanaele + 1):
        platz["RG%d" % n] = Platz("RG%d" % n, 24.0 + (n - 1) * 4.7, 15.50,
                                  3.70, 1.90, 0, False)
        platz["RP%d" % n] = Platz("RP%d" % n, 24.0 + (n - 1) * 4.7, 18.60,
                                  3.70, 1.90, 0, False)

    # Kanalzone: Freilaufdioden-Zeile, FET-Zeile buendig ueber den
    # Klemmen (kuerzester Drain-Weg), D4 in der zweiten Reihe.
    diode_platz = ((13.70, 29.20), (24.15, 29.20), (34.60, 29.20),
                   (34.60, 21.70))
    for n in range(1, kanaele + 1):
        dx, dy = diode_platz[n - 1]
        platz["D%d" % n] = Platz("D%d" % n, dx, dy, 9.80, 6.70, 0, False)
        platz["Q%d" % n] = Platz("Q%d" % n, _SPALTE[n - 1], 36.50,
                                 11.10, 7.00, 0, False)
        # Hof-y = 50,0 legt die Klemmen-PADS auf y = 53,6 -- dieselbe
        # Hoehe wie die Motorklemme, sicher suedlich des Verdreht-
        # Landepunktstreifens.
        platz["J%d" % (4 + n)] = Platz("J%d" % (4 + n),
                                       8.0 + (n - 1) * 8.6, 50.00,
                                       8.00, 8.60, 0, True)

    footprints = dict(M.FOOTPRINTS)
    for r in ("C9", "C10", "C11", "C13", "C14", "C15", "C16",
              "D1", "J3", "J5", "Q1",
              "R5", "R7", "R8", "R9", "R10", "R13", "R15",
              "R16", "R17", "R18", "R19", "R20", "R21",
              "U1", "U3", "U4", "U5", "U6", "U7"):
        footprints.pop(r, None)
    footprints["Q10"] = FP_TO252
    footprints["D10"] = FP_SMC
    footprints["C12"] = FP_CP
    for n in range(1, kanaele + 1):
        footprints["Q%d" % n] = FP_TO252
        footprints["D%d" % n] = FP_SMC
        footprints["RG%d" % n] = M.FOOTPRINTS["R11"]
        footprints["RP%d" % n] = M.FOOTPRINTS["R11"]
        footprints["J%d" % (4 + n)] = FP_KLEMME_2

    # Nest-Vorverdrahtung des Motormoduls: alles, was am Nest haengt,
    # gilt hier unveraendert (die Plaetze sind identisch). Die
    # Leistungs-Eintraege des Motors (Halsstuecke, Ladungspumpe,
    # Out1/Out2, NFAULT ueber R13) haben hier keine Entsprechung.
    nest_netze = ("GND", "/SEL_OUT", "/NQ", "/NRST", "3V3",
                  "/FLASH_MODE", "/ID0", "/ID1")
    pre_tracks = tuple(e for e in M.PRE_TRACKS if e[0] in nest_netze)
    pre_vias = tuple(v for v in M.PRE_VIAS
                     if v[0] in ("/SEL_OUT", "/ID0", "/ID1", "3V3", "GND"))

    naehte = _naehte(platz)

    return {
        "BOARD_W": S.BOARD_W, "BOARD_H": S.BOARD_H,
        "CORNER_R": S.CORNER_R, "M3_DRILL": S.M3_DRILL,
        "M3_HOLES": S.M3_HOLES, "M3_KEEPOUT": S.M3_KEEPOUT,
        "COURTYARD_GAP": M.COURTYARD_GAP,
        "EDGE_CLEARANCE": M.EDGE_CLEARANCE,
        "IST_MODUL": True,
        "FOOTPRINTS": footprints,
        "PLACEMENT": platz,
        "PRE_TRACKS": pre_tracks,
        "PRE_VIAS": pre_vias,
        "RULE_AREAS": (),
        "STITCH_RASTER": M.STITCH_RASTER,
        "STITCH_VIAS": naehte,
        "PIN1_MARKE": M.PIN1_MARKE,
        "KLEMMEN_POS": (55.5, 58.0),
        "POWER_NETS": tuple(["/PWR24V", "/+24V"]
                            + ["/LED%d" % n for n in range(1, kanaele + 1)]),
    }


def _naehte(platz):
    """Naht-Raster wie beim Motormodul, gegen DIESE Plaetze gefiltert."""
    via_r = 0.5
    aus = []
    n_x = int((S.BOARD_W - 2 * M.EDGE_CLEARANCE) / M.STITCH_RASTER)
    n_y = int((S.BOARD_H - 2 * M.EDGE_CLEARANCE) / M.STITCH_RASTER)
    ox = (S.BOARD_W - (n_x - 1) * M.STITCH_RASTER) / 2.0
    oy = (S.BOARD_H - (n_y - 1) * M.STITCH_RASTER) / 2.0
    for iy in range(n_y):
        for ix in range(n_x):
            vx = round(ox + ix * M.STITCH_RASTER, 3)
            vy = round(oy + iy * M.STITCH_RASTER, 3)
            rand = M.EDGE_CLEARANCE + via_r
            if not (rand <= vx <= S.BOARD_W - rand
                    and rand <= vy <= S.BOARD_H - rand):
                continue
            if any((vx - hx) ** 2 + (vy - hy) ** 2
                   < (S.M3_KEEPOUT / 2.0) ** 2 for hx, hy in S.M3_HOLES):
                continue
            if any(p.x - via_r < vx < p.x + p.w + via_r
                   and p.y - via_r < vy < p.y + p.h + via_r
                   for p in platz.values()):
                continue
            aus.append((vx, vy))
    return tuple(aus)

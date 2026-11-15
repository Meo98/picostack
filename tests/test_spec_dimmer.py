"""Platzierung der Dimmer-Module v3 gegen Vertrag und Regeln, KiCad-frei.

Prueft tools/pcb/spec_dimmer_basis.beschreibung(k) fuer k = 1, 3, 4:
  * geometry.check_all: keine Hof-Ueberlappung, nichts ueber der Kante,
    nichts im M3-Freihaltebereich
  * Vertragsplaetze J1/J2/J3 liegen exakt auf STECKER_POS
  * Klemmen in KLEMMENZONE, kantenbuendig, Kanalreihenfolge von links,
    Einspeisung ganz rechts (R1/R2)
  * nichts Hohes im Pico-Schatten, keine Teile in ANTENNE_FREI (R3/P5)
  * Platzierungsregeln P1-P4 als Hof-Abstaende
  * Slot-Matrix: je Signal vier Plaetze, Referenzen aus dem Vertrag
Rot-Nachweis: eine absichtlich verschobene Klemme und ein in die
Antennenzone geschobener Kondensator muessen anschlagen.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "tools"))
sys.path.insert(0, os.path.join(HIER, "..", "tools", "pcb"))

import geometry           # noqa: E402
import spec_dimmer_basis  # noqa: E402
import stack_spec as S    # noqa: E402
from platz import Platz, hof_abstand  # noqa: E402

fails = []


def check(label, bedingung, detail=""):
    if not bedingung:
        fails.append("%s%s" % (label, (" -- %s" % (detail,)) if detail else ""))


class _B:
    def __init__(self, d):
        self.__dict__.update(d)


def innerhalb(p, zone):
    x0, y0, x1, y1 = zone
    return (p.x >= x0 - 1e-6 and p.y >= y0 - 1e-6
            and p.x + p.w <= x1 + 1e-6 and p.y + p.h <= y1 + 1e-6)


def schneidet(p, zone):
    x0, y0, x1, y1 = zone
    return not (p.x + p.w <= x0 or x1 <= p.x or p.y + p.h <= y0 or y1 <= p.y)


HOCH = {"CP63": 7.7, "KLEMME": 8.5, "L6045": 4.5, "STAPEL20": 8.5, "STAPEL4": 8.5}

for k in (1, 3, 4):
    b = _B(spec_dimmer_basis.beschreibung(k))
    P = b.PLACEMENT
    tag = "Dimmer%d" % k

    bad = geometry.check_all(P, b)
    check("%s geometry.check_all" % tag, bad == [], bad)

    for ref, platz in b.VERTRAGSPLATZ.items():
        e = S.STECKER_POS[platz]
        p = P[ref]
        check("%s %s auf Vertragslage" % (tag, ref),
              p.rechteck() == e["flaeche"] and p.rot == e["drehung"], p)

    klemmen = ["J%d" % (4 + n) for n in range(1, k + 1)] + ["J90"]
    for ref in klemmen:
        p = P[ref]
        check("%s %s in KLEMMENZONE" % (tag, ref), innerhalb(p, S.KLEMMENZONE), p)
        check("%s %s kantenbuendig" % (tag, ref), abs(p.y + p.h - S.BOARD_H) < 1e-6, p)
        check("%s %s Oeffnung nach aussen" % (tag, ref),
              S.KLEMME_OEFFNUNG_GLOBAL(b.FOOTPRINTS[ref], p.rot) == (0.0, 1.0))
        check("%s %s nicht im Pico-Schatten" % (tag, ref), not schneidet(p, S.PICO_SCHATTEN))
    xs = [P["J%d" % (4 + n)].x for n in range(1, k + 1)]
    check("%s Kanalklemmen von links in Reihenfolge" % tag, xs == sorted(xs), xs)
    check("%s Einspeisung ganz rechts" % tag, P["J90"].x > max(xs))

    for ref, p in P.items():
        art = [a for a, (fp, _w, _h) in spec_dimmer_basis.FP.items()
               if fp == b.FOOTPRINTS[ref]]
        hoehe = HOCH.get(art[0], 2.0) if art else 2.0
        if schneidet(p, S.PICO_SCHATTEN) and ref not in ("J1", "J2"):
            check("%s %s unter dem Pico <= %.1f mm hoch"
                  % (tag, ref, S.BAUTEILHOEHE_PICO_SCHATTEN_MAX),
                  hoehe <= S.BAUTEILHOEHE_PICO_SCHATTEN_MAX, hoehe)
        check("%s %s <= %.1f mm hoch" % (tag, ref, S.BAUTEILHOEHE_OBEN_MAX),
              hoehe <= S.BAUTEILHOEHE_OBEN_MAX)
        if ref not in ("J1", "J2"):
            check("%s %s nicht in ANTENNE_FREI" % (tag, ref),
                  not schneidet(p, S.ANTENNE_FREI), p)

    # P1: Abblock-/Eingangskeramik am IC. P2: Spule und Freilauf am IC.
    R = S.LAYOUT_REGELN
    check("%s P2 Spule am Buck" % tag, hof_abstand(P["U90"], P["L90"]) <= R["P2"]["max_mm"])
    check("%s P2 Freilauf am Buck" % tag, hof_abstand(P["U90"], P["D93"]) <= R["P2"]["max_mm"])
    check("%s P2 Eingangskeramik am Buck" % tag,
          hof_abstand(P["U90"], P["C91"]) <= R["P2"]["max_mm"])
    check("%s P1 Boot-C am Buck" % tag, hof_abstand(P["U90"], P["C93"]) <= R["P1"]["max_mm"])
    for n in range(1, k + 1):
        q, j, rg, d = P["Q%d" % n], P["J%d" % (4 + n)], P["RG%d" % n], P["D%d" % n]
        check("%s P3 Q%d an seiner Klemme" % (tag, n),
              hof_abstand(q, j) <= R["P3"]["max_mm"], hof_abstand(q, j))
        check("%s P4 RG%d am Gate" % (tag, n),
              hof_abstand(q, rg) <= R["P4"]["max_mm"], hof_abstand(q, rg))
        check("%s Freilauf D%d am FET" % (tag, n), hof_abstand(q, d) <= 6.0)
        check("%s Q%d Beine nach oben (rot 270)" % (tag, n), q.rot == 270)

    # Slot-Matrix
    for n in range(1, k + 1):
        for bank in S.BAENKE:
            ref = S.MATRIX_REF(n, bank)
            check("%s Matrix %s platziert" % (tag, ref), ref in P)
            check("%s Matrix %s ist 0603" % (tag, ref),
                  b.FOOTPRINTS.get(ref) == S.MATRIX_FOOTPRINT)
    check("%s keine Matrix-Plaetze fuer fehlende Signale" % tag,
          not any(r.startswith("J") and r[1] in "ABCD" and int(r[2:]) > k for r in P))
    check("%s BANK = Vorgabe" % tag, b.BANK == S.BANK_VORGABE["Dimmer"])
    check("%s Naehvias vorhanden" % tag, len(b.STITCH_VIAS) >= 8, len(b.STITCH_VIAS))
    check("%s Rule Area Antenne beide Lagen" % tag,
          any(set(l) == {"F.Cu", "B.Cu"} and z == S.ANTENNE_FREI
              for _n, l, z, _v in b.RULE_AREAS))

# --- Rot-Nachweise ---------------------------------------------------------
b = _B(spec_dimmer_basis.beschreibung(4))
P = dict(b.PLACEMENT)
P["J5"] = Platz("J5", P["J5"].x, P["J5"].y - 3.0, P["J5"].w, P["J5"].h, 0, True)
check("Rot-Nachweis: Klemme 3 mm von der Kante weg ist nicht kantenbuendig",
      abs(P["J5"].y + P["J5"].h - S.BOARD_H) > 1e-6)
P["C94"] = Platz("C94", 48.0, 13.0, 9.4, 7.1)
check("Rot-Nachweis: Elko in der Antennenzone wird erkannt",
      schneidet(P["C94"], S.ANTENNE_FREI))
P2 = dict(b.PLACEMENT)
P2["Q1"] = Platz("Q1", P2["Q1"].x + 10.0, P2["Q1"].y, P2["Q1"].w, P2["Q1"].h, 270)
check("Rot-Nachweis: verschobener FET ueberlappt",
      any("Ueberlappung" in x for x in geometry.check_all(P2, b)))

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Dimmer-Platzierung 1/3/4: alle Pruefungen bestanden")

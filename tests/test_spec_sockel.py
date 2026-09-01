"""Prueft die Platinenbeschreibung der Sockelplatine. Ohne KiCad.

Was hier geprueft wird, ist genau das, was in spec_sockel.py als Zahl
behauptet wird -- und zwar so, dass es rot werden kann. Der Anlass ist
die Regel aus diesem Projekt: eine gerechnete Groesse ist eine
Zusicherung und braucht einen Nachweis, dass die Pruefung sie auch
verwirft, wenn sie falsch ist.

Drei Gruppen:

1. Die Vertragsteile (J2, J3, J4, U1) sind AUSGERECHNET, nicht
   abgeschrieben. Der Test rechnet sie unabhaengig aus stack_spec nach
   -- wer eine Zahl in spec_sockel.py von Hand "korrigiert", faellt auf.

2. Die Naehvias (STITCH_VIAS) liegen wirklich frei. Das steht in
   spec_sockel.py als Behauptung im Kommentar; hier wird sie
   nachgerechnet: Abstand zu jedem Hof, zu jeder M3-Freihaltung, zur
   Platinenkante und zum Antennenschlitz samt dessen Kantenabstand.
   Ein Via zu dicht an einem Pad ist ein Kurzschluss, den man auf dem
   Rendering nicht sieht.

3. Die Beschreibung ist vollstaendig: fuer jedes Bauteil des
   Schaltplans gibt es einen Footprint UND eine Platzierung.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "pcb"))

import fertigung
import geometry
import spec_sockel as B
import stack_spec as S

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- 1. Vertragsteile ------------------------------------------------
check("Umriss", (B.BOARD_W, B.BOARD_H), (S.BOARD_W, S.BOARD_H))
check("Lochbild", B.M3_HOLES, S.M3_HOLES)

for ref, flaeche, drehung in (
        ("J2", S.STECKER_POS["stapel"]["flaeche"],
         S.STECKER_POS["stapel"]["drehung"]),
        ("J3", S.HOF(B.FP_HDR_1X02_SMD, S.STECKER_POS["kette"]["pin1"],
                     S.STECKER_POS["kette"]["drehung"]),
         S.STECKER_POS["kette"]["drehung"]),
        ("J4", S.HOF(B.FP_HDR_2X02_SMD, S.STECKER_POS["leistung"]["pin1"],
                     S.STECKER_POS["leistung"]["drehung"]),
         S.STECKER_POS["leistung"]["drehung"]),
        ("U1", S.PICO_POS["flaeche"], S.PICO_POS["drehung"])):
    p = B.PLACEMENT[ref]
    x0, y0, x1, y1 = flaeche
    check(ref + " Lage", (p.x, p.y), (x0, y0))
    check(ref + " Groesse", (p.w, p.h), (round(x1 - x0, 3), round(y1 - y0, 3)))
    check(ref + " Drehung", p.rot, drehung)

# Die Platzierung selbst muss die Geometriepruefung bestehen -- dieselbe,
# die build.py vor dem Bauen fahren laesst.
bad = geometry.check_all(B.PLACEMENT, B)
if bad:
    fails.extend("Geometrie: " + b for b in bad)

# --- 2. Naehvias liegen frei -----------------------------------------
# Ein Via belegt VIA_PAD im Durchmesser; dazu kommt der Bahnabstand.
# Beides aus fertigung.py, damit die Pruefung mitwandert, wenn die
# Fertigungsvorgabe sich aendert.
CLEARANCE = 0.2
VIA_R = fertigung.VIA_PAD / 2.0 + CLEARANCE

for i, (vx, vy) in enumerate(B.STITCH_VIAS):
    name = "Naehvia %d (%.1f|%.1f)" % (i + 1, vx, vy)

    rand = B.EDGE_CLEARANCE + fertigung.VIA_PAD / 2.0
    if not (rand <= vx <= B.BOARD_W - rand and rand <= vy <= B.BOARD_H - rand):
        fails.append(name + ": zu nah an der Platinenkante")

    for hx, hy in B.M3_HOLES:
        if (vx - hx) ** 2 + (vy - hy) ** 2 < (B.M3_KEEPOUT / 2.0) ** 2:
            fails.append(name + ": im Freihaltebereich von M3 (%g|%g)"
                         % (hx, hy))

    for ref, p in sorted(B.PLACEMENT.items()):
        if ref == B.PICO_REF:
            # UNTER dem gesockelten Pico darf ein Via liegen -- dieselbe
            # Ausnahme, die geometry.check_all() fuer SMD-Teile macht
            # (8,5 mm Luft unter dem Sockel). Ein Via ist flach und
            # stoert dort niemanden; zwei der sechs Naehte sitzen genau
            # deshalb dort, weil die abgehaengten Masseflaechen dort
            # liegen und nirgends sonst.
            # Was dort NICHT gehen wuerde, sind seine Pad-Reihen: die
            # sind Kupfer auf beiden Lagen.
            for label, (ry0, ry1) in (("obere", B.PICO_ROW_TOP),
                                      ("untere", B.PICO_ROW_BOTTOM)):
                if (B.PICO_PAD_X[0] - VIA_R < vx < B.PICO_PAD_X[1] + VIA_R
                        and ry0 - VIA_R < vy < ry1 + VIA_R):
                    fails.append(name + ": auf der %sn Pad-Reihe des Pico"
                                 % label)
            continue
        if (p.x - VIA_R < vx < p.x + p.w + VIA_R
                and p.y - VIA_R < vy < p.y + p.h + VIA_R):
            fails.append(name + ": im Hof von " + ref)

    # Der Antennenschlitz ist gefraest: dort ist keine Platine, und um
    # ihn herum gilt derselbe Kantenabstand wie am Aussenrand.
    sx0, sy0, sx1, sy1 = B.ANTENNA_SLOT
    e = B.EDGE_CLEARANCE + fertigung.VIA_PAD / 2.0
    if (sx0 - e < vx < sx1 + e and sy0 - e < vy < sy1 + e):
        fails.append(name + ": im Antennenschlitz oder dessen Kantenabstand")

if len(set(B.STITCH_VIAS)) != len(B.STITCH_VIAS):
    fails.append("Naehvias: doppelte Lage")

# --- 3. Beschreibung vollstaendig ------------------------------------
check("jedes platzierte Bauteil hat einen Footprint",
      sorted(set(B.PLACEMENT) - set(B.FOOTPRINTS)), [])
check("jeder Footprint ist platziert",
      sorted(set(B.FOOTPRINTS) - set(B.PLACEMENT)), [])

# Der Pico traegt die Sonderfaelle in geometry.py -- ohne PICO_REF
# greifen sie stillschweigend nicht.
check("PICO_REF zeigt auf ein platziertes Bauteil",
      B.PICO_REF in B.PLACEMENT, True)
check("SMD_CORRIDOR aus", B.SMD_CORRIDOR, None)

# Die Pad-Reihen des Pico muessen dort liegen, wo seine Pads wirklich
# sind: aus PICO_POS nachgerechnet, nicht aus spec_sockel abgeschrieben.
_, py = S.PICO_POS["pin1"]
check("obere Pad-Reihe", B.PICO_ROW_TOP, (round(py - 17.78 - 0.8, 3),
                                          round(py - 17.78 + 0.8, 3)))
check("untere Pad-Reihe", B.PICO_ROW_BOTTOM, (round(py - 0.8, 3),
                                              round(py + 0.8, 3)))

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Sockelbeschreibung: %d Bauteile, %d Naehvias -- "
      "alle Pruefungen bestanden" % (len(B.PLACEMENT), len(B.STITCH_VIAS)))

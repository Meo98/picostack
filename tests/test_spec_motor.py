"""Prueft die Platinenbeschreibung des Motormoduls. Ohne KiCad.

Spiegel von tests/test_spec_sockel.py, mit den Sonderfaellen dieser
Platine:

1. Die Vertragsteile (J100..J104) sind AUSGERECHNET, nicht
   abgeschrieben -- das Modul traegt von Ketten- und Leistungsstecker
   beide Haelften, die Stifthaelften gespiegelt unten.

2. Die RASTER-Naehte muessen frei liegen (wie beim Sockel). Die
   STITCH_EXTRA-Punkte dagegen sitzen ABSICHTLICH in Hoefen (unter
   Bauteilbaeuchen, um die Gussfragmente zu vernaehen) -- fuer sie
   gelten schwaechere, aber rot-faehige Zusagen: im Brett, nicht im
   M3-Freihaltebereich, nicht in der Waermepfad-Regelflaeche, nicht
   doppelt, und NICHT im Kupfer der eigenen Vorverdrahtung. Die
   letzte Pruefung hat ihren Rot-Nachweis in der Geschichte: der
   erste Suchlauf setzte (24,0|34,5) mit Beruehrung auf die
   /+24V-Bahn nach R17 -- Kurzschluss, von der DRC gefangen.

3. Die Vorverdrahtung haelt die 0/45/90-Zusage auch auf den
   literalen Zwischenpunkten (build.pre_tracks prueft zusaetzlich
   die aufgeloesten PAD-Endpunkte am gebauten Board).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "pcb"))

import fertigung
import geometry
import spec_motor as B
import stack_spec as S

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- 1. Vertragsteile ------------------------------------------------
check("Umriss", (B.BOARD_W, B.BOARD_H), (S.BOARD_W, S.BOARD_H))
check("Lochbild", B.M3_HOLES, S.M3_HOLES)
check("ist ein Modul", B.IST_MODUL, True)

for ref, fp in (("J101", B.FP_SKT_1X02), ("J102", B.FP_HDR_1X02)):
    flaeche = S.HOF(fp, S.STECKER_POS["kette"]["pin1"],
                    S.STECKER_POS["kette"]["drehung"])
    p = B.PLACEMENT[ref]
    check(ref + " Lage", (p.x, p.y), (flaeche[0], flaeche[1]))
    check(ref + " Drehung", p.rot, S.STECKER_POS["kette"]["drehung"])
for ref, fp in (("J103", B.FP_SKT_2X02), ("J104", B.FP_HDR_2X02)):
    flaeche = S.HOF(fp, S.STECKER_POS["leistung"]["pin1"],
                    S.STECKER_POS["leistung"]["drehung"])
    p = B.PLACEMENT[ref]
    check(ref + " Lage", (p.x, p.y), (flaeche[0], flaeche[1]))
    check(ref + " Drehung", p.rot, S.STECKER_POS["leistung"]["drehung"])

fx0, fy0, fx1, fy1 = S.STECKER_POS["stapel"]["flaeche"]
p = B.PLACEMENT["J100"]
check("J100 Lage", (p.x, p.y), (fx0, fy0))
check("J100 Groesse", (p.w, p.h), (round(fx1 - fx0, 3), round(fy1 - fy0, 3)))
check("J100 Drehung", p.rot, S.STECKER_POS["stapel"]["drehung"])

# Die Stifthaelften treiben nach unten ins naechste Modul; alles
# andere sitzt oben.
check("J102/J104 sitzen unten",
      sorted(r for r in ("J102", "J104") if not B.PLACEMENT[r].unten), [])
check("kein anderes Bauteil sitzt unten",
      sorted(r for r, pl in B.PLACEMENT.items()
             if pl.unten and r not in ("J102", "J104")), [])

bad = geometry.check_all(B.PLACEMENT, B)
if bad:
    fails.extend("Geometrie: " + b for b in bad)

# --- 2a. Raster-Naehte liegen frei (wie beim Sockel) -----------------
CLEARANCE = 0.2
VIA_R = fertigung.VIA_PAD / 2.0 + CLEARANCE
raster = [v for v in B.STITCH_VIAS if v not in set(B.STITCH_EXTRA)]

for i, (vx, vy) in enumerate(raster):
    name = "Naehvia %d (%.2f|%.2f)" % (i + 1, vx, vy)
    rand = B.EDGE_CLEARANCE + fertigung.VIA_PAD / 2.0
    if not (rand <= vx <= B.BOARD_W - rand and rand <= vy <= B.BOARD_H - rand):
        fails.append(name + ": zu nah an der Platinenkante")
    for hx, hy in B.M3_HOLES:
        if (vx - hx) ** 2 + (vy - hy) ** 2 < (B.M3_KEEPOUT / 2.0) ** 2:
            fails.append(name + ": im Freihaltebereich von M3 (%g|%g)"
                         % (hx, hy))
    for ref, pl in sorted(B.PLACEMENT.items()):
        if (pl.x - VIA_R < vx < pl.x + pl.w + VIA_R
                and pl.y - VIA_R < vy < pl.y + pl.h + VIA_R):
            fails.append(name + ": im Hof von " + ref)
    for _n, _l, (x0, y0, x1, y1), verbote in B.RULE_AREAS:
        if "vias" in verbote and (x0 - VIA_R < vx < x1 + VIA_R
                                  and y0 - VIA_R < vy < y1 + VIA_R):
            fails.append(name + ": in der Regelflaeche " + _n)

# --- 2b. Extra-Naehte und Vorverdrahtungs-Vias -----------------------
def _seg_abstand(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _literal_segmente():
    for eintrag in B.PRE_TRACKS:
        netz, _lage, pts = eintrag[:3]
        breite = eintrag[3] if len(eintrag) > 3 else fertigung.TRACK_SIGNAL
        lit = [q for q in pts if not (isinstance(q, tuple) and len(q) == 3)]
        for a, b in zip(lit, lit[1:]):
            yield netz, breite, a, b


alle_vias = list(B.STITCH_EXTRA) + [(x, y) for _n, x, y in B.PRE_VIAS]
for vx, vy in alle_vias:
    name = "Zusatzvia (%.2f|%.2f)" % (vx, vy)
    rand = B.EDGE_CLEARANCE + fertigung.VIA_PAD / 2.0
    if not (rand <= vx <= B.BOARD_W - rand and rand <= vy <= B.BOARD_H - rand):
        fails.append(name + ": zu nah an der Platinenkante")
    for hx, hy in B.M3_HOLES:
        if (vx - hx) ** 2 + (vy - hy) ** 2 < (B.M3_KEEPOUT / 2.0) ** 2:
            fails.append(name + ": im Freihaltebereich von M3")
    for _n, _l, (x0, y0, x1, y1), verbote in B.RULE_AREAS:
        if "vias" in verbote and (x0 - VIA_R < vx < x1 + VIA_R
                                  and y0 - VIA_R < vy < y1 + VIA_R):
            fails.append(name + ": in der Regelflaeche " + _n)
    for netz, breite, a, b in _literal_segmente():
        noetig = fertigung.VIA_PAD / 2.0 + breite / 2.0 + CLEARANCE
        d = _seg_abstand(vx, vy, a, b)
        # Ein Via DARF im Kupfer der eigenen Vorverdrahtung sitzen,
        # wenn es dasselbe Netz traegt -- das /+24V-Via (46,5|25,4)
        # sitzt absichtlich mitten auf der Fettbahn.
        eigenes = any(n == netz and abs(vx - x) < 1e-6 and abs(vy - y) < 1e-6
                      for n, x, y in B.PRE_VIAS)
        if d < noetig - 1e-9 and not eigenes:
            fails.append("%s: %.3f mm an der %s-Bahn %s->%s (noetig %.2f)"
                         % (name, d, netz, a, b, noetig))

if len(set(B.STITCH_VIAS)) != len(B.STITCH_VIAS):
    fails.append("Naehvias: doppelte Lage")

# --- 3. Vorverdrahtung: 0/45/90 auf den Literalen --------------------
for netz, breite, a, b in _literal_segmente():
    dx = round((b[0] - a[0]) * 1000)
    dy = round((b[1] - a[1]) * 1000)
    if dx and dy and abs(dx) != abs(dy):
        fails.append("PRE_TRACKS %s: %s->%s ist weder 0/90 noch 45 Grad"
                     % (netz, a, b))

# --- 4. Beschreibung vollstaendig ------------------------------------
check("jedes platzierte Bauteil hat einen Footprint",
      sorted(set(B.PLACEMENT) - set(B.FOOTPRINTS)), [])
check("jeder Footprint ist platziert",
      sorted(set(B.FOOTPRINTS) - set(B.PLACEMENT)), [])
check("Leistungsnetze benannt",
      sorted(B.POWER_NETS),
      sorted(("/PWR24V", "/+24V", "/Out1", "/Out2")))

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Motorbeschreibung: %d Bauteile, %d Naehte (davon %d gezielt), "
      "%d Vorverdrahtungs-Vias -- alle Pruefungen bestanden"
      % (len(B.PLACEMENT), len(B.STITCH_VIAS), len(B.STITCH_EXTRA),
         len(B.PRE_VIAS)))

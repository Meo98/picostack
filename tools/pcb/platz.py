"""Gemeinsame Bausteine aller Platinenbeschreibungen (spec_*.py).

Bis v2.1 lebte das in spec_motor.py und wurde von spec_dimmer_basis.py
quer importiert; v3 zieht es hierher, damit kein Modul ein anderes
Modul importieren muss, nur um an die Platz-Klasse zu kommen.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import stack_spec as S  # noqa: E402

COURTYARD_GAP = 0.6      # mm Luft zwischen zwei Hoefen
EDGE_CLEARANCE = 0.5     # mm Hof zur Platinenkante (R5)
STITCH_RASTER = 7.5      # mm Raster der GND-Naehvias


class Platz:
    """Ein platziertes Bauteil: Hof-Ecke (x, y) links oben, Hofmasse w x h,
    Drehung in Grad (KiCad, gegen den Uhrzeigersinn), tht = bedrahtet,
    unten = auf der Rueckseite."""

    def __init__(self, ref, x, y, w, h, rot=0, tht=False, unten=False):
        self.ref, self.rot, self.tht, self.unten = ref, rot, tht, unten
        self.x, self.y, self.w, self.h = x, y, w, h

    def mitte(self):
        return (self.x + self.w / 2.0, self.y + self.h / 2.0)

    def rechteck(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def __repr__(self):
        return "Platz(%s, %.2f, %.2f, %.2fx%.2f, %d%s)" % (
            self.ref, self.x, self.y, self.w, self.h, self.rot,
            ", unten" if self.unten else "")


def aus_vertrag(ref, flaeche, rot, tht=True):
    """Ein Bauteil, dessen Lage der Vertrag festlegt (S.STECKER_POS)."""
    x0, y0, x1, y1 = flaeche
    return Platz(ref, x0, y0, round(x1 - x0, 3), round(y1 - y0, 3), rot, tht)


def hof_abstand(a, b):
    """Kleinster Abstand zweier Hoefe (0, wenn sie sich beruehren)."""
    ax0, ay0, ax1, ay1 = a.rechteck()
    bx0, by0, bx1, by1 = b.rechteck()
    dx = max(bx0 - ax1, ax0 - bx1, 0.0)
    dy = max(by0 - ay1, ay0 - by1, 0.0)
    return (dx * dx + dy * dy) ** 0.5


def naehte(platzierung, rule_areas, m3_holes=None):
    """GND-Naehvias im STITCH_RASTER, ausserhalb aller Hoefe, Loecher
    und Regelflaechen mit Via-Verbot."""
    m3_holes = S.M3_HOLES if m3_holes is None else m3_holes
    rand = EDGE_CLEARANCE + 0.5

    def erlaubt(vx, vy):
        if not (rand <= vx <= S.BOARD_W - rand and rand <= vy <= S.BOARD_H - rand):
            return False
        for hx, hy in m3_holes:
            if abs(vx - hx) < S.M3_KEEPOUT / 2.0 and abs(vy - hy) < S.M3_KEEPOUT / 2.0:
                return False
        for p in platzierung.values():
            if p.x - 0.5 < vx < p.x + p.w + 0.5 and p.y - 0.5 < vy < p.y + p.h + 0.5:
                return False
        for _n, _l, (x0, y0, x1, y1), verbote in rule_areas:
            if "vias" in verbote and x0 - 0.5 < vx < x1 + 0.5 and y0 - 0.5 < vy < y1 + 0.5:
                return False
        return True

    aus = []
    n_x = int((S.BOARD_W - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    n_y = int((S.BOARD_H - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    ox = (S.BOARD_W - (n_x - 1) * STITCH_RASTER) / 2.0
    oy = (S.BOARD_H - (n_y - 1) * STITCH_RASTER) / 2.0
    for iy in range(n_y):
        for ix in range(n_x):
            vx = round(ox + ix * STITCH_RASTER, 3)
            vy = round(oy + iy * STITCH_RASTER, 3)
            if erlaubt(vx, vy):
                aus.append((vx, vy))
    return tuple(aus)

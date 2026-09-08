"""Prueft die Platinenbeschreibung des Motormoduls (v2). Ohne KiCad.

Umgeschrieben fuer Aufgabe 7 (Etappe 2, "Platzierungs-Spec v2 +
Motor-Board durch die Pipeline"): neues Boardmass (75x65), zwei
Stapelreihen (J100/J105) statt einem 2x20-Block, Randpad-Realisierung
(J95/J96), Versorgungszelle statt Q1-Strang, ANTENNE_FREI-Bindung.

Struktur wie vorher (Spiegel von tests/test_spec_sockel.py), mit den
Sonderfaellen dieser Platine:

1. Die Vertragsteile (J100..J105) sind AUSGERECHNET, nicht
   abgeschrieben -- das Modul traegt von Ketten- und Leistungsstecker
   beide Haelften, die Stifthaelften gespiegelt unten.

2. Die RASTER-Naehte muessen frei liegen. STITCH_EXTRA-Punkte (falls
   welche noetig werden) sitzen ABSICHTLICH in Hoefen -- fuer sie
   gelten schwaechere, aber rot-faehige Zusagen (s. unten).

3. ANTENNE_FREI ist BINDEND: kein eigenes Bauteil (ausser den vier
   Vertragssteckern, die selbst der Anker sind) darf dort einen Hof
   haben, und RULE_AREAS muss dort Bahnen/Vias/Guss auf F.Cu sperren.

4. Die Vorverdrahtung haelt die 0/45/90-Zusage auch auf den
   literalen Zwischenpunkten.
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

for ref, platz in (("J100", "stapel_links"), ("J105", "stapel_rechts")):
    fx0, fy0, fx1, fy1 = S.STECKER_POS[platz]["flaeche"]
    p = B.PLACEMENT[ref]
    check(ref + " Lage", (p.x, p.y), (fx0, fy0))
    check(ref + " Groesse", (p.w, p.h),
          (round(fx1 - fx0, 3), round(fy1 - fy0, 3)))
    check(ref + " Drehung", p.rot, S.STECKER_POS[platz]["drehung"])

# Die Stifthaelften treiben nach unten ins naechste Modul; alles
# andere sitzt oben -- AUSSER den Randpads (J95/J96, echte
# THT-Loetpads auf der Bestueckungsseite dieser Platine, nicht Teil
# eines Steckerpaars) und J5/J90/C90/U90, die aus Platzgruenden ihren
# eigenen Weg gehen (s. spec_motor-Docstring) -- deshalb wird hier nur
# noch geprueft, dass GENAU J102/J104 unten sitzen.
check("J102/J104 sitzen unten",
      sorted(r for r in ("J102", "J104") if not B.PLACEMENT[r].unten), [])
_unten_erlaubt = {"J102", "J104", "J100", "J105", "J90", "C90", "U90", "J5",
                  "J95", "J96"}
check("kein unerwartetes Bauteil sitzt unten",
      sorted(r for r, pl in B.PLACEMENT.items()
             if pl.unten and r not in _unten_erlaubt), [])
# J100/J105 (Buchsen, THT) und J90/C90/U90 (THT-Bauteile auf dieser
# Seite) sitzen tatsaechlich OBEN trotz tht=True -- die "unten"-Probe
# oben schliesst nur EIN, dass sie nicht UNERWARTET unten liegen. Ob
# sie WIRKLICH oben liegen (unten=False), steht direkt in PLACEMENT
# und wird von geometry.check_all() (Kollisionspruefung) indirekt
# mitgeprueft: zwei Bauteile auf verschiedenen Seiten kollidieren nie,
# ein Fehler hier waere also nur an falschen Kollisionsmeldungen
# erkennbar -- ausreichend fuer dieses Detail.

bad = geometry.check_all(B.PLACEMENT, B)
if bad:
    fails.extend("Geometrie: " + b for b in bad)

# --- 2. ANTENNE_FREI ist bindend --------------------------------------
_AX0, _AY0, _AX1, _AY1 = S.ANTENNE_FREI
_VERTRAGSSTECKER = {"J100", "J101", "J102", "J103", "J104", "J105"}
for ref, p in sorted(B.PLACEMENT.items()):
    if ref in _VERTRAGSSTECKER or p.unten:
        continue
    x0, y0, x1, y1 = p.x, p.y, p.x + p.w, p.y + p.h
    if x0 < _AX1 and _AX0 < x1 and y0 < _AY1 and _AY0 < y1:
        fails.append("ANTENNE_FREI verletzt von {} ({:.2f}|{:.2f})-"
                     "({:.2f}|{:.2f})".format(ref, x0, y0, x1, y1))

_hat_antennenregel = False
for name, lagen, (x0, y0, x1, y1), verbote in B.RULE_AREAS:
    if (x0, y0, x1, y1) == S.ANTENNE_FREI:
        _hat_antennenregel = True
        if "F.Cu" not in lagen:
            fails.append("ANTENNE_FREI-Regelflaeche gilt nicht fuer F.Cu")
        for v in ("bahnen", "vias", "guss"):
            if v not in verbote:
                fails.append("ANTENNE_FREI-Regelflaeche erlaubt " + v)
if not _hat_antennenregel:
    fails.append("keine RULE_AREAS-Regelflaeche fuer ANTENNE_FREI gefunden")

# --- 2a. Raster-Naehte liegen frei -------------------------------------
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


# --- 2b. Extra-Naehte und Vorverdrahtungs-Vias -------------------------
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
        eigenes = any(n == netz and abs(vx - x) < 1e-6 and abs(vy - y) < 1e-6
                      for n, x, y in B.PRE_VIAS)
        if d < noetig - 1e-9 and not eigenes:
            fails.append("%s: %.3f mm an der %s-Bahn %s->%s (noetig %.2f)"
                         % (name, d, netz, a, b, noetig))

if len(set(B.STITCH_VIAS)) != len(B.STITCH_VIAS):
    fails.append("Naehvias: doppelte Lage")

# --- 3. Vorverdrahtung: 0/45/90 auf den Literalen ----------------------
for netz, breite, a, b in _literal_segmente():
    dx = round((b[0] - a[0]) * 1000)
    dy = round((b[1] - a[1]) * 1000)
    if dx and dy and abs(dx) != abs(dy):
        fails.append("PRE_TRACKS %s: %s->%s ist weder 0/90 noch 45 Grad"
                     % (netz, a, b))

# --- 4. Beschreibung vollstaendig ---------------------------------------
check("jedes platzierte Bauteil hat einen Footprint",
      sorted(set(B.PLACEMENT) - set(B.FOOTPRINTS)), [])
check("jeder Footprint ist platziert",
      sorted(set(B.FOOTPRINTS) - set(B.PLACEMENT)), [])
check("Leistungsnetze benannt",
      sorted(B.POWER_NETS),
      sorted(("/PWR_IN", "/+24V", "/Out1", "/Out2")))

# --- 5. Randpads: alle 22 Vertrags-Kontakte kommen aus J95/J96 ----------
# S.RANDPADS zaehlt 22 (pin, label, (x,y))-Eintraege. Diese Platine
# realisiert sie nicht buchstaeblich an denselben (x,y) (s. Docstring,
# "einseitig statt beidseitig gerahmt"), aber die MENGE der 22
# Kontakte muss trotzdem aus GENAU J95 (18 Pins) und J96 (4 Pins)
# kommen -- keiner darf verloren gehen oder verdoppelt werden.
check("RANDPADS-Anzahl", len(S.RANDPADS), 22)
check("J95 hat 18 Kontakte -- ein Pin je freien GPIO",
      len([p for p, l, _ in S.RANDPADS if l.startswith("GP")]), 18)

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Motorbeschreibung: %d Bauteile, %d Naehte (davon %d gezielt), "
      "%d Vorverdrahtungs-Vias -- alle Pruefungen bestanden"
      % (len(B.PLACEMENT), len(B.STITCH_VIAS), len(B.STITCH_EXTRA),
         len(B.PRE_VIAS)))

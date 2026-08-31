"""Geometriepruefungen fuer die Platzierung. Kennt kein KiCad.

Herkunft: PecheAuxCanards/tools/pcb/geometry.py (Etappe 1b, Aufgabe 1).
Dort importierte die Datei ein einziges globales Modul "spec", weil
jenes Projekt genau eine Platine hatte. PicoStack baut in einem Lauf
zwei verschiedene Platinen (Sockel und Motormodul, spaeter weitere) --
ein globaler Import haette bedeutet, das Werkzeug entweder zu kopieren
(zwei Kopien laufen zwangslaeufig auseinander) oder die zweite Platine
mit den Massen der ersten zu pruefen. check_all() nimmt die
Platinenbeschreibung deshalb jetzt als Parameter entgegen, statt sie zu
importieren -- pro Lauf kann so jede Platine ihre eigene bekommen.

check_all gibt Klartext-Befunde zurueck; eine leere Liste heisst
bestanden. Die Pruefungen sind bewusst so geschrieben, dass sie auch
anschlagen, wenn jemand die Beschreibung veraendert -- sie sind die
Bremse gegen ein Layout, das nur auf dem Papier aufgeht.

`beschreibung` ist ein Modul oder Objekt (z.B. tools/pcb/spec_sockel.py
oder tools/pcb/spec_motor.py, nach dem Muster von tools/stack_spec.py)
mit mindestens:
    BOARD_W, BOARD_H, M3_HOLES

Optional, mit denselben Vorgaben wie im Vorlaeuferprojekt, falls nicht
gesetzt:
    COURTYARD_GAP (0.6), M3_KEEPOUT (7.0), EDGE_CLEARANCE (0.5)

Nur noetig, wenn die Platine selbst einen gesockelten Pico traegt (in
PicoStack bisher nur der Sockel, das Motormodul hat stattdessen einen
Modul-MCU ohne diese Bauform-Eigenheiten):
    PICO_PAD_X, PICO_ROW_TOP, PICO_ROW_BOTTOM, SMD_CORRIDOR, ANTENNA_SLOT

Fehlen diese fuenf (oder auch nur ANTENNA_SLOT / SMD_CORRIDOR einzeln),
werden die zugehoerigen Pruefungen einfach uebersprungen, statt mit
AttributeError abzubrechen.
"""
import os
import sys


def _rect(p):
    return (p.x, p.y, p.x + p.w, p.y + p.h)


# Teile, die genau den geforderten Abstand einhalten, sollen bestehen.
# Ohne Toleranz meldet 10.80 + 0.6 > 11.40 einen Ueberlapp, den es
# nicht gibt -- reiner Gleitkomma-Rest.
EPS = 1e-6


def _overlap(a, b, gap):
    ax0, ay0, ax1, ay1 = _rect(a)
    bx0, by0, bx1, by1 = _rect(b)
    g = gap - EPS
    return (ax0 < bx1 + g and bx0 < ax1 + g and
            ay0 < by1 + g and by0 < ay1 + g)


def check_all(placement, beschreibung):
    b = beschreibung
    courtyard_gap = getattr(b, "COURTYARD_GAP", 0.6)
    m3_keepout = getattr(b, "M3_KEEPOUT", 7.0)
    edge_clearance = getattr(b, "EDGE_CLEARANCE", 0.5)
    pico_pad_x = getattr(b, "PICO_PAD_X", None)
    pico_row_top = getattr(b, "PICO_ROW_TOP", None)
    pico_row_bottom = getattr(b, "PICO_ROW_BOTTOM", None)
    smd_corridor = getattr(b, "SMD_CORRIDOR", None)
    antenna_slot = getattr(b, "ANTENNA_SLOT", None)
    pico_pads_bekannt = (pico_pad_x is not None and pico_row_top is not None
                         and pico_row_bottom is not None)

    bad = []
    # "U3" ist die Referenz des gesockelten Pico im Vorlaeuferprojekt.
    # Traegt eine Platine keinen (z.B. das Motormodul), ist pico einfach
    # None und alle Sonderfaelle dafuer bleiben aus.
    pico = placement.get("U3")
    refs = sorted(placement)

    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            a, c = placement[refs[i]], placement[refs[j]]
            # SMD darf unter dem gesockelten Pico liegen (8,5 mm Luft)
            if pico is not None and (a is pico or c is pico):
                other = c if a is pico else a
                if not other.tht:
                    continue
            if _overlap(a, c, courtyard_gap):
                bad.append("Ueberlappung {} / {}".format(a.ref, c.ref))

    r = m3_keepout / 2.0
    for ref in refs:
        p = placement[ref]
        x0, y0, x1, y1 = _rect(p)
        # Kein Teil ragt hinaus -- auch der Pico nicht. Sein Ueberhang
        # haette auf dem Vorlaeuferprojekt Pins gekostet; die Antenne
        # bekommt ihre freie Luft stattdessen durch den Schlitz.
        if x0 < edge_clearance:
            bad.append("{} ragt links hinaus".format(p.ref))
        if y0 < edge_clearance:
            bad.append("{} ragt oben hinaus".format(p.ref))
        if x1 > b.BOARD_W - edge_clearance:
            bad.append("{} ragt rechts hinaus".format(p.ref))
        if y1 > b.BOARD_H - edge_clearance:
            bad.append("{} ragt unten hinaus".format(p.ref))

        for hx, hy in b.M3_HOLES:
            if x0 - r < hx < x1 + r and y0 - r < hy < y1 + r:
                bad.append("{} im Freihaltebereich von M3 ({}|{})".format(
                    p.ref, hx, hy))

    if pico_pads_bekannt:
        # Die Pad-Reihen des Pico sind Kupfer auf beiden Lagen. Ein
        # SMD-Teil darunter ist nicht bloss zu dicht, sondern
        # kurzgeschlossen -- so entstanden im Vorlaeuferprojekt sieben
        # echte Kurzschluesse, die die reine Ueberlappungspruefung nicht
        # sehen konnte, weil sie den Pico als Ganzes fuer SMD freigibt.
        px0, px1 = pico_pad_x
        for ref in refs:
            p = placement[ref]
            if p.tht or p is pico:
                continue
            x0, y0, x1, y1 = _rect(p)
            if x1 < px0 or x0 > px1:
                continue
            for name, (ry0, ry1) in (("obere", pico_row_top),
                                     ("untere", pico_row_bottom)):
                if y0 < ry1 and ry0 < y1:
                    bad.append("{} liegt auf der {}n Pad-Reihe des Pico"
                               .format(p.ref, name))
            if smd_corridor is not None:
                cx0, cy0, cx1, cy1 = smd_corridor
                if (x0 < cx0 - EPS or y0 < cy0 - EPS or
                        x1 > cx1 + EPS or y1 > cy1 + EPS):
                    bad.append("{} liegt ausserhalb des SMD-Korridors"
                               .format(p.ref))

        if antenna_slot is not None:
            # Der Schlitz muss die Antenne wirklich freistellen und
            # dabei zwischen den Pad-Reihen bleiben -- schneidet er in
            # eine Reihe, faellt genau der Pin weg, den der Schlitz
            # retten sollte.
            sx0, sy0, sx1, sy1 = antenna_slot
            if sy0 < pico_row_top[1]:
                bad.append("Schlitz schneidet in die obere Pad-Reihe")
            if sy1 > pico_row_bottom[0]:
                bad.append("Schlitz schneidet in die untere Pad-Reihe")
            if sx0 < edge_clearance or sy0 < edge_clearance:
                bad.append("Schlitz liegt zu nah an der Platinenkante")
            if sx1 > b.BOARD_W - edge_clearance:
                bad.append("Schlitz laeuft rechts aus der Platine")

            # Kein Bauteil darf in den Schlitz ragen -- dort ist keine
            # Platine.
            for ref in refs:
                p = placement[ref]
                if p is pico:
                    continue
                x0, y0, x1, y1 = _rect(p)
                if x0 < sx1 and sx0 < x1 and y0 < sy1 and sy0 < y1:
                    bad.append("{} steht ueber dem Antennenschlitz"
                               .format(p.ref))
    return bad



def freie_flaeche(beschreibung, hindernisse, raster=0.1):
    """Wieviel Platz eine Platine noch hergibt, in mm2.

    Rueckgabe: (groesste zusammenhaengende freie Flaeche, groesstes
    freies achsparalleles Rechteck). Die erste Zahl sagt, wieviel
    ueberhaupt uebrig ist, die zweite, wieviel davon man am Stueck
    bebauen kann -- eine Flaeche, die nur ueber einen 1 mm breiten Hals
    zusammenhaengt, ist keine 2000 mm2 Bauflaeche.

    `hindernisse` sind Rechtecke (x0, y0, x1, y1) in
    Platinenkoordinaten -- typischerweise die Stecker aus
    stack_spec.STECKER_POS. Zusaetzlich gesperrt sind, ohne dass sie
    genannt werden muessen: der Randstreifen (EDGE_CLEARANCE), die
    Freihaltekreise der M3-Bohrungen (M3_KEEPOUT) und ein Ring von
    COURTYARD_GAP um jedes Hindernis -- dieselben drei Regeln, gegen
    die check_all() oben prueft.

    Gerastert statt analytisch: die M3-Freihaltung ist ein Kreis, und
    ein exakter Polygonschnitt waere fuer die Frage "passt ein Modul
    noch drauf" mehr Maschinerie als Nutzen. Bei raster=0,1 mm ist der
    Fehler kleiner als die Fertigungstoleranz der Platine.
    """
    import collections

    gap = getattr(beschreibung, "COURTYARD_GAP", 0.6)
    m3 = getattr(beschreibung, "M3_KEEPOUT", 7.0) / 2.0
    rand = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
    bw, bh = beschreibung.BOARD_W, beschreibung.BOARD_H
    nx, ny = int(bw / raster), int(bh / raster)

    frei = [[True] * nx for _ in range(ny)]
    for iy in range(ny):
        cy = (iy + 0.5) * raster
        for ix in range(nx):
            cx = (ix + 0.5) * raster
            if cx < rand or cy < rand or cx > bw - rand or cy > bh - rand:
                frei[iy][ix] = False
                continue
            for hx, hy in beschreibung.M3_HOLES:
                if (cx - hx) ** 2 + (cy - hy) ** 2 < m3 * m3:
                    frei[iy][ix] = False
                    break
            else:
                for x0, y0, x1, y1 in hindernisse:
                    if (x0 - gap < cx < x1 + gap and
                            y0 - gap < cy < y1 + gap):
                        frei[iy][ix] = False
                        break

    gesehen = [[False] * nx for _ in range(ny)]
    groesste = 0
    for iy in range(ny):
        for ix in range(nx):
            if not frei[iy][ix] or gesehen[iy][ix]:
                continue
            stapel = collections.deque([(iy, ix)])
            gesehen[iy][ix] = True
            n = 0
            while stapel:
                y, x = stapel.popleft()
                n += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if (0 <= yy < ny and 0 <= xx < nx and frei[yy][xx]
                            and not gesehen[yy][xx]):
                        gesehen[yy][xx] = True
                        stapel.append((yy, xx))
            groesste = max(groesste, n)

    # Groesstes Rechteck: Standard-Histogrammverfahren, Zeile fuer Zeile.
    hoehe = [0] * nx
    bestes = 0
    for iy in range(ny):
        for ix in range(nx):
            hoehe[ix] = hoehe[ix] + 1 if frei[iy][ix] else 0
        keller = []
        for ix in range(nx + 1):
            aktuell = hoehe[ix] if ix < nx else 0
            start = ix
            while keller and keller[-1][1] > aktuell:
                s, h = keller.pop()
                bestes = max(bestes, h * (ix - s))
                start = s
            keller.append((start, aktuell))

    q = raster * raster
    return (round(groesste * q, 1), round(bestes * q, 1))


if __name__ == "__main__":
    import importlib

    if len(sys.argv) != 2:
        raise SystemExit(
            "Aufruf: geometry.py <spec_modul, z.B. spec_sockel>")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    beschreibung = importlib.import_module(sys.argv[1])
    bad = check_all(beschreibung.PLACEMENT, beschreibung)
    if bad:
        print("Platzierung fehlerhaft:")
        for b in bad:
            print("  -", b)
        raise SystemExit(1)
    print("Platzierung in Ordnung.")

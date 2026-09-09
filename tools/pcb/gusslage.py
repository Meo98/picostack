"""Gemeinsame Werkzeuge: erreicht ein gefuellter Guss diese Stelle?

Herkunft: aus masseheiler.py herausgezogen (Aufgabe 7c). masseheiler.py
prueft NACH dem Verlegen, ob zwei Kupferstuecke zusammenhaengen, und
kennt darum laengst die richtige Antwort auf "liegt hier Kupfer eines
Netzes" -- ueber das gefuellte Zonenpolygon, nicht ueber eine Schaetzung
aus der Beschreibung. build.py brauchte genau dieselbe Frage VOR dem
Verlegen, fuer den Naehpunkt-Filter (s. build.stitching_vias): die alte
Fassung dort pruefte nur Abstand zu Bauteil-Hoefen, nie ob der Guss die
Stelle ueberhaupt FUELLT. Zwei Kopien derselben Polygon-Logik waeren
genau das Muster, vor dem fertigung.py in seinem eigenen Docstring warnt
(eine Bahnbreite an zwei Stellen lief im Muttern-Redesign auseinander) --
darum liegt die Logik jetzt hier, und beide Aufrufer importieren sie.
"""
import pcbnew

mm = lambda v: int(round(v * 1e6))

FREI = 0.2          # Abstand zu fremdem Kupfer (Netzklassen-Clearance)


def gnd_zonen(board, netcode):
    """{lage: gefuellte Polygone} fuer alle Guss-Zonen dieses Netzes."""
    zonen = {}
    for z in board.Zones():
        if z.GetNetCode() != netcode or z.GetIsRuleArea():
            continue
        for lage in (pcbnew.F_Cu, pcbnew.B_Cu):
            if z.IsOnLayer(lage):
                zonen[lage] = z.GetFilledPolysList(lage)
    return zonen


def stueck(zonen, lage, x, y):
    """Index des gefuellten Polygonstuecks unter (x,y) auf dieser Lage,
    oder None, wenn der Guss dort nicht hinreicht."""
    polys = zonen.get(lage)
    if polys is None:
        return None
    for i in range(polys.OutlineCount()):
        if polys.Contains(pcbnew.VECTOR2I(int(x), int(y)), i):
            return i
    return None


def erreicht(zonen, x, y, lagen=(pcbnew.F_Cu, pcbnew.B_Cu)):
    """Fuellt der Guss (x,y) auf JEDER angegebenen Lage?

    Fuer ein durchkontaktiertes Naehvia ist eine einseitige Anbindung
    nutzlos -- pcb_checks.freihaengende_vias() meldet ein Via schon als
    "freihaengend", wenn nur EINE Lage kein Kupfer traegt. Ein Via, das
    der Guss auf keiner Lage erreicht, ist noch schlimmer: es haengt
    isoliert in der Luft und heilt nichts (der Fund, der Aufgabe 7c
    ausgeloest hat -- s. dortiger Bericht).
    """
    return all(stueck(zonen, lage, x, y) is not None for lage in lagen)


def frei(board, x, y, radius, eigenes_netz, frei_mm=FREI, nur_lage=None):
    """Darf hier Kupfer von `eigenes_netz` mit diesem Radius hin?

    Am Board gemessen: Abstand zu fremden Pads (auch Loecher desselben
    Netzes, die ein Via meiden muss), fremden Bahnen, vorhandenen
    Vias desselben Netzes und Regelflaechen, die Vias verbieten.

    `nur_lage`: nur Kupfer auf DIESER Lage zaehlt als Hindernis fuer
    EINSEITIGE Objekte (SMD-Pads, Bahnsegmente). Durchkontaktierte
    Objekte (THT-Loecher, Vias) sperren immer, auf jeder Lage -- ihr
    Bohrloch geht durch beide. Ohne `nur_lage` (Standard, fuer VIAS:
    ein Via beruehrt ohnehin beide Lagen) zaehlt jedes Objekt, gleich
    auf welcher Lage. Gebraucht fuer eine Bahn, die NUR auf einer Lage
    liegt (masseheiler-Bruecken, Aufgabe 7c): ohne diesen Filter blockte
    fremdes Kupfer der ANDEREN Lage eine Bahn, die es dort nie beruehrt
    haette.
    """
    pos = pcbnew.VECTOR2I(int(x), int(y))
    kante = radius + mm(frei_mm)
    bb = board.GetBoardEdgesBoundingBox()
    if not (bb.GetLeft() + mm(0.8) < x < bb.GetRight() - mm(0.8)
            and bb.GetTop() + mm(0.8) < y < bb.GetBottom() - mm(0.8)):
        return False
    for f in board.GetFootprints():
        for p in f.Pads():
            einseitig = p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
            if einseitig and nur_lage is not None and not p.IsOnLayer(nur_lage):
                continue
            d = p.GetBoundingBox()
            d.Inflate(kante)
            if d.Contains(pos) and p.GetNetCode() != eigenes_netz:
                return False
            if not einseitig and d.Contains(pos):
                return False        # Loecher auch bei gleichem Netz meiden
    for t in board.Tracks():
        if t.GetNetCode() == eigenes_netz:
            if t.Type() == pcbnew.PCB_VIA_T:
                d = t.GetBoundingBox()
                d.Inflate(mm(0.2))
                if d.Contains(pos):
                    return False    # nicht auf ein vorhandenes Via
            continue
        if (t.Type() == pcbnew.PCB_TRACE_T and nur_lage is not None
                and t.GetLayer() != nur_lage):
            continue                # Bahn auf der jeweils ANDEREN Lage
        d = t.GetBoundingBox()
        d.Inflate(kante)
        if d.Contains(pos) and t.HitTest(pos, kante):
            return False
    for z in board.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias():
            if nur_lage is not None and not z.IsOnLayer(nur_lage):
                continue
            d = z.GetBoundingBox()
            d.Inflate(kante)
            if d.Contains(pos):
                return False
    return True

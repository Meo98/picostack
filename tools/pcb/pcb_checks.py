"""Nachpruefungen an der FERTIGEN Platine, die die DRC nicht macht.

Zwei Pruefungen, beide am gebauten Kupfer gemessen, nicht an der
Beschreibung geschaetzt:

1. FREIHAENGENDE VIAS. Ein Via, an dem auf einer der beiden Lagen
   nichts anliegt, ist eine gebohrte, verkupferte Sackgasse: es kostet
   Bohrzeit, schwaecht das Brett und ist fast immer der Rest eines
   Zuges, den der Router spaeter wieder aufgeloest hat. Die DRC sieht
   das NICHT -- ein einseitig angebundenes Via ist elektrisch
   vollstaendig verbunden (ueber die eine Lage), also meldet sie
   nichts. Gezaehlt wird pro Via und Lage: liegt dort ein
   Bahnendpunkt, ein Pad oder ein gefuelltes Zonenstueck desselben
   Netzes? Die GND-Naehvias (build.stitching_vias) sind der
   Normalfall, an dem BEIDE Lagen nur ueber Zonen anliegen -- deshalb
   zaehlen Zonen mit.

2. ANTENNE_FREI. stack_spec.ANTENNE_FREI ist eine BINDENDE Zusage an
   fremde Modulbauer: im Schatten der Pico-Antenne darf auf der
   Bestueckungsseite (F.Cu) kein Kupfer liegen. build.rule_areas()
   traegt dafuer eine Sperrflaeche ein, und der Router haelt sich
   daran -- aber "der Router haelt sich daran" ist eine Annahme, keine
   Messung. Hier wird nachgesehen: Bahnsegmente, Vias und
   Zonen-Fuellstuecke auf F.Cu gegen das Rechteck.
   AUSGENOMMEN sind die Pads der Vertragsstecker selbst (J100/J105
   reichen mit ihren unteren Kontakten in das Rechteck hinein) -- sie
   SIND der Anker, in den der Pico steckt, und stehen so im Vertrag.
   Ausgenommen ist ausserdem die Rueckseite: die Antenne sitzt auf dem
   aufgesteckten Pico, nicht auf dieser Platine.

Aufruf:  kipy pcb_checks.py <board.kicad_pcb>
Rueckgabe 1, sobald eine der beiden Pruefungen etwas findet (ROT).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import pcbnew
import stack_spec

mm = lambda v: int(round(v * 1e6))

# Wie nah ein Bahnendpunkt an der Via-Mitte liegen muss, um als
# Anschluss zu gelten. 0,05 mm, dieselbe Toleranz wie in
# autoroute.auf_platine(): freerouting rundet die DSN-Koordinaten in
# sein eigenes Raster und liefert dieselbe Lage um Bruchteile eines
# Mikrometers verschoben zurueck -- ein exakter Vergleich wuerde
# angeschlossene Vias als freihaengend melden.
NAH = mm(0.05)

# Die Stecker, deren Pads in ANTENNE_FREI liegen DUERFEN (s. Docstring).
STECKER_AUSNAHME = ("J100", "J105")


def freihaengende_vias(board):
    """Vias, an denen auf einer der beiden Lagen nichts anliegt."""
    lagen = (pcbnew.F_Cu, pcbnew.B_Cu)

    # Bahnendpunkte je (Lage, Netz), damit ein fremdes Netz nicht als
    # Anschluss durchgeht.
    enden = {}
    for t in board.Tracks():
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        schluessel = (t.GetLayer(), t.GetNetCode())
        for p in (t.GetStart(), t.GetEnd()):
            enden.setdefault(schluessel, []).append((p.x, p.y))

    def bahn_anliegend(lage, netz, x, y):
        for ex, ey in enden.get((lage, netz), ()):
            if abs(ex - x) <= NAH and abs(ey - y) <= NAH:
                return True
        return False

    def pad_anliegend(lage, netz, x, y):
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetCode() != netz or not pad.IsOnLayer(lage):
                    continue
                if pad.HitTest(pcbnew.VECTOR2I(x, y)):
                    return True
        return False

    def zone_anliegend(lage, netz, x, y):
        for z in board.Zones():
            if z.GetNetCode() != netz or not z.IsOnLayer(lage):
                continue
            if z.HitTestFilledArea(lage, pcbnew.VECTOR2I(x, y)):
                return True
        return False

    schlecht = []
    for v in board.Tracks():
        if v.Type() != pcbnew.PCB_VIA_T:
            continue
        pos = v.GetPosition()
        netz = v.GetNetCode()
        offen = []
        for lage in lagen:
            if not v.IsOnLayer(lage):
                continue
            if (bahn_anliegend(lage, netz, pos.x, pos.y)
                    or pad_anliegend(lage, netz, pos.x, pos.y)
                    or zone_anliegend(lage, netz, pos.x, pos.y)):
                continue
            offen.append(board.GetLayerName(lage))
        if offen:
            schlecht.append((pos.x / 1e6, pos.y / 1e6, v.GetNetname(),
                             ", ".join(offen)))
    return schlecht


def antenne_frei(board):
    """Kupfer auf F.Cu im Antennenschatten -- Verstoss gegen den Vertrag."""
    x0, y0, x1, y1 = stack_spec.ANTENNE_FREI
    kasten = pcbnew.BOX2I(pcbnew.VECTOR2I(mm(x0), mm(y0)),
                          pcbnew.VECTOR2I(mm(x1 - x0), mm(y1 - y0)))

    treffer = []
    for t in board.Tracks():
        if not t.IsOnLayer(pcbnew.F_Cu):
            continue
        art = "Via" if t.Type() == pcbnew.PCB_VIA_T else "Bahn"
        if kasten.Intersects(t.GetBoundingBox()) and t.HitTest(kasten, False):
            p = t.GetPosition()
            treffer.append("%s [%s] bei (%.2f|%.2f)"
                           % (art, t.GetNetname(), p.x / 1e6, p.y / 1e6))

    # Guss gegen das Rechteck schneiden statt Collide(): die
    # SHAPE_POLY_SET-Bindings nehmen an dieser Stelle nur Punkt, SEG
    # oder SHAPE -- kein BOX2I. Ein Schnitt, der nicht leer ist, IST
    # Kupfer im Sperrbereich.
    rechteck = pcbnew.SHAPE_POLY_SET()
    rechteck.NewOutline()
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        rechteck.Append(mm(px), mm(py))

    for z in board.Zones():
        if not z.IsOnLayer(pcbnew.F_Cu):
            continue
        schnitt = pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(pcbnew.F_Cu))
        schnitt.BooleanIntersection(rechteck)
        if not schnitt.IsEmpty():
            treffer.append("Gussstueck [%s] der Zone '%s', %.3f mm^2"
                           % (z.GetNetname(), z.GetZoneName(),
                              schnitt.Area() / 1e12))

    for fp in board.GetFootprints():
        if fp.GetReference() in STECKER_AUSNAHME:
            continue
        for pad in fp.Pads():
            if not pad.IsOnLayer(pcbnew.F_Cu):
                continue
            if kasten.Intersects(pad.GetBoundingBox()):
                p = pad.GetPosition()
                treffer.append("Pad %s von %s bei (%.2f|%.2f)"
                               % (pad.GetNumber(), fp.GetReference(),
                                  p.x / 1e6, p.y / 1e6))
    return treffer


def main(pfad):
    board = pcbnew.LoadBoard(pfad)
    board.BuildListOfNets()
    board.BuildConnectivity()

    fehler = 0

    schlecht = freihaengende_vias(board)
    n_vias = sum(1 for t in board.Tracks() if t.Type() == pcbnew.PCB_VIA_T)
    if schlecht:
        fehler = 1
        print("  ! %d von %d Vias haengen frei (Lage ohne Anschluss):"
              % (len(schlecht), n_vias))
        for x, y, netz, lagen in schlecht:
            print("      (%.3f|%.3f) [%s] offen auf: %s" % (x, y, netz, lagen))
    else:
        print("Vias: %d, alle beidseitig angebunden" % n_vias)

    treffer = antenne_frei(board)
    x0, y0, x1, y1 = stack_spec.ANTENNE_FREI
    if treffer:
        fehler = 1
        print("  ! ANTENNE_FREI (%.1f..%.1f x %.1f..%.1f) auf F.Cu verletzt, "
              "%d Fund(e):" % (x0, x1, y0, y1, len(treffer)))
        for t in treffer:
            print("      " + t)
    else:
        print("ANTENNE_FREI (%.1f..%.1f x %.1f..%.1f): F.Cu kupferfrei "
              "(ausser den Vertragsstecker-Pads %s)"
              % (x0, x1, y0, y1, "/".join(STECKER_AUSNAHME)))

    return fehler


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Aufruf: pcb_checks.py <board.kicad_pcb>")
    raise SystemExit(main(sys.argv[1]))

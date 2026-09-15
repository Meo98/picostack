#!/usr/bin/env python3
"""Schweisst KiCadRoutingTools-Vias, die knapp neben ihrer eigenen
Bahn landen, mit einem kurzen Steg auf die Bahn.

Herkunft: Aufgabe v2.1d (KiCadRoutingTools-Umstieg). Vierter
Handgriff, der beim Umstieg auf den neuen Router noetig wurde --
zusaetzlich zu den drei in task-v21d-eval-report.md dokumentierten
(Fab-Tier, DRC-Refill, Via-Tenting). Anders als die Eval-Platine
(Dimmer1 im Trockenlauf) zeigt der ECHTE Lauf ihn: tools/pcb/pcb_checks.py
meldete nach dem ersten Dimmer1-Routing 14 von 120 Vias als
"freihaengend" -- pro betroffener Via lag auf der gemeldeten Lage aber,
gemessen, immer ein Bahnende DESSELBEN Netzes 0,10-0,30 mm entfernt
(nie weiter, nie gar keins). Das ist kein DRC-Fehler (kicad-cli meldet
0 Verletzungen/0 unconnected, die Kupferflaechen ueberlappen sich
physisch innerhalb des Via-Restrings) und keine echte Sackgasse --
sondern ein Rasterversatz aus dem Router selbst: seine interne
Routing-Rasterweite liegt grober als pcb_checks.py's 0,05-mm-Toleranz
(kalibriert auf freerouting/Handverlegung, die immer exakt auf die
Via-Mitte trifft). `bahn_anliegend()` in pcb_checks.py prueft
Koinzidenz der Bahn-ENDPUNKTE, nicht physische Kupferueberlappung --
ein Massstab, den freerouting immer erfuellte und den dieser Router
knapp verfehlt.

Statt die Toleranz in pcb_checks.py (Projektdatei, nicht Teil dieser
Aufgabe) aufzuweichen -- das wuerde eine echte zukuenftige Sackgasse
im selben Abstand durchwinken --, fuegt dieses Skript echtes,
zusaetzliches Kupfer ein: einen kurzen Steg von der Via-Mitte zum
naechsten Bahnende desselben Netzes auf der gemeldeten Lage, in der
Breite dieser Bahn. Das macht aus "nah dran" ein echtes exaktes
Zusammentreffen, keine Kosmetik am Pruefskript. Nur Vias, deren
naechstes gleichnetziges Bahnende innerhalb MAX_ABSTAND liegen,
werden geschweisst; alles darueber bricht laut ab, weil das dann
keine Rasterungenauigkeit mehr waere, sondern eine echte Sackgasse,
die pcb_checks.py zu Recht meldet.

Zweite, seltenere Form (erster Fund: Dimmer4, 1 von 91 Vias): die Via
liegt nicht knapp NEBEN einem Bahnende, sondern MITTEN AUF einer
durchlaufenden Bahn desselben Netzes -- ein T-Abzweig, elektrisch
voellig normal und von kicad-cli DRC/Konnektivitaet laengst als
verbunden erkannt, aber `bahn_anliegend()` prueft nur Bahn-ENDPUNKTE,
nicht das Innere einer Strecke. Hierfuer wird KEIN neues Kupfer
eingefuegt, sondern die durchlaufende Bahn an der Via-Position in zwei
Teilstuecke zerlegt (gleiche Lage/Breite/Netz, identische Gesamtflaeche)
-- danach hat die Via einen echten Bahn-ENDPUNKT an genau ihrer eigenen
Position, ohne dass sich am verlegten Kupfer etwas aendert.

Aufruf: kipy via_weld.py <board.kicad_pcb>
Rueckgabe 1, wenn eine gemeldete Luecke weder durch einen kurzen Steg
noch durch eine Bahnzerlegung geschlossen werden kann (dann NICHT
geschweisst -- echter Befund, kein Rasterversatz/T-Abzweig).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pcbnew
from pcb_checks import freihaengende_vias

mm = lambda v: int(round(v * 1e6))

# Gemessen (Dimmer1, erster echter Lauf): 0,10 / 0,1414 (=0,1*sqrt(2))
# / 0,30 mm. 0,5 mm laesst reichlich Reserve nach oben, ohne in den
# Bereich zu kommen, in dem eine echte Fehlverlegung faelschlich
# geschweisst wuerde (das naechste Bauteil-Pad steht ueberall staerker
# entfernt als das).
MAX_ABSTAND = mm(0.5)

# Toleranz quer zur Bahnmitte fuer den T-Abzweig-Fall: die halbe
# Bahnbreite plus etwas Grid-Schlupf. Bahnbreiten reichen hier von
# 0,20 bis 1,00 mm -- 0,15 mm deckt die halbe Breite der schmalsten
# Signalbahn (0,10 mm) grosszuegig ab, ohne bei einer 1,00-mm-
# Leistungsbahn (0,50 mm Halbbreite) zu grob zu werden.
QUER_TOLERANZ = mm(0.15)

LAGEN = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}


def _naechster_punkt_auf_strecke(px, py, sx, sy, ex, ey):
    """Naechster Punkt auf der Strecke (s->e) zu (px,py), geklemmt auf
    das Segment selbst (kein Verlaengern ueber die Enden hinaus).
    Liefert (punkt_x, punkt_y, abstand, t in [0,1])."""
    dx, dy = ex - sx, ey - sy
    laenge2 = dx * dx + dy * dy
    if laenge2 == 0:
        return sx, sy, math.hypot(px - sx, py - sy), 0.0
    t = ((px - sx) * dx + (py - sy) * dy) / laenge2
    t = max(0.0, min(1.0, t))
    qx, qy = sx + t * dx, sy + t * dy
    return qx, qy, math.hypot(px - qx, py - qy), t


def _t_abzweig_schliessen(board, px, py, netz, lage):
    """Sucht eine durchlaufende Bahn desselben Netzes/derselben Lage,
    auf deren INNEREM (nicht an den Enden) die Via liegt, und zerlegt
    sie an genau dieser Stelle in zwei Teilstuecke. Liefert True, wenn
    geschlossen."""
    for t in list(board.Tracks()):
        if (t.Type() != pcbnew.PCB_TRACE_T
                or t.GetLayer() != lage
                or t.GetNetCode() != netz):
            continue
        s, e = t.GetStart(), t.GetEnd()
        qx, qy, d, tparam = _naechster_punkt_auf_strecke(
            px, py, s.x, s.y, e.x, e.y)
        # Echt INNERES Stueck, kein (schon vom Endpunkt-Schritt
        # behandelter) Fall nahe an s oder e.
        if d <= QUER_TOLERANZ and 0.02 < tparam < 0.98:
            mitte = pcbnew.VECTOR2I(px, py)
            teil1 = pcbnew.PCB_TRACK(board)
            teil1.SetStart(s)
            teil1.SetEnd(mitte)
            teil1.SetWidth(t.GetWidth())
            teil1.SetLayer(lage)
            teil1.SetNetCode(netz)
            teil2 = pcbnew.PCB_TRACK(board)
            teil2.SetStart(mitte)
            teil2.SetEnd(e)
            teil2.SetWidth(t.GetWidth())
            teil2.SetLayer(lage)
            teil2.SetNetCode(netz)
            board.Remove(t)
            board.Add(teil1)
            board.Add(teil2)
            return True
    return False


def main(pfad):
    board = pcbnew.LoadBoard(pfad)
    board.BuildListOfNets()
    board.BuildConnectivity()

    offene = freihaengende_vias(board)
    if not offene:
        print("via_weld: keine freihaengenden Vias, nichts zu tun")
        return 0

    geschweisst = 0
    zerlegt = 0
    ungeloest = []
    for x, y, netzname, lagen_text in offene:
        px, py = mm(x), mm(y)
        netz = board.GetNetcodeFromNetname(netzname)
        for lage_name in lagen_text.split(", "):
            lage = LAGEN[lage_name]
            bester = None
            beste_breite = None
            for t in board.Tracks():
                if (t.Type() != pcbnew.PCB_TRACE_T
                        or t.GetLayer() != lage
                        or t.GetNetCode() != netz):
                    continue
                for p in (t.GetStart(), t.GetEnd()):
                    d = math.hypot(p.x - px, p.y - py)
                    if bester is None or d < bester[0]:
                        bester = (d, p)
                        beste_breite = t.GetWidth()
            if bester is not None and bester[0] <= MAX_ABSTAND:
                _, ziel = bester
                steg = pcbnew.PCB_TRACK(board)
                steg.SetStart(pcbnew.VECTOR2I(px, py))
                steg.SetEnd(ziel)
                steg.SetWidth(beste_breite)
                steg.SetLayer(lage)
                steg.SetNetCode(netz)
                board.Add(steg)
                geschweisst += 1
                continue
            if _t_abzweig_schliessen(board, px, py, netz, lage):
                zerlegt += 1
                continue
            ungeloest.append((x, y, netzname, lage_name,
                               bester[0] / 1e6 if bester else None))

    if geschweisst or zerlegt:
        board.Save(pfad)

    print("via_weld: %d Steg(e) geschweisst, %d Bahn(en) am T-Abzweig "
          "zerlegt" % (geschweisst, zerlegt))
    if ungeloest:
        print("  ! %d Luecke(n) weder Steg noch T-Abzweig -- NICHT "
              "geschlossen (echter Befund):"
              % len(ungeloest))
        for x, y, netzname, lage_name, d in ungeloest:
            print("      (%.3f|%.3f) [%s] auf %s, naechstes Bahnende %s"
                  % (x, y, netzname, lage_name,
                     ("%.3f mm" % d) if d is not None else "keins gefunden"))
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Aufruf: via_weld.py <board.kicad_pcb>")
    raise SystemExit(main(sys.argv[1]))

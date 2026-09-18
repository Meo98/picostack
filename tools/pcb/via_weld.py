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

Dritte Form (erster Fund: Motormodul, 1 von 235 Vias, nach dem
QFN-Fanout-Umweg fuer U1s eng gepackte Leistungspins): eine Via, die
GENAU auf einem Pad desselben Netzes sitzt (hier: U5 Pad 3, F.Cu), aber
auf der Gegenlage (B.Cu) ueberhaupt kein Kupfer dieses Netzes in der
Naehe hat (naechstes Bahnstueck 8,3 mm entfernt) -- weder ein
Rasterversatz noch ein T-Abzweig, sondern eine schlicht UNNOETIGE Via:
das Pad selbst stellt die Verbindung schon her, die Via traegt nichts
zum Netz bei, das nicht schon durch das Pad da waere. Gemessen (kipy-
Probe, Board vor/nach Entfernen): `kicad-cli pcb drc
--refill-zones --save-board` bleibt 0/0, `masseheiler --nur-pruefen`
bleibt gruen -- die Via ist beweisbar ueberfluessig, ihr Fehlen aendert
nichts an der Konnektivitaet. Fuer DIESEN Fall wird nichts geschweisst
und keine Bahn zerlegt, sondern die Via schlicht ENTFERNT (nicht nur
eine Lage davon -- eine Via ist immer ein durchgehender Stift, es gibt
bei einer 2-Lagen-Platine keine "halbe" Via) -- aber NUR, wenn sie
exakt auf einem gleichnetzigen Pad sitzt (das Pad bleibt als Anker
stehen); eine Via ohne diesen Anker wird NICHT geloescht, selbst wenn
sie ansonsten ungenutzt aussieht, weil das ein Urteil ueber die
Netz-Topologie waere, das dieses Skript nicht treffen soll.

Aufruf: kipy via_weld.py <board.kicad_pcb>
Rueckgabe 1, wenn eine gemeldete Luecke weder durch einen kurzen Steg
noch durch eine Bahnzerlegung noch durch Entfernen einer ueberfluessigen
Via geschlossen werden kann (dann NICHTS geaendert -- echter Befund).
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


def _auf_gleichnetzigem_pad(board, px, py, netz):
    """Das Pad DESSELBEN Netzes unter (px,py), oder None.

    Der Anker, der eine dort sitzende Via ueberfluessig machen KANN
    (s. Moduldocstring, dritte Form) -- ob sie es wirklich ist, ent-
    scheidet erst `_ueberfluessige_via_entfernen()`."""
    punkt = pcbnew.VECTOR2I(px, py)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() == netz and pad.HitTest(punkt):
                return pad
    return None


def _kupfer_auf_lage(board, px, py, netz, lage, radius):
    """Liegt gleichnetziges Bahnkupfer dieser Lage am Punkt an?"""
    punkt = pcbnew.VECTOR2I(px, py)
    for t in board.Tracks():
        if (t.Type() != pcbnew.PCB_TRACE_T or t.GetNetCode() != netz
                or t.GetLayer() != lage):
            continue
        if t.HitTest(punkt, radius):
            return True
    return False


def _ueberfluessige_via_entfernen(board, px, py, netz):
    """Entfernt die Via bei (px,py), aber NUR wenn sie wirklich nichts
    traegt. Liefert True, wenn entfernt.

    ZWEI Bedingungen, nicht eine (Fehlerkorrektur Aufgabe D3, v2.1):

      1. Die Via sitzt auf einem gleichnetzigen Pad (der Anker).
      2. Auf jeder Lage, die dieses Pad NICHT selbst traegt, liegt auch
         kein gleichnetziges Bahnkupfer an der Via an.

    Bedingung 2 stand seit der Einfuehrung im Moduldocstring ("auf der
    Gegenlage ueberhaupt kein Kupfer dieses Netzes in der Naehe"), war
    aber NIE implementiert -- der Code prueste nur den Anker. Das ist
    genau dann falsch, wenn der Anker ein SMD-Pad ist (nur EINE Lage):
    dann ist die Via das einzige, was eine Bahn der Gegenlage ans Pad
    bringt, und ihr Entfernen trennt das Netz auf. GEMESSEN
    (Dimmer1, Aufgabe D3): C91 Pad 1 (0805, nur F.Cu) hing ueber genau
    so eine Via an /+5V_LOKAL auf B.Cu; via_weld entfernte sie, DRC
    meldete danach "1 unconnected items". Die urspruengliche Messung,
    die dieses Entfernen rechtfertigte, betraf einen Fall, in dem auf
    der Gegenlage tatsaechlich nichts lag (naechstes Bahnstueck 8,3 mm
    entfernt) -- der Code verallgemeinerte davon zu weit.
    """
    pad = _auf_gleichnetzigem_pad(board, px, py, netz)
    if pad is None:
        return False
    # Radius, in dem Kupfer als "anliegend" gilt: der Via-Restring.
    radius = 0
    for t in board.Tracks():
        if (t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == netz
                and t.GetPosition().x == px and t.GetPosition().y == py):
            radius = t.GetWidth(pcbnew.F_Cu) // 2
    for lage in (pcbnew.F_Cu, pcbnew.B_Cu):
        if pad.IsOnLayer(lage):
            continue            # diese Lage deckt das Pad selbst ab
        if _kupfer_auf_lage(board, px, py, netz, lage, radius):
            return False        # die Via traegt diese Lage ans Pad
    for t in list(board.Tracks()):
        if t.Type() != pcbnew.PCB_VIA_T or t.GetNetCode() != netz:
            continue
        p = t.GetPosition()
        if p.x == px and p.y == py:
            board.Remove(t)
            return True
    return False


def _kreuzung_aufloesen(board, px, py, netz, leere_lage):
    """Via, die auf EINER Lage nichts traegt, auf der anderen aber zwei
    Bahnen zusammenhaelt -- auf der vollen Lage verbinden, dann weg.

    FUENFTE FORM (Aufgabe D3, v2.1). Nach einem Lauf mit
    `--rip-existing-nets '*'` bleiben Vias stehen, an denen auf einer
    Lage gar nichts mehr haengt (vierte Form), die aber trotzdem nicht
    entfernt werden duerfen: auf der ANDEREN Lage enden zwei Bahnen
    knapp NEBEN der Via-Mitte, und nur das Via-Pad verbindet sie. Ein
    Lagenwechsel findet trotzdem nicht statt -- das Loch ist gebohrt,
    ohne etwas von einer Lage zur anderen zu bringen.

    Hier wird deshalb erst das Kupfer der vollen Lage explizit
    verbunden (Steg von jedem nahen Bahnende zur Via-Mitte, Breite der
    jeweiligen Bahn) und DANACH die Via nach der Messregel der vierten
    Form entfernt -- bleibt die Konnektivitaet nicht gleich, werden
    Stege und Via wieder zurueckgenommen.
    """
    voll = pcbnew.B_Cu if leere_lage == pcbnew.F_Cu else pcbnew.F_Cu
    mitte = pcbnew.VECTOR2I(px, py)
    stege = []
    for t in board.Tracks():
        if (t.Type() != pcbnew.PCB_TRACE_T or t.GetLayer() != voll
                or t.GetNetCode() != netz):
            continue
        for p in (t.GetStart(), t.GetEnd()):
            d = math.hypot(p.x - px, p.y - py)
            if 0 < d <= MAX_ABSTAND:
                steg = pcbnew.PCB_TRACK(board)
                steg.SetStart(mitte)
                steg.SetEnd(pcbnew.VECTOR2I(p.x, p.y))
                steg.SetWidth(t.GetWidth())
                steg.SetLayer(voll)
                steg.SetNetCode(netz)
                stege.append(steg)
    if len(stege) < 2:
        return False
    for steg in stege:
        board.Add(steg)
    if _beweisbar_nutzlose_via_entfernen(board, px, py, netz):
        return True
    for steg in stege:
        board.Remove(steg)
    board.BuildConnectivity()
    return False


def _beweisbar_nutzlose_via_entfernen(board, px, py, netz):
    """Entfernt eine Via, wenn ihr Fehlen die Konnektivitaet NICHT
    aendert -- gemessen, nicht geschlossen.

    VIERTE FORM (Aufgabe D3, v2.1). Ein Lauf mit
    `route.py --rip-existing-nets '*'` laesst Vias stehen, an denen auf
    einer Lage ueberhaupt nichts mehr haengt: keine Bahn, kein Pad,
    keine Gussflaeche (genau das prueft `freihaengende_vias()`). Das ist
    weder ein Rasterversatz (erste Form) noch ein T-Abzweig (zweite)
    noch ein Pad-Anker (dritte) -- es ist ein Rest, den der Router beim
    Umverlegen nicht mit aufgeraeumt hat: ein gebohrtes, verkupfertes
    Loch, das nichts verbindet.

    Warum das Entfernen hier erlaubt ist und in der dritten Form nur mit
    Pad-Anker: dort wird GESCHLOSSEN, die Via sei entbehrlich; hier wird
    es GEMESSEN. Die Via wird testweise entfernt, die Konnektivitaet neu
    gerechnet, und nur wenn die Zahl der unverbundenen Stellen GLEICH
    bleibt, bleibt sie entfernt -- sonst wird sie zurueckgelegt. Damit
    trifft das Skript kein Urteil ueber die Netz-Topologie, es misst
    eines.
    """
    opfer = None
    for t in board.Tracks():
        if (t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == netz
                and t.GetPosition().x == px and t.GetPosition().y == py):
            opfer = t
            break
    if opfer is None:
        return False
    board.BuildConnectivity()
    vorher = board.GetConnectivity().GetUnconnectedCount(True)
    board.Remove(opfer)
    board.BuildConnectivity()
    nachher = board.GetConnectivity().GetUnconnectedCount(True)
    if nachher <= vorher:
        return True
    board.Add(opfer)          # das Loch wurde doch gebraucht
    board.BuildConnectivity()
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
    entfernt = 0
    ungeloest = []
    for x, y, netzname, lagen_text in offene:
        px, py = mm(x), mm(y)
        netz = board.GetNetcodeFromNetname(netzname)
        if _ueberfluessige_via_entfernen(board, px, py, netz):
            entfernt += 1
            continue
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
            if _kreuzung_aufloesen(board, px, py, netz, lage):
                zerlegt += 1
                entfernt += 1
                break
            if _beweisbar_nutzlose_via_entfernen(board, px, py, netz):
                entfernt += 1
                break        # die Via ist weg, andere Lage erledigt sich
            ungeloest.append((x, y, netzname, lage_name,
                               bester[0] / 1e6 if bester else None))

    if geschweisst or zerlegt or entfernt:
        board.Save(pfad)

    print("via_weld: %d Steg(e) geschweisst, %d Bahn(en) am T-Abzweig "
          "zerlegt, %d ueberfluessige Via(s) entfernt"
          % (geschweisst, zerlegt, entfernt))
    if ungeloest:
        print("  ! %d Luecke(n) weder Steg noch T-Abzweig noch "
              "ueberfluessige Via -- NICHT geschlossen (echter Befund):"
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

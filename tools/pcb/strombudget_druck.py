"""Druckt das Strombudget auf den Bestueckungsdruck.

Warum das auf die Platine gehoert (Aufgabe D3, v2.1). Der Vertrag sagt
seit v2.1 eine Obergrenze fuer den 24-V-Strang zu
(`stack_spec.STROMBUDGET`), und diese Zusage ist KLEINER, als die
Kanalzahl vermuten laesst: ein Dimmer4 hat vier Klemmen fuer je 3 A,
aber sein Verpolschutz Q90 (IRFR5305, TO-252) traegt in Summe nur 4,0 A.
Wer das Brett in die Hand nimmt, sieht vier Klemmen und keine Zahl.

Eine Zusage, die nur in einer Datei steht, schuetzt niemanden am
Arbeitstisch. Dieselbe Ueberlegung wie beim Elko-Polaritaetshinweis in
`build.mark_version()` -- dort waren zwei Elkos explodiert, weil der
Aufdruck die Wahrheit nicht zeigte.

Was gedruckt wird (zwei Zeilen, F.SilkS):

    +24V MAX 4.0A          <- stack_spec.STROMBUDGET["modul_gesamt_a"]
    STACK MAX 3.0A         <- ...["stapel_durchleitung_a"]

Beide Zahlen kommen aus dem Vertrag, keine wird hier wiederholt -- wer
das Budget aendert, aendert automatisch den Aufdruck.

Der Platz wird GESUCHT, nicht geraten: das Werkzeug probiert ein Raster
moeglicher Positionen durch und nimmt die erste, die weder ein Pad noch
einen vorhandenen Silkscreen-Text noch den Platinenrand beruehrt. Findet
es keine, bricht es ab (Rueckgabe 1), statt den Text irgendwohin zu
setzen -- ein Aufdruck ueber einem Pad ist schlimmer als keiner.

Aufruf: kipy strombudget_druck.py <board.kicad_pcb> [--nur-pruefen]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import fertigung
import stack_spec as S

import pcbnew

mm = lambda v: int(round(v * 1e6))

HOEHE = fertigung.SILK_TEXT      # 0,8 mm -- die Mindesthoehe der Regeln
DICKE = 0.15
ZEILENABSTAND = 1.4
RAND = 1.0                        # Abstand zum Platinenrand
FREI = 0.3                        # Abstand zu Pads und fremdem Silkscreen


def zeilen():
    """Die beiden Zeilen, beide aus dem Vertrag gerechnet."""
    B = S.STROMBUDGET
    return ("+24V MAX %.1fA" % B["modul_gesamt_a"],
            "STACK MAX %.1fA" % B["stapel_durchleitung_a"])


def _hindernisse(board):
    """Bounding-Boxen, die der Aufdruck nicht beruehren darf."""
    aus = []
    for f in board.GetFootprints():
        for p in f.Pads():
            aus.append(p.GetBoundingBox())
        for it in f.GraphicalItems():
            if it.GetLayer() in (pcbnew.F_SilkS, pcbnew.F_Fab):
                if it.GetLayer() == pcbnew.F_SilkS:
                    aus.append(it.GetBoundingBox())
        for t in (f.Reference(), f.Value()):
            if t.IsVisible() and t.GetLayer() == pcbnew.F_SilkS:
                aus.append(t.GetBoundingBox())
    for it in board.GetDrawings():
        if it.GetLayer() == pcbnew.F_SilkS:
            aus.append(it.GetBoundingBox())
    return aus


def _passt(board, hindernisse, x, y, texte):
    """Passen beide Zeilen mit der linken oberen Ecke bei (x, y)?"""
    bb = board.GetBoardEdgesBoundingBox()
    kaesten = []
    for i, txt in enumerate(texte):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(mm(HOEHE), mm(HOEHE)))
        t.SetTextThickness(mm(DICKE))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y + i * ZEILENABSTAND)))
        k = t.GetBoundingBox()
        if not (bb.GetLeft() + mm(RAND) < k.GetLeft()
                and k.GetRight() < bb.GetRight() - mm(RAND)
                and bb.GetTop() + mm(RAND) < k.GetTop()
                and k.GetBottom() < bb.GetBottom() - mm(RAND)):
            return None
        kaesten.append((t, k))
    for _t, k in kaesten:
        gross = pcbnew.BOX2I(k.GetOrigin(), k.GetSize())
        gross.Inflate(mm(FREI))
        for h in hindernisse:
            if gross.Intersects(h):
                return None
    return [t for t, _k in kaesten]


def main(pfad, nur_pruefen=False):
    board = pcbnew.LoadBoard(pfad)
    texte = zeilen()

    # Schon gestempelt? Dann nur pruefen, ob die Zahlen noch stimmen --
    # ein zweiter Aufdruck neben einem veralteten waere schlimmer als
    # gar keiner.
    vorhanden = [d for d in board.GetDrawings()
                 if isinstance(d, pcbnew.PCB_TEXT)
                 and d.GetLayer() == pcbnew.F_SilkS
                 and d.GetText().startswith(("+24V MAX", "STACK MAX"))]
    alt = sorted(d.GetText() for d in vorhanden)
    if alt:
        if alt == sorted(texte):
            print("Strombudget bereits aufgedruckt: %s" % " / ".join(texte))
            return 0
        print("ROT: aufgedruckt steht %s, der Vertrag sagt %s"
              % (" / ".join(alt), " / ".join(texte)))
        if nur_pruefen:
            return 1
        for d in vorhanden:
            board.Remove(d)

    if nur_pruefen:
        print("ROT: kein Strombudget auf dem Bestueckungsdruck (%s)"
              % " / ".join(texte))
        return 1

    hindernisse = _hindernisse(board)
    bb = board.GetBoardEdgesBoundingBox()
    schritt = 0.5
    gefunden = None
    # Von unten links nach oben rechts -- unten links liegt bei allen
    # vier Brettern der Versionsvermerk, also ist die Gegend erfahrungs-
    # gemaess der ruhigste Fleck; probiert wird trotzdem das ganze Brett.
    y = bb.GetBottom() / 1e6 - RAND - 2 * ZEILENABSTAND
    while y > bb.GetTop() / 1e6 + RAND and gefunden is None:
        x = bb.GetLeft() / 1e6 + RAND
        while x < bb.GetRight() / 1e6 - RAND:
            t = _passt(board, hindernisse, x, y, texte)
            if t:
                gefunden = t
                break
            x += schritt
        y -= schritt
    if gefunden is None:
        print("ROT: kein freier Platz fuer den Aufdruck gefunden")
        return 1
    for t in gefunden:
        board.Add(t)
    board.Save(pfad)
    p = gefunden[0].GetPosition()
    print("Strombudget aufgedruckt bei (%.2f|%.2f): %s"
          % (p.x / 1e6, p.y / 1e6, " / ".join(texte)))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Aufruf: strombudget_druck.py <board.kicad_pcb> "
                          "[--nur-pruefen]")
    raise SystemExit(main(sys.argv[1], "--nur-pruefen" in sys.argv[2:]))

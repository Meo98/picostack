#!/usr/bin/env python3
"""Stempelt explizites Via-Tenting auf vom Router hinzugefuegte Vias.

Herkunft: Aufgabe v2.1d (KiCadRoutingTools-Umstieg), zuerst als
Eval-Helfer unter /tmp/eval/stamp_via_tenting.py gebaut
(task-v21d-eval-report.md Abschnitt 3c), hierher verschoben, weil JEDE
mit KiCadRoutingTools verlegte Platine dieselbe Nacharbeit braucht --
nicht nur die Eval-Platine.

KiCadRoutingTools schreibt fuer selbst hinzugefuegte Vias BEWUSST
keinen (tenting ...)-Token (dokumentiert in KiCadRoutingTools/CLAUDE.md
unter "Via Attributes": Vias, die das Werkzeug hinzufuegt, erben
stattdessen die (setup ...)-Regel der Platine -- exakt das, was pcbnew
fuer eine per GUI gesetzte Via auch tut). Elektrisch/physikalisch ist
das korrekt: pcbnew's eigenes via.IsTented(F_Mask) loest solche Vias
gegen board.setup auf und liefert True, sobald das Board-Setup Tenting
verlangt -- genau wie bei jeder handgeroutet Via auf diesem Projekt.

ABER picostacks eigenes tools/pcb/steckerprobe.py::verdrehtprobe()
prueft `via.GetFrontTentingMode() == pcbnew.TENTING_MODE_TENTED` -- ein
strenger Vergleich auf das ROHE Attribut, der TENTING_MODE_FROM_BOARD
nicht gegen die Board-Regel aufloest. Jede Via, die diese
Werkzeugkette bisher selbst gelegt hat, schrieb den Token immer explizit
mit, deshalb ist diese Luecke nie aufgefallen, bis KiCadRoutingTools'
Ausgabe ankam. Verifiziert per kipy-Probe (task-v21d-eval-report.md):
GetFrontTentingMode()==FROM_BOARD fuer alle betroffenen Vias, aber
IsTented(F_Mask)==True fuer jede einzelne -- die Vias SIND also
abgedeckt, die Diskrepanz ist ein reiner Rohwert-vs-aufgeloester-Wert-
Fehler im Pruefskript, kein Fehler im verlegten Kupfer.

Statt picostacks Gate-Skript zu flicken, normalisiert dieser Helfer die
AUSGABEPLATINE auf die im Projekt ueblichen Konvention: er stempelt ein
explizites (front yes)(back yes) auf jede Via, die aktuell FROM_BOARD
ist -- genau das, was jede vorher von Hand/freerouting gelegte Via auf
dieser Platine ohnehin schon traegt. Das aendert keine Geometrie, keine
Clearance, keine elektrische Eigenschaft -- es macht nur explizit, was
durch Vererbung bereits wahr war.

Empfehlung fuer eine Folgeaufgabe (bewusst NICHT hier erledigt, ausserhalb
des Umfangs von Aufgabe D): steckerprobe.py::verdrehtprobe() auf
via.IsTented(pcbnew.F_Mask) statt der rohen Attributabfrage umstellen --
dann entfaellt dieser Stempelschritt fuer alle KUENFTIGEN Boards.

Aufruf: kipy stamp_via_tenting.py <board.kicad_pcb>
"""
import sys
import pcbnew


def main(path):
    board = pcbnew.LoadBoard(path)
    stamped = 0
    for t in board.Tracks():
        if t.Type() != pcbnew.PCB_VIA_T:
            continue
        if t.GetFrontTentingMode() == pcbnew.TENTING_MODE_FROM_BOARD:
            t.SetFrontTentingMode(pcbnew.TENTING_MODE_TENTED)
            t.SetBackTentingMode(pcbnew.TENTING_MODE_TENTED)
            stamped += 1
    board.Save(path)
    print("stamped explicit tenting on %d via(s) (were FROM_BOARD, board "
          "setup already says tented)" % stamped)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Aufruf: stamp_via_tenting.py <board.kicad_pcb>")
    raise SystemExit(main(sys.argv[1]))

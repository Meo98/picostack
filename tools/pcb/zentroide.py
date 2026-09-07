"""Schreibt je Board die Pad-Zentroiden aller Bauteile als CSV.

    tools/pcb/kipy tools/pcb/zentroide.py <board.kicad_pcb> <ziel.csv>

Hintergrund (Bestellrunde 2026-09-07): KiCads Positionsexport liefert
den FOOTPRINT-ANKER, und der liegt bei den THT-Familien (CP_Radial,
TerminalBlock, PinHeader) auf Pin 1 statt in der Bauteilmitte. JLC
setzt sein Bauteilmodell aber auf die Mid-X/Y-Koordinate der CPL --
der Elko schwebte im Bestueckungs-Preview einen halben Pinabstand
(1,75 mm) neben seinen Loechern, die Klemmen ebenso. Statt die
Anker-Offsets je Footprint von Hand nachzurechnen (fehlertraechtig bei
gedrehten Teilen), fragen wir pcbnew nach den ABSOLUTEN Pad-Lagen und
mitteln sie; jlc.py ersetzt damit die Anker-Koordinate genau fuer die
betroffenen Footprint-Familien.
"""
import csv
import sys

import pcbnew


def main(pcb_pfad, ziel):
    brett = pcbnew.LoadBoard(pcb_pfad)
    with open(ziel, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Ref", "MidX", "MidY"])
        for fp in sorted(brett.GetFootprints(),
                         key=lambda fp: fp.GetReference()):
            pads = list(fp.Pads())
            if not pads:
                continue
            x = sum(p.GetPosition().x for p in pads) / len(pads)
            y = sum(p.GetPosition().y for p in pads) / len(pads)
            # Gleiche Konvention wie kicad-cli export pos: x wie im
            # Board, y negiert.
            w.writerow([fp.GetReference(),
                        "%.4f" % (x / 1e6), "%.4f" % (-y / 1e6)])
    print("Zentroiden: %s" % ziel)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

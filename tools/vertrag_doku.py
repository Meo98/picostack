"""Erzeugt docs/vertrag.md aus tools/stack_spec.py.

Von Hand gepflegte Doppelungen laufen auseinander. Wer die
Steckerbelegung aendert, aendert stack_spec.py und laesst dieses
Skript laufen -- das Dokument hat keine eigene Wahrheit.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stack_spec as S

ZIEL = os.path.join(HERE, "..", "docs", "vertrag.md")


def tabelle(kopf, zeilen):
    aus = ["| " + " | ".join(kopf) + " |",
           "|" + "|".join(["---"] * len(kopf)) + "|"]
    aus += ["| " + " | ".join(str(z) for z in zeile) + " |"
            for zeile in zeilen]
    return "\n".join(aus)


def main():
    teile = ["# PicoStack — der Vertrag",
             "",
             "Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.",
             "",
             "## Status",
             "",
             "Die Zusagen rund um das Flashen -- die Pins `FLASH_TX`, "
             "`FLASH_RX`, `SEL`, `SEL_CLK` und `FLASH_MODE` und alles, "
             "was daran haengt -- ruhen auf einer Annahme, die noch "
             "**nicht auf Hardware belegt** ist: dass der Pico einen "
             "Modul-MCU ueber dessen ROM-Bootlader wirklich beschreiben "
             "kann. Geprueft ist bisher nur das Protokoll gegen eine "
             "Attrappe, nicht gegen echtes Silizium. Stand und offene "
             "Schritte: `docs/nachweis-2026-08.md`.",
             "",
             "## Umriss",
             "",
             "%.1f x %.1f mm, Ecken %.1f mm gerundet, %.1f mm zwischen "
             "den Platinen." % (S.BOARD_W, S.BOARD_H, S.CORNER_R,
                                S.STAPEL_ABSTAND),
             "",
             tabelle(["M3-Bohrung", "x", "y", "Bohrdurchmesser"],
                     [(i + 1, x, y, S.M3_DRILL) for i, (x, y) in
                      enumerate(S.M3_HOLES)]),
             "",
             "## Steckerbelegung",
             "",
             tabelle(["Pin", "Rolle"],
                     [(p, S.PIN_ROLLE[p]) for p in sorted(S.PIN_ROLLE)
                      if S.PIN_ROLLE[p] != "frei"]),
             "",
             "Alle nicht aufgefuehrten Pins gehen unveraendert durch "
             "und stehen Modulen frei zur Verfuegung.",
             "",
             "## Auflagen an die Modulfirmware",
             "",
             "\n\n".join("- " + a for a in S.AUFLAGEN),
             "",
             "## Modultypen",
             "",
             tabelle(["Nummer", "Name", "Kanaele"],
                     [("0x%02X" % nr, t["name"], t["kanaele"])
                      for nr, t in sorted(S.MODULTYPEN.items())]),
             "",
             "Nummern ab `0x80` bleiben fremden Modulen vorbehalten.",
             "",
             "## Kennwiderstaende",
             "",
             tabelle(["Stufe", "Widerstand", "Spannungsanteil"],
                     [(i, "%.0f" % r, "%.3f" % S.ID_ANTEIL(r))
                      for i, r in enumerate(S.ID_WIDERSTAENDE)]),
             ""]
    with open(ZIEL, "w", encoding="utf-8") as f:
        f.write("\n".join(teile))
    print("geschrieben:", ZIEL)


if __name__ == "__main__":
    main()

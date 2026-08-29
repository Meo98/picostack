"""Prueft die Logik der Auswahlkette als Wahrheitstabelle."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "tools"))
from kette import modul_zustand

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# Ausser Flash-Modus laufen ALLE Module, unabhaengig vom Token.
# Das ist der Normalbetrieb -- wer das vergisst, baut einen Stapel,
# in dem nur ein Modul laeuft.
for sel in (0, 1):
    reset, boot0, sel_out = modul_zustand(flash_mode=0, sel_in=sel)
    check("Normalbetrieb sel=%d: kein Reset" % sel, reset, 0)
    check("Normalbetrieb sel=%d: kein Bootlader" % sel, boot0, 0)
    check("Normalbetrieb sel=%d: Token weiter" % sel, sel_out, sel)

# Im Flash-Modus liegt jedes Modul im Reset, ausser dem gewaehlten.
reset, boot0, sel_out = modul_zustand(flash_mode=1, sel_in=0)
check("Flash, nicht gewaehlt: Reset", reset, 1)
check("Flash, nicht gewaehlt: kein Bootlader", boot0, 0)
check("Flash, nicht gewaehlt: Token bleibt aus", sel_out, 0)

reset, boot0, sel_out = modul_zustand(flash_mode=1, sel_in=1)
check("Flash, gewaehlt: kein Reset", reset, 0)
check("Flash, gewaehlt: Bootlader", boot0, 1)

# Der Kern der Kette: das gewaehlte Modul gibt das Token NICHT weiter.
# Gaebe es weiter, waeren zwei Module gleichzeitig wach und wuerden
# sich auf der gemeinsamen Sendeleitung ins Wort fallen.
check("Flash, gewaehlt: Token wird angehalten", sel_out, 0)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

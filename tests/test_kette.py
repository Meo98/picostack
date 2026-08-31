"""Prueft die Auswahlkette: Gatterlogik und Schieberegister."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "tools"))
from kette import modul_zustand, Modul, kette_takten

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- Teil 1: die Gatterlogik als Wahrheitstabelle -------------------
# Das ist genau das, was die Gatter auf dem Modul aus FLASH_MODE und
# dem Flipflop-Ausgang Q machen.

# Ausser Flash-Modus laufen ALLE Module, unabhaengig vom Q im
# Schieberegister. Das ist der Normalbetrieb -- wer das vergisst, baut
# einen Stapel, in dem nur ein Modul laeuft.
for q in (0, 1):
    reset, boot0, sel_out = modul_zustand(flash_mode=0, q=q)
    check("Normalbetrieb q=%d: kein Reset" % q, reset, 0)
    check("Normalbetrieb q=%d: kein Bootlader" % q, boot0, 0)
    check("Normalbetrieb q=%d: SEL_OUT ist Q" % q, sel_out, q)

# Im Flash-Modus liegt jedes Modul im Reset, ausser dem gewaehlten.
reset, boot0, sel_out = modul_zustand(flash_mode=1, q=0)
check("Flash, nicht gewaehlt: Reset", reset, 1)
check("Flash, nicht gewaehlt: kein Bootlader", boot0, 0)
check("Flash, nicht gewaehlt: SEL_OUT bleibt 0", sel_out, 0)

reset, boot0, sel_out = modul_zustand(flash_mode=1, q=1)
check("Flash, gewaehlt: kein Reset", reset, 0)
check("Flash, gewaehlt: Bootlader", boot0, 1)

# SEL_OUT ist der Flipflop-Ausgang selbst, kein gattergesteuertes
# Anhalten: das ausgewaehlte Modul reicht seine 1 an das D des Moduls
# darunter weiter. Wach wird das erst mit dem naechsten Takt -- und
# dann ist dieses Modul nicht mehr gewaehlt. Zwei gleichzeitig wache
# MCU auf der gemeinsamen Sendeleitung kann es dadurch nicht geben.
check("Flash, gewaehlt: SEL_OUT ist Q", sel_out, 1)


# --- Teil 2: die Kette als Schieberegister --------------------------
# Ohne diese Pruefung ist die Zusage der Spezifikation nicht gedeckt:
# jedes Modul muss einzeln erreichbar sein, und es darf nie mehr als
# eines gleichzeitig ausgewaehlt sein. Die frueher rein kombinatorische
# Fassung erreichte nur das oberste Modul -- unbemerkt, weil niemand
# mehr als ein Modul simuliert hat.

def gewaehlte(zustaende):
    """Indizes der Module, deren BOOT0 anliegt (= ausgewaehlt)."""
    return [i for i, (_r, boot0, _s) in enumerate(zustaende) if boot0]


N = 3
stapel = [Modul() for _ in range(N)]

# Vor dem ersten Takt ist das Register leer: niemand ist gewaehlt.
check("leeres Register: niemand gewaehlt",
      gewaehlte([m.zustand(flash_mode=1) for m in stapel]), [])

# Der Sockel legt eine 1 an und taktet einmal -- danach nur noch 0.
# Die 1 wandert bei jedem Takt genau eine Position tiefer.
for erwartet in range(N):
    sel_in = 1 if erwartet == 0 else 0
    zustaende = kette_takten(stapel, sel_in=sel_in, flash_mode=1)

    check("Takt %d: genau ein Modul gewaehlt" % (erwartet + 1),
          gewaehlte(zustaende), [erwartet])
    for i, (reset, boot0, _s) in enumerate(zustaende):
        soll = 1 if i == erwartet else 0
        check("Takt %d: Modul %d BOOT0" % (erwartet + 1, i + 1), boot0, soll)
        check("Takt %d: Modul %d RESET" % (erwartet + 1, i + 1),
              reset, 1 - soll)

# Jedes der drei Module war einmal an der Reihe: die Kette ist
# vollstaendig durchlaufen, keines bleibt unerreichbar.

# Ein Takt weiter: das Bit faellt unten aus der Kette, niemand ist mehr
# gewaehlt. So merkt der Sockel, dass er das Ende des Stapels erreicht
# hat, und kennt damit zugleich die Zahl der Module.
zustaende = kette_takten(stapel, sel_in=0, flash_mode=1)
check("nach dem letzten Modul: niemand mehr gewaehlt",
      gewaehlte(zustaende), [])

# Zwei Bits gleichzeitig waeren zwei wache MCU auf einer Sendeleitung.
# Der Sockel darf deshalb nur einen einzigen Takt lang eine 1 anlegen.
stapel = [Modul() for _ in range(N)]
kette_takten(stapel, sel_in=1, flash_mode=1)
zustaende = kette_takten(stapel, sel_in=1, flash_mode=1)
check("zwei 1en am Eingang: zwei Module wach (Sockel muss das lassen)",
      gewaehlte(zustaende), [0, 1])

# Im Normalbetrieb laufen alle, egal was im Register steht.
zustaende = [m.zustand(flash_mode=0) for m in stapel]
check("Normalbetrieb: kein Modul im Reset",
      [r for r, _b, _s in zustaende], [0] * N)
check("Normalbetrieb: kein Modul im Bootlader", gewaehlte(zustaende), [])

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

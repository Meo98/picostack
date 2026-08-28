"""Prueft den Vertrag. Ohne KiCad, ohne Hardware."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "tools"))
import stack_spec as S

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- Umriss und Lochbild ---
check("Breite", S.BOARD_W, 64.0)
check("Hoehe", S.BOARD_H, 60.0)
check("vier M3", len(S.M3_HOLES), 4)
check("Lochbild 56 mm", S.M3_HOLES[2][0] - S.M3_HOLES[0][0], 56.0)
check("Lochbild 52 mm", S.M3_HOLES[1][1] - S.M3_HOLES[0][1], 52.0)

# --- Steckerbelegung ---
check("40 Pins beschrieben", len(S.PIN_ROLLE), 40)

# Jede reservierte Rolle kommt genau einmal vor. Zwei Pins mit
# derselben Aufgabe waeren ein stiller Kurzschluss im Vertrag.
for rolle in S.RESERVIERT:
    n = sum(1 for r in S.PIN_ROLLE.values() if r == rolle)
    check("Rolle %s genau einmal" % rolle, n, 1)

# Reservierte Rollen duerfen nicht auf Versorgungspins liegen.
for pin, rolle in S.PIN_ROLLE.items():
    if rolle in S.RESERVIERT:
        check("Pin %d ist kein Versorgungspin" % pin,
              S.IST_VERSORGUNG(pin), False)

# --- Modultypen ---
check("Motor hat Nummer", "Motor" in
      {t["name"] for t in S.MODULTYPEN.values()}, True)
# Nummern ab 0x80 bleiben fremden Modulen vorbehalten; wer sie
# selbst belegt, nimmt der Community den Platz weg.
for nr in S.MODULTYPEN:
    check("Nummer 0x%02X unter 0x80" % nr, nr < 0x80, True)

# --- Kennwiderstaende ---
# Zwei Teiler zu je 16 Stufen ergeben 256 Nummern. Die Stufen muessen
# sich im ADC sicher unterscheiden lassen.
stufen = sorted(S.ID_WIDERSTAENDE)
check("16 Stufen", len(stufen), 16)
verhaeltnisse = [S.ID_ANTEIL(r) for r in stufen]
abstaende = [b - a for a, b in zip(verhaeltnisse, verhaeltnisse[1:])]
check("Stufen mindestens 3 % auseinander", min(abstaende) > 0.03, True)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

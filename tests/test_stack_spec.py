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

# Alle vier Ecken einzeln, nicht nur zwei Differenzen: sonst darf die
# vierte Bohrung irgendwo liegen und der Test merkt es nicht.
check("Lochbild vollstaendig", sorted(S.M3_HOLES),
      [(4.0, 4.0), (4.0, 56.0), (60.0, 4.0), (60.0, 56.0)])

# Masse, die die Spezifikation zusichert und die bisher niemand prueft.
check("Eckenradius", S.CORNER_R, 3.0)
check("M3-Bohrdurchmesser", S.M3_DRILL, 3.2)
check("Stapelabstand", S.STAPEL_ABSTAND, 13.0)

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

# --- Stapelstecker/Kettenstecker (seit 2026-08-31) -------------------
# SEL laeuft seit der Umstellung auf den Stapelstecker (Buchse mit
# durchgehendem Stift) nicht mehr ueber den 2x20-Stecker, sondern ueber
# einen eigenen Kettenstecker -- die Rolle "SEL" darf in
# RESERVIERT/PIN_ROLLE nicht mehr auftauchen.
check("SEL nicht mehr reserviert", "SEL" in S.RESERVIERT, False)
check("SEL steht in keiner Pin-Rolle mehr",
      "SEL" in S.PIN_ROLLE.values(), False)

# Pin 4 (GP2) war kurz "frei" (erste Runde), ist seit Befund 2
# (Aufgabe-4-Fix-1, 2026-08-31) aber wieder eine echte Vertragsrolle:
# SEL_OUT, der Pico-Pin, der die Auswahlkette treibt. Grund: die lokale,
# unreservierte Verdrahtung auf GP8 (Pin 11) kollidierte, sobald Pin 11
# selbst zu einem durchgereichten freien GPIO wurde (stack_spec selbst
# bleibt unveraendert dafuer verantwortlich, dass GP8 wieder "frei" ist,
# s. Pruefung unten).
check("Pin 4 (GP2) traegt SEL_OUT", S.PIN_ROLLE[4], "SEL_OUT")
check("SEL_OUT reserviert", "SEL_OUT" in S.RESERVIERT, True)
check("SEL_OUT kein Versorgungspin", S.IST_VERSORGUNG(4), False)
check("Pin 11 (GP8) frei (kein lokaler SEL-Treiber mehr)",
      S.PIN_ROLLE[11], "frei")

# Der Kettenstecker traegt genau SEL und eine GND, sonst nichts.
check("Kettenstecker zweipolig", len(S.STECKER_KETTE["pins"]), 2)
check("Kettenstecker traegt SEL",
      "SEL" in S.STECKER_KETTE["pins"].values(), True)
check("Kettenstecker traegt GND",
      "GND" in S.STECKER_KETTE["pins"].values(), True)

# Die Einstecktiefe wird aus STAPEL_ABSTAND und den Steckermassen
# nachgerechnet (nicht nur die Zahl 13.0 abgefragt) -- das faengt den
# naechsten Denkfehler ab: wer STAPEL_ABSTAND aendert, ohne die
# Steckermasse mitzudenken, oder umgekehrt.
MINDEST_EINSTECKTIEFE = 2.0  # mm, konservativ unter dem knappsten
# belegten Fall (Kettenstecker, rechnerisch 3,1 mm bei 13,0 mm,
# hardware/bauteile-1b.md Beleg 1/Beleg 6) -- faengt Rechen- oder
# Bauteiländerungen ab, ohne die exakte Zahl selbst zu duplizieren.
check("Stapelstecker-Einstecktiefe ueber Mindestschwelle",
      S.EINSTECKTIEFE_STAPEL() > MINDEST_EINSTECKTIEFE, True)
check("Kettenstecker-Einstecktiefe ueber Mindestschwelle",
      S.EINSTECKTIEFE_KETTE() > MINDEST_EINSTECKTIEFE, True)

# Ueber den Schraubklemmen (urspruenglicher Grund fuer den alten
# 15,0-mm-Wert) und dem K7805 (hoechstes denkbares Bauteil im Spalt,
# falls je ein Modul es nutzt) muss im Spalt noch Luft bleiben.
check("Ueber der Klemme bleibt Luft im Spalt",
      (S.STAPEL_ABSTAND - S.PLATINE_DICKE - S.KLEMME_HOEHE_MM) > 0, True)
check("Ueber dem K7805 bleibt Luft im Spalt",
      (S.STAPEL_ABSTAND - S.PLATINE_DICKE - S.K7805_HOEHE_MM) > 0, True)

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

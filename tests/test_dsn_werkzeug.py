"""Prueft das Aufspalten von Mehrpunkt-Drahtzuegen in der DSN.

Hintergrund in tools/pcb/dsn_werkzeug.py: freerouting haengt sich an
Mehrpunkt-wire-Pfaden auf, die KiCads DSN-Export je nach Reihenfolge
aus der Vorverdrahtung verschmilzt.

Rot-Nachweis: Testfall 3 fuettert exakt den Pfad, der das Motormodul
am 2026-09-02 aufgehaengt hat -- ohne das Aufspalten (Anzahl 0 oder
unveraenderter Text) wird er rot.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "tools", "pcb"))
import dsn_werkzeug  # noqa: E402

FEHLER = []


def pruefe(name, gut, meldung):
    if gut:
        print("  ok  %s" % name)
    else:
        FEHLER.append(name)
        print("  ROT %s -- %s" % (name, meldung))


# 1: Zweipunkt-Zuege bleiben wortgleich stehen.
zwei = ('    (wire (path F.Cu 400  42800 -25725  44600 -25725)'
        '(net /+24V)(type route))\n')
neu, n = dsn_werkzeug.zweipunkt_zeilen(zwei)
pruefe("zweipunkt-unangetastet", neu == zwei and n == 0,
       "Zweipunkt-Zug veraendert (n=%d)" % n)

# 2: Fremde Zeilen (Header, Netze, Vias) bleiben wortgleich stehen.
fremd = ('  (resolution um 10)\n'
         '    (net /+24V\n'
         '    (via "Via[0-1]_600:300_um"  45250 -25725 (net GND))\n')
neu, n = dsn_werkzeug.zweipunkt_zeilen(fremd)
pruefe("fremdzeilen-unangetastet", neu == fremd and n == 0,
       "fremde Zeile veraendert")

# 3 (ROT-NACHWEIS): der Dreipunkt-Pfad des Motormodul-Haengers muss in
# zwei Zweipunkt-Zuege zerfallen, Lage/Breite/Netz/Typ unveraendert.
drei = ('    (wire (path F.Cu 1000  45250 -25725  45575 -25400  '
        '47775 -25400)(net /+24V)(type route))\n')
neu, n = dsn_werkzeug.zweipunkt_zeilen(drei)
erwartet = ('    (wire (path F.Cu 1000  45250 -25725  45575 -25400)'
            '(net /+24V)(type route))\n'
            '    (wire (path F.Cu 1000  45575 -25400  47775 -25400)'
            '(net /+24V)(type route))\n')
pruefe("dreipunkt-aufgespalten", neu == erwartet and n == 1,
       "n=%d\n%r" % (n, neu))

# 4: Fuenf Punkte ergeben vier Segmente; negative Koordinaten ueberleben.
fuenf = ('  (wire (path B.Cu 250  0 0  10 -10  20 -10  30 -20  40 -20)'
         '(net "GND")(type protect))\n')
neu, n = dsn_werkzeug.zweipunkt_zeilen(fuenf)
pruefe("fuenfpunkt-vier-segmente",
       n == 1 and neu.count("(wire ") == 4
       and "(path B.Cu 250  30 -20  40 -20)" in neu
       and neu.count("(type protect)") == 4,
       "n=%d\n%r" % (n, neu))

# 5 (ROT-NACHWEIS 2): Nachkommastellen. Die erste Splitter-Fassung
# matchte nur Ganzzahlen -- der verschmolzene 3V3-Zug des Motormoduls
# traegt x = 24542.5 und blieb stehen, der Haenger blieb. Exakt diese
# Zeile muss zerfallen, die Bruchkoordinate wortgleich ueberleben.
bruch = ('    (wire (path F.Cu 250  24542.5 -21300  28900 -21300  '
         '29250 -20950)(net 3V3)(type route))\n')
neu, n = dsn_werkzeug.zweipunkt_zeilen(bruch)
pruefe("bruchkoordinate-aufgespalten",
       n == 1 and neu.count("(wire ") == 2
       and "(path F.Cu 250  24542.5 -21300  28900 -21300)" in neu
       and "(path F.Cu 250  28900 -21300  29250 -20950)" in neu,
       "n=%d\n%r" % (n, neu))

if FEHLER:
    raise SystemExit("ROT: %s" % ", ".join(FEHLER))
print("alle Pruefungen gruen")

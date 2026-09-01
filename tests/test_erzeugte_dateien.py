"""Prueft, dass jede eingecheckte .kicad_sch zu ihrem Generator passt.

WARUM ES DIESEN TEST GIBT (2026-09-01, vor Aufgabe 6 gefunden).
Der Sockelschaltplan im Repo war veraltet: er trug an J3/J4 noch die
BEDRAHTETEN Steckerfootprints, obwohl tools/sch/modulsockel.py in
Commit fa46a9f auf SMD-PAARE umgestellt worden war (Aufgabe 5e). Der
Generator war richtig, sein Erzeugnis nicht -- er ist danach nie wieder
gelaufen. Der Motormodul-Schaltplan war zufaellig in Ordnung, weil er
nach fa46a9f noch einmal erzeugt wurde (a750b59).

Warum das teuer geworden waere: stack_spec.STECKER_POS rechnet die Lage
der Stecker aus den SMD-Hoefen (die Loetpads liegen SEITLICH neben den
Stiften, bei den bedrahteten Teilen mittig darunter). Aufgabe 6 haette
aus der veralteten Datei bedrahtete Stecker an SMD-Koordinaten gesetzt --
der Stapel haette mechanisch nicht gepasst, und zwar erst nach der
Fertigung sichtbar.

Warum kein bestehendes Gate das gefunden hat -- nachgemessen, nicht
vermutet: mit der veralteten Datei liefen ALLE SIEBEN Testreihen gruen
und kicad-cli ERC meldete unveraendert 0 Fehler / 1 Warnung. Die
Testreihen pruefen den GENERATOR gegen den Vertrag; die eingecheckte
Datei sehen sie nie an. ERC prueft Verbindungen, und die waren richtig --
nur das Bauteil darunter war ein anderes. Vierter Fall in diesem Projekt,
in dem ERC/DRC einen echten Fehler nicht sehen konnten.

Der Test vergleicht nicht Byte fuer Byte: gen.Schaltplan vergibt dem
Blatt bei jedem Lauf eine neue Kennung (sheet_uuid), die auch in jedem
sheet-Instanzpfad auftaucht. Beim Sockel waren das 72 der 80 geaenderten
Zeilen. Diese Kennungen werden vor dem Vergleich vereinheitlicht -- alles
andere zaehlt als Unterschied.
"""
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "sch"))

import motormodul
import sockelplatine

fails = []

# Jeder Generator, der eine Datei im Repo erzeugt. Neue Module gehoeren
# hierher -- sonst gilt fuer sie wieder, was oben schiefging.
GENERATOREN = (sockelplatine, motormodul)

_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                   r"[0-9a-f]{4}-[0-9a-f]{12}")


def ohne_uuids(text):
    return _UUID.sub("UUID", text)


for modul in GENERATOREN:
    name = modul.__name__

    # Die Angaben stehen als Modulkonstanten und werden hier NICHT
    # abgeschrieben: erzeugen() ist dieselbe Funktion, die auch der
    # __main__-Aufruf benutzt.
    if not os.path.exists(modul.ZIEL):
        fails.append("{}: {} fehlt".format(name, modul.ZIEL))
        continue

    with tempfile.TemporaryDirectory() as tmp:
        frisch = modul.erzeugen(os.path.join(tmp, "frisch.kicad_sch"))
        neu = ohne_uuids(open(frisch, encoding="utf-8").read())
    alt = ohne_uuids(open(modul.ZIEL, encoding="utf-8").read())

    if neu == alt:
        continue

    # Nicht bloss "ungleich" melden: die erste abweichende Zeile sagt,
    # WAS veraltet ist. Beim gefundenen Fall waren es genau die vier
    # Footprint- und Wert-Zeilen von J3/J4.
    a, b = alt.splitlines(), neu.splitlines()
    for i in range(max(len(a), len(b))):
        za = a[i] if i < len(a) else "<Datei zu Ende>"
        zb = b[i] if i < len(b) else "<Datei zu Ende>"
        if za != zb:
            fails.append(
                "{}: {} ist nicht der Stand des Generators -- "
                "erste Abweichung Zeile {}:\n"
                "      eingecheckt: {}\n"
                "      erzeugt:     {}\n"
                "      Beheben mit: python3 tools/sch/{}.py"
                .format(name, os.path.relpath(modul.ZIEL,
                                              os.path.join(HERE, "..")),
                        i + 1, za.strip(), zb.strip(), name))
            break

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("%d erzeugte Schaltplaene auf dem Stand ihrer Generatoren -- "
      "alle Pruefungen bestanden" % len(GENERATOREN))

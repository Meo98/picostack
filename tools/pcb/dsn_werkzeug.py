"""Textwerkzeuge fuer Specctra-DSN-Dateien. Bewusst OHNE KiCad.

Hier steht, was zwischen ExportSpecctraDSN und freerouting an der
DSN repariert werden muss. KiCad-frei, damit tests/ es ohne den
kipy-Starter pruefen kann (dieselbe Regel wie fuer die spec_*-Module).
"""
import re

# Ein Drahtzug der wiring-Sektion, eine Zeile je wire -- so schreibt
# KiCad 10 die Datei. Gruppen: Einrueckung, Lage, Breite, Koordinaten,
# Rest (net/type unveraendert uebernehmen). Koordinaten koennen
# NACHKOMMASTELLEN tragen (24542.5 fuer x = 24,5425 mm) -- die erste
# Fassung matchte nur Ganzzahlen, liess genau so einen verschmolzenen
# Zug stehen, und der Haenger blieb.
_WIRE = re.compile(
    r"^(\s*)\(wire \(path (\S+) (\d+)((?:\s+-?\d+(?:\.\d+)?)+)\)"
    r"(\(net [^)]*\)\(type \w+\)\))\s*$")


def zweipunkt_zeilen(text):
    """Spaltet Mehrpunkt-Drahtzuege in Zweipunkt-Segmente auf.

    KiCad verschmilzt beim DSN-Export aneinanderstossende Segmente der
    Vorverdrahtung MANCHMAL zu einem Pfad mit mehr als zwei Punkten --
    ob es dazu kommt, haengt von der Export-Reihenfolge ab, nicht vom
    Inhalt. freerouting 2.2.4 haengt sich an solchen Pfaden beim
    Import auf (Endlosschleife vor oder zwischen den Durchgaengen,
    Log bricht kommentarlos ab). Gefunden 2026-09-02 am Motormodul:
    vier scheinbar verschiedene Ausloeser (NRST-Zug, T-Abzweig,
    C10-Verschiebung, +24V-Absenkung) waren alle nur Aenderungen
    daran, WELCHE Zuege der Exporter gerade verschmolz -- die Platine
    trug genau einen Mehrpunkt-Pfad, und mit von Hand aufgespaltenem
    Pfad lief derselbe Stand in 27 s durch.

    Liefert (neuer_text, anzahl_aufgespaltener_zuege).
    """
    zeilen, n = [], 0
    for zeile in text.splitlines(keepends=True):
        m = _WIRE.match(zeile)
        if not m:
            zeilen.append(zeile)
            continue
        einzug, lage, breite, koord, rest = m.groups()
        # Koordinaten als TEXT weiterreichen, nicht als Zahl: eine
        # int()-Wandlung wuerde Nachkommastellen verwerfen und die
        # Bahn verschieben.
        werte = koord.split()
        punkte = list(zip(werte[::2], werte[1::2]))
        if len(punkte) <= 2:
            zeilen.append(zeile)
            continue
        n += 1
        for a, b in zip(punkte, punkte[1:]):
            zeilen.append("%s(wire (path %s %s  %s %s  %s %s)%s\n"
                          % (einzug, lage, breite, a[0], a[1],
                             b[0], b[1], rest))
    return "".join(zeilen), n


def datei_zweipunkt(pfad):
    """zweipunkt_zeilen() auf eine Datei; liefert die Anzahl."""
    text = open(pfad, encoding="utf-8").read()
    neu, n = zweipunkt_zeilen(text)
    if n:
        open(pfad, "w", encoding="utf-8").write(neu)
    return n

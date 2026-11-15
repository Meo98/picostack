"""Prueft, dass jede erzeugte Datei im Repo zu ihrem Generator passt.

Betroffen: die drei Dimmer-Schaltplaene und docs/vertrag.md -- alles,
was ein Werkzeug schreibt und trotzdem eingecheckt ist.

WARUM (2026-09-01): Der Sockelschaltplan im Repo war veraltet -- der
Generator war richtig, sein Erzeugnis nicht, und alle Testreihen
blieben gruen, weil sie den Generator pruefen, nie die Datei.

Der Vergleich ignoriert UUIDs (gen.Schaltplan vergibt je Lauf neue).
"""
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "sch"))

import dimmermodul   # noqa: E402
import vertrag_doku  # noqa: E402

fails = []
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def ohne_uuids(text):
    return _UUID.sub("UUID", text)


def vergleiche(name, ziel, erzeuge, behebe):
    if not os.path.exists(ziel):
        fails.append("%s: %s fehlt" % (name, ziel))
        return
    with tempfile.TemporaryDirectory() as tmp:
        frisch = erzeuge(os.path.join(tmp, os.path.basename(ziel)))
        neu = ohne_uuids(open(frisch, encoding="utf-8").read())
    alt = ohne_uuids(open(ziel, encoding="utf-8").read())
    if neu == alt:
        return
    a, b = alt.splitlines(), neu.splitlines()
    for i in range(max(len(a), len(b))):
        za = a[i] if i < len(a) else "<Datei zu Ende>"
        zb = b[i] if i < len(b) else "<Datei zu Ende>"
        if za != zb:
            fails.append("%s: nicht der Stand des Generators -- Zeile %d:\n"
                         "      eingecheckt: %s\n      erzeugt:     %s\n      Beheben: %s"
                         % (name, i + 1, za.strip()[:100], zb.strip()[:100], behebe))
            break


vergleiche("vertrag_doku", vertrag_doku.ZIEL, vertrag_doku.erzeugen,
           "python3 tools/vertrag_doku.py")
for kanaele, ziel in sorted(dimmermodul._ZIELE.items()):
    vergleiche("Dimmer%d" % kanaele, ziel,
               lambda p, k=kanaele: dimmermodul.erzeugen(p, kanaele=k),
               "python3 tools/sch/dimmermodul.py")

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("%d erzeugte Dateien auf dem Stand ihrer Generatoren -- alle Pruefungen bestanden"
      % (1 + len(dimmermodul._ZIELE)))

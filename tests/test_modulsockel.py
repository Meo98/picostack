"""Prueft den gemeinsamen Modulsockel-Block gegen den Vertrag.

Der Block sitzt auf jedem Modul. Ein Fehler darin ist ein Fehler in
jedem kuenftigen Modul -- deshalb wird er gegen tools/stack_spec.py
geprueft und nicht gegen sich selbst.

Stand 2026-08-31: SEL laeuft nicht mehr ueber den 2x20-Stapelstecker
(der ist seit der Umstellung auf den durchgehenden Stift EIN Bauteil
je Modul, kein Buchse/Stift-Paar mehr), sondern ueber den eigenen,
zweipoligen Kettenstecker (stack_spec.STECKER_KETTE). Deshalb ist "SEL"
absichtlich NICHT in stack_spec.RESERVIERT und darf auch nicht in
modulsockel.STECKER_NETZE auftauchen -- die Pruefung unten spiegelt
das.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ("tools", "tools/sch"):
    sys.path.insert(0, os.path.join(HERE, "..", d))
import stack_spec as S
import modulsockel

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


netze = modulsockel.NETZE_NACH_AUSSEN

# Der Block muss jede reservierte Leitung des Vertrags bedienen.
for rolle in S.RESERVIERT:
    check("Rolle %s im Block" % rolle, rolle in modulsockel.STECKER_NETZE, True)

# Und keine erfinden, die der Vertrag nicht kennt.
unbekannt = set(modulsockel.STECKER_NETZE) - set(S.RESERVIERT) - {
    "GND", "3V3", "VSYS", "VBUS", "3V3_EN"}
check("keine erfundenen Steckerleitungen", unbekannt, set())

# SEL laeuft ueber den eigenen Kettenstecker, nicht mehr ueber den
# 2x20 -- STECKER_NETZE (die Rollen DIESES Steckers) darf "SEL" daher
# nicht enthalten.
check("SEL nicht im 2x20-Stapelstecker", "SEL" in modulsockel.STECKER_NETZE, False)

# Die Endstufe bekommt genau die Anschluesse, die sie braucht.
for n in ("IN1", "IN2", "NSLEEP", "NFAULT", "IPROPI", "NOTAUS"):
    check("Endstufen-Anschluss %s" % n, n in netze, True)

# Zwei Kennwiderstaende, nicht einer -- 256 Modultypen.
check("zwei Kennwiderstaende", modulsockel.ANZAHL_KENNWIDERSTAENDE, 2)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

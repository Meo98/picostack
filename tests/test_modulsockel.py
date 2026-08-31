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

# ------------------------------------------------------------ Polaritaet
# Aufgabe 3 (Reset-Verpolung, siehe hardware/bauteile-1b.md, Nachtrag
# 2026-08-31): NRST am STM32C011 ist aktiv LOW. Das Gatter, das NRST
# treibt, muss deshalb INVERTIEREND sein (NAND) -- eine blosse
# Gatterzaehlung faengt eine Verpolung nicht: ein AND-Gatter an
# derselben Stelle waere immer noch "ein Gatter". Deshalb wird hier der
# Block tatsaechlich aufgebaut und der Verdrahtung bis zum treibenden
# Bauteil gefolgt, statt nur eine Ref-Bezeichnung abzufragen.
import gen as _gen  # noqa: E402


def _netz_pins(sch, netzname):
    """Alle (ref, pinnr, libid, value) an Pins, deren Stichleitung auf
    einem Label `netzname` endet (Pin-Ende oder Gegenstueck einer
    WIRES-Strecke, die dort ankommt)."""
    label_pts = {(x, y) for x, y, rot, txt in sch.LABELS if txt == netzname}
    pin_pts = set()
    for a, b in sch.WIRES:
        if a in label_pts:
            pin_pts.add(b)
        if b in label_pts:
            pin_pts.add(a)
    treffer = []
    for ref, libid, pos, rot, value, fp, _, _, einheit in sch.COMPS:
        einheiten = sch.UNITPINS.get(libid)
        nums = einheiten[einheit] if einheiten else sch.PINS[libid].keys()
        for num in nums:
            p = sch.PINS[libid][num]
            xy = _gen.xf(pos, (p[0], p[1]), rot)
            if xy in pin_pts:
                treffer.append((ref, num, libid, value))
    return treffer


_sch = _gen.Schaltplan("modulsockel_test", "Modulsockel (Test)", "")
modulsockel.einbauen(_sch, 0.0, 0.0, mit_flipflop=True)
_an_nrst = _netz_pins(_sch, "NRST")
check("zwei Pins am Netz NRST (MCU-Eingang + Gatter-Ausgang)", len(_an_nrst), 2)
_treiber = [t for t in _an_nrst if t[0] != "U100"]
check("genau ein Gatter treibt NRST", len(_treiber), 1)
if _treiber:
    _ref, _pin, _libid, _value = _treiber[0]
    check("das Gatter an NRST ist ein NAND (invertierend), kein AND",
          _libid, "74xGxx:74LVC1G00")

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

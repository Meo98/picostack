"""Netzlisten-Zusagen der Versorgungszelle v3 (tools/sch/versorgung.py).

Prueft am ERZEUGTEN Blatt (nicht am Quelltext), welche Pins an welchem
Netz haengen -- genau die Topologie, die stack_spec.VERSORGUNG
verspricht. ERC prueft nur, ob Verbindungen vorhanden sind; ob der
Drain an der richtigen Seite haengt, sieht er nicht (v1-Fehler).

Rot-Nachweis: dieselbe Drain-Probe gegen eine absichtlich verkehrt
gebaute Zelle (Source an PWR_IN) muss anschlagen.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "tools"))
sys.path.insert(0, os.path.join(HIER, "..", "tools", "sch"))

import gen           # noqa: E402
import stack_spec as S  # noqa: E402
import versorgung    # noqa: E402

fails = []


def check(label, got, want=True):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


def netz_pins(sch, netzname):
    """{(ref, pin)} aller Pins, deren Stichleitung auf Label/Power `netzname` endet."""
    pts = {(x, y) for x, y, _rot, txt in sch.LABELS if txt == netzname}
    pts |= {pos for _lib, pos, _rot, value in sch.POWERS if value == netzname}
    pin_pts = set()
    for a, b in sch.WIRES:
        if a in pts:
            pin_pts.add(b)
        if b in pts:
            pin_pts.add(a)
    aus = set()
    for ref, libid, pos, rot, _v, _fp, _r, _vv, _einheit in sch.COMPS:
        for num, p in sch.PINS[libid].items():
            if gen.xf(pos, (p[0], p[1]), rot) in pin_pts:
                aus.add((ref, num))
    return aus


sch = gen.Schaltplan("versorgung_test", "Versorgungszelle (Test)", "")
versorgung.bauen(sch, 0.0, 0.0)
N = {n: netz_pins(sch, n) for n in ("PWR_IN", "VIN", "GND", "+5V_LOKAL", "VSYS",
                                    "Q90_GATE", "VSW", "BOOT", "FB")}

# Verpolschutz: Drain an der Einspeisung, Source an der lokalen Schiene,
# Zener zwischen Gate und Source, Gate-Widerstand nach GND.
check("Q90-Drain an PWR_IN", ("Q90", "2") in N["PWR_IN"])
check("Q90-Source an VIN", ("Q90", "3") in N["VIN"])
check("Q90-Gate an Q90_GATE", ("Q90", "1") in N["Q90_GATE"])
check("D92 Kathode an VIN (Source)", ("D92", "1") in N["VIN"])
check("D92 Anode am Gate", ("D92", "2") in N["Q90_GATE"])
check("R91 Gate -> GND", ("R91", "1") in N["Q90_GATE"] and ("R91", "2") in N["GND"])
check("kein Widerstand an PWR_IN (v2-Fehlerklasse Gate-Teiler)",
      not any(r.startswith("R") for r, _ in N["PWR_IN"]))
# TVS und Stuetzung HINTER dem Schutz
check("D90 an VIN", ("D90", "1") in N["VIN"] and ("D90", "2") in N["GND"])
for c in ("C90", "C91", "C92"):
    check("%s an VIN/GND" % c, (c, "1") in N["VIN"] and (c, "2") in N["GND"])
# Buck
check("U90 VIN-Pin an VIN", ("U90", "7") in N["VIN"])
check("U90 EN offen (vertraegt max. 7 V)", ("U90", "5") not in N["VIN"])
check("U90 PH an VSW", ("U90", "8") in N["VSW"])
check("Boot-C zwischen BOOT und VSW", ("C93", "1") in N["BOOT"] and ("C93", "2") in N["VSW"])
check("Freilauf D93: Kathode VSW, Anode GND",
      ("D93", "1") in N["VSW"] and ("D93", "2") in N["GND"])
check("Spule VSW -> +5V_LOKAL", ("L90", "1") in N["VSW"] and ("L90", "2") in N["+5V_LOKAL"])
check("Teiler R92 +5V->FB, R93 FB->GND",
      ("R92", "1") in N["+5V_LOKAL"] and ("R92", "2") in N["FB"]
      and ("R93", "1") in N["FB"] and ("R93", "2") in N["GND"])
check("FB am VSENSE-Pin", ("U90", "4") in N["FB"])
check("Teiler ergibt die Vertragsspannung",
      round(1.221 * (1 + 10.0 / 3.3), 2) == S.VERSORGUNG["ausgang_v"])
# VSYS nur ueber die Diode
check("D91 Anode +5V_LOKAL, Kathode VSYS",
      ("D91", "2") in N["+5V_LOKAL"] and ("D91", "1") in N["VSYS"])
check("VSYS haengt an nichts anderem als D91", {r for r, _ in N["VSYS"]} == {"D91"})
check("Vertrag: vsys_diode", S.VERSORGUNG["vsys_diode"])
# Jedes Teil der Zelle ist platziert
refs = {c[0] for c in sch.COMPS if not c[0].startswith("#")}
check("alle TEILE platziert (fehlt: %s)" % sorted(set(versorgung.TEILE) - refs),
      set(versorgung.TEILE) <= refs)

# ROT-NACHWEIS: Zelle bauen, dann die Labels an Q90s Drain- und
# Source-Stummel vertauschen (die v1-Topologie) -- dieselbe Drain-Probe
# muss jetzt anschlagen.
rot = gen.Schaltplan("versorgung_rot", "verkehrt", "")
versorgung.bauen(rot, 0.0, 0.0)
drain, source = rot.pinpos("Q90", "2"), rot.pinpos("Q90", "3")


def nahe(p, q):
    return abs(p[0] - q[0]) < 6 and abs(p[1] - q[1]) < 6


neu = []
for x, y, r, t in rot.LABELS:
    if t == "PWR_IN" and nahe((x, y), drain):
        t = "VIN"
    elif t == "VIN" and nahe((x, y), source):
        t = "PWR_IN"
    neu.append((x, y, r, t))
rot.LABELS = neu
check("Rot-Nachweis: verkehrter Drain faellt durch",
      ("Q90", "2") in netz_pins(rot, "PWR_IN"), False)

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Versorgungszelle v3: alle Pruefungen bestanden")

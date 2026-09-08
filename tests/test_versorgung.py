"""Prueft die Versorgungszelle (tools/sch/versorgung.py) gegen den Vertrag
stack_spec.VERSORGUNG -- der Verpolschutz-Rot-Nachweis fuer PicoStack v2.

Der v1-Fehler, den diese Zelle behebt (motormodul.py, Q1/R11/R12,
`_endstufe_leistung()`): der P-Kanal-MOSFET saß mit dem SOURCE an der
rohen Einspeisung ("PWR24V") und mit dem DRAIN an der bereits
geschuetzten, lokalen Schiene ("+24V") -- genau umgekehrt zur richtigen
Schutzschaltung. Der Gate-Teiler (R11/R12) haengt dort ausserdem an
PWR24V, nicht an der lokalen Schiene. Bei verpolter Einspeisung bilden
die Body-Diode des FET UND die (bei Verpolung in Durchlassrichtung
liegende) TVS-Diode einen Kurzschluss-Pfad ("Crowbar") statt den
Rueckstrom zu sperren -- der Schutz schuetzt in diesem Fall gar nichts.

tools/stack_spec.py.VERSORGUNG haelt seit dieser Etappe die korrekte
Topologie als Vertrag fest:
    schutz_drain_an = "PWR_IN"        -- Drain an der Einspeisung
    gate_teiler_an  = "+24V_LOKAL"    -- Gate-Teiler an der lokalen Schiene
    vsys_diode      = True            -- Schottky-Diode vor VSYS
    eingang_v       = (6.0, 30.0)     -- zulaessiges Eingangsfenster

Diese Zelle (tools/sch/versorgung.py, Referenzen J90/Q90/R90/R91/D90/
U90/D91/C90/C91) ist die Implementierung genau dieser Zusagen. Die vier
Kern-Checks unten stammen woertlich aus dem Aufgabenbrief (Task 3);
`_netz_pins()` ist woertlich aus tests/test_modulsockel.py uebernommen
(dort dokumentiert, warum ein reiner Textvergleich im .kicad_sch die
falsche Pruefung waere -- er triffe Pinnamen im Symbol, nicht
tatsaechliche Verdrahtung).

ROT-NACHWEIS DER FEHLERKLASSE (unten, eigener Abschnitt): derselbe
Drain-Check laeuft zusaetzlich gegen die tatsaechlich generierte
motormodul.py-v1-Netzliste (Q1) -- und bestaetigt dort, wo dieser Test
läuft (2026-09-08, Stand vor der Umstellung von motormodul.py auf diese
neue Zelle), dass Q1s Drain (Pin 2) NICHT an der Einspeisung PWR24V
haengt, sondern an der lokalen Schiene +24V -- exakt der eingangs
beschriebene, umgekehrte Fehler. Das ist eine echte Assertion gegen
motormodul.bauen(), kein blosser Kommentar: faellt sie irgendwann um
(weil motormodul.py auf die neue Zelle umgestellt wurde, ohne diesen
Testabschnitt zu entfernen), macht sich das hier bemerkbar.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in ("tools", "tools/sch"):
    sys.path.insert(0, os.path.join(HERE, "..", _d))
import gen                 # noqa: E402
import motormodul           # noqa: E402  (nur fuer den Rot-Nachweis unten)
import versorgung           # noqa: E402

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


def _netz_pins(sch, gen_mod, netzname):
    """Aus tests/test_modulsockel.py uebernommen (s. Task-3-Brief), mit
    derselben Erweiterung wie tests/test_sockelplatine.py's eigene Kopie:
    alle (ref, pinnr, libid, value) an Pins, deren Stichleitung auf
    einem Label ODER Power-Symbol `netzname` endet -- GND laeuft in
    dieser Zelle ueber ein Power-Symbol (gen.PWR), nicht ueber ein
    Label; die reine Label-Fassung aus test_modulsockel.py (dort nur
    fuer das Label-Netz "NRST" gebraucht) faende GND-Treffer nicht."""
    label_pts = {(x, y) for x, y, rot, txt in sch.LABELS if txt == netzname}
    label_pts |= {pos for libid, pos, rot, value in sch.POWERS if value == netzname}
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
            xy = gen_mod.xf(pos, (p[0], p[1]), rot)
            if xy in pin_pts:
                treffer.append((ref, num, libid, value))
    return treffer


# ------------------------------------------------------ Zelle aufbauen
_sch = gen.Schaltplan("versorgung_test", "Versorgungszelle (Test)", "")
versorgung.bauen(_sch, 0.0, 0.0)

_NETZE = ("PWR_IN", "+24V", "GND", "+5V_LOKAL", "VSYS", "Q90_GATE")
pins = {name: {(r, n) for r, n, _, _ in _netz_pins(_sch, gen, name)}
        for name in _NETZE}

# --------------------------------------------- Die vier Kern-Checks (Brief)
check("Schutz-Drain an der Einspeisung", ("Q90", "2") in pins["PWR_IN"], True)
check("Schutz-Source an der lokalen Schiene", ("Q90", "3") in pins["+24V"], True)
check("Gate-Teiler an der lokalen Schiene", ("R90", "2") in pins["+24V"], True)
check("VSYS nur ueber die Diode", ("D91", "1") in pins["VSYS"]
      and not any(r == "U90" for r, _ in pins["VSYS"]), True)

# --------------------------------------------- Vollstaendigkeits-Checks
_ALLE_REFS = {c[0] for c in _sch.COMPS}
for _ref in ("J90", "Q90", "R90", "R91", "D90", "U90", "D91", "C90", "C91"):
    check("%s ist platziert" % _ref, _ref in _ALLE_REFS, True)

# R91 schliesst den Gate-Teiler nach GND, nicht Q90_GATE ins Leere.
check("R90 Gate-seitig an Q90_GATE", ("R90", "1") in pins["Q90_GATE"], True)
check("R91 an Q90_GATE", ("R91", "1") in pins["Q90_GATE"], True)
check("R91 nach GND", ("R91", "2") in pins["GND"], True)
check("Q90-Gate selbst an Q90_GATE", ("Q90", "1") in pins["Q90_GATE"], True)

# D90 (SMCJ30A) klemmt die lokale Schiene gegen Masse: Kathode an +24V.
check("D90 Kathode an +24V", ("D90", "1") in pins["+24V"], True)
check("D90 Anode an GND", ("D90", "2") in pins["GND"], True)

# U90 (K7805-1000R3): IN von der lokalen 24V-Schiene, OUT auf +5V_LOKAL.
check("U90 Eingang (IN) an +24V", ("U90", "1") in pins["+24V"], True)
check("U90 Ausgang (OUT) an +5V_LOKAL", ("U90", "3") in pins["+5V_LOKAL"], True)
check("U90 GND-Pin an GND", ("U90", "2") in pins["GND"], True)

# C90 (220u) stuetzt die lokale 24V-Schiene, C91 (22u) die 5V-Schiene.
check("C90 an +24V", ("C90", "1") in pins["+24V"], True)
check("C91 an +5V_LOKAL", ("C91", "1") in pins["+5V_LOKAL"], True)

# D91 (SS36C): Anode an +5V_LOKAL (Regler-Ausgang), Kathode an VSYS --
# damit die 5V-Schiene VSYS speisen kann, ein USB-gespeister Pico aber
# nicht rueckwaerts in den lokalen Regler einspeist.
check("D91 Anode an +5V_LOKAL", ("D91", "2") in pins["+5V_LOKAL"], True)

# J90 (Klemme) ist die einzige Quelle von PWR_IN in dieser Zelle.
check("J90 speist PWR_IN", ("J90", "1") in pins["PWR_IN"], True)

# Keine unverbundenen Pins -- dieselbe Selbstpruefung, die auch
# sch.schreiben() vor dem Schreiben laufen laesst.
check("keine unverbundenen Pins in der Zelle", _sch.selbstpruefung(), [])

# ------------------------------------------- Rot-Nachweis der Fehlerklasse
# Baut motormodul.py (die tatsaechliche v1-Endstufe, unveraendert von
# dieser Aufgabe) in ein eigenes, leeres Blatt und wendet DENSELBEN
# Drain-Check auf sein Q1/PWR24V-Netz an -- der laut Moduldoku
# (motormodul.py::_endstufe_leistung Docstring: "Q1: P-MOSFET, Source an
# PWR24V (vom Stapel), Drain an +24V (lokal, geschuetzt)") dort genau
# umgekehrt verdrahtet ist. Diese Assertion bestaetigt das gegen die
# ECHTE generierte Netzliste, nicht nur gegen den Kommentar.
_sch_v1 = gen.Schaltplan("motormodul_rot_nachweis", "Motormodul (Rot-Nachweis)", "")
motormodul.bauen(_sch_v1, 0.0, 0.0)
_pins_v1_pwr24v = {(r, n) for r, n, _, _ in _netz_pins(_sch_v1, gen, "PWR24V")}
_pins_v1_24v = {(r, n) for r, n, _, _ in _netz_pins(_sch_v1, gen, "+24V")}
check("ROT-NACHWEIS: Q1 (v1, motormodul.py) haengt mit dem Drain (Pin 2) "
      "NICHT an der Einspeisung PWR24V -- derselbe Drain-Check wie oben "
      "schlaegt hier fehl, das ist die Fehlerklasse, die diese Etappe "
      "behebt", ("Q1", "2") in _pins_v1_pwr24v, False)
check("ROT-NACHWEIS: Q1s Drain (Pin 2) haengt stattdessen an der "
      "lokalen Schiene +24V -- der umgekehrte, falsche Anschluss",
      ("Q1", "2") in _pins_v1_24v, True)
check("ROT-NACHWEIS: Q1s Source (Pin 3) haengt an der rohen Einspeisung "
      "PWR24V -- Source und Drain sind gegenueber der korrekten "
      "Schutzschaltung vertauscht", ("Q1", "3") in _pins_v1_pwr24v, True)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

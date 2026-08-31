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

Zwei Pruefungen unten (Polaritaet an NRST, ERC-Lauf) bauen den Block
tatsaechlich per `modulsockel.einbauen()` auf, was ueber `gen.py` ->
`symlib.py` ein installiertes `kicad-cli` braucht (fuer die Symbol-
bibliothekspfade UND fuer den ERC-Lauf selbst). Ist `kicad-cli` in der
Umgebung nicht auffindbar, werden genau diese zwei Pruefungen mit einer
deutlichen Meldung uebersprungen, statt entweder mit einem rohen
Tracebook abzubrechen oder still gruen zu melden -- die Dict/Konstanten-
Pruefungen oben brauchen kein kicad-cli und laufen immer.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

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

# Der Block muss jede reservierte Leitung des Vertrags bedienen --
# ausser SEL_OUT: das ist seit Befund 2 (Aufgabe-4-Fix-1, 2026-08-31)
# eine Vertragsrolle, aber KEIN Pin dieses 2x20-Stapelsteckers (SEL
# laeuft ueber den eigenen Kettenstecker, stack_spec.STECKER_KETTE).
# modulsockel._stapelstecker() behandelt die Rolle deshalb ausdruecklich
# als no_connect, nicht als STECKER_NETZE-Eintrag -- dieselbe Ausnahme
# wie unten fuer die alte Rolle "SEL", nur jetzt unter neuem Namen und
# mit echtem RESERVIERT-Status.
for rolle in S.RESERVIERT:
    if rolle == "SEL_OUT":
        continue
    check("Rolle %s im Block" % rolle, rolle in modulsockel.STECKER_NETZE, True)

# Und keine erfinden, die der Vertrag nicht kennt.
unbekannt = set(modulsockel.STECKER_NETZE) - set(S.RESERVIERT) - {
    "GND", "3V3", "VSYS", "VBUS", "3V3_EN"}
check("keine erfundenen Steckerleitungen", unbekannt, set())

# SEL laeuft ueber den eigenen Kettenstecker, nicht mehr ueber den
# 2x20 -- STECKER_NETZE (die Rollen DIESES Steckers) darf weder "SEL"
# noch "SEL_OUT" enthalten.
check("SEL nicht im 2x20-Stapelstecker", "SEL" in modulsockel.STECKER_NETZE, False)
check("SEL_OUT nicht im 2x20-Stapelstecker",
      "SEL_OUT" in modulsockel.STECKER_NETZE, False)

# Die Endstufe bekommt genau die Anschluesse, die sie braucht.
for n in ("IN1", "IN2", "NSLEEP", "NFAULT", "IPROPI", "NOTAUS"):
    check("Endstufen-Anschluss %s" % n, n in netze, True)

# Zwei Kennwiderstaende, nicht einer -- 256 Modultypen.
check("zwei Kennwiderstaende", modulsockel.ANZAHL_KENNWIDERSTAENDE, 2)


def _netz_pins(sch, gen_mod, netzname):
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
            xy = gen_mod.xf(pos, (p[0], p[1]), rot)
            if xy in pin_pts:
                treffer.append((ref, num, libid, value))
    return treffer


_KICAD_CLI = shutil.which("kicad-cli")
if _KICAD_CLI is None:
    print("UEBERSPRUNGEN: kicad-cli nicht in PATH gefunden -- die "
          "Polaritaets- und ERC-Pruefung (beide bauen den Block ueber "
          "gen.py/symlib.py tatsaechlich auf, das braucht kicad-cli fuer "
          "die Symbolbibliothekspfade) koennen in dieser Umgebung nicht "
          "laufen und werden ausgelassen. Alle anderen Pruefungen liefen.")
else:
    import gen as _gen

    # ------------------------------------------------------ Polaritaet
    # Aufgabe 3 (Reset-Verpolung, siehe hardware/bauteile-1b.md, Nachtrag
    # 2026-08-31): NRST am STM32C011 ist aktiv LOW. Das Gatter, das NRST
    # treibt, muss deshalb INVERTIEREND sein (NAND) -- eine blosse
    # Gatterzaehlung faengt eine Verpolung nicht: ein AND-Gatter an
    # derselben Stelle waere immer noch "ein Gatter". Deshalb wird hier
    # der Block tatsaechlich aufgebaut und der Verdrahtung bis zum
    # treibenden Bauteil gefolgt, statt nur eine Ref-Bezeichnung
    # abzufragen. Seit dem zweiten Nachtrag treibt eine EINHEIT eines
    # Dual-NAND-Bauteils (74xGxx:74LVC2G00) NRST, kein Einzel-Gatter mehr.
    _sch = _gen.Schaltplan("modulsockel_test", "Modulsockel (Test)", "")
    modulsockel.einbauen(_sch, 0.0, 0.0, mit_flipflop=True)
    _an_nrst = _netz_pins(_sch, _gen, "NRST")
    check("zwei Pins am Netz NRST (MCU-Eingang + Gatter-Ausgang)", len(_an_nrst), 2)
    _treiber = [t for t in _an_nrst if t[0] != "U100"]
    check("genau ein Gatter treibt NRST", len(_treiber), 1)
    if _treiber:
        _ref, _pin, _libid, _value = _treiber[0]
        check("das Gatter an NRST ist ein NAND (invertierend), kein AND",
              _libid, "74xGxx:74LVC2G00")

    # ------------------------------------------- Modulseite bleibt nc
    # Gegenprobe zu Befund 1/2 (Aufgabe-4-Fix-1, s. tests/
    # test_sockelplatine.py): die Sockelplatine reicht freie GPIO durch
    # und behandelt SEL_OUT als Vertragsrolle, die Modulseite
    # (modulsockel._stapelstecker(), hier ueber J100) bleibt dabei
    # ausdruecklich unveraendert -- beide Faelle no_connect.
    check("J100 Pin 4 (SEL_OUT) bleibt no_connect",
          _sch.pinpos("J100", "4") in _sch.NOCONN, True)
    for _p in ("11", "12", "20", "29", "31", "34"):
        check("J100 Pin %s (freier GPIO) bleibt no_connect" % _p,
              _sch.pinpos("J100", _p) in _sch.NOCONN, True)

    # ------------------------------------------------------------- ERC
    # Aufgabe 3, Nachtrag (Pruefer-Befund #2): drei echte Fehler (Phantom-
    # Stromsymbole, ungeloeste extends-Vererbung, Koordinaten neben dem
    # Raster) wurden beim ersten Durchlauf dieser Aufgabe nur durch einen
    # MANUELLEN `kicad-cli sch erc`-Lauf gefunden -- die reine
    # Pin-auf-Draht-Selbstpruefung (gen.Schaltplan.selbstpruefung) sieht
    # keinen davon. Aufgabe 4/5 erzeugen mit demselben Generator zwei
    # weitere Schaltplaene; bricht dort einer der drei Fehler wieder auf,
    # faellt es sonst niemandem auf. Deshalb hier der ERC-Lauf als
    # Testschritt: bauen, exportieren, pruefen, aufraeumen.
    ERWARTETE_ERC_WARNUNGEN = 6  # isolated_pin_label fuer IN1/IN2/NSLEEP/
    # NFAULT/IPROPI/NOTAUS -- absichtlich einseitige Uebergabenetze, die
    # erst Aufgabe 5 (Motormodul) auf der Gegenseite schliesst. Steigt
    # diese Zahl, ist das entweder ein neues, ebenso erklaerbares
    # Warnungsmuster ODER ein echter neuer Befund -- in jedem Fall soll
    # der Test es melden, nicht stillschweigend durchwinken.

    _tmp = tempfile.mkdtemp(prefix="modulsockel_erc_")
    try:
        _sch_erc = _gen.Schaltplan("modulsockel_erc_test",
                                    "Modulsockel (ERC-Test)", "")
        modulsockel.einbauen(_sch_erc, 0.0, 0.0, mit_flipflop=True)
        _sch_pfad = _sch_erc.schreiben(os.path.join(_tmp, "Modulsockel.kicad_sch"))
        _json_pfad = os.path.join(_tmp, "erc.json")
        _proc = subprocess.run(
            [_KICAD_CLI, "sch", "erc", "--format", "json",
             "--output", _json_pfad, _sch_pfad],
            capture_output=True, text=True)
        if not os.path.exists(_json_pfad):
            fails.append("kicad-cli sch erc lieferte keinen JSON-Report "
                          "(rc=%s): %s" % (_proc.returncode, _proc.stderr.strip()))
        else:
            with open(_json_pfad, encoding="utf-8") as f:
                _report = json.load(f)
            _errors = []
            _warnings = []
            for _sheet in _report.get("sheets", []):
                for _v in _sheet.get("violations", []):
                    if _v["severity"] == "error":
                        _errors.append(_v)
                    elif _v["severity"] == "warning":
                        _warnings.append(_v)
            check("ERC-Fehler auf dem erzeugten Blatt", len(_errors), 0)
            check("ERC-Warnungen auf dem erzeugten Blatt (isolierte "
                  "Uebergabenetze IN1/IN2/NSLEEP/NFAULT/IPROPI/NOTAUS)",
                  len(_warnings), ERWARTETE_ERC_WARNUNGEN)
            if _errors:
                for _e in _errors:
                    print("  ERC-Fehler:", _e.get("type"), "-", _e.get("description"))
    finally:
        shutil.rmtree(_tmp, ignore_errors=True)

# --- "frei" im Vertrag heisst wirklich frei ---------------------------
# Dreimal in dieser Etappe hiess ein Pin in PIN_ROLLE "frei", war es aber
# nicht: Pin 4 trieb lokal die Auswahlkette (Befund 2, Fix-1-Runde), Pin
# 30 ist der Reset des RP2040 und Pin 35 die analoge Referenz. Jedes Mal
# haette ein Modulautor, der sich auf den Vertrag verlaesst, etwas
# beschaedigt oder blockiert. Diese Pruefung schliesst die Klasse ab,
# statt den naechsten Einzelfall abzuwarten: die Menge der als "frei"
# gefuehrten Pins und die Menge der tatsaechlich durchgereichten GPIO
# muessen deckungsgleich sein. Wer kuenftig einen Pin fuer eine Sonder-
# aufgabe abzweigt, muss ihm hier eine Rolle geben -- oder der Test
# faellt.
_frei = {p for p, r in S.PIN_ROLLE.items() if r == "frei"}
check("als 'frei' gefuehrte Pins ohne durchgereichten GPIO",
      sorted(_frei - set(modulsockel.PIN_GPIO_NAME)), [])
check("durchgereichte GPIO, die der Vertrag nicht 'frei' nennt",
      sorted(set(modulsockel.PIN_GPIO_NAME) - _frei), [])

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

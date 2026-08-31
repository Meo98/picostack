"""Prueft die Sockelplatine gegen den Vertrag und gegen sich selbst.

Vorbild: tests/test_modulsockel.py. Die Sockelplatine ist -- anders als
der Modulsockel-Block -- KEIN wiederverwendeter Baustein, sondern ein
einzelnes, fertiges Blatt (hardware/kicad/sockel/Sockelplatine.kicad_sch).
Trotzdem gilt hier dieselbe Sorgfalt wie bei Aufgabe 3: die reine
Pin-auf-Draht-Selbstpruefung (gen.Schaltplan.selbstpruefung, laeuft
bereits beim Schreiben) sieht keine ERC-Fehler wie Phantom-Stromsymbole
oder zwei "Power output"-Pins auf demselben Netz -- deshalb der
zusaetzliche kicad-cli-ERC-Lauf unten.

Die mit Abstand gefaehrlichste Verwechslung in diesem Schaltplan waere
+5V an 3V3_OUT (Pico-Pin 36) statt an VSYS (Pico-Pin 39) zu legen --
das legt 5V direkt an den Ausgang des internen Schaltreglers des Pico
und zerstoert ihn. Die Pruefung unten haengt deshalb nicht an einem
Kommentar, sondern liest die tatsaechliche Verdrahtung aus dem
aufgebauten Schaltplan-Objekt aus (`_netz_pins`, woertlich aus
test_modulsockel.py uebernommen).

Stand 2026-08-31: Beide kicad-cli-gestuetzten Pruefblöcke (Polaritaet/
Netzzuordnung, ERC-Lauf) brauchen wie in test_modulsockel.py ein
installiertes kicad-cli (fuer Symbolbibliothekspfade UND den ERC-Lauf
selbst). Fehlt es, werden genau diese Pruefungen mit einer deutlichen
Meldung uebersprungen statt entweder mit einem rohen Traceback
abzubrechen oder still gruen zu melden.
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
import stack_spec as S           # noqa: E402
import modulsockel                # noqa: E402
import sockelplatine               # noqa: E402

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# ------------------------------------------------- reine Python-Pruefungen
# Brauchen kein kicad-cli: die Footprint-Angaben sind woertlich aus dem
# Aufgabenbrief uebernommen und duerfen nicht stillschweigend abweichen.
check("Footprint Pico", sockelplatine.FP_PICO,
      "Module:RaspberryPi_Pico_Common_THT")
check("Footprint 220uF radial", sockelplatine.FP_CP_RADIAL,
      "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm")
check("Footprint TVS SMC", sockelplatine.FP_TVS_SMC,
      "Diode_SMD:D_SMC_Handsoldering")
# Der Sockel verwendet den GLEICHEN Stapelstecker-Baustein wie jedes
# Modul (Aufgabe-4-Brief, Punkt 2) -- ueber Wiederverwendung von
# modulsockel._stapelstecker, nicht ueber eine eigene Nachbildung.
_quelltext = open(os.path.join(HERE, "..", "tools", "sch", "sockelplatine.py"),
                   encoding="utf-8").read()
check("modulsockel._stapelstecker wird fuer J2 wiederverwendet",
      "modulsockel._stapelstecker(sch, \"J2\"" in _quelltext, True)
# Punkt 1: kein Kleinst-MCU, kein Flipflop, keine Gatter, keine
# Kennwiderstaende -- der Sockel ist kein Modul.
for verboten in ("STM32C0", "74xGxx", "74LVC", "Kennwiderstand"):
    check("kein Modul-Baustein '%s' im Sockel" % verboten,
          verboten in _quelltext, False)


def _netz_pins(sch, gen_mod, netzname):
    """Alle (ref, pinnr) an Pins, deren Stichleitung auf einem Label
    ODER Power-Symbol `netzname` endet. Woertlich aus
    tests/test_modulsockel.py uebernommen."""
    ziel_pts = {(x, y) for x, y, rot, txt in sch.LABELS if txt == netzname}
    ziel_pts |= {pos for libid, pos, rot, value in sch.POWERS if value == netzname}
    pin_pts = set()
    for a, b in sch.WIRES:
        if a in ziel_pts:
            pin_pts.add(b)
        if b in ziel_pts:
            pin_pts.add(a)
    treffer = []
    for ref, libid, pos, rot, value, fp, _, _, einheit in sch.COMPS:
        einheiten = sch.UNITPINS.get(libid)
        nums = einheiten[einheit] if einheiten else sch.PINS[libid].keys()
        for num in nums:
            p = sch.PINS[libid][num]
            xy = gen_mod.xf(pos, (p[0], p[1]), rot)
            if xy in pin_pts:
                treffer.append((ref, num))
    return treffer


_KICAD_CLI = shutil.which("kicad-cli")
if _KICAD_CLI is None:
    print("UEBERSPRUNGEN: kicad-cli nicht in PATH gefunden -- die "
          "Netzzuordnungs- und ERC-Pruefung (beide bauen die Sockelplatine "
          "ueber gen.py/symlib.py tatsaechlich auf, das braucht kicad-cli "
          "fuer die Symbolbibliothekspfade UND fuer den ERC-Lauf selbst) "
          "koennen in dieser Umgebung nicht laufen und werden ausgelassen. "
          "Alle anderen Pruefungen liefen.")
else:
    import gen as _gen

    _sch = _gen.Schaltplan("sockelplatine_test", "Sockelplatine (Test)", "")
    sockelplatine.bauen(_sch, 0.0, 0.0)

    # -------------------------------------------------- Bauteilliste
    _refs = sorted(set(c[0] for c in _sch.COMPS if not c[0].startswith("#")))
    check("Referenzen entsprechen genau der Aufgabenbrief-Tabelle", _refs,
          ["C1", "C2", "C3", "D1", "J1", "J2", "J3", "J4", "R1", "R2", "U1", "U2"])

    # -------------------------------------------- Die gefaehrlichste Stelle
    # +5V (U2-Ausgang) MUSS an VSYS (Pico-Pin 39), NIEMALS an 3V3_OUT
    # (Pico-Pin 36) -- eine Verwechslung legt 5V an den Ausgang des
    # internen Schaltreglers des Pico und zerstoert ihn.
    _an_5v = set(_netz_pins(_sch, _gen, "+5V"))
    check("VSYS (U1 Pin 39) haengt an +5V", ("U1", "39") in _an_5v, True)
    check("U2-Ausgang (Pin 3) haengt an +5V", ("U2", "3") in _an_5v, True)
    check("3V3_OUT (U1 Pin 36) haengt NICHT an +5V", ("U1", "36") in _an_5v, False)

    _an_3v3 = set(_netz_pins(_sch, _gen, "3V3"))
    check("3V3_OUT (U1 Pin 36) haengt an 3V3", ("U1", "36") in _an_3v3, True)
    check("VSYS (U1 Pin 39) haengt NICHT an 3V3", ("U1", "39") in _an_3v3, False)
    # 3V3 ist die Quelle der Stapel-3V3-Schiene: muss auch am
    # Stapelstecker (J2 Pin 36, stack_spec.PIN_ROLLE[36] == "3V3") liegen,
    # sonst bekaeme kein Modul Versorgung.
    check("3V3 erreicht den Stapelstecker (J2 Pin 36)",
          ("J2", "36") in _an_3v3, True)

    # -------------------------------------------------- I2C-Abschluss
    # R1/R2 -- nur hier auf dem Sockel, nicht auf Modulen (stack_spec/
    # Aufgabenbrief). Muessen zwischen 3V3 und den jeweiligen I2C-Leitungen
    # haengen, nicht irgendwo sonst.
    check("R1 an 3V3", ("R1", "1") in _an_3v3, True)
    _an_sda = set(_netz_pins(_sch, _gen, "I2C_SDA"))
    check("R1 an I2C_SDA", ("R1", "2") in _an_sda, True)
    check("R2 an 3V3", ("R2", "1") in _an_3v3, True)
    _an_scl = set(_netz_pins(_sch, _gen, "I2C_SCL"))
    check("R2 an I2C_SCL", ("R2", "2") in _an_scl, True)

    # -------------------------------------------------- SEL erreicht J3
    # Punkt 3: der Sockel treibt SEL nur nach unten (nur die Stiftseite
    # des Kettensteckers) -- J3 Pin 1 muss auf demselben Netz haengen wie
    # der treibende Pico-GPIO. Seit Befund 2 (Aufgabe-4-Fix-1) ist das
    # Pin 4 (GP2, stack_spec.PIN_ROLLE[4] == "SEL_OUT"), nicht mehr GP8.
    _an_sel = set(_netz_pins(_sch, _gen, "SEL_OUT"))
    check("J3 Pin 1 (Kettenstecker, Stift) an SEL_OUT", ("J3", "1") in _an_sel, True)
    check("U1 Pin 4 (GP2) treibt SEL_OUT", ("U1", "4") in _an_sel, True)
    # J3 traegt NUR die Stiftseite -- die Referenzliste oben (exakt
    # J1..J4, kein zusaetzliches "J101"-aequivalentes Buchsenbauteil)
    # ist bereits die Pruefung dafuer, dass keine Kettenstecker-Buchse
    # (oben) mitgebaut wurde.

    # ------------------------ Befund 2: SEL-Treiber NICHT auf J2 -----
    # Der Kern von Befund 2 (Aufgabe-4-Fix-1): der SEL-Treiberpin darf
    # auf dem 2x20-Stapelstecker J2 UEBERHAUPT NICHT erscheinen -- sonst
    # triebe ein Modul, das denselben physischen Pin als freien GPIO
    # beansprucht, gegen den Sockel (zwei Ausgaenge auf einem Netz).
    # Baut man die alte, lokale GP8-Verdrahtung (ohne Sonderrolle) wieder
    # ein UND reicht Befund 1 gleichzeitig jeden freien GPIO durch, wird
    # genau das wieder wahr -- diese Pruefung faengt es ab.
    check("SEL-Treiberpin (U1 Pin 4) erscheint NICHT auf J2",
          any(ref == "J2" for ref, _ in _an_sel), False)

    # ------------------ Befund 1: freie GPIO erreichen J2 ------------
    # stack_spec.py nennt "freie GPIO" ausdruecklich als eine Leitungsart,
    # die im ganzen Stapel dasselbe Netz ist (STECKER_STAPEL-Kommentar) --
    # jeder als "frei" gefuehrte GPIO-Pin muss auf der Sockelplatine mit
    # dem gleichnummerierten J2-Pin verbunden sein, sonst kann ihn kein
    # Modul je benutzen. modulsockel.PIN_GPIO_NAME ist die massgebliche
    # Liste der tatsaechlich durchgereichten GPIO (RUN/ADC_VREF bewusst
    # ausgenommen, s. dortiger Kommentar). Setzt man frei_durchreichen
    # auf J2 wieder ab (Befund 1 erneut eingebaut), verschwindet der
    # J2-Anteil dieser Netze wieder -- diese Pruefung wird dann rot.
    for _pin, _name in sorted(modulsockel.PIN_GPIO_NAME.items()):
        _an_gpio = set(_netz_pins(_sch, _gen, _name))
        check("U1 Pin %d (%s) erreicht J2 Pin %d" % (_pin, _name, _pin),
              {("U1", str(_pin)), ("J2", str(_pin))} <= _an_gpio, True)

    # ------------------------------------------------------------- ERC
    ERWARTETE_ERC_FEHLER = 0
    # Genau EINE Warnung wird erwartet: lib_symbol_mismatch fuer
    # "R-78B5.0-2.0" -- eine unvermeidliche Folge von gen.Schaltplan.
    # lib_extends() (der flache, in sich geschlossene Nachbau eines
    # KiCad-"extends"-Symbols weicht absichtlich von der noch die
    # "(extends ...)"-Referenz tragenden Bibliotheksversion ab, siehe
    # tools/sch/gen.py, Docstring von lib_extends). Dieselbe Warnung
    # tritt nachweislich auch im bereits gefertigten led_dimmer-Projekt
    # auf (eigene Messung: `kicad-cli sch erc` gegen
    # led_dimmer_4ch.kicad_sch liefert dieselbe Meldung fuer dasselbe
    # Bauteil UND zusaetzlich fuer "RaspberryPi_Pico_W") -- kein neuer
    # Befund, sondern eine bekannte, harmlose Alterserscheinung
    # eingebetteter "extends"-Symbole.
    ERWARTETE_ERC_WARNUNGEN = 1

    _tmp = tempfile.mkdtemp(prefix="sockelplatine_erc_")
    try:
        _sch_erc = _gen.Schaltplan("sockelplatine_erc_test",
                                    "Sockelplatine (ERC-Test)", "")
        sockelplatine.bauen(_sch_erc, 0.0, 0.0)
        _sch_pfad = _sch_erc.schreiben(os.path.join(_tmp, "Sockelplatine.kicad_sch"))

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
            _errors, _warnings = [], []
            for _sheet in _report.get("sheets", []):
                for _v in _sheet.get("violations", []):
                    (_errors if _v["severity"] == "error" else _warnings).append(_v)
            check("ERC-Fehler auf der Sockelplatine", len(_errors), ERWARTETE_ERC_FEHLER)
            check("ERC-Warnungen auf der Sockelplatine (lib_symbol_mismatch "
                  "R-78B5.0-2.0, s.o.)", len(_warnings), ERWARTETE_ERC_WARNUNGEN)
            for _e in _errors:
                print("  ERC-Fehler:", _e.get("type"), "-", _e.get("description"))
            for _w in _warnings:
                if _w.get("type") != "lib_symbol_mismatch":
                    print("  unerwartete ERC-Warnung:", _w.get("type"), "-",
                          _w.get("description"))

        # --------------------------------------------------------- Netzliste
        # Aufgabenbrief, Schritt 3: der Export darf KEINE Annotationswarnung
        # melden.
        _net_pfad = os.path.join(_tmp, "sockel.net")
        _proc2 = subprocess.run(
            [_KICAD_CLI, "sch", "export", "netlist", "-o", _net_pfad, _sch_pfad],
            capture_output=True, text=True)
        check("Netzlisten-Export lief fehlerfrei durch", _proc2.returncode, 0)
        _ausgabe = (_proc2.stdout + _proc2.stderr).lower()
        check("keine Annotationswarnung beim Netzlisten-Export",
              "annotat" in _ausgabe, False)
    finally:
        shutil.rmtree(_tmp, ignore_errors=True)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

"""Prueft das Motormodul gegen den Vertrag, gegen das Altprojekt und gegen
sich selbst.

Vorbild: tests/test_sockelplatine.py und tests/test_modulsockel.py. Das
Motormodul ist -- wie die Sockelplatine -- ein einzelnes, fertiges Blatt
(hardware/kicad/motor/Motormodul.kicad_sch), baut aber zusaetzlich den
vollen Modulsockel-Block (modulsockel.einbauen(..., mit_flipflop=True))
mit ein, statt nur dessen Steckerteile wiederzuverwenden.

Die reine Pin-auf-Draht-Selbstpruefung (gen.Schaltplan.selbstpruefung,
laeuft bereits beim Schreiben ueber motormodul.bauen()/sch.schreiben())
sieht keine ERC-Fehler wie Phantom-Stromsymbole oder zwei zufaellig
deckungsgleiche Stichleitungen verschiedener Netze -- genau letzteres kam
beim ersten Entwurf dieser Datei tatsaechlich vor (zu enger Zeilenabstand
liess z.B. IN1 und U1_PH_IN2 zu einem Netz verschmelzen, s. Kommentare in
tools/sch/motormodul.py) und wurde ausschliesslich durch den
`kicad-cli sch erc`-Lauf gefunden, nicht durch die Selbstpruefung. Der
ERC-Testschritt unten ist deshalb keine Formalitaet.

Stand 2026-08-31: alle kicad-cli-gestuetzten Pruefbloecke brauchen ein
installiertes `kicad-cli`. Fehlt es, werden sie mit einer deutlichen
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
import stack_spec as S       # noqa: E402
import modulsockel            # noqa: E402
import motormodul              # noqa: E402

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# ------------------------------------------------------- reine Python-Pruefungen
# Brauchen kein kicad-cli.

# Der reparierte DRV8876-Footprint aus dem Altprojekt: Waermepad MIT
# Masken-/Pastenoeffnung, segmentiertes Pastenmuster, zwoelf Waermevias
# mit echtem Restring auf Pad 17 (Aufgabenbrief, Schritt 2).
_fp_mod = os.path.join(HERE, "..", "hardware", "kicad", "components",
                        "footprints", "DRV8876PWPR.pretty", "IC_DRV8876PWPR.kicad_mod")
check("DRV8876-Footprint aus dem Altprojekt uebernommen (Datei vorhanden)",
      os.path.isfile(_fp_mod), True)
if os.path.isfile(_fp_mod):
    _fp_txt = open(_fp_mod, encoding="utf-8").read()
    check("zwoelf Waerme-Durchkontaktierungen auf Pad 17 (reparierter Footprint)",
          _fp_txt.count("(pad 17 thru_hole circle"), 12)

check("Footprint DRV8876 zeigt auf die uebernommene Bibliothek",
      motormodul.FP_DRV8876, "DRV8876PWPR:IC_DRV8876PWPR")
check("Footprint TVS SMC (D1, wie sockelplatine.py)", motormodul.FP_TVS_SMC,
      "Diode_SMD:D_SMC_Handsoldering")
check("Footprint 220uF radial (C12, wie sockelplatine.py C3)",
      motormodul.FP_CP_RADIAL, "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm")

# Punkt 1 des Auftrags: R5 ist NEU gerechnet (2,538 A bei VVREF=3,3V,
# AIPROPI=1000uA/A), nicht der Altprojekt-Wert (2,2k -> 1,5A, zu klein
# fuer den 2-A-Motor -- exakt der dokumentierte Muttern-Board-Fehler).
_AIPROPI = 1000e-6   # A/A, TI DRV8876-Datenblatt SLVSDS7B, Abschnitt 6.5
_VVREF = 3.3
_R5_OHM = 1300.0
check("R5-Wert wie in motormodul.py verdrahtet", motormodul.R5_WERT, "1.3k")
_itrip = _VVREF / (_R5_OHM * _AIPROPI)
check("neu gerechnete Stromgrenze liegt ueber dem 2-A-Motor (mit Marge)",
      _itrip > 2.2, True)
check("neu gerechnete Stromgrenze bleibt unter der Hardware-Notbremse "
      "IOCP (3,5 A min, Datenblatt Abschnitt 6.5)", _itrip < 3.5, True)
# Der Altprojekt-Wert (2,2k) haette denselben Motor NICHT versorgt --
# Gegenprobe, dass diese Aufgabe nicht einfach denselben Fehler wiederholt.
_itrip_alt = _VVREF / (2200.0 * _AIPROPI)
check("Altprojekt-Wert (2,2k) haette 2-A-Motor unterversorgt (zur Gegenprobe)",
      _itrip_alt < 2.0, True)
check("R10 bleibt der unveraenderte Altprojekt-Wert (nur DNP, nicht neu "
      "gerechnet -- die Aufgabe verlangt das nur fuer R5)",
      motormodul.R10_WERT, "4.7k")

_KICAD_CLI = shutil.which("kicad-cli")
if _KICAD_CLI is None:
    print("UEBERSPRUNGEN: kicad-cli nicht in PATH gefunden -- die "
          "Netzzuordnungs- und ERC-Pruefung (beide bauen das Motormodul "
          "ueber gen.py/symlib.py tatsaechlich auf, das braucht kicad-cli "
          "fuer die Symbolbibliothekspfade UND fuer den ERC-Lauf selbst) "
          "koennen in dieser Umgebung nicht laufen und werden ausgelassen. "
          "Alle anderen Pruefungen liefen.")
else:
    import gen as _gen

    _sch = _gen.Schaltplan("motormodul_test", "Motormodul (Test)", "")
    motormodul.bauen(_sch, 0.0, 0.0)

    def _netz_pins(sch, gen_mod, netzname):
        """Alle (ref, pinnr) an Pins, deren Stichleitung auf einem Label
        ODER Power-Symbol `netzname` endet. Woertlich aus
        tests/test_modulsockel.py / tests/test_sockelplatine.py
        uebernommen."""
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

    # -------------------------------------------------- Bauteilliste
    _refs = sorted(set(c[0] for c in _sch.COMPS if not c[0].startswith("#")))
    _erwartet_endstufe = {"D1", "D2", "D3", "D4", "C9", "C10", "C11", "C12",
                           "C13", "J2", "J3", "J5", "Q1", "R5", "R6", "R7",
                           "R8", "R9", "R10", "R11", "R12", "R13", "R14",
                           "R15", "U1", "U2"}
    _erwartet_sockel = {"U100", "U101", "U102", "U103", "R100", "R101",
                         "R102", "R104", "R105", "C100", "C101",
                         "J100", "J101", "J102", "J103", "J104"}
    check("Referenzen = Modulsockel-Block + Endstufe (nichts Ueberzaehliges)",
          set(_refs), _erwartet_endstufe | _erwartet_sockel)

    # -------------------------------- Steuerleitungen haengen am MCU ---
    # Der eigentliche Auftrag: IN1/IN2/NSLEEP haengen am Modul-MCU (U100),
    # NICHT direkt am Stapelstecker (J100) -- die Vorwiderstaende R7/R8/R9
    # trennen den MCU-seitigen Knoten vom DRV8876-seitigen.
    for rolle, u100_pin, r_ref in (("IN1", "9", "R7"), ("IN2", "10", "R8"),
                                     ("NSLEEP", "11", "R9")):
        _treffer = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN[rolle]))
        check("U100 Pin %s (%s) haengt am MCU" % (u100_pin, rolle),
              ("U100", u100_pin) in _treffer, True)
        check("%s (Vorwiderstand) haengt auf demselben Netz wie %s"
              % (r_ref, rolle), (r_ref, "1") in _treffer, True)
        check("%s erreicht NICHT direkt den Stapelstecker J100"
              % rolle, any(ref == "J100" for ref, _ in _treffer), False)
        check("U1 (DRV8876) haengt NICHT direkt an der MCU-Seite von %s "
              "(der Vorwiderstand muss dazwischen sitzen)" % rolle,
              any(ref == "U1" for ref, _ in _treffer), False)

    # NFAULT und IPROPI haben laut Aufgabenbrief KEINEN Vorwiderstand --
    # DRV8876, Pullup/Filter und MCU teilen sich direkt ein Netz.
    _an_nfault = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["NFAULT"]))
    check("NFAULT erreicht U100 (MCU-Eingang)", ("U100", "12") in _an_nfault, True)
    check("NFAULT erreicht U1 Pin 4 (DRV8876 ~NFAULT)", ("U1", "4") in _an_nfault, True)
    check("NFAULT traegt den Pullup R13", ("R13", "2") in _an_nfault, True)

    _an_ipropi = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["IPROPI"]))
    # PA6 traegt laut STM32C011-Datenblatt (DS13866, Tabelle 12 "Pin
    # assignment and description") die Zusatzfunktion ADC_IN6 -- per
    # WebSearch-Auszug aus der Tabelle bestaetigt (zwei unabhaengige
    # Fundstellen), keine selbst geoeffnete PDF-Seite (st.com blockiert
    # den direkten Download mit HTTP/2 INTERNAL_ERROR, dieselbe
    # Einschraenkung wie hardware/bauteile.md, Beleg 1, dort dokumentiert).
    check("IPROPI erreicht U100 Pin 13 (PA6 -- ADC_IN6, DS13866 Tabelle 12)",
          ("U100", "13") in _an_ipropi, True)
    check("IPROPI erreicht U1 Pin 6 (DRV8876 IPROPI-Ausgang)",
          ("U1", "6") in _an_ipropi, True)
    check("IPROPI traegt R5 (bestueckt, s.o.)", ("R5", "1") in _an_ipropi, True)
    check("IPROPI traegt R10 (DNP)", ("R10", "1") in _an_ipropi, True)

    # -------------------------------------------------------- Punkt 3: C12
    # Polarisierter Kondensator: Pin 1 ("+" im Device:C_Polarized-Symbol)
    # MUSS an +24V liegen, NIE an GND (der Muttern-Print-Fehler).
    _an_24v = set(_netz_pins(_sch, _gen, "+24V"))
    check("C12 Pin 1 (\"+\") haengt an +24V", ("C12", "1") in _an_24v, True)
    _an_gnd = set(_netz_pins(_sch, _gen, "GND"))
    check("C12 Pin 1 (\"+\") haengt NICHT an GND", ("C12", "1") in _an_gnd, False)
    check("C12 Pin 2 haengt an GND", ("C12", "2") in _an_gnd, True)
    check("R5 ist bestueckt (nicht in sch.DNP)", "R5" in _sch.DNP, False)
    check("R10 ist DNP (Aufgabenbrief: 'R10 unbestueckt')", "R10" in _sch.DNP, True)

    # ----------------------------------------------------- Punkt 4: NOTAUS
    # Die Sammelleitung erreicht den Stapelstecker (global) UND die
    # Hardware-Verriegelung (D2, wirkt auf U1_NSLEEP unabhaengig vom MCU)
    # UND die beiden lokalen Notaus-Eingaenge (D3/D4, koppeln J3 auf die
    # globale Leitung, OHNE die zwei Kanaele lokal kurzzuschliessen).
    _an_notaus = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["NOTAUS"]))
    check("NOTAUS erreicht den Stapelstecker (J100 Pin 9)",
          ("J100", "9") in _an_notaus, True)
    check("NOTAUS erreicht D2 (Verriegelung Richtung NSLEEP)",
          ("D2", "1") in _an_notaus, True)
    check("NOTAUS erreicht D3 (lokaler Notaus-Eingang 1)",
          ("D3", "2") in _an_notaus, True)
    check("NOTAUS erreicht D4 (lokaler Notaus-Eingang 2)",
          ("D4", "2") in _an_notaus, True)
    check("NOTAUS traegt den Pullup R15", ("R15", "2") in _an_notaus, True)
    check("NOTAUS erreicht NICHT direkt U1 (der Weg fuehrt ueber D2 + "
          "U1_NSLEEP, nicht direkt auf den DRV8876)",
          any(ref == "U1" for ref, _ in _an_notaus), False)

    # Die zwei lokalen Kanaele bleiben elektrisch GETRENNT (nur ueber je
    # eine Diode an NOTAUS gekoppelt) -- sonst waere die
    # Software-Diagnose "welcher Kanal loeste aus" unmoeglich.
    _an_notaus1 = set(_netz_pins(_sch, _gen, "NOTAUS_1"))
    _an_notaus2 = set(_netz_pins(_sch, _gen, "NOTAUS_2"))
    check("NOTAUS_1 und NOTAUS_2 sind verschiedene Netze (nicht lokal "
          "kurzgeschlossen)", _an_notaus1.isdisjoint(_an_notaus2), True)
    check("U100 Pin 3 (PC15) liest NOTAUS_1", ("U100", "3") in _an_notaus1, True)
    check("U100 Pin 14 (PA7) liest NOTAUS_2", ("U100", "14") in _an_notaus2, True)
    check("J3 Pin 1 traegt NOTAUS_1", ("J3", "1") in _an_notaus1, True)
    check("J3 Pin 3 traegt NOTAUS_2", ("J3", "3") in _an_notaus2, True)

    # Die Verriegelung sitzt auf der DRV8876-Seite von NSLEEP (nach R9),
    # NICHT auf der MCU-Seite -- sonst wirkt sie nicht, wenn der MCU
    # haengt UND sein Pin aktiv treibt (s. Moduldoku in motormodul.py).
    _an_u1_nsleep = set(_netz_pins(_sch, _gen, "U1_NSLEEP"))
    check("R14 (Verriegelungs-Vorwiderstand) haengt auf der DRV8876-Seite "
          "von NSLEEP (nach R9), nicht auf der MCU-Seite",
          ("R14", "1") in _an_u1_nsleep, True)
    check("U1 Pin 3 (DRV8876 NSLEEP) haengt auf demselben Netz wie R14",
          ("U1", "3") in _an_u1_nsleep, True)
    _an_mcu_nsleep = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["NSLEEP"]))
    check("die Verriegelung (R14) haengt NICHT auf der MCU-Seite von NSLEEP",
          ("R14", "1") in _an_mcu_nsleep, False)

    # ------------------------------------------------------------- ERC
    ERWARTETE_ERC_FEHLER = 0
    ERWARTETE_ERC_WARNUNGEN = 0

    _tmp = tempfile.mkdtemp(prefix="motormodul_erc_")
    try:
        # sym-lib-table/fp-lib-table zeigen relativ auf "${KIPRJMOD}/../
        # components/..." (dieselbe Struktur wie hardware/kicad/motor/,
        # s. dort) -- der Testbau braucht deshalb dieselbe Verzeichnis-
        # SCHACHTELUNG, nicht nur die beiden Tabellen lose im Temp-Ordner.
        # Eigene Messung: ohne die Nachbar-components/ loeste kicad-cli
        # den Pfad zwar auf ("${KIPRJMOD}" korrekt ersetzt), fand die
        # Zieldatei aber nicht -- zwei ERC-Warnungen blieben stehen.
        _motor_dir = os.path.join(_tmp, "motor")
        os.makedirs(_motor_dir)
        os.symlink(os.path.abspath(os.path.join(HERE, "..", "hardware", "kicad",
                                                  "components")),
                   os.path.join(_tmp, "components"))

        _sch_erc = _gen.Schaltplan("motormodul_erc_test", "Motormodul (ERC-Test)", "")
        motormodul.bauen(_sch_erc, 0.0, 0.0)
        _sch_pfad = _sch_erc.schreiben(os.path.join(_motor_dir, "Motormodul.kicad_sch"))
        for _fname in ("sym-lib-table", "fp-lib-table", "Motormodul.kicad_pro"):
            shutil.copy(os.path.join(HERE, "..", "hardware", "kicad", "motor", _fname),
                        os.path.join(_motor_dir, _fname))

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
            check("ERC-Fehler auf dem Motormodul", len(_errors), ERWARTETE_ERC_FEHLER)
            check("ERC-Warnungen auf dem Motormodul", len(_warnings), ERWARTETE_ERC_WARNUNGEN)
            for _e in _errors:
                print("  ERC-Fehler:", _e.get("type"), "-", _e.get("description"))
            for _w in _warnings:
                print("  ERC-Warnung:", _w.get("type"), "-", _w.get("description"))

        # --------------------------------------------------------- Netzliste
        _net_pfad = os.path.join(_tmp, "motor.net")
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

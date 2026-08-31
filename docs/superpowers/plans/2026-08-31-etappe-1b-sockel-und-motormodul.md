# PicoStack Etappe 1b — Sockelplatine und Motormodul

> **Für agentische Bearbeiter:** ERFORDERLICHE SUB-SKILL:
> `superpowers:subagent-driven-development` (empfohlen) oder
> `superpowers:executing-plans`. Die Schritte nutzen Checkbox-Syntax
> (`- [ ]`) zur Nachverfolgung.

**Ziel:** Zwei bestellbare Leiterplatten — die Sockelplatine mit dem Pico
und ein Motormodul — die zusammen den ersten lauffähigen Stapel bilden.

**Architektur:** Schaltpläne und Layouts entstehen **skriptgeneriert**, nicht
gezeichnet. Das Muster stammt aus dem LED-Dimmer
(`~/Dokumente/Espace_des_Inventions/led_dimmer/hardware/generator/`): eine
Bauteil- und Netzbeschreibung als Python-Datenstruktur, daraus erzeugt ein
Generator die `.kicad_sch`, KiCad exportiert die Netzliste, und daraus baut
die Werkzeugkette aus dem Muttern-Redesign die Platine samt Flächen und
Verdrahtung. Der Modulsockel — MCU, beide Stapelstecker, Flipflop, Gatter,
Kennwiderstände — ist **ein** Baustein, den beide Platinen und jedes künftige
Modul verwenden.

**Tech-Stack:** Python 3 (Generatoren, ohne Fremdpakete), pcbnew-API aus
KiCad 10.0.5, `kicad-cli` für ERC/DRC/Export, freerouting 2.2.4 headless,
OpenSCAD für das Gehäuse.

**Spec:** `docs/superpowers/specs/2026-08-28-picostack-design.md`

## Globale Rahmenbedingungen

Wörtlich aus Spec und Vertrag (`tools/stack_spec.py`); sie gelten für **jede**
Aufgabe:

- Umriss **64,0 × 60,0 mm**, Ecken 3 mm gerundet, 2 Lagen
- Vier M3-Bohrungen (3,2 mm) bei (4|4), (4|56), (60|4), (60|56)
- **15 mm** zwischen den Platinen; Sockel sitzt **zuoberst**
- Signalstecker **2×20**, Pico-Pinbild, **zwei getrennte Steckerteile**
  je Modul (Buchse oben, Stift unten, in der Platine verbunden) — kein
  Stapelstecker, sonst lässt sich die Kette nicht auftrennen
- Reservierte Leitungen und ihre Pins stehen in `tools/stack_spec.py`
  (`PIN_ROLLE`); sie sind der Vertrag und **nicht** zu ändern
- I²C-Abschlusswiderstände **nur auf dem Sockel**
- Bahnbreiten: Signal **0,25 mm**, Leistung **1,00 mm**
- Sicherer Zustand nach **500 ms** ohne gültigen Befehl
- **Der Sockel muss die Kette leertakten**, bevor er `FLASH_MODE` das erste
  Mal auf 1 setzt — reale Flipflops starten undefiniert
- Die Flash-UART-Leitungen kurz und störungsarm führen: der Bootlader
  **misst** das Synchronisationsbyte, Störimpulse lassen die Erkennung
  fehlschlagen
- LCSC-Nummern nur von einer Produktseite; sonst Feld leer und genaue
  Beschreibung. Datenblattangaben mit Dokument und Abschnitt. **Bindend.**
- Arbeitsverzeichnis für alle Befehle: `~/Dokumente/picostack`

**KiCad-Python.** Das System-`python3` findet `pcbnew` nicht. Jedes Skript,
das `pcbnew` braucht, läuft über den Starter:
`~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy <skript.py>`

## Dateien

| Datei | Verantwortung |
|---|---|
| `tools/pcb/kicadlibs.py` | Bibliotheks-Spitznamen → Pfade, aus dem kicad-cli-Wrapper abgeleitet |
| `tools/pcb/geometry.py` | Platzierungsprüfung ohne KiCad |
| `tools/pcb/build.py` | Platine aus der Netzliste aufbauen, Flächen, Umriss |
| `tools/pcb/netclasses.py` | Netzklassen ins Projekt schreiben |
| `tools/pcb/autoroute.py` | DSN → freerouting → SES zurücklesen |
| `tools/sch/symlib.py` | Symbolblöcke und Pin-Geometrie aus den Bibliotheken |
| `tools/sch/gen.py` | Bauteile, Drähte, Labels, Selbstprüfung, Datei schreiben |
| `tools/sch/modulsockel.py` | Der gemeinsame Block: MCU, Stecker, Flipflop, Gatter, Kennwiderstände |
| `tools/sch/sockelplatine.py` | Beschreibung der Sockelplatine |
| `tools/sch/motormodul.py` | Beschreibung des Motormoduls |
| `hardware/bauteile-1b.md` | Bauteilwahl für diese Etappe, mit Belegen |
| `hardware/kicad/` | Die erzeugten Projekte beider Platinen |

---

### Aufgabe 1: Werkzeugkette übernehmen

Beides existiert bereits und ist erprobt — es fehlt nur hier. Aus
`~/Dokumente/Espace_des_Inventions/PecheAuxCanards/tools/pcb/` kommen die
Platinenwerkzeuge, aus
`~/Dokumente/Espace_des_Inventions/led_dimmer/hardware/generator/` die
Schaltplanwerkzeuge.

**Dateien:**
- Anlegen: `tools/pcb/{kicadlibs,geometry,build,netclasses,autoroute}.py`
- Anlegen: `tools/sch/{symlib,netlist}.py`
- Anlegen: `tests/test_werkzeuge.py`

**Schnittstellen:**
- Liefert: `kicadlibs.footprint_libs(projektpfad)`, `symlib.extract(datei, name)`,
  `symlib.pins(block)`, `netlist.load(pfad)`, `build.mm(v)`,
  `autoroute.ses_lesen(pfad)`

- [ ] **Schritt 1: Dateien kopieren**

```bash
mkdir -p tools/pcb tools/sch
P=~/Dokumente/Espace_des_Inventions/PecheAuxCanards/tools/pcb
cp "$P"/{kicadlibs,geometry,build,netclasses,autoroute}.py tools/pcb/
L=~/Dokumente/Espace_des_Inventions/led_dimmer/hardware/generator
cp "$L"/{symlib,netlist}.py tools/sch/
```

- [ ] **Schritt 2: Den fest eingetragenen Bibliothekspfad ersetzen**

`tools/sch/symlib.py` beginnt mit einem fest eingetragenen Nix-Store-Pfad:

```python
LIBDIR = "/nix/store/9iivbgi20l08m6kz6vs229pj706kfmr4-kicad-symbols-5a6700bbb3/share/kicad/symbols/"
```

Der bricht nach jedem `nixos-rebuild`. `tools/pcb/kicadlibs.py` löst dasselbe
Problem für Footprints schon richtig — es liest die Verzeichnisse aus dem
`kicad-cli`-Wrapper. Ersetze den festen Pfad durch:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "pcb"))
import kicadlibs


def _libdir():
    """Symbolverzeichnis aus der installierten KiCad-Version ableiten.

    Ein fest eingetragener Store-Pfad ueberlebt kein nixos-rebuild. Die
    Variable heisst KICAD<major>_SYMBOL_DIR und steht im kicad-cli-Wrapper.
    """
    d = kicadlibs.kicad_dirs()
    for k, v in d.items():
        if k.endswith("_SYMBOL_DIR"):
            return v.rstrip("/") + "/"
    raise SystemExit("kein KICAD*_SYMBOL_DIR im kicad-cli-Wrapper gefunden")


LIBDIR = _libdir()
```

- [ ] **Schritt 3: Den Test schreiben**

`tests/test_werkzeuge.py`:

```python
"""Prueft, dass die uebernommenen Werkzeuge hier laufen.

Sie stammen aus zwei anderen Projekten. Der haeufigste Fehler beim
Uebernehmen ist ein Pfad, der dort stimmte und hier nicht -- deshalb
prueft dieser Test genau das, nicht die Logik der Werkzeuge selbst.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "pcb"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "sch"))

import kicadlibs, symlib

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- Footprint-Bibliotheken werden gefunden ---
libs = kicadlibs.footprint_libs(os.path.join(HERE, "..", "hardware", "kicad"))
check("viele Footprint-Bibliotheken", len(libs) > 50, True)
for n in ("Resistor_SMD", "Package_TO_SOT_SMD", "Connector_PinHeader_2.54mm",
          "Connector_PinSocket_2.54mm", "Module"):
    check("Bibliothek %s bekannt" % n, n in libs, True)

# --- Symbolverzeichnis wird abgeleitet, nicht geraten ---
check("Symbolverzeichnis existiert", os.path.isdir(symlib.LIBDIR), True)
check("kein eingefrorener Store-Pfad im Quelltext",
      "9iivbgi20l08m6kz6vs229pj706kfmr4" in open(
          os.path.join(HERE, "..", "tools", "sch", "symlib.py")).read(), False)

# --- Ein Symbol laesst sich ziehen und seine Pins lesen ---
blk = symlib.extract("Device.kicad_sym", "R")
check("Symbolblock geholt", blk.startswith('(symbol "R"'), True)
p = symlib.pins(blk)
check("Widerstand hat zwei Pins", sorted(p), ["1", "2"])

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")
```

- [ ] **Schritt 4: Test laufen lassen**

Ausführen: `python3 tests/test_werkzeuge.py`
Erwartet zuerst einen Fehlschlag beim eingefrorenen Store-Pfad, falls
Schritt 2 vergessen wurde; danach `alle Pruefungen bestanden`.

- [ ] **Schritt 5: Committen**

```bash
git add tools/pcb tools/sch tests/test_werkzeuge.py
git commit -m "Werkzeugketten aus Muttern-Redesign und LED-Dimmer uebernommen"
```

---

### Aufgabe 2: Bauteilwahl für Etappe 1b belegen

Wie in Etappe 1a: Entscheidungen mit Beleg, keine erfundenen Nummern.

**Dateien:**
- Anlegen: `hardware/bauteile-1b.md`

- [ ] **Schritt 1: Die offenen Bauteile bestimmen**

Zu klären, jeweils mit Bauform, JLCPCB-Bestückbarkeit und LCSC-Nummer **nur
bei Sichtung auf einer Produktseite**:

| Zweck | Anforderung |
|---|---|
| D-Flipflop je Modul | Einzel-D-FF, SC-70/SOT-353, **asynchroner Löscheingang erwünscht** (spart dem Sockel das Leertakten) |
| Gatter | 2× NOT und 3× AND aus der 74LVC1G/2G-Reihe, Winzgehäuse |
| Stapelstecker | 2×20 Buchsenleiste (oben) und 2×20 Stiftleiste (unten), 2,54 mm; **Bauhöhe so, dass 15 mm Plattenabstand herauskommen** |
| Leistungsstecker | 24 V durch den Stapel, mehrere Kontakte parallel; Strombelastbarkeit belegen |
| 5-V-Regler | `K7805-2000R3` SIP-3, LCSC **C2931187** — beim LED-Dimmer bereits bestellt und geprüft |
| Klemmen | `DB128L-5.08-2P` (LCSC **C395868**, geprüft) und die 3-polige Variante |

- [ ] **Schritt 2: Steckerhöhe gegen den Plattenabstand rechnen**

Der Vertrag sichert 15 mm zwischen den Platinen zu. Rechne nach, welche
Bauhöhe von Buchsen- und Stiftleiste zusammen mit 1,6 mm Platinendicke
diesen Abstand ergibt, und halte die Rechnung fest. **Passt keine
Standardleiste, ist das ein Befund** — dann muss entweder der Abstand im
Vertrag geändert werden (und damit `tools/stack_spec.py` samt Gehäuse) oder
eine Sonderbauform her. Nicht stillschweigend auf einen anderen Abstand
ausweichen.

- [ ] **Schritt 3: `hardware/bauteile-1b.md` schreiben**

Tabelle wie in `hardware/bauteile.md`: Zweck, Typ, Bauform, LCSC, **geprüft
(ja/nein)**, Quelle. Dazu die Rechnung aus Schritt 2 und, falls der
Löscheingang am Flipflop verfügbar ist, ein Absatz dazu, dass das
Leertakten damit entfällt.

- [ ] **Schritt 4: Committen**

```bash
git add hardware/bauteile-1b.md
git commit -m "Bauteilwahl fuer Etappe 1b belegt"
```

---

### Aufgabe 3: Der Modulsockel als gemeinsamer Block

Das Herzstück dieser Etappe. Was hier entsteht, verwenden beide Platinen
und jedes künftige Modul.

**Dateien:**
- Anlegen: `tools/sch/gen.py`
- Anlegen: `tools/sch/modulsockel.py`
- Anlegen: `tests/test_modulsockel.py`

**Schnittstellen:**
- Verbraucht: `symlib.extract`, `symlib.pins`, `stack_spec.PIN_ROLLE`
- Liefert: `gen.Schaltplan` mit `bauteil(ref, libid, pos, wert, footprint)`,
  `draht(a, b)`, `netz(ref, pin, richtung, name)`, `nc(ref, pin)`,
  `selbstpruefung()`, `schreiben(pfad)`;
  `modulsockel.einbauen(sch, ox, oy, mit_flipflop=True)` liefert ein
  `dict` mit den Netznamen, die die Endstufe braucht.
  Ausserdem als Daten, weil der Test sie prüft:
  `modulsockel.STECKER_NETZE` (Rolle → Netzname am Stecker),
  `modulsockel.NETZE_NACH_AUSSEN` (was die Endstufe anschliesst:
  `IN1`, `IN2`, `NSLEEP`, `NFAULT`, `IPROPI`, `NOTAUS`),
  `modulsockel.ANZAHL_KENNWIDERSTAENDE` = `2`

- [ ] **Schritt 1: `tools/sch/gen.py` aus dem LED-Dimmer ableiten**

`~/Dokumente/Espace_des_Inventions/led_dimmer/hardware/generator/gen_sch.py`
enthält die Bausteine bereits: `comp`, `pinpos`, `net`, `wire`, `nc`, `emit`
und `selfcheck`. Ziehe sie in ein wiederverwendbares Modul `gen.py` heraus,
sodass die projektspezifischen Teile (welche Bauteile, welche Netze) draussen
bleiben. Übernimm die Selbstprüfung wörtlich — sie ist der Grund, dass das
Verfahren trägt: **jeder Bauteil-Pin muss an einem Drahtende oder an einem
`no_connect` hängen**, sonst bricht der Lauf ab.

- [ ] **Schritt 2: Den fehlschlagenden Test schreiben**

`tests/test_modulsockel.py`:

```python
"""Prueft den gemeinsamen Modulsockel-Block gegen den Vertrag.

Der Block sitzt auf jedem Modul. Ein Fehler darin ist ein Fehler in
jedem kuenftigen Modul -- deshalb wird er gegen tools/stack_spec.py
geprueft und nicht gegen sich selbst.
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
```

- [ ] **Schritt 3: Test laufen lassen, Fehlschlag bestätigen**

Ausführen: `python3 tests/test_modulsockel.py`
Erwartet: `ModuleNotFoundError: No module named 'modulsockel'`

- [ ] **Schritt 4: `tools/sch/modulsockel.py` schreiben**

Der Block enthält:

- **U100** STM32C011F6P6 (TSSOP-20) mit Abblockkondensator, Reset- und
  BOOT0-Anschluss vom Gatter, USART1 auf PA11/PA12 an `FLASH_TX`/`FLASH_RX`,
  I²C an `I2C_SDA`/`I2C_SCL`, zwei ADC-Eingänge an die Kennwiderstände
- **U101** D-Flipflop: `D` = `SEL` vom Stecker oben, `CLK` = `SEL_CLK`,
  `Q` = `SEL_OUT` zum Stecker unten **und** an die Gatter
- **U102/U103** die Gatter für `RESET = FLASH_MODE ∧ ¬Q` und
  `BOOT0 = FLASH_MODE ∧ Q`
- **R100/R101** die zwei Kennwiderstände gegen `ID_OBEN`
- **J100** Buchsenleiste 2×20 oben, **J101** Stiftleiste 2×20 unten,
  Pin für Pin verbunden **ausser** der Kettenleitung
- **J102** Leistungsstecker, durchgereicht

Die Zuordnung Pin → Rolle kommt aus `stack_spec.PIN_ROLLE`; schreibe sie
**nicht** ab, sondern lies sie aus dem Modul. Das ist der Sinn des Vertrags.

- [ ] **Schritt 5: Test laufen lassen, Erfolg bestätigen**

Ausführen: `python3 tests/test_modulsockel.py`
Erwartet: `alle Pruefungen bestanden`

- [ ] **Schritt 6: Committen**

```bash
git add tools/sch/gen.py tools/sch/modulsockel.py tests/test_modulsockel.py
git commit -m "Modulsockel als gemeinsamer Schaltplanblock"
```

---

### Aufgabe 4: Sockelplatine — Schaltplan

**Dateien:**
- Anlegen: `tools/sch/sockelplatine.py`
- Anlegen: `hardware/kicad/sockel/Sockelplatine.kicad_sch` (erzeugt)
- Anlegen: `hardware/kicad/sockel/Sockelplatine.kicad_pro`

**Schnittstellen:**
- Verbraucht: `gen.Schaltplan`, `modulsockel` (nur die Steckerteile, **ohne**
  MCU, Flipflop und Gatter — der Sockel ist kein Modul)

- [ ] **Schritt 1: Inhalt festlegen**

| Ref | Bauteil | Zweck |
|---|---|---|
| U1 | Raspberry Pi Pico, gesockelt | der Rechner |
| U2 | K7805-2000R3, SIP-3 | 24 V → 5 V, speist VSYS des Pico |
| C1, C2 | 0805 | Ein- und Ausgang des Reglers |
| C3 | 220 µF radial | Stützung am 24-V-Eingang |
| D1 | SMCJ30A, SMC | TVS am 24-V-Eingang |
| R1, R2 | 0805, 4,7 k | I²C-Abschluss, **nur hier** |
| J1 | Klemme 2-polig | 24 V Eingang |
| J2 | Stiftleiste 2×20, unten | zum Stapel |
| J3 | Leistungsstecker | 24 V in den Stapel |

Der Sockel hat **keine** Buchsenleiste oben — er sitzt zuoberst.

- [ ] **Schritt 2: `tools/sch/sockelplatine.py` schreiben und ausführen**

Ausführen: `python3 tools/sch/sockelplatine.py`
Erwartet: `hardware/kicad/sockel/Sockelplatine.kicad_sch` entsteht, und die
Selbstprüfung meldet keinen unverbundenen Pin.

- [ ] **Schritt 3: ERC und Netzliste prüfen**

```bash
kicad-cli sch erc --format json -o /tmp/erc_sockel.json \
  hardware/kicad/sockel/Sockelplatine.kicad_sch
kicad-cli sch export netlist -o /tmp/sockel.net \
  hardware/kicad/sockel/Sockelplatine.kicad_sch
```

Erwartet: keine Fehler (Warnungen zu nicht angeschlossenen Pico-Pins sind in
Ordnung und mit `no_connect` zu versehen), und der Export meldet **keine**
Annotationswarnung. Prüfe in der Netzliste von Hand: liegt `+5V` wirklich an
`VSYS` des Pico und **nicht** an `3V3`? Ein Verwechseln zerstört den Pico.

- [ ] **Schritt 4: Committen**

```bash
git add tools/sch/sockelplatine.py hardware/kicad/sockel
git commit -m "Sockelplatine: Schaltplan erzeugt"
```

---

### Aufgabe 5: Motormodul — Schaltplan

Die Endstufe ist bereits entworfen und auf JLCPCB-Bauteile umgestellt — im
Repo `~/Dokumente/Espace_des_Inventions/PecheAuxCanards`, Commit `39d871d`,
Datei `hardware/kicad/Unmögliche_Muttern.kicad_sch`. Übernimm die
Bauteilwerte und die Verschaltung von dort; **der Pico entfällt**, seine
Anschlüsse übernimmt der Modul-MCU aus dem Modulsockel.

**Dateien:**
- Anlegen: `tools/sch/motormodul.py`
- Anlegen: `hardware/kicad/motor/Motormodul.kicad_sch` (erzeugt)

- [ ] **Schritt 1: Die Endstufe aus dem Altprojekt ablesen**

```bash
cd ~/Dokumente/Espace_des_Inventions/PecheAuxCanards
kicad-cli sch export netlist -o /tmp/alt.net "hardware/kicad/Unmögliche_Muttern.kicad_sch"
```

Übernimm daraus: `D1` (SMCJ30A), `C12` (220 µF), `Q1` (P-MOSFET TO-252) mit
`R11`/`R12`, `U1` (DRV8876) mit `C9`/`C10`/`C11`, `R5`/`R10` (Stromgrenze,
`R10` unbestückt), `C13`, die Vorwiderstände `R7`/`R8`/`R9`/`R13`, `U2`
(PC817 SOP-4) mit `R6`, die Klemmen `J1` (24 V), `J5` (Motor), `J2` (Sensor)
und `J3` (Notaus, Stiftleiste).

**Was sich ändert:** Alles, was am Pico hing, hängt jetzt am Modul-MCU:
`IN1`, `IN2`, `NSLEEP`, `NFAULT`, `IPROPI`, die beiden Notaus-Eingänge und
der Sensoreingang. Die Namen dafür liefert
`modulsockel.NETZE_NACH_AUSSEN`.

**Die Netze, die den Modul-MCU mit der Endstufe verbinden** — das ist der
Teil, den es im Altprojekt so nicht gab, weil dort der Pico sass:

| Netz | von | nach |
|---|---|---|
| `IN1` | MCU-GPIO | `R7` → `U1` Pin 1 (EN/IN1) |
| `IN2` | MCU-GPIO | `R8` → `U1` Pin 2 (PH/IN2) |
| `NSLEEP` | MCU-GPIO | `R9` → `U1` Pin 3 (nSLEEP) |
| `NFAULT` | `U1` Pin 4, Pullup `R13` an +3V3 | MCU-GPIO (Eingang) |
| `IPROPI` | `U1` Pin 6, `R5`/`R10` gegen GND, `C13` | MCU-ADC |
| `NOTAUS_1`, `NOTAUS_2` | `J3` Pin 1 und 3 | MCU-GPIO **und** Stapelleitung `NOTAUS` |
| `SENSOR_3V3` | `U2` Pin 4 (Optokoppler-Ausgang) | MCU-GPIO |

Die Leistungsnetze bleiben wie im Altprojekt: `+24V`, `GND`, `Out1`, `Out2`
und der Strang von `J1` über die Source von `Q1`.

- [ ] **Schritt 2: Den korrigierten DRV8876-Footprint übernehmen**

Die Bibliothek im Altprojekt trägt drei Reparaturen, die hier nicht verloren
gehen dürfen: Wärmepad **mit** Masken- und Pastenöffnung, segmentiertes
Pastenmuster, und zwölf Wärmevias mit echtem Restring **auf Pad 17**.

```bash
mkdir -p hardware/kicad/components/footprints
cp -r ~/Dokumente/Espace_des_Inventions/PecheAuxCanards/hardware/kicad/components/footprints/DRV8876PWPR.pretty \
      hardware/kicad/components/footprints/
```

Prüfe danach: `grep -c '(pad 17 thru_hole circle' …/IC_DRV8876PWPR.kicad_mod`
muss **12** liefern.

- [ ] **Schritt 3: `tools/sch/motormodul.py` schreiben und ausführen**

Ausführen: `python3 tools/sch/motormodul.py`
Erwartet: Datei entsteht, Selbstprüfung ohne unverbundenen Pin.

- [ ] **Schritt 4: ERC und Netzlistenprüfung**

Prüfe von Hand in der exportierten Netzliste:
- `C12` Pin **1** liegt an `+24V` (das Symbol ist unpolarisiert, der
  Footprint nicht — auf v1 sind daran zwei Elkos explodiert)
- die Stromgrenze: `R5` bestückt, `R10` als DNP, beide zwischen `IPROPI`
  und `GND`
- `NOTAUS` erreicht den Modul-MCU **und** liegt auf der Stapelleitung

- [ ] **Schritt 5: Committen**

```bash
git add tools/sch/motormodul.py hardware/kicad/motor hardware/kicad/components
git commit -m "Motormodul: Schaltplan erzeugt, Endstufe aus dem Muttern-Print uebernommen"
```

---

### Aufgabe 6: Sockelplatine — Layout

**Dateien:**
- Anlegen: `tools/pcb/spec_sockel.py`
- Anlegen: `hardware/kicad/sockel/Sockelplatine.kicad_pcb` (erzeugt)

- [ ] **Schritt 1: Platzierung als Datenmodul**

Nach dem Muster von `tools/stack_spec.py`: Umriss und Lochbild aus dem
Vertrag, dazu die Platzierung. Der **2×20-Stecker muss an derselben Stelle
sitzen wie auf jedem Modul** — sonst passt der Stapel mechanisch nicht.
Lege diese Position **einmal** in `tools/stack_spec.py` fest
(`STECKER_POS`), damit beide Platinen daraus lesen; das schliesst zugleich
die Lücke, die die Schlussprüfung von Etappe 1a benannt hat.

- [ ] **Schritt 2: Geometrie prüfen**

Ausführen: `python3 tools/pcb/geometry.py` gegen die neue Platzierung.
Erwartet: keine Überlappung, nichts im M3-Freihaltebereich, nichts über der
Kante.

- [ ] **Schritt 3: Netzklassen setzen, Platine bauen**

```bash
python3 tools/pcb/netclasses.py hardware/kicad/sockel/Sockelplatine.kicad_pro
~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy tools/pcb/build.py
```

- [ ] **Schritt 4: Verdrahten und prüfen**

```bash
~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy tools/pcb/autoroute.py
kicad-cli pcb drc --format json -o /tmp/drc_sockel.json \
  hardware/kicad/sockel/Sockelplatine.kicad_pcb
```

Erwartet: **0 Kurzschlüsse, 0 unverbundene Netze, Schaltplan-Abgleich 0.**
Bahnbreiten prüfen: die Leistungsnetze müssen 1,00 mm haben, nicht 0,25 —
`autoroute.py` bricht ab, wenn ein Leistungsnetz fehlt, aber prüfe die
tatsächliche Breite in der SES nach.

- [ ] **Schritt 5: Hinsehen**

```bash
kicad-cli pcb render --side top --width 1400 -o /tmp/sockel_top.png \
  hardware/kicad/sockel/Sockelplatine.kicad_pcb
```

Das Bild ansehen. Kein Zahlen-Check ersetzt das: ein gespiegeltes Bauteil,
ein Stecker an der falschen Kante oder eine Bahn ins Leere sieht man, statt
sie zu zählen.

- [ ] **Schritt 6: Committen**

```bash
git add tools/pcb/spec_sockel.py tools/stack_spec.py hardware/kicad/sockel
git commit -m "Sockelplatine: Layout, Flaechen, Verdrahtung, DRC sauber"
```

---

### Aufgabe 7: Motormodul — Layout

**Dateien:**
- Anlegen: `tools/pcb/spec_motor.py`
- Anlegen: `hardware/kicad/motor/Motormodul.kicad_pcb` (erzeugt)

- [ ] **Schritt 1: Platzierung als Datenmodul**

Dieselbe Steckerposition wie der Sockel (aus `stack_spec.STECKER_POS`).
Die Klemmen an die Unterkante, damit die Kabel aller Module an derselben
Seite herauskommen.

**Der Wärmepfad des DRV8876 ist der Grund für diese Neuauflage.** Unter dem
Treiber gehört eine durchgehende Massefläche auf der Rückseite, an die die
zwölf Vias anschliessen. Keine Bahn darf sie zerschneiden.

- [ ] **Schritt 2: Geometrie prüfen**

Ausführen: `python3 tools/pcb/geometry.py` gegen die Platzierung des
Motormoduls. Erwartet: keine Überlappung, nichts im M3-Freihaltebereich,
nichts über der Kante.

- [ ] **Schritt 3: Netzklassen setzen, Platine bauen**

```bash
python3 tools/pcb/netclasses.py hardware/kicad/motor/Motormodul.kicad_pro
~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy tools/pcb/build.py
```

- [ ] **Schritt 4: Verdrahten und prüfen**

```bash
~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy tools/pcb/autoroute.py
kicad-cli pcb drc --format json -o /tmp/drc_motor.json \
  hardware/kicad/motor/Motormodul.kicad_pcb
```

Erwartet: **0 Kurzschlüsse, 0 unverbundene Netze, Schaltplan-Abgleich 0.**

- [ ] **Schritt 5: Hinsehen und die drei Altfehler nachprüfen**

```bash
kicad-cli pcb render --side top --width 1400 -o /tmp/motor_top.png \
  hardware/kicad/motor/Motormodul.kicad_pcb
kicad-cli pcb render --side bottom --width 1400 -o /tmp/motor_bot.png \
  hardware/kicad/motor/Motormodul.kicad_pcb
```

Beide Bilder ansehen. Auf der Rückseite muss die Massefläche unter dem
Treiber durchgehend sein — dort hängen die zwölf Wärmevias.

Zusätzlich zu prüfen, weil es die drei nachgewiesenen Fehler von v1 sind:

```bash
~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy \
  ~/.claude/skills/kicad-pcbnew-scripting/scripts/pcb_checks.py \
  hardware/kicad/motor/Motormodul.kicad_pcb --min-width 1.0 --power '^\+?24V|Out[12]'
```

Erwartet: keine verpolten Elkos, keine zu dünnen Leistungsbahnen, keine
nummerierten Pads ohne Netz.

- [ ] **Schritt 6: Committen**

```bash
git add tools/pcb/spec_motor.py hardware/kicad/motor
git commit -m "Motormodul: Layout mit repariertem Waermepfad, DRC sauber"
```

---

### Aufgabe 8: Fertigungsdaten für beide Platinen

**Dateien:**
- Anlegen: `tools/jlc.py`
- Anlegen: `hardware/fertigung/{sockel,motor}/`

- [ ] **Schritt 1: `tools/jlc.py` nach dem Muster des LED-Dimmers**

Vorlage:
`~/Dokumente/Espace_des_Inventions/led_dimmer/hardware/generator/gen_jlc.py`.
Übernimm die Konventionen wörtlich:

- Kopfzeile `Comment,Designator,Footprint,LCSC Part #`
- CPL mit `Designator,Mid X,Mid Y,Layer,Rotation`, Masse in mm mit
  `mm`-Endung, **y negativ**
- Bauteile mit `geprueft=False` bekommen **keine** LCSC-Nummer, sondern eine
  so genaue Beschreibung, dass JLCs Abgleich eindeutig trifft
- Ein Eintrag `UNBESTUECKT` mit **Begründung je Zeile**; darin gehören die
  Pico-Buchsenleisten (von Hand, mit gestecktem Pico ausgerichtet) und `R10`
  (Stromgrenze, ab Werk unbestückt)
- Das Skript **bricht ab**, wenn ein Designator in der CPL fehlt, den die BOM
  nennt — JLC weist den Auftrag sonst zurück

- [ ] **Schritt 2: Gerber, Bohrdaten, Position exportieren**

```bash
for B in sockel motor; do
  kicad-cli pcb export gerbers -o hardware/fertigung/$B/gerber/ hardware/kicad/$B/*.kicad_pcb
  kicad-cli pcb export drill   -o hardware/fertigung/$B/gerber/ hardware/kicad/$B/*.kicad_pcb
  kicad-cli pcb export pos --format csv --units mm \
    -o hardware/fertigung/$B/pos.csv hardware/kicad/$B/*.kicad_pcb
done
```

- [ ] **Schritt 3: BOM und CPL erzeugen und gegenlesen**

Ausführen: `python3 tools/jlc.py sockel` und `python3 tools/jlc.py motor`.
Beide Dateien **selbst öffnen und lesen**. Prüfe: keine erfundene Nummer,
jede unbestückte Position begründet, die Zahl der CPL-Zeilen passt zur BOM.

- [ ] **Schritt 4: Committen**

```bash
git add tools/jlc.py hardware/fertigung
git commit -m "Fertigungsdaten fuer beide Platinen, BOM und CPL im JLC-Format"
```

---

### Aufgabe 9: Gehäuse und Dokumentation

**Dateien:**
- Ändern: `hardware/box/canards_box.scad` (aus dem Muttern-Projekt übernehmen)
- Ändern: `README.md`, `docs/vertrag.md`

- [ ] **Schritt 1: Gehäuse übernehmen und auf den Stapel anpassen**

Vorlage:
`~/Dokumente/Espace_des_Inventions/PecheAuxCanards/hardware/box/canards_box.scad`.
Sie ist gegen die Druck-Gates geprüft und sichert ihre Masse per `assert`
gegen die Spezifikation zu. Anzupassen: die Höhe wächst mit der Zahl der
Module (15 mm je Platine), die Kabelschlitze müssen für **jede** Ebene
offen sein, und das Loch unter der Pico-Antenne entfällt — der Sockel sitzt
oben.

Danach prüfen:

```bash
openscad -o /tmp/box.stl -D 'teil="box"' hardware/box/picostack_box.scad
python3 ~/.claude/skills/print-mesh-gates/scripts/verify_stl.py /tmp/box.stl
python3 ~/.claude/skills/print-mesh-gates/scripts/downfacing_probe.py /tmp/box.stl --quiet
```

Erwartet: 1 Shell, non-manifold 0. Der Sektor-Test meldet bei einem
Rechteckgehäuse „leere Sektoren" und damit FAIL — das ist ohne Aussage,
verwertbar sind Auflage und Überhang.

- [ ] **Schritt 2: README und Vertrag nachziehen**

Im README: der Statushinweis wird kürzer, weil es jetzt Platinen **gibt** —
aber der Tischnachweis bleibt offen, solange kein Chip beschrieben wurde.
Schreibe genau das hin, nicht mehr. Im Vertrag: die Steckerposition
ergänzen, die in Aufgabe 6 festgelegt wurde.

- [ ] **Schritt 3: Committen**

```bash
git add hardware/box README.md docs/vertrag.md tools/vertrag_doku.py
git commit -m "Gehaeuse fuer den Stapel, Doku nachgezogen"
```

---

## Was dieser Plan bewusst nicht enthält

- **Keine Modul-Firmware.** Der Registersatz, der sichere Zustand und die
  Aufzählung des Stapels sind Etappe 1c.
- **Keine Dimmer-Varianten.** Etappe 2.
- **Keine Bestellung.** Die Fertigungsdaten entstehen, abgeschickt werden
  sie von Hand — mit dem Wissen, dass der Tischnachweis noch aussteht.

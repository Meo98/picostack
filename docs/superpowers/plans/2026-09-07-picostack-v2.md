# PicoStack v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sockelplatine abschaffen — jedes Modul trägt Pico-Steckreihen, eigene 6–30-V-Versorgung und beschriftete Randpads; die beiden v1-Blocker (Notaus-Inversion, Verpolschutz-Topologie) sind mit Rot-Nachweisen gefixt.

**Architecture:** Generativer KiCad-Fluss wie v1: `tools/stack_spec.py` (bindender Vertrag) → Schaltplan-Generatoren (`tools/sch/*.py`) → Platzierungs-Specs (`tools/pcb/spec_*.py`) → Pipeline `build.py`/`autoroute.py`/`masseheiler.py`/`steckerprobe.py` → Fab-Daten via `tools/jlc.py`. v2 ändert die Stapel-GEOMETRIE (zwei 1×20-Reihen in Pico-Anordnung statt 2×20-Block); `PIN_ROLLE` bleibt wörtlich.

**Tech Stack:** Python 3 (KiCad-frei wo möglich), pcbnew via `tools/pcb/kipy`, `kicad-cli` (ERC/DRC/Gerber), freerouting 2.3.0 (Dice-Loop), Testsuite `python3 tests/run_all.py`.

**Spec:** `docs/superpowers/specs/2026-09-07-picostack-v2-design.md`

## Global Constraints

- Vertragswerte in `stack_spec.py` sind bindend; Änderung nur bewusst und mit Test.
- LCSC-Nummern NUR von selbst gesichteten Produktseiten (Beleg in `hardware/bauteile*.md`); gesichtet und freigegeben: 1G07 = C7830, K7805-1000R3 = C909765, SS36C = C16237, KF350-3.5-2P = C474892.
- Kommentare/Bezeichner deutsch, ASCII-Umschreibung (ue/oe/ae) wie im Bestand.
- Nach jeder Aufgabe: `python3 tests/run_all.py` → „alle Suiten gruen“ (Suitenzahl wächst).
- ERC/DRC immer `--severity-error --exit-code-violations`; die Wahrheit über Routing ist KiCads DRC, nie der Router-Report.
- Commits klein, deutsch, mit Warum; Board-Artefakte (`.kicad_pcb`) committen (Artifact of Record).
- v1 bleibt unangetastet lauffähig, bis eine Aufgabe sie ausdrücklich ersetzt; `test_erzeugte_dateien.py` muss in jedem Zwischenstand bestehen.

---

### Task 1: Platzprobe → neues Einheitsmaß

**Files:**
- Create: `tools/platzprobe_v2.py`
- Test: Skript selbst ist die Probe (Exit ≠ 0 bei Nichtpassen)

**Interfaces:**
- Produces: entschiedene Konstanten `BOARD_W_V2`, `BOARD_H_V2`, Kantenbelegung der Randpads — werden in Task 2 in den Vertrag übernommen (Zahlen aus dem Skriptreport in den Vertragskommentar kopieren).

- [ ] **Step 1: Flächeninventar schreiben.** KiCad-freies Skript, das die v2-Pflichtflächen addiert und gegen Kandidatenmaße prüft: zwei 1×20-Reihen (je 50,8 × 5,1 mm Hof, Reihenabstand 17,78 mm, Pico-Schatten 51 × 21 mm als Höhen-Keepout, keine Bauteile > 3 mm darunter), Leistungsstecker-2×2 + zwei Kettenstecker (Höfe aus `stack_spec.STECKER_POS` übernehmen), Versorgungszelle (Klemme 8×8,6 + Q-Schutz 11,1×7 + TVS 9,8×6,7 + Regler SIP-3 10×10 + Schottky 9,8×6,7 + Elko 8,5×8,5), Randpads (18 GPIO + 4×3V3/GND = 22 Löcher à 2,54 mm = 55,9 mm Kante, zzgl. Silk-Beschriftung 4 mm Tiefe), M3-Ecklöcher + Freihaltekreise, und als Nutzlast-Referenz die Bauteilhoffläche des Motormoduls v1 (aus `spec_motor.PLACEMENT` summieren, minus entfallende Teile: J100-Block, plus neue Zelle).
- [ ] **Step 2: Kandidaten rechnen.** Kandidaten 70×60, 75×65, 80×70 prüfen; Ausgabe je Kandidat: freie Nutzfläche in mm² und ob Randpad-Kante + Pico-Reihen kollisionsfrei liegen. Skript endet mit `raise SystemExit(1)`, wenn KEIN Kandidat passt.
- [ ] **Step 3: Laufen lassen:** `python3 tools/platzprobe_v2.py` — Expected: mindestens ein Kandidat „PASST“, kleinsten wählen.
- [ ] **Step 4: Commit** `git add tools/platzprobe_v2.py && git commit -m "v2-Platzprobe: Einheitsmass hergeleitet"`

### Task 2: Vertrag v2 in `stack_spec.py` (TDD)

**Files:**
- Modify: `tools/stack_spec.py`
- Test: `tests/test_stack_spec.py` (erweitern)

**Interfaces:**
- Produces: `VERTRAG_VERSION = 2`; `BOARD_W`/`BOARD_H` = Maß aus Task 1; `STECKER_POS["stapel_links"]` / `["stapel_rechts"]` (je `{"zweck","stecker","footprints",("PinHeader_1x20"/"PinSocket_1x20"),"pin1","drehung","mitte","flaeche"}`, Reihenabstand exakt 17,78 mm, Pinraster 2,54 mm); `PIN_ROLLE` unverändert (Pico-Zählung: 1–20 links oben→unten, 21–40 rechts unten→oben); `RANDPADS` = Tupel aus `(pico_pin, "GPx"|"3V3"|"GND", (x, y))`; `VERSORGUNG` = Dict mit Zusicherungen `{"schutz_drain_an": "PWR_IN", "gate_teiler_an": "+24V_LOKAL", "vsys_diode": True, "eingang_v": (6.0, 30.0)}`.

- [ ] **Step 1: Failing Tests schreiben** in `tests/test_stack_spec.py`:
```python
check("Vertragsversion 2", getattr(S, "VERTRAG_VERSION", 1), 2)
check("Stapelreihen in Pico-Geometrie",
      round(abs(S.STECKER_POS["stapel_links"]["mitte"][0]
                - S.STECKER_POS["stapel_rechts"]["mitte"][0]), 2), 17.78)
check("alter 2x20-Block ist weg", "stapel" in S.STECKER_POS, False)
check("jeder freie Pin hat genau ein Randpad",
      sorted(p for p, _, _ in S.RANDPADS if S.PIN_ROLLE.get(p) == "frei"),
      sorted(p for p, r in S.PIN_ROLLE.items() if r == "frei"))
check("Versorgungszusagen vorhanden",
      S.VERSORGUNG["schutz_drain_an"], "PWR_IN")
```
- [ ] **Step 2: Rot sehen:** `python3 tests/test_stack_spec.py` — Expected: FEHLER-Zeilen zu allen fünf Checks.
- [ ] **Step 3: Vertrag implementieren** (Werte aus Task 1; `LANDEPUNKTE_VERDREHT`/M3 auf neues Maß umrechnen — dieselbe Herleitungslogik wie v1, Kommentar dokumentiert die Rechnung).
- [ ] **Step 4: Grün sehen:** `python3 tests/test_stack_spec.py` → „alle Pruefungen bestanden“. Danach `python3 tests/run_all.py`: Suiten, die v1-Geometrie prüfen (`test_modulsockel`, `test_spec_*`), werden ROT — das ist der Fahrplan der Folgeaufgaben; im Commit-Text festhalten, WELCHE Suiten bewusst rot sind.
- [ ] **Step 5: Commit** (`stack_spec v2 + Rot-Liste der Folgearbeiten`).

### Task 3: Versorgungszelle `tools/sch/versorgung.py` (TDD, enthält Verpolschutz-Rot-Nachweis)

**Files:**
- Create: `tools/sch/versorgung.py`
- Create: `tests/test_versorgung.py`

**Interfaces:**
- Produces: `versorgung.bauen(sch, ox, oy)` — platziert mit festen Referenzen `J90` (KF350-Klemme, Netz `PWR_IN`), `Q90` (IRFR5305, **Pad 2/Drain = PWR_IN, Pad 3/Source = +24V**), `R90`/`R91` (10k-Gate-Teiler: R90 Gate↔**+24V**, R91 Gate↔GND), `D90` (SMCJ30A, Kathode +24V), `U90` (K7805-1000R3: IN=+24V, OUT=`+5V_LOKAL`), `D91` (SS36C: Anode +5V_LOKAL, Kathode **VSYS**), `C90` (220u-Elko an +24V), `C91` (22u an +5V_LOKAL). Verbraucher: alle Modul-Generatoren rufen `versorgung.bauen` auf; `+24V` ist die geschützte lokale Schiene (identisch mit der Stapel-24V-Schiene), `VSYS` liegt auf Pico-Pin 39.

- [ ] **Step 1: Failing Test schreiben** (`tests/test_versorgung.py`): Zelle in ein leeres `gen.Schaltplan` bauen, Netzliste extrahieren (Muster: `_netz_pins` aus `tests/test_modulsockel.py` wörtlich übernehmen) und prüfen:
```python
check("Schutz-Drain an der Einspeisung", ("Q90", "2") in pins["PWR_IN"], True)
check("Schutz-Source an der lokalen Schiene", ("Q90", "3") in pins["+24V"], True)
check("Gate-Teiler an der lokalen Schiene", ("R90", "2") in pins["+24V"], True)
check("VSYS nur ueber die Diode", ("D91", "1") in pins["VSYS"]
      and not any(r == "U90" for r, _ in pins["VSYS"]), True)
```
   Zusätzlich als **Rot-Nachweis der Fehlerklasse**: denselben Check gegen `motormodul`-v1-Netze laufen lassen und im Testkommentar festhalten, dass er dort (Q1 Source an PWR24V) VOR dieser Etappe fehlschlug.
- [ ] **Step 2: Rot sehen** (`python3 tests/test_versorgung.py` → Import-/Attributfehler).
- [ ] **Step 3: Zelle implementieren** (Symbole/Footprints wie Sockel-v1: `FP_KLEMME_2` KF350-Muster aus `dimmermodul.py`, `Q_PMOS_GDS`, `FP_RECOM` aus `sockelplatine.py`, `D_SMC`; Herleitungs-Kommentare aus `sockelplatine.py` Nachtrag 2026-09-07 übernehmen).
- [ ] **Step 4: Grün sehen**, `run_all.py`-Stand unverändert zu Task 2.
- [ ] **Step 5: Commit.**

### Task 4: `gen.py` MPN-Felder + `modulsockel.py` v2 (Stapelreihen, Randpads)

**Files:**
- Modify: `tools/sch/gen.py` (Parameter `felder=None` an `bauteil()`: Dict → zusätzliche Symbol-Properties, z. B. `{"LCSC": "C7830"}`)
- Modify: `tools/sch/modulsockel.py` (`_stapelstecker` → zwei 1×20 aus `STECKER_POS["stapel_links"/"stapel_rechts"]`; neue Funktion `randpads(sch)` platziert je Kante eine unbestückte THT-Padreihe `J95`/`J96` mit Pin-Zuordnung aus `S.RANDPADS`)
- Test: `tests/test_modulsockel.py` (Geometrie-Checks auf die zwei Reihen + Randpad-Vollständigkeit umschreiben; alte 2×20-Checks löschen)

**Interfaces:**
- Consumes: `S.STECKER_POS["stapel_links"/"stapel_rechts"]`, `S.RANDPADS`.
- Produces: `modulsockel.bauen(sch, ...)` wie bisher, plus `modulsockel.randpads(sch)`; `gen.Schaltplan.bauteil(..., felder={"LCSC": ...})`.

- [ ] Step 1: Tests zuerst umschreiben (rot), Step 2: implementieren, Step 3: `python3 tests/test_modulsockel.py` grün, Step 4: Commit.

### Task 5: Motormodul v2 (inkl. Notaus-Fix mit Rot-Nachweis)

**Files:**
- Modify: `tools/sch/motormodul.py`
- Test: `tests/test_motormodul.py`

**Interfaces:**
- Consumes: `versorgung.bauen`, `modulsockel` v2.
- Produces: `hardware/kicad/motor/Motormodul.kicad_sch` v2, ERC 0/0.

- [ ] **Step 1: Notaus-Polaritätsprobe als failing Test** in `tests/test_motormodul.py`:
```python
# Ruhestromschleife ok (SCHLEIFE HIGH) MUSS NOTAUS freigeben: der
# Treiber ist ein NICHTinvertierender OD-Buffer. 1G06 macht das Board
# fail-unsafe -- dieser Check war gegen v1 ROT (2026-09-07).
check("Notaus-Treiber nichtinvertierend",
      "74LVC1G07" in _quelltext and "74LVC1G06" not in _quelltext, True)
```
- [ ] **Step 2: Rot sehen.** **Step 3:** U6/U7 auf `74xGxx:74LVC1G07` (Wert `SN74LVC1G07`, Feld LCSC C7830) umstellen; alten 1G06-Herleitungskommentar als „ERSETZT, Grund:“ stehen lassen; `_BAUSTEINE`-Menge im Test mitziehen. Versorgungszelle einbauen (ersetzt Q1/R11/R12/D1/C12-Strang — Referenzen werden Q90…), Sensorlose Altteile prüfen, je Einzelgatter ein 100n (`C17`…) ergänzen, `erzeugen()` laufen lassen.
- [ ] **Step 4:** `kicad-cli sch erc --severity-error --exit-code-violations -o /tmp/erc.rpt hardware/kicad/motor/Motormodul.kicad_sch` → Exit 0; `python3 tests/test_motormodul.py` + `tests/test_versorgung.py` grün.
- [ ] **Step 5: Commit.**

### Task 6: Dimmermodul v2 (PWM-Pins, Versorgungszelle)

**Files:**
- Modify: `tools/sch/dimmermodul.py`
- Test: `tests/test_erzeugte_dateien.py` (läuft mit), `tests/test_spec_dimmer.py` folgt in Task 8

**Interfaces:**
- Produces: `Dimmer{1,3,4}.kicad_sch` v2, ERC 0/0; `PWM_PINS` neu = `{1:"15" (PA8), 2:"14" (PA7), 3:"12" (PA5), 4:"13" (PA6)}` — vorher am STM32C011F6-TSSOP20-Symbol verifizieren, dass Pin 12/13 = PA5/PA6 und im Nest unbelegt sind; wenn belegt, die zwei freien Port-A-Pins mit den kleinsten Nummern nehmen und die Zuordnung im Docstring als Firmware-Zusage dokumentieren.

- [ ] Step 1: Docstring-Zusage + `PWM_PINS` ändern (Begründung: PC14/PC15 sind OSC32-Pins mit schwachem Treiber — 47-nC-Gates bekämen träge Flanken). Step 2: `versorgung.bauen` statt `_leistung()` (Q10/R11/R12/D10/C12 entfallen zugunsten Q90-Zelle). Step 3: Gatter-Abblockung ergänzen. Step 4: `python3 tools/sch/dimmermodul.py` + ERC aller drei → 0/0. Step 5: Commit.

### Task 7: Platzierungs-Specs v2 + Motor-Board durch die Pipeline

**Files:**
- Modify: `tools/pcb/spec_motor.py` (neues Boardmaß, zwei Stapelreihen-Höfe, Randpad-Reihen, Versorgungszelle rechts oben; PRE_TRACKS-Nestbestand bleibt, Leistungs-Vorverdrahtung neu herleiten)
- Modify: `tests/test_spec_motor.py`
- Produce: `hardware/kicad/motor/Motormodul.kicad_pcb` v2

- [ ] Step 1: Spec-Tests auf v2-Geometrie umschreiben (rot). Step 2: Spec anpassen, `python3 tests/test_spec_motor.py` grün. Step 3: Pipeline (Kommandos wörtlich):
```bash
tools/pcb/kipy tools/pcb/build.py spec_motor hardware/kicad/motor/Motormodul.net hardware/kicad/motor/Motormodul.kicad_pcb
tools/pcb/kipy tools/pcb/autoroute.py hardware/kicad/motor/Motormodul.kicad_pcb spec_motor   # Dice-Loop bis DRC 0/0, bestes Board behalten
tools/pcb/kipy tools/pcb/masseheiler.py hardware/kicad/motor/Motormodul.kicad_pcb
tools/pcb/kipy tools/pcb/steckerprobe.py hardware/kicad/motor/Motormodul.kicad_pcb
kicad-cli pcb drc --severity-error --exit-code-violations hardware/kicad/motor/Motormodul.kicad_pcb
```
  (exakte Argumentlisten vor dem Lauf gegen die `Aufruf:`-Zeilen der Skripte prüfen — `build.py` erwartet `<spec> <netlist> <ziel>`, `autoroute.py` `<board> <spec>`). Dangling-Via-Scan ergänzen: pcbnew-Einzeiler, der Vias ohne zwei Anschlüsse meldet, in `tools/pcb/pcb_checks.py` falls dort noch nicht vorhanden. Step 4: alle Proben grün → Commit (Board ist Artifact of Record).

### Task 8: Dimmer-Specs v2 + drei Boards durch die Pipeline

**Files:**
- Modify: `tools/pcb/spec_dimmer_basis.py`, `tests/test_spec_dimmer.py`
- Produce: `Dimmer{1,3,4}.kicad_pcb` v2

- [ ] Wie Task 7, parametrisch: Basis-Beschreibung auf neues Maß + Q90-Zelle + Randpads; Nest-wörtlich-vom-Motor-Zusage im Test beibehalten; Pipeline je Board; DRC 0/0 ×3; Commit.

### Task 9: Fertigungsdaten v2

**Files:**
- Modify: `tools/jlc.py` (BOM-Zeilen: 1G07 C7830 statt 1G06; je Board Klemme C474892, K7805 C909765, Schottky-VSYS SS36C C16237, Elko C45078; Sockel-Eintrag als deprecated markieren, `BOARDS["sockel"]` bleibt für v1-Archiv), `tools/pcb/fertigung.py`-Lauf je Board, `tools/pcb/zentroide.py` je Board
- Create: `hardware/fertigung/{motor,dimmer1,dimmer3,dimmer4}/…` v2 (gerber/, pos.csv, zentroide.csv, jlc-bom.csv, jlc-cpl.csv, UNBESTUECKT.txt, `<board>-gerber-jlc.zip`)
- Modify: `hardware/bauteile-dimmer.md` → Nachtrag v2 (nur neue Sichtungen; alle vier Nummern oben sind bereits belegt)

- [ ] Step 1: `python3 tools/jlc.py <board>` je Board → Vollständigkeitsabgleich grün (der beidseitige Abgleich ist die Probe). Step 2: ZIPs bauen (Python `zipfile`, flach). Step 3: `python3 tests/run_all.py` → ALLE Suiten grün (keine bewusste Rot-Restliste mehr). Step 4: Commit.

### Task 10: Doku, Website, Release

**Files:**
- Modify: `README.md`, `docs/index.html` (v2-Story „one board + a Pico“, Renders via `kicad-cli pcb render` wie v1), `hardware/fertigung/ORDERING.md`
- Modify: Sockel-Verzeichnisse mit „v1-only“-Hinweis (README-Zeile, kein Löschen)
- Release: Tag `v0.2.0` mit vier Fab-ZIPs

- [ ] Step 1: Texte/Renders. Step 2: `gh release create v0.2.0 …`. Step 3: Memory-Eintrag (`picostack-modulsystem.md`) aktualisieren. Step 4: Commit + Push.

---

## Self-Review (erledigt)

- Spec-Deckung: Stapelgeometrie (T2/T4), Versorgung+Schottky-OR (T3), Randpads (T2/T4/T7-8), Blocker-Fixes mit Rot-Nachweisen (T3/T5), MPN-Felder (T4), PWM-Umzug (T6), Wertesync (T5-8 erzeugen alles neu), Boardmaß (T1), TVS-Fenster-Entscheid (T3 Step 3, Datenblatt-Beleg in bauteile-dimmer.md), Migration/Release (T9-10). Keine Lücke gefunden.
- Platzhalter: keine („prüfen ob Pin 12/13 = PA5/PA6“ ist eine echte Verifikationsanweisung mit definiertem Fallback, kein TBD).
- Typkonsistenz: Referenzen Q90/R90/R91/D90/D91/U90/C90/C91/J90/J95/J96 in T3 definiert und in T5-T8 identisch verwendet; `RANDPADS`-Format aus T2 wird in T4 konsumiert.

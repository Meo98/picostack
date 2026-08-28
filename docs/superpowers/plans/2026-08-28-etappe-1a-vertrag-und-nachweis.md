# PicoStack Etappe 1a — Vertrag und Machbarkeitsnachweis

> **Für agentische Bearbeiter:** ERFORDERLICHE SUB-SKILL:
> `superpowers:subagent-driven-development` (empfohlen) oder
> `superpowers:executing-plans`. Die Schritte nutzen Checkbox-Syntax
> (`- [ ]`) zur Nachverfolgung.

**Ziel:** Die Steckerbelegung als prüfbares Datenmodul festschreiben und
beweisen, dass ein Pico einen Modul-MCU über dessen ROM-Bootlader
beschreiben kann — bevor Leiterplatten darum herum entstehen.

**Architektur:** Ein KiCad-freies Python-Modul (`tools/stack_spec.py`)
ist die einzige Quelle für Steckerbelegung, Umriss, Lochbild und
Modultyp-Nummern; es ist ohne KiCad testbar. Darauf setzt eine
MicroPython-Umsetzung des ST-Bootlader-Protokolls auf dem Pico auf.
Der Nachweis läuft auf dem Tisch mit einem einzelnen MCU, ohne Platine.

**Tech-Stack:** Python 3 (Werkzeuge und Tests), MicroPython (Pico),
STM32C0 als Modul-MCU, ST-Bootlader nach AN3155.

**Spec:** `docs/superpowers/specs/2026-08-28-picostack-design.md`

## Globale Rahmenbedingungen

Wörtlich aus der Spec übernommen; sie gelten für **jede** Aufgabe:

- Umriss **64,0 × 60,0 mm**, Ecken 3 mm gerundet
- Vier M3-Bohrungen (3,2 mm), je 4,0 mm von den Kanten
- **15 mm** Abstand zwischen den Platinen
- Signalstecker **2×20**, Pico-Pinbild, zwei getrennte Steckerteile je
  Modul (Buchse oben, Stift unten, in der Platine verbunden)
- Abschlusswiderstände des I²C **nur auf dem Sockel**
- Sicherer Zustand nach **500 ms** ohne gültigen Befehl
- Der Sockel sitzt **zuoberst** im Stapel
- LCSC-Nummern werden nur eingetragen, wenn sie von einer
  LCSC- oder JLCPCB-Produktseite stammen — nie aus dem Gedächtnis.
  Sonst bleibt das Feld leer und die Beschreibung ist so genau, dass
  der Abgleich eindeutig trifft. (Konvention aus dem LED-Dimmer.)

**Arbeitsverzeichnis für alle Befehle:** `~/Dokumente/picostack`

---

### Aufgabe 1: Bauteilwahl belegen

Diese Aufgabe erzeugt keinen Code, sondern Entscheidungen mit Beleg.
Alles Weitere hängt daran, und alles Weitere wäre wertlos, wenn der
MCU sich nicht maschinell bestücken lässt.

**Dateien:**
- Anlegen: `hardware/bauteile.md`

**Schnittstellen:**
- Liefert: die MCU-Typenbezeichnung, seine Bootlader-Pins und die
  LCSC-Nummern für Aufgabe 2 und 4

- [ ] **Schritt 1: MCU-Verfügbarkeit bei JLCPCB prüfen**

Auf `jlcpcb.com/parts/componentSearch` nach `STM32C011` suchen.
Festhalten: Bauform, ob Basic oder Extended, Lagerbestand, LCSC-Nummer.
Bekannt ist bisher nur: **STM32C011F6P6, TSSOP-20, LCSC C5456198**,
rund 0,55 $ — gefunden auf einer LCSC-Produktseite, aber die
JLCPCB-*Bestückbarkeit* ist damit **nicht** belegt.

Wenn nicht bestückbar: `PY32F002A` prüfen (Puya, rund 8 Rappen). Der
ist billiger, sein Bootlader aber schlechter dokumentiert — das ist ein
bewusster Rückschritt gegenüber der Spec-Entscheidung „Bootlader
nachschlagen statt nachbauen" und gehört als solcher vermerkt.

- [ ] **Schritt 2: Bootlader-Pins aus AN2606 heraussuchen**

ST-Dokument AN2606, Abschnitt zum STM32C0. Festhalten: auf welchen
Pins der USART-Bootlader lauscht, wie er aktiviert wird (BOOT0-Pin oder
Option-Byte), und ob diese Pins mit SWDIO/SWCLK zusammenfallen.

Der letzte Punkt ist der kritische: fallen sie zusammen, tragen diese
Pins nach dem Reset Pull-Widerstände, und die gemeinsame Sendeleitung
im Stapel bekommt damit ein Problem.

- [ ] **Schritt 3: Pin-Zustand nach Reset belegen**

Im Referenzhandbuch nachlesen, in welchem Zustand die GPIO nach einem
Reset stehen. Erwartet wird: analog beziehungsweise Eingang, also
hochohmig. Genau darauf beruht der Entwurf — unbeteiligte Module liegen
im Reset und dürfen die gemeinsame Sendeleitung nicht belasten.

Trifft das für die Bootlader-Pins **nicht** zu, ist der Entwurf an
dieser Stelle falsch und braucht ein Gatter in der Sendeleitung. Das
hier festzustellen kostet eine Stunde, es später festzustellen kostet
eine Leiterplattenserie.

- [ ] **Schritt 4: Die übrigen offenen Punkte der Spec abarbeiten**

- Strombelastbarkeit des vorgesehenen Leistungssteckers → Obergrenze
  für den ganzen Stapel
- 3,3-V-Budget des Pico gegen die Zahl der Module (Ruhestrom eines
  Modul-MCU × 10)
- Verfügbarkeit des `DRV8876` bei JLCPCB

- [ ] **Schritt 5: `hardware/bauteile.md` schreiben**

Eine Tabelle je Bauteil mit den Spalten: Zweck, Typ, Bauform, LCSC,
**geprüft (ja/nein)**, Quelle. „Geprüft" heisst: von einer Produktseite
abgelesen, nicht erinnert. Dazu je ein Absatz zu den drei
Belegen aus Schritt 2 bis 4, mit Dokumentnummer und Abschnitt.

- [ ] **Schritt 6: Committen**

```bash
git add hardware/bauteile.md
git commit -m "Bauteilwahl belegt: MCU, Bootlader-Pins, Reset-Zustand"
```

---

### Aufgabe 2: Der Vertrag als prüfbares Datenmodul

**Dateien:**
- Anlegen: `tools/stack_spec.py`
- Anlegen: `tests/test_stack_spec.py`

**Schnittstellen:**
- Liefert: `PIN_ROLLE` (dict Pico-Pin → Rolle), `RESERVIERT`,
  `BOARD_W`, `BOARD_H`, `M3_HOLES`, `MODULTYPEN`, `ID_WIDERSTAENDE`
- Verbraucht: nichts (bewusst ohne KiCad-Abhängigkeit)

- [ ] **Schritt 1: Den fehlschlagenden Test schreiben**

`tests/test_stack_spec.py`:

```python
"""Prueft den Vertrag. Ohne KiCad, ohne Hardware."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "tools"))
import stack_spec as S

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- Umriss und Lochbild ---
check("Breite", S.BOARD_W, 64.0)
check("Hoehe", S.BOARD_H, 60.0)
check("vier M3", len(S.M3_HOLES), 4)
check("Lochbild 56 mm", S.M3_HOLES[2][0] - S.M3_HOLES[0][0], 56.0)
check("Lochbild 52 mm", S.M3_HOLES[1][1] - S.M3_HOLES[0][1], 52.0)

# --- Steckerbelegung ---
check("40 Pins beschrieben", len(S.PIN_ROLLE), 40)

# Jede reservierte Rolle kommt genau einmal vor. Zwei Pins mit
# derselben Aufgabe waeren ein stiller Kurzschluss im Vertrag.
for rolle in S.RESERVIERT:
    n = sum(1 for r in S.PIN_ROLLE.values() if r == rolle)
    check("Rolle %s genau einmal" % rolle, n, 1)

# Reservierte Rollen duerfen nicht auf Versorgungspins liegen.
for pin, rolle in S.PIN_ROLLE.items():
    if rolle in S.RESERVIERT:
        check("Pin %d ist kein Versorgungspin" % pin,
              S.IST_VERSORGUNG(pin), False)

# --- Modultypen ---
check("Motor hat Nummer", "Motor" in
      {t["name"] for t in S.MODULTYPEN.values()}, True)
# Nummern ab 0x80 bleiben fremden Modulen vorbehalten; wer sie
# selbst belegt, nimmt der Community den Platz weg.
for nr in S.MODULTYPEN:
    check("Nummer 0x%02X unter 0x80" % nr, nr < 0x80, True)

# --- Kennwiderstaende ---
# Zwei Teiler zu je 16 Stufen ergeben 256 Nummern. Die Stufen muessen
# sich im ADC sicher unterscheiden lassen.
stufen = sorted(S.ID_WIDERSTAENDE)
check("16 Stufen", len(stufen), 16)
verhaeltnisse = [S.ID_ANTEIL(r) for r in stufen]
abstaende = [b - a for a, b in zip(verhaeltnisse, verhaeltnisse[1:])]
check("Stufen mindestens 3 % auseinander", min(abstaende) > 0.03, True)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")
```

- [ ] **Schritt 2: Test laufen lassen, Fehlschlag bestätigen**

Ausführen: `python3 tests/test_stack_spec.py`
Erwartet: `ModuleNotFoundError: No module named 'stack_spec'`

- [ ] **Schritt 3: `tools/stack_spec.py` schreiben**

```python
"""Der Vertrag von PicoStack: Steckerbelegung, Umriss, Modultypen.

Bewusst ohne KiCad-Abhaengigkeit, damit er ohne KiCad geprueft werden
kann -- und damit fremde Werkzeuge ihn lesen koennen, ohne KiCad zu
installieren.

Was hier steht, ist die Zusage an alle, die eigene Module bauen.
Aendert sich etwas davon, sind fremde Module unbrauchbar. Alles andere
im System darf sich aendern.

Grundlage: docs/superpowers/specs/2026-08-28-picostack-design.md
"""

BOARD_W = 64.0
BOARD_H = 60.0
CORNER_R = 3.0

M3_DRILL = 3.2
M3_HOLES = [(4.0, 4.0), (4.0, 56.0), (60.0, 4.0), (60.0, 56.0)]

STAPEL_ABSTAND = 15.0     # mm zwischen zwei Platinen

# --- Steckerbelegung ------------------------------------------------
# Pico-Pins 1..40. Die Nummern folgen dem Pico-Datenblatt, nicht der
# GPIO-Nummer: der Stecker traegt Pins, nicht GPIO.
RESERVIERT = (
    "I2C_SDA", "I2C_SCL",     # Bus zu den Modulen
    "FLASH_TX", "FLASH_RX",   # Bootlader der Modul-MCU
    "SEL",                    # Auswahl-Token, von Modul zu Modul
    "FLASH_MODE",             # global: Stapel im Flash-Modus
    "NOTAUS",                 # global, wired-OR, wirkt ohne Software
)

_GND = {3, 8, 13, 18, 23, 28, 33, 38}
_VERSORGUNG = _GND | {36, 37, 39, 40}    # 3V3_OUT, 3V3_EN, VSYS, VBUS


def IST_VERSORGUNG(pin):
    return pin in _VERSORGUNG


PIN_ROLLE = {}
for _p in range(1, 41):
    PIN_ROLLE[_p] = "GND" if _p in _GND else "frei"
PIN_ROLLE.update({
    36: "3V3", 37: "3V3_EN", 39: "VSYS", 40: "VBUS",
    1:  "FLASH_TX",     # GP0
    2:  "FLASH_RX",     # GP1
    4:  "SEL",          # GP2
    5:  "FLASH_MODE",   # GP3
    6:  "I2C_SDA",      # GP4
    7:  "I2C_SCL",      # GP5
    9:  "NOTAUS",       # GP6
})

# --- Modultypen -----------------------------------------------------
# 0x00 ist ungueltig (ein unbeschriebener Kennwiderstand liest 0).
# 0x80 und darueber bleibt fremden Modulen vorbehalten.
MODULTYPEN = {
    0x01: {"name": "Motor",    "kanaele": 1},
    0x10: {"name": "Dimmer1",  "kanaele": 1},
    0x11: {"name": "Dimmer3",  "kanaele": 3},
    0x12: {"name": "Dimmer4",  "kanaele": 4},
}

# --- Kennwiderstaende -----------------------------------------------
# Zwei Teiler gegen einen festen Oberwiderstand, je 16 Stufen aus der
# E24-Reihe. Die Stufen sind so gewaehlt, dass sich benachbarte
# Spannungsteiler um mehr als 3 % unterscheiden -- weit mehr als die
# Streuung von 1-%-Widerstaenden und die Aufloesung des ADC.
ID_OBEN = 10000.0
ID_WIDERSTAENDE = (
    0.0, 1000.0, 2200.0, 3300.0, 4700.0, 6800.0, 10000.0, 15000.0,
    22000.0, 33000.0, 47000.0, 68000.0, 100000.0, 150000.0, 220000.0,
    None,                      # None = unbestueckt, liest Vollausschlag
)


def ID_ANTEIL(r):
    """Spannungsanteil am ADC fuer einen Kennwiderstand."""
    if r is None:
        return 1.0
    return r / (r + ID_OBEN)
```

- [ ] **Schritt 4: Test laufen lassen, Erfolg bestätigen**

Ausführen: `python3 tests/test_stack_spec.py`
Erwartet: `alle Pruefungen bestanden`

- [ ] **Schritt 5: Committen**

```bash
git add tools/stack_spec.py tests/test_stack_spec.py
git commit -m "Vertrag als pruefbares Datenmodul: Belegung, Umriss, Modultypen"
```

---

### Aufgabe 3: Die Auswahlkette als Wahrheitstabelle

Die Kette entscheidet, welcher MCU im Reset liegt und welcher im
Bootlader steht. Ein Denkfehler darin fällt erst an der bestückten
Platine auf. Deshalb wird sie erst als Tabelle geprüft, dann in
Kupfer gegossen.

**Dateien:**
- Anlegen: `tools/kette.py`
- Anlegen: `tests/test_kette.py`

**Schnittstellen:**
- Liefert: `modul_zustand(flash_mode, sel_in) -> (reset, boot0, sel_out)`

- [ ] **Schritt 1: Den fehlschlagenden Test schreiben**

`tests/test_kette.py`:

```python
"""Prueft die Logik der Auswahlkette als Wahrheitstabelle."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "tools"))
from kette import modul_zustand

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# Ausser Flash-Modus laufen ALLE Module, unabhaengig vom Token.
# Das ist der Normalbetrieb -- wer das vergisst, baut einen Stapel,
# in dem nur ein Modul laeuft.
for sel in (0, 1):
    reset, boot0, sel_out = modul_zustand(flash_mode=0, sel_in=sel)
    check("Normalbetrieb sel=%d: kein Reset" % sel, reset, 0)
    check("Normalbetrieb sel=%d: kein Bootlader" % sel, boot0, 0)
    check("Normalbetrieb sel=%d: Token weiter" % sel, sel_out, sel)

# Im Flash-Modus liegt jedes Modul im Reset, ausser dem gewaehlten.
reset, boot0, sel_out = modul_zustand(flash_mode=1, sel_in=0)
check("Flash, nicht gewaehlt: Reset", reset, 1)
check("Flash, nicht gewaehlt: kein Bootlader", boot0, 0)
check("Flash, nicht gewaehlt: Token bleibt aus", sel_out, 0)

reset, boot0, sel_out = modul_zustand(flash_mode=1, sel_in=1)
check("Flash, gewaehlt: kein Reset", reset, 0)
check("Flash, gewaehlt: Bootlader", boot0, 1)

# Der Kern der Kette: das gewaehlte Modul gibt das Token NICHT weiter.
# Gaebe es weiter, waeren zwei Module gleichzeitig wach und wuerden
# sich auf der gemeinsamen Sendeleitung ins Wort fallen.
check("Flash, gewaehlt: Token wird angehalten", sel_out, 0)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")
```

- [ ] **Schritt 2: Test laufen lassen, Fehlschlag bestätigen**

Ausführen: `python3 tests/test_kette.py`
Erwartet: `ModuleNotFoundError: No module named 'kette'`

- [ ] **Schritt 3: `tools/kette.py` schreiben**

```python
"""Die Logik der Auswahlkette, als Wahrheitstabelle pruefbar.

Jedes Modul leitet aus zwei Eingaengen drei Signale ab:

    FLASH_MODE  global, vom Sockel
    SEL_IN      Token vom Modul darueber (beim obersten: vom Sockel)

    RESET       an den Modul-MCU (1 = im Reset gehalten)
    BOOT0       an den Modul-MCU (1 = Bootlader statt Anwendung)
    SEL_OUT     Token an das Modul darunter

Der Kniff steckt in SEL_OUT: das gewaehlte Modul gibt das Token nicht
weiter. Dadurch wandert es beim naechsten Puls genau eine Position
tiefer, und der Sockel muss nur mitzaehlen, um die Adressen zu kennen.

Ausserhalb des Flash-Modus laufen alle Module. Das ist der
Normalbetrieb und der haeufigste Fall -- er darf nicht vom Token
abhaengen.
"""


def modul_zustand(flash_mode, sel_in):
    if not flash_mode:
        # Normalbetrieb: alle laufen, das Token wird nur durchgereicht
        return 0, 0, sel_in
    if sel_in:
        # dieses Modul ist an der Reihe: wach, im Bootlader, haelt das
        # Token an
        return 0, 1, 0
    # nicht an der Reihe: im Reset, Ausgaenge hochohmig
    return 1, 0, 0
```

- [ ] **Schritt 4: Test laufen lassen, Erfolg bestätigen**

Ausführen: `python3 tests/test_kette.py`
Erwartet: `alle Pruefungen bestanden`

- [ ] **Schritt 5: Die Tabelle in Gatter übersetzen und dokumentieren**

In `hardware/bauteile.md` ergänzen: welche Gatter die drei Gleichungen
umsetzen, wie viele Bauteile das sind und was sie kosten. Erwartung
aus der Spec: ein einzelnes Doppelgatter im SMD-Gehäuse.

- [ ] **Schritt 6: Committen**

```bash
git add tools/kette.py tests/test_kette.py hardware/bauteile.md
git commit -m "Auswahlkette als Wahrheitstabelle gepruefft, Gatter benannt"
```

---

### Aufgabe 4: Das Bootlader-Protokoll auf dem Pico

**Dateien:**
- Anlegen: `firmware/sockel/an3155.py`
- Anlegen: `tests/test_an3155.py`

**Schnittstellen:**
- Liefert: `Bootlader(uart)` mit `sync()`, `get()`, `erase_all()`,
  `write(adresse, daten)`, `go(adresse)`
- Verbraucht: `stack_spec.PIN_ROLLE` für die Pin-Wahl (Aufgabe 2)

- [ ] **Schritt 1: Den fehlschlagenden Test schreiben**

Der Test läuft **ohne Hardware** gegen eine nachgebildete
Gegenstelle. Damit ist das Protokoll prüfbar, bevor ein Chip da ist.

`tests/test_an3155.py`:

```python
"""Prueft die Bootlader-Umsetzung gegen eine nachgebildete Gegenstelle."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "firmware", "sockel"))
from an3155 import Bootlader, ACK, NACK

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


class FakeUart:
    """Nimmt Bytes entgegen und antwortet nach Skript."""

    def __init__(self, antworten):
        self.gesendet = bytearray()
        self.antworten = bytearray(antworten)

    def write(self, b):
        self.gesendet += b

    def read(self, n):
        aus, self.antworten = self.antworten[:n], self.antworten[n:]
        return bytes(aus)


# --- Synchronisieren ---
u = FakeUart([ACK])
b = Bootlader(u)
check("sync meldet Erfolg", b.sync(), True)
check("sync sendet 0x7F", bytes(u.gesendet), b"\x7f")

# --- Jeder Befehl geht mit seinem Komplement raus ---
# Das ist die Pruefsumme des Protokolls: faellt ein Bit, passt das
# Komplement nicht mehr und der Chip antwortet mit NACK.
u = FakeUart([ACK, ACK])
b = Bootlader(u)
b.erase_all()
check("Loeschbefehl mit Komplement", bytes(u.gesendet[:2]), b"\x44\xbb")

# --- Schreiben: Adresse und Daten je mit XOR-Pruefsumme ---
u = FakeUart([ACK, ACK, ACK])
b = Bootlader(u)
b.write(0x08000000, b"\x01\x02\x03\x04")
g = bytes(u.gesendet)
check("Schreibbefehl mit Komplement", g[:2], b"\x31\xce")
check("Adresse gefolgt von XOR", g[2:7], b"\x08\x00\x00\x00\x08")
# Laengenbyte ist N-1, dann die Daten, dann XOR ueber Laenge und Daten
check("Laengenbyte ist N-1", g[7], 3)
check("Datenpruefsumme", g[-1], 3 ^ 1 ^ 2 ^ 3 ^ 4)

# --- NACK wird nicht verschluckt ---
# Ein Bootlader, der Fehler stillschweigend hinnimmt, schreibt halbe
# Firmware auf ein Modul und niemand merkt es.
u = FakeUart([NACK])
b = Bootlader(u)
check("NACK meldet Misserfolg", b.sync(), False)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")
```

- [ ] **Schritt 2: Test laufen lassen, Fehlschlag bestätigen**

Ausführen: `python3 tests/test_an3155.py`
Erwartet: `ModuleNotFoundError: No module named 'an3155'`

- [ ] **Schritt 3: `firmware/sockel/an3155.py` schreiben**

Vor dem Schreiben AN3155 öffnen und die Zahlenwerte abgleichen. Die
folgenden Werte sind aus dem Gedaechtnis notiert und **müssen gegen
das Dokument geprüft werden** — sie sind der wahrscheinlichste Ort für
einen stillen Fehler.

```python
"""Der USART-Bootlader der STM32, so weit PicoStack ihn braucht.

Laeuft auf dem Pico unter MicroPython und beschreibt darueber die
Modul-MCU. Absichtlich klein gehalten: synchronisieren, loeschen,
schreiben, starten -- mehr braucht das Aufspielen einer Firmware
nicht.

Die Schnittstelle ist 8 Datenbits mit gerader Paritaet und einem
Stoppbit. Jeder Befehl geht mit seinem Einerkomplement hinaus; das ist
die einzige Pruefung, die das Protokoll auf der Befehlsebene hat.

Werte nach ST AN3155.
"""

ACK = 0x79
NACK = 0x1F

SYNC = 0x7F
CMD_GET = 0x00
CMD_ERASE_EXT = 0x44
CMD_WRITE = 0x31
CMD_GO = 0x21


def _xor(daten, start=0):
    p = start
    for b in daten:
        p ^= b
    return p


class Bootlader:
    def __init__(self, uart):
        self.uart = uart

    # --- unterste Ebene ---
    def _quittung(self):
        a = self.uart.read(1)
        return len(a) == 1 and a[0] == ACK

    def _befehl(self, code):
        """Befehl samt Komplement senden und Quittung abholen."""
        self.uart.write(bytes([code, code ^ 0xFF]))
        return self._quittung()

    # --- Protokoll ---
    def sync(self):
        self.uart.write(bytes([SYNC]))
        return self._quittung()

    def get(self):
        return self._befehl(CMD_GET)

    def erase_all(self):
        if not self._befehl(CMD_ERASE_EXT):
            return False
        # 0xFFFF = Massenloeschung, Pruefsumme ist das XOR darueber
        self.uart.write(b"\xff\xff\x00")
        return self._quittung()

    def write(self, adresse, daten):
        if len(daten) > 256 or len(daten) % 4:
            raise ValueError("Block muss 1..256 Byte und durch 4 teilbar sein")
        if not self._befehl(CMD_WRITE):
            return False
        a = bytes([(adresse >> 24) & 0xFF, (adresse >> 16) & 0xFF,
                   (adresse >> 8) & 0xFF, adresse & 0xFF])
        self.uart.write(a + bytes([_xor(a)]))
        if not self._quittung():
            return False
        n = len(daten) - 1
        self.uart.write(bytes([n]) + daten + bytes([_xor(daten, n)]))
        return self._quittung()

    def go(self, adresse):
        if not self._befehl(CMD_GO):
            return False
        a = bytes([(adresse >> 24) & 0xFF, (adresse >> 16) & 0xFF,
                   (adresse >> 8) & 0xFF, adresse & 0xFF])
        self.uart.write(a + bytes([_xor(a)]))
        return self._quittung()
```

- [ ] **Schritt 4: Test laufen lassen, Erfolg bestätigen**

Ausführen: `python3 tests/test_an3155.py`
Erwartet: `alle Pruefungen bestanden`

- [ ] **Schritt 5: Die Zahlenwerte gegen AN3155 abgleichen**

Jeden Befehlscode, `ACK`, `NACK` und die Pruefsummenregel im Dokument
nachschlagen und im Modul-Docstring die Abschnittsnummer vermerken.
Weicht etwas ab: Test und Umsetzung gemeinsam korrigieren.

- [ ] **Schritt 6: Committen**

```bash
git add firmware/sockel/an3155.py tests/test_an3155.py
git commit -m "Bootlader-Protokoll AN3155 auf dem Pico, gegen Attrappe geprueft"
```

---

### Aufgabe 5: Nachweis auf dem Tisch

Der erste Schritt, der Hardware braucht — und der einzige, der die
tragende Annahme des ganzen Systems wirklich beweist.

**Voraussetzung:** ein STM32C011 (oder der in Aufgabe 1 gewählte Typ)
auf einem Adapterplättchen, ein Pico, vier Drähte.

**Dateien:**
- Anlegen: `firmware/sockel/nachweis.py`
- Anlegen: `firmware/modul/blink/` (winziges Testprogramm)
- Anlegen: `docs/nachweis-2026-08.md`

- [ ] **Schritt 1: Testprogramm für das Modul bauen**

Das kleinstmögliche Programm, dessen Wirkung man von aussen sieht: ein
Pin im Sekundentakt umschalten. Als `.bin` übersetzen — der Bootlader
kennt keine ELF-Dateien.

- [ ] **Schritt 2: Verdrahtung aufbauen**

Pico Pin 1 → MCU-RX, Pico Pin 2 → MCU-TX, Pico Pin 4 → BOOT0,
Pico Pin 5 → NRST, gemeinsame Masse, 3,3 V vom Pico.

Die Zuordnung stammt aus `stack_spec.PIN_ROLLE` — dieselben Pins, die
später der Stecker führt. Damit prüft der Aufbau nicht irgendetwas,
sondern genau den späteren Weg.

- [ ] **Schritt 3: `nachweis.py` schreiben**

```python
"""Beschreibt einen Modul-MCU vom Pico aus. Nachweis, kein Produkt.

Reihenfolge: BOOT0 hoch, Reset ausloesen, synchronisieren, loeschen,
blockweise schreiben, Reset mit BOOT0 tief -- danach laeuft die
Anwendung.
"""
from machine import Pin, UART
import time
from an3155 import Bootlader

BLOCK = 256
START = 0x08000000

uart = UART(0, baudrate=115200, bits=8, parity=0, stop=1, tx=0, rx=1)
boot0 = Pin(2, Pin.OUT)
nrst = Pin(3, Pin.OUT)


def reset(in_bootlader):
    boot0.value(1 if in_bootlader else 0)
    nrst.value(0)
    time.sleep_ms(10)
    nrst.value(1)
    time.sleep_ms(50)


def aufspielen(pfad):
    reset(in_bootlader=True)
    bl = Bootlader(uart)
    if not bl.sync():
        raise RuntimeError("keine Antwort vom Bootlader")
    if not bl.erase_all():
        raise RuntimeError("Loeschen abgelehnt")
    with open(pfad, "rb") as f:
        adresse = START
        while True:
            block = f.read(BLOCK)
            if not block:
                break
            if len(block) % 4:
                block += b"\xff" * (4 - len(block) % 4)
            if not bl.write(adresse, block):
                raise RuntimeError("Schreiben abgelehnt bei 0x%08X" % adresse)
            adresse += len(block)
    reset(in_bootlader=False)
    print("aufgespielt:", pfad)
```

- [ ] **Schritt 4: Durchführen und festhalten**

Erwartet: das Testprogramm läuft nach dem Aufspielen, der Pin blinkt.

In `docs/nachweis-2026-08.md` festhalten: Datum, Typ, Taktrate der
Schnittstelle, wie lange das Aufspielen dauert (das begrenzt später die
Startzeit des Stapels), und **jede** Abweichung vom erwarteten Ablauf.

- [ ] **Schritt 5: Den Fehlerfall prüfen**

Das Kabel zur Sendeleitung mitten im Schreiben abziehen. Erwartet: das
Programm meldet einen Fehler, statt stillschweigend weiterzulaufen. Ein
halb beschriebenes Modul ist der Fehlerfall, den die Spec als Preis
dieser Lösung benennt — er muss sichtbar sein.

- [ ] **Schritt 6: Committen**

```bash
git add firmware/sockel/nachweis.py firmware/modul/blink docs/nachweis-2026-08.md
git commit -m "Nachweis: der Pico beschreibt einen Modul-MCU ueber den ROM-Bootlader"
```

---

### Aufgabe 6: Den Vertrag lesbar machen

**Dateien:**
- Anlegen: `docs/vertrag.md`
- Ändern: `README.md`

- [ ] **Schritt 1: `docs/vertrag.md` aus dem Datenmodul erzeugen**

Ein kleines Skript liest `stack_spec.py` und schreibt daraus die
Tabellen: Steckerbelegung, Umriss, Modultyp-Nummern,
Kennwiderstandsstufen. Erzeugt statt getippt, damit Dokument und Modul
nicht auseinanderlaufen — die haeufigste Ursache dafuer, dass ein
fremdes Modul nicht passt.

- [ ] **Schritt 2: README schreiben**

Was PicoStack ist, wie ein Stapel aussieht, was fest bleibt (die fünf
Punkte aus der Spec), und wie jemand ein eigenes Modul anfängt.

- [ ] **Schritt 3: Committen**

```bash
git add docs/vertrag.md README.md tools/
git commit -m "Vertrag als Dokument, aus dem Datenmodul erzeugt"
```

---

## Was dieser Plan bewusst nicht enthält

- **Keine Leiterplatten.** Sockel, Modulsockel und Motormodul bekommen
  einen eigenen Plan, sobald Aufgabe 5 den Flash-Weg belegt hat. Drei
  Layouts um eine unbewiesene Annahme zu bauen, waere die teuerste
  Reihenfolge.
- **Keine Modul-Firmware ausser dem Blinkprogramm.** Der Registersatz
  und der sichere Zustand gehoeren in den Firmware-Plan.
- **Keine Dimmer-Varianten.** Etappe 2 der Spec.

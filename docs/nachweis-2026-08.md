# Nachweis: der Pico beschreibt einen Modul-MCU ueber den ROM-Bootlader

## Status: **NACHWEIS STEHT NOCH AUS**

Dieses Dokument ist eine Vorbereitung, keine Durchfuehrung. Es gibt
**keinen** Aufbau auf dem Tisch, der die tragende Annahme des Systems
belegt hat — dass der Pico einen Modul-MCU allein ueber dessen
ROM-Bootlader mit Firmware beschreiben kann. Grund: es liegt **kein
STM32C011 (oder Ersatztyp) auf dem Tisch vor**. Ohne Chip auf einem
Adapterplaettchen laesst sich die Verdrahtung nicht abschliessen und
`nachweis.py` nicht laufen lassen.

Was unten steht, ist der geplante Ablauf mit ausdruecklich offenen
Feldern. Niemand sollte aus diesem Dokument den Eindruck gewinnen, der
Nachweis sei erbracht — er ist es nicht. Sobald ein Chip vorhanden
ist, sind Schritt 4 (Durchfuehren und festhalten) und Schritt 5 (den
Fehlerfall pruefen) aus
`.superpowers/sdd/2026-08-28-etappe-1a-vertrag-und-nachweis/aufgabe-5-brief.md`
nachzuholen und dieses Dokument entsprechend zu ergaenzen.

## Was schon existiert

- `firmware/sockel/an3155.py` — AN3155-Bootlader-Protokoll, gegen die
  Attrappe geprueft (Aufgabe 4).
- `firmware/sockel/nachweis.py` — das Aufspiel-Programm, syntaktisch
  geprueft (`python3 -m py_compile`), **nie auf echter Hardware
  gelaufen** (laeuft unter MicroPython auf dem Pico, hier nicht
  ausfuehrbar).
- `firmware/modul/blink/README.md` — Beschreibung des Testprogramms
  fuers Modul; noch kein Quelltext, siehe dort.
- `tools/kette.py` — Kettenlogik (`modul_zustand`), gegen die
  Wahrheitstabelle geprueft (Aufgabe 3).

## Geplante Verdrahtung

**Wichtig — Abweichung von der ersten Fassung des Briefs:** der Brief
zu Aufgabe 5 nennt "Pico Pin 4 -> BOOT0" und "Pico Pin 5 -> NRST". Das
ist nach `tools/stack_spec.PIN_ROLLE` falsch benannt: Steckerpin 4
heisst `SEL`, Steckerpin 5 heisst `FLASH_MODE`. Auf der fertigen
Platine leitet ein Gatter aus SEL und FLASH_MODE erst die
Reset-/Bootlader-Auswahl (RESET, BOOT0) ab (siehe
`hardware/bauteile.md`, Abschnitt zur Auswahlkette, und
`tools/kette.py`). Dieses Gatter existiert auf dem Tischaufbau nicht —
dort haengt nur der blanke MCU auf einem Adapterplaettchen. Die
Verdrahtung unten geht deshalb **direkt** an die rohen MCU-Pins BOOT0
und NRST, nicht an SEL/FLASH_MODE. Damit der Aufbau trotzdem dieselbe
Logik prueft, die spaeter das Gatter in Kupfer ausfuehrt, berechnet
`nachweis.py::reset()` die Werte fuer BOOT0 und NRST ueber
`kette.modul_zustand(flash_mode, sel_in)`, statt sie frei zu waehlen —
siehe Docstring dort.

| Pico-Pin | Pico-GPIO | Rolle im Nachweis-Skript | MCU-Anschluss |
|---|---|---|---|
| Pin 1 | GP0 | `uart` TX (entspricht Steckerpin-Rolle `FLASH_TX`) | USART1_RX, physisch **PA12** |
| Pin 2 | GP1 | `uart` RX (entspricht Steckerpin-Rolle `FLASH_RX`) | USART1_TX, physisch **PA11** |
| Pin 4 | GP2 | `boot0` — direkt, **nicht** ueber den Steckerpin `SEL` | BOOT0, physisch **PA14** |
| Pin 5 | GP3 | `nrst` — direkt, **nicht** ueber den Steckerpin `FLASH_MODE` | NRST |
| — | GND | gemeinsame Masse | GND |
| — | 3V3 (Pin 36) | Versorgung | VDD |

TX/RX sind gekreuzt (Pico TX -> MCU RX, Pico RX -> MCU TX), wie bei
jeder UART-Punkt-zu-Punkt-Verbindung.

## Erwarteter Ablauf

1. `blink.bin` liegt vor (aus dem Hersteller-Beispielprojekt uebersetzt,
   siehe `firmware/modul/blink/README.md`).
2. `nachweis.aufspielen("blink.bin")` auf dem Pico ausfuehren:
   - `reset(flash_mode=1, sel_in=1)` haelt den MCU kurz im Reset und
     gibt ihn dann mit BOOT0=1 frei -> ROM-Bootlader startet.
   - `Bootlader.sync()` synchronisiert die Schnittstelle.
   - `Bootlader.erase_all()` loescht den Flash vollstaendig.
   - Blockweises Schreiben (256 Byte je Block) ab `0x08000000`.
   - `reset(flash_mode=0, sel_in=0)` gibt den MCU mit BOOT0=0 frei ->
     die Anwendung (blink) startet.
3. Erwartet: ein Pin des MCU schaltet im Sekundentakt um (LED oder
   Multimeter am Pin zeigt es).

## Offene Felder — nach der Durchfuehrung auszufuellen

- **Datum der Durchfuehrung:** _(offen — kein Chip vorhanden)_
- **MCU-Typ tatsaechlich verwendet:** _(offen; geplant STM32C011F6P6,
  siehe `hardware/bauteile.md`)_
- **Taktrate der Schnittstelle:** _(offen — Skript setzt 115200 Baud,
  8N1 gerade Paritaet laut `an3155.py`-Docstring; ob das in der Praxis
  synchronisiert, ist unbelegt)_
- **Dauer des Aufspielens:** _(offen — begrenzt spaeter die Startzeit
  des Stapels; noch nicht gemessen)_
- **Beobachtete Abweichungen vom erwarteten Ablauf:** _(offen)_
- **Ergebnis des Fehlerfall-Tests (Schritt 5, Sendeleitung mitten im
  Schreiben abgezogen):** _(offen — Test nicht durchgefuehrt)_

## Was fehlt, um die offenen Felder zu schliessen

- Ein STM32C011F6P6 (oder der in Aufgabe 1 gewaehlte Ersatztyp) auf
  einem Adapterplaettchen.
- Ein uebersetztes `blink.bin` nach `firmware/modul/blink/README.md`.
- Ein Pico mit `firmware/sockel/an3155.py`, `tools/kette.py` und
  `firmware/sockel/nachweis.py` im Dateisystem (MicroPython-Import
  verlangt, dass alle drei im selben Suchpfad liegen).

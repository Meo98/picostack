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
- `tools/kette.py` — Kettenlogik: `modul_zustand()` (Gatter) gegen die
  Wahrheitstabelle geprueft, `Modul`/`kette_takten()` (Schieberegister)
  gegen eine Simulation aus drei Modulen (Aufgabe 3).

## Wie riskant ist die offene Annahme?

Der Status oben — **Nachweis steht noch aus** — bleibt unverändert. Was
folgt, ist keine Abschwächung davon, sondern eine Einordnung: Wie oft
ist "ein Mikrocontroller beschreibt einen STM32 über dessen
ROM-USART-Bootlader" schon gemacht worden, und was geht dabei
erfahrungsgemäss schief? Externe Berichte ersetzen den eigenen
Tischnachweis nicht — sie belegen nichts über *unseren* Aufbau, unsere
Verdrahtung, unser Timing. Sie senken nur die Wahrscheinlichkeit, dass
das Verfahren an sich ein Sackgassen-Ansatz ist.

### Das Verfahren ist verbreitet

- **[stm32flash](https://github.com/ARMinARM/stm32flash)** — der
  meistzitierte quelloffene Host für AN3155/AN2606, plattformübergreifend
  (POSIX, Windows, Android), UART und I²C. Ursprung auf SourceForge, auf
  GitHub u.a. bei ARMinARM gespiegelt.
- **[stm32-hotspot/stm32-host-programmer-usart](https://github.com/stm32-hotspot/stm32-host-programmer-usart)**
  — ST selbst (offizielle GitHub-Organisation `stm32-hotspot`) zeigt hier,
  wie ein STM32 (Nucleo-L4R5ZI) einen zweiten STM32 über USART nach
  AN3155/AN2606 beschreibt. Kein Pico, aber dieselbe Rolle: ein
  Mikrocontroller als Bootlader-Host für einen anderen.
- **[joeferner/pi-stm32-uart-bootloader](https://github.com/joeferner/pi-stm32-uart-bootloader)**
  — ein Raspberry Pi (getestet auf Pi 3, TypeScript/Node.js) schaltet
  BOOT0, Reset und UART, um einen STM32 zu beschreiben. Kein Pico und
  kein reiner Mikrocontroller-Host, aber dieselbe Pin-Choreografie
  (BOOT0/Reset setzen, dann UART), die `nachweis.py` auch fährt.

Eine dedizierte "RP2040 als AN3155-Host"-Referenz wurde nicht gefunden;
das Verfahren selbst (Host misst Baudrate über 0x7F, sendet Befehl +
Komplement, wertet ACK/NACK aus) ist aber MCU-Host-agnostisch und in
den drei Projekten oben mehrfach unabhängig umgesetzt.

### Bekannte Fallstricke aus ST-Community und Projektdokumentation

- **0x7F wird gemessen, nicht nur empfangen, und nur direkt nach
  Reset.** AN3155 selbst beschreibt das Verfahren: "The duration of
  this data frame is measured using the Systick timer. The count value
  of the timer is then used to calculate the corresponding baud rate
  factor" (AN3155 Rev 16, Abschnitt 1, S. 5/50). Ein Nutzer im
  ST-Forum bestätigt, dass das eine Einmal-Messung ist: "9600 8E1
  should work on all platforms. I[t] should be relatively robust, but
  is a one-shot deal, and will be sensitive to even very brief
  glitches/pulses." (community.st.com,
  [STM32L151 bootloader autobaud issues](https://community.st.com/t5/stm32-mcus-products/stm32l151-bootloader-autobaud-issues/td-p/480672)).
  Störimpulse auf der Leitung während der Synchronisation lassen die
  Erkennung scheitern — ein Reset ist dann der einzige Ausweg.
- **Gerade Parität ist die Vorgabe** — AN3155 Rev 16, Abschnitt
  "Communication safety" (S. 8/50): "UART: parity check active (even
  parity)". Vereinzelt gibt es dokumentierte Ausnahmen: laut den
  durchsuchten Auszügen aus AN3155 Rev 21 verwenden STM32WB0 und
  STM32WL3x keine Parität. **Nicht unabhängig nachgelesen** — dieser
  Punkt stammt aus der Websuche über den PDF-Inhalt, nicht aus einer
  selbst geöffneten Seite; für den hier geplanten Chip (STM32C0)
  bleibt gerade Parität die dokumentierte Vorgabe.
- **Handschlag gelingt, erster Befehl NACK.** Klassisches Fehlerbild im
  ST-Forum: "The initial 0x7F sync byte received an ACK (0x79), but
  every subsequent command returned a NACK" — als Ursache bestätigt
  sich dort ein Framing-/Paritätsfehler: "The bootloader expects 8E1."
  (community.st.com,
  [Bootloader NACK](https://community.st.com/t5/stm32-mcus-products/bootloader-nack/td-p/504283)).
- **Kurze Pausen zwischen Befehlsbytes.** Ein Nutzer, dessen
  MCU-zu-MCU-Verbindung (STM32-zu-STM32, keine Terminal-Software)
  ohne Pause NACKs erzeugte: "After waiting for about 22ms between
  each byte transfer (inter byte delay) we're getting proper response
  of all the commands." (community.st.com,
  [Inter Byte Delay while sending Bootloader commands](https://community.st.com/t5/stm32-mcus-products/inter-byte-delay-while-sending-bootloader-commands-on/td-p/346555)).
  22 ms ist ein Extremfall aus einem einzelnen Bericht, kein
  allgemeiner Richtwert — aber ein Hinweis, dass `nachweis.py` bei
  NACKs auch das Timing zwischen Bytes prüfen sollte, nicht nur
  Verdrahtung und Parität.
- **BOOT0-Pin gilt als der verlässlichere Weg gegenüber dem
  Software-Sprung aus der Anwendung heraus.** Kein einzelner Beleg
  sagt das direkt so, aber die ST-Community-Anleitung für den
  Software-Sprung listet, was dafür alles sauber laufen muss:
  Peripherie deinitialisieren, Interrupts sperren, Takt zurücksetzen
  (`HAL_RCC_DeInit()`), den Stack-Pointer auf die Bootlader-Adresse
  umlegen, den Watchdog entschärfen — und der Artikel nennt
  Gerätefamilien (STM32F0, einige STM32L0), auf denen der Sprung gar
  nicht unterstützt wird (community.st.com,
  [How to jump to system bootloader from application code on STM32 microcontrollers](https://community.st.com/t5/stm32-mcus/how-to-jump-to-system-bootloader-from-application-code-on-stm32/ta-p/49424)).
  PicoStack nutzt ohnehin den BOOT0-Pin direkt (siehe Verdrahtung
  unten) und ist von dieser Fehlerklasse damit nicht betroffen — das
  bestätigt nur, dass diese Wahl richtig war, nicht dass sie den
  eigenen Nachweis ersetzt.

### Einordnung

Nichts davon ist beim Aufbau am Tisch überprüft. Was es zeigt: das
Verfahren selbst ist nicht das Risiko — es ist gut begangen, die
Fallstricke sind bekannt und meist auf Parität, Timing und
Störimpulse zurückzuführen, nicht auf einen grundsätzlichen Fehler im
Ansatz. Das Risiko liegt in der *eigenen* Umsetzung: Leitungsführung,
Timing von `nachweis.py`, und ob der STM32C0 sich wie in AN3155
beschrieben verhält. Nur der Tischnachweis mit echtem Chip kann das
klären.

## Geplante Verdrahtung

**Wichtig — Abweichung von der ersten Fassung des Briefs:** der Brief
zu Aufgabe 5 nennt "Pico Pin 4 -> BOOT0" und "Pico Pin 5 -> NRST". Das
ist nach `tools/stack_spec.PIN_ROLLE` falsch benannt: Steckerpin 4
heisst `SEL`, Steckerpin 5 heisst `FLASH_MODE`. Auf der fertigen
Platine haelt ein D-Flipflop je Modul die Auswahl (`Q`, getaktet ueber
`SEL_CLK`), und ein Gatter leitet daraus zusammen mit FLASH_MODE erst
die Reset-/Bootlader-Auswahl (RESET, BOOT0) ab (siehe
`hardware/bauteile.md`, Abschnitt zur Auswahlkette, und
`tools/kette.py`). Dieses Gatter existiert auf dem Tischaufbau nicht —
dort haengt nur der blanke MCU auf einem Adapterplaettchen. Die
Verdrahtung unten geht deshalb **direkt** an die rohen MCU-Pins BOOT0
und NRST, nicht an SEL/FLASH_MODE. Damit der Aufbau trotzdem dieselbe
Logik prueft, die spaeter das Gatter in Kupfer ausfuehrt, berechnet
`nachweis.py::reset()` die Werte fuer BOOT0 und NRST ueber
`kette.modul_zustand(flash_mode, q)`, statt sie frei zu waehlen — `q`
ist am Tisch von Hand gesetzt, weil es dort weder Flipflop noch zweites
Modul gibt. Siehe Docstring dort.

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
   - `reset(flash_mode=1, q=1)` haelt den MCU kurz im Reset und
     gibt ihn dann mit BOOT0=1 frei -> ROM-Bootlader startet.
   - `Bootlader.sync()` synchronisiert die Schnittstelle.
   - `Bootlader.erase_all()` loescht den Flash vollstaendig.
   - Blockweises Schreiben (256 Byte je Block) ab `0x08000000`.
   - `reset(flash_mode=0, q=0)` gibt den MCU mit BOOT0=0 frei ->
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

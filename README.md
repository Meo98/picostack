# PicoStack

Ein Baukasten für stapelbare Platinen auf dem Raspberry Pi Pico — ein einfacher, offener Standard damit Fremde eigene Module bauen können.

## Wie sieht ein Stapel aus?

Ein PicoStack-System ist ein vertikaler Turm:

```
        Pico (Sockel)           <- zuoberst: USB und Antenne zeigen frei nach oben
┌─────────────────────┐
│  (15 mm Abstand)    │
├─────────────────────┤
│   Modul 2 (z.B.     │
│   Dimmer)           │
├─────────────────────┤
│  (15 mm Abstand)    │
├─────────────────────┤
│   Modul 1 (z.B.     │
│   Motor)            │
└─────────────────────┘
```

Jede Platine ist **64 × 60 mm** mit Ecken von **3 mm** Radius und vier M3-Befestigungslöchern. Ein Signalstecker auf jeder Platine verbindet sie nach unten, ein zweiter (oder einer auf dem Sockel) nach oben.

Der Pico sitzt als Sockel zuoberst im Stapel. Er ist der Wirt: Die Module sind dafür da, um Funktionen (Motoren, Dimmer, Sensoren) zu steuern; der Pico koordiniert sie über einen gemeinsamen I²C-Bus und I/O-Pins.

## Was bleibt fest — der Vertrag

Damit ein fremdes Modul in jeden Stapel passt, halten wir an fünf Dingen fest:

1. **Umriss, Lochbild und Steckerpositionen**  
   Siehe [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Umriss".

2. **Belegung beider Stecker**  
   Der Signalstecker ist immer 2×20 mit Pico-Pinbild. Die Rollen der Pins (I²C, Stromversorgung, Ein-/Ausgänge für den Bootlader und Notaus) sind dokumentiert in [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Steckerbelegung". Alle anderen Pins stehen dem Modul frei zur Verfügung.

3. **Nummernvergabe für Modultypen**  
   Jeder Modultyp hat eine eindeutige 8-Bit-Nummer. Die ist in einem I²C-Register auf der Platine fix verdrahtet, damit der Pico sofort weiß, was er vor sich hat. Siehe [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Modultypen". Nummern ab `0x80` sind für fremde Module reserviert.

4. **Ein gemeinsamer Registersatz auf dem Bus**  
   Jedes Modul beantwortet auf seiner I²C-Adresse folgende Register (Offsets ab 0):
   - **0x00** — Typ (read-only): die 8-Bit-Nummer des Modultyps
   - **0x01** — Version (read-only): Firmware-Version des Moduls
   - **0x02** — Zustand (read/write): Bitzustand des Moduls (Motor an/aus, LED-Kanäle aktiv, …)
   - **0x03** — Sicherer Zustand (read-only): der Wert auf den Register 0x02 zurückfällt, wenn 500 ms kein gültiger Befehl kommt

   Ab Register **0x04** ist Platz für modultyp-spezifische Register (Temperatur, Stromlimit, PWM-Wert, …).

5. **Regel für den sicheren Zustand: Timeout nach 500 ms**  
   Kommt auf dem I²C-Bus 500 Millisekunden lang kein gültiger Befehl an ein Modul, setzt es sein eigenes `Zustand`-Register auf den `Sicheren Zustand` zurück. Das heißt konkret: Motor aus, alle Dimmer auf 0, Heizung aus — alles, das Streckung oder Risiko bringt, geht in den Ruhezustand. Das ist die Schutzregel, damit ein abgestürzter Pico oder ein ausgefallener Bus nicht zu einer Runaway-Platine führt.

## Wie fängt man ein eigenes Modul an?

1. **Vertrags-Checkliste durchgehen**  
   Lies [`docs/vertrag.md`](docs/vertrag.md) und überzeugte dich, dass du alle Einschränkungen verstanden hast: Umriss, Stecker, I²C-Register, Timeout.

2. **Lochbild auf deine Platine zeichnen**  
   64 × 60 mm, Ecken 3 mm gerundet, vier M3-Bohrungen an (4, 4), (4, 56), (60, 4), (60, 56). Das geht mit KiCAD, Fusion 360, Plasticity, oder was du magst.

3. **Stecker platzieren und Pins durchleiten**  
   Ein 2×20-Stecker oben (Buchse) und einer unten (Stift), in der Platine verbunden, damit die Signale durchgehen und Fremde unter das Modul ein weiteres Module drunter bauen können.

4. **Deine Schaltung auslegen**  
   Was ist deine Aufgabe? Motor treiben? Kanäle dimmen? Sensoren auslesen? Das ist deine Auswahl. Nimm dir Platz auf den 64 × 60 mm und nutze die freien Pins.

5. **I²C-Adresse und Typ-Widerstand festlegen**  
   Auf deinem Modul hängt ein Widerstand zwischen 3V3 und GND, der mit anderen Modulen in Serie dein Modul eindeutig macht. Siehe [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Kennwiderstände". Der Pico misst das Spannungsteiler-Verhältnis und weiß dann, dass **du** diesen Slot hast. (Das ist die I²C-Adresse: nicht fest verdrahtet, sondern aus dem Widerstand gemessen, damit Du nicht mehrere Picos brauchst, um alle Modul-Varianten zu bauen.)

6. **Firmware schreiben**  
   Dein Modul läuft auf einem kleinen MCU (STM32, RP2040, …). Der muss die I²C-Protokolle auf den Registern verstehen: Typen-Abfrage, Zustand lesen/schreiben, Timeout zählen.

7. **Testen, dann teilen**  
   Fahr deinen Stapel hoch, rede mit dem Modul über I²C vom Pico aus, und schreib auf, was du gelernt hast. Wenn du magst, mach einen Git-Branch oder ein Repo und teil es mit Anderen.

## Warnung: Das ist eine Entwurfsetappe

Diese Etappe setzt den **Vertrag** und die erste **Logik** um. Aber es gibt zwei große Dinge, die **noch nicht gebaut** sind:

### 1. Der Nachweis steht noch aus

Der Vertrag besagt, dass der Pico einen Modul-MCU über dessen ROM-Bootlader beschreiben kann. Das ist noch nicht auf echter Hardware erprobt. Der Grund: Es gibt **noch keinen STM32 auf einem Adapterplaettchen** zum Testen.

Details und was dann noch zu tun ist: siehe [`docs/nachweis-2026-08.md`](docs/nachweis-2026-08.md). Es ist nicht euer Projekt — but if you read this and want to help, get in touch.

**Das Fazit:** Nimm an, dass die Schnittstellen so funktionieren wie dokumentiert, aber baue nicht auf Garantie. Wenn du ein Modul bauen möchtest, fang mit Schritt 1 (Vertrag lesen) an und schreib mir, falls Fragen auftauchen.

### 2. Es gibt noch keine Platinen

Der Sockel (Pico-Träger mit den Steckersockeln), die Modulsockel (die 2×20 oben und unten) und ein Motormodul als Testfall — das alles ist eine **nächste Etappe**. Aktuell sind das nur Datenmodule, geprüfte Logik, und dieser Vertrag als Text.

Wenn du schon deine Schaltung zeichnest: Leg die Ecken, Löcher und Stecker unten an, dann kannst du sofort mit Produktionspartner reden, sobald der Sockel fertig ist.

## Weitere Lektüre

- [`tools/stack_spec.py`](tools/stack_spec.py) — der Vertrag als Python-Datenmodul (Steckerbelegung, Umriss, Lochbild, Modultypen, Kennwiderstände)
- [`tools/kette.py`](tools/kette.py) — die Logik der Bootlader-Auswahlkette (geprüft gegen Wahrheitstabelle)
- [`hardware/bauteile.md`](hardware/bauteile.md) — die Bauteilwahl für die Auswahlkette
- [`firmware/sockel/an3155.py`](firmware/sockel/an3155.py) — das AN3155-Bootlader-Protokoll (gegen die Attrappe geprüft)
- [`firmware/sockel/nachweis.py`](firmware/sockel/nachweis.py) — das Programm für den Tischnachweis
- [`firmware/modul/blink/README.md`](firmware/modul/blink/README.md) — ein Testprogramm fürs erste Modul

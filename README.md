# PicoStack

Ein Baukasten für stapelbare Platinen auf dem Raspberry Pi Pico — ein einfacher, offener Standard damit Fremde eigene Module bauen können.

## Status: Entwurfsetappe

Diese Etappe setzt den **Vertrag** und die erste **Logik** um. Aber es gibt zwei große Dinge, die **noch nicht gebaut** sind:

### Der Nachweis steht noch aus

Der Vertrag besagt, dass der Pico einen Modul-MCU über dessen ROM-Bootlader beschreiben kann. Das ist noch nicht auf echter Hardware erprobt. Der Grund: Es gibt **noch keinen STM32 auf einem Adapterplättchen** zum Testen.

Details und was dann noch zu tun ist: siehe [`docs/nachweis-2026-08.md`](docs/nachweis-2026-08.md). Wer das liest und helfen will, kann mich kontaktieren.

**Das Fazit:** Nimm an, dass die Schnittstellen so funktionieren wie dokumentiert, aber baue nicht auf Garantie. Wenn du ein Modul bauen möchtest, fang mit Schritt 1 (Vertrag lesen) an und schreib mir, falls Fragen auftauchen.

### Es gibt noch keine Platinen

Der Sockel (Pico-Träger mit den Steckersockeln), die Modulsockel (die 2×20 oben und unten) und ein Motormodul als Testfall — das alles ist eine **nächste Etappe**. Aktuell sind das nur Datenmodule, geprüfte Logik, und dieser Vertrag als Text.

Wenn du schon deine Schaltung zeichnest: Leg die Ecken, Löcher und Stecker unten an, dann kannst du sofort mit Produktionspartner reden, sobald der Sockel fertig ist.

---

## Wie sieht ein Stapel aus?

Ein PicoStack-System ist ein vertikaler Turm:

```
        Pico (Sockel)           <- zuoberst: USB und Antenne zeigen frei nach oben
┌─────────────────────┐
│  (Abstand siehe     │
│   docs/vertrag)     │
├─────────────────────┤
│   Modul 1 (z.B.     │
│   Motor)            │
├─────────────────────┤
│  (Abstand siehe     │
│   docs/vertrag)     │
├─────────────────────┤
│   Modul 2 (z.B.     │
│   Dimmer)           │
└─────────────────────┘
```

Jede Platine hat einen definierten Umriss, vier M3-Befestigungslöcher, Kantenradius und Abstand zum nächsten Modul — alle Details siehe [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Umriss". Ein Signalstecker auf jeder Platine verbindet sie nach unten, ein zweiter (oder einer auf dem Sockel) nach oben.

Der Pico sitzt als Sockel zuoberst im Stapel. Er ist der Wirt: Die Module sind dafür da, um Funktionen (Motoren, Dimmer, Sensoren) zu steuern; der Pico koordiniert sie über einen gemeinsamen I²C-Bus und I/O-Pins.

## Was bleibt fest — der Vertrag

Damit ein fremdes Modul in jeden Stapel passt, halten wir an fünf Dingen fest:

1. **Umriss, Lochbild und Steckerpositionen**  
   Umriss, Lochbild und Bohrdurchmesser stehen in [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Umriss". Die **Steckerpositionen sind noch offen** — sie stehen weder im Vertrag noch im Datenmodul und werden erst mit den ersten Platinen festgelegt (Etappe 1b). Wer heute schon zeichnet, hält die Fläche entlang der beiden 2×20-Reihen frei.

2. **Belegung beider Stecker**  
   Der Signalstecker ist immer 2×20 mit Pico-Pinbild. Die Rollen seiner Pins (I²C, Stromversorgung, Ein-/Ausgänge für den Bootlader und die Auswahlkette, Notaus) sind dokumentiert in [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Steckerbelegung". Alle anderen Pins stehen dem Modul frei zur Verfügung. Die Belegung des **Leistungssteckers ist noch offen**: entschieden ist bisher nur, dass es ihn gibt und dass er 24 V und Masse führt. Bauteil, Position und Zahl der Kontakte kommen in Etappe 1b.

3. **Nummernvergabe für Modultypen**  
   Jeder Modultyp hat eine eindeutige 8-Bit-Nummer. Sie steckt in **zwei Kennwiderständen** auf der Platine: zwei Spannungsteiler gegen einen gemeinsamen festen Oberwiderstand, je 16 Stufen — zusammen 256 Nummern. Gelesen werden sie nicht vom Pico, sondern vom **Modul-MCU selbst**: der Pico schreibt zuerst ein winziges Erkennungsprogramm, das die beiden Teiler misst und den Typ meldet, und schickt danach die passende Firmware. Stufenwerte und die Schwelle, ab der fremde Module Nummern reserviert haben, stehen in [`docs/vertrag.md`](docs/vertrag.md), Abschnitte "Kennwiderstaende" und "Modultypen".  
   Die **I²C-Adresse** kommt nicht von den Widerständen, sondern aus der Auswahlkette: der Sockel schiebt die Auswahl von oben nach unten durch den Stapel und zählt dabei mit. Deine Adresse ist deine Position im Stapel.

4. **Ein gemeinsamer Registersatz auf dem Bus**  
   Jedes Modul beantwortet auf seiner I²C-Adresse einen kleinen gemeinsamen Registersatz: Typ, Firmware-Version, Zustand und sicherer Zustand; dahinter Platz für typeigene Register (Temperatur, Stromlimit, PWM-Wert, …).  
   **Entwurf für Etappe 1c, noch nicht festgelegt:** Die folgenden Offsets stehen bisher nirgends sonst — weder in der Spezifikation noch im Datenmodul. Sie werden zusammen mit der Firmware beschlossen und können sich bis dahin ändern:
   - **0x00** — Typ (read-only): die 8-Bit-Nummer des Modultyps
   - **0x01** — Version (read-only): Firmware-Version des Moduls
   - **0x02** — Zustand (read/write): Bitzustand des Moduls (Motor an/aus, LED-Kanäle aktiv, …)
   - **0x03** — Sicherer Zustand (read-only): der Wert, auf den Register 0x02 zurückfällt, wenn 500 ms kein gültiger Befehl kommt
   - ab **0x04** — modultyp-spezifische Register

5. **Regel für den sicheren Zustand: Timeout nach 500 ms**  
   Kommt auf dem I²C-Bus 500 Millisekunden lang kein gültiger Befehl an ein Modul, setzt es sein eigenes `Zustand`-Register auf den `Sicheren Zustand` zurück. Das heisst konkret: Motor aus, alle Dimmer auf 0, Heizung aus — alles, was Bewegung oder Risiko bringt, geht in den Ruhezustand. Das ist die Schutzregel, damit ein abgestürzter Pico oder ein ausgefallener Bus nicht zu einer Runaway-Platine führt.

## Wie fängt man ein eigenes Modul an?

1. **Vertrags-Checkliste durchgehen**  
   Lies [`docs/vertrag.md`](docs/vertrag.md) und überzeuge dich, dass du alle Einschränkungen verstanden hast: Umriss, Stecker, I²C-Register, Timeout, und die Auflagen an die Modulfirmware.

2. **Lochbild auf deine Platine zeichnen**  
   Nutze die genauen Masse und Bohrpositionen aus [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Umriss". Das geht mit KiCAD, Fusion 360, Plasticity, oder was du magst.

3. **Stecker platzieren und Pins durchleiten**  
   Ein 2×20-Stecker oben (Buchse) und einer unten (Stift), in der Platine verbunden, damit die Signale durchgehen und Fremde unter dein Modul ein weiteres bauen können.

4. **Deine Schaltung auslegen**  
   Was ist deine Aufgabe? Motor treiben? Kanäle dimmen? Sensoren auslesen? Das ist deine Auswahl. Nutze die Fläche (siehe [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Umriss") und die freien Pins auf dem Stecker (siehe Abschnitt "Steckerbelegung" dort).

5. **Kennwiderstände für deinen Modultyp festlegen**  
   Zwei Widerstände auf deinem Modul bilden je einen Spannungsteiler gegen einen festen Oberwiderstand; die beiden Stufen zusammen ergeben die Nummer deines Modultyps. Gemessen werden sie vom MCU auf deinem eigenen Modul, nicht vom Pico. Siehe [`docs/vertrag.md`](docs/vertrag.md), Abschnitt "Kennwiderstaende". Die **I²C-Adresse musst du nicht festlegen** — die vergibt der Sockel über die Auswahlkette, nach deiner Position im Stapel.

6. **Firmware schreiben**  
   Dein Modul läuft auf einem kleinen MCU (STM32, RP2040, …). Der muss die I²C-Protokolle auf den Registern verstehen: Typen-Abfrage, Zustand lesen/schreiben, Timeout zählen. Und er muss sich an die Auflagen aus [`docs/vertrag.md`](docs/vertrag.md) halten — vor allem: die gemeinsame Sendeleitung zum Pico ausserhalb des Flash-Modus nicht treiben.

7. **Testen, dann teilen**  
   Fahr deinen Stapel hoch, rede mit dem Modul über I²C vom Pico aus, und schreib auf, was du gelernt hast. Wenn du magst, mach einen Git-Branch oder ein Repo und teil es mit Anderen.

## Weitere Lektüre

- [`docs/vertrag.md`](docs/vertrag.md) — der Vertrag als Dokument: Umriss, Lochbild, Steckerbelegung, Modultypen, Kennwiderstände, Auflagen an die Modulfirmware. Erzeugt aus dem Datenmodul, nicht von Hand gepflegt
- [`tools/stack_spec.py`](tools/stack_spec.py) — derselbe Vertrag als Python-Datenmodul, die Quelle aller Zahlen
- [`tools/kette.py`](tools/kette.py) — die Logik der Auswahlkette: Schieberegister und Gatterlogik, geprüft gegen eine Wahrheitstabelle und gegen eine Simulation aus drei Modulen
- [`hardware/bauteile.md`](hardware/bauteile.md) — die belegte Bauteilwahl: Modul-MCU, Bootlader-Pins, Pin-Zustand nach Reset, 3,3-V-Budget, Leistungsstecker und die Bauteile der Auswahlkette. Jede Angabe mit Quelle oder ausdrücklich als offen gekennzeichnet
- [`firmware/sockel/an3155.py`](firmware/sockel/an3155.py) — das AN3155-Bootlader-Protokoll (nur gegen eine Attrappe geprüft)
- [`firmware/sockel/nachweis.py`](firmware/sockel/nachweis.py) — das Programm für den Tischnachweis (nie auf Hardware gelaufen)
- [`firmware/modul/blink/README.md`](firmware/modul/blink/README.md) — ein Testprogramm fürs erste Modul

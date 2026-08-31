# PicoStack — der Vertrag

Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.

## Status

Die Zusagen rund um das Flashen -- die Leitungen `FLASH_TX`, `FLASH_RX`, `SEL`, `SEL_CLK` und `FLASH_MODE` (SEL seit 2026-08-31 auf dem eigenen Kettenstecker, alle anderen auf dem 2x20-Stapelstecker) und alles, was daran haengt -- ruhen auf einer Annahme, die noch **nicht auf Hardware belegt** ist: dass der Pico einen Modul-MCU ueber dessen ROM-Bootlader wirklich beschreiben kann. Geprueft ist bisher nur das Protokoll gegen eine Attrappe, nicht gegen echtes Silizium. Stand und offene Schritte: `docs/nachweis-2026-08.md`.

## Umriss

64.0 x 60.0 mm, Ecken 3.0 mm gerundet, 13.0 mm zwischen den Platinen.

| M3-Bohrung | x | y | Bohrdurchmesser |
|---|---|---|---|
| 1 | 4.0 | 4.0 | 3.2 |
| 2 | 4.0 | 56.0 | 3.2 |
| 3 | 60.0 | 4.0 | 3.2 |
| 4 | 60.0 | 56.0 | 3.2 |

## Steckerbelegung

| Pin | Rolle |
|---|---|
| 1 | FLASH_TX |
| 2 | FLASH_RX |
| 3 | GND |
| 5 | FLASH_MODE |
| 6 | I2C_SDA |
| 7 | I2C_SCL |
| 8 | GND |
| 9 | NOTAUS |
| 10 | SEL_CLK |
| 13 | GND |
| 18 | GND |
| 23 | GND |
| 28 | GND |
| 33 | GND |
| 36 | 3V3 |
| 37 | 3V3_EN |
| 38 | GND |
| 39 | VSYS |
| 40 | VBUS |

Alle nicht aufgefuehrten Pins gehen unveraendert durch und stehen Modulen frei zur Verfuegung.

## Stapelstecker und Kettenstecker

Der 2x20-Signalstecker (Steckerbelegung oben) ist ein **Stapelstecker**: Buchse mit durchgehendem Stift (Stapelstecker), 2x20, 2,54 mm. Bauteil: LCSC `C35165`, Gehaeusehoehe 8.50 mm, Stiftlaenge unterhalb des Gehaeuses 12.46 mm. Quelle: hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31).

Einzige Ausnahme ist die Auswahlkette (`SEL`): sie muss von Modul zu Modul aufgetrennt werden (Schieberegister, `tools/kette.py`) und ist deshalb kein Pin des Stapelsteckers mehr. Sie laeuft ueber einen eigenen, zweipoligen **Kettenstecker** (Buchse oben / Stiftleiste unten (auftrennbar), 1x2, 2,54 mm): traegt SEL (Auswahlkette) und eine GND daneben. Buchse LCSC `C541849`, Stiftleiste LCSC `C492401`. Quelle: hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31).

| Pin (Kettenstecker) | Rolle |
|---|---|
| 1 | SEL |
| 2 | GND |

## Auflagen an die Modulfirmware

- Ausserhalb des Flash-Modus darf ein Modul die Leitung FLASH_RX nicht treiben. FLASH_RX ist der Empfangspin des Pico und damit die gemeinsame Sendeleitung aller Module. Im Normalbetrieb sind alle Module gleichzeitig wach; treibt mehr als eines diese Leitung, fallen sie einander ins Wort und koennen einander im Gegentakt beschaedigen. Senden darf ein Modul nur, solange es ueber die Auswahlkette ausgewaehlt ist (FLASH_MODE = 1 und das eigene Flipflop Q = 1). Sonst bleibt der Pin hochohmig.

## Modultypen

| Nummer | Name | Kanaele |
|---|---|---|
| 0x01 | Motor | 1 |
| 0x10 | Dimmer1 | 1 |
| 0x11 | Dimmer3 | 3 |
| 0x12 | Dimmer4 | 4 |

Nummern ab `0x80` bleiben fremden Modulen vorbehalten.

## Kennwiderstaende

| Stufe | Widerstand | Spannungsanteil |
|---|---|---|
| 0 | 0 | 0.000 |
| 1 | 680 | 0.064 |
| 2 | 1500 | 0.130 |
| 3 | 2200 | 0.180 |
| 4 | 3300 | 0.248 |
| 5 | 4700 | 0.320 |
| 6 | 6200 | 0.383 |
| 7 | 7500 | 0.429 |
| 8 | 10000 | 0.500 |
| 9 | 13000 | 0.565 |
| 10 | 16000 | 0.615 |
| 11 | 22000 | 0.688 |
| 12 | 30000 | 0.750 |
| 13 | 43000 | 0.811 |
| 14 | 68000 | 0.872 |
| 15 | 150000 | 0.938 |

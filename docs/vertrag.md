# PicoStack — der Vertrag

Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.

## Umriss

64.0 x 60.0 mm, Ecken 3.0 mm gerundet, 15.0 mm zwischen den Platinen.

| M3-Bohrung | x | y |
|---|---|---|
| 1 | 4.0 | 4.0 |
| 2 | 4.0 | 56.0 |
| 3 | 60.0 | 4.0 |
| 4 | 60.0 | 56.0 |

## Steckerbelegung

| Pin | Rolle |
|---|---|
| 1 | FLASH_TX |
| 2 | FLASH_RX |
| 3 | GND |
| 4 | SEL |
| 5 | FLASH_MODE |
| 6 | I2C_SDA |
| 7 | I2C_SCL |
| 8 | GND |
| 9 | NOTAUS |
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

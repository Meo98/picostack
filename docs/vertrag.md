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
| 4 | SEL_OUT |
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
| 30 | RUN |
| 33 | GND |
| 35 | ADC_VREF |
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

## Wo die Stecker sitzen

Alle Masse in mm, Ursprung linke obere Ecke, x nach rechts, y nach unten. Diese Lage gilt fuer **jede** Platine im Stapel -- der Stapelstecker der Sockelplatine steht senkrecht ueber dem jedes Moduls, Ketten- und Leistungsstecker ebenso. Wer sie verschiebt, macht alle bereits gebauten Module unbrauchbar.

| Stecker | Zweck | Mitte x | Mitte y | Drehung | belegte Flaeche (x0 y0 x1 y1) |
|---|---|---|---|---|---|
| stapel | 2x20-Stapelstecker, Pico-Pinbild (PIN_ROLLE) | 32.125 | 11.725 | 90 Grad | 6.22 8.68 58.03 14.77 |
| kette | zweipoliger Kettenstecker, SEL + GND (STECKER_KETTE) | 12.5 | 4.025 | 0 Grad | 10.73 0.98 14.27 7.07 |
| leistung | 2x2-Leistungsstecker, 24 V und GND je doppelt | 58.775 | 43.275 | 0 Grad | 55.73 40.23 61.82 46.32 |

Die belegte Flaeche ist der Hof (F.CrtYd) des Footprints nach der Drehung. Ketten- und Leistungsstecker bestehen auf jedem Modul aus zwei Haelften (Buchse oben, Stiftleiste unten); beide Haelften belegen **denselben** Platz, sonst treffen sie sich im Stapel nicht.

Der Pico sitzt nur auf der Sockelplatine, mit Mitte (27.55 | 27.11), Drehung 90 Grad, Flaeche 0.63 15.57 54.48 38.65. Unter seiner WLAN-Antenne liegt der Sperrbereich 44.43 20.01 53.43 34.21 (9.0 x 14.2 mm) -- dort darf kein Kupfer und kein Bauteil liegen (Raspberry Pi Pico W Datasheet, Release 7, Abschnitt 2.2.1 "Keep-out area": Ausschnitt 14 x 9 mm).

Um jede M3-Bohrung bleibt ein Freihaltebereich von 7.0 mm Durchmesser fuer Schraubenkopf und Abstandsbolzen frei.

Das Lochbild ist punktsymmetrisch -- ein Modul laesst sich um 180 Grad verdreht anschrauben. Die Steckerlage ist deshalb bewusst unsymmetrisch: verdreht liegt kein Stift naeher als 2.88 mm an einem Kontakt (halbes Raster waeren 1.27 mm), ein verdreht aufgesetztes Modul steckt also nirgends und bleibt tot statt kaputt.

## Auflagen an die Modulfirmware

- Ausserhalb des Flash-Modus darf ein Modul die Leitung FLASH_RX nicht treiben. FLASH_RX ist der Empfangspin des Pico und damit die gemeinsame Sendeleitung aller Module. Im Normalbetrieb sind alle Module gleichzeitig wach; treibt mehr als eines diese Leitung, fallen sie einander ins Wort und koennen einander im Gegentakt beschaedigen. Senden darf ein Modul nur, solange es ueber die Auswahlkette ausgewaehlt ist (FLASH_MODE = 1 und das eigene Flipflop Q = 1). Sonst bleibt der Pin hochohmig.

## Auflagen an das Modul-Layout

- Jede Platine traegt neben Pin 1 des Stapelsteckers eine Kennzeichnung im Bestueckungsdruck (Dreieck plus Text "1") und an der Klemmenkante (untere Kante, y = BOARD_H) die Beschriftung "KLEMMEN". Grund: das M3-Lochbild ist punktsymmetrisch, ein Modul laesst sich also um 180 Grad verdreht anschrauben. Die Steckerlage (STECKER_POS) ist bewusst so unsymmetrisch, dass dann kein einziger Stift in einen Buchsenkontakt findet -- das verhindert den Schaden, macht den Fehler aber nicht sichtbar. Ausserdem darf in den drei Flaechen VERDREHT(STECKER_POS[...]["flaeche"]) kein freiliegendes Kupfer liegen (keine Testpunkte, keine offenen Pads): dort setzen die Stifte eines verdreht aufgesteckten Moduls auf.

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

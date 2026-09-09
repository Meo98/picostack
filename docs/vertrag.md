# PicoStack — der Vertrag

Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.

## Status

Die Zusagen rund um das Flashen -- die Leitungen `FLASH_TX`, `FLASH_RX`, `SEL`, `SEL_CLK` und `FLASH_MODE` (SEL seit 2026-08-31 auf dem eigenen Kettenstecker, alle anderen auf den beiden 1x20-Stapelstecker-Reihen) und alles, was daran haengt -- ruhen auf einer Annahme, die noch **nicht auf Hardware belegt** ist: dass der Pico einen Modul-MCU ueber dessen ROM-Bootlader wirklich beschreiben kann. Geprueft ist bisher nur das Protokoll gegen eine Attrappe, nicht gegen echtes Silizium. Stand und offene Schritte: `docs/nachweis-2026-08.md`.

## Umriss

75.0 x 65.0 mm, Ecken 3.0 mm gerundet, 13.6 mm zwischen den Platinen.

| M3-Bohrung | x | y | Bohrdurchmesser |
|---|---|---|---|
| 1 | 4.0 | 4.0 | 3.2 |
| 2 | 4.0 | 61.0 | 3.2 |
| 3 | 71.0 | 4.0 | 3.2 |
| 4 | 71.0 | 61.0 | 3.2 |

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

### Pins, die eine Rolle tragen und trotzdem NICHT benutzbar sind

Diese Pins fuehren eine Bezeichnung, liegen aber auf keiner Platine des Stapels an einem Netz. Wer sich auf die Rolle allein verlaesst, haelt sie faelschlich fuer belegt.

| Pin | Rolle | Warum nicht benutzbar |
|---|---|---|
| 30 | RUN | Reset des RP2040, aktiv-LOW mit eigenem Pullup (Pico Datasheet Rel. 21, Abschnitt 2.1). Ein Modul, das ihn treibt, setzt den Pico zurueck. |
| 35 | ADC_VREF | analoge Referenzspannung des ADC, kein Digitalanschluss. |
| 37 | 3V3_EN | schaltet den internen Regler des Pico ab. Nach aussen gefuehrt waere das ein Ausschalter fuer den ganzen Stapel, den jedes Modul versehentlich ziehen koennte. |
| 40 | VBUS | liegt nur an, wenn am Pico ein USB-Kabel steckt. Eine Schiene, die von einem Zufall abhaengt, ist keine Zusage. |

## Stapelstecker und Kettenstecker

Die Steckerbelegung oben laeuft seit Vertragsversion 2 nicht mehr ueber einen einzelnen 2x20-Block, sondern ueber **zwei 1x20-Buchsenreihen in echter Pico-Geometrie** (Reihenabstand 17,78 mm, Raster 2,54 mm): `stapel_links` traegt Pico-Pin 1..20, `stapel_rechts` Pico-Pin 21..40. Der Pico steckt dadurch direkt oben in den Stapel; die Pin-Rollen aus der Tabelle oben aendern sich dadurch NICHT, nur ihre Steckergeometrie. Beide Reihen sind **Stapelstecker**: 1x20 (oder 2x 1x10 in Reihe), 2,54 mm, Buchse mit durchgehendem Stift (PC104/Arduino-Stapelleisten-Prinzip) -- je EINE Reihe (stapel_links ODER stapel_rechts, s. STECKER_POS), nicht mehr die ganze 2x20-Pico-Bahn wie in v1. Bauteil: offen bis Fertigungs-Sichtung (1x20-Sourcing-Ruling s. Kommentar oben), Gehaeusehoehe 8.50 mm, Stiftlaenge unterhalb des Gehaeuses 12.46 mm. Quelle: hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31, C35165 als Bauform-Beleg); Sourcing-Ruling fuer 1x20 s. Kommentar oben (Aufgabe 2, Fix-Runde 1, 2026-09-08).

Einzige Ausnahme ist die Auswahlkette (`SEL`): sie muss von Modul zu Modul aufgetrennt werden (Schieberegister, `tools/kette.py`) und ist deshalb kein Pin des Stapelsteckers mehr. Sie laeuft ueber einen eigenen, zweipoligen **Kettenstecker** (SMD-Buchse oben / SMD-Stiftleiste unten (auftrennbar), 1x2, 2,54 mm): traegt SEL (Auswahlkette) und eine GND daneben.

| Pin (Kettenstecker) | Rolle |
|---|---|
| 1 | SEL |
| 2 | GND |

Ketten- und Leistungsstecker sind seit 2026-08-31 **SMD-Paare**: Buchse auf der Oberseite, Stiftleiste auf der Unterseite, am selben Ort. Zwei bedrahtete Haelften am selben Ort brauchten dieselben Bohrungen -- und dieselbe Bohrung ist derselbe Leiter, was beim Kettenstecker `SEL_IN` und `SEL_OUT` kurzschliessen wuerde. Einstecktiefe je 5.00 mm, Luft zwischen Stiftkoerper und Buchsenoberkante 1.00 mm.

| Stecker | Bauart | oben | unten | Buchse LCSC | Buchse Typ | Stift LCSC | Stift Typ |
|---|---|---|---|---|---|---|---|
| stapel | 1x20 (oder 2x 1x10 in Reihe), 2,54 mm, Buchse mit durchgehendem Stift (PC104/Arduino-Stapelleisten-Prinzip) -- je EINE Reihe (stapel_links ODER stapel_rechts, s. STECKER_POS), nicht mehr die ganze 2x20-Pico-Bahn wie in v1 | THT | THT | offen:  | None | offen:  | None |
| kette | SMD-Buchse oben / SMD-Stiftleiste unten (auftrennbar), 1x2, 2,54 mm | SMD | SMD | `C46635838` | hanxia HX PM2.54-1x2P TP H8.5-YQ | `C41417359` | hanxia HX PZ2.54-1x2P TP-YQ |
| leistung | SMD-Buchse oben / SMD-Stiftleiste unten, 2x2, 2,54 mm | SMD | SMD | `C3975147` | HCTL PM254-2-02-S-8.5 | `C919361` | BOOMELE 2.54-2*2P |

Alle sechs Steckerhaelften tragen seit 2026-08-31 eine Bauteilnummer von einer gesehenen LCSC-Produktseite; alle sind in der JLCPCB-Bestueckungsbibliothek gefuehrt. Damit sind Sockelplatine und Module bestueckt bestellbar -- ein einziges leeres Feld haette das verhindert.

Quellen: hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31, C35165 als Bauform-Beleg); Sourcing-Ruling fuer 1x20 s. Kommentar oben (Aufgabe 2, Fix-Runde 1, 2026-09-08) / hardware/bauteile-1b.md, Beleg 13 und 14 (2026-08-31) / hardware/bauteile-1b.md, Beleg 4, 13 und 14.

## Wo die Stecker sitzen

Alle Masse in mm, Ursprung linke obere Ecke, x nach rechts, y nach unten. Diese Lage gilt fuer **jede** Platine im Stapel -- der Stapelstecker der Sockelplatine steht senkrecht ueber dem jedes Moduls, Ketten- und Leistungsstecker ebenso. Wer sie verschiebt, macht alle bereits gebauten Module unbrauchbar.

| Stecker | Zweck | Mitte x | Mitte y | Drehung | belegte Flaeche (x0 y0 x1 y1) |
|---|---|---|---|---|---|
| stapel_links | 1x20-Buchsenreihe, Pico-Pins 1..20 (links, oben->unten) | 30.61 | 26.4 | 0 Grad | 28.84 0.50 32.38 52.30 |
| stapel_rechts | 1x20-Buchsenreihe, Pico-Pins 21..40 (rechts, unten->oben) | 48.39 | 26.4 | 180 Grad | 46.62 0.50 50.16 52.30 |
| kette | zweipoliger Kettenstecker, SEL + GND (STECKER_KETTE) | 20.59 | 4.02 | 0 Grad | 17.18 0.87 24.00 7.17 |
| leistung | 2x2-Leistungsstecker, 24 V und GND je doppelt | 63.77 | 46.77 | 0 Grad | 57.90 43.72 69.64 49.82 |

Die belegte Flaeche ist die Vereinigung der Hoefe (F.CrtYd) aller Footprints an diesem Platz, nach der Drehung. Ketten- und Leistungsstecker bestehen auf jedem Modul aus zwei Haelften (SMD-Buchse oben, SMD-Stiftleiste unten); beide Haelften belegen **denselben** Platz, sonst treffen sie sich im Stapel nicht.

Seit Vertragsversion 2 steckt der Pico nicht mehr nur auf einer eigenen Sockelplatine, sondern oben auf **jedem** Modul, in `stapel_links`/`stapel_rechts`. Sein Umriss (`PICO_SCHATTEN`, 51 x 21 mm laut Datenblatt) liegt bei 29.00 0.90 50.00 51.90. Am Pico-Ende gegenueber der USB-Buchse liegt der WLAN-Antennen-Sperrbereich `ANTENNE_FREI` 29.00 42.90 50.00 51.90 (21.0 x 9.0 mm) -- dort darf auf der Seite, auf der der Pico steckt, weder Kupfer noch ein Bauteil liegen (Raspberry Pi Pico W Datasheet, RP-008312-DS-2, Abschnitt 2.2.1 "Keep-out area": Ausschnitt 14 x 9 mm).

Um jede M3-Bohrung bleibt ein Freihaltebereich von 7.0 mm Durchmesser fuer Schraubenkopf und Abstandsbolzen frei.

Das Lochbild ist punktsymmetrisch -- ein Modul laesst sich um 180 Grad verdreht anschrauben. Die Steckerlage ist deshalb bewusst unsymmetrisch: verdreht liegt kein Stift naeher als 4.03 mm an einem Kontakt (halbes Raster waeren 1.27 mm), ein verdreht aufgesetztes Modul steckt also nirgends und bleibt tot statt kaputt.

## Auflagen an die Modulfirmware

- Ausserhalb des Flash-Modus darf ein Modul die Leitung FLASH_RX nicht treiben. FLASH_RX ist der Empfangspin des Pico und damit die gemeinsame Sendeleitung aller Module. Im Normalbetrieb sind alle Module gleichzeitig wach; treibt mehr als eines diese Leitung, fallen sie einander ins Wort und koennen einander im Gegentakt beschaedigen. Senden darf ein Modul nur, solange es ueber die Auswahlkette ausgewaehlt ist (FLASH_MODE = 1 und das eigene Flipflop Q = 1). Sonst bleibt der Pin hochohmig.

## Auflagen an das Modul-Layout

- Jede Platine traegt neben Pin 1 des Stapelsteckers eine Kennzeichnung im Bestueckungsdruck (Dreieck plus Text "1") und an der Klemmenkante (untere Kante, y = BOARD_H) die Beschriftung "KLEMMEN". Grund: das M3-Lochbild ist punktsymmetrisch, ein Modul laesst sich also um 180 Grad verdreht anschrauben. Die Steckerlage (STECKER_POS) ist bewusst so unsymmetrisch, dass dann kein einziger Stift in einen Buchsenkontakt findet -- das verhindert den Schaden, macht den Fehler aber nicht sichtbar. Ausserdem darf auf der OBERSEITE eines Moduls im Umkreis von LANDE_SPERRRADIUS um jeden der Punkte aus LANDEPUNKTE_VERDREHT() kein freiliegendes Kupfer liegen (keine Testpunkte, keine offenen Pads, keine unbedeckten Durchkontaktierungen): genau dort setzen die Stifte eines verdreht aufgesteckten Aufbaus auf. Die Sockelplatine ist von dieser Kupferregel ausgenommen -- sie sitzt zuoberst, auf ihre Oberseite drueckt nie ein Stift.

- Ketten- und Leistungsstecker sind SMD-Paare: Buchse auf der Oberseite, Stiftleiste auf der Unterseite, auf demselben Kontaktraster und OHNE Durchkontaktierung zwischen den beiden Kontaktflaechen. Beim Kettenstecker ist die fehlende Durchkontaktierung die eigentliche Funktion: oben liegt SEL_IN, unten SEL_OUT: waeren sie verbunden, waere die Auswahlkette kurzgeschlossen und das Schieberegister (tools/kette.py) wirkungslos. Beim Leistungsstecker fuehren beide Seiten dasselbe Netz; dort ist die Verbindung erlaubt, aber sie gehoert dann in eine eigene Durchkontaktierung neben dem Pad, nicht in das SMD-Pad selbst.

- Beide SMD-Steckerpaare brauchen eine Zugentlastung: die Steckkraft eines ganzen Stapels darf nicht an den Loetstellen haengen. Zulaessig sind zwei zusaetzliche, mechanisch verschraubte oder verklebte Befestigungspunkte je Stecker, oder ein Fuegeverfahren, bei dem die Platinen ERST gesteckt und DANN auf die Abstandsbolzen geschraubt werden. Welches von beiden, entscheidet die Layout-Aufgabe -- aber nicht keines von beiden. Bedrahtete Stecker haetten das nicht gebraucht; sie sind hier aber ausgeschlossen (s. Block bei STECKER_KETTE).

Kein freiliegendes Kupfer naeher als 1.5 mm an einem der 46 Landepunkte aus `LANDEPUNKTE_VERDREHT()` (das sind die um 180 Grad gedrehten Lagen aller Steckerkontakte).

## Versorgung je Board

Seit Vertragsversion 2 hat jedes Modul seine eigene Versorgungszelle statt einer gemeinsamen Sockelplatine: Klemme (6.0-30.0 V), Verpolschutz (P-FET, Drain am Netz `PWR_IN`), TVS, K7805-1000R3 und ein Schottky-OR (vsys_diode) vor VSYS. Beliebig viele bestueckte Regler koennen im selben Stapel koexistieren; ein einziges eingespeistes Board versorgt die ganze Kette. Der Gate-Teiler des Verpolschutzes haengt an `+24V_LOKAL`, nicht an der Einspeisung selbst -- das ist der aus v1 uebernommene Blocker-Fix: lag der Teiler am Eingang, bildeten Bodydiode und TVS bei verpolter Einspeisung einen Kurzschluss statt zu sperren.

## Randpads

Jeder als "frei" deklarierte Pico-Pin (und mehrere 3V3-/GND-Pads) liegt zusaetzlich als beschriftetes Loetpad auf der Plattenkante -- Position vertraglich fixiert, identisch auf jedem Modul, auf der Unterseite (B.Cu), damit die Verdreh-Sicherheit der Landepunkte unangetastet bleibt. 22 Pads insgesamt.

| Pico-Pin | Beschriftung | x | y |
|---|---|---|---|
| 3 | GND | 8.0 | 63.0 |
| 36 | 3V3 | 10.54 | 63.0 |
| 11 | GP8 | 13.08 | 63.0 |
| 12 | GP9 | 15.62 | 63.0 |
| 14 | GP10 | 18.16 | 63.0 |
| 15 | GP11 | 20.7 | 63.0 |
| 16 | GP12 | 23.24 | 63.0 |
| 17 | GP13 | 25.78 | 63.0 |
| 19 | GP14 | 28.32 | 63.0 |
| 20 | GP15 | 30.86 | 63.0 |
| 21 | GP16 | 33.4 | 63.0 |
| 22 | GP17 | 35.94 | 63.0 |
| 24 | GP18 | 38.48 | 63.0 |
| 25 | GP19 | 41.02 | 63.0 |
| 26 | GP20 | 43.56 | 63.0 |
| 27 | GP21 | 46.1 | 63.0 |
| 29 | GP22 | 48.64 | 63.0 |
| 31 | GP26 | 51.18 | 63.0 |
| 32 | GP27 | 53.72 | 63.0 |
| 34 | GP28 | 56.26 | 63.0 |
| 36 | 3V3 | 58.8 | 63.0 |
| 38 | GND | 61.34 | 63.0 |

## Montage

ERST stecken, DANN auf die Abstandsbolzen schrauben. Die Zugentlastung der SMD-Steckerpaare ist die Verschraubung des Stapels; ein bereits verschraubter Stapel darf nicht auseinandergezogen werden, ohne zuerst die Bolzen zu loesen.

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

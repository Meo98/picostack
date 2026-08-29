# Bauteilwahl: Modul-MCU, Bootlader-Pins, Reset-Zustand

**Stand:** 2026-08-28. Bestand und Preise bei LCSC/JLCPCB ändern sich
laufend; die hier genannten Zahlen sind Stichproben vom Recherchezeitpunkt,
keine Garantie.

## Bauteiltabelle

| Zweck | Typ | Bauform | LCSC | geprüft | Quelle |
|---|---|---|---|---|---|
| Modul-MCU | STM32C011F6P6 | TSSOP-20 | C5456198 | ja | JLCPCB-Produktseite `jlcpcb.com/partdetail/STMicroelectronics-STM32C011F6P6/C5456198` (Rohdaten: `componentLibraryType":"expand"`, `assemblyMode":"smtWeld"`, `moistureSensitivityLevelEn":"MSL 1"`); LCSC-Produktseite `lcsc.com/product-detail/C5456198.html` |
| Motortreiber | DRV8876PWPR | HTSSOP-16-EP | C575551 | ja | JLCPCB-Produktseite `jlcpcb.com/partdetail/TexasInstruments-DRV8876PWPR/C575551` (Rohdaten: `"Extended Part"`, `componentLibraryType":"expand"`); LCSC-API-Abfrage `wmsc.lcsc.com/ftps/wm/product/detail?productCode=C575551` |
| Motortreiber (Automotive-Grade, Alternative) | DRV8876QPWPRQ1 | HTSSOP-16-EP | C2860987 | ja | LCSC-API-Abfrage `wmsc.lcsc.com/ftps/wm/product/detail?productCode=C2860987`; nur 14 Stück Lagerbestand am Stichtag, deshalb nicht empfohlen |
| Leistungsstecker (Vorschlag, nicht festgelegt) | generischer 2,54-mm-Doppelreihen-Stiftverbinder | THT | — | nein | kein konkretes Bauteil im Vertrag festgelegt; Referenzwert 3 A/Kontakt aus Multicomp-Datenblatt (Farnell-Dok. 2585485, Abschnitt „Specifications", `Current Rating: 3A AC/DC`) — Beschreibung s. Absatz unten |

Zu **STM32C011F6P6**: Preisstaffel laut JLCPCB-Rohdaten (Stichtag) 1,47 $
(1 Stk.) fallend auf 0,87 $ (ab 1036 Stk.); Lagerbestand laut
LCSC-API 3063 Stück. Das ist deutlich mehr als der zuvor nur von der
LCSC-Seite bekannte Näherungswert von „rund 0,55 $"; der Preisunterschied
liegt vermutlich an schwankenden Staffelpreisen, ändert aber nichts an der
Kernaussage: das Bauteil **ist** bei JLCPCB bestückbar — als **Extended
Part**, nicht als Basic Part (Beleg unten). Ein Rückgriff auf `PY32F002A`
ist damit **nicht nötig**.

Zu **DRV8876PWPR**: ebenfalls Extended Part, Lagerbestand 620 Stück laut
LCSC-API. Das ist der Standardtyp (keine automotive-Qualifizierung); die
Q-Variante DRV8876QPWPRQ1 ist zwar für JLCPCB gelistet, aber am Stichtag
mit 14 Stück praktisch nicht verfügbar.

## Beleg 1 — Bootlader-Pins (AN2606)

**Quelle:** AN2606 „STM32 microcontroller system memory boot mode",
Rev 61 (Januar 2024), Abschnitt 5 „STM32C011xx devices bootloader",
Tabelle 9 und die zugehörige Fussnote. Bezogen über einen Volltext-Mirror
(`kolegite.com`), weil der direkte Download von der offiziellen
`st.com`-Ressourcen-URL blockiert war (HTTP/2 `INTERNAL_ERROR` auf jeden
Versuch) — ich habe die dortige Revision deshalb **nicht selbst
gesehen**. Ein WebSearch-Treffer zeigte für dieselbe URL den Titel
„February 2026 AN2606 Rev 70"; das war nur ein Suchergebnis-Schnipsel,
keine geprüfte Sichtung, und laut Prüfung durch den Auftraggeber liefert
die offizielle URL inhaltlich tatsächlich Rev 61. Diese Aussage stützt
sich deshalb ausschliesslich auf die tatsächlich gelesene **Rev 61**
(Mirror). Der Abschnitt zum STM32C0 wurde laut Änderungshistorie in
Rev 52 (01-Mar-2022) eingeführt und ist seither laut derselben
Änderungshistorie inhaltlich nicht mehr angefasst worden.

Der USART-Bootlader des STM32C011xx läuft auf **USART1**, nicht USART2.
Laut Tabelle 9: „PA10 pin: USART1 in reception mode... PA9 pin: USART1 in
transmission mode". Die Fussnote dazu: „On WLCSP12, SO8N, TSSOP20, and
UFQFN20 packages USART1 PA9/PA10 IOs are remapped on PA11/PA12." Da
STM32C011F6P6 im TSSOP-20-Gehäuse kommt, liegt der Bootlader-UART auf den
**physischen Pins PA11 (TX) und PA12 (RX)**. Das deckt sich mit dem
Datenblatt (DS13866 Rev 3, Pinout-Tabelle, TSSOP20-Zeilen „PA11[PA9]" /
„PA12[PA10]") und dessen Fussnote 1: „Pins PA9 and PA10 can be remapped in
place of pins PA11 and PA12 (default mapping)" — auf diesem Gehäuse ist
PA11/PA12 also die Standardbelegung.

Aktiviert wird der Bootlader über **Pattern 11** (Tabelle 2, AN2606
Abschnitt 4.1): über den BOOT0-Pin oder wahlweise über die Optionsbytes
`nBOOT0` zusammen mit `nBOOT0_SEL`/`BOOT_LOCK` (Boot0-Signalquelle
umschaltbar, RM0490 Abschnitt 2.5 „Boot configuration", Tabelle 4). Die
Bit-Definitionen selbst liegen in zwei verschiedenen Registern, einzeln
geprüft: `nBOOT_SEL` (Bit 24), `nBOOT0` (Bit 26) und `nBOOT1` (Bit 25)
stehen im RM0490 Abschnitt 3.7.6 „FLASH option register (FLASH_OPTR)";
`BOOT_LOCK` (Bit 16) dagegen in einem anderen Register, RM0490 Abschnitt
3.7.13 „FLASH security register (FLASH_SECR)". Für den Stapel relevant:
**BOOT0 ist physisch PA14** (Datenblatt DS13866, Pinout: Pin
„PA14-BOOT0"). PA14 ist zugleich SWCLK — dazu mehr in Beleg 2.

Zum in der Aufgabe genannten ST-Community-Hinweis „USART2 liegt auf
SWDIO/SWCLK": das stimmt, ist für unseren Bootlader aber **nicht**
relevant, weil dieser USART1 nutzt, nicht USART2. Bestätigt aus dem
Datenblatt (DS13866 Rev 3, Tabelle 13 „Port A alternate function
mapping (AF0 to AF7)"): PA13 trägt
`USART2_RX`, PA14 trägt `USART2_TX` als Alternate Function — der Hinweis
bezog sich also korrekt auf USART2, nicht auf den ROM-Bootlader. Folgerung
für den Entwurf: **USART2 darf auf keinem Modul für andere Zwecke
verwendet werden**, solange SWD-Pins frei bleiben sollen — das ist aber
ein Firmware-Hinweis, keine Bootlader-Einschränkung.

## Beleg 2 — Pin-Zustand nach Reset (RM0490)

**Quelle:** RM0490 „STM32C0 Series advanced Arm-based 32-bit MCUs
reference manual", Rev 3 (Dezember 2022), Abschnitt 6.3.1
„General-purpose I/O (GPIO)", Abschnitt 6.3.16 „Boot0 pin (PA14) in GPIO
mode" und Abschnitt 26.3.3 „Internal pull-up & pull-down on SWD pins".
Bezogen über Mirror `state-machine.com`, weil auch hier der direkte
`st.com`-Download blockiert war.

Wörtlich, RM0490 §6.3.1: „During and just after reset, the alternate
functions are not active and most of the I/O ports are configured in
analog mode. The debug pins are in AF pull-up/pull-down after reset: PA14:
SWCLK in pull-down, PA13: SWDIO in pull-up. Note: PA14 is shared with
BOOT0 functionality."

Das bestätigt die Entwurfsannahme **grösstenteils**: alle GPIO, die nicht
Debug-Pins sind, stehen nach Reset auf **Analog** (hochohmig, kein
Pull) — das schliesst die Bootlader-UART-Pins PA11/PA12 ein (Register
`GPIOA_MODER` (RM0490 §6.4.1), Reset-Wert `0xEBFF FFFF`; die betroffenen Bits für
MODE13/MODE14 = `10` (AF) sind nur PA13/PA14, alle anderen Bits bleiben
`11` = Analog). Die **gemeinsame Sendeleitung des Bootlader-UART ist damit
im Reset tatsächlich hochohmig**, wie der Entwurf voraussetzt.

**Einschränkung, die dokumentiert gehört:** PA14 — physisch BOOT0 — ist
zugleich SWCLK und liegt nach Reset **nicht** auf Analog, sondern in
Alternate-Function-Modus mit aktivem internem Pull-down (RM0490 §6.4.4
„GPIO port pull-up/pull-down register (GPIOx_PUPDR)"; Widerstandswert
laut Datenblatt DS13866, Tabelle 49 „I/O static characteristics": `RPD`
typ. 40 kΩ, min. 25 kΩ, max. 55 kΩ).
PA13 (SWDIO) liegt analog mit Pull-up. Wenn die geplante globale
„Flash-Modus"-Leitung der Spec auf PA14/BOOT0 gelegt wird, trägt jedes
unbeteiligte Modul dort einen schwachen Pull-down (~40 kΩ) statt reiner
Hochohmigkeit. Das ist **kein Blocker** — ein aktiver Treiber am Sockel
überstimmt einen 40-kΩ-Pull-down mühelos, und die Ruherichtung
(Pull-down = „Flash-Modus aus") passt sogar zur gewünschten Grundstellung
— aber es ist eine reale Abweichung von „rein hochohmig" und sollte beim
Entwurf der Flash-Modus-Leitung (Aufgabe 2/4) berücksichtigt werden, nicht
stillschweigend angenommen werden.

Für die I²C-Pins des Bootladers (PB6/PB7) gilt die allgemeine Regel ohne
Einschränkung: Port B liegt komplett auf `0xFFFF FFFF` (Analog für alle
16 Pins), keine Sonderbehandlung dokumentiert.

## Beleg 3 — Übrige offene Punkte (Leistungsstecker, 3,3-V-Budget, DRV8876)

**Leistungsstecker-Strombelastbarkeit:** Im Entwurf (`docs/superpowers/specs/2026-08-28-picostack-design.md`)
ist bisher **kein konkretes Bauteil** für den Leistungsstecker festgelegt
— nur „eigener Stecker, nur 24 V und Masse, mehrere Kontakte parallel".
Diese Aufgabe kann deshalb keine geprüfte LCSC-Nummer dafür liefern; das
wäre erfunden. Als Anhaltspunkt für die Obergrenze: ein generischer
2,54-mm-Doppelreihen-Stiftverbinder (Multicomp-Datenblatt, Farnell-Dok.
2585485, Rev. V1.0, Abschnitt „Specifications") ist mit **3 A AC/DC pro
Kontakt** spezifiziert. Bei zwei parallelen Kontakten je Ader (24 V und
GND, wie in der Spec vorgesehen) ergäbe das rechnerisch bis 6 A pro Ader
vor Derating — das ist ein Anhaltspunkt für Aufgabe 2 (Steckerbelegung),
keine Festlegung. Die endgültige Bauteilwahl für den Leistungsstecker
gehört in die Steckerbelegung, nicht in diese Aufgabe.

**3,3-V-Budget des Pico:** Laut Raspberry Pi Pico Datasheet (Abschnitt
„Pin Description", Beschreibung des Pins `3V3`): „This pin can be used to
power external circuitry (maximum output current will depend on RP2040
load and VSYS voltage, it is recommended to keep the load on this pin
less than 300 mA)." Das Modul-MCU-Datenblatt (DS13866 Rev 3, Tabelle 27
„Current consumption in Run mode from flash memory") gibt für
STM32C011F6P6 bei 48 MHz (HSI48) einen Laufstrom `IDD(Run)` von typ.
3,40 mA / max. 3,90 mA bei 25 °C (bis max. 4,90 mA bei 125 °C) an. Zehn
Module: 10 × 3,90 mA ≈ **39 mA**, selbst bei 125 °C nur ≈ 49 mA — das
liegt weit unter den empfohlenen 300 mA und lässt reichlich Spielraum für
den RP2040-Eigenverbrauch und die restliche Peripherie auf dem Sockel.
Budget-Frage ist damit **unkritisch geklärt**, nicht neu zu bewerten.

**Verfügbarkeit DRV8876 bei JLCPCB:** siehe Bauteiltabelle oben —
DRV8876PWPR (C575551) ist als Extended Part bei JLCPCB gelistet und mit
620 Stück Lagerbestand am Stichtag verfügbar.

## Was das für Aufgabe 2 und 4 bedeutet

- Modul-MCU: **STM32C011F6P6**, TSSOP-20, LCSC C5456198.
- Bootlader-UART-Pins (physisch, TSSOP-20-Gehäuse): **PA11 = USART1_TX**,
  **PA12 = USART1_RX** (intern remapped von PA9/PA10).
- Beide Pins stehen nach Reset auf Analog/hochohmig — die gemeinsame
  Sendeleitung ist sicher.
- BOOT0 ist physisch **PA14**, zugleich SWCLK, mit ~40-kΩ-Pull-down nach
  Reset aktiv, sobald das Modul die SWD-Funktion nicht per Optionsbyte
  freigegeben hat (`USE_BOOT0_OPT`). Für die globale Flash-Modus-Leitung
  einplanen, kein Blocker.
- Kein `PY32F002A`-Rückfall nötig — STM32C011F6P6 ist bestückbar.

## Beleg 4 — Auswahlkette und Gatter (Aufgabe 3)

**Quelle:** `tools/kette.py`, Wahrheitstabelle als Modul-Zustandslogik.

Die Auswahlkette wird durch drei Boolesche Gleichungen beschrieben:

| Ausgang | Gleichung |
|---|---|
| RESET | `flash_mode AND (NOT sel_in)` |
| BOOT0 | `flash_mode AND sel_in` |
| SEL_OUT | `(NOT flash_mode) AND sel_in` |

Diese Logik setzt sich aus fünf elementaren Gatteroperationen zusammen:

1. **Invertierung flash_mode** → 1× NOT-Gatter (für SEL_OUT)
2. **Invertierung sel_in** → 1× NOT-Gatter (für RESET)
3. **RESET = flash_mode ∧ ¬sel_in** → 1× 2-Input AND-Gatter
4. **BOOT0 = flash_mode ∧ sel_in** → 1× 2-Input AND-Gatter
5. **SEL_OUT = ¬flash_mode ∧ sel_in** → 1× 2-Input AND-Gatter

**Bauteilwahl — Einzelgatter statt Multi-Gate-ICs:** Fünf Gatterfunktionen in zwei grossen
SOIC-14-Gehäusen (8,7 × 3,9 mm je IC) bedeuten 50 % Verschnitt bei einer Platine mit
Kleinheit-Anspruch. Die empfohlene Lösung nutzt Einzelgatter und Doppelgatter aus der
CMOS-Familie 74LVC1G/74LVC2G in miniaturisierten SMD-Gehäusen (SC-70 oder SOT-363,
rund 2 × 1,25 mm je IC):

| IC | Typ | Gatteranzahl | Gehäuse | LCSC | Funktion |
|---|---|---|---|---|---|
| IC1 | Doppel-Inverter (2× 1-Input NOT) | 74LVC2G04 | SC-70 oder SOT-363 | — | Invertiert flash_mode und sel_in |
| IC2 | Doppel-AND-Gatter (2× 2-Input AND) | 74LVC2G08 | SC-70 oder SOT-363 | — | Realisiert RESET und BOOT0 |
| IC3 | Einzel-AND-Gatter (1× 2-Input AND) | 74LVC1G08 | SC-70 oder SOT-363 | — | Realisiert SEL_OUT |

**Spezifikation:**
- IC1: CMOS Doppel-NOT-Gatter, Typ 74LVC2G04 oder baugleiches IC aus der 74LVC-Familie
- IC2: CMOS Doppel-AND-Gatter (2-Input), Typ 74LVC2G08 oder baugleiches IC aus der 74LVC-Familie
- IC3: CMOS Einzel-AND-Gatter (2-Input), Typ 74LVC1G08 oder baugliches IC aus der 74LVC-Familie
- Alle in Gehäusen SC-70 oder SOT-363 (max. 2 × 1,25 mm je IC)
- Betriebsspannung: 1,65–5,5 V (kompatibel mit 3,3-V-Betrieb)
- Stromverbrauch: CMOS (picoampere static, nanoampere dynamic)

**Verfügbarkeit:** LCSC und JLCPCB führen die 74LVC1G und 74LVC2G Serien als Standard-Logik.
Eine konkrete Nummernvergabe wird bei nächster Beschaffungs-Phase recherchiert (Constraint: keine
LCSC-Nummer ohne Produktseiten-Nachweis). Die drei Gehäuse beanspruchen zusammen eine
Platinenfläche ungefähr ein Zehntel der früheren Zwei-SOIC-14-Lösung.

**Alternative: Decoder-Struktur (erwogen, nicht weiter verfolgt):** RESET und BOOT0 bilden
zusammen einen 1-aus-2-Decoder mit Freigabe (`flash_mode` als Freigabesignal, `sel_in` als
Adresseingabe). Ein spezialisierter Decoder-IC (z.B. 74LVC138 als 3-aus-8-Decoder) wäre für
zwei Ausgänge zu mächtig. Der Decoder-Ansatz wurde zugunsten der einfachen Einzelgatter-Lösung
nicht weiter verfolgt.

**Klarstellung zu MCU-Verhalten:** Der Kommentar „Ausgänge hochohmig" in `kette.py` bezieht sich
auf die GPIO-Pins des **Modul-MCU im Reset-Zustand** — nicht auf die Ausgänge der Logik-ICs. Die
Gatterausgänge arbeiten aktiv in Gegentaktverstärkung (totem pole) und treiben die Reset- und
BOOT0-Eingänge des MCU mit definierten High- und Low-Pegeln. Nur die GPIO-Pins des im Reset
gehaltenen MCU sind hochohmig, weil der MCU keinen Taktgenerator hat und keine Ausgänge aktiv
treibt.

**Token-Durchleitungslogik:** Das Token (SEL_OUT) wird unter zwei Bedingungen weitergeleitet:

- **Im Normalbetrieb (FLASH_MODE = 0):** SEL_OUT folgt sel_in direkt; das Token wandert
  ungehindert durch die Kette weiter, unabhängig von der bisherigen Auswahl.
- **Im Flash-Modus (FLASH_MODE = 1) bei Nichtauswahl (sel_in = 0):** SEL_OUT = 0; das Token
  wird hier blockiert und wandert nicht weiter.

Im Ruhezustand eines unbeteiligten Moduls (FLASH_MODE = 0) wird das Token normalerweise
weitergereicht (SEL_OUT = sel_in). Blockiert wird das Token nur durch eine bewusste Aktion:
der Sockel setzt FLASH_MODE = 1, was die Schaltung in den Programmiermode versetzt, und
die Auswahl (sel_in = 0 für alle außer dem gewählten) sorgt dafür, dass nur das ausgewählte
Modul das Token nicht weitergeben darf.

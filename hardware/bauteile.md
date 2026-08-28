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
(`kolegite.com`), weil `st.com` den direkten PDF-Download der aktuellen
Revision (Rev 70, Februar 2026) programmatisch blockiert (HTTP/2
`INTERNAL_ERROR` auf jeden Downloadversuch). Der Abschnitt zum STM32C0
wurde laut Änderungshistorie in Rev 52 (01-Mar-2022) eingeführt und seither
inhaltlich nicht mehr angefasst — die verwendete Rev 61 sollte deshalb mit
Rev 70 inhaltlich übereinstimmen, das ist aber **nicht** gegen die
Originalrevision gegengeprüft.

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
umschaltbar, RM0490 Abschnitt 3.5, Bit `nBOOT_SEL`). Für den Stapel
relevant: **BOOT0 ist physisch PA14** (Datenblatt DS13866, Pinout: Pin
„PA14-BOOT0"). PA14 ist zugleich SWCLK — dazu mehr in Beleg 2.

Zum in der Aufgabe genannten ST-Community-Hinweis „USART2 liegt auf
SWDIO/SWCLK": das stimmt, ist für unseren Bootlader aber **nicht**
relevant, weil dieser USART1 nutzt, nicht USART2. Bestätigt aus dem
Datenblatt (DS13866 Rev 3, alternate-function-Tabelle): PA13 trägt
`USART2_RX`, PA14 trägt `USART2_TX` als Alternate Function — der Hinweis
bezog sich also korrekt auf USART2, nicht auf den ROM-Bootlader. Folgerung
für den Entwurf: **USART2 darf auf keinem Modul für andere Zwecke
verwendet werden**, solange SWD-Pins frei bleiben sollen — das ist aber
ein Firmware-Hinweis, keine Bootlader-Einschränkung.

## Beleg 2 — Pin-Zustand nach Reset (RM0490)

**Quelle:** RM0490 „STM32C0 Series advanced Arm-based 32-bit MCUs
reference manual", Rev 3 (Dezember 2022), Abschnitt 6.3.1
„General-purpose I/O (GPIO)" und Abschnitt 26.3.3 „Internal pull-up &
pull-down on SWD pins". Bezogen über Mirror `state-machine.com`, weil auch
hier der direkte `st.com`-Download blockiert war. Ergänzend: Datenblatt
DS13866 Rev 3, Abschnitt 6.3.16 „Boot0 pin (PA14) in GPIO mode".

Wörtlich, RM0490 §6.3.1: „During and just after reset, the alternate
functions are not active and most of the I/O ports are configured in
analog mode. The debug pins are in AF pull-up/pull-down after reset: PA14:
SWCLK in pull-down, PA13: SWDIO in pull-up. Note: PA14 is shared with
BOOT0 functionality."

Das bestätigt die Entwurfsannahme **grösstenteils**: alle GPIO, die nicht
Debug-Pins sind, stehen nach Reset auf **Analog** (hochohmig, kein
Pull) — das schliesst die Bootlader-UART-Pins PA11/PA12 ein (Register
`GPIOA_MODER`, Reset-Wert `0xEBFF FFFF`; die betroffenen Bits für
MODE13/MODE14 = `10` (AF) sind nur PA13/PA14, alle anderen Bits bleiben
`11` = Analog). Die **gemeinsame Sendeleitung des Bootlader-UART ist damit
im Reset tatsächlich hochohmig**, wie der Entwurf voraussetzt.

**Einschränkung, die dokumentiert gehört:** PA14 — physisch BOOT0 — ist
zugleich SWCLK und liegt nach Reset **nicht** auf Analog, sondern in
Alternate-Function-Modus mit aktivem internem Pull-down (RM0490 §6.4.1,
Register `GPIOx_PUPDR`; Widerstandswert laut Datenblatt DS13866 Tabelle
„I/O static characteristics": `RPD` typ. 40 kΩ, min. 25 kΩ, max. 55 kΩ).
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

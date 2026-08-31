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
`nBOOT0` zusammen mit `nBOOT_SEL`/`BOOT_LOCK` (Boot0-Signalquelle
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
- BOOT0 ist physisch **PA14**, zugleich SWCLK; nach Reset liegt dort der
  interne Pull-down von typ. 40 kΩ (Beleg 2, RM0490 §6.3.1 und §6.4.4,
  Widerstandswert DS13866 Tabelle 49). Für die globale
  Flash-Modus-Leitung einplanen, kein Blocker.
- Kein `PY32F002A`-Rückfall nötig — STM32C011F6P6 ist bestückbar.

## Beleg 4 — Auswahlkette: Flipflop und Gatter (Aufgabe 3)

**Quelle:** `tools/kette.py` und `tests/test_kette.py`. Die Kette ist ein
**Schieberegister** über den ganzen Stapel: jedes Modul trägt ein
D-Flipflop, alle hängen an derselben Taktleitung `SEL_CLK` vom Sockel.

| Signal | Bedeutung |
|---|---|
| `SEL_IN` | D des Flipflops — Ausgang des Moduls darüber (oberstes Modul: vom Sockel) |
| `SEL_CLK` | Takt, global vom Sockel; alle Flipflops übernehmen gleichzeitig |
| `Q` | „dieses Modul ist ausgewählt"; zugleich `SEL_OUT` an das Modul darunter |
| `FLASH_MODE` | global vom Sockel |

Die Ausgänge an den Modul-MCU:

| Ausgang | Gleichung |
|---|---|
| RESET | `flash_mode AND (NOT Q)` |
| BOOT0 | `flash_mode AND Q` |
| SEL_OUT | `Q` (der Flipflop-Ausgang selbst, ohne Gatter) |

Damit bleiben neben dem Flipflop nur drei Gatterfunktionen:

1. **Invertierung Q** → 1× NOT-Gatter (für RESET)
2. **RESET = flash_mode ∧ ¬Q** → 1× 2-Input AND-Gatter
3. **BOOT0 = flash_mode ∧ Q** → 1× 2-Input AND-Gatter

`SEL_OUT` braucht kein eigenes Gatter mehr: es ist der Flipflop-Ausgang.
Die frühere Fassung hatte dafür ein AND (`¬flash_mode ∧ sel_in`) — und
genau das machte die Kette unbrauchbar, weil `SEL_OUT` im Flash-Modus
immer 0 war.

**Bauteilwahl — Einzelgatter statt Multi-Gate-ICs:** Vier
Funktionsblöcke in grossen SOIC-14-Gehäusen bedeuten viel Verschnitt auf
einer Platine mit Kleinheit-Anspruch. Die empfohlene Lösung nutzt
Einzel- und Doppelgatter aus der CMOS-Familie 74LVC1G/74LVC2G in
kleinen SMD-Gehäusen (SC-70, SOT-353, SOT-363 — welches genau, sagt
erst das Datenblatt des gewählten Typs).

| IC | Funktion | Typ (Kandidat) | LCSC | Aufgabe |
|---|---|---|---|---|
| IC1 | D-Flipflop, flankengetaktet | 74LVC1G175 oder 74LVC1G80 | — | hält `Q`; D = `SEL_IN`, Takt = `SEL_CLK` |
| IC2 | Doppel-AND-Gatter (2× 2-Input) | 74LVC2G08 | — | RESET und BOOT0 |
| IC3 | Einzel-Inverter (1-Input NOT) | 74LVC1G04 | — | invertiert `Q` für RESET |

**Spezifikation:**
- IC1: CMOS-Einzel-D-Flipflop mit Flankentakt aus der 74LVC-Familie
- IC2: CMOS-Doppel-AND-Gatter (2-Input) aus der 74LVC-Familie
- IC3: CMOS-Einzel-Inverter aus der 74LVC-Familie
- Alle drei als Einzelgatter-Gehäuse derselben Familie, damit Pegel und
  Versorgung zusammenpassen

**Was hier bewusst NICHT steht:** keine LCSC-Nummer, kein Gehäusemass,
keine Betriebsspannung, kein Strombedarf. Für keinen dieser drei Typen
lag beim Schreiben ein Datenblatt oder eine Produktseite vor; auch die
Typennummern sind Kandidaten aus der Familie, nicht geprüfte
Bestellnummern. Diese Angaben gehören in die Beschaffungsphase, aus dem
Datenblatt und der Produktseite — nicht aus dem Gedächtnis. (Der Satz
„picoampere static, nanoampere dynamic" stand hier früher und war
zusätzlich sachlich verdreht: der dynamische Strom eines CMOS-Gatters
liegt über dem statischen, nicht darunter.)

**Zwei Punkte fürs Datenblatt-Studium in der Beschaffungsphase:**

- Bringt das Flipflop einen **invertierten Ausgang `Q̄`** mit, entfällt
  IC3 — der Inverter ist dann schon im Gehäuse.
- Bringt es einen **asynchronen Reset**, kann der Sockel das ganze
  Schieberegister mit einer Leitung leeren, statt es leerzutakten. Ohne
  Reset muss er nach dem Durchzählen so oft mit 0 takten, wie der Stapel
  hoch ist, damit keine 1 im Register stehen bleibt. Beides funktioniert;
  der Reset wäre nur eine Leitung wert, wenn ein Typ ihn ohnehin hat.

**Auswahlkriterium aus der Einschalt-Analyse:** Ein reales Flipflop hat
beim Einschalten einen undefinierten Zustand, nicht `Q=0`. Der Sockel
muss die Kette deshalb leertakten, bevor er `FLASH_MODE` das erste Mal
auf 1 setzt (verbindliche Regel, siehe Design-Doc, Abschnitt „Bus und
Adressierung", „Einschaltzustand"). Ein Flipflop mit asynchronem
Löscheingang erspart dieses Leertakten, wenn der Sockel ihn beim Start
ansteuert — das macht den asynchronen Löscheingang zu einem echten
Auswahlkriterium bei der Typwahl, nicht nur zu einer Ersparnis.

**Verfügbarkeit:** LCSC und JLCPCB führen die Serien 74LVC1G und 74LVC2G
als Standard-Logik. Eine konkrete Nummernvergabe wird bei der nächsten
Beschaffungs-Phase recherchiert (Constraint: keine LCSC-Nummer ohne
Produktseiten-Nachweis).

**Alternative: Decoder-Struktur (erwogen, nicht weiter verfolgt):** RESET und BOOT0 bilden
zusammen einen 1-aus-2-Decoder mit Freigabe (`flash_mode` als Freigabesignal, `Q` als
Adresseingabe). Ein spezialisierter Decoder-IC (z.B. 74LVC138 als 3-aus-8-Decoder) wäre für
zwei Ausgänge zu mächtig. Der Decoder-Ansatz wurde zugunsten der einfachen Einzelgatter-Lösung
nicht weiter verfolgt.

**Klarstellung zu MCU-Verhalten:** Der Kommentar „Ausgänge hochohmig" in `kette.py` bezieht sich
auf die GPIO-Pins des **Modul-MCU im Reset-Zustand** — nicht auf die Ausgänge der Logik-ICs. Die
Gatterausgänge arbeiten aktiv in Gegentaktverstärkung (totem pole) und treiben die Reset- und
BOOT0-Eingänge des MCU mit definierten High- und Low-Pegeln. Nur die GPIO-Pins des im Reset
gehaltenen MCU sind hochohmig, weil der MCU keinen Taktgenerator hat und keine Ausgänge aktiv
treibt.

**Wie die Auswahl wandert:** `SEL_OUT` ist immer `Q` — es wird nichts
angehalten und nichts blockiert. Weitergereicht wird ausschliesslich
durch den Takt:

1. Der Sockel legt `FLASH_MODE = 1` und eine **1** an `SEL_IN` des
   obersten Moduls und gibt einen Takt auf `SEL_CLK`. Modul 1 hat jetzt
   `Q = 1`: es ist wach und im Bootlader, alle anderen liegen im Reset.
2. Der Sockel legt **0** an und taktet erneut. Die 1 rückt in Modul 2;
   Modul 1 fällt zurück in den Reset. Es ist immer genau ein Modul
   ausgewählt, weil im Register immer genau eine 1 steht.
3. Nach so vielen Takten, wie der Stapel hoch ist, fällt die 1 unten
   heraus und niemand ist mehr ausgewählt. Daran erkennt der Sockel das
   Ende des Stapels — und weil er mitgezählt hat, kennt er zugleich die
   Adressen.

Der entscheidende Fall, den die frühere Beschreibung ausliess: **ein
ausgewähltes Modul reicht seine 1 sehr wohl weiter** — an das D des
Moduls darunter. Wach wird das darunterliegende Modul davon nicht,
denn D wirkt erst mit der nächsten Taktflanke, und dann ist das obere
Modul nicht mehr ausgewählt. Zwei gleichzeitig wache MCU auf der
gemeinsamen Sendeleitung kann es dadurch nicht geben, solange der
Sockel nur eine einzige 1 einschiebt.

Ausserhalb des Flash-Modus (`FLASH_MODE = 0`) sind RESET und BOOT0 beide
0: **alle** Module laufen, unabhängig davon, was im Schieberegister
steht. Das ist der Normalbetrieb und der häufigste Fall.

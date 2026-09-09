# Bauteil-Belege Dimmer-Module (1/3/4 Kanäle)

Die Dimmer übernehmen das MCU-Nest wörtlich vom Motormodul; deren
Nummern sind in `bauteile.md` / `bauteile-1b.md` belegt. Hier stehen
nur die Positionen, die es NUR auf den Dimmern gibt bzw. die für die
Bestückungs-Bestellung 2026-09-04 neu gesichtet wurden. Regel wie
immer: eine LCSC-Nummer steht nur hier, wenn die Produktseite selbst
geöffnet und gelesen wurde.

| Position | Bauteil | Gehäuse | LCSC | gesichtet | Beleg |
|---|---|---|---|---|---|
| Freilaufdiode D1–D4 | SS36**C** (MDD/Microdiode) | **SMC (DO-214AB)** | C16237 | ja | LCSC-Produktseite `lcsc.com/product-detail/C16237.html` (Rohdaten: „SMC(DO-214AB)", 60 V, 3 A, „700mV@3A", Lager 102 720). **Falle:** das MDD-Teil mit dem nackten Namen „SS36" (C16015) ist laut seiner Produktseite **SMA (DO-214AC)** — falsches Gehäuse für unsere Pads. Das onsemi-SS36 in SMC (C391251) existiert, hatte am Recherchetag aber nur 847 Stück Lager bei ~0,37 $ |
| Gate-Vorwiderstand RG1–RG4 | 0805W8F1000T5E (UNI-ROYAL), 100 Ω ±1 % | 0805 | C17408 | ja | LCSC-Produktseite `lcsc.com/product-detail/C17408.html` (Rohdaten: „100Ω", „±1%", „125mW", „150V", Lager 8 236 700). Gleiche geprüfte Baureihe wie der 10-kΩ-Beleg C17414 in `bauteile-1b.md` |
| Stütz-Elko C12 (auch C3 Sockel, C12 Motor) | GR227M035F12RR0VL4FP0 (Chengx) | radial D8×L12, RM 3,5 | C45078 | ja | LCSC-Produktseite `lcsc.com/product-detail/…C45078.html` (Rohdaten: „220µF ±20%", „35V", „8mm × 12mm", „Lead Pitch: 3.5mm", „3000hrs@105℃", Lager 123 720) |
| Schraubklemme J5–J8 | KF350-3.5-2P (Cixi Kefa) | THT, RM 3,5, 2P | C474892 | ja | LCSC-Produktseite `lcsc.com/product-detail/C474892.html` (Rohdaten: „3.5mm", „1x2P", „10A", „300V", „18–24 AWG", M2-Schraube, Lager 7 100). **Ehrlich vermerkt:** das ist ein Klon auf dem Raster des Phoenix-PT-1,5/2-3,5-H-Footprints, keine Maßzeichnungs-Gegenprüfung Pad für Pad — Sitz im JLC-Bestückungs-Preview kontrollieren. Der Phoenix-Originaltyp war bei LCSC nicht auffindbar |

## Nachtrag 2026-09-04: JLC-Matching-Runde 2 (Lagerprobleme)

JLCs Abgleich traf drei Widerstandszeilen auf lagerleere Teile (Qty 0)
und hatte vom Kanal-FET NCE6050KA nur noch 3 Stück; die LCSC-Seite
C96013 meldet „Out of Stock". Ersatz, jeweils Produktseite gesichtet:

| Position | Bauteil | LCSC | Beleg |
|---|---|---|---|
| Kanal-FET Q1–Q4 | **NCE6020AK** (NCE), TO-252-2L — **ersetzt den ausverkauften NCE6050KA** | C108639 | LCSC-Produktseite `lcsc.com/product-detail/C108639.html` (Rohdaten: „60V", „20A", „40mΩ@4.5V", „<35mΩ @ VGS = 10V", Gate-Schwelle „2.5V", Lager 6 010). Gleiches V_GS(th)-Limit wie der 6050KA → das 3,3-V-Ansteuerargument (Herleitung in `tools/sch/dimmermodul.py`) bleibt konservativ tragfähig: 40 mΩ × (3 A)² = 0,36 W je Kanal. **Ehrlich vermerkt:** die Espace-Felderfahrung gilt wörtlich nur für den 6050KA — am ersten Board Temperatur nachmessen |
| Kennwiderstand 1,5 kΩ (R100 Dimmer4) | 0805W8F1501T5E (UNI-ROYAL) | C4310 | LCSC-Produktseite `lcsc.com/product-detail/C4310.html` (Rohdaten: „1.5kΩ", „±1%", „125mW", Lager 376 800); JLC-**Basic** laut Basic-Parts-Liste |
| Kennwiderstand 680 Ω (R101, R100 Motor) | 0805W8F6800T5E (UNI-ROYAL) | C17798 | LCSC-Produktseite `lcsc.com/product-detail/…C17798.html` (Rohdaten: „680Ω", „±1%", „125mW", Lager 1 216 700); JLC-Basic |
| 100 kΩ (R102, RP1–RP4) | 0805W8F1003T5E (UNI-ROYAL) | C149504 | JLCPCB-Produktseite `jlcpcb.com/partdetail/160838-0805W8F1003T5E/C149504` (Bestückungsbibliothek); LCSC führt denselben Widerstand doppelt — C17407 („SMT-Geschäft vorbehalten", Lager 185 900 im Retail) meldete im JLC-Dialog trotzdem 35 shortfall, C149504 ist der bestückbare Eintrag. JLCs Auto-Match C5713386 hatte Lager 0 |
| 0-Ω-Brücke (R101 Motor, R100 Dimmer1) | 0805W8F0000T5E (UNI-ROYAL) | C17477 | LCSC-Produktseite `lcsc.com/product-detail/C17477.html` (Rohdaten: „0Ω Jumper", „125mW", Lager 6 207 600) |

## Nachtrag 2026-09-07: JLC-Basic-Festlegung der Kleinteile (Runde 3)

Die „Extended components fee" (3,07 $ je Nicht-Basic-BOM-Zeile) machte
sichtbar, welche Zeilen JLCs Beschreibungs-Matching dem Zufall
überließ. Sichtung per headless Chrome direkt aus dem Seiten-JSON der
JLC-Teileseiten (`componentLibraryType`, `overseasStockCount`,
`noBuyReason`), alle am 2026-09-07:

| Teil | LCSC | Befund |
|---|---|---|
| 100 nF 50 V X7R 0805 (C100 u. a.) | C49678 | YAGEO CC0805KRX7R9BB104, „base", Lager 20,6 Mio |
| 1 µF 50 V X7R 0805 (C101) | C28323 | Samsung CL21B105KBFNNNE, „base", Lager 3,9 Mio |
| 22 µF 25 V X5R 0805 (C2 Sockel) | C45783 | Samsung CL21A226MAQNNNE, „base", Lager 5,2 Mio |
| 4,7 kΩ 0805 (R1/R2 Sockel, R20/R21 Motor) | C17673 | 0805W8F4701T5E, „base", Lager 6,6 Mio |
| 100 kΩ — Bestätigung | C149504 | **„base", Lager 5,2 Mio** — der Karteileichen-Match C17407 ist „expand" UND `noBuyReason: "This product is no longer manufactured."` |
| 100 kΩ — verworfen | C2889441 | VO-Teil aus der Websuche: „expand", Lager 0, ebenfalls abgekündigt |

Ergebnis: Alle Widerstands- und Kondensator-Zeilen aller Boards sind
Basic (keine Gebühr, deterministisches Auto-Match). Die verbleibenden
8 Extended-Zeilen des Dimmer4 sind sämtlich Halbleiter ohne
Basic-Äquivalent — die ~24,56 $ Gebühr sind das Minimum für dieses
Design.

Die übrigen Dimmer-BOM-Nummern (STM32C011F6P6 C5456198, 74LVC-Gatter
C202238/C206109/C7832, IRFR5305 C2624, SMCJ30A C340696, 10 kΩ C17414)
sind in `bauteile.md` / `bauteile-1b.md` bzw. im LED-Dimmer-Altprojekt
belegt und in `tools/jlc.py` als Konstanten übernommen. Der dort
belegte NCE6050KA (C96013) bleibt als Referenz stehen, wird aber seit
dem Nachtrag oben nicht mehr bestückt.

## Nachtrag 2026-09-09: v2-Versorgungszelle (Task 9, Fertigungsdaten)

Mit v2 trägt **jedes** Modul (Motor, Dimmer1/3/4) die Versorgungszelle
aus `tools/sch/versorgung.py` (J90/Q90/R90/R91/D90/C90/U90/C91/D91,
löst den bisherigen board-eigenen Verpolschutz Q1/Q10/D1/D10/C12 ab —
per `pos.csv` nachgemessen, keiner dieser alten Bezeichner existiert
mehr). Für `tools/jlc.py` neu **zusammengesetzt**, aber **keine neue
LCSC-Sichtung** nötig — alle vier Nummern sind bereits an anderer
Stelle in diesem Projekt mit Produktseite belegt:

| Bauteil (Zelle) | LCSC | bereits belegt in |
|---|---|---|
| J90 KF350-3.5-2P | C474892 | `tools/jlc.py` (Bestellrunde 2026-09-04) |
| U90 K7805-1000R3 | C909765 | `tools/sch/sockelplatine.py` / `tools/jlc.py` (Sockel-U2) |
| D91 SS36C | C16237 | `tools/jlc.py` (Dimmer-Kanaldioden D1–D4) |
| C90 220µF Elko | C45078 | `tools/jlc.py` (Sockel-C3 / bisheriges C12) |

Q90 (IRFR5305, C2624), D90 (SMCJ30A, C340696), R90/R91 (10 kΩ,
C17414), C91 (22µF, C45783) sind ebenfalls reine Wiederverwendungen
bereits belegter Nummern (s. Konstanten in `tools/jlc.py`).

**Eine echte neue Sichtung diese Runde:** U6/U7 (Motormodul) wechseln
von SN74LVC1G06 (C7828, invertierend — für den Ruhestrom-Notaus falsch
gepolt, s. `tools/sch/motormodul.py::INVERTER_WERT`) auf **SN74LVC1G07
(C7830)**, nichtinvertierender Puffer mit Open-Drain-Ausgang,
pinidentisch (SOT-353/SC-70-5, gleicher Footprint wie U3/U103). Die
Quelle in `motormodul.py` leitet C7830 aus der LCSC-Nummernfolge der
Nachbartypen her (C7828 = 1G06, C7832 = 1G08) statt aus einer selbst
gesichteten Produktseite — das wäre nach der bindenden Regel dieses
Projekts eigentlich ein Lückenfall (Feld leer lassen). Für diese
Aufgabe **selbst nachgesehen** (WebFetch auf
`lcsc.com/product-detail/C7830.html`, 2026-09-09): Seite bestätigt
MPN **SN74LVC1G07DCKR**, Gehäuse **SC-70-5**, Beschreibung „Single
Buffer/Driver With Open-Drain Output", 1,65–5,5 V, 32 mA Senkstrom —
die Nummer ist korrekt, die Herleitung war nur unvollständig belegt.
`tools/jlc.py` führt C7830 jetzt als `LCSC_1G07`-Konstante.

Unbestückt und ohne LCSC-Bedarf: J95/J96 (Randpad-Reihen, SMD-Lötpads
auf B.Cu, `stack_spec.RANDPADS`) und J105 (zweiter Stapelstecker,
Pico-Pins 21–40 — vorher Teil eines einzelnen 2×20-Steckers J100,
jetzt zwei 1×20-Buchsen) — beide von Hand im gesteckten Verbund
bestückt, s. `hardware/fertigung/*/UNBESTUECKT.txt`.

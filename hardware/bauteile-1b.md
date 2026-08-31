# Bauteilwahl Etappe 1b: Stapelstecker, Auswahlketten-Logik, Leistung, Klemmen

**Stand:** 2026-08-31. Bestand und Preise bei LCSC/JLCPCB ändern sich laufend;
die hier genannten Zahlen sind Stichproben vom Recherchezeitpunkt, keine
Garantie. Vorlage und Sorgfaltsmassstab: `hardware/bauteile.md` (Etappe 1a).

## Bauteiltabelle

**Nachtrag 2026-08-31 (Prüfung durch den Auftraggeber):** Der 2×20-Signalstecker
ist nach der Entscheidung des Auftraggebers **kein** Buchse/Stift-Paar mehr,
sondern ein echter Stapelstecker (Buchse mit durchgehendem Stift). Die
ursprünglichen zwei Zeilen dafür (Buchse C2977589 / Stift C50980) stehen unten
als **verworfen** markiert, ersetzt durch die neue Stapelstecker-Zeile.
Begründung und Rechnung: Beleg 1 (überarbeitet) und der neue Abschnitt
„Beleg 6 — Entscheidung Stapelstecker". Die beiden verworfenen Bauteile
bleiben sichtbar stehen, weil ihre Zahlen (6,0/3,0 mm bzw. 8,5 mm) jetzt die
Grundlage des neuen, eigenständigen Kettensteckers sind.

| Zweck | Typ | Bauform | LCSC | geprüft | Quelle |
|---|---|---|---|---|---|
| Signalstecker, Buchse (oben, 2×20) — **verworfen, s. u.** | BOOMELE/ZHOURI-Familie, 2,54 mm Buchsenleiste | THT, Gehäusehöhe 8,5 mm über Platine | C2977589 | verworfen (Bauform an sich geprüft) | LCSC-Produktseite `lcsc.com/product-detail/C2977589.html`; Datenblatt (ZHOURI, Rev. ZRLCGY2025-06-17-CJ A/1), Masszeichnung „8,5±0,2"; JLCPCB-Produktseite `jlcpcb.com/partdetail/2.54-2*20/C2977589` (SMT Assembly, Economic/Standard PCBA) |
| Signalstecker, Stift (unten, 2×20) — **verworfen, s. u.** | BOOMELE 2,54 mm Stiftleiste, gerade | THT, Stift 6,0 mm oberhalb / 3,0 mm unterhalb des Isolierkörpers (Gesamtlänge 9,0 mm) | C50980 | verworfen (Bauform an sich geprüft) | LCSC-Produktseite `lcsc.com/product-detail/Male-Header_Made-in-China-2-54mm-2-20P-Header_C50980.html`; Datenblatt (东莞康孚电子), Masszeichnung „3.0" / „6.0"; JLCPCB-Produktseite `jlcpcb.com/partdetail/BOOMELE-2_54mm2_20PHeader/C50980` (SMT Assembly, Economic/Standard PCBA) |
| **Stapelstecker, Signal (2×20) — ersetzt die beiden Zeilen oben** | ZHOURI/BOOMELE „PC104-2*NA+1": Buchse mit durchgehendem Stift | THT, Gehäuse 8,5 mm über Platine, Stift 12,46 mm unterhalb des Gehäuses (Gesamtlänge 23,50 mm), 3 A/Kontakt | C35165 | ja | LCSC-Produktseite `lcsc.com/product-detail/Pin-Header-Female-Header_Boom-Precision-Elec-2-54mm-2-20P_C35165.html`; Datenblatt (ZHOURI/上海康司玛, Zeichnung „PC104-2*NA+1"), Masszeichnung „8,5±0,2" / „12,46±0,2" / „23,50"; JLCPCB-Produktseite `jlcpcb.com/partdetail/BOOMELE-2_54_2_20PFemaleLongPC104/C35165` (SMT Assembly, Economic/Standard PCBA) |
| ~~Kettenstecker, Buchse (oben, 1×2, trägt SEL+GND)~~ — **verworfen 2026-08-31 (Aufgabe 5e): zwei bedrahtete Hälften können sich am selben Ort keine Bohrungen teilen, s. Beleg 13** | XFCN PM254V-11-02-H85 | THT, 8,5 mm über Platine, 3 A/Kontakt, 250 V | C541849 | verworfen (Bauform an sich geprüft) | LCSC-Produktseite `lcsc.com/product-detail/C541849.html` (Rohdaten: „3A", „250V", „8.5mm"); JLCPCB-Produktseite `jlcpcb.com/partdetail/XFCN-PM254V_1102H85/C541849` (SMT Assembly, Economic/Standard PCBA) — laut Herstellerbezeichnung passend zur XFCN-PZ254-Reihe |
| ~~Kettenstecker, Stift (unten, 1×2)~~ — **verworfen 2026-08-31 (Aufgabe 5e): zwei bedrahtete Hälften können sich am selben Ort keine Bohrungen teilen, s. Beleg 13** | XFCN PZ254V-11-02P | THT, Stift 6,0 mm oberhalb / 3,0 mm unterhalb des Isolierkörpers, 3 A/Kontakt, 250 V | C492401 | verworfen (Bauform an sich geprüft) | LCSC-Produktseite `lcsc.com/product-detail/Pin-Header-Female-Header_XFCN-PZ254V-11-02P_C492401.html` (Rohdaten: „6mm"/„3mm" Steck-/Lötpin); JLCPCB-Produktseite `jlcpcb.com/partdetail/XFCN-PZ254V_1102P/C492401` (SMT Assembly, Economic/Standard PCBA) |
| ~~Leistungsstecker, Buchse (oben, 2×2)~~ — **verworfen 2026-08-31 (Aufgabe 5e): zwei bedrahtete Hälften können sich am selben Ort keine Bohrungen teilen, s. Beleg 13** | gleiche ZHOURI-Familie, 2,54 mm | THT, 8,5 mm über Platine, 2,5 A/Kontakt | C2977590 | verworfen (Bauform an sich geprüft) | LCSC-Produktseite `lcsc.com/product-detail/Female-Headers_ZHOURI-2-54-2-2_C2977590.html` (Rohdaten: „2.5A", „8.5mm insulation height") |
| ~~Leistungsstecker, Stift (unten, 2×2)~~ — **verworfen 2026-08-31 (Aufgabe 5e): zwei bedrahtete Hälften können sich am selben Ort keine Bohrungen teilen, s. Beleg 13** | gleiche BOOMELE-Familie, 2,54 mm | THT, 6,0/3,0 mm, 3 A/Kontakt | C66690 | verworfen (Bauform an sich geprüft) | LCSC-Produktseite `lcsc.com/product-detail/Male-Header_Double-Rows2-2p-pitch2-54mm_C66690.html` (Rohdaten: „3A", „6mm"/„3mm") |
| **Kettenstecker, Buchse (oben, 1×2) — ersetzt die verworfene Zeile** | Buchsenleiste 1×2, 2,54 mm, SMD senkrecht, Isolationshöhe 8,5 mm, ≥ 1 A | **SMD**, 8,5 mm über Platine | *(offen — keine gesichtete Nummer)* | Bauform ja, Polzahl nein | Bauform belegt an C261072 (BOOMELE 2.54-2\*5P, „Surface mount, vertical", „Insulation Height: 8.5mm", „Current Rating: 2.5A") und C52611 (BOOMELE 2.54-2\*25P, „SMD header 2\*25P 2.54mm H=8.5mm Gold-plated"); in 1×2 auf **keiner** Produktseite gesehen — deshalb kein LCSC-Feld, s. Beleg 13.4 |
| **Kettenstecker, Stift (unten, 1×2) — ersetzt die verworfene Zeile** | Stiftleiste 1×2, 2,54 mm, SMD senkrecht, Isolierkörper ≤ 2,5 mm, Steckstift 6,0 mm | **SMD**, 8,5 mm unter der Platine (2,5 + 6,0) | *(offen — keine gesichtete Nummer)* | Bauform ja, Polzahl nein | Bauform belegt an C919361 (2×2), C192300 (2×4), C124390/C124391 (Ckmtw, 2×3/2×5); in 1×2 nicht gesehen, s. Beleg 13.4 |
| **Leistungsstecker, Buchse (oben, 2×2) — ersetzt die verworfene Zeile** | Buchsenleiste 2×2, 2,54 mm, SMD senkrecht, Isolationshöhe 8,5 mm, ≥ 2,5 A/Kontakt | **SMD**, 8,5 mm über Platine | *(offen — keine gesichtete Nummer)* | Bauform ja, Polzahl nein | wie die Zeile darüber: C261072 / C52611; in 2×2 nicht gesehen, s. Beleg 13.4 |
| **Leistungsstecker, Stift (unten, 2×2) — ersetzt die verworfene Zeile** | BOOMELE „2.54-2\*2P" | **SMD senkrecht**, Isolierkörper 2,5 mm, Steckstift 6,0 mm, 3 A/Kontakt | **C919361** | ja | LCSC-Produktseite `lcsc.com/product-detail/C919361.html` (Rohdaten: „Surface Mount (SMD), Vertical", „Insulation Height: 2.5mm", „Mating Pin Length: 6mm", „Current Rating: 3A", 28 460 auf Lager) |
| D-Flipflop, asynchroner Löscheingang | SN74LVC1G175DCKR (TI) | SOT-363-6 (SC-70-6), 6 Pins | C202238 | ja | LCSC-Produktseite `lcsc.com/product-detail/74-Series_TI_SN74LVC1G175DCKR_SN74LVC1G175DCKR_C202238.html`; JLCPCB-Produktseite `jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G175DCKR/C202238` (SMT Assembly, Economic/Standard PCBA, MSL 1); Primärquelle TI-Datenblatt `SN74LVC1G175`, Dok. SCES560G (März 2004, revidiert Juni 2015), Abschnitt 3 „Description" und Abschnitt 5 „Pin Configuration and Functions" (Gehäuse „DCK Package, 6-Pin SC70", Pin 6 = `CLR`) |
| Gatter Dual-NAND (NOT via NAND(Q,Q), NRST) — **ersetzt die Zeilen NOT+NAND unten, s. Nachtrag 2026-08-31 (2. Runde)** | SN74LVC2G00DCUR (TI) | **VSSOP-8 (0,5 mm Pitch), 8 Pins — NICHT SOT-363**, s. Anmerkung unten | C206109 | ja | LCSC-Produktseite `lcsc.com/product-detail/C206109.html` (Rohdaten: Gehäuse „VSSOP-8-0.5mm"); TI-Datenblatt `SN74LVC2G00`, „Dual 2-Input Positive-NAND Gate" |
| ~~Gatter NOT (Invertierung Q)~~ — **verworfen, s. Nachtrag 2026-08-31 (2. Runde): ersetzt durch eine Einheit des Dual-NAND (Eingänge kurzgeschlossen)** | SN74LVC1G04DCKR (TI) | SOT-353 (SC-70-5), 5 Pins | C8207 | ja (Bauform an sich geprüft, aber verworfen) | LCSC-Produktseite `lcsc.com/product-detail/C8207.html`; JLCPCB-Produktseite `jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G04DCKR/C8207` (SMT Assembly, Economic/Standard PCBA, MSL 1) |
| ~~Gatter NAND (NRST)~~ — **verworfen, s. Nachtrag 2026-08-31 (2. Runde): ersetzt durch die zweite Einheit desselben Dual-NAND** | SN74LVC1G00DCKR (TI) | SOT-353 (SC-70-5), 5 Pins | C8185 | ja (Bauform an sich geprüft, aber verworfen) | LCSC-Produktseite `lcsc.com/product-detail/C8185.html` (Rohdaten: „SOT-353“, „ultra-small DPW package… 0.8 mm × 0.8 mm“); TI-Datenblatt `SN74LVC1G00`, „Single 2-Input Positive-NAND Gate“ |
| Gatter AND (BOOT0) | SN74LVC1G08DCKR (TI) | SOT-353 (SC-70-5), 5 Pins | C7832 | ja | LCSC-Produktseite `lcsc.com/product-detail/C7832.html` (Rohdaten: „SC-70-5“, „ultra-small DPW package… 0.8 mm × 0.8 mm“); TI-Datenblatt `SN74LVC1G08`, „Single 2-Input Positive-AND Gate“ |
| ~~Gatter Dual-AND (RESET, BOOT0) — **verworfen, s. Nachtrag 2026-08-31**~~ | 74LVC2G08GT,115 (Nexperia) | XSON-8 (1×2 mm), 8 Pins | C548580 | ja (Bauform an sich geprüft, aber verworfen) | JLCPCB-Produktseite `jlcpcb.com/partdetail/Nexperia-74LVC2G08GT115/C548580` (SMT Assembly, Economic/Standard PCBA, MSL 1) |
| 5-V-Regler | K7805-2000R3 | SIP-3 | C2931187 | ja | bereits geprüft in Etappe 1a / LED-Dimmer-Projekt, siehe `hardware/bauteile.md` — hier unverändert übernommen, nicht neu recherchiert |
| Klemme 2-polig | DB128L-5.08-2P-GN-S | THT, 5,08 mm | C395868 | ja | bereits geprüft in Etappe 1a / LED-Dimmer-Projekt — unverändert übernommen |
| Klemme 3-polig | DB128L-5.08-3P-GN-S | THT, 5,08 mm | C395869 | ja | LCSC-Produktseite `lcsc.com/product-detail/C395869.html` (16 A, 300 V, M2-Schraube, 12–22 AWG); JLCPCB-Produktseite bestätigt (DORABO-Familie, SMT/Wave-Assembly, Economic/Standard PCBA) — selbe Farbe/Baureihe wie die bereits geprüfte 2-polige Klemme |
| ~~Schaltdiode (Notaus-Verriegelung, Aufgabe 5)~~ — **verworfen, s. Nachtrag 2026-08-31 (Aufgabe-5-Fix-1): eine Si-Diode ist für den gezogenen Ruhepegel der NOTAUS-Sammelleitung zu hochohmig, s. Beleg 10** | 1N4148W (ST/Semtech) | SOD-123 | C81598 | ja (Bauform an sich geprüft, aber verworfen) | LCSC-Produktseite `lcsc.com/product-detail/Switching-Diode_ST-Semtech-1N4148W_C81598.html` (Rohdaten: Gehäuse „SOD-123", `Vf "1V@50mA"`); JLCPCB-Produktseite `jlcpcb.com/partdetail/ST-1N4148W/C81598` bestätigt SMT-Assembly („Economic and Standard" PCBA, MSL 3) |
| ~~Koppeldiode NOTAUS-Sammelleitung (D3/D4, Aufgabe-5-Fix-1)~~ — **verworfen, s. Nachtrag 2026-08-31 (Aufgabe 5d): der Notaus-Eingang arbeitet jetzt im Ruhestrom, der Bus wird von einem Open-Drain-Ausgang gezogen; eine Diode IN REIHE dazu liesse null Reserve gegen V_IL, s. Beleg 11. Die Grenzwerte bleiben stehen, weil die Gegenproben im Test mit ihnen rechnen** | BAT54W (YANGJIE), Schottky | SOD-123 (gleicher Footprint wie bisher) | C699107 | ja | LCSC-Produktseite `lcsc.com/product-detail/Schottky-Barrier-Diodes-SBD_Yangzhou-Yangjie-Elec-Tech-BAT54W_C699107.html` (Rohdaten: Hersteller „YANGJIE", Gehäuse „SOD-123", 30 V, 200 mA, Leckstrom „2µA@25V"; Bestand am Recherchetag 440 Stück — **wenig, vor der Bestellung prüfen**). Grenzwerte für die Pegelrechnung aus dem Vishay-Typdatenblatt `BAT54W`, Dok. **86408, Rev. 1.0 vom 20-Nov-2023**, Tabelle „ELECTRICAL CHARACTERISTICS" (T_amb = 25 °C): V_F ≤ 240 mV @ 0,1 mA, ≤ 320 mV @ 1 mA, ≤ 400 mV @ 10 mA, I_R ≤ 2 µA @ 25 V. **Ehrlich vermerkt:** das Yangjie-eigene PDF war über LCSC nicht als PDF abrufbar (die Datenblatt-URL liefert eine HTML-Seite); die zitierten Grenzwerte sind die des JEDEC-Typs BAT54W bei Vishay, nicht die von Yangjie selbst. Vor der Fertigung mit dem Yangjie-Datenblatt gegenprüfen |
| Verriegelungsgatter NOTAUS→nSLEEP (U3, Aufgabe-5-Fix-1) | SN74LVC1G08DCKR (TI) — **zweite Verwendung desselben Bauteils wie U103**, keine neue Nummer | SOT-353 (SC-70-5), 5 Pins | C7832 | ja | dieselbe geprüfte Produktseite wie die BOOT0-Zeile oben; Grenzwerte für die Pegelrechnung aus dem TI-Datenblatt `SN74LVC1G08`, Dok. **SCES217AA** (April 1999, revidiert August 2026), Abschnitt 5.3 „Recommended Operating Conditions" (V_IH ≥ 2,0 V, V_IL ≤ 0,8 V bei V_CC = 3–3,6 V) und Abschnitt 5.5 „Electrical Characteristics" (V_OH ≥ V_CC − 0,15 V bei −100 µA, V_OL ≤ 0,1 V bei 100 µA, I_I ≤ ±5 µA) |
| **Kanaltreiber Notaus→NOTAUS (U6/U7, Aufgabe 5d)** — Inverter mit **Open-Drain**-Ausgang; ersetzt die verworfenen Koppeldioden D3/D4 | SN74LVC1G06DCKR (TI) | SOT-353 (SC-70-5), 5 Pins — **gleicher Footprint wie U3/U103** | C7828 | ja | LCSC-Produktseite `lcsc.com/product-detail/Inverters_Texas-Instruments-SN74LVC1G06DCKR_C7828.html` (Rohdaten: Gehäuse „SC-70-5“, Versorgung „1.65V~5.5V“, Ausgangstyp „Open-drain“, Eingang „Schmitt trigger“, „Output sink current 32mA max“, Ruhestrom „10µA max“, Bestand 3 600). Primärquelle TI-Datenblatt `SN74LVC1G06`, Dok. **SCES295AB** (JUNE 2000 – REVISED OCTOBER 2025), selbst geöffnet und gelesen: Abschnitt 5.3 „Recommended Operating Conditions“ (V_IH ≥ 2,0 V, V_IL ≤ 0,8 V bei V_CC = 3–3,6 V; I_OL ≤ 24 mA bei V_CC = 3 V), Abschnitt 5.5 „Electrical Characteristics“ (V_OL ≤ 0,1 V bei 100 µA, **≤ 0,4 V bei 16 mA / V_CC = 3 V**, ≤ 0,55 V bei 24 mA; I_I ≤ ±1 µA; I_off ≤ ±10 µA; I_CC ≤ 10 µA), Abschnitt 1 „Features“ („Schmitt trigger action on all ports“, „Ioff supports partial-power-down mode and back-drive protection“), Abschnitt 3 „Description“ (Ausgänge dürfen für „active-low wired-OR“ zusammengeschaltet werden) |
| **Optokoppler Sensoreingang und Notaus-Schleifen (U2 sowie U4/U5, Aufgabe 5d)** — U2 war seit dem Altprojekt bestückt, stand aber **nie in dieser Tabelle**; hier nachgetragen | PC817X1CSP9F (SHARP), Rangmarke **A** | SMD-4P (SMT-Gullwing) | C97308 | ja | LCSC-Produktseite `lcsc.com/product-detail/Optocouplers_Sharp-Microelectronics-PC817X1CSP9F_C97308.html` (Rohdaten: Hersteller „SHARP“, Gehäuse „SMD-4P“, „Current Transfer Ratio 600%;50%“, „Forward Current (If) 50mA“, „Forward Voltage (Vf) 1.2V“, „VCE Saturation 200mV@20mA,1mA“, „Isolation Voltage 5kV“, Bestand 10 640). Primärquelle SHARP-Datenblatt „PC817X Series“, **Sheet No. D2-A03101EN, Date Sep. 30. 2003**, selbst gelesen: „Absolute Maximum Ratings“ (I_F 50 mA, I_C 50 mA, P_tot 200 mW, T_opr −30…+100 °C), „Electro-optical Characteristics“ (V_F TYP 1,2 V / MAX 1,4 V bei I_F = 20 mA; I_CEO MAX 100 nA; **I_C MIN 2,5 mA bei I_F = 5 mA, V_CE = 5 V** = CTR ≥ 50 %; V_CE(sat) MAX 0,2 V bei I_F = 20 mA, I_C = 1 mA; t_r/t_f TYP 4/3 µs, MAX 18 µs), „Model Line-up“ (Rangmarke A = I_C 4,0–8,0 mA bei I_F = 5 mA). **Footprint-Auflage:** die Gullwing-Bauform misst laut „Outline Dimensions“ 6,5 × 4,58 mm Körper bei 10,0 mm Anschlussspanne und 7,62 mm Reihenabstand — der eingetragene Platzhalter `Package_SO:SOP-4_3.8x4.1mm_P2.54mm` passt **nicht**, s. Beleg 12 |
| **Schleifenwiderstände Notaus (R16–R19, Aufgabe 5d)** — 1206 statt 0805, weil sie einen äusseren Dauerkurzschluss aushalten müssen | 1206W4F3301T5E (UNI-ROYAL), 3,3 kΩ ±1 % | 1206, Dickschicht | C26032 | ja | LCSC-Produktseite `lcsc.com/product-detail/Chip-Resistor-Surface-Mount_Uniroyal-Elec-1206W4F3301T5E_C26032.html` (Rohdaten: Gehäuse „1206“, „3.3kΩ“, Toleranz „±1%“, Leistung „**250mW**“, max. Arbeitsspannung „200V“, TK „±100ppm/℃“, Bestand 164 200). Die 250 mW sind der Beleg für die Kurzschlussrechnung in Beleg 11 |

Von den acht in der ersten Fassung neu recherchierten Nummern (nicht sieben, wie dort irrtümlich stand — Zählfehler korrigiert) sowie den drei in dieser Nachbesserung hinzugekommenen (Stapelstecker C35165, Kettenstecker C541849/C492401) wurde jede auf einer echten LCSC- oder
JLCPCB-Produktseite gesichtet (Datenblatt-Zeichnung oder strukturierte
Attribute), nicht aus dem Gedächtnis übernommen. Wo eine WebSearch-Kurzfassung
unterwegs Angaben behauptete, die dem tatsächlich gelesenen Datenblatt
widersprachen (siehe Beleg 2), wurde die Kurzfassung verworfen und nur das
gelesene PDF verwendet.

## Beleg 1 — Steckerhöhe gegen den 15-mm-Plattenabstand

**Aufgabe:** `STAPEL_ABSTAND = 15.0` (`tools/stack_spec.py`) ist der Abstand
**Platinenoberkante zu Platinenoberkante** zweier benachbarter Platinen (so
die Aufgabenstellung). Jedes Modul hat oben eine Buchsenleiste, unten eine
Stiftleiste, in der Platine verbunden. Zu prüfen: passt eine gängige
Bauform von Stift- und Buchsenleiste zusammen mit 1,6 mm Platinendicke auf
genau diesen Abstand.

**Geometrie.** Modul A (oben) trägt die Stiftleiste an seiner Unterseite,
Modul B (darunter) die Buchsenleiste an seiner Oberseite. Der freie
Luftspalt zwischen der Unterseite von A und der Oberseite von B ist

    G = STAPEL_ABSTAND − Platinendicke = 15,0 mm − 1,6 mm = 13,4 mm

Dieser Spalt wird nicht von den Steckern getragen — das leisten die
Abstandsbolzen (Design-Doc, Abschnitt „Mechanik": „Abstandsbolzen tragen
die Mechanik; die Stecker haben nur elektrische Aufgaben"). Für die
Steckverbindung heisst das: Stiftlänge unterhalb der Platine (M) plus
Buchsenhöhe oberhalb der Platine (F) müssen den Spalt **überbrücken**
(M + F ≥ G), und der Stift darf nicht so lang sein, dass sein Schulter
(Isolierkörper) am oberen Rand der Buchse anschlägt, bevor die Bolzen die
Platinen auf Abstand gebracht haben (M ≤ G).

**Belegte Werte (aus Beleg-Datenblättern oben):**

- Stiftleiste C50980: Stift ragt **6,0 mm** unterhalb des Isolierkörpers
  heraus (das ist die Seite, die als Steckseite nach unten zeigt, wenn das
  Bauteil mit dem Lötschwanz — 3,0 mm — durch die Platine nach oben lötet).
  → **M = 6,0 mm**
- Buchsenleiste C2977589: Gehäusehöhe **8,5 mm** über der Platine, auf der
  sie sitzt. → **F = 8,5 mm**

**Rechnung:**

    M + F = 6,0 mm + 8,5 mm = 14,5 mm
    G     = 13,4 mm
    Einstecktiefe = (M + F) − G = 14,5 mm − 13,4 mm = 1,1 mm

    M = 6,0 mm ≤ G = 13,4 mm → kein Anschlagen der Stiftschulter, grosser
    Puffer (7,4 mm) in diese Richtung.

**Befund:** Die Kombination **mattet gerade so**, mit rechnerisch **nur
1,1 mm Einstecktiefe**. Das ist kein „passt nicht", aber ein dünner Rand:

- Beide Bauteile tragen ±0,2 mm Toleranz auf den relevanten Massen
  (zusammen bis zu ±0,4 mm), dazu kommen die Toleranz der Platinendicke
  (JLCPCB-Standard: 1,6 mm ± 10 %, also ±0,16 mm) und die Fertigungslänge
  der Abstandsbolzen. Im ungünstigsten Fall reduziert sich die
  Einstecktiefe auf nahe null oder wird rechnerisch negativ — dann stecken
  die Kontakte nicht mehr sicher ineinander.
- Für 2,54-mm-Stiftkontakte wird in der Verbindungstechnik üblicherweise
  eine Mindest-Einstecktiefe von einigen mm für zuverlässigen Kontaktdruck
  und Selbstreinigung durch Wischen empfohlen; das ist allgemeines
  Auslegungswissen aus der Steckverbinder-Praxis, keine Angabe aus den
  hier gelesenen Datenblättern — beide Datenblätter machen dazu keine
  Aussage.
- Eine gründliche Suche nach einer **passenderen Standard-Buchse** (grösser
  als 8,5 mm, aber ohne durchgehenden Einzelstift wie beim PC104-Typ, der
  unten verworfen wird) oder einem **längeren Standard-Stift** (länger als
  6,0 mm mattend, bei derselben Lieferantenfamilie) blieb erfolglos: die
  generischen 2,54-mm-Serien auf LCSC bieten für Stiftleisten regelmässig
  nur die 6,0/3,0-mm-Kombination, für Buchsenleisten regelmässig maximal
  8,5 mm — jenseits davon wird es entweder ein Sonderpreis-Einzelfund oder
  ein Bauteil mit durchgehendem Stift (siehe unten).

**Verworfen: ZHOURI 2,54-2×20 PC104 (LCSC C35165).** Diese „Buchse" mit
12,3 mm Isolationshöhe (Datenblatt, Masszeichnung „8,5±0,2" Gehäuse plus
„12,46±0,2" / „23,50" lange durchgehende Stiftbeine) ist elektrisch ein
**Sockel-plus-langer-Stift in einem Bauteil** — genau die Bauform, die der
Vertrag ausdrücklich ausschliesst („ein echter Stapelstecker wäre hier
falsch: sein langer Stift bildet oben und unten denselben Kontakt").
Deshalb nicht als Ersatz verwendet, obwohl die Höhe besser passen würde.

**Ergebnis für Aufgabe 2, Schritt 2 — keine stillschweigende Ausweichung:**
Mit den zwei belegten Standard-Bauteilen (C50980 / C2977589) lässt sich der
Vertrag mit **15,0 mm** rechnerisch erfüllen, aber nur mit einer knappen,
toleranzgefährdeten Einstecktiefe von 1,1 mm. Drei Wege stehen offen, und
die Entscheidung darüber liegt beim Auftraggeber:

1. **So lassen** und die 1,1 mm als ausreichend akzeptieren — mit dem
   Risiko, dass ungünstige Toleranzstapel die Verbindung im Extremfall zu
   locker machen.
2. **`STAPEL_ABSTAND` verringern** (z. B. auf 14,0–14,3 mm), um mehr
   Einstecktiefe zu gewinnen — dann muss geprüft werden, ob die 10 mm
   hohen Schraubklemmen (Design-Doc, Abschnitt „Mechanik") noch passen;
   der ursprüngliche Grund für 15 mm war gerade deren Höhe plus Reserve.
3. **Sonderbauform suchen/bestellen lassen** (z. B. eine Buchse mit mehr
   als 8,5 mm bei einem anderen Hersteller/Distributor als LCSC) — hier
   nicht weiter verfolgt, weil ausserhalb des Bindungsrahmens „nur
   gesichtete LCSC/JLCPCB-Nummern".

### Nachtrag 2026-08-31 — Entscheidung des Auftraggebers: doch der Stapelstecker

Der Auftraggeber hat nach Prüfung dieses Befundes entschieden: **der
2×20-Signalstecker wird der oben verworfene PC104-Stapelstecker (LCSC
C35165)** — nicht mehr das Buchse/Stift-Paar C2977589/C50980. Begründung
und Grenzen dieser Entscheidung stehen ausführlich in Beleg 6 unten; hier
nur die nachgerechnete Geometrie, weil sie dieselbe Systematik wie oben
verwendet, nur mit einem anderen Bauteil.

**Geometrie beim durchgehenden Stift.** Anders als beim Buchse/Stift-Paar
sitzt hier auf **jedem** Modul dieselbe Buchse-mit-langem-Stift (C35165).
Der Stift von Modul A führt durch dessen eigene Platine (1,6 mm) hindurch
und ragt dann weiter nach unten in die Buchse von Modul B hinein:

    M = Stiftlänge unter dem Gehäuse − Platinendicke von A
      = 12,46 mm − 1,6 mm = 10,86 mm  (Nettoreichweite unter A's Unterseite)
    F = Gehäusehöhe der Buchse über B's Oberseite = 8,5 mm  (unverändert)

Dieselbe Bedingung wie oben (M ≤ G ≤ M + F, mit G = STAPEL_ABSTAND −
1,6 mm) ergibt jetzt:

    M + F = 10,86 mm + 8,5 mm = 19,36 mm
    G(15,0 mm) = 15,0 mm − 1,6 mm = 13,4 mm

    M = 10,86 mm ≤ 13,4 mm  → kein Anschlagen, 2,54 mm Puffer
    Einstecktiefe = 19,36 mm − 13,4 mm = 5,96 mm  → komfortabel

Umgestellt nach dem gültigen Bereich für `STAPEL_ABSTAND` (Bedingung
M ≤ G ≤ M+F, G = STAPEL_ABSTAND − 1,6 mm):

    STAPEL_ABSTAND_min = M + 1,6 mm  = 10,86 + 1,6  = 12,46 mm
    STAPEL_ABSTAND_max = M+F + 1,6 mm = 19,36 + 1,6 = 20,96 mm

**Ergebnis: 15,0 mm liegt komfortabel im gültigen Bereich [12,46 mm;
20,96 mm]**, mit 5,96 mm rechnerischer Einstecktiefe — deutlich mehr
Reserve als die 1,1 mm des ursprünglich geprüften Paars. Auch im
ungünstigsten Toleranzfall (±0,2 mm auf beiden Bauteilmassen, ±0,16 mm
Platinendicke) bleibt die Einstecktiefe über 5,5 mm; eine Nachrechnung mit
den etwas niedrigeren, automatisch aus dem LCSC-Attributfeld gelesenen
Werten (8,3 mm statt 8,5 mm, 12,3 mm statt 12,46 mm — kleine Abweichung
zur direkt aus der Datenblattzeichnung gelesenen Zahl, vermutlich Rundung
der automatischen Attributextraktion) ändert daran nichts Wesentliches
(M+F ≈ 19,0 mm, Einstecktiefe ≈ 5,6 mm bei 15,0 mm).

**`STAPEL_ABSTAND` muss also NICHT geändert werden.** Die Vermutung des
Auftraggebers, es könnte auf 12,6 mm sinken müssen, hat sich mit den
tatsächlich gelesenen Datenblattzahlen nicht bestätigt — 15,0 mm passt mit
gutem Spielraum. Umgesetzt in `tools/stack_spec.py` als Kommentar bei
`STAPEL_ABSTAND` und in den neuen Konstanten `STECKER_STAPEL`/
`STECKER_KETTE`.

**Unabhängige Bestätigung, nicht aus dem Datenblatt:** PC/104 ist ein
dokumentierter Industriestandard mit **fest definiertem** Platinenabstand
von 0,600 Zoll = 15,24 mm (Quelle: PC/104-Consortium, `pc104.org/hardware-
specifications/pc104/`; unabhängig bestätigt durch Samtec, die für exakt
diesen Standard passende Abstandsbolzen mit 15,24 mm Stapelhöhe führen).
Das hier gewählte Bauteil trägt den Namen „PC104-2\*NA+1“ und ist damit
mit hoher Wahrscheinlichkeit für genau diesen Industriewert ausgelegt —
15,24 mm liegt nur 0,24 mm über unserem Vertragswert 15,0 mm, tief im oben
berechneten gültigen Bereich. Das ist ein unabhängiger Plausibilitätscheck
von ausserhalb der Datenblattzeichnung, kein Ersatz für die eigene
Rechnung, aber eine Bestätigung, dass die eigene Dimensionsinterpretation
der Zeichnung (M und F wie oben zugeordnet) nicht offensichtlich falsch
ist.

> **Überholt seit 2026-08-31 (Aufgabe 5e), s. Beleg 13.** Die hier für den Kettenstecker gewählten bedrahteten Teile (C492401 / C541849) sind nicht baubar — zwei bedrahtete Hälften am selben Ort brauchten dieselben Bohrungen. Der Kettenstecker ist jetzt ein **SMD-Paar**, Einstecktiefe 5,60 statt 3,1 mm.

**Der Kettenstecker reproduziert den ursprünglichen Befund unverändert.**
Die eine Leitung, die weiterhin aufgetrennt werden muss (`SEL`), bekommt
zwangsläufig wieder ein normales Buchse/Stift-Paar (kein Durchgangsstift
möglich, sonst liesse sie sich nicht auftrennen — derselbe Grund, der den
2×20-Stecker ursprünglich zum Paar gemacht hatte). Die dafür gefundenen,
extra für die Zweipoligkeit gesichteten Bauteile XFCN PZ254V-11-02P
(C492401, Stift) und XFCN PM254V-11-02-H85 (C541849, Buchse) tragen
**exakt dieselben Masse** wie C50980/C2977589 (6,0/3,0 mm bzw. 8,5 mm,
beide Datenblätter/Attribute gesichtet) — die Rechnung von oben gilt
deshalb unverändert: **1,1 mm Einstecktiefe bei 15,0 mm, derselbe dünne
Rand wie ursprünglich gefunden.** Der Umstieg auf den Stapelstecker löst
das Höhenproblem nur für die 39 durchgereichten Leitungen, nicht für den
Kettenstecker. Das ist keine neue Erkenntnis, sondern derselbe Befund wie
oben, jetzt auf einen kleineren, eigenständigen Stecker konzentriert statt
über den ganzen 40-Pin-Stecker verteilt — hier explizit festgehalten, weil
das beim ersten Lesen der Aufgabenstellung leicht überlesen werden könnte:
„zur selben Bauhöhe passen" heisst nicht „dasselbe Höhenproblem gelöst".

## Beleg 2 — D-Flipflop mit asynchronem Löscheingang: gefunden

**Ergebnis: Ja, es gibt eines, JLCPCB-bestückbar.** `SN74LVC1G175DCKR`
(Texas Instruments), LCSC C202238, Gehäuse SOT-363-6 (6 Pins).

**Primärquelle, direkt gelesen:** TI-Datenblatt `SN74LVC1G175`, Dokument
SCES560G, „MARCH 2004 – REVISED JUNE 2015“ (heruntergeladen von
`ti.com/lit/ds/symlink/sn74lvc1g175.pdf`). Titel bereits im Dokumentkopf:
„SN74LVC1G175 Single D-Type Flip-Flop With Asynchronous Clear“. Abschnitt 3
„Description“, wörtlich: „The SN74LVC1G175 device has an asynchronous
clear (CLR) input. When CLR is high, data from the input pin (D) is
transferred to the output pin (Q) on the clock's (CLK) rising edge. When
CLR is low, Q is forced into the low state, regardless of the clock edge
or data on D.“ Abschnitt 5 „Pin Configuration and Functions“ zeigt für das
hier gewählte Gehäuse „DCK Package, 6-Pin SC70“ die Pinbelegung 1=CLK,
2=GND, 3=D, 4=Q, 5=VCC, 6=CLR (aktiv LOW, Balken über CLR im Schaltzeichen
und in der Pin-Tabelle als „Clear Data Input“ beschriftet) — exakt das
Gehäuse von C202238 (LCSC-Attribut „SC70(6)“ bzw. „SOT-363-6“, dieselbe
Bauform unter anderem Namen).

Ergänzend, nicht als Ersatz für die Primärquelle: Nexperia führt denselben
Standardtyp unter identischem Familiennamen 74LVC1G175 (Datenblatt Rev. 11,
15. Aug. 2023) mit gleicher Funktion („master reset MR, asynchronous
active LOW“) — die beiden Hersteller bieten pin- und funktionskompatible
Varianten desselben Typs an. Die vorherige Fassung dieses Dokuments zitierte
irrtümlich nur die Nexperia-Quelle für ein bei LCSC als TI-Bauteil
gesichtetes Teil; korrigiert auf die tatsächliche Herstellerquelle des
gesichteten Bauteils. Auf der tatsächlich
gesichteten LCSC-Produktseite steht die TI-Beschreibung wörtlich „Single
D-Type Flip-Flop With Asynchronous Clear".

**Wichtige Korrektur unterwegs — nicht 74LVC1G74, nicht 74LVC1G79:**
Zwei andere Kandidaten aus der ersten Web-Recherche mussten verworfen
werden, nachdem ich die echten Datenblätter gelesen hatte (nicht nur
Suchmaschinen-Kurzfassungen):

- **74LVC1G74** (Nexperia, gesichtet als `74LVC1G74GT,115`, LCSC C548415):
  hat zusätzlich zum Reset auch einen Set-Eingang UND einen invertierten
  Ausgang Q̄ — macht 8 Signale (D, CP, SD, RD, Q, Q̄, VCC, GND) nötig.
  Gehäuse laut LCSC-Produktseite tatsächlich **XSON-8**, nicht SC-70/SOT.
  Nur 75 Stück Lagerbestand am Stichtag — für unseren Zweck ohnehin
  überdimensioniert (wir brauchen keinen Set-Eingang, kein Q̄).
- **74LVC1G79** (Nexperia): eine WebSearch-Kurzfassung behauptete, dieses
  Bauteil habe einen Reset-Eingang in einem 6-Pin-SOT-363. Das
  tatsächliche Nexperia-Datenblatt (Rev. 16, 9. Sept. 2025) widerlegt das:
  Pinbelegung ist nur D, CP, GND, Q, VCC (5 Pins, Funktionstabelle kennt
  **kein** Reset-Signal überhaupt) — ein einfaches Flipflop ohne jeden
  Löscheingang, in SOT-353 (5-Pin). Die Web-Kurzfassung war schlicht
  falsch; verworfen zugunsten des selbst gelesenen PDF.

**Warum SOT-363-6 statt SOT-353/SC-70 (5-Pin), wie in der Aufgabe
gewünscht:** Ein Flipflop mit Löscheingang braucht mindestens sechs
Signale (D, CP, Löscheingang, Q, VCC, GND) — eines mehr, als das reine
5-Pin-SOT-353 (D, CP, Q, VCC, GND, wie beim löscheingangslosen
74LVC1G175-Vorgänger 74LVC1G79) bietet. SOT-363-6 (auch SC-70-6 genannt)
ist dieselbe Gehäusefamilie und Baugrösse, nur mit einem sechsten Anschluss
— das ist die kleinstmögliche Bauform für diese Funktion, keine
gleichwertige 5-Pin-Alternative existiert.

**Was der Löscheingang am Sockel zusätzlich braucht:** `MR̄` ist aktiv
LOW und muss vom Sockel (oder lokal) angesteuert werden. Zwei Wege, beide
technisch gangbar, Entscheidung nicht hier getroffen:

1. **Neue globale Leitung** (z. B. `SEL_CLR`, aktiv LOW, vom Sockel über
   den 2×20-Stecker durchgereicht). Das ist eine Vertragsänderung: ein
   neuner Eintrag in `RESERVIERT`/`PIN_ROLLE` (`tools/stack_spec.py`) —
   verbindlich laut Vertrag „nicht zu ändern" ohne die Erlaubnis des
   Auftraggebers. Vorteil: der Sockel kann die Kette **jederzeit**
   erneut löschen, nicht nur beim Einschalten.
2. **Lokales RC-Power-on-Reset pro Modul**, ohne neue Leitung: ein
   passives RC-Glied an `MR̄`, das beim Hochfahren der Versorgung kurz LOW
   hält und dann freigibt. Passt gut zur tatsächlichen Anforderung des
   Vertrags — der verlangt das Leertakten ausdrücklich nur „bevor er
   FLASH_MODE das erste Mal auf 1 setzt", also einmalig beim Einschalten
   (Design-Doc, Abschnitt „Einschaltzustand"). Da laut Vertrag ausserdem
   kein Hot-Plug vorgesehen ist („Module werden stromlos gesteckt"),
   schalten alle Module gemeinsam mit dem Sockel ein — ein lokales RC-POR
   pro Modul feuert dann bei jedem Einschalten genau einmal, deckt exakt
   den geforderten Fall ab und braucht **keine** Vertragsänderung. Nachteil:
   die Zeitkonstante hängt von Bauteiltoleranzen ab (muss mit Marge gegen
   die Versorgungs-Anstiegszeit ausgelegt werden) und der Sockel kann die
   Kette später nicht mehr aktiv nachlöschen — dafür bliebe weiterhin das
   Leertakten als Rückfalloption.

Mit diesem Löscheingang **entfällt das Leertakten** in beiden Fällen für
den Einschaltfall — Weg 1 ersetzt es vollständig und wiederholbar, Weg 2
deckt exakt den einmaligen Einschaltfall ab, den der Vertrag verlangt.

## Beleg 3 — Gatter (Invertierung, RESET-/BOOT0-AND): JLCPCB-bestückbar

Die in `hardware/bauteile.md`, Beleg 4, genannten Kandidaten wurden auf
echten LCSC-/JLCPCB-Produktseiten geprüft:

- **Invertierung Q** (für RESET): `SN74LVC1G04DCKR` (TI), LCSC C8207,
  Gehäuse SOT-353 (SC-70-5) — genau die in der Aufgabe gewünschte
  Winzbauform. JLCPCB-Produktseite bestätigt SMT Assembly.
- **RESET = FLASH_MODE ∧ ¬Q und BOOT0 = FLASH_MODE ∧ Q** (2× 2-Input-AND):
  `74LVC2G08GT,115` (Nexperia), LCSC C548580, Gehäuse **XSON-8** (1×2 mm,
  kein 6-Pin-SOT möglich — ein Dual-Gatter mit zwei unabhängigen
  2-Input-AND-Funktionen braucht mindestens acht Signale: 2×(2 Eingänge +
  1 Ausgang) + VCC + GND = 8. Das deckt **beide** AND-Funktionen
  (RESET und BOOT0) in einem einzigen Bauteil ab — pro Modul also ein
  einziger Dual-AND-Chip statt zwei Einzel-AND-Chips.

**Zur Stückzahl-Angabe in der Aufgabenstellung:** Die Aufgabentabelle
nennt „2× NOT und 3× AND". Das deckt sich **nicht** mit der tatsächlichen
Gatterlogik in `tools/kette.py` (Funktion `modul_zustand`) und mit
`hardware/bauteile.md`, Beleg 4: dort sind es pro Modul **1× NOT und
2× AND** (`SEL_OUT` braucht seit der Korrektur in Etappe 1a kein eigenes
Gatter mehr, es ist direkt der Flipflop-Ausgang `Q`). Ich habe mich an den
Code und die bereits geprüfte Herleitung in `bauteile.md` gehalten, nicht
an die möglicherweise veraltete Zahl in der Aufgabenstellung — das sollte
beim Lesen auffallen, falls die „2×/3×"-Angabe woanders noch eine Rolle
spielt.

### Nachtrag 2026-08-31 — RESET-Gatter verpolt: aus dem AND wird ein NAND

**Befund (gemeldeter Fehler dieser Aufgabe):** `tools/kette.py` modelliert
`RESET = flash_mode ∧ ¬q` als **aktiv HIGH** ("1 = im Reset gehalten").
Der Reset-Eingang des STM32C011F6P6 heisst aber `NRST` (PF2-NRST) und ist
laut Datenblatt **aktiv LOW**. Im Stand vor dieser Korrektur trieb das
UND-Gatter oben (Einheit 1 von `74LVC2G08GT,115`, C548580) sein Ergebnis
direkt auf `NRST` — verpolt: das Modul liefe genau dann, wenn es im Reset
stehen soll, und umgekehrt.

**Auflösung:** Aus dem UND-Gatter für `NRST` wird ein NAND —
`NRST = ¬(FLASH_MODE ∧ ¬Q)` — das ist exakt die fehlende Invertierung,
ohne ein zusätzliches Gatter im Signalweg. `BOOT0 = FLASH_MODE ∧ Q` bleibt
unverändert ein AND (der Bootloader-Pin des STM32 ist aktiv HIGH, dort
liegt keine Verpolung vor).

**Warum jetzt zwei Einzel-Gatter-ICs statt eines Dual-Gatter-ICs.** Der
bisherige Dual-AND (`74LVC2G08GT,115`, XSON-8, C548580) bildete beide
AND-Funktionen in einem Bauteil. Ein homogenes „2G"-Dual-Gatter kann aber
nur **eine** Funktion für beide Einheiten liefern (2× AND oder 2× NAND,
nicht gemischt) — ein Bauteil mit einer AND- und einer NAND-Einheit in
einem Gehäuse wurde bei LCSC/JLCPCB nicht gefunden. Da `NRST` jetzt NAND
und `BOOT0` weiterhin AND braucht, ersetzen zwei Einzel-Gatter-ICs den
einen Dual-Gatter-IC:

- **NRST-Gatter:** `SN74LVC1G00DCKR` (TI), LCSC C8185, SOT-353 (SC-70-5).
- **BOOT0-Gatter:** `SN74LVC1G08DCKR` (TI), LCSC C7832, SOT-353 (SC-70-5).

Beide auf ihren LCSC-Produktseiten gesichtet (nicht aus dem Gedächtnis):
`lcsc.com/product-detail/C8185.html` nennt das Gehäuse „SOT-353“,
`lcsc.com/product-detail/C7832.html` „SC-70-5“ — dieselbe Bauform unter
zwei gängigen Namen, mit identischer Pinbelegung (1,2 Eingänge, 3 GND,
4 Ausgang, 5 VCC — selbst aus der KiCad-Symbolgeometrie nachgemessen,
`tools/sch/symlib.py`), also 1:1 austauschbar mit dem bereits im Entwurf
verwendeten NOT-Gatter U102 (`SN74LVC1G04DCKR`, C8207, ebenfalls
SOT-353) — exakt „gleiches Gehäuse, gleicher Platz".

**Bauteilzahl, ehrlich benannt:** Die Gatter-**logik** bleibt bei drei
Funktionen (1× NOT, 1× NAND, 1× AND — unverändert gegenüber der
Aufgabenzählung), aber die **physische** IC-Zahl steigt von einem
Dual-Gatter-Bauteil auf zwei Einzel-Gatter-Bauteile (ein IC mehr auf der
Stückliste als unmittelbar zuvor). Das ist keine stillschweigende
Abweichung: ein gemischtes AND/NAND-Dual-Gatter wurde gesucht und nicht
gefunden: mangels passendem Bauteil ist das der einzige gangbare Weg, ohne
einen vierten Gattertyp (einen zusätzlichen Inverter) einzuführen.

**Umgesetzt:**

- `tools/sch/modulsockel.py`: `U103` ist jetzt der NAND-Einzelgatter-IC
  (treibt `NRST` direkt), `U104` neu als AND-Einzelgatter-IC (treibt
  weiterhin `BOOT0`); das Netz an MCU-Pin 6 heisst jetzt `NRST` statt
  `RESET`, um die Aktiv-LOW-Polung im Netznamen sichtbar zu machen.
- `tools/kette.py`: Modellfunktion `modul_zustand()` unverändert (der
  Test hängt an der Aussage "RESET=1 heisst im Reset gehalten"), Docstring
  ergänzt um den Hinweis auf die Hardware-Invertierung.
- `tests/test_modulsockel.py`: neue Zusicherung, dass das an `NRST`
  angeschlossene Gatter invertierend (NAND) ist, nicht nur eine
  Gatterzahl-Prüfung.

### Nachtrag 2026-08-31, zweite Runde — der zusätzliche Baustein war vermeidbar

**Befund der Prüfung:** Die obige Aufteilung in zwei Einzel-Gatter-ICs
übersah den Standardtrick, dass **ein NAND mit kurzgeschlossenen
Eingängen ein Inverter ist** — `¬Q = NAND(Q,Q)`. Damit sind die
NOT-Funktion (`Q → NQ`) und das NRST-Gatter (`NAND(FLASH_MODE, NQ)`)
beide NAND und passen in **ein** Doppel-NAND-Bauteil; nur `BOOT0` bleibt
als eigenständiges AND übrig. Physische Gatter-ICs: **zwei statt drei**
(vorher: NOT + NAND + AND je einzeln).

**Bauteil:** `SN74LVC2G00DCUR` (TI), LCSC **C206109**, „Dual 2-Input
Positive-NAND Gate". **Wichtige Korrektur der zunächst genannten
Gehäuseangabe:** Trotz der Namensähnlichkeit zum SOT-363-Flipflop
(`SN74LVC1G175DCKR`) ist dieses Bauteil **nicht** SOT-363/SC-70-6 —
das auf der LCSC-Produktseite (`lcsc.com/product-detail/C206109.html`)
tatsächlich genannte Gehäuse ist **„VSSOP-8-0.5mm"**, unabhängig
bestätigt über eine zweite Suche (DigiKey/weitere Distributoren nennen
denselben Wert: „NAND Gate IC with 2 channels in an 8-VSSOP package").
Das ist auch physikalisch zwingend: SOT-363/SC-70-6 hat nur 6 Anschlüsse,
ein Dual-2-Input-Gatter braucht mindestens 8 (2×(2 Eingänge + 1 Ausgang)
+ VCC + GND) — ein Dual-Gatter passt in dieses 6-Pin-Gehäuse gar nicht.
Verwendeter KiCad-Footprint: `Package_SO:VSSOP-8_2.3x2mm_P0.5mm`
(0,5-mm-Pitch, passend zur LCSC-Gehäuseangabe).

**Verdrahtung (`tools/sch/modulsockel.py`, U102):** Pin-Gruppierung laut
KiCad-Symbol `74xGxx:74LVC2G00` (`tools/sch/symlib.py`, `_subunits()`
nachgemessen): Einheit 1 = Pins {1,2,7} (Eingänge 1/2, Ausgang 7),
Einheit 2 = Pins {3,5,6} (Eingänge 5/6, Ausgang 3), Einheit 3 = Pins
{4,8} (GND/VCC, gemeinsam). Einheit 1 bekommt an beiden Eingängen
`SEL_OUT` (Q) — die absichtliche Kurzschaltung, die den Inverter bildet
— und liefert `NQ` auf Pin 7. Einheit 2 bildet aus `FLASH_MODE` und `NQ`
das Ergebnis `NRST` auf Pin 3, direkt an PF2-NRST des MCU. Im Code
ausführlich kommentiert, warum die zwei kurzgeschlossenen Pins **kein**
Fehler sind (sonst „repariert" sie der nächste Blick).

**Ersetzt/verworfen (Tabelle oben nachgezogen):**
- `SN74LVC1G04DCKR` (NOT, C8207) — Bauform weiterhin korrekt geprüft,
  aber nicht mehr verbaut.
- `SN74LVC1G00DCKR` (NAND, C8185) — dito, ersetzt durch eine Einheit des
  Dual-NAND.
- `SN74LVC1G08DCKR` (AND, C7832) — **bleibt unverändert** für `BOOT0`;
  kein Gegenstück im Dual-NAND, weil ein homogenes Dual-Gatter nicht eine
  AND- und eine NAND-Einheit zugleich liefern kann.

**Umgesetzt:**

- `tools/sch/modulsockel.py`: `U102` ist jetzt `SN74LVC2G00DCUR`
  (Dual-NAND, drei Platzierungen wie zuvor beim verworfenen Dual-AND:
  Einheit 1 = NOT via NAND(Q,Q), Einheit 2 = NRST-NAND, Einheit 3 =
  Versorgung). `U103` bleibt der Einzel-AND-Gatter-IC für `BOOT0`
  (vorher `U104`, umbenannt, da die Lücke durch die Konsolidierung
  entfällt). Neue Footprint-Konstante `FP_VSSOP8`.
- `hardware/bauteile-1b.md`: neue Zeile für `SN74LVC2G00DCUR` (C206109),
  die drei ersetzten Einzel-Gatter-Zeilen als verworfen markiert (Bauform
  weiterhin korrekt), Gehäuseangabe „VSSOP-8", nicht „SOT-363" — mit
  eigener Anmerkung, weil das zunächst falsch vermutet wurde.
- `tests/test_modulsockel.py`: bestehende Polaritäts-Zusicherung bleibt
  gültig (sucht das treibende Bauteil an `NRST` generisch über die
  Verdrahtung, nicht über eine feste Referenzbezeichnung) — geprüft
  gegen `libid == "74xGxx:74LVC2G00"`, die neue Multi-Unit-Einheit.
- `tests/test_modulsockel.py`: neuer ERC-Testschritt (siehe unten).

## Beleg 4 — Leistungsstecker: Bauform gewählt, Strombelastbarkeit belegt

> **Überholt seit 2026-08-31 (Aufgabe 5e), s. Beleg 13.** Die hier gewählte bedrahtete Buchse/Stift-Paarung (C2977590 / C66690) ist nicht baubar: beide Hälften müssen am selben Ort sitzen und bräuchten dann dieselben Bohrungen. Der Leistungsstecker ist jetzt ein **SMD-Paar**. Die Stromrechnung unten (Engpass Buchse, zwei Kontakte je Ader, ~5 A vor Derating) gilt unverändert weiter — die SMD-Buchse trägt dieselben 2,5 A je Kontakt.

**Bauform:** dieselbe 2,54-mm-Stift-/Buchsenleisten-Familie wie der
Signalstecker (BOOMELE/ZHOURI), aber als eigener, getrennter 2×2-Stecker
— getrennt geführt vom Signalstecker, wie es das Design-Doc verlangt
(„Getrennt vom Signalstecker geführt, damit Motorströme nicht neben
empfindlichen Leitungen liegen"). Dieselbe Familie wurde gewählt, damit
Stiftlänge und Buchsenhöhe zum bereits gerechneten Stapelabstand passen
(Beleg 1) — ein anderer Verbindertyp hier hätte eine zweite,
unabhängige Höhenrechnung nötig gemacht.

- Buchse: C2977590 (ZHOURI 2,54-2×2), LCSC-Produktseite bestätigt
  „2.5A"-Stromangabe pro Kontakt und „8.5mm insulation height" — identische
  Werte wie beim 2×20-Signalstecker (C2977589), nur mit weniger Positionen.
- Stift: C66690 (BOOMELE 2,54-2×2P), LCSC-Produktseite bestätigt „3A" pro
  Kontakt, „6mm"/„3mm" Stiftlänge — identisch zu C50980.

**Strombelastbarkeit (belegt, nicht angenommen):** Engpass ist die Buchse
mit **2,5 A pro Kontakt** (Datenblatt-Rohdaten, „Current rating: 2.5AMP";
die Stiftleiste erlaubt mit 3 A mehr). Bei zwei parallelen Kontakten je
Ader (24 V auf zwei der vier Positionen, GND auf den anderen zwei) ergibt
sich rechnerisch **bis 5 A pro Ader vor Derating** — dieselbe Vorsicht wie
schon in `hardware/bauteile.md`, Beleg 3, für die Etappe-1a-Schätzung: das
ist eine einfache Parallel-Summe der Einzelkontakt-Nennwerte, keine
geprüfte Aussage über reale Stromaufteilung bei ungleichen
Kontaktwiderständen, und keine Herstellerangabe für den Parallelbetrieb
selbst. Der Vertrag legt keinen Strombudget-Wert für den ganzen Stapel
fest (`docs/superpowers/specs/2026-08-28-picostack-design.md` nennt nur
„eigener Stecker, nur 24 V und Masse, mehrere Kontakte parallel", ohne
Zahl) — die Positionsanzahl (2×2) ist hier ein **Vorschlag**, kein
Vertragswert. Reicht 5 A vor Derating nicht (z. B. bei mehreren
Motor-Modulen gleichzeitig unter Last), lässt sich mit einer grösseren
Positionszahl (z. B. 2×3, je 3 parallele Kontakte) mehr herausholen, ohne
die Höhenrechnung aus Beleg 1 zu ändern — die Familie bleibt dieselbe.

## Beleg 5 — Klemmen: 3-polig gefunden, 2-polig unverändert

- **2-polig** (`DB128L-5.08-2P-GN-S`, LCSC C395868): unverändert aus
  Etappe 1a / LED-Dimmer-Projekt übernommen, nicht neu recherchiert (siehe
  `hardware/bauteile.md`).
- **3-polig** (`DB128L-5.08-3P-GN-S`, LCSC C395869): auf der
  LCSC-Produktseite gesichtet, selbe Farbe/Baureihe wie die bereits
  geprüfte 2-polige Klemme (DORABO-Hersteller, „DB128L-5.08"-Familie).
  Datenblatt-Rohdaten: 16 A, 300 V, M2-Schraube, 12–22 AWG (2,5 mm²),
  −40 °C…+105 °C. JLCPCB listet die Geschwister-Varianten derselben
  Baureihe (2P, 3P-OG-S, 3P-BK-S, 4P) mit „Economic and Standard"-PCBA;
  die JLCPCB-Seite für exakt die GN-S-Farbvariante wurde nicht einzeln mit
  eigener URL gesichtet, die LCSC-Produktseite mit der vollständigen
  Spezifikation aber schon.

## Beleg 6 — Entscheidung Stapelstecker: warum zuerst ausgeschlossen, warum jetzt doch

**Warum ursprünglich ausgeschlossen (Etappe 1b, erste Fassung dieses
Dokuments, und schon im Design-Doc):** Der Signalstecker führt alle 40
Pico-Pins durch den Stapel. Ein „echter Stapelstecker" — eine Buchse mit
einem einzigen, durchgehenden Stift statt getrennter Buchse oben/Stift
unten — bildet auf **jedem** dieser 40 Pins denselben elektrischen Knoten
von der Platinenoberseite bis zur Unterseite. Für 39 der 40 Leitungen ist
das gewollt: I²C, die Flash-UART, `SEL_CLK`, `FLASH_MODE`, `NOTAUS`,
Versorgung und alle freien GPIO sind **globale oder durchgereichte Netze**
— im ganzen Stapel dasselbe Signal, unabhängig davon, welches Modul gerade
angesprochen wird. Genau **eine** Leitung ist anders: `SEL`, die
Auswahlkette. Sie ist ein Schieberegister (`tools/kette.py`) — jedes
Modul haelt seinen eigenen Zustand `Q` in einem Flipflop, und `SEL` muss
von Modul zu Modul **unterbrochen** werden koennen (D des einen Moduls ist
Q des Moduls darueber, nicht dieselbe Leitung). Ein durchgehender Stift
kann das nicht: er verbindet `SEL` elektrisch mit sich selbst durch den
ganzen Stapel, und aus der Kette würde ein einziger gemeinsamer Knoten —
das Schieberegister bräche zusammen, mehrere Module wären gleichzeitig
„ausgewählt". Deshalb stand in der ersten Fassung dieses Dokuments (siehe
Beleg 1, unveränderter Text oben): der PC104-Stapelstecker C35165 sei
„elektrisch ein Sockel-plus-langer-Stift in einem Bauteil — genau die
Bauform, die der Vertrag ausdrücklich ausschliesst" und wurde verworfen.

**Was sich geändert hat, ist nicht die Physik, sondern der Zuschnitt.**
Der ursprüngliche Ausschluss galt dem *ganzen* 2×20-Stecker, weil er alle
40 Leitungen auf einmal traf. Er bleibt für **eine** Leitung richtig
(`SEL`) — aber falsch verallgemeinert für die anderen 39. Die Lösung des
Auftraggebers trennt das: Der 2×20-Stecker traegt nur noch die 39
Leitungen, die ohnehin durchgehend sein sollen, als echter Stapelstecker
mit den bekannten Vorteilen (ein Bauteil statt zwei, mechanisch belastbare
lange Kontakte, siehe Beleg 1 Nachtrag für die Hoehenrechnung). `SEL`
bekommt einen eigenen, kleinen, **nicht** durchgehenden Stecker
(Kettenstecker, C492401/C541849) — dort gilt der ursprüngliche Ausschluss
unveraendert, und genau deshalb ist der Kettenstecker ein normales
Buchse/Stift-Paar wie der alte 2×20-Stecker es war, mit demselben
1,1-mm-Befund (Beleg 1, Nachtrag).

**Was das für den Vertrag bedeutet (`tools/stack_spec.py`):**

- `SEL` faellt aus `RESERVIERT` und `PIN_ROLLE` heraus; Pin 4 (GP2) ist
  wieder `"frei"`.
- Zwei neue Konstanten `STECKER_STAPEL` und `STECKER_KETTE` halten Bauteil,
  Hoehenrechnung und (fuer den Kettenstecker) die Pinbelegung fest, analog
  zu den anderen Vertragsgegenstaenden.
- `STAPEL_ABSTAND` bleibt bei 15,0 mm (Beleg 1, Nachtrag: passt komfortabel
  zum Stapelstecker; der Kettenstecker traegt weiterhin nur 1,1 mm
  Einstecktiefe, dokumentiert, nicht stillschweigend uebergangen).
- `docs/vertrag.md` wurde mit `python3 tools/vertrag_doku.py` neu erzeugt
  und zeigt jetzt einen eigenen Abschnitt „Stapelstecker und
  Kettenstecker" mit Bauteil, Hoehen und der Pinbelegung des
  Kettensteckers.
- `tests/test_stack_spec.py` prueft neu: `SEL` steht in keiner Rolle mehr,
  Pin 4 ist frei, und `STECKER_KETTE` traegt genau zwei Pins (`SEL` und
  `GND`).

### Zweite Runde 2026-08-31 — `STAPEL_ABSTAND` sinkt von 15,0 auf 13,0 mm

**Warum 15,0 mm nicht bleiben konnte.** Der obige Stand liess den
Kettenstecker mit rechnerisch nur **1,1 mm Einstecktiefe** stehen (Beleg 1,
Nachtrag) — an ihm haengt die ganze Auswahlkette. Zwei unabhaengige
Suchen (LCSC-Katalog und JLCPCB-Bibliothek) nach einer laengeren
einreihigen Stiftleiste blieben erfolglos: die gaengigen 2,54-mm-Serien
bieten fuer Stiftleisten regelmaessig nur die 6,0/3,0-mm-Kombination, wie
schon in Beleg 1 fuer den urspruenglichen Signalstecker festgestellt.
Ohne laengeres Bauteil bleibt nur, den Spalt selbst zu verkleinern.

**Warum 13,0 mm geht — mit belegten Zahlen, nicht geschaetzt.** Kleinerer
Spalt heisst mehr Einstecktiefe fuer beide Stecker, aber weniger Platz
fuer die Schraubklemmen, die den urspruenglichen 15-mm-Wert begruendet
hatten (Design-Doc, Abschnitt „Mechanik“). Vor der Entscheidung wurden
deshalb die tatsaechlichen Bauhoehen der drei infrage stehenden Bauteile
aus ihren Datenblaettern gelesen, nicht aus der groben Vorabschaetzung
„rund 10 mm“ uebernommen:

- **DB128L-5.08-2P-GN-S (C395868) und DB128L-5.08-3P-GN-S (C395869):**
  Datenblatt DORABO „DB128L-5.08-XXP-C-S“ (Zeichnungsdatum 2022.11.25,
  gesichtet ueber den auf der jeweiligen LCSC-Produktseite verlinkten
  `pdfUrl`, PDF-Hash `774f77501d8e260538e3ee59c3ecee93` — **dasselbe PDF
  fuer beide Bauteile**, weil es ein generischer Zeichnungssatz „XXP“ fuer
  alle Polzahlen dieser Baureihe ist). Seitenansicht, Bemassung **„10.10“**
  — das ist die Gesamthoehe des Klemmenkoerpers ueber der Platine; sie
  haengt in dieser Zeichnung nicht von der Polzahl ab (nur die Breite
  waechst mit „N×5.08“). Die zusaetzlich in derselben Zeichnung bemasste
  Breite „14.10“ (= (2−1)×5,08 mm + Randmass, stimmig fuer die 2-polige
  Ausfuehrung) bestaetigt, dass die Zeichnung tatsaechlich zu dieser
  Baureihe gehoert und nicht vertauscht wurde.
  → **Bauhoehe 10,10 mm**, fuer beide Klemmen gleich.
- **K7805-2000R3 (C2931187):** Datenblatt DEXU Electronics
  „K78xx-2000R3“, Rev. A0-2018.12 (gesichtet ueber den `pdfUrl` der
  LCSC-Produktseite, PDF-Hash `17983581d455f7b27113790e48e5474c`), Seite 2
  („产品特性“ / Produkteigenschaften), Zeile „外观尺寸“ (Aussenmasse):
  „长\*宽\*高 11.6\*7.5\*10.2mm“ (Laenge×Breite×**Hoehe**). Die separate
  Massskizze auf Seite 5 zeigt zusaetzliche Zahlen (u. a. „17.50“ fuer die
  Gesamthoehe inklusive der durchgesteckten Anschlussbeine unterhalb der
  Platine) — fuer die hier gesuchte Frage (Bauhoehe **oberhalb** der
  Platine, im Spalt) ist die explizite Textangabe „10.2mm“ eindeutig und
  wird verwendet.
  → **Bauhoehe 10,2 mm.**

**Rechnung bei 13,0 mm:**

    G = STAPEL_ABSTAND − PLATINE_DICKE = 13,0 − 1,6 = 11,4 mm

    Kettenstecker : Einstecktiefe = 14,5 − 11,4 = 3,1 mm   (statt 1,1 mm bei 15,0 mm)
    Stapelstecker : Einstecktiefe = 19,36 − 11,4 = 7,96 mm (statt 5,96 mm bei 15,0 mm)

    Rest ueber der Klemme (10,10 mm)  : 11,4 − 10,10 = 1,3 mm
    Rest ueber dem K7805  (10,2 mm)   : 11,4 − 10,2  = 1,2 mm

Beide Klemmenhoehen (10,10 mm und 10,2 mm) liegen **unter** der
11,0-mm-Reissleine, ab der der Auftraggeber die Entscheidung selbst
haette treffen wollen — 13,0 mm haelt, mit rundem 1,2–1,3 mm Luft ueber
der Klemme beziehungsweise dem K7805, und mit deutlich mehr Einstecktiefe
an beiden Steckern als vorher. Der K7805 sitzt zwar tatsaechlich nur auf
dem Sockel (oberste Platine, darueber kommt nichts mehr im Stapel), wurde
aber als worst-case gepruemft, falls ein kuenftiges Modul denselben
Regler in einem Spalt verwendet — auch dieser Fall passt.

**Toleranzhinweis, unveraendert aus Beleg 1:** Beide Steckerbauteile
tragen ±0,2 mm Fertigungstoleranz, die Platinendicke ±10 % (JLCPCB-
Standard). Im ungünstigsten Fall schrumpft jede der obigen Reserven
entsprechend — bei 1,2–1,3 mm Luft ueber den Klemmen und 3,1 mm
Einstecktiefe am Kettenstecker ist das ein deutlich engerer Rand als beim
Stapelstecker (7,96 mm), aber in allen vier Faellen bleibt die Reserve im
ungünstigsten Toleranzstapel positiv.

**Umgesetzt:**

- `tools/stack_spec.py`: `STAPEL_ABSTAND = 13.0`, neuer Kommentar mit der
  vollstaendigen Herleitung; neue Konstante `PLATINE_DICKE = 1.6`; neue
  Konstanten `KLEMME_HOEHE_MM = 10.10` und `K7805_HOEHE_MM = 10.2` mit
  Quellenangabe; `STECKER_KETTE` traegt jetzt `buchsenhoehe_mm` und
  `stiftlaenge_mm` als Masse statt eines fest hinterlegten
  `einstecktiefe_mm`-Werts; zwei neue Funktionen
  `EINSTECKTIEFE_STAPEL()`/`EINSTECKTIEFE_KETTE()` berechnen die
  Einstecktiefe aus `STAPEL_ABSTAND` und den Steckermassen, statt sie als
  Zahl zu duplizieren.
- `docs/vertrag.md` neu erzeugt mit `python3 tools/vertrag_doku.py` —
  zeigt jetzt 13,0 mm.
- `tests/test_stack_spec.py`: Wert auf 13,0 mm nachgezogen; zwei neue
  Zusicherungen pruefen, dass `EINSTECKTIEFE_STAPEL()` und
  `EINSTECKTIEFE_KETTE()` ueber einer Mindestschwelle liegen (2,0 mm,
  konservativ unter dem knappsten belegten Fall), und zwei weitere, dass
  ueber `KLEMME_HOEHE_MM` und `K7805_HOEHE_MM` noch Luft im Spalt bleibt
  — nicht nur die Zahl 13,0 selbst.

**Offen — ausdruecklich nicht in dieser Aufgabe erledigt:** Das Gehaeuse
(Aufgabe 9 dieser Etappe) wurde gegen den alten Wert `STAPEL_ABSTAND =
15,0 mm` entworfen bzw. ist dafuer vorgesehen und muss auf den neuen Wert
13,0 mm nachgezogen werden, sobald diese Aufgabe angegangen wird.

## Beleg 7 — Layout-Auflage: C3 muss nah an U2 Pin 1 sitzen (Aufgabe-4-Fix-1, 2026-08-31)

**Hintergrund.** `tools/sch/sockelplatine.py` setzt C1 (HF-Abblockung an
U2, den Reglerpins direkt benachbart) auf 100 nF/50 V statt der vom
Datenblatt für die K78xx-2000R3-Baureihe genannten 22 µF/50 V (Begründung
im Code: 22 µF/50 V ist in 0805/X7R keine sinnvolle Bauform). C3 (220 µF
radial, ohnehin für "Stützung am 24-V-Eingang" im Aufgabenbrief
vorgesehen) übernimmt dabei die vom Datenblatt eigentlich gemeinte
Speicherkapazität an U2s Eingang.

**Auflage, damit das haelt.** Diese Aufteilung funktioniert nur, wenn C3
tatsächlich **nah an U2 Pin 1 (IN)** sitzt — nicht irgendwo sonst auf der
Platine. Liegt zwischen C3 und U2 Pin 1 eine lange Leiterbahn, macht die
Schleifeninduktivität dieser Strecke die Stützwirkung zunichte: C3 kann
dann hochfrequente Stromtransienten am Reglereingang nicht mehr
abfangen, genau die Aufgabe, die die Absicht (C1 klein/HF, C3 groß/
Speicher) ihm zuweist. Das ist keine Platzierungsempfehlung, sondern eine
**Layout-Auflage für Aufgabe 6** (PCB-Layout der Sockelplatine): C3
gehört so nah wie mechanisch sinnvoll an U2 Pin 1, mit möglichst kurzer,
möglichst breiter Verbindung (kurze Schleife PWR24V zwischen C3⁺ und U2
Pin 1, ebenso kurzer Rückweg über GND). Der Schaltplan selbst kann diese
Auflage nicht erzwingen (Netzlisten kennen keine Distanz) — deshalb hier
schriftlich festgehalten, nicht nur im Code kommentiert.

## Beleg 8 — 3,3-V-Haushalt des Stapels, mit dem Motormodul nachgerechnet (Aufgabe 5)

**Aufgabe (Auftraggeber-Punkt 2 der Aufgabe 5):** Die Modul-MCU ziehen ihre
Versorgung aus der 3V3-Schiene, deren Quelle der interne Regler des Pico ist
(3V3_OUT, Pin 36). Nachzurechnen: wie viel darf extern entnommen werden, und
wie viele Module trägt das.

**Obergrenze aus dem Pico-Datenblatt.** Dieselbe Quelle wie bereits in
`hardware/bauteile.md`, Beleg 3, zitiert (Raspberry Pi Pico Datasheet,
Abschnitt „Pin Description", Beschreibung des Pins `3V3`): „This pin can be
used to power external circuitry (maximum output current will depend on
RP2040 load and VSYS voltage, it is recommended to keep the load on this pin
less than 300 mA)." Diese 300 mA sind explizit die Grenze für **externe**
Last — der RP2040-Eigenverbrauch selbst zieht aus VSYS über den internen
Regler, nicht aus dieser Zahl.

**Was ein Modul tatsächlich zieht — vollständiger als in Etappe 1a, weil das
Motormodul zwei neue Verbraucher an die 3V3-Schiene hängt, die es in Etappe
1a (reine Modul-MCU-Abschätzung) noch nicht gab:**

1. **Modul-MCU (STM32C011F6P6), unverändert aus `hardware/bauteile.md`,
   Beleg 3:** DS13866 Rev 3, Tabelle 27 „Current consumption in Run mode
   from flash memory", `IDD(Run)` bei 48 MHz (HSI48): typ. 3,40 mA, max.
   3,90 mA (25 °C), bis max. 4,90 mA (125 °C). Für diese Rechnung wird der
   ungünstigste Wert verwendet: **4,90 mA**.
2. **Zwei Kennwiderstand-Spannungsteiler pro Modul** (`tools/sch/
   modulsockel.py`, `_kennwiderstand()`: R104/R100 und R105/R101, je
   3V3–[ID_OBEN]–Knoten–[Kennwiderstand]–GND). Worst-case-Strom pro Teiler
   bei kleinstem tatsächlich vergebenen Kennwiderstand (`stack_spec.
   ID_WIDERSTAENDE[1]` = 680 Ω — der erste Eintrag, 0 Ω, ist laut
   `stack_spec.py`-Kommentar für „Modultyp 0x00, ungültig" reserviert und
   wird nie real bestückt, aber selbst mit ihm ändert sich die Rechnung
   kaum):

       I_Teiler = 3,3 V / (ID_OBEN + R_kenn) = 3,3 / (10000 + 680) ≈ 0,309 mA

   Zwei Teiler je Modul: **≈ 0,62 mA** (konservativ mit dem theoretischen
   0-Ω-Fall aufgerundet: 3,3/10000 × 2 = 0,66 mA).
3. **U1 VREF (DRV8876, Pin 5), neu gegenüber Etappe 1a:** liegt in diesem
   Modul direkt an 3V3 (wie im Altprojekt). Das DRV8876-Datenblatt (TI
   SLVSDS7B) nennt für VREF nur den zulässigen Spannungsbereich (Abschnitt
   6.3, „Recommended Operating Conditions": 0–3,6 V), **keinen eigenen
   Ruhestromwert** — VREF ist der Referenzeingang eines internen
   Komparators, kein Lastausgang. Ohne eine tatsächlich gelesene
   Datenblattzahl wird hier **keine** erfundene Zahl eingesetzt (Bindend-
   Regel dieser Aufgabe) — die Größenordnung eines Komparator-
   Referenzeingangs liegt allgemein im Nanoampere- bis niedrigen
   Mikroampere-Bereich, also um mindestens zwei Zehnerpotenzen unter den
   beiden obigen Posten. Die Budget-Aussage unten ändert sich dadurch
   nicht, selbst wenn der tatsächliche Wert am oberen Rand dieser
   Größenordnung läge.
4. **Logikgatter (U101 Flipflop, U102 Dual-NAND, U103 AND), neu gegenüber
   Etappe 1a:** CMOS-Standardlogik dieser Bauart liegt typischerweise im
   niedrigen einstelligen Mikroampere-Bereich statischer Stromaufnahme —
   auch hier keine einzeln aus einem gelesenen Datenblattwert belegte Zahl
   (die drei zugehörigen Datenblätter geben zwar `ICC`-Werte an, die wurden
   für diese Rechnung nicht extra herausgesucht, weil selbst ein
   pessimistischer zweistelliger µA-Wert je Gatter die Summe nicht in die
   Nähe der MCU- oder Kennwiderstand-Anteile brächte) — wie Punkt 3 eine
   vernachlässigbare Größenordnung, hier ausdrücklich als solche benannt,
   nicht verschwiegen.

**Rechnung pro Modul (Posten 1+2, die einzigen zahlenmäßig belegten):**

    I_Modul = 4,90 mA + 0,66 mA = 5,56 mA  (worst case, 125 °C)

**Wie viele Module das trägt:**

    N_max = 300 mA / 5,56 mA/Modul ≈ 53 Module

Zehn Module (die Zahl aus `hardware/bauteile.md`, Beleg 3): 10 × 5,56 mA =
**55,6 mA** — weit unter 300 mA, mit über fünffacher Reserve bis zur
theoretischen Grenze von ~53 Modulen. **Die Rechnung ist NICHT eng** — das
Ergebnis aus Etappe 1a (unkritisch) bleibt auch mit den beiden neuen, hier
erstmals berücksichtigten Verbrauchern (Kennwiderstände, VREF) bestehen; ein
eigener 3,3-V-Regler für den Stapel ist nach dieser Rechnung nicht nötig.
Die tatsächliche mechanische Obergrenze (wie viele Module überhaupt
gestapelt werden, Steckerlänge, Gehäuse) liegt weit unter 53 — das
3,3-V-Budget ist an keiner realistischen Stapelgröße der limitierende
Faktor.

## Beleg 9 — Layout-Auflage: C12-Polarität (Aufgabe 5, Motormodul)

**Hintergrund.** Auf dem Muttern-Print (v1, `~/Dokumente/Espace_des_
Inventions/PecheAuxCanards`) lag der „+"-Aufdruck eines 220-µF-Elkos auf
GND statt auf der Versorgungsschiene — zwei Kondensatoren sind dadurch
explodiert (s. `docs/superpowers/specs` bzw. die Projekt-Historie dieses
Fundes). Der Fehler liegt in der KiCad-Quelle des Muttern-Projekts und ist
dort **nicht korrigiert** — diese Aufgabe übernimmt bewusst nur die
Bauteilwerte/die Verschaltungslogik von dort, nicht die Polarität
unbesehen.

**Prüfung für C12 (220 µF, `tools/sch/motormodul.py`).** Das
`Device:C_Polarized`-Symbol trägt Pin 1 wörtlich als „+" (eigene Prüfung der
KiCad-Quelle, `Device.kicad_sym`). Im Motormodul liegt Pin 1 auf `+24V`,
Pin 2 auf `GND` — geprüft sowohl über die Netzliste
(`kicad-cli sch export netlist`, Netz `+24V` enthält `(C12, 1)`) als auch
über eine eigene Testzusicherung (`tests/test_motormodul.py`: „C12 Pin 1
(\"+\") hängt an +24V" / „... NICHT an GND"). Kein weiterer polarisierter
Kondensator kommt in dieser Datei vor (C9/C10/C11/C13 sind unpolarisierte
Keramikkondensatoren, `Device:C`, ohne Vorzugsrichtung).

**Auflage für Aufgabe 7 (PCB-Layout Motormodul).** Der Schaltplan legt die
elektrische Polarität fest, **nicht** aber, ob der spätere Footprint-Silk-
Aufdruck auf der Platine tatsächlich mit Pin 1 übereinstimmt — genau diese
Lücke hat den Muttern-Print-Fehler verursacht (dort war vermutlich nicht die
Schaltplan-Polung falsch, sondern der Footprint/Silk-Aufdruck gegenüber dem
Pad-1-Anschluss verdreht oder das Bauteil beim Bestücken falsch orientiert).
Aufgabe 7 muss deshalb **vor dem Fertigungsauftrag** explizit prüfen: liegt
das Pad, das Pin 1 (`+24V`) trägt, tatsächlich unter dem „+"-Silk-Symbol des
gewählten `CP_Radial_D8.0mm_P3.50mm`-Footprints? Eine reine
Netzlisten-/ERC-Prüfung sieht das nicht (beide Pads sind für die
Konnektivität gleichwertig, nur die Bauteil-Geometrie kennt den
Polaritäts-Silk) — das ist eine manuelle oder skriptgestützte
Footprint-Geometrie-Prüfung (z. B. `tools/pcb/pcb_checks.py`, das laut
Aufgabe-7-Brief ohnehin auf „verpolte Elkos" prüft), keine, die der
Schaltplan selbst erzwingen kann.

## Beleg 10 — Notaus-Verriegelung: die Pegel, nicht nur die Bauteile (Aufgabe-5-Fix-1, 2026-08-31)

**Der Befund.** Die erste Fassung des Motormoduls verriegelte `NOTAUS` →
`nSLEEP` mit einer Diode (D2) und einem Vorwiderstand (R14, 1 kΩ) vor dem
MCU-Vorwiderstand R9 (100 Ω). Der Kommentar dazu rechnete den *Fehlstrom*
aus ((3,3 − 0,6)/1100 ≈ 2,4 mA, unbedenklich für den GPIO) — aber nicht die
*Spannung* am Pin. R9 und R14 bilden einen Spannungsteiler:

    U(nSLEEP) = 0,6 V + 2,4 mA × 1 kΩ ≈ 3,05 V

V_IL des DRV8876-nSLEEP-Eingangs ist 0,8 V (SLVSDS7B, Abschnitt 6.5,
Block „LOGIC-LEVEL INPUTS", Zeile V_VM ≥ 5 V). Der Pin blieb also nicht nur
über V_IL, sondern sogar über V_IH (1,5 V): **die Verriegelung wirkte
nicht.** Genau in dem Fall, für den sie gebaut war — hängender MCU, GPIO
aktiv auf HIGH eingefroren — wäre der Motor angeblieben.

**Der zweite, unabhängige Grund.** Auch ohne R14 hätte die Klemme die
Schwelle verfehlt. Die Sammelleitung `NOTAUS` geht nämlich nicht auf 0 V:
sie wird über D3/D4 gegen den potentialfreien Schaltkontakt
heruntergezogen und liegt damit selbst **eine Durchlassspannung** über
Masse. Eine zweite Diode vom nSLEEP-Pin auf diesen Bus addiert die nächste:

    U(nSLEEP) = V_F(D3) + V_F(D2) ≈ 1,0 … 1,3 V   (1N4148W)   > 0,8 V

Selbst mit **Schottky-Dioden auf beiden Wegen** blieben im Grenzfall
2 × 400 mV = 0,8 V übrig — exakt die Schwelle, null Reserve. Eine passive
Dioden-UND-Verknüpfung kann diese Schwelle in dieser Topologie nicht
sicher einhalten.

**Die Lösung: ein UND-Gatter.** `U1_NSLEEP = NSLEEP(MCU) ∧ NOTAUS`, gebildet
von U3 (`SN74LVC1G08`, C7832 — dasselbe Bauteil wie U103, keine neue
Bauteilnummer) plus Abblockkondensator C14. D2 und R14 entfallen. Der
Gatterausgang ist eine Gegentaktstufe, deshalb sind die Pegel garantiert
statt gerechnet (SCES217AA, Abschnitt 5.5, jeweils bei 100 µA Laststrom):

| Fall | U an U1 Pin 3 | Schwelle (SLVSDS7B 6.5) | Reserve |
|---|---|---|---|
| NOTAUS gezogen | ≤ V_OL = **0,10 V** | V_IL = 0,8 V | 0,70 V |
| Normalbetrieb | ≥ V_OH = **3,15 V** | V_IH = 1,5 V | 1,65 V |

Die V_OL/V_OH-Werte gelten bis 100 µA Laststrom; der interne Pulldown des
nSLEEP-Pins (R_PD = 100 kΩ, SLVSDS7B 6.5) zieht bei 3,15 V nur 32 µA — die
Bedingung ist eingehalten. Fällt die 3,3-V-Schiene aus, geht der
Gatterausgang mit und derselbe Pulldown legt den Treiber schlafen: die
Ausfallrichtung ist die sichere.

**Nebenwirkung, die das Ursprungsanliegen erledigt.** R14 war eingefügt
worden, um den MCU-GPIO zu schützen (ohne ihn hätte die Diodenklemme über
R9 = 100 Ω rund 27 mA gezogen). Ein CMOS-Gattereingang zieht I_I ≤ ±5 µA
(SCES217AA 5.5) — das Schutzanliegen ist ohne Widerstand erledigt, und
ohne die Wirkung zu verhindern. R9 bleibt bei 100 Ω und ist jetzt ein
reiner Serien-/ESD-Widerstand (0,5 mV Abfall).

**Warum D3/D4 jetzt Schottky sind.** Der gezogene Ruhepegel des Busses *ist*
die Durchlassspannung dieser Dioden, und alles, was am Bus hängt — das
Gatter hier (V_IL = 0,8 V), der Pico auf der Sockelplatine, künftige
Module — muss diesen Pegel als LOW lesen. Für den Auslegungsfall aus
Beleg 8 (zehn Module, jedes mit R15 = 10 kΩ gegen 3,3 V):

    I(Bus) = 10 × (3,3 V − 0,4 V) / 10 kΩ ≈ 2,9 mA
    V_F(BAT54W) ≤ 400 mV   (Vishay 86408, MAX-Wert schon bei 10 mA)
    Reserve gegen V_IL = 0,8 V:  ≥ 0,4 V

Mit einem 1N4148W läge derselbe Pegel bei rund 0,6–0,65 V, und das
Datenblatt nennt für diese kleinen Ströme **überhaupt keinen MAX-Wert** —
für eine Sicherheitsfunktion nicht nachweisbar genug. Der BAT54W sitzt in
derselben Bauform (SOD-123); der Footprint bleibt unverändert.

**R15 bleibt bei 10 kΩ** und wird bewusst *nicht* vergrößert: bei zehn
Modulen parallel ergibt das 1 kΩ Bus-Pullup, und die Leckströme aller
Koppeldioden (I_R ≤ 2 µA, Vishay 86408) und Gattereingänge (≤ 5 µA) heben
den Ruhepegel um weniger als 0,1 V an — der Bus bleibt sicher über
V_IH = 2,0 V. Ein sehr viel hochohmigerer Pullup würde genau das kippen.

**Testabdeckung.** `tests/test_motormodul.py` prüft seit dieser
Nachbesserung nicht mehr die Anwesenheit der Diode, sondern die **Pegel**:
alle Größen (R9, R15, V_IL/V_IH des Treibers, V_OL/V_OH/V_IL/V_IH/I_I des
Gatters, V_F/I_R der Schottky-Diode) liegen als benannte Konstanten in
`tools/sch/motormodul.py`, jede mit Dokumentnummer und Abschnitt. Der Test
rechnet damit den Pegel am nSLEEP-Pin aus — **hergeleitet aus dem, was
laut Schaltplan auf dem Netz `U1_NSLEEP` hängt** — und enthält drei
Gegenproben, die zeigen, dass die alte Klemme, die Klemme ohne R14 und
sogar die reine Schottky-Variante die Schwelle verfehlen.

**Offener Punkt für Aufgabe 7 (PCB-Layout).** `NOTAUS_1`/`NOTAUS_2` haben
keinen eigenen Pullup; sie hängen am internen Pullup des Modul-MCU, den
erst die Firmware einschaltet. Für die *Sicherheitsfunktion* ist das
folgenlos (der Schaltkontakt zieht den Bus über D3/D4 unabhängig davon
herunter), für die *Kanaldiagnose* aber schon: vor dem ersten
Firmware-Lauf und bei hohen Temperaturen (Schottky-Leckstrom gegen einen
~40-kΩ-Pullup) ist der gelesene Pegel nicht garantiert. Wenn die
Kanaldiagnose verlässlich sein soll, gehören zwei 10-kΩ-Pullups dazu —
bewusst nicht in dieser Nachbesserung ergänzt, weil sie am Auftrag
(Verriegelung) vorbeigeht.

> **Nachtrag 2026-08-31 (Aufgabe 5d): dieser offene Punkt ist erledigt.**
> Die zwei Kanalknoten heissen jetzt `SCHLEIFE_1`/`SCHLEIFE_2` und tragen je
> einen echten 4,7-kΩ-**Pulldown** (R20/R21). Ihr Pegel ist damit zu jeder
> Zeit definiert — auch vor dem ersten Firmware-Lauf und unabhängig davon,
> was die Firmware an den MCU-Pins einstellt. Kein Zusatzbauteil nötig: der
> Pulldown ist ohnehin Teil des Ruhestrom-Eingangs (Beleg 11).

## Beleg 11 — Notaus-Eingang auf Ruhestromprinzip umgebaut (Aufgabe 5d, 2026-08-31)

**Der Befund.** Bis hierher war der externe Notaus-Kontakt ein **Schliesser**:
J3 Pin 1 bzw. 3 lag über einen potentialfreien Kontakt an GND, Schliessen hiess
Notaus. Ein Kabelbruch, ein abgezogener Stecker oder eine lose Klemme sehen
damit aus wie „alles in Ordnung" — die Schutzfunktion verschwindet still. Das
kam unverändert aus dem Altprojekt und stand als Bedenken 4 im
Aufgabe-5-Fix-1-Bericht. Entscheidung des Auftraggebers: Umbau auf
**Ruhestromprinzip (Öffner)**.

**Was jetzt gilt.** Der Kontakt ist im Normalbetrieb geschlossen. Öffnen löst
aus — und ebenso jeder Kabelbruch, jeder abgezogene Stecker, jede lose Klemme.

```
+24V --R16(3k3,1206)-- J3.1 ==ÖFFNER== J3.2 --R18(3k3,1206)-- U4-LED -- GND

3V3 --U4 Kollektor ... U4 Emitter --+-- SCHLEIFE_1 --> U100 Pin 3 (Diagnose)
                                    |               \
                                  R20 (4k7)          `-> U6 (Open-Drain) --> NOTAUS
                                    |
                                   GND
```

Kanal 2 ist Bauteil für Bauteil identisch (R17/R19/U5/R21/U7, J3 Pin 3+4,
U100 Pin 14).

**Warum 24 V nach draussen und nicht 3,3 V.** Museumskabel sind lang und liegen
neben Motor- und Netzleitungen. Ein 3,3-V-Signal auf eine hochohmige Last wird
von eingekoppelter Störspannung *und* von Kriechwegen (Feuchte, Staub in einer
Klemme) in beide Richtungen verfälscht. Hier fliesst stattdessen ein
definierter **Strom** von 3,0–3,9 mA; das ist zugleich ein brauchbarer
Benetzungsstrom für einen mechanischen Kontakt. Die Rückwandlung macht ein
Optokoppler, kein Spannungsteiler: kein Feldpotential erreicht die Logik. (Eine
echte galvanische Trennung ist es **nicht** — LED-Kathode und Logik liegen auf
derselben Masse; der Gewinn ist die Entkopplung des Signalwegs.)

**Pegelnachweis.** Bindende Schwellen: der Inverter-Eingang U6/U7
(SCES295AB 5.3, V_CC = 3–3,6 V) mit V_IH ≥ 2,0 V und V_IL ≤ 0,8 V; er ist
Schmitt-Trigger und verträgt die trägen Optokopplerflanken (t_r/t_f MAX 18 µs,
D2-A03101EN).

| Zustand | Rechnung | Ergebnis | Schwelle | Reserve |
|---|---|---|---|---|
| Schleife zu, schlechtester Fall | I_F = (21,6 − 1,4)/(2 × 3,3 kΩ × 1,01) | **3,03 mA** → nötiges CTR = (2,0 V / 4,7 kΩ)/3,03 mA = **14 %** | garantiert **≥ 50 %** (I_C ≥ 2,5 mA bei I_F = 5 mA, D2-A03101EN) | Faktor **3,6** |
| Schleife offen (Kabelbruch) | (I_CEO 100 nA + I_I 1 µA) × 4,7 kΩ | **5,2 mV** | V_IL = 0,8 V | **0,79 V** |
| Bus gezogen | 10 Module × (3,3 − 0,4)/10 kΩ = 2,9 mA → V_OL | **≤ 0,40 V** (MAX bei 16 mA / V_CC = 3 V, SCES295AB 5.5) | V_IL(U3) = 0,8 V | **0,40 V** |
| Bus in Ruhe | 10 × (2 × I_off 10 µA + I_I 5 µA) = 250 µA an 1 kΩ | **3,05 V** | V_IH(U3) = 2,0 V | **1,05 V** |

Der gezogene Buspegel ist damit **zahlengleich** mit der bisherigen
Schottky-Rechnung aus Beleg 10 — an der Verriegelung (U3, R9, R15,
`U1_NSLEEP`) ist deshalb **kein Bauteil und keine Zahl geändert**.

*Ehrlicher Vermerk zum CTR:* der Arbeitspunkt liegt bei 3,0–3,9 mA, nicht bei
den 5 mA der garantierten Datenblattzeile; für 3 mA nennt SHARP nur eine
Kennlinie, keinen MIN-Wert. Der Sicherheitsschluss hängt nicht daran: reicht
der Strom nicht, bleibt der Knoten unter V_IH, der Kanal meldet „offen", die
Anlage steht. **Ein CTR-Mangel kann kein falsches „in Ordnung" erzeugen** — er
kostet Verfügbarkeit, nie Sicherheit. Das beschaffte PC817X**1** trägt zudem
Rangmarke A (CTR ≥ 80 %).

**Warum die Koppeldioden D3/D4 entfallen mussten.** Die naheliegende Annahme
war, ein lokaler Pulldown ziehe den Kanalknoten LOW und die vorhandene Diode
ziehe die Sammelleitung mit. Das geht nicht:

```
Pulldown 4,7 kΩ gegen den auf 1 kΩ parallelgeschalteten Buspullup:
U(Bus) = 3,3 V × 4,7/(1 + 4,7) = 2,72 V   -- der Bus rührt sich nicht.
```

Ein Pulldown müsste (mit der Diode im Weg) unter **160 Ω** liegen, um den Bus
unter 0,8 V zu ziehen — und einen 160-Ω-Pulldown könnte kein Optokoppler mehr
auf V_IH heben (12,5 mA Fotostrom, mehr als der ganze Schleifenstrom). Der
bisherige Knoten wurde eben nicht von einem Widerstand, sondern von einem
**Schaltkontakt** (≈ 0 Ω) gezogen. Das Ruhestromprinzip verlangt, dass die
*Abwesenheit* von Strom eine *aktive* Handlung auslöst — das kann kein passives
Bauteil. Deshalb der Open-Drain-Inverter. Und eine Diode **in Reihe** dazu wäre
das Gegenteil einer Verbesserung: 0,4 V (V_OL) + 0,4 V (V_F) = 0,8 V, also
exakt die Schwelle, **null Reserve**.

**Kurzschluss der Rückleitung nach GND.** Die LED ist überbrückt, I_F = 0, der
Knoten fällt auf 5,2 mV, der Bus wird gezogen, der Treiber schläft — die sichere
Richtung. Gleiches gilt für die Hinleitung gegen GND.

**Strombegrenzung nach aussen.** Jede der vier Adern liegt hinter mindestens
3,3 kΩ:

```
I_max = 26,4 V / 3,3 kΩ   = 8,0 mA     (26,4 V = 24 V + 10 %)
P_max = 26,4 V^2 / 3,3 kΩ = 0,211 W    (84 % von 250 mW)
Normalbetrieb             = 0,049 W    (20 %)
```

**Deshalb 1206 und nicht 0805:** ein 0805 (125 mW) wäre im Kurzschluss um 70 %
überlastet. Beide Widerstände eines Kanals sind absichtlich gleich gross — dann
bleibt der Kurzschluss einer beliebigen Ader gegen GND **oder** gegen +24 V in
jedem Fall unter 8,0 mA und unter der Nennleistung, und der LED-Strom bleibt
weit unter den 50 mA Grenzstrom des PC817. *Vermerk:* die 84 % gelten bis 70 °C
Umgebungstemperatur; ein Dauerkurzschluss in einem heissen Gehäuse müsste
derated werden.

**Querschluss zwischen den Kanälen — was dann noch bleibt.** Ehrlich: hier
verliert die Zweikanaligkeit einen Teil ihres Sinns (A = Hinleitung,
B = Rückleitung). A1–A2 ist folgenlos. **B1–B2** koppelt die zwei LED-Zweige:
ist *ein* Kontakt offen und der andere geschlossen, speist der geschlossene
beide LEDs, der offene Kanal ist **blind** — öffnen beide Kontakte (der
Normalfall bei einem Not-Halt-Taster), fällt der Strom trotzdem auf null.
A1–B1 bzw. A2–B2 überbrückt den Kontakt des eigenen Kanals (das ist zugleich
die *absichtliche* Brücke für einen unbenutzten Kanal — die Schaltung kann
Absicht und Fehler nicht unterscheiden). Über Kreuz (A1–B2, A2–B1) sowie eine
Rückleitung an +24 V machen ebenfalls je einen Kanal blind. **Es bleibt: ein
Querschluss macht höchstens einen Kanal blind, der zweite löst weiter aus; für
einen Durchlauf braucht es zwei Fehler.** Was fehlt: die Schaltung **erkennt**
den Querschluss nicht — dafür bräuchte es getaktete Prüfimpulse (OSSD) oder ein
Sicherheitsrelais. Beide Kanäle hängen aber einzeln am Modul-MCU; eine
**Diskrepanzüberwachung in der Firmware** (zwei Kanäle melden länger als ein
paar hundert Millisekunden Verschiedenes → sperren) ist damit möglich und ist
hiermit als Firmware-Auftrag festgehalten. Verlege-Auflage fürs Museum: die
zwei Kreise gehören in **getrennt geführte Leitungen**, nicht in zwei Adern
desselben Mantels.

**Ein schmaler Rückschritt, ehrlich benannt.** Der Schaltkontakt zog den Bus
früher rein *passiv* herunter, auch ohne lokale 3,3 V. Jetzt braucht der
Koppelweg die 3,3-V-Schiene dieses Moduls. Stapelweiter 3V3-Ausfall ist
folgenlos (U3 stirbt mit, der interne 100-kΩ-Pulldown des DRV8876 legt den
Treiber schlafen). Fällt 3V3 **nur auf diesem Modul** aus — gebrochener
3V3-Pin am Stapelstecker —, schläft zwar dieses Modul, aber der an ihm
angeschlossene Not-Halt erreicht die übrigen Module nicht mehr. Nicht
vermeidbar: Ruhestrom verlangt einen gespeisten Treiber.

### Auflage 1 — der unbenutzte Kanal MUSS gebrückt werden

Wird nur ein Notaus-Kreis angeschlossen, hängt der zweite Kanal offen und
meldet **dauerhaft Notaus**; die Anlage läuft nicht an. Richtige Vorgabe
(offen = sicher), aber der Nutzer muss wissen, was zu tun ist:

> **Unbenutzten Kanal am Stecker brücken:
> Kanal 1 = J3 Pin 1+2, Kanal 2 = J3 Pin 3+4.**

J3 ist eine 2,54-mm-Stiftleiste; die zwei Pins eines Kanals liegen deshalb
absichtlich **nebeneinander** — eine handelsübliche Jumper-Brücke genügt. Der
Hinweis steht als Text im Schaltplan neben J3. **Aufgabe 7 (PCB-Layout) muss
ihn zusätzlich auf den Siebdruck neben J3 setzen**, zusammen mit der
Kanalzuordnung der vier Pins.

### Auflage 2 — die Verkabelung des Pêche-aux-Canards-Exponats MUSS umgeklemmt werden

**J3 bleibt vierpolig** (zwei Adern je Kanal statt Signal+GND). Gleiche
Bauform, gleiche Polzahl, völlig andere Bedeutung: **ein altes Kabel passt
mechanisch weiterhin.** Steckt man es, liegt der alte Schliesser zwischen
Pin 1 und Pin 2, also im Weg von Kanal 1; im Ruhezustand ist er offen → der
Kanal meldet Notaus, Kanal 2 hängt ohnehin offen. **Das Exponat stünde nach
dem Modultausch dauerhaft auf Notaus.** Sicher, aber unbrauchbar. Beim
Umstieg ist deshalb zwingend umzuklemmen:

- Not-Halt-Taster mit **Öffnerkontakt** verwenden (nicht Schliesser),
- je Kanal **zwei Adern** zum Taster führen (nicht Signal + Masse),
- Kanal 1 an J3 Pin 1+2, Kanal 2 an J3 Pin 3+4,
- wird nur ein Kreis verdrahtet, den anderen brücken (Auflage 1).

Empfehlung für Aufgabe 7/9, nicht ausgeführt: J3 **codieren oder auf einen
anderen Steckertyp wechseln**, damit ein altes Kabel gar nicht mehr passt —
und für ein Feld-Sicherheitssignal wäre eine Schraubklemme mit Zugentlastung
ohnehin die bessere Bauform als eine 2,54-mm-Stiftleiste.

## Beleg 12 — Layout-Auflage: der Optokoppler-Footprint stimmt nicht (Aufgabe 5d)

Beim Nachtragen des PC817 in die Bauteiltabelle ist aufgefallen, dass der seit
dem Altprojekt eingetragene Footprint nicht zum Bauteil passt — und zwar schon
für das geerbte U2, nicht erst für die neuen U4/U5.

`Package_SO:SOP-4_3.8x4.1mm_P2.54mm` (KiCad-Standardbibliothek) beschreibt ein
Gehäuse von 3,8 × 4,1 mm mit Pad-Mitten bei ±2,75 mm. Der PC817 in
SMT-Gullwing-Bauform misst laut SHARP D2-A03101EN, Abschnitt „Outline
Dimensions", Variante „SMT Gullwing Lead-Form": Körper **6,5 × 4,58 mm**,
Anschlussspanne **10,0 mm**, Reihenabstand **7,62 mm**, Pitch 2,54 mm. Das
passt nicht — auch der grössere Nachbar `SOP-4_7.5x4.1mm_P2.54mm` (Pad-Mitten
±4,6875 mm) trifft es nicht genau.

Im Schaltplan ist das folgenlos (Repo-Praxis: Footprints sind Platzhalter, bis
Aufgabe 7 die echten zeichnet — dieselbe Lage wie bei den DB128L-Klemmen), aber
**Aufgabe 7 muss für U2/U4/U5 einen eigenen PC817-Footprint zeichnen**, bevor
bestückt wird. Zusammen mit der C12-Silkscreen-Prüfung (Beleg 9) und der
U3-Nähe-Auflage sind das jetzt drei Layout-Auflagen aus der Motormodul-Kette.

**Nebenbefund, nicht behoben:** R6 (Vorwiderstand des Sensor-Optokopplers U2,
2,2 kΩ im 0805-Footprint) liegt an 24 V und verheizt bei leitendem Sensor
24²/2,2 kΩ ≈ **0,24 W** — fast das Doppelte dessen, was ein 0805 trägt. Genau
der Fehler, den Beleg 11 für die neuen Schleifenwiderstände bewusst vermeidet.
Aus dem Altprojekt geerbt, nicht Gegenstand dieser Aufgabe, gehört
nachgerechnet.


## Beleg 13 — Ketten- und Leistungsstecker: SMD-Paare statt bedrahteter Paare (Aufgabe 5e, 2026-08-31)

**Der Fehler.** Beide Stecker waren Paare aus Buchse oben (J101/J103) und
Stiftleiste unten (J102/J104), beide **bedrahtet**, beide an derselben Stelle.
An derselben Stelle *müssen* sie sitzen: alle Platinen des Stapels sind gleich,
und eine Verschiebung hebt sich zwischen zwei gleichen Platinen nicht auf, sie
summiert sich — der Stift an der Unterseite von Modul N trifft die Buchse an der
Oberseite von Modul N+1 nur bei identischer (x|y). Zwei bedrahtete Bauteile
können sich aber keine Bohrungen teilen. Der 2×20 hat das am 31.08. gelöst,
indem er ein echter Stapelstecker mit durchgehendem Stift wurde (Beleg 6); bei
den beiden kleinen Steckern blieb der Fehler stehen.

### 13.1 Warum die Kette kein durchgehender Stift sein darf

Nachgerechnet, nicht angenommen. Bei durchgehenden Kontakten ist Kontakt *k*
**ein** Netz über den ganzen Stapel. Alle Module sind gleich gebaut, verbinden
also denselben Modulknoten mit demselben Kontakt. Läge `SEL_OUT` auf Kontakt *a*
und `SEL_IN` auf Kontakt *b*, verlangte die Kette `SEL_OUT(n) = SEL_IN(n+1)` für
**jedes** *n* — erfüllbar nur, wenn Netz(*a*) = Netz(*b*). Dann liegen alle
`SEL_IN` und alle `SEL_OUT` des Stapels auf einem Knoten: D und Q jedes
Flipflops kurzgeschlossen, das Schieberegister aus `tools/kette.py` wirkungslos.
**Die Rechnung hängt nicht an der Kontaktzahl** — auch zwei oder zwanzig
Kontakte des vorhandenen 2×20 können die Kette nicht tragen.

Zwei bedrahtete Hälften am selben Ort brauchten dieselben Bohrungen, und dieselbe
Bohrung *ist* ein durchgehender Kontakt. Die Mischung THT/SMD geht ebenfalls
nicht: die Bohrungen der bedrahteten Hälfte liegen genau dort, wo die Kontakte
der SMD-Hälfte auf der Gegenseite liegen müssten. Es bleibt: **beide Hälften
oberflächenmontiert.**

### 13.2 Einen 2×2-Stapelstecker gibt es bei LCSC nicht

Für den Leistungsstecker wäre ein durchgehender Stift **erlaubt** (beide Hälften
führen Pin für Pin `PWR24V`/`GND`). Gesucht bei LCSC und in der
JLCPCB-Bestückungsbibliothek. Auf Produktseiten tatsächlich gesehen:

| LCSC | Hersteller/Teil | Befund |
|---|---|---|
| `C35165` | BOOMELE „2.54-2*20PPC104" | Stapelstecker, **2×20**; Attribute: „Through Hole", „Current Rating: 3A", „Insulation Height: 8.3mm", „PIN Length: 12.3mm" (Zeichnung: 8,5 / 12,46 mm, s. Beleg 1) |
| `C5307344` | ZHOURI „PC104-2*20" | Stapelstecker, **2×20**; „Current Rating: 2.5A", „Insulation Height: 10.5mm", „PIN Length: 12.2mm" |
| `C5307345` | ZHOURI „PC104-2*40" | Stapelstecker, **2×40** |
| `C72555` | BOOMELE „2.54-2*8P3.8" | „Female header 2*8P pitch 2.54mm **Heightened, Pins are long 3.8mm**", 2×8 |
| `C5307342` / `C5307343` / `C5307346` | ZHOURI PM2.54-2*6 / PM2.54-2*16 / PM2.0-1*10 | die Nachbarnummern derselben Reihe: **gewöhnliche** Buchsen, Lötstift 2,8–3,2 mm |

**Kleinere Polzahlen als 2×20 gibt es in dieser Bauform nicht.** Das
nächstliegende „langbeinige" Teil (`C72555`) überbrückt den Spalt nicht einmal:
M = 3,8 − 1,6 = 2,2 mm, M + F = 2,2 + 8,5 = **10,7 mm < G = 11,4 mm**.

### 13.3 Die Leistung über den vorhandenen 2×20 zu führen, geht auch nicht

Dort ist **kein Kontakt frei**: alle 40 tragen Pico-Pins (`PIN_ROLLE`), und die
Sockelplatine verbindet sie mit dem Pico — 24 V auf einem davon zerstört ihn.
Elektrisch tot sind allein Kontakt 30 (`RUN`) und 35 (`ADC_VREF`), die kein
Modul anfassen darf. Das wäre **ein** Pfad für 24 V mit 3 A (`C35165`):

* **unter dem Bedarf** — der DRV8876 zieht über 2,5 A (Beleg 4 / SLVSDS7B), und
  der Stapelstrom ist die Summe aller Module darunter;
* **im 2,54-mm-Raster direkt neben 3,3-V-GPIO** (Kontakt 29 = GP22, 31 = GP26);
* gegen die ausdrückliche Design-Doc-Vorgabe, Motorströme vom Signalstecker
  getrennt zu führen.

### 13.4 Die gewählten Bauteile

Alle Angaben von tatsächlich geöffneten LCSC-Produktseiten, 2026-08-31.

**Stiftleiste unten — SMD, senkrecht, 2,54 mm:**

* **`C919361`** — BOOMELE „2.54-2*2P", **2×2**: „Mounting: Surface Mount (SMD),
  Vertical", „Insulation Height: 2.5mm", „Mating Pin Length: 6mm",
  „Current Rating: 3A", Kontakt Messing, 28 460 auf Lager.
  → **Stift des Leistungssteckers.**
* Dieselbe Bauform in anderen Polzahlen, als Beleg dafür, dass 2,5 mm / 6,0 mm
  der Familienwert ist: `C192300` (BOOMELE 2.54-2*4P, 2×4, SMD vertikal,
  2,5 mm / 6 mm, 3 A, 11 780 auf Lager); `C124390` (Ckmtw B-2100N06P-B111, 2×3,
  SMD vertikal, **2,0 mm** / 6 mm); `C124391` (Ckmtw B-2100N10P-B110, 2×5, SMD
  vertikal, 2,0 mm / 6 mm).
* **1×2 nicht gesehen** → die LCSC-Nummer des Kettenstecker-Stifts bleibt
  **leer**. Spezifikation: *Stiftleiste 1×2, 2,54 mm, SMD senkrecht,
  Isolierkörper ≤ 2,5 mm, Steckstift 6,0 mm.*

**Buchse oben — SMD, senkrecht, 2,54 mm, Isolationshöhe 8,5 mm:**

* `C261072` — BOOMELE „2.54-2*5P", 2×5: „Mounting: Surface mount, vertical",
  „Insulation Height: 8.5mm", „Current Rating: 2.5A", Messing vergoldet,
  3 175 auf Lager.
* `C52611` — BOOMELE „2.54-2*25P", 2×25: „SMD header 2*25P 2.54mm **H=8.5mm**
  Gold-plated", „Mounting: SMD".
* **1×2 und 2×2 nicht gesehen** → beide LCSC-Nummern bleiben **leer**.
  Spezifikation: *Buchsenleiste 1×2 bzw. 2×2, 2,54 mm, SMD senkrecht,
  Isolationshöhe 8,5 mm, ≥ 1 A (Kette) bzw. ≥ 2,5 A je Kontakt (Leistung).*

**Warum nicht die kurzen SMD-Buchsen:** `C2685112` (Liansheng FH-00339) und
`C2685115` (FH-00369), beide 2×20, „Surface Mount, Vertical", sind nur
**3,9 mm** hoch. M + F = 8,5 + 3,9 = 12,4 mm gegen G = 11,4 mm ergäbe 1,0 mm
Einstecktiefe — derselbe dünne Rand, den Beleg 1 schon einmal verworfen hat.

**Ein vollständig belegtes Paar existiert, nur in falscher Polzahl:**
`C261072` (Buchse 2×5) + `C124391` (Stift 2×5). Wer nicht warten will, bis die
2×2/1×2-Buchse auftaucht, kann darauf umsteigen; das ändert die Polzahl in
`stack_spec.STECKER_KETTE["pins"]` und in `tools/sch/modulsockel.py`, sonst
nichts an der Konstruktion.

### 13.5 Höhenrechnung

    G = STAPEL_ABSTAND − PLATINE_DICKE          = 13,0 − 1,6  = 11,40 mm
    F = Isolationshöhe der Buchse                             =  8,50 mm
    M = Isolierkörper 2,50 + Steckstift 6,00                  =  8,50 mm

    Einstecktiefe            = (M + F) − G = 17,00 − 11,40    =  5,60 mm
    Luft Stiftkörper/Buchse  = G − F − Isolierkörper          =  0,40 mm

**5,60 mm statt 3,1 mm** — der Gewinn kommt daher, dass ein SMD-Stift **auf** der
Platine sitzt statt in ihr: kein 3,0-mm-Lötschwanz, keine Platinendurchführung.
Der Wert wird in `stack_spec.EINSTECKTIEFE_SMD_PAAR()` aus den Bauteilmassen
gerechnet, nicht eingetragen. Zusätzlich geprüft: die Einstecktiefe ist nicht
grösser als der Stift lang ist (5,60 ≤ 6,00 mm).

**0,40 mm Luft** ist der neue enge Punkt: der Isolierkörper des Stifts kann nicht
in die Buchse eintauchen und muss über deren Oberkante bleiben. Nominell
positiv, aber im ungünstigen Toleranzstapel (± 0,2 mm je Bauteil, ± 10 %
Platinendicke) kann er verschwinden — dann stossen die Kunststoffe aneinander,
bevor die Abstandsbolzen sitzen. **Zwei belegte Auswege, beide Entscheidung des
Auftraggebers:**

1. Ein SMD-Stift mit **2,0 mm** Isolierkörper (dieselbe Bauform, belegt an
   `C124390`/`C124391`) → 0,90 mm Luft bei 5,10 mm Einstecktiefe.
2. `STAPEL_ABSTAND` von 13,0 auf **13,5 mm** → 0,90 mm Luft, 5,10 mm
   Einstecktiefe, 7,46 mm am Stapelstecker und **mehr** Luft über den Klemmen
   (1,80 statt 1,30 mm). Verbessert jede einzelne Reserve; nicht getan, weil
   `STAPEL_ABSTAND` nicht Teil der Aufgabe war und am Gehäuse (Aufgabe 9) hängt.

Damit dreht sich die Richtung der Enge um: `STAPEL_ABSTAND` wird jetzt **nach
unten** von der Buchsenluft begrenzt (G ≥ 8,5 + 2,5 = 11,0 mm, also
≥ 12,6 mm) — enger als die Klemmen (11,7 mm) — und nach oben praktisch von
nichts (erst ab 16,6 mm fiele die Einstecktiefe unter 2,0 mm).

### 13.6 Strom am Leistungsstecker

Engpass ist die **Buchse mit 2,5 A je Kontakt** (`C261072`, „Current Rating:
2.5A"); der Stift kann 3 A (`C919361`). Zwei Kontakte je Ader ergeben
rechnerisch **5,0 A vor Derating** — dieselbe Vorsicht wie in Beleg 4: das ist
eine Parallel-Summe von Einzelkontakt-Nennwerten, keine Herstelleraussage über
Parallelbetrieb bei ungleichen Kontaktwiderständen. **Ein** Motormodul (DRV8876,
ITRIP ≈ 2,538 A, Beleg 4 / Stromgrenze) passt mit Faktor 2; mehrere gleichzeitig
unter Volllast nicht. Mehr Reserve gäbe es nur mit mehr Kontakten — dann aber
mit dem 2×5-Paar aus 13.4.

### 13.7 Was das am Layout ändert

Ein SMD-Paar baut breiter als eine bedrahtete Stiftleiste: die Lötpads liegen
seitlich **neben** den Stiften. Höfe weiterhin aus echten `.kicad_mod`-Dateien
(kicad-footprints `a2d01395d2`), jetzt aus den SMD-Fassungen, und als
**Vereinigung beider Hälften** gerechnet:

| Stecker | Kontakt 1 | Fläche vorher | Fläche jetzt |
|---|---|---|---|
| Kette | 12,50 \| 2,75 (unverändert) | 10,73 0,98 14,27 7,07 | **9,09 0,87 15,91 7,17** |
| Leistung | 57,50 → **54,70** \| 42,00 | 55,73 40,23 61,82 46,32 | **50,10 40,22 61,84 46,32** |

Der Leistungsstecker **musste** wandern: an x = 57,50 hätte sein Hof bei
x = 64,64 über die Platinenkante gestanden. x = 54,70 ist die am weitesten rechts
liegende zulässige Lage, an der die Verdreh-Probe noch über der 2,5-mm-Reissleine
bleibt (**2,755 mm**; bei x = 56,00 wären es nur 2,460 mm) — abgesucht in
0,1-mm-Schritten über alle zulässigen Lagen. Die Reissleine wurde nicht gesenkt.

### 13.8 Auflagen, die aus dieser Bauart folgen

1. **Keine Durchkontaktierung zwischen den beiden Kontaktflächen des
   Kettensteckers.** Oben liegt `SEL_IN`, unten `SEL_OUT`. Die fehlende
   Verbindung *ist* die Funktion. Beim Leistungsstecker ist die Verbindung
   erlaubt, gehört aber in eine eigene Durchkontaktierung **neben** dem Pad, nicht
   in das SMD-Pad selbst.
2. **Zugentlastung für beide SMD-Steckerpaare.** Die Steckkraft eines ganzen
   Stapels darf nicht an den Lötstellen hängen. Zulässig: zwei zusätzliche
   mechanische Befestigungspunkte je Stecker **oder** ein Fügeverfahren, bei dem
   erst gesteckt und dann auf die Abstandsbolzen geschraubt wird. Welches von
   beiden, entscheidet die Layout-Aufgabe — aber nicht keines von beiden.
   Konkrete Bohrungskoordinaten sind hier bewusst **nicht** festgelegt; sie wären
   eine Zahl ohne Herkunft.
3. **Beidseitige SMD-Bestückung.** Der Stapel braucht jetzt Bauteile auf der
   Unterseite (die beiden Stiftleisten). Bei JLCPCB möglich, kostet aber einen
   zweiten Bestückungsvorgang. Vorher waren beide Seiten bedrahtet. Das ist ein
   Preis, kein Fehler — er gehört in die Kalkulation.
4. **Die Footprints bleiben Platzhalter**, nur genauere: die SMD-Fassungen der
   KiCad-Standardbibliothek statt der bedrahteten. Vor der Bestellung müssen
   eigene `.kicad_mod` gezeichnet und die Lage neu nachgerechnet werden;
   `tests/test_stack_spec.py` erzwingt das über den Abgleich der
   Footprint-Namen mit `tools/sch/modulsockel.py`.

### 13.9 Was der Test seither festhält

`tests/test_stack_spec.py` prüft neu eine **Regel** statt einer Zahl: jeder
Stecker trägt maschinenlesbar `durchgehend`, `montage_oben`, `montage_unten`,
`haelften_gleiche_netze`; ein durchgehender Stecker darf nur dort stehen, wo
beide Seiten dasselbe Netz führen, und ein Paar darf **nicht zwei bedrahtete
Hälften** haben. Auf einer Wegwerfkopie mit dem Stand vom 30.08. (nur die
Montageart zurückgedreht) meldet er vier Zusicherungen rot; erklärt man den
Kettenstecker stattdessen zum durchgehenden Stapelstecker, meldet er die zwei
anderen. Gegen die wortwörtliche Datei von `2c06340` läuft er gar nicht erst
durch — `STECKER_LEISTUNG` existierte dort nicht. Dass die Bauart des
Leistungssteckers nirgends maschinenlesbar stand, ist Teil des Befunds.


## Zusammenfassung für die Beschaffung

| Offener Punkt aus der Aufgabe | Antwort |
|---|---|
| Layout-Auflage C3 nah an U2 Pin 1 (Aufgabe-4-Fix-1) | C1 (100 nF) übernimmt nur die lokale HF-Abblockung, C3 (220 µF) die vom Datenblatt gemeinte Speicherkapazität — hält nur bei kurzer, niederinduktiver Verbindung C3↔U2 Pin 1 (Beleg 7); an Aufgabe 6 (PCB-Layout) weitergereicht |
| Steckerhöhe vs. 15 mm, ursprüngliches Buchse/Stift-Paar | Passte rechnerisch, aber nur mit 1,1 mm Einstecktiefe — dünner Rand (Beleg 1) |
| **Entscheidung 2026-08-31 (erste Runde)** | Stapelstecker (Buchse mit durchgehendem Stift, C35165) für 39 der 40 Leitungen; eigener Kettenstecker (C492401/C541849) nur für `SEL`. `STAPEL_ABSTAND` zunächst bei 15,0 mm belassen — passte komfortabel zum Stapelstecker (5,96 mm Einstecktiefe), der Kettenstecker trug aber nur 1,1 mm (Beleg 1 Nachtrag, Beleg 6) |
| **Entscheidung 2026-08-31 (zweite Runde)** | Keine passende längere Stiftleiste gefunden (zwei unabhängige Suchen) → `STAPEL_ABSTAND` auf **13,0 mm** gesenkt: Kettenstecker jetzt 3,1 mm Einstecktiefe, Stapelstecker 7,96 mm; Klemmenhöhe belegt (DB128L 10,10 mm, K7805 10,2 mm, beide Datenblätter gelesen) bleibt unter der 11,0-mm-Reissleine, 1,2–1,3 mm Luft im Spalt (Beleg 6, zweite Runde). Gehäuse (Aufgabe 9) noch auf 13,0 mm nachzuziehen |
| D-Flipflop mit Löscheingang | Gefunden: SN74LVC1G175DCKR, C202238, SOT-363-6, JLCPCB-bestückbar; Primärquelle TI SCES560G; braucht neue Leitung ODER lokales RC-POR |
| Gatter (NOT, 2× AND) | ~~Beide JLCPCB-bestückbar: C8207 (SOT-353) und C548580 (XSON-8, deckt beide AND-Funktionen)~~ — **überholt, s. Nachtrag 2026-08-31 (2. Runde):** `NRST` war verpolt (AND statt NAND auf einen aktiv-LOW-Pin); jetzt 1× Dual-NAND `SN74LVC2G00DCUR` (C206109, VSSOP-8 — NICHT SOT-363, s. Anmerkung) deckt NOT (via NAND(Q,Q)) UND das NRST-Gatter ab, plus 1× Einzel-AND `SN74LVC1G08DCKR` (C7832, SOT-353) für BOOT0 — **zwei physische Gatter-ICs statt drei** |
| Leistungsstecker + Strombelastbarkeit | 2×2 derselben Stecker-Familie, ~5 A/Ader vor Derating (Engpass Buchse 2,5 A/Kontakt); Positionszahl ist Vorschlag, kein Vertragswert |
| Klemme 3-polig | DB128L-5.08-3P-GN-S, C395869, 16 A/300 V |
| `tools/stack_spec.py`, `docs/vertrag.md`, Tests | Nachgezogen: SEL raus aus PIN_ROLLE/RESERVIERT, STECKER_STAPEL/STECKER_KETTE neu, Vertrag neu erzeugt, Tests ergänzt (siehe Beleg 6) |
| Stromgrenze DRV8876 (Motormodul, Aufgabe 5) | Altprojekt-Wert (R5=2,2k → 1,5 A) reichte für den 2-A-Motor nicht (dokumentierter Muttern-Board-Fehler); neu gerechnet über TI-Gleichung 3 (SLVSDS7B, Abschnitt 7.3.3.2): R5 = 1,3 kΩ → ITRIP ≈ 2,538 A (~27 % Marge über 2 A, deutlich unter IOCP-min 3,5 A); R10 bleibt DNP, unveränderter Altprojekt-Wert (4,7 kΩ) |
| 3,3-V-Haushalt des Stapels (Aufgabe 5) | Nachgerechnet mit den zwei neuen Verbrauchern des Motormoduls (Kennwiderstände, VREF) — bleibt unkritisch: ≈5,56 mA/Modul worst case, ~53 Module trügen das 300-mA-Budget der Pico-3V3-Schiene; Details Beleg 8 |
| Layout-Auflage C12-Polarität (Aufgabe 5) | Schaltplan-Polung geprüft (Pin 1 „+" an +24V, testgesichert) — Aufgabe 7 muss zusätzlich die Footprint-Silk-Polarität gegen Pad 1 prüfen, das sieht keine ERC/Netzlisten-Prüfung; Details Beleg 9 |
| **Notaus-Verriegelung wirkte nicht (Aufgabe-5-Fix-1)** | Die Diodenklemme D2+R14 liess den nSLEEP-Pin bei ≈3,05 V stehen (V_IL wäre 0,8 V); ersetzt durch ein UND-Gatter U3 (`SN74LVC1G08`, C7832, keine neue Bauteilnummer) + C14, D2/R14 entfallen, D3/D4 jetzt Schottky (BAT54W, C699107). Reserve jetzt 0,70 V gegen V_IL bzw. 1,65 V gegen V_IH; Details Beleg 10 |
| **Notaus-Eingang auf Ruhestrom umgebaut (Aufgabe 5d)** | Der externe Kontakt ist jetzt ein **Öffner**: geschlossen = in Ordnung, offen = Notaus — und damit lösen auch Kabelbruch, gezogener Stecker und lose Klemme aus. Je Kanal 24 V über 2 × 3,3 kΩ (1206, C26032) hinaus, zurück über eine zweite Ader in einen PC817 (C97308), Emitterfolger gegen 4,7 kΩ Pulldown, von dort über einen Open-Drain-Inverter (SN74LVC1G06, **C7828**) auf die Sammelleitung. **D3/D4 entfallen** (eine Diode in Reihe zum Open-Drain-Ausgang liesse null Reserve). An U3/R9/R15/`U1_NSLEEP` **keine Änderung**. Details Beleg 11 |
| **Zwei Auflagen aus Aufgabe 5d, die niemand übersehen darf** | (1) **Unbenutzter Kanal muss am Stecker gebrückt werden** — Kanal 1 = J3 Pin 1+2, Kanal 2 = J3 Pin 3+4, sonst meldet er dauerhaft Notaus (Jumper 2,54 mm; zusätzlich Siebdruck-Auflage für Aufgabe 7). (2) **Die bestehende Verkabelung des Pêche-aux-Canards-Exponats muss umgeklemmt werden** — J3 hat weiterhin vier Pole, ein altes Kabel passt mechanisch, das Exponat stünde danach dauerhaft auf Notaus. Details Beleg 11, Auflagen 1 und 2 |
| **Optokoppler-Footprint passt nicht (Nebenbefund Aufgabe 5d)** | `SOP-4_3.8x4.1mm_P2.54mm` gegen den PC817-Gullwing (Körper 6,5 × 4,58 mm, Spanne 10,0 mm, Reihe 7,62 mm laut D2-A03101EN) — betrifft auch das geerbte U2. Aufgabe 7 muss einen eigenen Footprint zeichnen; ebenso offen: R6 verheizt an 24 V ≈ 0,24 W in einem 0805. Details Beleg 12 |
| A_IPROPI des DRV8876 nachgeprüft (Aufgabe-5-Fix-1) | **1000 µA/A**, bestätigt aus dem PDF SLVSDS7B, Abschnitt 6.5, Block „CURRENT SENSE AND REGULATION (IPROPI, VREF)" — der Wert 1100 µA/A gehört zu keinem der beiden Familienmitglieder (der Schwestertyp DRV8874, Dok. SLVSF66A, nennt 450 µA/A). Damit bleibt ITRIP = 2,538 A bei R5 = 1,3 kΩ richtig, Marge unverändert ~27 % über 2 A |
| **Ketten- und Leistungsstecker waren nicht baubar (Aufgabe 5e)** | Beide waren Paare aus **bedrahteter** Buchse oben und **bedrahteter** Stiftleiste unten am selben Ort — zwei bedrahtete Bauteile können sich aber keine Bohrungen teilen. Jetzt **SMD-Paare** (Buchse oben, Stiftleiste unten, gleicher Ort, keine Durchkontaktierung dazwischen); Einstecktiefe 5,60 statt 3,1 mm. Ein 2×2-**Stapelstecker** existiert bei LCSC nicht (nur 2×20/2×40), und über den vorhandenen 2×20 lässt sich die Leistung nicht führen (kein freier Kontakt, alle 40 sind Pico-Pins). Belegte Nummer: **C919361** (Stift 2×2). Buchsen 1×2/2×2 und Stift 1×2: **Nummer offen**, Spezifikation in Beleg 13.4; vollständig belegtes Ersatzpaar in 2×5: C261072 + C124391. Enger Punkt: 0,40 mm Luft über der Buchse (Beleg 13.5) |

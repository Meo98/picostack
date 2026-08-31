# Bauteilwahl Etappe 1b: Stapelstecker, Auswahlketten-Logik, Leistung, Klemmen

**Stand:** 2026-08-31. Bestand und Preise bei LCSC/JLCPCB ändern sich laufend;
die hier genannten Zahlen sind Stichproben vom Recherchezeitpunkt, keine
Garantie. Vorlage und Sorgfaltsmassstab: `hardware/bauteile.md` (Etappe 1a).

## Bauteiltabelle

| Zweck | Typ | Bauform | LCSC | geprüft | Quelle |
|---|---|---|---|---|---|
| Signalstecker, Buchse (oben, 2×20) | BOOMELE/ZHOURI-Familie, 2,54 mm Buchsenleiste | THT, Gehäusehöhe **8,5 mm** über Platine | C2977589 | ja | LCSC-Produktseite `lcsc.com/product-detail/C2977589.html`; Datenblatt (ZHOURI, Rev. ZRLCGY2025-06-17-CJ A/1), Masszeichnung „8,5±0,2"; JLCPCB-Produktseite `jlcpcb.com/partdetail/2.54-2*20/C2977589` (SMT Assembly, Economic/Standard PCBA) |
| Signalstecker, Stift (unten, 2×20) | BOOMELE 2,54 mm Stiftleiste, gerade | THT, Stift **6,0 mm** oberhalb / **3,0 mm** unterhalb des Isolierkörpers (Gesamtlänge 9,0 mm) | C50980 | ja | LCSC-Produktseite `lcsc.com/product-detail/Male-Header_Made-in-China-2-54mm-2-20P-Header_C50980.html`; Datenblatt (东莞康孚电子), Masszeichnung „3.0" / „6.0"; JLCPCB-Produktseite `jlcpcb.com/partdetail/BOOMELE-2_54mm2_20PHeader/C50980` (SMT Assembly, Economic/Standard PCBA) |
| Leistungsstecker, Buchse (oben, 2×2) | gleiche ZHOURI-Familie, 2,54 mm | THT, **8,5 mm** über Platine, 2,5 A/Kontakt | C2977590 | ja | LCSC-Produktseite `lcsc.com/product-detail/Female-Headers_ZHOURI-2-54-2-2_C2977590.html` (Rohdaten: „2.5A", „8.5mm insulation height") |
| Leistungsstecker, Stift (unten, 2×2) | gleiche BOOMELE-Familie, 2,54 mm | THT, 6,0/3,0 mm, 3 A/Kontakt | C66690 | ja | LCSC-Produktseite `lcsc.com/product-detail/Male-Header_Double-Rows2-2p-pitch2-54mm_C66690.html` (Rohdaten: „3A", „6mm"/„3mm") |
| D-Flipflop, asynchroner Löscheingang | SN74LVC1G175DCKR (TI) | **SOT-363-6** (SC-70-6), 6 Pins | C202238 | ja | LCSC-Produktseite `lcsc.com/product-detail/74-Series_TI_SN74LVC1G175DCKR_SN74LVC1G175DCKR_C202238.html`; JLCPCB-Produktseite `jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G175DCKR/C202238` (SMT Assembly, Economic/Standard PCBA, MSL 1); Datenblatt Nexperia 74LVC1G175 Rev. 11 (15. Aug. 2023) — baugleiche Funktion, TI-Bauteil elektrisch/pinkompatibel |
| Gatter NOT (Invertierung Q) | SN74LVC1G04DCKR (TI) | **SOT-353** (SC-70-5), 5 Pins | C8207 | ja | LCSC-Produktseite `lcsc.com/product-detail/C8207.html`; JLCPCB-Produktseite `jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G04DCKR/C8207` (SMT Assembly, Economic/Standard PCBA, MSL 1) |
| Gatter Dual-AND (RESET, BOOT0) | 74LVC2G08GT,115 (Nexperia) | **XSON-8** (1×2 mm), 8 Pins | C548580 | ja | JLCPCB-Produktseite `jlcpcb.com/partdetail/Nexperia-74LVC2G08GT115/C548580` (SMT Assembly, Economic/Standard PCBA, MSL 1) |
| 5-V-Regler | K7805-2000R3 | SIP-3 | C2931187 | ja | bereits geprüft in Etappe 1a / LED-Dimmer-Projekt, siehe `hardware/bauteile.md` — hier unverändert übernommen, nicht neu recherchiert |
| Klemme 2-polig | DB128L-5.08-2P-GN-S | THT, 5,08 mm | C395868 | ja | bereits geprüft in Etappe 1a / LED-Dimmer-Projekt — unverändert übernommen |
| Klemme 3-polig | DB128L-5.08-3P-GN-S | THT, 5,08 mm | C395869 | ja | LCSC-Produktseite `lcsc.com/product-detail/C395869.html` (16 A, 300 V, M2-Schraube, 12–22 AWG); JLCPCB-Produktseite bestätigt (DORABO-Familie, SMT/Wave-Assembly, Economic/Standard PCBA) — selbe Farbe/Baureihe wie die bereits geprüfte 2-polige Klemme |

Alle sieben neu recherchierten Nummern wurden auf einer echten LCSC- oder
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

## Beleg 2 — D-Flipflop mit asynchronem Löscheingang: gefunden

**Ergebnis: Ja, es gibt eines, JLCPCB-bestückbar.** `SN74LVC1G175DCKR`
(Texas Instruments), LCSC C202238, Gehäuse SOT-363-6 (6 Pins). Laut
Nexperia-Datenblatt zur baugleichen Funktion 74LVC1G175 (Rev. 11, 15. Aug.
2023), Abschnitt 1 „General description": „individual data (D) input,
clock (CP) input, master reset (MR) input, and Q output […] The master
reset (MR) is an asynchronous active LOW input and operates independently
of the clock input." Funktionstabelle (Abschnitt 7, Tabelle 4): `MR=L` →
`Q=L`, unabhängig von Takt und D. Das TI-Bauteil ist die pin- und
funktionskompatible Variante desselben Standardtyps (Familienname
„74LVC1G175" bei beiden Herstellern identisch); auf der tatsächlich
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

## Beleg 4 — Leistungsstecker: Bauform gewählt, Strombelastbarkeit belegt

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

## Zusammenfassung für die Beschaffung

| Offener Punkt aus der Aufgabe | Antwort |
|---|---|
| Steckerhöhe vs. 15 mm | Passt rechnerisch (14,5 mm Reserve gegen 13,4 mm Spalt), aber nur mit 1,1 mm Einstecktiefe — dünner Rand, drei Wege in Beleg 1, Entscheidung offen |
| D-Flipflop mit Löscheingang | Gefunden: SN74LVC1G175DCKR, C202238, SOT-363-6, JLCPCB-bestückbar; braucht neue Leitung ODER lokales RC-POR |
| Gatter (NOT, 2× AND) | Beide JLCPCB-bestückbar: C8207 (SOT-353) und C548580 (XSON-8, deckt beide AND-Funktionen) |
| Leistungsstecker + Strombelastbarkeit | 2×2 derselben Stecker-Familie, ~5 A/Ader vor Derating (Engpass Buchse 2,5 A/Kontakt); Positionszahl ist Vorschlag, kein Vertragswert |
| Klemme 3-polig | DB128L-5.08-3P-GN-S, C395869, 16 A/300 V |

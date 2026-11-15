# PicoStack v3 -- der Pico treibt direkt

Stand 2026-11-15. Entscheidungen mit Meo abgestimmt (Chat, 15.11.:
"mach alles genau so, wie du das fuer richtig haeltst", plus eine
Vorgabe: das Modul muss am USB-5V des Pico laufen, damit man beim
Programmieren kein Netzteil braucht, und eingebaut am 5-30-V-Netzteil).
Status: beschlossen, in Umsetzung auf Zweig `v3`.

## Warum v3

Die Bewertung von v2.1 (Chat 15.11.) fand drei Dinge, die sich nicht
durch weiteres Verlegen beheben lassen:

1. **Zu viel Intelligenz je Modul.** Jedes Modul trug einen STM32C011,
   ein Flipflop, zwei Gatter-ICs, Kennwiderstaende, zwei Ketten- und
   zwei Leistungsstecker -- nur damit der Pico das Modul durch den
   Stapel flashen und per Token-Kette auswaehlen kann. Das heisst eine
   zweite Prozessorfamilie, eine zweite Toolchain, ein eigener
   Bootloader-Host und eigene Auswahl-Hardware, bevor eine LED dimmt.
   Reale Exponate brauchen ein bis zwei Module; der Pico hat 16
   PWM-Kanaele und reicht 23 freie GPIO durch den Stapel.
2. **Die tragende Annahme war nach zweieinhalb Monaten ungeprueft**
   (Pico flasht STM32C0 ueber den ROM-Bootloader; nie ein Chip gekauft),
   und es gab **null Firmware** fuer die Module.
3. **Drei Verlegerunden, immer noch funktionsfremd platziert**
   (VM-Abblockung 11,7 mm vom Pin, MCU 50 mm vom Treiber, FET 51 mm von
   seiner Klemme; Bericht `.superpowers/sdd/2026-10-14-picostack-v3/
   recherche/04-referenz-layouts-review.md`). Ursache: Platzierung nach
   Vertragszonen und Autorouter statt nach Stromfluss.

Dazu: Regler K7805-1000R3/-2000R3 bei LCSC ausverkauft, 1x20-
Stapelbuchse ohne LCSC-Quelle, 11-16 Extended-Teile je Board, 82x73 mm
fuer einen Einkanal-Dimmer.

## Beschlossene Grundsaetze

1. **Dumme Module.** Kein Modul-MCU, keine Kette, kein Bootloader,
   keine Modul-Firmware. Der Pico treibt jeden Kanal direkt ueber
   GPIO. Was wegfaellt: mehr als vier Module gleichen Typs im Stapel,
   "smarte" Module. Was man gewinnt: ein Board mit einem Drittel der
   Stueckliste, das die bestehenden Exponatplatinen sofort ersetzt.
2. **Pico-Geometrie bleibt der Stapel** (v2-Erbe): zwei 1x20-
   Stapelbuchsen in echter Pico-Anordnung, der Pico steckt zuoberst,
   alle 40 Pins laufen durch. Neu: Pico liegt QUER (USB zeigt zur
   linken Kante, Antenne nach rechts), Lastklemmen in einer Reihe an
   der unteren Kante.
3. **Signalbaenke + Slot-Matrix statt Adressen.** Die 16 PWM-faehigen
   GPIO GP7..GP22 sind in vier Baenke A-D zu je vier Pins geteilt, dazu
   die ADC-Bank GP26..GP28. Ein Modul belegt EINE Bank; welche, waehlt
   eine 0603-0-Ohm-Matrix (Signale x Baenke) auf dem Board. Vorgabe ab
   Werk: Motor = Bank A, Dimmer = Bank B, Motor-Strommessung = GP26.
   Damit laeuft "ein Motor + ein Dimmer" ohne Loeten. Alle 16 Pins
   sind getrennte PWM-Kanaele des RP2040 (Slices 3B..7B, 0A..3A).
4. **Versorgung je Board, zwei Quellen gleichberechtigt.** Klemme
   6-30 V -> Verpolschutz -> TVS -> Buck 5 V -> Schottky -> VSYS. USB am
   Pico speist VSYS ueber die Pico-eigene Diode. Beide duerfen
   gleichzeitig anliegen: zwei Dioden, kein Rueckstrom in den
   USB-Host, kein Rueckstrom in den Buck. Die Lasten (LED, Motor)
   haengen an der Klemmenspannung und laufen ohne Netzteil nicht --
   das ist gewollt (programmieren ohne Last).
5. **Werkzeugkette bleibt** (Vertrag als Code, Generatoren, Tore,
   Rot-Nachweis), aber der Vertrag wird neu geschrieben (v4) und auf
   das Noetige gekuerzt. Platzierung von Hand nach Stromfluss
   (Bericht 04, Regeln A1-A12); der Router verlegt nur noch.
6. **Reihenfolge: erst ein Board auf den Tisch.** Dimmer zuerst (die
   LED-Dimmer-Exponate sind der naechste Bedarf), Motor danach auf
   demselben Vertrag. Fuenf Stueck bei JLCPCB bestellen, in Betrieb
   nehmen, dann erst Spec-Dokument und KiCad-Vorlage fuer Dritte.

## Vertrag v4 (`tools/stack_spec.py`, VERTRAG_VERSION = 4)

### Umriss und Mechanik

| Groesse | Wert | Herleitung |
|---|---|---|
| Platine | 74 x 50 mm, Ecken R3 | Pico quer (51 mm) + Versorgungsspalte rechts (14 mm) + Rand; Klemmenreihe unten (54 mm nutzbar zwischen den M3-Freihaltekreisen) |
| M3-Loecher | 4,0 mm von jeder Kante: (4|4) (70|4) (4|46) (70|46), Bohrung 3,2, Freihaltekreis 7 mm | wie v1-v2.1 |
| Stapelabstand | **12,0 mm** (M3-Bolzen 12 mm) | Pimoroni Pico Stacking Headers: Buchse 8,5 mm, Stift 11 mm. Durch die eigene Platine (1,6) bleiben 9,4 mm Stift; Spalt 12,0 - 1,6 = 10,4 -> Einstecktiefe 7,5 mm, 1,9 mm Luft zwischen Buchsenoberkante und Platine darueber. Bei 11,0 mm stiesse der Stift auf die Platine darunter. ZU VERIFIZIEREN am echten Teil (Rot-Nachweis in `tests/test_stack_spec.py` rechnet gegen diese Zahlen). |
| Bauteilhoehe oben | <= 9,5 mm | 12,0 - 1,6 - 0,9 Reserve. Klemmen 8,5, SMD-Elkos 7,7, Spule 4,5 |
| Bauteilhoehe unter dem Pico (PICO_SCHATTEN) | <= 8,0 mm | Buchsenhoehe 8,5 |
| Verdreht-Sicherheit | Lochbild punktsymmetrisch; alle Stapelreihen so gelegt, dass ein um 180 Grad verdrehtes Modul NIRGENDS steckt | Reihen bei y=10,00 und 27,78 landen verdreht bei 22,22 und 40,00; die 1x4-Leistungsreihe (y=4) landet in der Klemmenreihe. Kupferfreie Landepunkte (LANDE_SPERRRADIUS 1,5 mm) bleiben als Probe. |

### Stecker (alle bedrahtet, ein Bauteiltyp)

| Platz | Bauteil | Lage (Kontakt 1) | Netze |
|---|---|---|---|
| `stapel_unten` | Stapelbuchse 1x20, Pico-Pins 1..20 | (9,00 \| 27,78), Pin 1 links, +x | Pico-Pinbild |
| `stapel_oben` | Stapelbuchse 1x20, Pico-Pins 21..40 | (57,26 \| 10,00), Pin 21 rechts, -x | Pico-Pinbild |
| `leistung` | Stapelbuchse 1x4 (aus 1x20 abgelaengt) | (26,00 \| 4,00), +x | VIN, VIN, GND, GND -- 3 A je Kontakt, 3 A Durchleitung |
| `qwiic` | JST SH 4-pol (SM04B-SRSS-TB) | obere Kante, rechts der Leistungsreihe | GND, 3V3, SDA (GP4), SCL (GP5) |
| `user` | Stiftleiste 1x6 | obere Kante links | GP0, GP1, GP2, GP3, 3V3, GND |
| Lastklemmen | Phoenix PT 1,5/2-3,5 (3,5 mm) bzw. MKDS 3/2-5,08 (Motor) | untere Kante, kantenbuendig, Oeffnung nach aussen, in Kanalreihenfolge von links; Einspeisung ganz rechts | je Modul |

Der Pico-Ursprung: Pin 1 bei (9,00|27,78), Reihe 1..20 nach +x im
2,54-Raster; Pin 21 bei (57,26|10,00), 21..40 nach -x. Reihenabstand
17,78 mm = Pico-Datenblatt. PICO_SCHATTEN = (7,6 | 8,4 | 58,6 | 29,4),
ANTENNE_FREI (Pico W, Antenne am USB-fernen Ende) = (46,0 | 8,4 |
58,6 | 29,4): dort kein Kupfer auf F.Cu und keine Schaltregler-Teile.

### Pinrollen (PIN_ROLLE, Pico-Pinnummern)

* GND: 3, 8, 13, 18, 23, 28, 33, 38. 3V3: 36. VSYS: 39 (Einspeisepunkt
  der Module). VBUS: 40 (nicht belegbar). 3V3_EN 37, RUN 30, ADC_VREF
  35, AGND 33: nicht belegbar.
* I2C_SDA = GP4 (Pin 6), I2C_SCL = GP5 (Pin 7): Qwiic-Port. Pull-ups
  4,7 k NUR auf dem Modul, das sie per Loetbruecke aktiviert (Vorgabe:
  offen; der Pico-Treiber schaltet seine internen Pull-ups ein).
* NOTAUS = GP6 (Pin 9): open-drain, wired-AND, aktiv-LOW = gesperrt.
  Pull-up 10 k auf jedem Modul, das NOTAUS treibt (Motor). Module, die
  es nicht brauchen, lassen den Pin unberuehrt.
* Bank A = GP8..GP11 (Pins 11,12,14,15), Bank B = GP12..GP15 (16,17,
  19,20), Bank C = GP16..GP19 (21,22,24,25), Bank D = GP20,GP21,GP22,
  GP7 (26,27,29,10). ADC-Bank = GP26,GP27,GP28 (31,32,34).
* GP0..GP3 (Pins 1,2,4,5): frei, am User-Header.

### Slot-Matrix

Je Modulsignal S_k (k = 1..4) vier 0603-Plaetze JB_k_A..JB_k_D nach
Bank-Pin k; genau EINER ist bestueckt (0 Ohm, JLC-Basic). Fuer das
ADC-Signal drei Plaetze JA_26/27/28. Die Probe: je Signal genau ein
bestueckter Platz, und kein Bank-Pin von zwei Signalen. Der
Bestueckungsdruck traegt die Bankbuchstaben.

### Versorgungszelle (VERSORGUNG)

J90 Klemme VIN 6-30 V -> Q90 AOD409 (P-Kanal, Drain an der
Einspeisung, Source an +VIN_LOKAL; Gate ueber R91 100 k an GND, D92
Zener 12 V Gate-Source: Vgs = -min(Vin, 12 V), bei 6 V voll
durchgesteuert, bei 30 V unter dem 20-V-Limit -- behebt den
Bericht-03-Befund "IRFR5305 bei 6 V nur -3 V") -> D90 TVS SMCJ30A
(nur Transienten; klemmt ueber dem 36-V-Maximum des Reglers, Dauer-
Ueberspannung ist nicht Teil der Zusage) -> C90 47 uF/50 V SMD-Elko +
C91/C92 2x 10 uF/50 V 1210 -> U90 TPS5430DDAR (JLC-Basic, 5,5-36 V,
3 A, 500 kHz; Boot 10 nF, L90 15 uH SWPA6045S150MT, Freilauf D93
SS36C, Cout C93 100 uF/16 V SMD-Elko, Teiler R92 10 k / R93 3,3 k ->
4,92 V) -> D91 SS36C -> VSYS. LED90 gruen an +VIN_LOKAL ueber 10 k
("VIN"). Der Buck sitzt unter dem Pico am USB-Ende (fern der
Antenne), Schleife IC-L-Diode-Cin auf kleinstem Umfang, Thermal-Vias
unter dem PowerPAD.

Zusagen (pruefbar): Drain von Q90 am Einspeisenetz; Zener zwischen
Gate und Source; Diode zwischen Reglerausgang und VSYS; Regler-
Eingangsfenster umfasst 6-30 V; alle Netze, die 4 A tragen, in der
Netzklasse Stamm (STROMBUDGET wie v2.1: 4 A je Modul, 3 A je Kanal,
3 A Durchleitung, Motor 2,538 A).

### Dimmer-Kanal (unveraendert bewaehrt)

Qn NCE6020AK low-side, RGn 100 Ohm vom Bank-Pin, RPn 100 k nach GND,
Dn SS36C Freilauf Drain -> +VIN_LOKAL, Jn Klemme (1 = +VIN, 2 =
geschaltetes Minus). Gate bei 3,3 V: Espace-Felderfahrung mit der
NCE60xx-Familie bei 3 A je Kanal; am ersten Board nachmessen.

### Motormodul (naechste Etappe, gleicher Vertrag)

DRV8876 im PH/EN-Modus: S1 = EN (PWM), S2 = PH (Richtung), S3 =
nFAULT (Eingang, open-drain), S4 = nSLEEP ueber 1G08 UND NOTAUS
(Hardware-Sperre bleibt, fail-safe), IPROPI -> ADC-Bank.
Notaus-Ruhestromschleife mit PC817 wie v2 (1G07, nicht 1G06).

## Was aus v2.1 wegfaellt

Modul-MCU-Nest (STM32C011, 1G175, 2G00, 1G08-Kette, Kennwiderstaende,
NRST-Glied), Kettenstecker, SMD-Steckerpaare, Randpads (ersetzt durch
User-Header), Sockelplatine (v1-Archiv im Tag v0.1.0), `tools/kette.py`,
`firmware/sockel/*` (AN3155), `docs/nachweis-2026-08.md`, die Berichte
unter `.superpowers/sdd/` bis v2.1 bleiben als Geschichte im Git.

## Umsetzung (Zweig `v3`)

1. Repo aufraeumen: Sockel, Kette, AN3155, Reports im Wurzelverzeichnis,
   v2-Generatoren, die den Modulsockel brauchen.
2. Vertrag v4 + `tests/test_stack_spec.py` (jede Zahl oben als
   Zusicherung, Rot-Nachweis fuer Stapelabstand, Baenke, Matrix,
   Verdreht-Probe).
3. `tools/sch/versorgung.py` (Buck-Zelle) und `tools/sch/dimmermodul.py`
   neu; ERC 0/0; Netzlisten-Proben (Zener, Drain, VSYS-Diode, Matrix).
4. `tools/pcb/spec_dimmer_basis.py` neu: Platzierung von Hand nach
   Stromfluss, Hof-Ueberlappungsprobe, dann KiCadRoutingTools, DRC 0/0,
   Strombelastung gruen.
5. Fertigungsdaten Dimmer1/3/4, BOM mit LCSC-Nummern, ORDERING.md.
6. `firmware/pico/picostack.py` (MicroPython): `Dimmer(bank, kanaele)`,
   `Motor(bank, adc)`, `notaus()`.
7. README/Website/vertrag.md auf v3; Notiz.
8. Danach: Motormodul v3, Bestellung, Inbetriebnahme.

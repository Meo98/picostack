# PicoStack -- Vertrag v4

Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.

## Umriss und Mechanik

| Groesse | Wert |
|---|---|
| Platine | 74 x 58 mm, Ecken R3 |
| Dicke | 1.6 mm |
| M3-Loecher | (4\|4), (4\|54), (70\|4), (70\|54) -- Bohrung 3.2 mm, Freihaltekreis 7 mm |
| Stapelabstand | 12 mm (M3-Bolzen 12 mm) |
| Einstecktiefe | 7.5 mm; Luft Stiftende 1.0 mm, Luft Buchsenoberkante 1.9 mm |
| Bauteilhoehe | oben <= 9.5 mm, unter dem Pico <= 8 mm |
| Stapelleiste | Pimoroni Pico Stacking Headers (Paar 1x20); 3 A je Kontakt; Buchse 8.5 mm, Stift 11 mm |
| Verdreht aufgesetzt | steckt nirgends (kleinster Stift-Kontakt-Abstand 2.44 mm) |

## Pico-Lage

Der Pico liegt quer, USB zur linken Kante, Antenne nach rechts. Pin 1 bei (9\|27.78), Reihe 1..20 nach +x; Pin 21 bei (57.26\|10), Reihe 21..40 nach -x. Reihenabstand 17.78 mm.

* Pico-Schatten (R1/R3): (7.63\|8.39)-(58.63\|29.39)
* Antennenzone, kupferfrei auf beiden Lagen (P5): (46\|11.9)-(60.6\|25.9)
* Klemmenzone (R2): (7.5\|49)-(66.5\|58)

## Stapelstecker

| Platz | Zweck | Kontakt 1 | Drehung | Hof |
|---|---|---|---|---|
| stapel_unten | Stapelbuchse 1x20, Pico-Pins 1..20, nach +x | (9\|27.78) | 90 | (7.23\|26.01)-(59.03\|29.55) |
| stapel_oben | Stapelbuchse 1x20, Pico-Pins 21..40, nach -x | (57.26\|10) | 270 | (7.23\|8.23)-(59.03\|11.77) |
| leistung | Stapelbuchse 1x4: VIN, VIN, GND, GND (Durchleitung) | (27\|4) | 90 | (25.23\|2.23)-(36.39\|5.77) |

Leistungsreihe: 1 = VIN, 2 = VIN, 3 = GND, 4 = GND (3 A Durchleitung).
Qwiic: 1 = GND, 2 = 3V3, 3 = I2C_SDA, 4 = I2C_SCL.
User-Header: 1 = GP0, 2 = GP1, 3 = GP2, 4 = GP3, 5 = 3V3, 6 = GND.

## Pinrollen

| Pico-Pin | GP | Rolle |
|---|---|---|
| 1 | GP0 | USER_GP0 |
| 2 | GP1 | USER_GP1 |
| 3 |  | GND |
| 4 | GP2 | USER_GP2 |
| 5 | GP3 | USER_GP3 |
| 6 | GP4 | I2C_SDA |
| 7 | GP5 | I2C_SCL |
| 8 |  | GND |
| 9 | GP6 | NOTAUS |
| 10 | GP7 | BANK_D_S4 |
| 11 | GP8 | BANK_A_S1 |
| 12 | GP9 | BANK_A_S2 |
| 13 |  | GND |
| 14 | GP10 | BANK_A_S3 |
| 15 | GP11 | BANK_A_S4 |
| 16 | GP12 | BANK_B_S1 |
| 17 | GP13 | BANK_B_S2 |
| 18 |  | GND |
| 19 | GP14 | BANK_B_S3 |
| 20 | GP15 | BANK_B_S4 |
| 21 | GP16 | BANK_C_S1 |
| 22 | GP17 | BANK_C_S2 |
| 23 |  | GND |
| 24 | GP18 | BANK_C_S3 |
| 25 | GP19 | BANK_C_S4 |
| 26 | GP20 | BANK_D_S1 |
| 27 | GP21 | BANK_D_S2 |
| 28 |  | GND |
| 29 | GP22 | BANK_D_S3 |
| 30 |  | RUN |
| 31 | GP26 | ADC_26 |
| 32 | GP27 | ADC_27 |
| 33 |  | AGND |
| 34 | GP28 | ADC_28 |
| 35 |  | ADC_VREF |
| 36 |  | 3V3 |
| 37 |  | 3V3_EN |
| 38 |  | GND |
| 39 |  | VSYS |
| 40 |  | VBUS |

Nicht belegbar: Pin 30: RUN -- Reset des RP2040, aktiv-LOW mit eigenem Pullup.; Pin 33: AGND -- analoge Masse, nicht als Rueckleiter fuer Lasten.; Pin 35: ADC_VREF -- analoge Referenzspannung, kein Digitalanschluss.; Pin 37: 3V3_EN -- schaltet den Pico-Regler ab; ein Ausschalter fuer den ganzen Stapel, den jedes Modul versehentlich ziehen koennte.; Pin 40: VBUS -- liegt nur an, wenn am Pico ein USB-Kabel steckt.

## Baenke und Slot-Matrix

| Bank | Signal 1 | Signal 2 | Signal 3 | Signal 4 |
|---|---|---|---|---|
| A | GP8 | GP9 | GP10 | GP11 |
| B | GP12 | GP13 | GP14 | GP15 |
| C | GP16 | GP17 | GP18 | GP19 |
| D | GP20 | GP21 | GP22 | GP7 |
| ADC | GP26 | GP27 | GP28 |  |

Ein Modul belegt genau eine Bank; die Wahl trifft eine 0603-Matrix (0 Ohm, C21189) mit den Referenzen J<Bank><Signal>, genau ein Platz je Signal bestueckt. Vorgabe ab Werk: Dimmer = B, Motor = A; ADC: Motor = GP26.

## Versorgung

| Zusage | Wert |
|---|---|
| eingang_v | (6.0, 30.0) |
| regler | TPS5430DDAR |
| regler_eingang_v | (5.5, 36.0) |
| regler_abs_max_v | 40.0 |
| ausgang_v | 4.92 |
| schutz_fet | AOD409 |
| schutz_drain_an | PWR_IN |
| gate_klemmung | Zener 12 V Gate-Source |
| vsys_diode | True |
| usb_parallel | True |
| tvs | SMCJ30A |

| Strombudget | Wert |
|---|---|
| modul_gesamt_a | 4.0 |
| stamm_netze | ('/PWR_IN', '/VIN') |
| stapel_durchleitung_a | 3.0 |
| kanal_a | 3.0 |
| motor_a | 2.538 |
| q90_rdson_ohm | 0.04 |
| q90_verlust_max_w | 1.5 |
| klemme_a | 10.0 |

## Layoutregeln

* **R1** Klemmen kantenbuendig an der unteren Kante, Oeffnung nach aussen; kein Klemmen-Hof schneidet PICO_SCHATTEN. *(Hardware design with RP2040 (Raspberry Pi): Bauteile unter dem Pico niedriger als der Steckabstand; eine Klemme braucht Schraubendreher-Zugriff von oben.)*
* **R2** Alle Lastklemmen eines Moduls in EINER Reihe in Kanalreihenfolge von links, Einspeisung ganz rechts, vollstaendig in KLEMMENZONE. *(Pimoroni Automation HAT, Adafruit 5095, Kitronik 5331.)*
* **R3** Bauteilhoehe unter dem Pico <= 8,0 mm, sonst <= 9,5 mm. *(Buchsenhoehe 8,5 mm; STAPEL_ABSTAND-Rechnung oben.)*
* **R4** Luft-/Kriechstrecke zwischen Klemmenkontakten >= 0,8 mm. *(IEC 60664, 0,8 mm bei 50 V.)*
* **R5** Kupfer mindestens 0,5 mm von der Platinenkante. *(JLCPCB-Designregel 0,3 mm plus Reserve.)*
* **R6** Jedes Bauteil traegt seine Referenz sichtbar auf F.Silkscreen. *(Konvention (Audit v2 W1).)*
* **R7** Jede Klemme, jeder Stecker und jede Matrix-Spalte traegt ihre Funktion im Siebdruck. *(Adafruit 5095 / DFRobot 2591: Pinnamen an jeder Klemme.)*
* **R9** Modulname, Vertragsversion und Bank-Vorgabe stehen lesbar im Siebdruck. *(Konvention (Audit v2 W7).)*
* **P1** Abblockkondensator <= 5 mm vom Versorgungspin seines IC, gleiche Lage. *(TI SLVA959B 5.3.1 (< 0,5 cm).)*
* **P2** Schaltregler: Spule, Freilaufdiode und Eingangs-Keramik <= 6 mm vom IC (kleinste Schleife). *(TI SLVS632L Layout-Beispiel; SLVA959B 6.3.2.)*
* **P3** Schalter (FET/Treiber) <= 15 mm von seiner Lastklemme. *(Adafruit/SparkFun 10-12 mm (Konvention).)*
* **P4** Gate-Widerstand <= 5 mm vom Gate. *(Adafruit 2,5 mm, SparkFun 3,8 mm (Konvention).)*
* **P5** Keine Schaltregler-Teile und kein Kupfer in ANTENNE_FREI. *(Pico-Datenblatt 2.2.1.)*

## Auflagen

* Jede Platine traegt neben Pin 1 der unteren Stapelreihe eine Kennzeichnung im Bestueckungsdruck (Dreieck plus "1") und an der Klemmenkante die Marke "UNTEN". Das M3-Lochbild ist punktsymmetrisch; ein verdreht angeschraubtes Modul steckt nirgends (VERDREHT_STECKT_NIRGENDS), bleibt also tot statt kaputt -- die Marke macht den Fehler sichtbar.
* ERST stecken, DANN auf die Abstandsbolzen schrauben.

## Modultypen

| Code | Name | Familie | Kanaele | Signale | ADC |
|---|---|---|---|---|---|
| 0x01 | Motor | Motor | 1 | 4 | ja |
| 0x10 | Dimmer1 | Dimmer | 1 | 1 | nein |
| 0x11 | Dimmer3 | Dimmer | 3 | 3 | nein |
| 0x12 | Dimmer4 | Dimmer | 4 | 4 | nein |

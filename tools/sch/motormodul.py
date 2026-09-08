"""Das Motormodul: erstes echte Modul des Stapels -- Modulsockel + Endstufe.

Die Endstufe (DRV8876 samt Beschaltung) stammt aus dem Muttern-Board v2
(`~/Dokumente/Espace_des_Inventions/PecheAuxCanards`, Commit `39d871d`,
Datei `hardware/kicad/Unmögliche_Muttern.kicad_sch`) -- Bauteilwerte und
Verschaltung von dort tatsaechlich aus der exportierten Netzliste gelesen
(`kicad-cli sch export netlist`), nicht neu erfunden. Was NICHT
uebernommen wird: der dortige Pico (U3), der lokale 5-V-Regler (U13) samt
seinen Kondensatoren (C7/C8) und die Original-Klemme J1 -- Begruendung
bei PWR24V unten.

**Der eine Unterschied zum Altprojekt:** dort hingen IN1/IN2/NSLEEP/
NFAULT/IPROPI und die Notaus-Eingaenge direkt am Pico. Hier haengen sie
am Modul-MCU (U100 aus modulsockel.py); der Pico spricht nur noch per
I2C mit U100. Die Netznamen dafuer liefert modulsockel.NETZE_NACH_AUSSEN
-- diese Datei schliesst genau die Seite, die modulsockel.py als
"isolierte Uebergabenetze" offen liess (s. tests/test_modulsockel.py,
ERWARTETE_ERC_WARNUNGEN).

## Die vier Punkte, die der Auftrag ausdruecklich verlangt

**1. Stromgrenze (R5) bewusst gerechnet, nicht uebernommen.** Formel aus
dem TI-Datenblatt DRV8876 (Dok. SLVSDS7B, AUGUST 2019 - REVISED NOVEMBER
2019), Abschnitt 7.3.3.2 "Current Regulation", Gleichung 3:

    ITRIP (A) x AIPROPI (uA/A) = VVREF (V) / RIPROPI (Ohm)

AIPROPI = 1000 uA/A (Abschnitt 6.5 "Electrical Characteristics", Zeile
"CURRENT SENSE AND REGULATION (IPROPI, VREF)", "AIPROPI ... 1000 uA/A").
VREF haengt wie im Altprojekt direkt an der 3,3-V-Schiene (VVREF = 3,3 V;
das liegt innerhalb des laut Abschnitt 6.3 "Recommended Operating
Conditions" zulaessigen Bereichs 0-3,6 V fuer VVREF).

Der Motor dieses Projekts ist laut Projekthistorie (Muttern-Board-
Betriebsbericht, `PecheAuxCanards/README.md`, Abschnitt "Fehler 2":
"der Motor ist ein 2-A-Typ") ein 2-A-Typ. Auf dem Muttern-Board sass
R5 = 2,2 kOhm -- das ergibt (nachgerechnet mit derselben Gleichung):

    ITRIP = VVREF / (RIPROPI x AIPROPI) = 3,3 / (2200 x 0,001) = 1,5 A

deutlich UNTER den 2 A, die der Motor braucht -- exakt der in
hardware/muttern-board-drv8876-stromlimit.md dokumentierte Fehler ("2A-
Motor kriegt nie Nennstrom"). Fuer das Motormodul wird die Schwelle
deshalb bewusst auf einen Wert UEBER dem Nennstrom gelegt, mit Marge fuer
Anlauf-/Lastspitzen, aber weit unter der festen Hardware-Notbremse IOCP
(3,5-5,5 A laut Abschnitt 6.5, "Overcurrent protection trip point") --
die einstellbare Stromregelung soll im Normalbetrieb greifen, IOCP bleibt
der letzte Schutz, nicht der erste:

    RIPROPI = VVREF / (ITRIP_ziel x AIPROPI), ITRIP_ziel = 2,5 A (2 A + 25 %)
    RIPROPI = 3,3 / (2,5 x 0,001) = 1320 Ohm

Naechster E24-Normwert: **1,3 kOhm** (R5, bestueckt). Nachgerechnet:

    ITRIP = 3,3 / (1300 x 0,001) = 2,538 A  (~27 % Marge ueber 2 A,
                                              weit unter IOCP-min 3,5 A)

**Derselbe Widerstand setzt die Skala der Strommessung.** Aus Gleichung 1
(Abschnitt 7.3.3.1 "Current Sensing"): IPROPI(uA) = ILOAD(A) x AIPROPI.
Aus Gleichung 2: VIPROPI(V) = IPROPI(A) x RIPROPI(Ohm). Bei den vollen
2 A Nennstrom: IPROPI = 2 x 1000 = 2000 uA = 2 mA; VIPROPI = 2 mA x
1300 Ohm = 2,6 V -- 79 % des 3,3-V-ADC-Bereichs des Modul-MCU, guter
Ausschlag ohne Uebersteuerung. Am ITRIP-Punkt selbst (2,538 A) klemmt
VIPROPI laut Datenblatt exakt auf VVREF = 3,3 V (interne IPROPI-Klemme
"with respect to VVREF") -- die Rechnung ist in sich konsistent.

R10 bleibt wie im Altprojekt eine zweite, NICHT bestueckte
IPROPI/GND-Alternative (`dnp=True`) -- der Wert (4,7 kOhm) wird
unveraendert uebernommen, weil das Bauteil ohnehin nicht bestueckt wird
und die Aufgabe nur R5 als "bewusst zu rechnen" nennt.

**2. 3,3-V-Haushalt des Stapels.** Ergebnis und Rechnung stehen in
`hardware/bauteile-1b.md`, Beleg 8 -- hier nur die Kurzfassung: die
Quelle ist der interne Regler des Pico (3V3_OUT, Pin 36), fuer den das
Pico-Datenblatt empfiehlt, die externe Last unter 300 mA zu halten. Der
Modul-MCU zieht laut STM32C011-Datenblatt (DS13866, Tabelle 27) maximal
3,90 mA (25 C) bzw. 4,90 mA (125 C) -- zehn Module bleiben damit weit
unter 50 mA, ein Bruchteil des Budgets. NEU gegenueber der Etappe-1a-
Abschaetzung: dieses Modul haengt zusaetzlich VREF (U1 Pin 5) an die
3,3-V-Schiene -- das DRV8876-Datenblatt nennt dafuer keinen eigenen
Ruhestromwert (VREF ist ein hochohmiger Komparator-Referenzeingang, kein
Lastausgang), die Grössenordnung liegt laut allgemeiner Komparator-
Eingangs-Praxis im Nanoampere- bis niedrigen Mikroampere-Bereich -- nicht
einzeln aus einem gelesenen Datenblattwert belegt, aber um Groessenord-
nungen kleiner als der MCU-Anteil und aendert die Budget-Aussage nicht.

**3. Polarisierte Bauteile.** Zwei polarisierte Kondensatoren in dieser
Datei: C12 (220 uF, Device:C_Polarized) und implizit keiner sonst (C9/
C10/C11/C13 sind unpolarisierte Keramik-Kondensatoren, Device:C). Fuer
C12 gilt exakt dieselbe Pruefung wie fuer C3 auf der Sockelplatine
(hardware/bauteile-1b.md, Beleg 7-Umfeld: der Fehler auf dem
Muttern-Print lag darin, dass der "+"-Aufdruck auf GND landete):
Device:C_Polarized Pin 1 ist wortwoertlich mit "+" beschriftet (eigene
Pruefung der KiCad-Quelle, Device.kicad_sym) -- hier an Pin 1 liegt
"+24V", NIE GND. tests/test_motormodul.py sichert das explizit ab. Die
Layout-Auflage (Footprint-Silk-Polaritaet gegen den Schaltplan pruefen,
bevor bestueckt wird) steht in hardware/bauteile-1b.md, Beleg 9.

**4. NOTAUS wirkt ohne Software.** Der Weg, den das Signal nimmt, steht
unten bei `_notaus_schleifen()` und `_notaus_verriegelung()` im Detail;
hier die Kurzfassung: die Endstufe wird ueber das DRV8876-eigene
nSLEEP-Pin abgeschaltet (ein echter Hardware-Steuereingang des Treibers,
kein Software-Zustand). Die Verriegelung ist ein UND-Gatter (U3,
SN74LVC1G08):

    U1_NSLEEP = NSLEEP(vom Modul-MCU)  UND  NOTAUS(Sammelleitung)

Sinkt NOTAUS -- von IRGENDEINEM Modul im Stapel heruntergezogen --, geht
der Gatterausgang auf VOL und legt den Treiber schlafen, unabhaengig
davon, was der eigene MCU auf seinem NSLEEP-Pin treibt oder ob er
ueberhaupt noch laeuft. Der MCU behaelt die volle Kontrolle in die
andere Richtung (MCU LOW -> Ausgang LOW), verliert sie aber
vollstaendig, sobald NOTAUS gezogen wird.

**Diese Fassung ersetzt eine Diodenklemme (D2 + R14), die NICHT wirkte**
-- vollstaendige Fehleranalyse in `_notaus_verriegelung()` unten und in
`.superpowers/sdd/2026-08-31-etappe-1b-sockel-und-motormodul/
aufgabe-5-fix1-report.md`. Kurz: eine Diode von NSLEEP nach NOTAUS bildet
zusammen mit dem MCU-Vorwiderstand einen Spannungsteiler und laesst den
Pin bei rund 3,0 V stehen (VIL waere 0,8 V); und selbst ohne
Vorwiderstand hoben ZWEI Diodenspannungen in Reihe (D2 zum Bus, D3/D4
vom Bus zum Schaltkontakt) den Pin auf rund 1,2 V. Ein Gatter hat dieses
Problem nicht: sein Ausgang ist eine echte Gegentaktstufe.

**5. Der Notaus-EINGANG arbeitet im Ruhestrom (Aufgabe 5d, 2026-08-31).**
Der externe Kontakt ist jetzt ein OEFFNER: im Normalbetrieb geschlossen,
Oeffnen loest aus -- und ebenso jeder Kabelbruch, jeder abgezogene
Stecker, jede lose Klemme. Vorher war es ein Schliesser ("zumachen =
Notaus"), bei dem ein gebrochenes Kabel wie "alles in Ordnung" aussah.
Vollstaendige Herleitung, alle fuenf geforderten Betrachtungen
(Schleifenspannung, Kurzschluss der Rueckleitung, Querschluss der
Kanaele, Strombegrenzung, unbenutzter Kanal) und die Rechnungen dazu
stehen in `_notaus_schleifen()`. Die drei Kernpunkte:

  * Je Kanal gehen 24 V ueber 3,3 kOhm hinaus und kommen ueber eine
    zweite Ader und einen weiteren 3,3 kOhm in die LED eines
    Optokopplers zurueck; dessen Emitter treibt gegen einen 4,7-kOhm-
    Pulldown den Knoten SCHLEIFE_1/2. Geschlossen = HIGH, offen = LOW.
  * Der Knoten kann den wired-OR-Bus NICHT selbst ziehen -- ein Pulldown
    gegen zehn parallele 10-kOhm-Pullups steht bei 2,7 V. Deshalb sitzt
    zwischen Knoten und Bus ein nichtinvertierender Puffer mit
    Open-Drain-Ausgang (U6/U7, SN74LVC1G07). Die bisherigen Koppeldioden
    D3/D4 entfallen dabei ersatzlos.
  * J3 bleibt vierpolig (zwei Adern je Kanal statt Signal+GND). **Ein
    unbenutzter Kanal muss am Stecker gebrueckt werden**, sonst meldet er
    dauerhaft Notaus; und die bestehende Verkabelung des
    Peche-aux-Canards-Exponats muss beim Umstieg umgeklemmt werden.

**6. Zwei geerbte Fehler behoben, und beide als KLASSE geschlossen
(Aufgabe 5f, 2026-08-31).** Der Muttern-Print brachte zwei Fehler mit,
die beim Uebernehmen der Endstufe niemand nachgerechnet hat. Beide sind
behoben; wichtiger ist, dass tests/test_motormodul.py sie jetzt als
GATTUNG prueft, nicht als Einzelfall:

  * **R6 (Vorwiderstand des Sensor-Optokopplers) verheizte 0,24 W in
    einem 0805.** Nachgerechnet (24 V - 1,2 V VF)^2 / 2,2 kOhm = 0,236 W
    gegen 0,125 W Belastbarkeit -- Faktor 1,9 dauerhaft ueber Grenzwert.
    Die Antwort ist nicht ein groesseres Gehaeuse, sondern **der ganze
    Sensoreingang entfaellt** (J2, R6, U2): er war im Altprojekt
    unbenutzt ("Die Eingaenge des Boards (GPIO16 Sensor via PC817 ...)
    sind in diesem Projekt unbenutzt -- es sind keine Sensoren
    angeschlossen oder geplant", dortiges README.md), und das
    Design-Dokument nennt fuer den Modultyp Motor ausdruecklich nur
    "DRV8876, ein Motor, Strommessung, Notaus-Eingaenge"
    (docs/superpowers/specs/2026-08-28-picostack-design.md). Ein Bauteil,
    das nichts tut, aber ueberlastet ist, wird weggelassen und nicht
    vergroessert. Was frei wird: PC14 (U100 Pin 2) ist wieder ein freier
    GPIO, die 3-polige Klemme J2 entfaellt, und mit ihr der einzige
    Punkt, an dem 24 V ungeschuetzt Richtung Optokoppler gingen.
  * **Der Optokoppler-Footprint passte nicht zum Bauteil.**
    `Package_SO:SOP-4_3.8x4.1mm_P2.54mm` hat seine Padreihen 5,5 mm
    auseinander; der beschaffte PC817X1CSP9F ist die SMT-Gullwing-Form
    mit 10,0 mm Anschlussspanne, deren Fuesse erst bei ~4,0 mm vom
    Bauteilmittelpunkt beginnen -- die Pads lagen also VOLLSTAENDIG
    NEBEN den Anschluessen. Jetzt liegt der Footprint als eigene
    Bibliothek im Projekt (`FP_PC817` unten) und ist Pad fuer Pad aus
    dem Sharp-Datenblatt gezeichnet.
  * **Dabei aufgefallen (dritter Fall derselben Gattung): Q1 gab es in
    seinem Footprint gar nicht.** Der Schaltplan trug "IRF4905" im
    TO-252-Footprint. Den IRF4905 gibt es bei Infineon/IR nur als
    TO-220AB (IRF4905PbF, LCSC C2564) und als D2Pak/TO-263 (IRF4905S,
    LCSC C5337969) -- **kein TO-252**. Bestueckt haette JLCPCB entweder
    ein anderes Bauteil oder gar nichts. Ersetzt durch den
    Schwestertyp derselben HEXFET-Familie, den es genau in dieser
    Bauform gibt: **IRFR5305PbF, D-Pak (TO-252AA)**, s. Q1 unten.

Beide Pruefungen in tests/test_motormodul.py decken die Klasse ab:
jede Bauform bringt ihre Belastbarkeit als benannte Groesse mit Herkunft
mit, jedes Bauteil braucht einen belegten Gehaeuseeintrag. Ein neues
Bauteil ohne Beleg faellt durch, nicht erst das naechste Exemplar
desselben Fehlers.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S    # noqa: E402
import modulsockel         # noqa: E402
import versorgung           # noqa: E402  (ersetzt den alten Q1-Strang, s. unten)

# -------------------------------------------------------------- Footprints
FP_R0805 = modulsockel.FP_R0805
FP_C0805 = modulsockel.FP_C0805
FP_HDR_1X04 = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
# FP_CP_RADIAL/FP_TVS_SMC/FP_TO252 (Q1/D1/C12) sind mit dem alten
# Verpolschutz-Strang ENTFALLEN -- die gleichnamigen Bauteile Q90/D90/
# C90 leben jetzt in tools/sch/versorgung.py, s. Kommentar vor
# `_stapel_speist_lokal()` unten.
FP_SOD123 = "Diode_SMD:D_SOD-123"                                 # BAT54W (D3/D4)
# Optokoppler U4/U5 (PC817 in SMT-Gullwing-Form). **Nicht** mehr
# `Package_SO:SOP-4_3.8x4.1mm_P2.54mm` -- der Platzhalter aus dem
# Altprojekt (Aufgabe 5f, s. Moduldoku Punkt 6). Dessen Padreihen liegen
# 5,5 mm auseinander (Pads bei +-2,75 mm, je 1,45 mm lang, also von 2,03
# bis 3,48 mm vom Mittelpunkt); der Anschlussfuss des PC817 beginnt erst
# bei rund 4,0 mm und endet bei 5,0 mm -- die Pads lagen VOLLSTAENDIG
# neben den Anschluessen, das Bauteil haette auf blankem Loetstopplack
# gesessen.
#
# Der neue Footprint ist Pad fuer Pad die vom Hersteller empfohlene
# Landflaeche: SHARP "PC817X Series", Sheet No. **D2-A03101EN, Date
# Sep. 30. 2003**, Abschnitt "Design Considerations" -> "Recommended
# Foot Print (reference)", Zeile "SMT Gullwing Lead-form": Reihenabstand
# **8,2 mm** (Pad-Mitte zu Pad-Mitte), Pad **2,2 mm x 1,7 mm**, Raster
# **2,54 mm**. Gegengeprueft an der Landflaeche, die LCSC/EasyEDA selbst
# fuer C97308 fuehrt (Paketname `OPTO-SMD-4_L4.6-W6.5-P2.54-LS10.3-TL`,
# Pads +-4,3 mm, 2,5 x 1,5 mm): 0,4 mm Unterschied im Reihenabstand,
# dieselbe Bauform, dieselbe Anschlussspanne (LS10.3 == 10,0 mm +0/-0,5
# aus "Outline Dimensions", Zeichnung 2 "SMT Gullwing Lead-Form").
# Gezeichnet wird die Herstellerempfehlung.
FP_PC817 = "Optocoupler_PC817:PC817_SMT_Gullwing"
FP_SOT353 = modulsockel.FP_SOT353                                 # U3/U6/U7 (SOT-353), wie U103
# 1206 statt 0805 NUR fuer die vier Schleifenwiderstaende R16..R19: sie
# liegen als einzige Bauteile dieser Platine dauerhaft an 24 V und
# muessen einen aeusseren Dauerkurzschluss aushalten -- Rechnung in
# `_notaus_schleifen()`, Punkt 4. Belegt an einem echten Bauteil:
# UNI-ROYAL 1206W4F3301T5E, 3,3 kOhm +-1 %, **250 mW**, 200 V max.
# Arbeitsspannung, LCSC C26032 -- Produktseite tatsaechlich gesichtet
# (`lcsc.com/product-detail/Chip-Resistor-Surface-Mount_Uniroyal-Elec-
# 1206W4F3301T5E_C26032.html`, Rohdaten: Gehaeuse "1206", "3.3kOhm",
# Toleranz "+-1%", Leistung "250mW", "200V", Bestand 164 200).
FP_R1206 = "Resistor_SMD:R_1206_3216Metric"
# DRV8876: der reparierte Footprint aus dem Altprojekt (Waermepad MIT
# Masken-/Pastenoeffnung, segmentiertes Pastenmuster, 12 Waermevias mit
# echtem Restring auf Pad 17) -- Aufgabenbrief Schritt 2. Uebernommen nach
# hardware/kicad/components/footprints/DRV8876PWPR.pretty/, eigene
# Pruefung: grep -c '(pad 17 thru_hole circle' liefert 12.
FP_DRV8876 = "DRV8876PWPR:IC_DRV8876PWPR"
# Terminalbloecke: dieselbe Bauteilfamilie/Simplification wie
# sockelplatine.py -- Symbol "Connector:Screw_Terminal_01xNN" (KiCad-
# Standardbibliothek), Footprint ein genormter 5,08-mm-Terminalblock-
# Platzhalter, bis die PCB-Layout-Aufgabe (7) einen eigenen DB128L-
# Footprint zeichnet. J5 (Motor, 2-polig) nutzt denselben Footprint-
# Platzhalter wie sockelplatine.FP_KLEMME_2 (beide DB128L-5.08-2P-GN-S,
# LCSC C395868, hardware/bauteile-1b.md). Der 3-polige Bruder
# (DB128L-5.08-3P-GN-S, LCSC C395869) wird von diesem Modul seit
# Aufgabe 5f nicht mehr gebraucht -- er trug die Sensorklemme J2, die
# mit dem Sensoreingang entfallen ist (Moduldoku Punkt 6).
FP_KLEMME_2 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal"

# ------------------------------------------------------- Bauteilwerte
# Aus dem Altprojekt uebernommen (Netzliste `kicad-cli sch export
# netlist` gegen Unmögliche_Muttern.kicad_sch tatsaechlich gelesen, nicht
# aus dem Gedaechtnis): C9/C10/C11/C13/R6/R7/R8/R9/R10/R13. (D1/C12/R11/
# R12 sind mit dem alten Verpolschutz-Strang entfallen -- s. Kommentar
# vor `_stapel_speist_lokal()` unten; die gleichnamigen Bauteile
# Q90/D90/C90/R90/R91 leben jetzt in tools/sch/versorgung.py.)
C9_WERT = "0.1u"         # VCP-Kondensator (VM<->VCP, DRV8876-Ladungspumpe)
C10_WERT = "0.022u"      # Ladungspumpen-Kondensator CPH<->CPL
C11_WERT = "0.1u"        # zweiter 24-V-Abblock-Kondensator (neben C9-Anteil)
C13_WERT = "0.1u"        # IPROPI-Filterkondensator gegen GND
# R6 (2,2k, Vorwiderstand des Sensor-Optokopplers U2) ist ENTFALLEN --
# mit dem ganzen Sensoreingang, s. Moduldoku Punkt 6. Die Zahlen bleiben
# als benannte Groessen stehen, damit die Leistungspruefung in
# tests/test_motormodul.py zeigen kann, WARUM: der Wert ist die
# Gegenprobe, nicht mehr ein bestuecktes Bauteil.
ALT_R6_OHM = 2200.0      # war 0805 an 24 V -> 0,236 W bei 0,125 W Belastbarkeit
R7_WERT = "0.1k"         # Vorwiderstand MCU -> U1 EN/IN1
R8_WERT = "0.1k"         # Vorwiderstand MCU -> U1 PH/IN2
R9_WERT = "0.1k"         # Vorwiderstand MCU -> U1 NSLEEP
R10_WERT = "4.7k"        # IPROPI/GND, NICHT bestueckt (dnp=True), unveraendert
# R11_WERT/R12_WERT (Q1-Gate-Teiler) sind entfallen -- die
# Nachfolgewerte (R90/R91, dieselben 10k/10k) stehen in versorgung.py.
R13_WERT = "10k"         # NFAULT-Pullup an 3V3
# R5 NEU gerechnet fuer diese Aufgabe (s. Moduldoku oben, Punkt 1) --
# NICHT der Altprojekt-Wert (2,2k, dort zu klein fuer den 2-A-Motor).
R5_WERT = "1.3k"         # ITRIP ~= 2,538 A bei VVREF=3,3V, AIPROPI=1000uA/A

# ---------------------------------------------- NOTAUS-Verriegelung
# Kein Gegenstueck im Altprojekt -- dort sass der Pico selbst auf den
# Notaus-Eingaengen, ein Verriegelungspfad ohne MCU war dort nicht
# gefordert.
#
# D3/D4 (Schottky-Koppeldioden von den lokalen Schaltkontakten auf die
# Sammelleitung) sind ENTFALLEN -- Begruendung in `_notaus_schleifen()`:
# der Eingang arbeitet seit dieser Aufgabe nach dem Ruhestromprinzip, und
# ein passiver Pulldown kann einen wired-OR-Bus nicht herunterziehen. Die
# Zahlen des BAT54W bleiben als benannte Konstanten stehen, weil die
# Gegenproben in tests/test_motormodul.py mit ihnen rechnen (und weil ein
# kuenftiges Fremdmodul den Bus weiterhin ueber eine Schottky-Diode
# ziehen darf -- die Pegelrechnung fuer den Gattereingang B bleibt
# dadurch unveraendert gueltig).
D_KOPPEL_WERT = "BAT54W"
R15_WERT = "10k"         # Pullup NOTAUS-Sammelleitung an 3V3, s. dort
C14_WERT = "0.1u"        # Abblockkondensator U3 (Verriegelungsgatter)

# ---------------------------------------------- Gatter-Abblockung (Task 6b)
# Dieselbe Luecke, die Task 6 fuer das Dimmermodul geschlossen hat
# (dort: tools/sch/dimmermodul.py::_gatter_abblockung(), C102/C103/
# C104), besteht hier unveraendert: modulsockel.einbauen() deckt mit
# C100 nur U100 (MCU) ab, C101 ist Teil des NCLR-Loeschglieds -- keines
# von beiden blockt U101 (SN74LVC1G175)/U102 (SN74LVC2G00DCUR)/U103
# (SN74LVC1G08) ab. Diese drei ICs sind dem Modulsockel-Block
# gemeinsam (`modulsockel.einbauen(mit_flipflop=True)`), NICHT dem
# Motormodul selbst -- sie sind etwas anderes als U3/U6/U7 (die
# EIGENEN Gatter dieses Moduls, s. Moduldoku Punkt 4/5), die bereits
# ihre eigenen Kondensatoren C14/C15/C16 haben (jeweils direkt beim
# `sch.bauteil(...)`-Aufruf kommentiert). Referenzen C17/C18/C19 --
# naechste freie Nummern NACH C16 (dem letzten hier vergebenen Ref);
# C102/C103/C104 (Dimmermodul) liegen im Referenzraum EINES ANDEREN,
# eigenstaendigen Schaltplans (Dimmer%d.kicad_sch) und koennen mit
# diesen Nummern hier nicht kollidieren.
C_SOCKEL_ABBLOCK_WERT = "100n"   # C17/C18/C19 (U101/U102/U103)
C_SOCKEL_ABBLOCK_LCSC = "C49678"   # 100nF/0805, JLCPCB-Basic-Teil
                                   # (identisch mit dimmermodul.
                                   # C_ABBLOCK_LCSC/-_WERT)

# ------------------------------ Ruhestrom-Notauseingang (Aufgabe 5d, neu)
# Werte: Herleitung vollstaendig in `_notaus_schleifen()`.
R_SCHLEIFE_WERT = "3.3k"   # R16..R19, je zwei in Reihe pro Kanal, 1206
R_PULLDOWN_WERT = "4.7k"   # R20/R21, Pulldown am rueckkehrenden Knoten
C_INV_WERT = "0.1u"        # C15/C16, Abblockkondensatoren U6/U7
OPTO_WERT = "PC817"        # U4/U5, dasselbe Bauteil wie U2 (Sensoreingang)
INVERTER_WERT = "SN74LVC1G07"   # U6/U7, nichtinvertierender Puffer, Open-Drain-Ausgang
# ERSETZT 2026-09-08, Grund: die vorherige Fassung setzte hier den
# Typkurzform-Vorgaenger "1G06" ein (volle Bezeichnung im Commit-
# Verlauf dieser Aenderung) -- ein INVERTIERENDES Gatter ("Single NOT
# Gate, Open Drain", TI SCES296AG-Vorgaenger SCES295AB) -- waehrend
# saemtliche Doku- und Pegelrechnung in dieser Datei (s.
# `_notaus_schleifen()`) von
# NICHTinvertierendem Verhalten ausgeht ("Schleife in Ordnung -> Eingang
# HIGH -> Ausgang hochohmig"). Mit dem tatsaechlich verbauten 1G06 waere
# das Board fail-UNSAFE gewesen: intakte Schleife (SCHLEIFE HIGH) haette
# NOTAUS gezogen (Y = NOT(HIGH) = LOW -> OD-Transistor an -> Bus tief),
# ein Drahtbruch (SCHLEIFE LOW) haette NOTAUS dagegen FREIGEGEBEN
# (Y = NOT(LOW) = HIGH -> OD-Transistor aus -> Bus floatet, R15 zieht
# hoch) -- genau die gefaehrliche Richtung: der Fehlerfall, den die ganze
# Ruhestromschleife eigentlich abfangen soll, waere unbemerkt geblieben.
# 1G07 ("Single Buffer/Driver With Open-Drain Output", TI SCES296AG,
# selbst gelesen) ist NICHTinvertierend und PINIDENTISCH (DCK/SOT-353:
# 1=NC, 2=A, 3=GND, 4=Y open_collector, 5=VCC -- eigene Pruefung beider
# Symbole in 74xGxx.kicad_sym) -- ein reiner Bauteiltausch ohne
# Pin-Umverdrahtung. LCSC C7830 (zwischen C7828/1G06 und C7832/1G08,
# derselben LCSC-Nummernfolge wie die beiden Nachbartypen).

# ------------------------------------- benannte Groessen der Verriegelung
# Diese Werte sind die Rechengrundlage der Pegelpruefung in
# tests/test_motormodul.py -- sie stehen hier und nicht nur im Fliesstext,
# damit die Zusicherung die Rechnung tatsaechlich nachvollzieht statt nur
# die Anwesenheit von Bauteilen zu bestaetigen.
V_3V3 = 3.3                     # Schienenspannung des Stapels

# DRV8876, Dok. SLVSDS7B (AUGUST 2019 - REVISED NOVEMBER 2019),
# Abschnitt 6.5 "Electrical Characteristics", Block "LOGIC-LEVEL INPUTS
# (EN/IN1, PH/IN2, nSLEEP)". VVM ist hier 24 V, also gilt die Zeile
# "VVM >= 5 V".
DRV_VIL_MAX = 0.8               # V, MAX
DRV_VIH_MIN = 1.5               # V, MIN
DRV_RPD = 100e3                 # Ohm, "RPD Input pulldown resistance ... 100 kOhm"
DRV_IIH_MAX = 75e-6             # A bei VI = 5 V ("IIH Input logic high current")

# SN74LVC1G08 (U3), Dok. SCES217AA (APRIL 1999 - REVISED AUGUST 2026),
# Abschnitt 5.3 "Recommended Operating Conditions" (VIH/VIL, Zeile
# "VCC = 3V to 3.6V") und Abschnitt 5.5 "Electrical Characteristics"
# (VOH/VOL/II).
GATTER_VIL_MAX = 0.8            # V, Abschnitt 5.3
GATTER_VIH_MIN = 2.0            # V, Abschnitt 5.3
GATTER_VOL_MAX = 0.1            # V bei IOL = 100 uA, Abschnitt 5.5
GATTER_VOH_MIN = V_3V3 - 0.15   # V bei IOH = -100 uA ("VCC - 0.15"), Abschnitt 5.5
GATTER_IO_BEZUG = 100e-6        # A -- der Laststrom, fuer den VOL/VOH oben gelten
GATTER_II_MAX = 5e-6            # A, "II ... +-5 uA", Abschnitt 5.5

# BAT54W (ehemals D3/D4), Vishay-Datenblatt Dok. 86408, Rev. 1.0 vom
# 20-Nov-2023, Tabelle "ELECTRICAL CHARACTERISTICS" (Tamb = 25 C): VF MAX
# 240 mV bei 0,1 mA, 320 mV bei 1 mA, 400 mV bei 10 mA; IR MAX 2 uA bei
# VR = 25 V.
SCHOTTKY_VF_MAX_1MA = 0.32      # V
SCHOTTKY_VF_MAX_10MA = 0.40     # V
SCHOTTKY_IR_MAX = 2e-6          # A bei VR = 25 V

# SN74LVC1G07 (U6/U7), nichtinvertierender Puffer mit Open-Drain-Ausgang,
# TI-Datenblatt Dok. SCES296AG (FEBRUARY 2000 - REVISED OCTOBER 2025,
# per WebFetch selbst gelesen, s. INVERTER_WERT-Kommentar zum Bauteil-
# tausch 1G06->1G07). Abschnitt 5.3 "Recommended Operating Conditions",
# Zeilen "VCC = 3V to 3.6V" bzw. "VCC = 3V": VIH MIN 2 V, VIL MAX 0,8 V,
# IOL MAX 24 mA. Abschnitt 5.5 "Electrical Characteristics": VOL MAX
# 0,1 V bei IOL = 100 uA (VCC 1,65-5,5 V) und VOL MAX 0,4 V bei
# IOL = 16 mA (VCC = 3 V); Ii (A-Eingang, VI = 5,5 V oder GND) MAX
# +-5 uA -- GROESSER als beim vorherigen 1G06 (dort +-1 uA): eigene
# Pruefung der Tabelle, kein blosser Uebertrag. Ioff ("Off-state
# current", VI oder VO = 5,5 V, VCC = 0) MAX +-10 uA; ICC MAX 10 uA.
#
# **Ehrlich vermerkt: KEIN Schmitt-Trigger.** Abschnitt "7.3 Feature
# Description" nennt fuer den 1G07 nur "Wide operating voltage range",
# "Allows down voltage translation" und die Ioff-Funktion -- anders als
# beim ersetzten 1G06 (dort "Schmitt trigger action on all ports")
# fehlt hier ausdruecklich die Hysterese. Die langsamen Flanken des
# PC817 (tr/tf typ. 4/3 us, MAX 18 us, s. OPTO_*-Konstanten unten)
# koennten den Eingang deshalb laenger im undefinierten Bereich
# zwischen VIL und VIH halten als bei einem Schmitt-Trigger-Eingang.
# Sicherheitsrelevant ist das trotzdem NICHT: ein OD-Ausgang kann in
# diesem Zustand hoechstens ZUSAETZLICH kurz auf VOL ziehen (Y=L moeglich,
# nie ein falsches, stabiles Y=Z) -- jedes Wackeln in der Uebergangszone
# kann die Sammelleitung also nur ZUSAETZLICH kurz Richtung NOTAUS
# ziehen, nie sie faelschlich freigeben. Die Ausfallrichtung bleibt
# damit sicher; unguenstigstenfalls loest die Anlage etwas oefter aus,
# nie seltener.
INV_VIL_MAX = 0.8               # V, Abschnitt 5.3
INV_VIH_MIN = 2.0               # V, Abschnitt 5.3
INV_VOL_MAX_100UA = 0.1         # V bei IOL = 100 uA, Abschnitt 5.5
INV_VOL_MAX_16MA = 0.4          # V bei IOL = 16 mA, VCC = 3 V, Abschnitt 5.5
INV_IOL_BEZUG_16MA = 16e-3      # A -- Stuetzpunkt zu INV_VOL_MAX_16MA
INV_IOL_MAX = 24e-3             # A, Abschnitt 5.3, VCC = 3 V
INV_II_MAX = 5e-6               # A, Abschnitt 5.5 (1G07: +-5 uA, NICHT +-1 uA wie 1G06)
INV_IOFF_MAX = 10e-6            # A, Abschnitt 5.5

# PC817 (U4/U5, und dasselbe Bauteil wie U2), SHARP-Datenblatt
# "PC817X Series", Sheet No. D2-A03101EN, Date Sep. 30. 2003.
# "Absolute Maximum Ratings": IF 50 mA, IC 50 mA, P (Diode) 70 mW,
# Ptot 200 mW, Topr -30 bis +100 C.
# "Electro-optical Characteristics" (Ta = 25 C):
#   VF   IF = 20 mA          TYP 1,2 V   MAX 1,4 V
#   ICEO VCE = 50 V, IF = 0              MAX 100 nA
#   IC   IF = 5 mA, VCE = 5 V   MIN 2,5 mA  MAX 30,0 mA   (= CTR 50-600 %)
#   VCE(sat) IF = 20 mA, IC = 1 mA       MAX 0,2 V
# "Model Line-up": Rangmarke A = IC 4,0 bis 8,0 mA bei IF = 5 mA; das
# beschaffte PC817X1CSP9F traegt Rang A. Gerechnet wird trotzdem mit dem
# Familien-Minimum 2,5 mA -- der schlechtere der beiden Werte.
OPTO_VF_TYP = 1.2               # V bei IF = 20 mA
OPTO_VF_MAX = 1.4               # V bei IF = 20 mA
OPTO_IF_ABSMAX = 50e-3          # A
OPTO_IF_BEZUG = 5e-3            # A -- Stuetzpunkt der IC-MIN-Zeile
OPTO_IC_MIN_BEI_5MA = 2.5e-3    # A, MIN bei IF = 5 mA, VCE = 5 V
OPTO_ICEO_MAX = 100e-9          # A
OPTO_VCESAT_MAX = 0.2           # V bei IF = 20 mA, IC = 1 mA

# 24-V-Schiene des Stapels. Kein Datenblattwert: die Anlage wird aus einem
# 24-V-Netzteil gespeist, +-10 % ist die uebliche Auslegungstoleranz einer
# solchen Schiene. Bewusst als Annahme benannt, nicht als Beleg.
V_24V_NOM = 24.0
V_24V_MIN = 21.6                # 24 V - 10 %
V_24V_MAX = 26.4                # 24 V + 10 %

# UNI-ROYAL 1206W4F3301T5E, LCSC C26032 (Produktseite gesichtet, s.
# FP_R1206 oben): 3,3 kOhm, +-1 %, 250 mW, 200 V max. Arbeitsspannung.
R1206_P_NENN = 0.25             # W
R1206_U_MAX = 200.0             # V
R_SCHLEIFE_OHM = 3300.0         # R16..R19 (je Kanal zwei in Reihe)
R_SCHLEIFE_TOL = 0.01           # +-1 %
R_PULLDOWN_OHM = 4700.0         # R20/R21

# Widerstandswerte, die in der Pegelrechnung vorkommen.
R9_OHM = 100.0                  # MCU -> U3 Eingang A (reiner Serienwiderstand)
R15_OHM = 10e3                  # Pullup NOTAUS je Modul
MODULE_IM_STAPEL = 10           # Auslegungsfall aus hardware/bauteile-1b.md, Beleg 8

# Nur fuer die Gegenprobe im Test: so war die Verriegelung zuerst gebaut
# (Diode D2 von NSLEEP auf NOTAUS, davor R14 als Strombegrenzung). Beide
# Bauteile sind ENTFALLEN; die Zahlen bleiben, damit der Test zeigen kann,
# dass genau diese Anordnung die VIL-Schwelle verfehlt.
ALT_R14_OHM = 1000.0
ALT_VF_1N4148 = 0.6             # V, gaengiger Arbeitspunkt einer Si-Diode


# ===================================================================
#  Aufgabe 5f, Klasse 1: Belastbarkeit der Bauformen
# ===================================================================
# Diese Tabelle ist die Rechengrundlage der Leistungspruefung in
# tests/test_motormodul.py. Sie steht hier und nicht im Test, damit
# Schaltplan und Pruefung DIESELBEN Zahlen benutzen -- und sie nennt zu
# jeder Zahl das Bauteil, an dem sie gemessen wurde. Eine Bauform ohne
# Eintrag laesst die Pruefung durchfallen; niemand kann einen
# Widerstand in ein unbelegtes Gehaeuse setzen.
#
# 0805: UNI-ROYAL 0805W8F1002T5E, 10 kOhm +-1 %, LCSC **C17414**
#   (`lcsc.com/product-detail/Chip-Resistor-Surface-Mount_Uniroyal-Elec-
#   0805W8F1002T5E_C17414.html`, Produktseite gesichtet -- Rohdaten:
#   Gehaeuse "0805", "10kOhm", Toleranz "+-1%", Leistung "**125mW**",
#   max. Arbeitsspannung "150V", TK "+-100ppm/C", Bestand 21 700 400).
#   Dieselbe Baureihe (0805W8F...) liefert alle 0805-Werte dieser
#   Platine; die 125 mW gelten fuer die Baureihe, nicht nur fuer den
#   10-kOhm-Wert.
# 1206: UNI-ROYAL 1206W4F3301T5E, LCSC C26032 (s. FP_R1206 oben).
#
# **Was die Zahl NICHT sagt:** 125 mW/250 mW sind die Nennwerte bis
# 70 C Umgebungstemperatur; darueber muessen sie derated werden. Die
# Pruefung rechnet ohne Derating -- sie ist damit die notwendige, nicht
# die hinreichende Bedingung.
P_NENN_JE_BAUFORM = {
    FP_R0805: 0.125,
    FP_R1206: 0.25,
}
U_MAX_JE_BAUFORM = {
    FP_R0805: 150.0,
    FP_R1206: 200.0,
}
#: Ab dieser Spannung an einem Widerstand verlangt der Auftrag die
#: Leistungsrechnung. Die Pruefung rechnet trotzdem fuer JEDEN
#: Widerstand -- die Grenze entscheidet nur, welche Faelle im
#: Testprotokoll namentlich auftauchen.
HOCHVOLT_GRENZE = 5.0
#: Toleranz der verwendeten Widerstandsbaureihen (beide +-1 %, s.
#: Produktseiten oben). Fuer die Verlustleistung zaehlt der KLEINSTE
#: Widerstand, weil P = U^2/R.
R_TOLERANZ = 0.01

# Wieviel Spannung kann ueberhaupt an einem Netz stehen? Die Pruefung
# leitet das aus dem Schaltplan her (Fixpunkt ueber die leitenden
# Bauteile); nur diese Startwerte sind gesetzt. Herkunft:
#   GND/3V3  -- Vertragsschienen (docs/vertrag.md)
#   PWR24V   -- Stapelschiene, +-10 % (Annahme, s. V_24V_MIN/MAX oben)
#   +24V     -- dieselbe Schiene hinter Q1; ein durchgesteuerter
#               P-MOSFET mit 65 mOhm faellt bei 2,5 A um 0,16 V ab,
#               das liegt innerhalb der 10-%-Toleranz und wird
#               deshalb nicht getrennt gefuehrt.
NETZ_SPANNUNG_FEST = {
    "GND": (0.0, 0.0),
    "3V3": (V_3V3, V_3V3),
    "PWR24V": (V_24V_MIN, V_24V_MAX),
    "+24V": (V_24V_MIN, V_24V_MAX),
}
#: Stecker, deren Gegenseite die MUSEUMSVERKABELUNG ist: was dort auf
#: einer Ader liegt, weiss die Platine nicht. Ihre Netze duerfen im
#: schlechtesten Fall alles zwischen 0 V und der 24-V-Schiene fuehren
#: (Kurzschluss gegen eine Nachbarader im selben Mantel) -- genau der
#: Fall, den `_notaus_schleifen()` unter Punkt 4 von Hand rechnet.
#: J90 (Task 5, versorgung.py): die eigene 24-V-Einspeisung dieses
#: Moduls -- ihre Gegenseite ist ein externes Netzteil, genauso
#: unbekannt wie die Museumsverkabelung an J3/J5. J95/J96 (Task 5,
#: modulsockel.randpads()): unbestueckte Loetpads, deren Gegenseite
#: "was auch immer jemand anlötet" ist -- ebenfalls unbekannt.
FELDSTECKER = {"J3", "J5", "J90", "J95", "J96"}
#: Stecker, deren Gegenseite ein anderes Modul DESSELBEN Entwurfs ist.
#: Was auf jedem Pin liegt, steht im Vertrag (tools/stack_spec.py) --
#: sie tragen deshalb nichts Unbekanntes ein. J105 (Task 5, v2): die
#: zweite Stapelstecker-Buchsenreihe (Pico-Pins 21..40), s.
#: modulsockel._stapelstecker().
STAPELSTECKER = {"J100", "J101", "J102", "J103", "J104", "J105"}
#: Pins, die ein Baustein aus eigener Kraft ueber die Schienen hinaus
#: treiben kann. Nur die Ladungspumpe des DRV8876 tut das: VCP liegt
#: laut SLVSDS7B, Abschnitt 7.3.1 "Charge Pump", ueber VM. An diesen
#: Knoten darf deshalb kein Widerstand haengen, dessen Leistung die
#: Pruefung aus den Schienen ableitet -- sie prueft das ausdruecklich.
LADUNGSPUMPE_PINS = {("U1", "12"), ("U1", "13"), ("U1", "14")}
#: Ein Baustein verbindet seine Pins NICHT miteinander -- aber jeder
#: seiner Pins kann ein Netz innerhalb der Schienen halten oder treiben,
#: an denen der Baustein selbst haengt. Die Pruefung liest diese
#: Schienen aus dem Schaltplan (welche festen Netze beruehrt dieser
#: Baustein?) und braucht deshalb keine Tabelle -- ausser dort, wo das
#: zu grob waere. Genau ein Baustein ist so ein Fall:
#:
#: **U1 (DRV8876)** liegt mit VM an +24V und mit VREF an 3V3, seine
#: Logik- und Analogpins gehoeren aber ausschliesslich in die
#: 3,3-V-Domaene. Ohne diese Ausnahme haette die Pruefung an R5/R7/R8/
#: R9/R13 26,4 V angesetzt und sechs falsche Alarme erzeugt. Belegt aus
#: TI SLVSDS7B:
#:   Pin 1/2/3 (EN/IN1, PH/IN2, nSLEEP) -- Logikeingaenge, Abschnitt 6.5
#:     "LOGIC-LEVEL INPUTS"; sie treiben gar nichts, ihr Pegel kommt vom
#:     MCU ueber R7/R8/R9 bzw. vom Gatter U3.
#:   Pin 4 (nFAULT) -- Open-Drain-Ausgang gegen GND, Abschnitt 7.3.2
#:     "Protection Circuits"; hochgezogen wird er allein von R13 an 3V3.
#:   Pin 5 (VREF) -- liegt in diesem Entwurf fest auf 3V3.
#:   Pin 6 (IPROPI) -- Stromausgang, Abschnitt 7.3.3.2 "Current
#:     Regulation": I = ITRIP x AIPROPI = 2,54 mA bei der hier
#:     gewaehlten Stromgrenze; an R5 (1,3 k) macht das 3,3 V, an R10
#:     (4,7 k, unbestueckt) waeren es rechnerisch mehr -- deshalb ist
#:     die Obergrenze hier ausdruecklich die 3,3-V-Schiene und nicht
#:     "Strom mal Widerstand": mehr als VREF kann der Pin nicht
#:     ausgeben, weil die Regelung bei ITRIP abschaltet.
#: Pin 8/10 (Out1/Out2) und Pin 11 (VM) bleiben ohne Ausnahme, also bei
#: der vollen 24-V-Spanne -- das ist richtig so.
IC_PIN_BEREICH_AUSNAHME = {
    ("U1", "1"): (0.0, V_3V3),
    ("U1", "2"): (0.0, V_3V3),
    ("U1", "3"): (0.0, V_3V3),
    ("U1", "4"): (0.0, V_3V3),
    ("U1", "5"): (0.0, V_3V3),
    ("U1", "6"): (0.0, V_3V3),
}


# ===================================================================
#  Aufgabe 5f, Klasse 2: Gehaeuse der gewaehlten Bauteile
# ===================================================================
# Zu jedem Bauteil das Gehaeuse des TATSAECHLICH gewaehlten Teils, mit
# Quelle. Geschluesselt nach dem Wert im Schaltplan -- also nach dem,
# was bestellt wird. Wer den Wert aendert (z.B. "IRFR5305" zurueck auf
# "IRF4905"), hat keinen Eintrag mehr und faellt durch.
#
# Felder: (Gehaeusename, Pinzahl, Raster in mm oder None,
#          Anschlussspanne in mm oder None, Quelle)
# Die **Anschlussspanne** ist der Abstand von Anschlussspitze zu
# Anschlussspitze quer ueber das Bauteil. Sie ist das Mass, mit dem sich
# ein Footprint maschinell widerlegen laesst: der Punkt Spanne/2 muss
# INNERHALB eines Pads liegen, sonst sitzt der Anschluss neben seiner
# Loetflaeche. Genau daran faellt der alte Optokoppler-Footprint auf.
# `None` heisst ausdruecklich: dieses Mass ist NICHT belegt und wird
# NICHT geprueft. Die Pruefung zaehlt diese Faelle und nennt sie beim
# Namen, statt sie stillschweigend als "in Ordnung" zu buchen.
GEHAEUSE = {
    # --- Endstufe -------------------------------------------------
    "IRFR5305": ("D-Pak (TO-252AA)", 3, None, None,
                 "LCSC C2624 (Produktseite gesichtet: 'DPAK (TO-252AA)'); "
                 "Datenblatt Infineon/IR PD-95025A, Abschnitt "
                 "'D-Pak (TO-252AA) Package Outline'. Rastermass der "
                 "Anschluesse nicht aus dem Datenblatt gelesen "
                 "(Massbild nur als Grafik) -- deshalb None."),
    "DRV8876PWPR": ("HTSSOP-16 mit Waermepad (PowerPAD, Pin 17)", 17, None, None,
                    "TI SLVSDS7B, Abschnitt 11 'Mechanical, Packaging, and "
                    "Orderable Information' (PWP-Gehaeuse). Footprint ist "
                    "der im Altprojekt reparierte, s. FP_DRV8876."),
    "SMCJ30A": ("SMC (DO-214AB)", 2, None, None,
                "LCSC C340696, bereits in sockelplatine.py gesichtet."),
    "220u": ("Elko radial, Raster 3,5 mm", 2, 3.5, None,
             "Aufgabenbrief 4, woertlich: CP_Radial_D8.0mm_P3.50mm."),
    "PC817": ("SMD-4P, SMT-Gullwing-Anschluesse", 4, 2.54, 10.0,
              "SHARP D2-A03101EN (Sep. 30. 2003), 'Outline Dimensions' "
              "Zeichnung 2 'SMT Gullwing Lead-Form' (Raster 2,54+-0,25, "
              "Spanne 10,0 +0/-0,5, Reihe 7,62+-0,3) und 'Design "
              "Considerations' -> 'Recommended Foot Print (reference)', "
              "Zeile 'SMT Gullwing Lead-form' (Reihenabstand 8,2, Pad "
              "2,2 x 1,7, Raster 2,54). LCSC C97308."),
    # ("Notaus-Ruhestrom"/"Motor-Klemme" sind Steckverbinder mit
    #  Durchsteck- bzw. Schraubanschluss -- dort ist nicht die
    #  Anschlussspanne das Mass, sondern das Raster; deshalb Spanne
    #  None und Raster gesetzt.)
    "SN74LVC1G07": ("SOT-353 (SC-70-5), DCK", 5, 0.65, 2.10,
                    "LCSC C7830 (Produktseite: Gehaeuse 'SC-70-5'); TI "
                    "SCES296AG, Abschnitt 3 'Description', Tabelle "
                    "'Package Information': 'DCK (SC70, 5) ... PACKAGE "
                    "SIZE 2.00mm x 2.10mm ... BODY SIZE 2.00mm x "
                    "1.25mm', Fussnote (2): 'The package size (length x "
                    "width) is a nominal value and includes pins' -- die "
                    "2,10 mm sind also die Anschlussspanne (die "
                    "Gehaeusezeichnung DCK0005A, 4214834/G 11/2024, in "
                    "Abschnitt 10 nennt dafuer 1,8 bis 2,4 mm). Das "
                    "Rastermass steht in derselben Zeichnung als "
                    "'2X 0.65'."),
    "SN74LVC1G08": ("SOT-353 (SC-70-5), DCK", 5, 0.65, 2.10,
                    "LCSC C7832 (Produktseite: Gehaeuse 'SC-70-5'); "
                    "dasselbe DCK-Gehaeuse (DCK0005A) wie der "
                    "SN74LVC1G07, Masse daher aus SCES296AG, s. dort."),
    "Motor-Klemme": ("Schraubklemme 2-polig, Raster 5,08 mm", 2, 5.08, None,
                     "DB128L-5.08-2P-GN-S, LCSC C395868 (hardware/"
                     "bauteile-1b.md). Der Footprint ist ein genormter "
                     "5,08-mm-Platzhalter -- Polzahl und Raster stimmen, "
                     "der Koerperumriss ist der eines Phoenix-Blocks. "
                     "Aufgabe 7 zeichnet den echten DB128L."),
    "Notaus-Ruhestrom": ("Stiftleiste 1x04, Raster 2,54 mm", 4, 2.54, None,
                         "Beleg 11 in hardware/bauteile-1b.md: "
                         "handelsuebliche 2,54-mm-Stiftleiste, damit eine "
                         "gewoehnliche Jumper-Bruecke den unbenutzten "
                         "Kanal schliessen kann."),
    # --- Versorgungszelle (Aufgabe 3, tools/sch/versorgung.py, hier nur
    #     wiederverwendet -- diese Bauteile werden von versorgung.bauen()
    #     platziert, tauchen aber ueber motormodul.bauen() in DERSELBEN
    #     generierten Netzliste auf und muessen deshalb hier einen
    #     Eintrag haben, sonst faellt diese Pruefung auf J90/U90/D91.) --
    "SS36C": ("SMC (DO-214AB)", 2, None, None,
              "LCSC C16237 (versorgung.py-Kommentar bei D91_WERT: "
              "'Schottky 60V 3A, DO-214AB'); dasselbe Gehaeuse wie "
              "SMCJ30A oben, andere Diode."),
    "K7805-1000R3": ("SIP-3 THT (RECOM-R-78B-Fussabdruck)", 3, 2.54, None,
                     "LCSC C909765 (versorgung.py-Kommentar bei U90_WERT). "
                     "Raster NICHT aus dem DEXU-Datenblatt gelesen "
                     "(Massbild nur als Grafik) -- eigene Pruefung der "
                     "tatsaechlichen Footprint-Datei "
                     "Converter_DCDC_RECOM_R-78B-2.0_THT.kicad_mod: drei "
                     "Pads bei x=0/2,54/5,08 mm, Raster also 2,54 mm. "
                     "Anschlussspanne bewusst None: die "
                     "Anschlussspanne-Pruefung erwartet ein um (0,0) "
                     "ZENTRIERTES Bauteil (Pruefpunkte +-Spanne/2) -- bei "
                     "diesem SIP-3-Footprint sitzt Pin 1 selbst im "
                     "Ursprung, das Bauteil ist nicht zentriert, die "
                     "Pruefung passt hier nicht."),
    "Versorgung Eingang": ("Schraubklemme 2-polig, Raster 3,5 mm", 2, 3.5, None,
                           "versorgung.py, FP_KLEMME_2-Kommentar: "
                           "PT-1,5-2-3.5 (LCSC-Nachbarbauteil von "
                           "KF350-3.5-2P, C474892), Footprint-String "
                           "identisch mit dimmermodul.FP_KLEMME_2."),
    # --- Modulsockel (Aufgaben 3/4, hier nur wiederverwendet) ------
    "STM32C011F6P6": ("TSSOP-20", 20, None, None,
                      "hardware/bauteile.md (Etappe 1a), ST DS13866. "
                      "Raster nicht aus dem Datenblatt gelesen."),
    "SN74LVC1G175": ("SOT-363 (SC-70-6)", 6, None, None,
                     "LCSC C202238; TI SCES560G, Abschnitt 3 "
                     "('DCK Package, 6-Pin SC70')."),
    "SN74LVC2G00DCUR": ("VSSOP-8, 0,5 mm", 8, 0.5, None,
                        "LCSC C206109 (Produktseite: Gehaeuse "
                        "'VSSOP-8-0.5mm')."),
    # "Stapelstecker 2x20" (v1, EIN 40-Pin-Block, LCSC C35165) ist mit
    # Task 4 entfallen -- v2 zerlegt ihn in zwei 1x20-Reihen (stack_spec.
    # STECKER_POS["stapel_links"/"stapel_rechts"]), je Reihe der halbe
    # Pinsatz derselben Bauteilfamilie ("Buchse mit durchgehendem
    # Stift"). Eine eigene LCSC-Nummer fuer die 20-Pin-Variante ist HIER
    # nicht belegt (Aufgabe 6/7, Beschaffung) -- Raster/Pinzahl kommen
    # stattdessen direkt aus stack_spec.py (dort mit voller Geometrie-
    # Herleitung, s. "stapel_links/stapel_rechts"-Kommentarblock).
    "Stapelstecker links, Pico-Pins 1..20 (Buchse)":
        ("Buchse mit durchgehendem Stift, 2,54 mm", 20, 2.54, None,
         "stack_spec.py, STECKER_POS['stapel_links']; LCSC-Nummer der "
         "20-Pin-Variante noch offen (Aufgabe 6/7)."),
    "Stapelstecker rechts, Pico-Pins 21..40 (Buchse)":
        ("Buchse mit durchgehendem Stift, 2,54 mm", 20, 2.54, None,
         "stack_spec.py, STECKER_POS['stapel_rechts'] -- exaktes "
         "Spiegelbild von stapel_links, s. dort."),
    "Randpads GPIO, unbestueckt (THT-Loetpad)":
        ("Stiftleiste 1x18, Raster 2,54 mm", 18, 2.54, None,
         "modulsockel.FP_RANDPAD_GPIO -- unbestueckter Platzhalter "
         "(dnp=True), Polzahl/Raster stimmen mit stack_spec.RANDPADS "
         "ueberein; die Silk-Beschriftung ist Sache des Layouts."),
    "Randpads Versorgung: 2x 3V3 + 2x GND, unbestueckt (THT-Loetpad)":
        ("Stiftleiste 1x04, Raster 2,54 mm", 4, 2.54, None,
         "modulsockel.FP_RANDPAD_VERSORGUNG, sonst wie oben."),
    "Kettenstecker, Buchse oben (SMD)": ("Buchsenleiste 1x02, 2,54 mm", 2, 2.54, None,
                                         "LCSC C541849."),
    "Kettenstecker, Stift unten (SMD)": ("Stiftleiste 1x02, 2,54 mm", 2, 2.54, None,
                                         "LCSC C492401."),
    "Leistungsstecker, Buchse oben (SMD)": ("Buchsenleiste 2x02, 2,54 mm", 4, 2.54, None,
                                            "LCSC C2977590."),
    "Leistungsstecker, Stift unten (SMD)": ("Stiftleiste 2x02, 2,54 mm", 4, 2.54, None,
                                            "LCSC C66690."),
}
#: Chipbauformen: hier bestimmt nicht der Wert das Gehaeuse, sondern die
#: Bauformwahl. Zollcode -> Koerperlaenge in mm. Der Code IST das Mass
#: (0805 = 0,080" x 0,050"), deshalb braucht er kein Datenblatt; die
#: metrische Zweitbezeichnung im KiCad-Namen (2012Metric = 2,0 x 1,2 mm)
#: sagt dasselbe noch einmal.
CHIP_LAENGE_MM = {"0805": 2.03, "1206": 3.05}
#: Wieviel darf die Spannweite der Pad-Mitten eines Chip-Footprints vom
#: Koerpermass abweichen, bevor die Pruefung sie fuer eine andere
#: Bauform haelt? 0,8 mm trennt 0805 (2,03) und 1206 (3,05) sicher --
#: die beiden benachbarten Zollcodes liegen 1,02 mm auseinander.
CHIP_TOLERANZ_MM = 0.8

#: Die vom Hersteller empfohlene Landflaeche des PC817 in SMT-Gullwing-
#: Form, gegen die der projekteigene Footprint Pad fuer Pad geprueft
#: wird. Quelle: SHARP D2-A03101EN, "Design Considerations" ->
#: "Recommended Foot Print (reference)", Zeile "SMT Gullwing Lead-form".
PC817_LAND_REIHE_MM = 8.2       # Pad-Mitte zu Pad-Mitte, quer
PC817_LAND_PAD_X_MM = 2.2       # Padlaenge (quer, Richtung Anschluss)
PC817_LAND_PAD_Y_MM = 1.7       # Padbreite (laengs, Richtung Raster)

#: Pads, die im Footprint vorkommen, aber im Symbol keinen Pin haben --
#: mit Begruendung. Ohne Eintrag faellt die Pruefung durch; ein
#: ueberzaehliges Pad ist sonst ein Hinweis auf den falschen Footprint.
#:
#: LEER seit dem Bauteiltausch 1G06->1G07 (Task 5, 2026-09-08) -- eigene
#: Pruefung der KiCad-Quelle (74xGxx.kicad_sym) foerderte dabei einen
#: echten Unterschied zwischen den beiden Symbolen zutage: 1G06
#: fuehrt gar keinen Pin "1" (die Symboldefinition beginnt direkt bei
#: Pin 2/A), waehrend 74LVC1G07 Pin 1 SEHR WOHL als Pin fuehrt (Typ
#: "free", Name "NC") -- deshalb war frueher hier ein Eintrag fuer
#: "SN74LVC1G07"/"1" noetig (Pad 1 des Footprints ohne Gegenstueck im
#: 1G06-Symbol); mit dem 1G07-Symbol matcht Pad 1 jetzt direkt Pin 1,
#: die Pruefung braucht dafuer keinen Eintrag mehr. `sch.nc(inv, "1")`
#: (s. `_notaus_schleifen()`) markiert den jetzt SYMBOLSEITIG
#: vorhandenen NC-Pin explizit -- ohne ihn meldete
#: `gen.Schaltplan.selbstpruefung()` "haengt in der Luft" (eigene
#: Pruefung, tatsaechlich rot gesehen).
FOOTPRINT_PAD_OHNE_PIN = {}


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C", "Device.kicad_sym", "C")
    sch.lib("Device:C_Polarized", "Device.kicad_sym", "C_Polarized")
    sch.lib("Device:D", "Device.kicad_sym", "D")
    sch.lib("Device:D_Zener", "Device.kicad_sym", "D_Zener")
    # Q1 (das GENERISCHE P-Kanal-Symbol, Transistor_FET:Q_PMOS_GDS) ist
    # mit dem alten Verpolschutz-Strang entfallen -- versorgung.py laedt
    # dasselbe Symbol fuer Q90 selbst (`versorgung._load_libs()`), s.
    # Kommentar vor `_stapel_speist_lokal()` oben.
    sch.lib("Isolator:PC817", "Isolator.kicad_sym", "PC817")
    # U3: dasselbe Gatter-Bauteil wie U103 im Modulsockel (SN74LVC1G08,
    # SOT-353) -- keine neue Bauteilnummer noetig, LCSC C7832 ist in
    # hardware/bauteile-1b.md bereits auf der Produktseite geprueft.
    sch.lib("74xGxx:74LVC1G08", "74xGxx.kicad_sym", "74LVC1G08")
    # U6/U7: NICHTinvertierender Puffer mit OPEN-DRAIN-Ausgang
    # (SN74LVC1G07, SOT-353, derselbe Footprint wie U3) -- ERSETZT
    # 2026-09-08 den zuvor eingesetzten 1G06 (invertierend,
    # fail-unsafe), s. INVERTER_WERT-Kommentar oben. Warum ein
    # Open-Drain-Ausgang und kein gewoehnliches Gatter: s.
    # `_notaus_schleifen()`, Abschnitt "Warum nicht Pulldown + Diode".
    # Pin 1 (NC) fuehrt das KiCad-Symbol gar nicht -- die Selbstpruefung
    # verlangt ihn deshalb auch nicht.
    sch.lib("74xGxx:74LVC1G07", "74xGxx.kicad_sym", "74LVC1G07")
    sch.lib("Connector:Screw_Terminal_01x02", "Connector.kicad_sym",
            "Screw_Terminal_01x02")
    sch.lib("Connector:Screw_Terminal_01x03", "Connector.kicad_sym",
            "Screw_Terminal_01x03")
    sch.lib("Connector:Conn_01x04_Pin", "Connector.kicad_sym", "Conn_01x04_Pin")
    # DRV8876PWPR: kein Gegenstueck in der KiCad-System-Bibliothek (eigene
    # Pruefung: weder Driver_Motor.kicad_sym noch sonst eine System-
    # Bibliothek fuehrt den Typ) -- das Altprojekt bindet dafuer einen
    # Snapeda-Export ein. Uebernommen nach hardware/kicad/components/
    # symbols/DRV8876PWPR.kicad_sym; symlib.extract() akzeptiert seit
    # dieser Aufgabe auch absolute Pfade (s. tools/sch/symlib.py), genau
    # dafuer.
    drv_sym = os.path.join(HERE, "..", "..", "hardware", "kicad",
                            "components", "symbols", "DRV8876PWPR.kicad_sym")
    sch.lib("DRV8876PWPR:DRV8876PWPR", os.path.abspath(drv_sym), "DRV8876PWPR")


# ===================================================================
#  Q1/R11/R12/D1/C12 (v1-Verpolschutz-Strang) ENTFALLEN (Task 5, 2026-09-08)
# ===================================================================
# Frueher stand hier `_endstufe_leistung()`: ein eigener Verpolschutz
# (Q1/R11/R12) plus TVS (D1) und Stuetzkondensator (C12) zwischen dem
# Stapel-Netz "PWR24V" (Quelle, ueber J103/J104) und der lokalen,
# geschuetzten Schiene "+24V". Diese Funktion ist ERSATZLOS entfallen
# -- ersetzt durch einen Aufruf von `versorgung.bauen()` (s. `bauen()`
# unten), der GENAU dieselbe Aufgabe uebernimmt (Verpolschutz + TVS +
# Stuetzkondensator vor "+24V"), nur mit einer eigenen Klemme J90 statt
# PWR24V als Eingang, UND -- anders als die alte Fassung -- RICHTIG
# gepolt.
#
# **Der behobene Fehler.** Q1 sass in der alten Fassung GENAU
# UMGEKEHRT: Source an der rohen Einspeisung ("PWR24V"), Drain an der
# bereits geschuetzten lokalen Schiene ("+24V"), und der Gate-Teiler
# (R11/R12) hing ebenfalls an PWR24V statt an der lokalen Schiene. Bei
# verpolter Einspeisung leitet die Body-Diode eines P-Kanal-MOSFETs in
# GENAU dieser Anordnung durch, und die (dann vorwaertsgespeiste) TVS
# D1 bildet zusammen mit ihr einen Kurzschluss-Pfad ("Crowbar") statt
# den Rueckstrom zu sperren -- der Schutz schuetzte in genau dem Fall
# nichts, fuer den er gedacht war. Volle Herleitung: tools/sch/
# versorgung.py (Moduldoku ganz oben). tests/test_versorgung.py haelt
# dazu einen Rot-Nachweis: er baut motormodul.bauen() vor dieser
# Aenderung tatsaechlich auf und bestaetigt die falsche Polung an der
# echten, generierten Netzliste (nicht nur am Kommentar hier) -- mit
# dieser Aenderung wird genau dieser Nachweis hinfaellig und die
# betroffenen Zusicherungen in tests/test_versorgung.py wurden
# entsprechend auf die POSITIVE Pruefung (Q90 statt Q1) umgestellt.
#
# **NETZ-ABBILDUNG v1 -> v2** (fuer die Endstufe unten UNVERAENDERT
# wichtig -- R7..R13/U1/C9..C13/R16..R21 haengen weiterhin an "+24V"/
# "GND", nur wer diese Schiene speist, hat sich geaendert):
#   * "+24V" (lokal, geschuetzt) -- bleibt namensgleich "+24V", nur
#     jetzt hinter Q90s Source (vorher Q1s Drain) getrieben.
#   * "PWR24V" (Stapel, ueber J103/J104 durchgereicht) -- bleibt
#     namensgleich "PWR24V"; s. `_stapel_speist_lokal()` unten, warum
#     dieses Netz auf DIESEM Modul trotzdem nicht ins Leere laeuft.
#   * "Q1_GATE" entfaellt ersatzlos -- der Nachfolgeknoten
#     ("Q90_GATE") ist intern in versorgung.py verdrahtet, nicht von
#     hier aus sichtbar.
#
# **IRFR5305-Herleitung (Sperrspannung/Gatespannung/Durchlassverlust,
# Aufgabe 5f) bleibt unten stehen, obwohl die Funktion entfallen ist**
# -- versorgung.py zitiert sie woertlich ("Q90_WERT = 'IRFR5305' ...
# Herleitung s. motormodul.py::_endstufe_leistung"), und dieselbe
# Bauteilwahl (nur richtig gepolt) gilt fuer Q90 unveraendert:
#
#   IRFR5305PbF (Infineon/International Rectifier), P-Kanal,
#   **D-Pak (TO-252AA)**, LCSC **C2624**
#   (`lcsc.com/product-detail/mosfets_infineon-technologies-
#   irfr5305trpbf_C2624.html`, Rohdaten: "P-Channel MOSFET",
#   Gehaeuse "DPAK (TO-252AA)", "55V", "31A", "65mOhm @ 10V",
#   "110W", Bestand 17 854).
#   Datenblatt Infineon/IR **PD-95025A** (12/13/04), selbst gelesen:
#   Titelzeile "IRFR5305PbF ... Surface Mount (IRFR5305) ...
#   VDSS = -55V, RDS(on) = 0.065 Ohm, ID = -31A"; "Absolute Maximum
#   Ratings": VGS +-20 V, PD 110 W; "Electrical Characteristics":
#   VGS(th) -2,0 bis -4,0 V, IGSS +-100 nA bei VGS = +-20 V;
#   Abschnitt "D-Pak (TO-252AA) Package Outline".
#
#   * Sperrspannung: 55 V gegen 26,4 V Schiene und gegen die
#     Klemmspannung der TVS (SMCJ30A, MAX 48,4 V) -- passt.
#   * Gatespannung: R90/R91 sind gleich gross (wie vorher R11/R12),
#     also VGS = -U/2 = -13,2 V im schlechtesten Fall. Unter +-20 V
#     (Grenzwert) und ueber den -4,0 V Einschaltschwelle (MAX) -- der
#     Transistor ist sicher durchgesteuert und sicher nicht
#     ueberlastet.
#   * Durchlassverlust: 0,065 Ohm x (2,5 A)^2 = 0,41 W; das
#     Datenblatt nennt fuer typische SMD-Montage "Power dissipation
#     levels up to 1.5 watts are possible".
#   * Gateleckstrom 100 nA gegen 1,3 mA Teilerstrom durch R90/R91 --
#     der Teiler bestimmt die Gatespannung, nicht der Transistor.


def _stapel_speist_lokal(sch, ox, oy):
    """Verbindet "PWR24V" (Stapel, ueber J103/J104 durchgereicht) mit
    "+24V" (lokal, hinter Q90 geschuetzt) zu EINEM elektrischen Knoten.

    Ohne diesen Draht waeren beide Netze auf diesem Modul voneinander
    isoliert: modulsockel.einbauen() legt J103/J104 unbedingt auf
    "PWR24V", aber nichts sonst haengt hier daran, seit der alte
    Q1-Strang (Quelle "PWR24V") entfallen ist. Der Vertrag sieht vor,
    dass EINE Platine im Stapel tatsaechlich extern gespeist wird
    (ihre eigene Klemme J90, s. versorgung.bauen()) und diese Speisung
    ueber den Leistungsstecker an den Rest des Stapels weitergibt --
    "eine gespeiste Platine versorgt den Stapel". Ist das Motormodul
    NICHT die gespeiste Platine (J90 bleibt dann unbestueckt/offen),
    schadet die Verbindung trotzdem nicht: sie macht "+24V" und
    "PWR24V" nur zu Namen fuer denselben Knoten, unabhaengig davon, wer
    ihn tatsaechlich treibt.

    Zwei lokale Labels an denselben Drahtenden sind in KiCad ein
    legitimer Weg, zwei Netznamen elektrisch gleichzusetzen -- dieselbe
    Grundidee wie modulsockel._stapelstecker()s gleichlautende Labels
    OHNE gemeinsamen Draht (s. dortiger Docstring), hier nur umgekehrt:
    derselbe Draht, zwei VERSCHIEDENE Namen. Verifiziert per
    `kicad-cli sch erc` (0 Fehler, 0 Warnungen) -- kein rein behaupteter
    Kurzschluss zweier Label."""
    a = (ox, oy)
    b = (ox + 15.24, oy)
    sch.draht(a, b)
    sch.LABELS.append((a[0], a[1], 0, "+24V"))
    sch.LABELS.append((b[0], b[1], 180, "PWR24V"))


def _gatter_abblockung_sockel(sch, ox, oy):
    """Je ein 100-nF-Abblockkondensator fuer U101/U102/U103 (Task 6b).

    Schliesst im Motormodul dieselbe Luecke, die Task 6 bereits im
    Dimmermodul geschlossen hat (dimmermodul.py::_gatter_abblockung()):
    modulsockel.py deckt mit C100 nur U100 (MCU) ab, C101 ist Teil des
    NCLR-Loeschglieds -- U101 (SN74LVC1G175, SOT-363), U102
    (SN74LVC2G00DCUR, VSSOP-8) und U103 (SN74LVC1G08, SOT-353) haengen
    alle drei mit VCC/GND an 3V3/GND, aber keines hatte bislang einen
    eigenen Kondensator direkt an seiner Versorgung. `ox`/`oy` sind
    hier DIESELBEN Koordinaten, die auch an `modulsockel.einbauen()`
    uebergeben werden (s. `bauen()` unten) -- der Modulsockel-Block ist
    in Dimmer- und Motormodul byte-fuer-byte derselbe Code, also liegen
    U101/U102/U103 an genau denselben Absolutkoordinaten wie im
    Dimmermodul, und dieselben drei x-Positionen (ox+152,40/+177,80/
    +203,20) bei y = oy - 45,72 -- knapp 15,24 mm unterhalb der
    Kennwiderstandsreihe (oy - 30,48, s. modulsockel.einbauen()) --
    treffen hier ebenso knapp neben die drei ICs wie dort.

    Referenzen C17/C18/C19 (naechste freie Motormodul-Nummern NACH
    C16, s. Kommentar bei C_SOCKEL_ABBLOCK_WERT oben) -- NICHT C102/
    C103/C104 wie im Dimmermodul: das sind zwei getrennte
    .kicad_sch-Dateien mit je eigenem Referenzraum, eine Kollision ist
    dort schon aus diesem Grund ausgeschlossen. Kollisionsfrei
    gegenueber den EIGENEN Bauteilen dieses Moduls, weil alle anderen
    Motormodul-Bloecke entweder bei ox-40,64/ox-76,2 (R7..R13, C13),
    bei ox+330,2 oder weiter (Verriegelung, Notaus-Ruhestrom,
    Versorgungszelle) oder bei ox+431,8 (Endstufe/Motor-Klemme) sitzen
    -- keiner davon beruehrt das Fenster ox+152,4..ox+203,2 bei
    y = oy - 45,72. Per `kicad-cli sch erc` gegen 0 Fehler geprueft
    (Warnungen s. task-6b-report.md), nicht nur angenommen."""
    for ref, x in (("C17", ox + 152.40), ("C18", ox + 177.80),
                   ("C19", ox + 203.20)):
        sch.bauteil(ref, "Device:C", (x, oy - 45.72), C_SOCKEL_ABBLOCK_WERT,
                    FP_C0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27),
                    felder={"LCSC": C_SOCKEL_ABBLOCK_LCSC})
        sch.netz(ref, "1", "U", "3V3")
        sch.netz(ref, "2", "D", "GND")


def _endstufe_treiber(sch, ox, oy, netze):
    """U1 (DRV8876) mit C9/C10/C11, den Vorwiderstaenden R7/R8/R9/R13, der
    Stromgrenze R5/R10 und dem IPROPI-Filter C13. `netze` ist der
    Rueckgabewert von modulsockel.einbauen() (== NETZE_NACH_AUSSEN) --
    diese Funktion schliesst die MCU-seitigen Enden von IN1/IN2/NSLEEP/
    NFAULT/IPROPI, die modulsockel.py offen liess."""
    sch.bauteil("U1", "DRV8876PWPR:DRV8876PWPR", (ox, oy), "DRV8876PWPR",
                FP_DRV8876, rot=0, roff=(-20.32, 30.48), voff=(-20.32, 33.02))
    sch.netz("U1", "1", "L", "U1_EN_IN1")
    sch.netz("U1", "2", "L", "U1_PH_IN2")
    sch.netz("U1", "3", "L", "U1_NSLEEP")
    sch.netz("U1", "4", "R", netze["NFAULT"])
    sch.netz("U1", "5", "L", "3V3")           # VREF, wie im Altprojekt an 3,3V
    sch.netz("U1", "6", "L", netze["IPROPI"])
    sch.netz("U1", "7", "L", "GND")           # IMODE=GND: Fixed Off-Time, Automatic Retry (Tabelle 6)
    sch.netz("U1", "8", "R", "Out1")
    sch.netz("U1", "9", "R", "GND")           # PGND
    sch.netz("U1", "10", "R", "Out2")
    sch.netz("U1", "11", "L", "+24V")         # VM
    sch.netz("U1", "12", "L", "VCP")
    sch.netz("U1", "13", "R", "CPH")
    sch.netz("U1", "14", "R", "CPL")
    sch.netz("U1", "15", "R", "GND")
    sch.netz("U1", "16", "L", "GND")          # PMODE=GND: Bridge-Control-Modus (wie Altprojekt)
    sch.netz("U1", "17", "R", "GND")          # EXP, Waermepad

    # C9 (VCP-Kondensator, VM<->VCP -- laut TI-App-Schaltung an VM
    # referenziert, NICHT an GND; eigene Pruefung der Altprojekt-
    # Netzliste: C9 Pin 1 liegt dort auf "+24V", nicht auf GND).
    sch.bauteil("C9", "Device:C", (ox + 60.96, oy + 33.02), C9_WERT, FP_C0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C9", "1", "U", "+24V")
    sch.netz("C9", "2", "D", "VCP")

    # C10 (Ladungspumpen-Kondensator CPH<->CPL, unpolarisiert).
    sch.bauteil("C10", "Device:C", (ox + 60.96, oy - 12.7), C10_WERT, FP_C0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C10", "1", "U", "CPH")
    sch.netz("C10", "2", "D", "CPL")

    # C11 (zweiter 24-V-Abblock-Kondensator, unpolarisiert).
    sch.bauteil("C11", "Device:C", (ox + 60.96, oy + 15.24), C11_WERT, FP_C0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C11", "1", "U", "GND")
    sch.netz("C11", "2", "D", "+24V")

    # R7/R8/R9/R13/R5/R10 sitzen alle in derselben Spalte (ox-40.64) und
    # brauchen deshalb genug Zeilenabstand: ein Device:R-Bauteil belegt
    # senkrecht rund 17,78 mm (Pin bei +-3,81 mm vom Zentrum, Stichleitung
    # weitere 5,08 mm je Seite) -- 25,4-mm-Schritte lassen reichlich Luft.
    # (Ohne diesen Abstand faellt das Ende der Stichleitung EINES
    # Widerstands exakt auf den Pin des naechsten -- eine echte, per
    # `kicad-cli sch erc` gefundene Verwechslung dieser Aufgabe: bei
    # 12,7-mm-Schritten verschmolzen z.B. IN1 und U1_PH_IN2 zu einem
    # einzigen Netz.)
    sch.bauteil("R7", "Device:R", (ox - 40.64, oy + 76.2), R7_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R7", "1", "U", netze["IN1"])
    sch.netz("R7", "2", "D", "U1_EN_IN1")
    sch.bauteil("R8", "Device:R", (ox - 40.64, oy + 50.8), R8_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R8", "1", "U", netze["IN2"])
    sch.netz("R8", "2", "D", "U1_PH_IN2")
    # R9 endet seit der Verriegelungs-Nachbesserung NICHT mehr am
    # DRV8876-Pin, sondern am Eingang A des UND-Gatters U3
    # (s. `_notaus_verriegelung()`); U1_NSLEEP treibt jetzt allein U3.
    # R9 ist damit ein reiner Serien-/ESD-Widerstand vor einem
    # CMOS-Eingang: er fuehrt hoechstens II = +-5 uA (SCES217AA,
    # Abschnitt 5.5), macht also 0,5 mV Spannungsabfall -- 100 Ohm sind
    # dafuer richtig und muessen NICHT vergroessert werden.
    sch.bauteil("R9", "Device:R", (ox - 40.64, oy + 25.4), R9_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R9", "1", "U", netze["NSLEEP"])
    sch.netz("R9", "2", "D", "NSLEEP_GATTER")

    # R13: NFAULT-Pullup an 3V3 (Open-Drain-Ausgang des DRV8876).
    sch.bauteil("R13", "Device:R", (ox - 40.64, oy), R13_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R13", "1", "U", "3V3")
    sch.netz("R13", "2", "D", netze["NFAULT"])

    # R5 (bestueckt, NEU gerechnet, s. Moduldoku oben Punkt 1) / R10
    # (NICHT bestueckt, dnp=True, Wert unveraendert) -- beide zwischen
    # IPROPI und GND, parallel; C13 filtert IPROPI zusaetzlich.
    sch.bauteil("R5", "Device:R", (ox - 40.64, oy - 25.4), R5_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R5", "1", "U", netze["IPROPI"])
    sch.netz("R5", "2", "D", "GND")
    sch.bauteil("R10", "Device:R", (ox - 40.64, oy - 50.8), R10_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27), dnp=True)
    sch.netz("R10", "1", "U", netze["IPROPI"])
    sch.netz("R10", "2", "D", "GND")
    # C13 auf einer DRITTEN Spalte (weder die R7..R10-Spalte noch die
    # Spalte, auf der U1s eigene Pin-Stichleitungen enden) -- sonst
    # dieselbe Kollisionsgefahr wie oben, nur zwischen C13 und U1.
    sch.bauteil("C13", "Device:C", (ox - 76.2, oy - 25.4), C13_WERT, FP_C0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C13", "1", "U", netze["IPROPI"])
    sch.netz("C13", "2", "D", "GND")


# Der Sensoreingang (J2 + R6 + U2) ist ENTFALLEN -- Aufgabe 5f,
# Begruendung in der Moduldoku oben, Punkt 6. Kurz: er war schon im
# Altprojekt unbenutzt ("keine Sensoren angeschlossen oder geplant",
# dortiges README.md), das Design-Dokument fuehrt ihn fuer den Modultyp
# Motor nicht ("DRV8876, ein Motor, Strommessung, Notaus-Eingaenge"),
# und sein Vorwiderstand R6 lag mit 0,236 W dauerhaft ueber der
# Belastbarkeit seines 0805-Gehaeuses (0,125 W). Ein ueberlastetes
# Bauteil ohne Aufgabe wird weggelassen, nicht vergroessert.
#
# Wer den Eingang spaeter doch braucht, baut ihn NICHT einfach mit einem
# groesseren Widerstand wieder ein: bei 24 V und einem PC817 (VF 1,2 V)
# braucht man fuer 0,125 W mindestens
#     R > (26,4 V - 1,2 V)^2 / 0,125 W = 5,1 kOhm  (0805)
# und landet dann bei 4,9 mA LED-Strom -- oder man nimmt gleich 1206
# (0,25 W) wie die Schleifenwiderstaende R16..R19, die genau dieselbe
# Aufgabe an derselben Schiene loesen und deren Rechnung in
# `_notaus_schleifen()`, Punkt 4, steht. Die Leistungspruefung in
# tests/test_motormodul.py rechnet das fuer JEDEN Widerstand nach, der
# an mehr als 5 V liegt -- ein zu kleines Gehaeuse faellt dort auf,
# egal an welcher Stelle des Schaltplans es steht.
#
# Frei geworden: U100 Pin 2 (PC14) ist wieder ein unbenutzter GPIO
# (modulsockel legt ihn ohne Eintrag in zusatz_pins selbst auf
# no_connect), und die 3-polige Klemme entfaellt aus der Stueckliste.


def _motor_out(sch, ox, oy):
    """J5 (Motor-Klemme, 2-polig) an Out1/Out2 (U1 Pins 8/10)."""
    sch.bauteil("J5", "Connector:Screw_Terminal_01x02", (ox, oy),
                "Motor-Klemme", FP_KLEMME_2, rot=0,
                roff=(2.54, -6.35), voff=(2.54, -3.81))
    sch.netz("J5", "1", "L", "Out1")
    sch.netz("J5", "2", "L", "Out2")


def _notaus_schleifen(sch, ox, oy, netze):
    """Der Notaus-Eingang nach dem RUHESTROMPRINZIP (Aufgabe 5d).

    ## Was vorher falsch war

    Bis zu dieser Aufgabe war der externe Kontakt ein SCHLIESSER: J3 Pin 1
    bzw. 3 lag ueber einen potentialfreien Kontakt an GND, Schliessen
    hiess Notaus. Damit sehen ein Kabelbruch, ein abgezogener Stecker und
    eine lose Klemme genau wie "alles in Ordnung" aus -- die
    Schutzfunktion verschwindet still. Ein Not-Halt-Kreis arbeitet
    deshalb mit OEFFNERN im Ruhestrom: Strom fliesst im Normalbetrieb,
    und alles, was den Stromfluss unterbricht -- der Taster, ein Bruch,
    ein gezogener Stecker, eine korrodierte Klemme -- loest aus.

    ## Was jetzt gilt

    Je Kanal fuehrt die Platine eine Ader nach draussen und nimmt sie
    ueber eine zweite zurueck. Dazwischen liegt der Oeffner. Der Weg
    (Kanal 1, Kanal 2 ist Bauteil fuer Bauteil identisch):

        +24V --R16(3k3)-- J3.1 ==Oeffner== J3.2 --R18(3k3)-- U4-LED -- GND
                                                              |
        3V3 --U4-Kollektor ... U4-Emitter --+-- SCHLEIFE_1 ----+
                                            |
                                          R20 (4k7, Pulldown)
                                            |
                                           GND

    SCHLEIFE_1 geht an (a) den Modul-MCU (U100 Pin 3, Kanaldiagnose) und
    (b) den Eingang von U6. Schleife geschlossen -> LED leuchtet ->
    Fototransistor leitet -> SCHLEIFE_1 HIGH -> "in Ordnung". Schleife an
    IRGENDEINER Stelle offen -> kein LED-Strom -> R20 zieht SCHLEIFE_1
    auf GND -> "Notaus".

    Die Polaritaet, die der MCU liest, bleibt dabei dieselbe wie vorher:
    LOW an seinem Eingang heisst weiterhin "dieser Kanal meldet Notaus".
    Der Netzname wechselt trotzdem (NOTAUS_1/2 -> SCHLEIFE_1/2), damit
    niemand alte Firmware oder alte Doku unbemerkt weiterverwendet: die
    Bedeutung des Pegels ist gleich, die Bedeutung des KONTAKTS ist es
    nicht.

    ## Punkt 1: welche Spannung geht nach draussen -- und warum nicht 3,3 V

    Nach draussen gehen die **24 V** der lokalen, ueber Q1 geschuetzten
    Schiene, und die Rueckwandlung macht ein OPTOKOPPLER, kein
    Spannungsteiler. Drei Gruende:

    1. **Stoerfestigkeit.** Museumskabel sind lang und liegen neben
       Motor- und Netzleitungen. Ein 3,3-V-Signal auf eine hochohmige
       Last gegeben wird von eingekoppelter Stoerspannung und von
       Kriechwegen (Feuchte, Staub in einer Klemme) in BEIDE Richtungen
       verfaelscht. Hier fliesst stattdessen ein definierter STROM von
       rund 3,5 mA (Rechnung unten); ein Kriechweg von einigen zehn
       kOhm aendert daran nichts Wesentliches, und eine eingekoppelte
       Stoerung muesste Milliampere liefern, um die LED zu taeuschen.
    2. **Kontaktbenetzung.** Ein mechanischer Kontakt, ueber den nur
       Mikroampere fliessen, oxidiert und wird unzuverlaessig. 3,5 mA
       sind ein brauchbarer Benetzungsstrom.
    3. **Kein Feldpotential an der Logik.** Der Optokoppler trennt den
       Aussenkreis vom Logikknoten. Was auf der Ader passiert -- 24 V,
       0 V, Stoerimpulse -- erreicht weder das Gatter noch den MCU. Der
       Pegel an SCHLEIFE_1 wird ausschliesslich von der eigenen
       3,3-V-Schiene und R20 gemacht. (Galvanische Trennung im strengen
       Sinn ist es NICHT: LED-Kathode und Logik liegen auf derselben
       Masse. Der Gewinn ist die Entkopplung des SIGNALWEGS, nicht die
       Potentialtrennung -- ehrlich benannt.)

    Die Schwellen, gegen die gerechnet wird, sind belegt: der Eingang von
    U6 (SN74LVC1G07, Dok. SCES296AG, Abschnitt 5.3, Zeile "VCC = 3V to
    3.6V") verlangt VIH >= 2,0 V und VIL <= 0,8 V; er ist -- anders als
    der ersetzte 1G06 -- KEIN Schmitt-Trigger (Abschnitt "7.3 Feature
    Description" des 1G07 nennt keine Hysterese-Eigenschaft, selbst
    gelesen), vertraegt die traegen Flanken des Optokopplers (tr/tf typ.
    4/3 us, MAX 18 us -- SHARP D2-A03101EN, "Electro-optical
    Characteristics") also OHNE dieses Netz. Das bleibt trotzdem sicher:
    ein Open-Drain-Ausgang kann in einer undefinierten Uebergangszone
    hoechstens ZUSAETZLICH kurz auf VOL wackeln (Y=L), nie stabil und
    faelschlich auf Y=Z springen -- jedes Wackeln zieht die Sammelleitung
    also hoechstens haeufiger Richtung NOTAUS, nie faelschlich davon weg
    (s. INV_II_MAX-Kommentar oben fuer die volle Herleitung).

    **HIGH-Pegel, Nachweis.** Schleifenstrom im schlechtesten Fall
    (24 V - 10 %, VF der LED beim MAX-Wert 1,4 V, beide Widerstaende
    +1 %):

        IF_min = (21,6 - 1,4) / (2 x 3300 x 1,01) = 3,03 mA

    Damit SCHLEIFE_1 die 2,0 V erreicht, muss der Fototransistor durch
    R20 treiben:

        IC_noetig = 2,0 V / 4,7 kOhm = 0,426 mA   ->  CTR >= 14 %

    Das Datenblatt garantiert IC >= 2,5 mA bei IF = 5 mA (SHARP
    D2-A03101EN, "Electro-optical Characteristics"), also CTR >= 50 %;
    das beschaffte PC817X1 traegt zusaetzlich Rangmarke A (IC 4,0 bis
    8,0 mA bei 5 mA, "Model Line-up"), also CTR >= 80 %. **Ehrlich
    vermerkt:** unser Arbeitspunkt liegt bei 3,0 bis 3,9 mA, nicht bei
    den 5 mA der garantierten Zeile -- fuer 3 mA nennt das Datenblatt
    keinen MIN-Wert, nur eine Kennlinie. Der Sicherheitsschluss haengt
    aber nicht daran: **ein CTR-Mangel faellt in die sichere Richtung.**
    Reicht der Strom nicht, bleibt SCHLEIFE_1 unter VIH, der Kanal meldet
    "offen", die Anlage steht. Ein falsches "in Ordnung" kann daraus
    nicht entstehen. Der unbelegte Bereich kostet Verfuegbarkeit, nie
    Sicherheit.

    **LOW-Pegel, Nachweis.** Bei offener Schleife fliesst durch R20 nur
    noch der Dunkelstrom des Fototransistors (ICEO MAX 100 nA, SHARP
    D2-A03101EN) und der Eingangsstrom von U6 (II MAX +-1 uA,
    SCES296AG 5.5):

        U(SCHLEIFE) <= (0,1 + 1,0) uA x 4,7 kOhm = 5,2 mV

    gegen VIL = 0,8 V -- fast die volle Schwelle als Reserve. R20 ist
    ausserdem bewusst NIEDEROHMIG genug, dass selbst ein
    Firmware-Fehler die Kette nicht aushebelt: schaltete jemand den
    internen Pullup des MCU-Pins ein (uebliche Groessenordnung 30 bis
    50 kOhm -- NICHT aus DS13866 belegt, hier nur als Abschaetzung), laege
    der Knoten bei 3,3 x 4,7/(4,7+30) = 0,45 V und damit immer noch unter
    VIL. Mit einem 10-kOhm-Pulldown waere das nicht mehr sicher der Fall.

    ## Warum nicht Pulldown + vorhandene Diode: die Einschaetzung stimmte nicht

    Der Auftrag ging davon aus, die Aenderung sitze allein zwischen J3 und
    dem lokalen Kanalknoten, und die vorhandene Schottky-Diode (D3/D4)
    ziehe die Sammelleitung weiter mit herunter. An der Sammelleitung
    selbst und an der Gatter-Verriegelung aendert sich tatsaechlich
    nichts (s. `_notaus_verriegelung()` -- R15, U3, R9, U1_NSLEEP sind
    unveraendert). Der KOPPELWEG auf den Bus muss aber trotzdem ersetzt
    werden, und das ist eine Rechnung, keine Geschmacksfrage:

    Der bisherige Kanalknoten wurde von einem SCHALTKONTAKT auf GND
    gezogen -- praktisch 0 Ohm. Ein Pulldown ist das nicht. Der Bus
    haengt im Auslegungsfall an zehn parallelen 10-kOhm-Pullups, also an
    1 kOhm gegen 3,3 V; durch D3 flossen dann rund 2,9 mA. Dieselben
    2,9 mA muessten durch den Pulldown, und der Knoten stuende bei

        R20 = 4,7 kOhm ->  U = 3,3 V x 4,7/(1 + 4,7) = 2,7 V

    -- der Bus wuerde ueberhaupt nicht heruntergezogen. Damit ein
    Pulldown den Bus unter VIL = 0,8 V zoege, muesste er unter etwa
    64 Ohm liegen; einen 64-Ohm-Pulldown wiederum kann kein Optokoppler
    auf 2 V heben (das waeren 31 mA statt 0,43 mA). Pulldown und
    Bustreiber sind in einem Bauteil nicht vereinbar. Genauer: das
    Ruhestromprinzip verlangt, dass ABWESENHEIT von Strom eine AKTIVE
    Aktion ausloest -- das kann kein passives Bauteil, dafuer braucht es
    einen lokal gespeisten Treiber.

    Der ist hier **U6/U7 (SN74LVC1G07, nichtinvertierender Puffer mit
    Open-Drain-Ausgang, SOT-353 wie U3)**: Eingang SCHLEIFE_k, Ausgang
    direkt auf NOTAUS.
    Schleife in Ordnung -> Eingang HIGH -> Ausgang hochohmig, der Bus
    bleibt frei. Schleife offen -> Eingang LOW -> Ausgang zieht den Bus
    auf VOL. Zwei Open-Drain-Ausgaenge duerfen auf denselben Bus
    ("active-low wired-OR", SCES296AG Abschnitt 3 "Description"), die
    zwei Kanaele bleiben also bis auf den Bus hinaus unabhaengig.

    **D3/D4 entfallen dabei ersatzlos, und das ist kein Verlust, sondern
    Gewinn.** Der gezogene Buspegel ist jetzt VOL statt einer
    Diodenspannung:

        I(Bus)  = 10 x (3,3 V - 0,4 V) / 10 kOhm = 2,9 mA
        VOL     <= 0,4 V   (SCES296AG 5.5, MAX-Wert bereits bei
                            IOL = 16 mA und VCC = 3 V; VOL steigt
                            monoton mit IOL, bei 2,9 mA also erst recht)
        Reserve gegen VIL(U3) = 0,8 V:  >= 0,4 V

    -- zahlengleich mit der bisherigen Schottky-Rechnung, die
    Pegelaussage aus Beleg 10 bleibt also unveraendert gueltig. Eine
    Diode IN REIHE zum Open-Drain-Ausgang haette dagegen 0,4 V + 0,4 V =
    0,8 V ergeben, also exakt die Schwelle und null Reserve -- der Grund,
    aus dem D3/D4 nicht bleiben duerfen, sondern gehen muessen. Der
    Ausgang haelt 24 mA (SCES296AG 5.3, VCC = 3 V), die 2,9 mA sind ein
    Achtel davon; er vertraegt am Bus bis 5,5 V (Abschnitt 5.3, "VO 0 bis
    5,5 V").

    Im Ruhezustand (Bus HIGH) leckt jeder Ausgang hoechstens Ioff =
    +-10 uA (SCES296AG 5.5). Zehn Module mit je zwei Ausgaengen und
    einem Gattereingang (II <= 5 uA, SCES217AA 5.5) machen 250 uA gegen
    den auf 1 kOhm parallelgeschalteten Pullup -- 0,25 V Absenkung, der
    Bus bleibt bei 3,05 V und damit weit ueber VIH = 2,0 V.

    **Eine Einschraenkung, die der alte Aufbau nicht hatte:** der
    Schaltkontakt zog den Bus frueher rein passiv herunter, auch ohne
    lokale 3,3 V. Jetzt braucht der Koppelweg die 3,3-V-Schiene dieses
    Moduls. Faellt sie stapelweit aus, ist das folgenlos (dann stirbt
    auch U3, und der interne 100-kOhm-Pulldown des DRV8876 legt den
    Treiber schlafen). Faellt sie NUR auf diesem Modul aus -- ein
    gebrochener 3V3-Pin am Stapelstecker --, dann schlaeft zwar dieses
    Modul, aber der an ihm angeschlossene Not-Halt-Taster erreicht die
    uebrigen Module nicht mehr. Das ist ein echter, wenn auch schmaler
    Rueckschritt und steht so auch in hardware/bauteile-1b.md.

    ## Punkt 2: Kurzschluss der Rueckleitung nach GND

    Liegt J3.2 auf Masse, ist die LED ueberbrueckt: durch R18 fliesst
    kein Strom mehr, IF = 0. SCHLEIFE_1 faellt auf die oben gerechneten
    5,2 mV, U6 zieht den Bus, die Anlage steht -- **die sichere
    Richtung**. Dasselbe gilt fuer einen Kurzschluss der HINLEITUNG
    (J3.1) nach GND: dann liegt der Fusspunkt von R16 auf Masse, durch
    R18/LED fliesst ebenfalls nichts. Der Strom in den Kurzschluss ist in
    beiden Faellen durch R16 begrenzt (Rechnung unter Punkt 4), es
    entsteht kein Schaden.

    ## Punkt 3: Kurzschluss ZWISCHEN den Kanaelen -- was dann noch bleibt

    Ehrlich: hier verliert die Zweikanaligkeit einen Teil ihres Sinns.
    Die Faelle im Einzelnen (A = Hinleitung, B = Rueckleitung):

    * **A1-A2** (beide Hinleitungen): folgenlos. Beide liegen ohnehin
      ueber je 3,3 kOhm auf +24 V; jeder Kanal behaelt seinen eigenen
      Kontakt im Weg.
    * **B1-B2** (beide Rueckleitungen): die zwei LED-Zweige haengen am
      selben Knoten. Ist EIN Kontakt offen und der andere geschlossen,
      speist der geschlossene Kanal beide LEDs -- beide Kanaele melden
      "in Ordnung", obwohl einer offen ist. **Dieser Kanal ist damit
      blind.** Sind BEIDE Kontakte offen (der Normalfall: ein Not-Halt-
      Taster oeffnet beide Kontakte gleichzeitig), faellt der Strom
      trotzdem auf null und die Anlage steht. Der Fehler wirkt also nur
      zusammen mit einem ZWEITEN Fehler (ein klebender Kontakt).
    * **A1-B1, A2-B2** (Hin- auf Rueckleitung DESSELBEN Kanals): der
      Kontakt ist ueberbrueckt, der Kanal meldet dauerhaft "in Ordnung".
      Genau das ist auch die absichtliche Bruecke fuer einen unbenutzten
      Kanal (Punkt 5) -- die Schaltung kann Absicht und Fehler nicht
      unterscheiden.
    * **A1-B2, A2-B1** (ueber Kreuz): der fremde Vorwiderstand speist die
      LED des anderen Kanals an dessen Kontakt vorbei; dieser Kanal ist
      blind, der andere bleibt heil.
    * **Rueckleitung an +24 V** (kein Querschluss, aber dieselbe
      Wirkung): ueberbrueckt den Kontakt dieses Kanals ebenfalls.

    Was die Schaltung nach einem solchen Fehler noch leistet: **den
    jeweils anderen Kanal.** Ein Querschluss macht hoechstens EINEN Kanal
    blind; der zweite loest weiterhin aus. Was sie NICHT leistet: sie
    ERKENNT den Querschluss nicht von sich aus. Dafuer braeuchte es
    getaktete Pruefimpulse auf den zwei Kreisen (OSSD-Prinzip) oder ein
    Sicherheitsrelais -- beides ist hier bewusst nicht gebaut. Was der
    Aufbau dafuer moeglich macht: beide Kanaele haengen einzeln am
    Modul-MCU (U100 Pin 3 und Pin 14). Die Firmware kann eine
    Diskrepanzueberwachung fuehren -- melden zwei Kanaele laenger als
    ein paar hundert Millisekunden Verschiedenes, ist einer defekt --
    und den Betrieb sperren. Das ist Software, nicht Hardware, und es
    steht hier als Auftrag an die Firmware, nicht als erledigt.

    Konstruktiv abgemildert, nicht beseitigt: die zwei Kreise gehoeren in
    getrennt gefuehrte Leitungen (nicht in dieselbe Ader eines
    gemeinsamen Mantels), damit eine einzelne mechanische Beschaedigung
    nicht beide trifft. Das ist eine Verlege-Auflage fuer den Aufbau im
    Museum.

    ## Punkt 4: Strombegrenzung nach aussen

    Jede der vier herausgefuehrten Adern liegt hinter mindestens
    3,3 kOhm. Der groesste Strom, den ein Kurzschluss von aussen
    hervorrufen kann, ist damit

        I_max = 26,4 V / 3,3 kOhm = **8,0 mA**

    (26,4 V = 24 V + 10 %). Die groesste Verlustleistung in einem
    einzelnen Widerstand betraegt dabei

        P_max = 26,4 V^2 / 3,3 kOhm = **0,211 W**  (84 % von 0,25 W)

    gegen die 250 mW des gewaehlten 1206-Typs (UNI-ROYAL
    1206W4F3301T5E, LCSC C26032, Produktseite gesichtet). Im
    Normalbetrieb sind es 3,3 kOhm x (3,9 mA)^2 = 0,050 W, also 20 %.
    **Deshalb 1206 und nicht 0805:** ein 0805 (125 mW) waere im
    Kurzschlussfall um 70 % ueberlastet. Auch die maximale
    Arbeitsspannung des Typs (200 V) ist gegenueber 26,4 V unkritisch.
    Die 84 % gelten fuer den Nennwert bei bis zu 70 C Umgebungstemperatur;
    ein DAUERKURZSCHLUSS in einem heissen Gehaeuse muesste derated werden
    -- deshalb ist der Wert genannt und nicht bloss "passt".

    Beide Widerstaende eines Kanals sind absichtlich gleich gross: der
    Kurzschluss einer beliebigen Ader gegen GND ODER gegen +24 V bleibt
    dann in JEDEM Fall unter den 8,0 mA und unter der Nennleistung, und
    der LED-Strom bleibt in jedem dieser Faelle unter 8 mA und damit weit
    unter den 50 mA Grenzstrom des PC817 (SHARP D2-A03101EN, "Absolute
    Maximum Ratings"). Der Preis dafuer: der Betriebsstrom von 3,0 bis
    3,9 mA liegt unter den 5 mA der garantierten CTR-Zeile -- die
    Abwaegung dazu steht oben unter Punkt 1.

    ## Punkt 5: der unbenutzte Kanal

    Wird nur EIN Not-Halt-Kreis angeschlossen, haengt der zweite Kanal
    offen und meldet dauerhaft Notaus -- die Anlage laeuft nicht an. Das
    ist die richtige Vorgabe (offen = sicher), aber der Nutzer muss
    wissen, was zu tun ist:

        **Unbenutzten Kanal am Stecker bruecken:
         Kanal 1 = J3 Pin 1+2, Kanal 2 = J3 Pin 3+4.**

    J3 ist eine 2,54-mm-Stiftleiste, die zwei Pins eines Kanals liegen
    deshalb absichtlich NEBENEINANDER: eine handelsuebliche
    Jumper-Bruecke genuegt. Der Hinweis steht als Text im Schaltplan
    (s. unten) und als Bestueckungs-/Siebdruck-Auflage in
    hardware/bauteile-1b.md; im Layout (Aufgabe 7) gehoert er auf den
    Siebdruck neben J3.

    ## J3: vier Pole -- und genau darin liegt eine Falle

    Zwei Adern je Kanal, zwei Kanaele: **J3 bleibt vierpolig.** Er hatte
    vorher auch vier Pole (zwei Signale, zwei GND) -- gleiche Bauform,
    gleiche Polzahl, voellig andere Bedeutung. Ein altes Kabel passt
    mechanisch weiterhin. Steckt man es, liegt der alte Schliesser
    zwischen Pin 1 und Pin 2, also im Weg von Kanal 1: geoeffnet (der
    Normalzustand des alten Tasters) heisst jetzt "Notaus", und
    Kanal 2 haengt offen. Das Exponat stuende dauerhaft still --
    unangenehm, aber sicher. Umgekehrt waere es gefaehrlich, und genau
    das kann nicht passieren, weil der alte Kontakt im gedrueckten
    Zustand schliesst und damit "in Ordnung" melden wuerde -- also die
    verkehrte Richtung, die ein Nutzer sofort bemerkt (Anlage laeuft nur,
    solange der Not-Halt gedrueckt ist). Trotzdem gilt: **die bestehende
    Verkabelung des Peche-aux-Canards-Exponats MUSS beim Umstieg
    umgeklemmt werden** (Oeffnerkontakt statt Schliesser, zwei Adern je
    Kanal statt Signal+GND). Steht so in hardware/bauteile-1b.md.
    """
    sch.bauteil("J3", "Connector:Conn_01x04_Pin", (ox, oy),
                "Notaus-Ruhestrom", FP_HDR_1X04, rot=180,
                roff=(7.62, -10.16), voff=(7.62, -12.7))
    sch.netz("J3", "1", "R", "KREIS1_A")   # Hinleitung Kanal 1
    sch.netz("J3", "2", "R", "KREIS1_B")   # Rueckleitung Kanal 1
    sch.netz("J3", "3", "R", "KREIS2_A")   # Hinleitung Kanal 2
    sch.netz("J3", "4", "R", "KREIS2_B")   # Rueckleitung Kanal 2

    sch.text(ox - 12.7, oy - 30.48,
             "J3 = Notaus, Ruhestrom (OEFFNER): Kanal 1 = Pin 1+2, "
             "Kanal 2 = Pin 3+4.", size=2.0, bold=True)
    sch.text(ox - 12.7, oy - 25.4,
             "UNBENUTZTEN KANAL BRUECKEN (Jumper 2,54 mm) -- sonst meldet "
             "er dauerhaft Notaus.", size=2.0, bold=True)
    sch.text(ox - 12.7, oy - 20.32,
             "ALTE VERKABELUNG (Schliesser gegen GND) NICHT "
             "weiterverwenden: umklemmen.", size=2.0, bold=True)

    for kanal, (r_hin, r_rueck, opto, r_pd, inv, c_ab, dy) in enumerate((
            ("R16", "R18", "U4", "R20", "U6", "C15", 25.4),
            ("R17", "R19", "U5", "R21", "U7", "C16", -25.4)), start=1):
        a = "KREIS%d_A" % kanal
        b = "KREIS%d_B" % kanal
        led = "%s_LED_A" % opto
        knoten = "SCHLEIFE_%d" % kanal
        y = oy + dy

        # R16/R17: Vorwiderstand auf der HINLEITUNG. Er allein sieht den
        # vollen Rail-Kurzschluss (s. Punkt 4) -- deshalb 1206.
        sch.bauteil(r_hin, "Device:R", (ox + 25.4, y), R_SCHLEIFE_WERT,
                    FP_R1206, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
        sch.netz(r_hin, "1", "U", "+24V")
        sch.netz(r_hin, "2", "D", a)

        # R18/R19: zweiter Vorwiderstand auf der RUECKLEITUNG, vor der
        # LED. Gleich gross wie R16 -- damit auch ein Kurzschluss der
        # Rueckleitung gegen +24V strombegrenzt bleibt.
        sch.bauteil(r_rueck, "Device:R", (ox + 50.8, y), R_SCHLEIFE_WERT,
                    FP_R1206, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
        sch.netz(r_rueck, "1", "U", b)
        sch.netz(r_rueck, "2", "D", led)

        # U4/U5: Optokoppler. Kollektor an 3V3, Emitter auf den
        # Schleifenknoten -- Emitterfolger: hier soll ein GESCHLOSSENER
        # Kreis HIGH ergeben, kein LOW. (Der frueher hier genannte
        # Vergleich mit U2 ist entfallen -- den Sensoreingang gibt es
        # seit Aufgabe 5f nicht mehr, s. Moduldoku Punkt 6.)
        # Footprint: FP_PC817, die Landflaeche aus dem Sharp-Datenblatt.
        # Bis Aufgabe 5f stand hier derselbe zu kleine SOP-4-Platzhalter
        # wie bei U2 -- die Pads lagen neben den Anschluessen.
        sch.bauteil(opto, "Isolator:PC817", (ox + 76.2, y), OPTO_WERT,
                    FP_PC817, rot=0, roff=(-7.62, 12.7), voff=(-7.62, 15.24))
        sch.netz(opto, "1", "L", led)      # Anode
        sch.netz(opto, "2", "L", "GND")    # Kathode
        sch.netz(opto, "3", "R", knoten)   # Emitter -> Schleifenknoten
        sch.netz(opto, "4", "R", "3V3")    # Kollektor

        # R20/R21: der Pulldown, der aus "kein Strom" ein LOW macht.
        sch.bauteil(r_pd, "Device:R", (ox + 101.6, y), R_PULLDOWN_WERT,
                    FP_R0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
        sch.netz(r_pd, "1", "U", knoten)
        sch.netz(r_pd, "2", "D", "GND")

        # U6/U7: nichtinvertierender Puffer mit Open-Drain-Ausgang
        # (ERSETZT 2026-09-08 den 1G06, s. INVERTER_WERT-
        # Kommentar). Schleife offen (LOW) -> Ausgang zieht die
        # Sammelleitung. Pin 1 (NC) fuehrt das 1G07-Symbol ANDERS als
        # das ersetzte 1G06-Symbol SEHR WOHL (Typ "free", eigene
        # Pruefung von 74xGxx.kicad_sym, s. FOOTPRINT_PAD_OHNE_PIN-
        # Kommentar) -- deshalb ausdruecklich `sch.nc()`, sonst meldet
        # `selbstpruefung()` "haengt in der Luft".
        sch.bauteil(inv, "74xGxx:74LVC1G07", (ox + 127.0, y),
                    INVERTER_WERT, FP_SOT353, rot=0,
                    roff=(-15.24, 12.7), voff=(-15.24, 15.24),
                    felder={"LCSC": "C7830"})
        sch.nc(inv, "1")
        sch.netz(inv, "2", "L", knoten)             # A
        sch.netz(inv, "3", "D", "GND")
        sch.netz(inv, "4", "R", netze["NOTAUS"])     # Y, open drain
        sch.netz(inv, "5", "U", "3V3")

        sch.bauteil(c_ab, "Device:C", (ox + 152.4, y), C_INV_WERT,
                    FP_C0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
        sch.netz(c_ab, "1", "U", "3V3")
        sch.netz(c_ab, "2", "D", "GND")


def _notaus_verriegelung(sch, ox, oy, netze):
    """Die Hardware-Verriegelung aus Punkt 4 des Auftrags: U3, C14, R15.

    Diese Funktion ist von der Ruhestrom-Umstellung (Aufgabe 5d)
    UNBERUEHRT geblieben -- absichtlich, und nachgeprueft: an der
    Sammelleitung NOTAUS (wired-OR, Pullup R15, LOW = Notaus) und an der
    Verriegelung selbst aendert sich kein Bauteil und keine Zahl. Was
    sich geaendert hat, sitzt ausschliesslich davor, zwischen J3 und der
    Sammelleitung -- s. `_notaus_schleifen()`. Dort steht auch, warum die
    bisherigen Koppeldioden D3/D4 dabei ersatzlos entfallen und was an
    die Stelle des frueheren Schaltkontakts tritt.

    U3 (SN74LVC1G08, UND-Gatter) bildet die eigentliche Verriegelung:

        U1_NSLEEP (an U1 Pin 3) = NSLEEP_GATTER (vom MCU ueber R9)
                                  UND  NOTAUS (Sammelleitung)

    Der Gatterausgang ist eine Gegentaktstufe: er gibt VOL <= 0,1 V
    bzw. VOH >= VCC-0,15 V ab (SCES217AA, Abschnitt 5.5, jeweils bei
    100 uA Laststrom -- der DRV8876-nSLEEP-Pin zieht ueber seinen
    internen 100-kOhm-Pulldown hoechstens 33 uA, liegt also mit
    grossem Abstand innerhalb dieser Bedingung). Damit gilt:

      * NOTAUS gezogen -> U1 Pin 3 <= 0,1 V, VIL des DRV8876 waere
        0,8 V (SLVSDS7B, Abschnitt 6.5): 0,7 V Reserve. Der Treiber
        geht in "an ultra-low power mode" und legt alle Ausgaenge in
        Hi-Z -- EGAL, was der Modul-MCU treibt oder ob er noch lebt.
      * Normalbetrieb -> U1 Pin 3 >= 3,15 V, VIH waere 1,5 V:
        1,65 V Reserve.
      * MCU LOW -> Ausgang LOW: der MCU behaelt seine Schlafsteuerung.
      * Der MCU-GPIO speist nichts mehr in die Verriegelung ein: ein
        CMOS-Gattereingang zieht II <= +-5 uA (SCES217AA, 5.5).

    ## Warum NICHT die urspruengliche Diodenklemme (D2 + R14)

    Die erste Fassung dieser Datei loeste die Verriegelung mit einer
    Diode D2 von NSLEEP nach NOTAUS und einem Vorwiderstand R14 (1 kOhm)
    davor. Sie hat NICHT gewirkt, aus zwei voneinander unabhaengigen
    Gruenden -- beide sind reine Pegelrechnungen, beide sind in
    tests/test_motormodul.py als Gegenprobe hinterlegt:

    1. **R14 macht aus der Klemme einen Spannungsteiler.** Der alte
       Kommentar rechnete nur den FEHLSTROM aus ((3,3-0,6)/1100 =~
       2,4 mA, unbedenklich fuer den GPIO), nicht die SPANNUNG am Pin.
       Mit R9 = 100 Ohm gegen 3,3 V und R14 = 1 kOhm plus Diode gegen
       0 V steht der Knoten bei

           U = 0,6 V + 2,4 mA x 1 kOhm =~ 3,05 V

       -- weit ueber VIL = 0,8 V. Genau der Widerstand, der den GPIO
       schuetzen sollte, verhinderte die Wirkung. Schutz und Wirkung
       schlossen sich in dieser Anordnung aus.

    2. **Auch ohne R14 stehen ZWEI Diodenspannungen in Reihe.** Der Bus
       ging damals nicht auf 0 V: er wurde ueber D3/D4 gegen den
       Schaltkontakt heruntergezogen, lag also selbst eine
       Durchlassspannung ueber Masse. Eine zweite Diode D2 vom
       nSLEEP-Pin auf diesen Bus haette den Pin auf VF(D3) + VF(D2)
       gehoben -- mit 1N4148W rund 1,0 bis 1,3 V, also ebenfalls ueber
       VIL = 0,8 V. Selbst mit Schottky-Dioden auf BEIDEN Wegen blieben
       im Grenzfall (2 x 400 mV bei 10 mA, Vishay 86408) genau 0,8 V
       uebrig -- null Reserve. Eine passive Dioden-UND-Verknuepfung kann
       diese Schwelle in dieser Topologie nicht sicher einhalten; ein
       Gatter kann es.

    Beide Gegenproben bleiben im Test stehen, obwohl D3/D4 inzwischen
    entfallen sind: sie beschreiben den Weg, den ein kuenftiges
    Fremdmodul mit passiver Diodenkopplung gehen wuerde, und begruenden,
    warum die Verriegelung ein Gatter bleiben muss.

    R15 (10k, NOTAUS -> 3V3) ist der Pullup, der der Sammelleitung
    ueberhaupt einen definierten Ruhepegel gibt -- ohne ihn waere HIGH
    (= "kein Notaus") nicht garantiert, sondern nur "nicht aktiv
    heruntergezogen", was bei einem wired-OR-Bus dasselbe wie
    "unbestimmt" ist. Weder modulsockel.py noch sockelplatine.py legen
    bisher einen Pullup auf NOTAUS -- eine Luecke, die hier fuer das
    erste tatsaechlich gebaute Modul geschlossen wird (mehrere Module
    duerfen denselben schwachen Pullup parallel tragen, das ist bei
    einem wired-OR-Bus ueblich und schadet nicht, es erhoeht nur
    geringfuegig den Ruhestrom). 10 kOhm bleibt bewusst stehen und wird
    NICHT vergroessert: bei zehn Modulen parallel bleibt der Bus-Pullup
    bei 1 kOhm, und die Leckstroeme der Open-Drain-Ausgaenge (Ioff <=
    10 uA, SCES296AG 5.5) und Gattereingaenge (<= 5 uA) senken den
    Ruhepegel damit nur um 0,25 V -- der Bus bleibt sicher ueber
    VIH = 2,0 V.

    Das DRV8876-nSLEEP-Pin traegt zusaetzlich einen eigenen internen
    Pulldown (SLVSDS7B, Abschnitt 6.5, "RPD Input pulldown resistance
    ... 100 kOhm"): faellt die 3,3-V-Schiene aus, geht auch der
    Gatterausgang mit, und der Treiber schlaeft von sich aus. Die
    Ausfallrichtung des Gatters ist damit die sichere.
    """
    # U3: das Verriegelungsgatter. A = NSLEEP_GATTER (vom Modul-MCU ueber
    # R9), B = NOTAUS (Sammelleitung), Y = U1_NSLEEP (an U1 Pin 3).
    # Pinbelegung wie U103 in modulsockel.py (1=A, 2=B, 3=GND, 4=Y,
    # 5=VCC). Der Platz ist bewusst so gewaehlt, dass keine Stichleitung
    # auf der Spalte x = ox_treiber-40,64 endet, auf der R7..R10 sitzen --
    # dort verschmolzen in dieser Aufgabe schon einmal zwei Netze.
    sch.bauteil("U3", "74xGxx:74LVC1G08", (ox + 35.56, oy + 40.64),
                "SN74LVC1G08", FP_SOT353, rot=0,
                roff=(-15.24, 12.7), voff=(-15.24, 15.24))
    sch.netz("U3", "1", "L", "NSLEEP_GATTER")     # A  <- MCU ueber R9
    sch.netz("U3", "2", "L", netze["NOTAUS"])      # B  <- Sammelleitung
    sch.netz("U3", "3", "D", "GND")
    sch.netz("U3", "4", "R", "U1_NSLEEP")          # Y  -> DRV8876 Pin 3
    sch.netz("U3", "5", "U", "3V3")

    # C14: Abblockkondensator fuer U3, wie ihn jedes Logik-IC braucht.
    sch.bauteil("C14", "Device:C", (ox + 68.58, oy + 40.64), C14_WERT,
                FP_C0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C14", "1", "U", "3V3")
    sch.netz("C14", "2", "D", "GND")

    sch.bauteil("R15", "Device:R", (ox + 76.2, oy + 15.24), R15_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R15", "1", "U", "3V3")
    sch.netz("R15", "2", "D", netze["NOTAUS"])


def bauen(sch, ox, oy):
    """Baut das Motormodul bei (ox, oy) in `sch` ein: Modulsockel-Block
    (MCU, Flipflop, Gatter, Kennwiderstaende, alle Stecker, Randpads)
    plus die DRV8876-Endstufe aus dem Muttern-Board plus die
    Versorgungszelle (Task 5, ersetzt den alten Q1-Strang)."""
    _load_libs(sch)

    # Zwei der neun "freien" U100-Pins (modulsockel.ZUSATZ_PIN_RICHTUNG)
    # tragen hier echte Aufgaben -- Pin "2" (PC14) und Pin "15" (PA8)
    # bleiben frei/nc. PC14 trug bis Aufgabe 5f den Ausgang des
    # Sensor-Optokopplers U2; mit dem Sensoreingang (Moduldoku Punkt 6)
    # ist er wieder frei geworden. frei_durchreichen=True (NEU, Task 5):
    # das Motormodul ist ein v2-Modul und traegt die Randpads (J95/J96,
    # s. modulsockel.randpads() unten) -- ohne frei_durchreichen=True
    # legte _stapelstecker() die freien GPIO auf no_connect, und die
    # Randpads-Labels haetten kein Gegenstueck (Leerlauf-Loetpad).
    # motorsignale=True (NEU, Fix-Runde 1 zu Task 6, 2026-09-08): das
    # Motormodul ist der einzige Aufrufer, der die DRV8876-Motorsignale
    # (IN1/IN2/NSLEEP/NFAULT/IPROPI auf PA2..PA6, Pin 9-13) tatsaechlich
    # braucht -- vorher verdrahtete modulsockel.einbauen() diese fuenf
    # Pins UNBEDINGT fuer JEDES Modul (auch den Dimmer, der sie nie
    # benutzte); seit der Fix-Runde muss ein Modul sie explizit
    # anfordern. Diese Zeile ist die einzige Aenderung, die die
    # generierte Netzliste dieses Moduls unveraendert laesst (Pin 9-13
    # tragen exakt dieselben Netznamen wie vorher) -- s.
    # task-6-report.md, Abschnitt "Motormodul-Regressionsnachweis".
    netze = modulsockel.einbauen(sch, ox, oy, mit_flipflop=True,
                                  frei_durchreichen=True, motorsignale=True,
                                  zusatz_pins={
        # PC15/PA7: die zwei Schleifenknoten der Notaus-Kanaele. Seit der
        # Ruhestrom-Umstellung (Aufgabe 5d) heissen sie SCHLEIFE_1/2 statt
        # NOTAUS_1/2 -- die PEGELbedeutung ist dieselbe geblieben (LOW =
        # dieser Kanal meldet Notaus), die KONTAKTbedeutung hat sich
        # umgekehrt. Der neue Name zwingt jede alte Firmware- und
        # Dokumentationsstelle, sich zu melden.
        "3": "SCHLEIFE_1",    # PC15 -- Kanal 1 (J3 Pin 1/2)
        "14": "SCHLEIFE_2",   # PA7  -- Kanal 2 (J3 Pin 3/4)
    })
    # J95/J96: die 22 unbestueckten Randpads (stack_spec.RANDPADS, v2) --
    # jedes v2-Modul traegt sie (Aufgabenbrief Task 5). Unabhaengig von
    # einbauen() (s. modulsockel.randpads()-Docstring); die Netznamen
    # (GP.., 3V3, GND) treffen sich mit den frei_durchreichen=True oben
    # gelegten Labels an J100/J105 ausschliesslich ueber den gemeinsamen
    # Namen, nicht ueber einen gemeinsamen Draht.
    modulsockel.randpads(sch)

    # Gatter-Abblockung des Modulsockel-Blocks (Task 6b, s. dortiger
    # Docstring) -- dieselbe Ergaenzung, die Task 6 fuer das
    # Dimmermodul gemacht hat. `ox`/`oy` sind hier die UNVERAENDERTEN
    # Koordinaten, die zwei Zeilen oberhalb auch an modulsockel.
    # einbauen() gehen.
    _gatter_abblockung_sockel(sch, ox, oy)

    # PWR_FLAG auf "+24V" und "VCP": beide haben nur "power_in"/"passive"-
    # Pins, keinen einzigen "power_out" -- ohne ein power_out-Pin
    # irgendwo im Netz meldet kicad-cli sch erc "Input Power pin not
    # driven" (eigene Messung, s. Testschritt). "+24V" wird jetzt von
    # Q90 (versorgung.py) gespeist, aber ein MOSFET-Source ist elektrisch
    # kein "power_out"-Pin (Symboltyp "passive"); "VCP" erzeugt der
    # DRV8876 intern per Ladungspumpe -- das weiss die ERC nicht, ihr
    # Symbol fuehrt VCP als gewoehnlichen "power_in". Dasselbe Muster
    # wie modulsockel.py (#FLG101/#FLG102 fuer GND/3V3) und
    # sockelplatine.py (#FLG1 fuer PWR24V), hier unter eigenen
    # Referenzen, damit nichts mit deren #FLG101/#FLG102/#FLG1 (oder mit
    # versorgung.py's eigenem #FLG90 auf PWR_IN) kollidiert.
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")
    sch.bauteil("#FLG201", "power:PWR_FLAG", (ox + 279.4, oy + 83.82), "PWR_FLAG", "")
    sch.netz("#FLG201", "1", "D", "+24V")
    sch.bauteil("#FLG202", "power:PWR_FLAG", (ox + 279.4, oy + 91.44), "PWR_FLAG", "")
    sch.netz("#FLG202", "1", "D", "VCP")

    # Versorgungszelle (Task 5, ersetzt Q1/R11/R12/D1/C12, s. Kommentar
    # vor `_stapel_speist_lokal()` oben): eigener, weit abgesetzter
    # Streifen unterhalb aller anderen Bloecke (die reichen hoechstens
    # bis y =~ oy+205, s. _notaus_schleifen() unten) -- geprueft per
    # kicad-cli sch erc (0 Fehler, 0 Warnungen), nicht bloss angenommen.
    versorgung.bauen(sch, ox + 60.96, oy + 228.6)
    # Bindet die geschuetzte lokale Schiene "+24V" (hinter Q90) an die
    # Stapel-Sammelschiene "PWR24V" (an J103/J104) -- s. Docstring dort.
    _stapel_speist_lokal(sch, ox + 320.04, oy + 228.6)

    _endstufe_treiber(sch, ox + 431.8, oy + 12.7, netze)
    _motor_out(sch, ox + 431.8, oy - 63.5)
    _notaus_verriegelung(sch, ox + 330.2, oy + 63.5, netze)
    # Eigener, weit abgesetzter Streifen: der Ruhestrom-Eingang bringt
    # zwoelf Bauteile mit, und die Stichleitungen der bestehenden Bloecke
    # reichen bis y =~ 104 (U3/C14). y = 165,1 +- 25,4 liegt darueber und
    # kollidiert mit nichts -- geprueft per kicad-cli sch erc (0 Fehler,
    # 0 Warnungen), nicht bloss angenommen.
    _notaus_schleifen(sch, ox + 330.2, oy + 165.1, netze)


# ------------------------------------------------------- Erzeugen
# Projektname, Titel, Datum und Zielpfad stehen hier als Konstanten und
# nicht mehr im __main__-Block: tests/test_erzeugte_dateien.py muss den
# Schaltplan mit GENAU denselben Angaben nachbauen koennen, um ihn gegen
# die eingecheckte Datei zu halten. Stuenden sie im __main__, muesste der
# Test sie abschreiben -- und zwei Kopien derselben Angabe laufen
# auseinander, ohne dass es jemand merkt. Genau daran ist die
# eingecheckte Datei schon einmal veraltet (s. Test).
PROJEKT = "Motormodul"
TITEL = "Motormodul"
DATUM = "2026-08-31"
ZIEL = os.path.join(HERE, "..", "..", "hardware", "kicad", "motor",
                    "Motormodul.kicad_sch")


def erzeugen(ziel=None):
    """Baut den Schaltplan und schreibt ihn nach `ziel` (Vorgabe: ZIEL)."""
    import gen

    # A2 quer und ein Ursprung, der den Inhalt (516 x 278 mm, von
    # x=-20/y=-70 aus gebaut) mittig aufs Blatt legt: auf A3 lief der
    # Plan an drei Seiten ueber den Rand. Raster 1,27 mm einhalten.
    sch = gen.Schaltplan(PROJEKT, TITEL, DATUM, papier="A2")
    bauen(sch, 60.96, 139.7)
    return sch.schreiben(ZIEL if ziel is None else ziel)


if __name__ == "__main__":
    print("keine unverbundenen Pins -- geschrieben:", erzeugen())

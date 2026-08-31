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
unten bei `_notaus_verriegelung()` im Detail; hier die Kurzfassung: die
Endstufe wird ueber das DRV8876-eigene nSLEEP-Pin abgeschaltet (ein
echter Hardware-Steuereingang des Treibers, kein Software-Zustand). Die
Verriegelung ist ein UND-Gatter (U3, SN74LVC1G08):

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
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S    # noqa: E402
import modulsockel         # noqa: E402

# -------------------------------------------------------------- Footprints
FP_R0805 = modulsockel.FP_R0805
FP_C0805 = modulsockel.FP_C0805
FP_HDR_1X04 = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
FP_CP_RADIAL = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"          # Aufgabenbrief 4, woertlich
FP_TVS_SMC = "Diode_SMD:D_SMC_Handsoldering"                      # Aufgabenbrief 4, woertlich
FP_SOD123 = "Diode_SMD:D_SOD-123"                                 # BAT54W (D3/D4)
FP_TO252 = "Package_TO_SOT_SMD:TO-252-3_TabPin2"                  # Q1, aus dem Altprojekt
FP_SOP4 = "Package_SO:SOP-4_3.8x4.1mm_P2.54mm"                    # U2 (PC817), aus dem Altprojekt
FP_SOT353 = modulsockel.FP_SOT353                                 # U3 (SN74LVC1G08), wie U103
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
# LCSC C395868, hardware/bauteile-1b.md); J2 (Sensor, 3-polig) den
# 3-poligen Bruder DB128L-5.08-3P-GN-S (LCSC C395869, ebenfalls
# hardware/bauteile-1b.md, Beleg 5).
FP_KLEMME_2 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal"
FP_KLEMME_3 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-3-5.08_1x03_P5.08mm_Horizontal"

# ------------------------------------------------------- Bauteilwerte
# Aus dem Altprojekt uebernommen (Netzliste `kicad-cli sch export
# netlist` gegen Unmögliche_Muttern.kicad_sch tatsaechlich gelesen, nicht
# aus dem Gedaechtnis): D1/C9/C10/C11/C12/C13/R6/R7/R8/R9/R10/R11/R12/R13.
D1_WERT = "SMCJ30A"      # TVS, unidirektional -- LCSC C340696 (bereits in
# sockelplatine.py geprueft und zitiert, dasselbe Bauteil, hier nur
# wiederverwendet, nicht neu recherchiert).
C12_WERT = "220u"        # 24-V-Stuetzkondensator, radial, polarisiert
C9_WERT = "0.1u"         # VCP-Kondensator (VM<->VCP, DRV8876-Ladungspumpe)
C10_WERT = "0.022u"      # Ladungspumpen-Kondensator CPH<->CPL
C11_WERT = "0.1u"        # zweiter 24-V-Abblock-Kondensator (neben C9-Anteil)
C13_WERT = "0.1u"        # IPROPI-Filterkondensator gegen GND
R6_WERT = "2.2k"         # Vorwiderstand Sensor-Eingang -> U2 (PC817) LED
R7_WERT = "0.1k"         # Vorwiderstand MCU -> U1 EN/IN1
R8_WERT = "0.1k"         # Vorwiderstand MCU -> U1 PH/IN2
R9_WERT = "0.1k"         # Vorwiderstand MCU -> U1 NSLEEP
R10_WERT = "4.7k"        # IPROPI/GND, NICHT bestueckt (dnp=True), unveraendert
R11_WERT = "10k"         # Q1 Gate<->Source (Reverse-Polarity-Schutz)
R12_WERT = "10k"         # Q1 Gate<->GND (schaltet Q1 im Normalfall durch)
R13_WERT = "10k"         # NFAULT-Pullup an 3V3
# R5 NEU gerechnet fuer diese Aufgabe (s. Moduldoku oben, Punkt 1) --
# NICHT der Altprojekt-Wert (2,2k, dort zu klein fuer den 2-A-Motor).
R5_WERT = "1.3k"         # ITRIP ~= 2,538 A bei VVREF=3,3V, AIPROPI=1000uA/A

# ---------------------------------------------- NOTAUS-Verriegelung (neu)
# Kein Gegenstueck im Altprojekt -- dort sass der Pico selbst auf den
# Notaus-Eingaengen, ein Verriegelungspfad ohne MCU war dort nicht
# gefordert.
#
# D3/D4 koppeln die zwei lokalen Schaltkontakte auf die
# NOTAUS-Sammelleitung. Sie sind SCHOTTKY-Dioden, nicht (wie zuerst
# gebaut) 1N4148W -- Begruendung in `_notaus_verriegelung()`: der
# gezogene Ruhepegel des Busses IST die Durchlassspannung dieser Diode,
# und die eines 1N4148W ist bei den hier fliessenden Stroemen nicht
# nachweisbar unterhalb der 0,8-V-VIL-Schwelle der Bauteile, die am Bus
# haengen. Bauteil: BAT54W (SOD-123), LCSC C699107 -- Produktseite
# tatsaechlich gesichtet: `lcsc.com/product-detail/Schottky-Barrier-
# Diodes-SBD_Yangzhou-Yangjie-Elec-Tech-BAT54W_C699107.html` (Rohdaten:
# Hersteller YANGJIE, Gehaeuse "SOD-123", 30 V, 200 mA, Leckstrom
# "2uA@25V").
D_KOPPEL_WERT = "BAT54W"
R15_WERT = "10k"         # Pullup NOTAUS-Sammelleitung an 3V3, s. dort
C14_WERT = "0.1u"        # Abblockkondensator U3 (Verriegelungsgatter)

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

# BAT54W (D3/D4), Vishay-Datenblatt Dok. 86408, Rev. 1.0 vom 20-Nov-2023,
# Tabelle "ELECTRICAL CHARACTERISTICS" (Tamb = 25 C): VF MAX 240 mV bei
# 0,1 mA, 320 mV bei 1 mA, 400 mV bei 10 mA; IR MAX 2 uA bei VR = 25 V.
SCHOTTKY_VF_MAX_1MA = 0.32      # V
SCHOTTKY_VF_MAX_10MA = 0.40     # V
SCHOTTKY_IR_MAX = 2e-6          # A bei VR = 25 V

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


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C", "Device.kicad_sym", "C")
    sch.lib("Device:C_Polarized", "Device.kicad_sym", "C_Polarized")
    sch.lib("Device:D", "Device.kicad_sym", "D")
    sch.lib("Device:D_Zener", "Device.kicad_sym", "D_Zener")
    sch.lib_extends("Transistor_FET:IRF4905", "Transistor_FET.kicad_sym",
                     "IRF9540N", "IRF4905")
    sch.lib("Isolator:PC817", "Isolator.kicad_sym", "PC817")
    # U3: dasselbe Gatter-Bauteil wie U103 im Modulsockel (SN74LVC1G08,
    # SOT-353) -- keine neue Bauteilnummer noetig, LCSC C7832 ist in
    # hardware/bauteile-1b.md bereits auf der Produktseite geprueft.
    sch.lib("74xGxx:74LVC1G08", "74xGxx.kicad_sym", "74LVC1G08")
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


def _endstufe_leistung(sch, ox, oy):
    """D1 (TVS), C12 (Stuetzkondensator), Q1+R11/R12 (Verpolungsschutz).

    PWR24V erreicht dieses Modul NICHT ueber eine eigene Schraubklemme
    (anders als im Altprojekt, dort J1) -- der Stapel hat dafuer bereits
    einen eigenen Leistungsstecker (J103/J104, modulsockel.py,
    `_leistungsstecker()`), den `modulsockel.einbauen()` in JEDEM Modul
    unbedingt anlegt und auf das Netz "PWR24V" legt. Eine zusaetzliche
    Klemme J1 waere ein zweiter, redundanter 24-V-Eingang auf demselben
    Modul -- dafuer nennt weder der Vertrag noch das Design-Dokument
    einen Zweck, und der Aufgabenbrief fuer das PCB-Layout (Aufgabe 7,
    Schritt 5) prueft die Leistungsbahnen ausdruecklich unter den
    Netznamen "+24V"/"Out1"/"Out2" -- also GENAU die Namen, die diese
    Datei fuer die LOKALE, geschuetzte Schiene hinter Q1 verwendet, nicht
    "PWR24V". Der Verpolungsschutz (Q1/R11/R12, unveraendert aus dem
    Altprojekt uebernommen) sitzt deshalb zwischen dem Stapel-Netz
    "PWR24V" (Quelle, ueber J103/J104) und der lokalen, geschuetzten
    Schiene "+24V" (Verbraucher: D1, C12, U1 VM, J2 Pin 1) -- dieselbe
    Funktion wie im Altprojekt (schuetzt vor Verpolung), nur an der
    Schnittstelle zum Stapelstecker statt an einer eigenen Schraubklemme.
    Das schuetzt sogar zusaetzlich vor einem falsch gesteckten
    Stapelstecker, nicht nur vor einer falsch verdrahteten Klemme.
    """
    # Q1: P-MOSFET, Source an PWR24V (vom Stapel), Drain an +24V (lokal,
    # geschuetzt), Gate ueber R11 an Source / R12 an GND -- unveraendert
    # aus dem Altprojekt (dort R11/R12 = 10k/10k, Netzliste bestaetigt).
    sch.bauteil("Q1", "Transistor_FET:IRF4905", (ox, oy), "IRF4905", FP_TO252,
                rot=0, roff=(2.54, 2.54), voff=(2.54, 5.08))
    sch.netz("Q1", "1", "L", "Q1_GATE")   # G
    sch.netz("Q1", "2", "U", "+24V")      # D -> lokale, geschuetzte Schiene
    sch.netz("Q1", "3", "D", "PWR24V")    # S -> vom Stapel-Leistungsstecker

    sch.bauteil("R11", "Device:R", (ox + 15.24, oy + 15.24), R11_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R11", "1", "U", "Q1_GATE")
    sch.netz("R11", "2", "D", "PWR24V")
    sch.bauteil("R12", "Device:R", (ox + 15.24, oy - 15.24), R12_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R12", "1", "U", "Q1_GATE")
    sch.netz("R12", "2", "D", "GND")

    # D1 (TVS, unveraendert): Kathode -> +24V, Anode -> GND -- exakt
    # dasselbe Muster wie sockelplatine.py (dort D1 an PWR24V statt +24V,
    # sonst identisch; Begruendung fuer Device:D_Zener statt Device:D_TVS
    # steht dort).
    sch.bauteil("D1", "Device:D_Zener", (ox + 40.64, oy + 20.32), D1_WERT,
                FP_TVS_SMC, rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz("D1", "1", "U", "+24V")
    sch.netz("D1", "2", "D", "GND")

    # C12 (220uF, polarisiert): Pin 1 = "+" im Device:C_Polarized-Symbol
    # (eigene Pruefung der KiCad-Quelle) -- MUSS an +24V liegen, NIE an
    # GND. Auf dem Muttern-Print lag der "+"-Aufdruck auf GND (zwei Elkos
    # explodiert, hardware/bauteile-1b.md); tests/test_motormodul.py
    # sichert das hier explizit ab (Punkt 3 des Auftrags).
    sch.bauteil("C12", "Device:C_Polarized", (ox + 40.64, oy - 5.08), C12_WERT,
                FP_CP_RADIAL, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C12", "1", "U", "+24V")     # Pin 1 = "+"
    sch.netz("C12", "2", "D", "GND")


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


def _sensor(sch, ox, oy, netze):
    """U2 (PC817) + R6, J2 (Sensor-Klemme, 3-polig). SENSOR_3V3 (U2 Pin 4,
    Optokoppler-Ausgang) erreicht den Modul-MCU ueber einen der vier
    freien U100-Pins (modulsockel.ZUSATZ_PIN_RICHTUNG) -- s.
    `bauen()` unten, Aufruf von `modulsockel.einbauen(..., zusatz_pins=...)`.
    """
    sch.bauteil("J2", "Connector:Screw_Terminal_01x03", (ox, oy),
                "Sensor-Klemme", FP_KLEMME_3, rot=0,
                roff=(2.54, -8.89), voff=(2.54, -6.35))
    sch.netz("J2", "1", "L", "+24V")
    sch.netz("J2", "2", "L", "SENSOR24V")
    sch.netz("J2", "3", "L", "GND")

    sch.bauteil("R6", "Device:R", (ox + 25.4, oy + 5.08), R6_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R6", "1", "U", "SENSOR24V")
    sch.netz("R6", "2", "D", "U2_LED_A")

    sch.bauteil("U2", "Isolator:PC817", (ox + 25.4, oy - 15.24), "PC817",
                FP_SOP4, rot=0, roff=(-7.62, 12.7), voff=(-7.62, 15.24))
    sch.netz("U2", "1", "L", "U2_LED_A")   # Anode -- aus R6
    sch.netz("U2", "2", "L", "GND")        # Kathode
    sch.netz("U2", "3", "R", "GND")        # Emitter
    sch.netz("U2", "4", "R", netze["SENSOR_3V3"])   # Kollektor -> MCU


def _motor_out(sch, ox, oy):
    """J5 (Motor-Klemme, 2-polig) an Out1/Out2 (U1 Pins 8/10)."""
    sch.bauteil("J5", "Connector:Screw_Terminal_01x02", (ox, oy),
                "Motor-Klemme", FP_KLEMME_2, rot=0,
                roff=(2.54, -6.35), voff=(2.54, -3.81))
    sch.netz("J5", "1", "L", "Out1")
    sch.netz("J5", "2", "L", "Out2")


def _notaus_verriegelung(sch, ox, oy, netze):
    """Die Hardware-Verriegelung aus Punkt 4 des Auftrags, samt J3 (Notaus-
    Stiftleiste, 4-polig, unveraendert aus dem Altprojekt uebernommen).

    ZWEI unabhaengige Wege, einer je Richtung:

    (a) J3 Pin 1/3 (Notaus_1/Notaus_2, je ein potentialfreier Schalter
        gegen GND, wie im Altprojekt) erreichen JE EINEN eigenen
        Modul-MCU-Eingang (fuer die Software-Diagnose: welcher der
        zwei Kanaele ausgeloest hat -- diese Unterscheidung bleibt
        erhalten, die beiden Kanaele werden NICHT lokal kurzgeschlossen)
        UND je eine Schottky-Diode (D3 fuer Notaus_1, D4 fuer Notaus_2,
        Device:D, Pin 1 = K, Pin 2 = A -- eigene Pruefung der
        KiCad-Quelle) auf die globale Sammelleitung NOTAUS: Anode an
        NOTAUS, Kathode an Notaus_1/2. Wird ein lokaler Schalter gegen GND geschlossen,
        zieht das ueber die zugehoerige Diode auch NOTAUS herunter --
        "jeder kann sie herunterziehen" (Design-Dok, Abschnitt
        "Bus und Adressierung"), rein durch einen Schaltkontakt gegen
        Masse, keine Software beteiligt. Ein bereits tiefgezogenes
        NOTAUS speist NICHT in die andere Richtung zurueck in Notaus_1/2
        (die Dioden sperren dann; jeder Kanal bleibt fuer die
        MCU-Diagnose unabhaengig lesbar, auch wenn ein FREMDES Modul
        NOTAUS gezogen hat).

    (b) U3 (SN74LVC1G08, UND-Gatter) bildet die eigentliche Verriegelung:

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

    Die erste Fassung dieser Datei loeste (b) mit einer Diode D2 von
    NSLEEP nach NOTAUS und einem Vorwiderstand R14 (1 kOhm) davor. Sie
    hat NICHT gewirkt, aus zwei voneinander unabhaengigen Gruenden --
    beide sind reine Pegelrechnungen, beide sind in
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
       geht nicht auf 0 V: er wird ueber D3/D4 gegen den Schaltkontakt
       heruntergezogen, liegt also selbst eine Durchlassspannung ueber
       Masse. Eine zweite Diode D2 vom NSLEEP-Pin auf diesen Bus haette
       den Pin auf VF(D3) + VF(D2) gehoben -- mit 1N4148W rund 1,0 bis
       1,3 V, also ebenfalls ueber VIL = 0,8 V. Selbst mit Schottky-
       Dioden auf BEIDEN Wegen blieben im Grenzfall (2 x 400 mV bei
       10 mA, Vishay 86408) genau 0,8 V uebrig -- null Reserve. Eine
       passive Dioden-UND-Verknuepfung kann diese Schwelle in dieser
       Topologie nicht sicher einhalten; ein Gatter kann es.

    Der zweite Grund ist auch der Grund, warum D3/D4 jetzt SCHOTTKY-
    Dioden (BAT54W) sind und keine 1N4148W mehr: der gezogene Ruhepegel
    der Sammelleitung IST die Durchlassspannung dieser Dioden, und alles,
    was am Bus haengt (das Gatter hier mit VIL = 0,8 V, der Pico auf der
    Sockelplatine, kuenftige Module), muss diesen Pegel als LOW lesen.
    Rechnung fuer den Auslegungsfall aus hardware/bauteile-1b.md,
    Beleg 8 (zehn Module, jedes mit R15 = 10 kOhm gegen 3,3 V):

        I(Bus)  = 10 x (3,3 V - 0,4 V) / 10 kOhm =~ 2,9 mA
        VF(BAT54W) <= 400 mV  (Vishay 86408, MAX-Wert bei 10 mA, also
                               erst recht bei 2,9 mA)
        Reserve gegen VIL = 0,8 V: >= 0,4 V

    Mit 1N4148W laege derselbe Pegel bei rund 0,6-0,65 V, und das
    Datenblatt nennt fuer diese kleinen Stroeme ueberhaupt keinen
    MAX-Wert -- fuer eine Sicherheitsfunktion nicht nachweisbar genug.
    Der BAT54W ist in derselben Bauform (SOD-123) wie die bisherigen
    Dioden; der Footprint bleibt unveraendert.

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
    bei 1 kOhm, und die Leckstroeme aller Koppeldioden (BAT54W: IR <=
    2 uA bei 25 V, Vishay 86408) und Gattereingaenge (<= 5 uA) heben den
    Ruhepegel damit um weniger als 0,1 V an -- der Bus bleibt sicher
    ueber VIH = 2,0 V.

    Das DRV8876-nSLEEP-Pin traegt zusaetzlich einen eigenen internen
    Pulldown (SLVSDS7B, Abschnitt 6.5, "RPD Input pulldown resistance
    ... 100 kOhm"): faellt die 3,3-V-Schiene aus, geht auch der
    Gatterausgang mit, und der Treiber schlaeft von sich aus. Die
    Ausfallrichtung des Gatters ist damit die sichere.
    """
    sch.bauteil("J3", "Connector:Conn_01x04_Pin", (ox, oy),
                "Notaus-Stiftleiste", FP_HDR_1X04, rot=180,
                roff=(7.62, -10.16), voff=(7.62, -12.7))
    sch.netz("J3", "1", "R", "NOTAUS_1")
    sch.netz("J3", "2", "R", "GND")
    sch.netz("J3", "3", "R", "NOTAUS_2")
    sch.netz("J3", "4", "R", "GND")

    # ACHTUNG (per kicad-cli sch erc gefunden): Device:D hat Pin 1 (K)
    # LINKS (x=-3,81) und Pin 2 (A) RECHTS (x=+3,81) -- die Stichleitung
    # muss deshalb vom Koerper WEG zeigen (Pin 1 -> "L", Pin 2 -> "R"),
    # sonst kreuzt sie den eigenen anderen Pin und verschmilzt beide
    # Netze.
    sch.bauteil("D3", "Device:D", (ox + 25.4, oy - 5.08), D_KOPPEL_WERT,
                FP_SOD123, rot=0, roff=(0, 2.54), voff=(0, -2.54))
    sch.netz("D3", "1", "L", "NOTAUS_1")          # Kathode
    sch.netz("D3", "2", "R", netze["NOTAUS"])      # Anode
    sch.bauteil("D4", "Device:D", (ox + 25.4, oy - 15.24), D_KOPPEL_WERT,
                FP_SOD123, rot=0, roff=(0, 2.54), voff=(0, -2.54))
    sch.netz("D4", "1", "L", "NOTAUS_2")          # Kathode
    sch.netz("D4", "2", "R", netze["NOTAUS"])      # Anode

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
    (MCU, Flipflop, Gatter, Kennwiderstaende, alle Stecker) plus die
    DRV8876-Endstufe aus dem Muttern-Board."""
    _load_libs(sch)

    # Drei der vier freien U100-Pins (modulsockel.ZUSATZ_PIN_RICHTUNG)
    # tragen hier echte Aufgaben -- Pin "15" (PA8) bleibt frei/nc.
    netze = modulsockel.einbauen(sch, ox, oy, mit_flipflop=True, zusatz_pins={
        "2": "SENSOR_3V3",    # PC14 -- Optokoppler-Ausgang (U2 Pin 4)
        "3": "NOTAUS_1",      # PC15 -- lokaler Notaus-Eingang 1 (J3 Pin 1)
        "14": "NOTAUS_2",     # PA7  -- lokaler Notaus-Eingang 2 (J3 Pin 3)
    })
    # modulsockel.NETZE_NACH_AUSSEN fuehrt SENSOR_3V3 nicht (das ist eine
    # Endstufen-eigene Zusatzleitung, kein Vertragsnetz) -- fuer die
    # Endstufenfunktionen unten wird sie deshalb hier ergaenzt, statt sie
    # in modulsockel.py einzutragen (dort waere sie modulfremd).
    netze = dict(netze)
    netze["SENSOR_3V3"] = "SENSOR_3V3"

    # PWR_FLAG auf "+24V" und "VCP": beide haben nur "power_in"/"passive"-
    # Pins, keinen einzigen "power_out" -- ohne ein power_out-Pin
    # irgendwo im Netz meldet kicad-cli sch erc "Input Power pin not
    # driven" (eigene Messung, s. Testschritt). "+24V" wird zwar von Q1
    # gespeist, aber ein MOSFET-Drain ist elektrisch kein "power_out"-Pin
    # (Symboltyp "passive"); "VCP" erzeugt der DRV8876 intern per
    # Ladungspumpe -- das weiss die ERC nicht, ihr Symbol fuehrt VCP als
    # gewoehnlichen "power_in". Dasselbe Muster wie modulsockel.py
    # (#FLG101/#FLG102 fuer GND/3V3) und sockelplatine.py (#FLG1 fuer
    # PWR24V), hier unter eigenen Referenzen, damit nichts mit deren
    # #FLG101/#FLG102/#FLG1 kollidiert.
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")
    sch.bauteil("#FLG201", "power:PWR_FLAG", (ox + 279.4, oy + 83.82), "PWR_FLAG", "")
    sch.netz("#FLG201", "1", "D", "+24V")
    sch.bauteil("#FLG202", "power:PWR_FLAG", (ox + 279.4, oy + 91.44), "PWR_FLAG", "")
    sch.netz("#FLG202", "1", "D", "VCP")

    _endstufe_leistung(sch, ox + 330.2, oy + 15.24)
    _endstufe_treiber(sch, ox + 431.8, oy + 12.7, netze)
    _sensor(sch, ox + 330.2, oy - 63.5, netze)
    _motor_out(sch, ox + 431.8, oy - 63.5)
    _notaus_verriegelung(sch, ox + 330.2, oy + 63.5, netze)


if __name__ == "__main__":
    import gen

    sch = gen.Schaltplan("Motormodul", "Motormodul", "2026-08-31")
    bauen(sch, 0.0, 0.0)
    ziel = os.path.join(HERE, "..", "..", "hardware", "kicad", "motor",
                         "Motormodul.kicad_sch")
    pfad = sch.schreiben(ziel)
    print("keine unverbundenen Pins -- geschrieben:", pfad)

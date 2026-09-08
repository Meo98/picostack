# -*- coding: utf-8 -*-
"""Die Versorgungszelle: Verpolschutz, TVS, 5V-Regler, VSYS-Diode.

Implementiert woertlich stack_spec.VERSORGUNG (Task 3, PicoStack v2):

    schutz_drain_an = "PWR_IN"        -- Q90-Drain an der Einspeisung
    gate_teiler_an  = "+24V_LOKAL"    -- R90/R91-Teiler an der lokalen Schiene
    vsys_diode      = True            -- D91 vor VSYS
    eingang_v       = (6.0, 30.0)     -- Eingangsfenster des Reglers U90

DER V1-FEHLER, DEN DIESE ZELLE BEHEBT. tools/sch/motormodul.py
(`_endstufe_leistung()`, Q1/R11/R12, aus dem Altprojekt uebernommen)
schaltete den P-Kanal-Verpolschutz genau umgekehrt: Q1s SOURCE lag an
der rohen Einspeisung ("PWR24V"), Q1s DRAIN an der bereits geschuetzten,
lokalen Schiene ("+24V") -- und der Gate-Teiler (R11/R12) haengt dort
ebenfalls an PWR24V, nicht an der lokalen Schiene. Bei einer P-Kanal-
Schutzschaltung ist die Reihenfolge kein Geschmacksdetail:

  * Ein MOSFET hat eine parasitaere Body-Diode zwischen Source und
    Drain, die in der Sperrichtung des Kanals ohnehin leitet (beim
    P-Kanal-Typ: Anode am Drain, Kathode an Source). Sitzt die Source
    an der Einspeisung, leitet diese Body-Diode bei VERPOLTER
    Einspeisung direkt in die lokale Schiene durch -- der Transistor
    kann das gar nicht verhindern, er wird von seiner eigenen Diode
    umgangen.
  * Zusaetzlich haengt in der v1-Schaltung die TVS-Diode (D1) an der
    JETZT vorwaertsgespeisten lokalen Schiene. Bei verpolter
    Einspeisung wird sie DURCH die leitende Body-Diode in
    Durchlassrichtung betrieben und leitet ihrerseits kraeftig --
    zusammen bilden Body-Diode und TVS einen Kurzschluss-Pfad
    ("Crowbar") von der verpolten Einspeisung nach Masse, statt den
    Rueckstrom zu sperren. Der Schutz schuetzt in genau dem Fall nichts,
    fuer den er gedacht ist.

RICHTIGE TOPOLOGIE (diese Datei, Q90/R90/R91):
  * Q90-Drain (Pin 2) an PWR_IN (der rohen Einspeisung, VOR jedem
    eigenen Schutz/Regler) -- die Body-Diode zeigt jetzt so, dass sie
    bei verpolter Einspeisung SPERRT (Anode am Drain/PWR_IN, das bei
    Verpolung negativ liegt; Kathode an Source/+24V), statt
    durchzuschalten.
  * Q90-Source (Pin 3) an +24V (der lokalen, bereits geschuetzten
    Schiene) -- alles, was danach kommt (D90, C90, U90 und jeder
    Verbraucher der Zelle, die diese Schiene bezieht), liegt HINTER dem
    Schutz.
  * Gate-Teiler R90 (Gate<->+24V) UND R91 (Gate<->GND) haengen an der
    LOKALEN Schiene, nicht an PWR_IN: haenge R90 stattdessen an PWR_IN,
    koennte eine verpolte Einspeisung das Gate direkt falsch ansteuern
    (Source auf +24V waere dann ueber R90 mit dem NEGATIVEN PWR_IN
    verbunden, VGS wird stark positiv -- bei einem P-Kanal-MOSFET
    schaltet das den Kanal AUS, gerade wenn er am dringendsten sperren
    soll) und den Schutz umgehen, den er gerade herstellen soll --
    exakt der Fall, den stack_spec.VERSORGUNG["gate_teiler_an"] =
    "+24V_LOKAL" ausschliesst.

tests/test_versorgung.py haelt die vier Kern-Pruefungen des Task-3-
Briefs UND einen Rot-Nachweis fest, der denselben Drain-Check
tatsaechlich gegen die generierte motormodul.py-Netzliste laufen laesst
und dort bestaetigt, dass er (Stand vor dieser Etappe) fehlschlaegt.

Herkunft der Bauteil-Muster (Task-3-Brief, woertlich uebernommen):
  * FP_KLEMME_2 (KF350/PT-1,5-3.5mm-Klemmen-Footprint) aus
    tools/sch/dimmermodul.py.
  * FP_SMC ("Diode_SMD:D_SMC", das MASCHINELLE Padset, nicht die
    Handloet-Variante) ebenfalls aus dimmermodul.py -- dort auch die
    SS36C-"C" vs. SS36-"SMA"-Unterscheidung dokumentiert.
  * Q_PMOS_GDS (generisches P-Kanal-Symbol, Pins 1=G/2=D/3=S) und
    FP_TO252 aus tools/sch/motormodul.py/sockelplatine.py.
  * FP_RECOM + die K7805-1000R3-Herleitung (NACHTRAG 2026-09-07) aus
    tools/sch/sockelplatine.py -- unten woertlich uebernommen, weil
    dieselbe Bauteilentscheidung (abgekuendigter 2-A-Typ, Ersatz durch
    den 1-A-Bruder derselben Baureihe) hier genauso gilt.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import modulsockel      # noqa: E402  (FP_R0805/FP_C0805-Konstanten)

# -------------------------------------------------------------- Footprints
FP_R0805 = modulsockel.FP_R0805
FP_C0805 = modulsockel.FP_C0805
FP_TO252 = "Package_TO_SOT_SMD:TO-252-3_TabPin2"                # Q90
FP_CP_RADIAL = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"          # C90
# Standard-Padset (maschinell bestueckt), nicht die Handloet-Variante des
# Motormoduls -- dieselbe Wahl wie tools/sch/dimmermodul.py (FP_TVS_SMC)
# fuer D90 (TVS) UND D91 (Schottky, gleiches DO-214AB-Gehaeuse).
FP_SMC = "Diode_SMD:D_SMC"
# KF350-3.5-2P (C474892) und PT-1,5-2-3.5 (dimmermodul.py, SS36C-
# Nachbarbauteil) sind fuer diese Pruefung austauschbar: beide sind
# zweipolige 3,5-mm-Raster-Schraubklemmen mit identischem Lochbild --
# derselbe Footprint-String wie tools/sch/dimmermodul.py.FP_KLEMME_2
# (dort fuer die LED-Kanal-Klemmen dokumentiert) wird deshalb hier
# woertlich uebernommen, statt eine zweite, geometrisch gleiche
# .kicad_mod-Angabe fuer J90 zu erfinden.
FP_KLEMME_2 = ("TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal")
# K7805-2000R3 (SIP-3) hat in den KiCad-Standardbibliotheken kein eigenes
# Symbol/Footprint. Wie tools/sch/sockelplatine.py wird deshalb Symbol
# UND Footprint des Recom-Bauteils (identische SIP-3-Pinbelegung
# IN/GND/OUT) wiederverwendet -- der WERT des platzierten Bauteils nennt
# trotzdem den tatsaechlich einzukaufenden Typ (K7805-1000R3), nicht den
# Recom-Platzhalter.
#
# NACHTRAG 2026-09-07 (Bestellrunde, woertlich aus sockelplatine.py
# uebernommen -- dieselbe Bauteilentscheidung gilt hier unveraendert):
# Der 2-A-Typ K7805-2000R3 ist als DEXU C2931187 ABGEKUENDIGT ("no
# longer manufactured" laut JLC-Seiten-JSON), und der einzige lieferbare
# 2-A-Namensvetter (JETEKPS C5378008) vertraegt laut LCSC-Rohdaten nur
# 7-18 V Eingang -- an der 24-V-Schiene unbrauchbar, gleiche
# Typenbezeichnung hin oder her. Bestueckt wird darum der 1-A-Bruder
# derselben DEXU-Baureihe, K7805-1000R3 (LCSC C909765): DEXU-Datenblatt
# "K78xx-1000R3" (REV A0-2018.12, selbst gelesen), Auswahltabelle S. 1:
# K7805-1000R3 Eingang "6.0-30V (24)", 5 V / 1000 mA, gleiche Bauform
# 11,6 x 7,5 x 10,2, LM78xx-Pinout -- exakt das Fenster, das
# stack_spec.VERSORGUNG["eingang_v"] = (6.0, 30.0) festhaelt. 1 A statt
# 2 A traegt die 5-V-Schiene locker: sie versorgt nur Logik (Pico,
# je Modul das kleine MCU-Nest, einzelne Optokoppler-LEDs).
FP_RECOM = "Converter_DCDC:Converter_DCDC_RECOM_R-78B-2.0_THT"

# ------------------------------------------------------------ Bauteilwerte
Q90_WERT = "IRFR5305"    # Verpolungsschutz, LCSC C2624 -- Herleitung s.
                         # motormodul.py::_endstufe_leistung (Sperrspannung,
                         # Gatespannung, Durchlassverlust bereits nachgerechnet;
                         # dieselbe Bauteilwahl, nur richtig gepolt)
R90_WERT = "10k"         # Gate<->+24V (lokal!) -- Reverse-Polarity-Schutz
R91_WERT = "10k"         # Gate<->GND -- schaltet Q90 im Normalfall durch
D90_WERT = "SMCJ30A"     # TVS, LCSC C340696 -- Herleitung s. sockelplatine.py
                         # (D1): Vrwm 30V, Vbr 36.8V min., Vc 48.4V max.
U90_WERT = "K7805-1000R3"   # LCSC C909765, s. NACHTRAG oben
D91_WERT = "SS36C"       # Schottky 60V 3A, DO-214AB, LCSC C16237 -- das
                         # "C" unterscheidet das SMC-Gehaeuse vom SMA-"SS36"
C90_WERT = "220u"        # radial, Stuetzung an der lokalen 24-V-Schiene
C91_WERT = "22u"         # 0805, Ausgangskondensator der 5-V-Schiene


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C", "Device.kicad_sym", "C")
    sch.lib("Device:C_Polarized", "Device.kicad_sym", "C_Polarized")
    sch.lib("Device:D_Zener", "Device.kicad_sym", "D_Zener")
    sch.lib("Device:D_Schottky", "Device.kicad_sym", "D_Schottky")
    # Generisches P-Kanal-Symbol (Pins 1=G, 2=D, 3=S) -- der Typ steht im
    # Wertfeld (IRFR5305), dieselbe Begruendung wie motormodul.py/
    # dimmermodul.py: die KiCad-Bibliothek fuehrt kein eigenes IRFR5305-
    # Symbol, und ein Symbolname, der einen anderen Typ nennt als die
    # Stueckliste, waere genau der Fehler, den diese Zelle vermeiden soll.
    sch.lib("Transistor_FET:Q_PMOS_GDS", "Transistor_FET.kicad_sym",
            "Q_PMOS_GDS")
    sch.lib("Connector:Screw_Terminal_01x02", "Connector.kicad_sym",
            "Screw_Terminal_01x02")
    sch.lib_extends("Converter_DCDC:R-78B5.0-2.0", "Converter_DCDC.kicad_sym",
                     "R-78B1.2-2.0", "R-78B5.0-2.0")
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")


def bauen(sch, ox, oy):
    """Baut die Versorgungszelle bei (ox, oy) in `sch` ein.

    Reihenfolge im Layout (links -> rechts): Einspeisung (J90) ->
    Verpolschutz (Q90/R90/R91) -> lokale 24-V-Schiene mit TVS+Elko
    (D90/C90) -> 5-V-Regler (U90) mit Ausgangskondensator (C91) ->
    VSYS-Entkopplung (D91).
    """
    _load_libs(sch)

    # ---------------------------------------------------- J90 Einspeisung
    # Klemme 2-polig (KF350-3.5-2P, LCSC C474892) -> PWR_IN/GND. PWR_IN
    # ist die ROHE Einspeisung, VOR jedem Schutz/Regler dieser Zelle --
    # stack_spec.VERSORGUNG["schutz_drain_an"] == "PWR_IN" verlangt
    # genau das als Bezugspunkt fuer Q90s Drain.
    j90x, j90y = ox, oy
    sch.bauteil("J90", "Connector:Screw_Terminal_01x02", (j90x, j90y),
                "Versorgung Eingang", FP_KLEMME_2, rot=0,
                roff=(2.54, -6.35), voff=(2.54, -3.81))
    sch.netz("J90", "1", "R", "PWR_IN")
    sch.netz("J90", "2", "R", "GND", laenge=7.62)

    # PWR_FLAG auf PWR_IN: J90/Q90-Drain sind beide "passive"-Pins --
    # ohne einen power_out-Pin irgendwo im Netz meldet die ERC "Input
    # Power pin not driven" (dasselbe Muster wie sockelplatine.py #FLG1
    # auf PWR24V).
    sch.bauteil("#FLG90", "power:PWR_FLAG", (j90x + 12.7, j90y - 15.24),
                "PWR_FLAG", "")
    sch.netz("#FLG90", "1", "D", "PWR_IN")

    # ---------------------------------------------- Q90/R90/R91 Verpolschutz
    # RICHTIGE Topologie (s. Moduldoku oben, im Unterschied zu
    # motormodul.py Q1): Drain an PWR_IN (Einspeisung), Source an +24V
    # (lokal, geschuetzt), Gate-Teiler an der LOKALEN Schiene.
    qx, qy = ox + 30.48, oy + 12.7
    sch.bauteil("Q90", "Transistor_FET:Q_PMOS_GDS", (qx, qy), Q90_WERT,
                FP_TO252, rot=0, roff=(2.54, 2.54), voff=(2.54, 5.08))
    sch.netz("Q90", "1", "L", "Q90_GATE")   # G
    sch.netz("Q90", "2", "U", "PWR_IN")     # D -> Einspeisung (schutz_drain_an)
    sch.netz("Q90", "3", "D", "+24V")       # S -> lokale, geschuetzte Schiene

    sch.bauteil("R90", "Device:R", (qx + 15.24, qy + 15.24), R90_WERT,
                FP_R0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R90", "1", "U", "Q90_GATE")
    sch.netz("R90", "2", "D", "+24V")        # gate_teiler_an == "+24V_LOKAL"
    sch.bauteil("R91", "Device:R", (qx + 15.24, qy - 15.24), R91_WERT,
                FP_R0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R91", "1", "U", "Q90_GATE")
    sch.netz("R91", "2", "D", "GND")

    # -------------------------------------------------- D90/C90 lokale 24V
    # TVS (Kathode -> +24V, Anode -> GND) und Stuetzkondensator, JETZT
    # hinter dem Schutz -- beide profitieren davon, dass Q90 bei
    # Verpolung sperrt, statt (wie in v1) selbst Teil des Crowbar-Pfads
    # zu sein.
    dx, dy = qx + 40.64, qy + 20.32
    sch.bauteil("D90", "Device:D_Zener", (dx, dy), D90_WERT, FP_SMC,
                rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz("D90", "1", "U", "+24V")
    sch.netz("D90", "2", "D", "GND")

    sch.bauteil("C90", "Device:C_Polarized", (dx, qy - 5.08), C90_WERT,
                FP_CP_RADIAL, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C90", "1", "U", "+24V")   # Pin 1 = "+" (Device:C_Polarized)
    sch.netz("C90", "2", "D", "GND")

    # ---------------------------------------------------- U90 5-V-Regler
    ux, uy = ox + 96.52, oy
    sch.bauteil("U90", "Converter_DCDC:R-78B5.0-2.0", (ux, uy), U90_WERT,
                FP_RECOM, rot=0, roff=(-7.62, -13.97), voff=(-7.62, -11.43))
    sch.netz("U90", "1", "L", "+24V")        # IN
    sch.netz("U90", "2", "D", "GND")         # GND
    sch.netz("U90", "3", "R", "+5V_LOKAL")   # OUT

    sch.bauteil("C91", "Device:C", (ux + 22.86, uy + 12.7), C91_WERT,
                FP_C0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C91", "1", "U", "+5V_LOKAL")
    sch.netz("C91", "2", "D", "GND")

    # ---------------------------------------------------- D91 VSYS-Diode
    # Schottky (SS36C), Anode an +5V_LOKAL (Regler-Ausgang dieser Zelle),
    # Kathode an VSYS (Pico Pin 39) -- stack_spec.VERSORGUNG["vsys_diode"]
    # == True: sperrt in Richtung dieser Zelle, falls der Pico
    # stattdessen ueber USB-VBUS versorgt wird. Ohne sie speisten zwei
    # Quellen (dieser Regler UND der Pico-eigene USB-Regler) denselben
    # VSYS-Knoten gegeneinander.
    d91x, d91y = ux + 45.72, uy + 20.32
    sch.bauteil("D91", "Device:D_Schottky", (d91x, d91y), D91_WERT, FP_SMC,
                rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz("D91", "1", "U", "VSYS")        # K -> VSYS
    sch.netz("D91", "2", "D", "+5V_LOKAL")   # A -> +5V_LOKAL


# ------------------------------------------------------- Erzeugen
# Kein eigenstaendiges Blatt: die Versorgungszelle wird von jedem
# Modul-Generator (dimmermodul.py, motormodul.py, ...) in dessen eigenes
# Blatt eingebaut (versorgung.bauen(sch, ox, oy)), genau wie
# sockelplatine.py seine 24-V-Kette selbst haelt. Ein `erzeugen()` mit
# eigenem ZIEL-Pfad gaebe es fuer ein Blatt, das nie fuer sich allein
# gefertigt wird -- deshalb bewusst kein __main__-Block hier.

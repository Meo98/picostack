# -*- coding: utf-8 -*-
"""Schaltplan-Generator der Dimmer-Module (1, 3 und 4 Kanaele).

EIN Generator fuer alle drei Vertragsvarianten (stack_spec.MODULTYPEN:
0x10 Dimmer1, 0x11 Dimmer3, 0x12 Dimmer4) -- die Varianten
unterscheiden sich NUR in der Zahl der bestueckten Kanaele. Aufbau je
Modul:

  * Modulsockel-Block (modulsockel.einbauen): MCU, Flipflop-Kette,
    Gatter, Kennwiderstaende, alle Stecker -- identisch zum Motormodul.
  * Verpolungsschutz Q10 (IRFR5305) + R11/R12 zwischen dem Stapelnetz
    PWR24V und der lokalen Schiene +24V, dazu TVS D10 und Elko C12 --
    unveraendert das Muster aus motormodul._endstufe_leistung(), dort
    steht die vollstaendige Bauteil-Herleitung (Datenblattzitate,
    Grenzwerte); sie gilt hier woertlich weiter, weil Schiene und
    Klemmspannung dieselben sind.
  * Je Kanal n: Low-Side-N-MOSFET Qn (NCE6020AK, TO-252) mit
    Gate-Vorwiderstand RGn (100 Ohm) und Gate-Pulldown RPn (100 kOhm),
    Freilaufdiode Dn (SS36C, Drain -> +24V) und Schraubklemme Jn
    (Pin 1 = +24V, Pin 2 = geschaltetes Minus der Last).

KANAL->PIN-ZUORDNUNG (hiermit festgelegt, Firmware richtet sich
danach): PWM1 = Pin "15" (PA8), PWM2 = Pin "14" (PA7), PWM3 = Pin "2"
(PC14), PWM4 = Pin "3" (PC15). PA8/PA7 zuerst, weil sie am STM32C011
Timerkanaele tragen (DS13866, Tabelle "Pin assignment": PA8 = TIM1_CH1,
PA7 = TIM1_CH1N/TIM3_CH2); PC14/PC15 sind reine GPIO -- Kanal 3 und 4
dimmen notfalls per Software-PWM. Deshalb hat der Ein-Kanal-Dimmer
IMMER Hardware-PWM.

GATE DIREKT AM 3,3-V-PIN: Der Kanal-FET ist bei VGS = 3,3 V nicht
vollstaendig durchgesteuert (Datenblatt spezifiziert RDS(on) bei 10 V
und 4,5 V). Das VIERKANALIGE LED-Dimmer-Board des Espace des
Inventions treibt NCE6050KA seit seiner Inbetriebnahme direkt aus
3,3-V-GPIO und bleibt bei 3 A je Kanal handwarm -- fuer LED-Lasten
dieser Groessenordnung reicht die Ansteuerung nachweislich. ERSATZ
2026-09-04: Der NCE6050KA ist bei JLC/LCSC ausverkauft; bestueckt wird
der NCE6020AK (gleiche Familie, gleiches Gehaeuse, gleiches
V_GS(th)-Limit "2.5V" laut LCSC-Rohdaten, RDS(on) 40 mOhm bei 4,5 V
statt 20 mOhm bei 10 V). Die Espace-Felderfahrung gilt woertlich nur
fuer den 6050KA; beim 6020AK ist die Rechnung konservativ dieselbe
(40 mOhm x (3 A)^2 = 0,36 W je Kanal, TO-252 auf Masseflaeche traegt
das), am ersten bestueckten Board aber nachzumessen. Wer mehr Strom
schalten will, braucht einen Gatetreiber (und sollte ein eigenes
Modul vorschlagen).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import modulsockel      # noqa: E402
import stack_spec as S  # noqa: E402

FP_R0805 = modulsockel.FP_R0805
FP_TO252 = "Package_TO_SOT_SMD:TO-252-3_TabPin2"
# Standard-Padset (nicht die Handloet-Variante des Motormoduls): die
# Dimmer-Dioden werden maschinell bestueckt, und nur so passen vier
# Freilaufdioden aufs Brett (s. spec_dimmer_basis).
FP_TVS_SMC = "Diode_SMD:D_SMC"
FP_CP_RADIAL = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"
# 3,5-mm-Klemme (13,5 A) statt der 5,08er des Motormoduls -- vier
# grosse Klemmen passen nicht an die Klemmenkante (s. spec_dimmer_basis).
FP_KLEMME_2 = ("TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal")

Q10_WERT = "IRFR5305"    # Verpolungsschutz, Herleitung in motormodul.py
R11_WERT = "10k"
R12_WERT = "10k"
D10_WERT = "SMCJ30A"
C12_WERT = "220u"
QK_WERT = "NCE6020AK"    # Kanal-FET: 60 V, 20 A, TO-252, LCSC C108639
                         # (Produktseite gesichtet 2026-09-04; Ersatz
                         # fuer den ausverkauften NCE6050KA, s. oben)
DK_WERT = "SS36C"        # Freilauf: Schottky 60 V 3 A, DO-214AB --
                         # das C unterscheidet bei MDD das SMC-Gehaeuse
                         # vom SMA-"SS36" (C16015), s. bauteile-dimmer.md
RG_WERT = "100"
RP_WERT = "100k"

#: Kanalnummer -> Zusatzpin des Modulsockels (s. Docstring).
PWM_PINS = {1: "15", 2: "14", 3: "2", 4: "3"}

#: Variante -> (Typcode, Kanalzahl); direkt am Vertrag verankert.
VARIANTEN = {1: 0x10, 3: 0x11, 4: 0x12}


def _kanal(sch, n, ox, oy):
    """Ein Dimmer-Kanal: Qn, RGn, RPn, Dn, Jn."""
    q, rg, rp, d, j = ("Q%d" % n, "RG%d" % n, "RP%d" % n,
                       "D%d" % n, "J%d" % (4 + n))
    pwm, led = "PWM%d" % n, "LED%d" % n

    sch.bauteil(q, "Transistor_FET:Q_NMOS_GDS", (ox, oy), QK_WERT, FP_TO252,
                rot=0, roff=(2.54, 2.54), voff=(2.54, 5.08))
    sch.netz(q, "1", "L", pwm + "_G")   # G, hinter RGn
    sch.netz(q, "2", "U", led)          # D -> Klemme (Minus der Last)
    sch.netz(q, "3", "D", "GND")        # S

    sch.bauteil(rg, "Device:R", (ox - 17.78, oy + 10.16), RG_WERT, FP_R0805,
                rot=90, roff=(-1.27, -2.54), voff=(1.27, -2.54))
    sch.netz(rg, "1", "L", pwm)
    sch.netz(rg, "2", "R", pwm + "_G")

    sch.bauteil(rp, "Device:R", (ox - 12.7, oy + 12.7), RP_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz(rp, "1", "U", pwm + "_G")
    sch.netz(rp, "2", "D", "GND")

    # Freilauf: Kathode an +24V. LED-Baender sind zwar ueberwiegend
    # ohmsch, aber die Zuleitung ist eine Induktivitaet -- beim
    # Abschalten muss ihr Strom irgendwohin (Muster aus dem
    # LED-Dimmer-Altprojekt, dort D1..D4).
    sch.bauteil(d, "Device:D_Schottky", (ox + 12.7, oy + 10.16), DK_WERT,
                FP_TVS_SMC, rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz(d, "1", "U", "+24V")       # K
    sch.netz(d, "2", "D", led)          # A

    sch.bauteil(j, "Connector:Screw_Terminal_01x02", (ox + 27.94, oy),
                "LED-Kanal %d" % n, FP_KLEMME_2, rot=0,
                roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz(j, "1", "R", "+24V")
    sch.netz(j, "2", "R", led)


def _leistung(sch, ox, oy):
    """Verpolungsschutz + TVS + Elko -- Muster aus motormodul.py."""
    sch.bauteil("Q10", "Transistor_FET:Q_PMOS_GDS", (ox, oy), Q10_WERT,
                FP_TO252, rot=0, roff=(2.54, 2.54), voff=(2.54, 5.08))
    sch.netz("Q10", "1", "L", "Q10_GATE")
    sch.netz("Q10", "2", "U", "+24V")
    sch.netz("Q10", "3", "D", "PWR24V")

    sch.bauteil("R11", "Device:R", (ox + 15.24, oy + 15.24), R11_WERT,
                FP_R0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R11", "1", "U", "Q10_GATE")
    sch.netz("R11", "2", "D", "PWR24V")
    sch.bauteil("R12", "Device:R", (ox + 15.24, oy - 15.24), R12_WERT,
                FP_R0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R12", "1", "U", "Q10_GATE")
    sch.netz("R12", "2", "D", "GND")

    sch.bauteil("D10", "Device:D_Zener", (ox + 40.64, oy + 20.32), D10_WERT,
                FP_TVS_SMC, rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz("D10", "1", "U", "+24V")
    sch.netz("D10", "2", "D", "GND")

    sch.bauteil("C12", "Device:C_Polarized", (ox + 40.64, oy - 5.08),
                C12_WERT, FP_CP_RADIAL, rot=0,
                roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C12", "1", "U", "+24V")    # Pin 1 = "+", s. motormodul.py
    sch.netz("C12", "2", "D", "GND")


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C_Polarized", "Device.kicad_sym", "C_Polarized")
    sch.lib("Device:D_Zener", "Device.kicad_sym", "D_Zener")
    sch.lib("Device:D_Schottky", "Device.kicad_sym", "D_Schottky")
    # Generische FET-Symbole (Pins 1=G, 2=D, 3=S): Typ steht im
    # Wertfeld -- dieselbe Begruendung wie bei motormodul._load_libs().
    sch.lib("Transistor_FET:Q_PMOS_GDS", "Transistor_FET.kicad_sym",
            "Q_PMOS_GDS")
    sch.lib("Transistor_FET:Q_NMOS_GDS", "Transistor_FET.kicad_sym",
            "Q_NMOS_GDS")
    sch.lib("Connector:Screw_Terminal_01x02", "Connector.kicad_sym",
            "Screw_Terminal_01x02")


def bauen(sch, ox, oy, kanaele):
    _load_libs(sch)
    zusatz = {PWM_PINS[n]: "PWM%d" % n for n in range(1, kanaele + 1)}
    modulsockel.einbauen(sch, ox, oy, mit_flipflop=True, zusatz_pins=zusatz)

    # PWR_FLAG auf +24V: dasselbe ERC-Muster wie im Motormodul
    # (kein power_out-Pin im Netz; der MOSFET-Drain ist "passive").
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")
    sch.bauteil("#FLG201", "power:PWR_FLAG", (ox + 279.4, oy + 83.82),
                "PWR_FLAG", "")
    sch.netz("#FLG201", "1", "D", "+24V")

    _leistung(sch, ox + 330.2, oy + 15.24)
    for n in range(1, kanaele + 1):
        _kanal(sch, n, ox + 330.2 + ((n - 1) % 2) * 101.6,
               oy + 78.74 + ((n - 1) // 2) * 55.88)


# ------------------------------------------------------- Erzeugen
DATUM = "2026-09-04"
_ZIELE = {
    kanaele: os.path.join(HERE, "..", "..", "hardware", "kicad",
                          "dimmer%d" % kanaele,
                          "Dimmer%d.kicad_sch" % kanaele)
    for kanaele in VARIANTEN
}


def erzeugen(ziel=None, kanaele=1):
    """Baut den Schaltplan einer Variante (Vorgabe: Dimmer1)."""
    import gen

    name = S.MODULTYPEN[VARIANTEN[kanaele]]["name"]
    sch = gen.Schaltplan(name, name, DATUM, papier="A2")
    bauen(sch, 60.96, 139.7, kanaele)
    pfad = _ZIELE[kanaele] if ziel is None else ziel
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    return sch.schreiben(pfad)


if __name__ == "__main__":
    for kanaele in sorted(VARIANTEN):
        print("Dimmer%d: keine unverbundenen Pins -- geschrieben: %s"
              % (kanaele, erzeugen(kanaele=kanaele)))

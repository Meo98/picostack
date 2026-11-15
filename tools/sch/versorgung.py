# -*- coding: utf-8 -*-
"""Die Versorgungszelle v3: Klemme -> Verpolschutz -> TVS -> Buck 5 V -> VSYS.

Implementiert stack_spec.VERSORGUNG woertlich:

    Klemme J90 (6-30 V)          PWR_IN, GND
    Q90 AOD409 (P-Kanal)         Drain an PWR_IN, Source an VIN (lokal)
    R91 100 k Gate->GND, D92 Zener 12 V Gate-Source
                                 Vgs = -min(Vin, 12 V): bei 6 V voll
                                 durchgesteuert, bei 30 V unter dem
                                 20-V-Gate-Limit. (v2 hatte einen
                                 10k/10k-Teiler: bei 6 V nur -3 V, der
                                 IRFR5305 war dort nicht sicher offen --
                                 Bericht 03, 2026-10-14.)
    D90 SMCJ30A (TVS)            VIN -> GND, nur Transienten
    C90 47 uF/50 V SMD-Elko, C91/C92 2x 10 uF/50 V 1210  an VIN
    U90 TPS5430DDAR              VIN -> PH; Boot C93 10 nF; L90 15 uH;
                                 D93 SS36C Freilauf; C94 100 uF/16 V
                                 Ausgang; R92 10 k / R93 3,3 k -> 4,92 V
    D91 SS36C                    +5V_LOKAL -> VSYS (Pico Pin 39)
    LED90 + R94 10 k             "VIN"-Anzeige an der lokalen Schiene

WARUM EIN BUCK UND KEIN SIP-3-MODUL MEHR: K7805-1000R3 (C909765) und
K7805-2000R3 (C2931187) sind bei LCSC ausverkauft (2026-10-14 und
2026-11-15 geprueft); die lieferbaren Geschwister beginnen bei 7 V und
verletzen die 6-V-Zusage. TPS5430 ist JLC-Basic (C9864), 5,5-36 V, 3 A.
Preis der Entscheidung: ein Schaltregler-Layout (Schleife IC-L-Diode-
Cin eng, PowerPAD mit Vias) -- Regel P2 des Vertrags.

USB PARALLEL: Der Pico speist VSYS aus VBUS ueber seine eigene
Schottky-Diode; diese Zelle speist VSYS ueber D91. Liegen beide an,
gewinnt die hoehere Spannung, keine Quelle speist in die andere
zurueck. Liegt nur USB an, ist der Buck stromlos (kein Rueckweg: D91
sperrt). Das erfuellt die Vorgabe "programmieren ohne Netzteil".

Netzliste-Zusagen (tests/test_versorgung.py prueft sie am erzeugten
Blatt): Q90-Drain an PWR_IN; D92 zwischen Q90-Gate und Q90-Source;
D91 zwischen +5V_LOKAL und VSYS; Teiler R92/R93 an VSENSE.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import stack_spec as S  # noqa: E402

FP_R0805 = "Resistor_SMD:R_0805_2012Metric"
FP_R0603 = "Resistor_SMD:R_0603_1608Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_C1210 = "Capacitor_SMD:C_1210_3225Metric"
FP_CP_63 = "Capacitor_SMD:CP_Elec_6.3x7.7"
# AOD409: Pin 1 = G, Pin 2 = D (Tab), Pin 3 = S -- dasselbe Padbild
# wie der Kanal-FET (Q_PMOS_GDS 1=G, 2=D, 3=S).
FP_TO252 = "Package_TO_SOT_SMD:TO-252-3_TabPin2"
FP_SMC = "Diode_SMD:D_SMC"
FP_SOD123 = "Diode_SMD:D_SOD-123"
FP_L6045 = "Inductor_SMD:L_Sunlord_SWPA6045S"
# OHNE die _ThermalVias-Variante: deren 0,2-mm-Bohrungen liegen unter der
# 0,3-mm-Regel des Projekts (DRC drill_out_of_range, 2026-11-15). Die
# Waermevias setzt spec_dimmer_basis als PRE_VIAS mit 0,3 mm.
FP_SOIC8EP = "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm"
FP_LED0805 = "LED_SMD:LED_0805_2012Metric"
FP_KLEMME_35 = S.FP_KLEMME_35

# Bauteil -> (Wert, Footprint, LCSC). LCSC nur, wo eine Produktseite
# gesichtet wurde (Bericht 03, 2026-10-14; jlcpcb-parts, 2026-11-15);
# sonst leer, Beschreibung traegt dann die Auswahl.
TEILE = {
    "J90": ("Versorgung 6-30V", FP_KLEMME_35, "C474892"),      # KF350-3.5-2P
    "Q90": ("AOD409", FP_TO252, "C36220"),
    "R91": ("100k", FP_R0805, "C149504"),
    "D92": ("BZT52C12", FP_SOD123, "C19077410"),
    "D90": ("SMCJ30A", FP_SMC, "C340696"),
    "C90": ("47u/50V", FP_CP_63, ""),
    "C91": ("10u/50V", FP_C1210, ""),
    "C92": ("10u/50V", FP_C1210, ""),
    "U90": ("TPS5430DDAR", FP_SOIC8EP, "C9864"),
    "C93": ("10n", FP_C0805, ""),
    "L90": ("15u", FP_L6045, "C83374"),                         # SWPA6045S150MT
    "D93": ("SS36C", FP_SMC, "C16237"),
    "C94": ("100u/16V", FP_CP_63, ""),
    "R92": ("10k", FP_R0603, "C25804"),      # 0603: Platz links von U90
    "R93": ("3.3k", FP_R0603, "C22978"),
    "D91": ("SS36C", FP_SMC, "C16237"),
    "LED90": ("gruen", FP_LED0805, ""),
    "R94": ("10k", FP_R0805, "C17414"),
}


def _felder(ref):
    lcsc = TEILE[ref][2]
    return {"LCSC": lcsc} if lcsc else None


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C", "Device.kicad_sym", "C")
    sch.lib("Device:C_Polarized", "Device.kicad_sym", "C_Polarized")
    sch.lib("Device:L", "Device.kicad_sym", "L")
    sch.lib("Device:LED", "Device.kicad_sym", "LED")
    sch.lib("Device:D_Zener", "Device.kicad_sym", "D_Zener")
    sch.lib("Device:D_Schottky", "Device.kicad_sym", "D_Schottky")
    sch.lib("Transistor_FET:Q_PMOS_GDS", "Transistor_FET.kicad_sym", "Q_PMOS_GDS")
    sch.lib("Regulator_Switching:TPS5430DDA", "Regulator_Switching.kicad_sym",
            "TPS5430DDA")
    sch.lib("Connector:Screw_Terminal_01x02", "Connector.kicad_sym",
            "Screw_Terminal_01x02")
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")


def _b(sch, ref, libid, pos, rot=0, roff=(2.54, -2.54), voff=(2.54, 2.54)):
    wert, fp, _ = TEILE[ref]
    sch.bauteil(ref, libid, pos, wert, fp, rot=rot, roff=roff, voff=voff,
                felder=_felder(ref))


def bauen(sch, ox, oy):
    """Baut die Versorgungszelle bei (ox, oy) ein (Breite ~200, Hoehe ~90)."""
    _load_libs(sch)

    # ------------------------------------------------------ J90 Einspeisung
    _b(sch, "J90", "Connector:Screw_Terminal_01x02", (ox, oy), roff=(2.54, -6.35),
       voff=(2.54, -3.81))
    sch.netz("J90", "1", "R", "PWR_IN")
    sch.netz("J90", "2", "R", "GND", laenge=7.62)
    sch.bauteil("#FLG90", "power:PWR_FLAG", (ox + 12.7, oy - 15.24), "PWR_FLAG", "")
    sch.netz("#FLG90", "1", "D", "PWR_IN")

    # ------------------------------------------------ Q90 / R91 / D92 Schutz
    qx, qy = ox + 30.48, oy + 12.7
    _b(sch, "Q90", "Transistor_FET:Q_PMOS_GDS", (qx, qy), roff=(2.54, 2.54),
       voff=(2.54, 5.08))
    sch.netz("Q90", "1", "L", "Q90_GATE")   # G
    sch.netz("Q90", "2", "U", "PWR_IN")     # D -> Einspeisung (schutz_drain_an)
    sch.netz("Q90", "3", "D", "VIN")        # S -> lokale, geschuetzte Schiene
    # VIN speist U90s Power-Input-Pin; ohne power_out-Pin im Netz
    # meldet der ERC "Input Power pin not driven".
    sch.bauteil("#FLG92", "power:PWR_FLAG", (qx + 30.48, qy - 30.48), "PWR_FLAG", "")
    sch.netz("#FLG92", "1", "D", "VIN")
    _b(sch, "R91", "Device:R", (qx + 15.24, qy + 17.78), roff=(2.54, -1.27),
       voff=(2.54, 1.27))
    sch.netz("R91", "1", "U", "Q90_GATE")
    sch.netz("R91", "2", "D", "GND")
    # Zener: Kathode an der Source (VIN), Anode am Gate -> Vgs = -Vz.
    _b(sch, "D92", "Device:D_Zener", (qx + 15.24, qy - 17.78), rot=0)
    sch.netz("D92", "1", "L", "VIN")        # K
    sch.netz("D92", "2", "R", "Q90_GATE")   # A

    # ------------------------------------------------ D90 / C90..C92 an VIN
    dx, dy = qx + 45.72, qy + 20.32
    _b(sch, "D90", "Device:D_Zener", (dx, dy), rot=270, roff=(2.54, -2.54),
       voff=(2.54, 2.54))
    sch.netz("D90", "1", "U", "VIN")        # K
    sch.netz("D90", "2", "D", "GND")        # A
    for i, ref in enumerate(("C90", "C91", "C92")):
        lib = "Device:C_Polarized" if ref == "C90" else "Device:C"
        _b(sch, ref, lib, (dx + 15.24 * (i + 1), dy), rot=0, roff=(2.54, -1.27),
           voff=(2.54, 1.27))
        sch.netz(ref, "1", "U", "VIN")      # C_Polarized: Pin 1 = "+"
        sch.netz(ref, "2", "D", "GND")

    # ---------------------------------------------------- U90 Buck
    # 139,7 statt 124,46: bei 124,46 lag U90s GND-Stummel (Pin 6) genau
    # auf C92s VIN-Stummel -- ERC meldete "GND und VIN am selben Netz"
    # (Rot-Nachweis dafuer, dass der ERC Kurzschluesse durch
    # Stummel-Ueberlappung findet).
    ux, uy = ox + 139.7, oy + 12.7
    _b(sch, "U90", "Regulator_Switching:TPS5430DDA", (ux, uy), roff=(-10.16, -15.24),
       voff=(-10.16, -12.7))
    sch.netz("U90", "7", "L", "VIN")        # VIN
    # EN (ENA): interner Pull-up, offen = ein. NICHT an VIN legen -- der
    # Pin vertraegt laut Datenblatt (SLVS632L, Abs. Max.) nur -0,3..7 V.
    sch.nc("U90", "5")
    sch.nc("U90", "2")
    sch.nc("U90", "3")
    sch.netz("U90", "6", "D", "GND")        # GND
    pins = sch.PINS["Regulator_Switching:TPS5430DDA"]
    if "9" in pins:
        sch.netz("U90", "9", "D", "GND")    # PowerPAD
    sch.netz("U90", "1", "R", "BOOT")       # BOOT
    sch.netz("U90", "8", "R", "VSW")        # PH
    sch.netz("U90", "4", "R", "FB")         # VSENSE

    # Boot-Kondensator BOOT -> VSW
    _b(sch, "C93", "Device:C", (ux + 27.94, uy + 2.54), rot=0, roff=(2.54, -1.27),
       voff=(2.54, 1.27))
    sch.netz("C93", "1", "U", "BOOT")
    sch.netz("C93", "2", "D", "VSW")
    # Freilauf: Kathode an VSW, Anode an GND
    _b(sch, "D93", "Device:D_Schottky", (ux + 43.18, uy + 15.24), rot=270)
    sch.netz("D93", "1", "U", "VSW")
    sch.netz("D93", "2", "D", "GND")
    # Spule VSW -> +5V_LOKAL
    # rot=90: Pin 1 liegt links, Pin 2 rechts (gen.xf: (X - py, Y - px)).
    _b(sch, "L90", "Device:L", (ux + 58.42, uy), rot=90, roff=(0, -5.08),
       voff=(0, 5.08))
    sch.netz("L90", "1", "L", "VSW")
    sch.netz("L90", "2", "R", "+5V_LOKAL")
    # Ausgangskondensator
    _b(sch, "C94", "Device:C_Polarized", (ux + 73.66, uy + 15.24), rot=0,
       roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C94", "1", "U", "+5V_LOKAL")
    sch.netz("C94", "2", "D", "GND")
    # Teiler +5V_LOKAL -> FB -> GND
    _b(sch, "R92", "Device:R", (ux + 88.9, uy + 5.08), rot=0, roff=(2.54, -1.27),
       voff=(2.54, 1.27))
    sch.netz("R92", "1", "U", "+5V_LOKAL")
    sch.netz("R92", "2", "D", "FB")
    _b(sch, "R93", "Device:R", (ux + 88.9, uy + 25.4), rot=0, roff=(2.54, -1.27),
       voff=(2.54, 1.27))
    sch.netz("R93", "1", "U", "FB")
    sch.netz("R93", "2", "D", "GND")
    sch.bauteil("#FLG91", "power:PWR_FLAG", (ux + 73.66, uy - 15.24), "PWR_FLAG", "")
    sch.netz("#FLG91", "1", "D", "+5V_LOKAL")

    # ---------------------------------------------------- D91 VSYS-Diode
    # rot=180: Anode links (+5V_LOKAL), Kathode rechts (VSYS).
    _b(sch, "D91", "Device:D_Schottky", (ux + 109.22, uy), rot=180)
    sch.netz("D91", "1", "R", "VSYS")        # K -> VSYS
    sch.netz("D91", "2", "L", "+5V_LOKAL")   # A

    # ---------------------------------------------------- LED "VIN"
    _b(sch, "R94", "Device:R", (ox + 15.24, oy + 45.72), rot=0, roff=(2.54, -1.27),
       voff=(2.54, 1.27))
    sch.netz("R94", "1", "U", "VIN")
    sch.netz("R94", "2", "D", "LED90_A")
    _b(sch, "LED90", "Device:LED", (ox + 15.24, oy + 66.04), rot=90, roff=(2.54, -2.54),
       voff=(2.54, 2.54))
    sch.netz("LED90", "2", "U", "LED90_A")   # A
    sch.netz("LED90", "1", "D", "GND")       # K

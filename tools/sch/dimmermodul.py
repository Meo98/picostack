# -*- coding: utf-8 -*-
"""Schaltplan-Generator der Dimmer-Module v3 (1, 3 und 4 Kanaele).

EIN Generator fuer alle drei Vertragsvarianten (stack_spec.MODULTYPEN:
0x10 Dimmer1, 0x11 Dimmer3, 0x12 Dimmer4). Aufbau je Modul:

  * Pico-Reihen J1 (Pins 1..20) und J2 (Pins 21..40): jeder Pin bekommt
    die Rolle aus stack_spec.PIN_ROLLE -- GND/3V3/VSYS als Netz, die
    hier benutzten GPIO als Label "GP<n>", alles andere no_connect.
    Kein Pin ist "frei" (v1-Lektion: ein Pin, der frei hiess, war es
    dreimal nicht).
  * Stapel-Leistungsreihe J3 (VIN, VIN, GND, GND), Qwiic J4 (GND, 3V3,
    SDA, SCL), User-Header J10 (GP0..GP3, 3V3, GND).
  * Slot-Matrix: je Kanal n vier 0-Ohm-Plaetze JB<n>A..JB<n>D nach
    BAENKE[bank][n-1]; bestueckt ist nur die Bank-Vorgabe (Dimmer = B),
    die anderen drei stehen als DNP im Blatt (Loetplatz vorhanden).
  * Versorgungszelle (tools/sch/versorgung.py): Klemme J90, Verpolschutz,
    TVS, Buck, VSYS-Diode.
  * Je Kanal n: Low-Side-N-MOSFET Qn (NCE6020AK) mit Gate-Vorwiderstand
    RGn (100 Ohm) vom Signal S<n>, Gate-Pulldown RPn (100 k), Freilauf-
    diode Dn (SS36C, Drain -> VIN) und Klemme Jn (1 = VIN, 2 =
    geschaltetes Minus der Last).

GATE DIREKT AM 3,3-V-GPIO: NCE6020AK ist bei VGS = 3,3 V nicht voll
durchgesteuert (Datenblatt nennt RDS(on) bei 10 V und 4,5 V). Das
vierkanalige LED-Dimmer-Board des Espace des Inventions treibt die
NCE60xx-Familie seit Inbetriebnahme direkt aus 3,3-V-GPIO und bleibt
bei 3 A je Kanal handwarm. Am ersten bestueckten v3-Board nachmessen.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import stack_spec as S  # noqa: E402
import versorgung        # noqa: E402

FP_R0805 = versorgung.FP_R0805
FP_TO252 = "Package_TO_SOT_SMD:TO-252-3_TabPin2"
FP_SMC = versorgung.FP_SMC
FP_KLEMME = S.FP_KLEMME_35

QK_WERT, QK_LCSC = "NCE6020AK", "C108639"
DK_WERT, DK_LCSC = "SS36C", "C16237"
RG_WERT, RG_LCSC = "100", "C17408"
RP_WERT, RP_LCSC = "100k", "C149504"

VARIANTEN = {1: 0x10, 3: 0x11, 4: 0x12}
FAMILIE = "Dimmer"


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:D_Schottky", "Device.kicad_sym", "D_Schottky")
    sch.lib("Transistor_FET:Q_NMOS_GDS", "Transistor_FET.kicad_sym", "Q_NMOS_GDS")
    sch.lib("Connector:Screw_Terminal_01x02", "Connector.kicad_sym",
            "Screw_Terminal_01x02")
    sch.lib("Connector_Generic:Conn_01x20", "Connector_Generic.kicad_sym", "Conn_01x20")
    sch.lib("Connector_Generic:Conn_01x04", "Connector_Generic.kicad_sym", "Conn_01x04")
    sch.lib("Connector_Generic:Conn_01x06", "Connector_Generic.kicad_sym", "Conn_01x06")
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")


# ------------------------------------------------------------ Pico-Reihen
def benutzte_gp(kanaele):
    """GPIO, die dieses Modul an den Pico-Reihen verdrahtet."""
    gp = set(S.USER_GP) | set(S.RESERVIERT) - {6}     # GP0..3, I2C
    for bank in S.BAENKE:
        for n in range(1, kanaele + 1):
            gp.add(S.MATRIX_GP(n, bank))
    return gp


def pico_reihen(sch, ox, oy, gp_benutzt):
    """J1 (Pico 1..20) und J2 (Pico 21..40), jede Rolle aus PIN_ROLLE."""
    sch.bauteil("J1", "Connector_Generic:Conn_01x20", (ox, oy),
                "Pico 1..20 (Stapelbuchse)", S.FP_STAPEL_20, roff=(2.54, -27.94),
                voff=(2.54, -25.4))
    sch.bauteil("J2", "Connector_Generic:Conn_01x20", (ox, oy + 76.2),
                "Pico 21..40 (Stapelbuchse)", S.FP_STAPEL_20, roff=(2.54, -27.94),
                voff=(2.54, -25.4))
    for pico_pin in range(1, 41):
        ref, kontakt = ("J1", pico_pin) if pico_pin <= 20 else ("J2", pico_pin - 20)
        rolle = S.PIN_ROLLE[pico_pin]
        if rolle == "GND":
            sch.netz(ref, str(kontakt), "L", "GND")
        elif rolle == "3V3":
            sch.netz(ref, str(kontakt), "L", "3V3")
        elif rolle == "VSYS":
            sch.netz(ref, str(kontakt), "L", "VSYS")
        elif pico_pin in S.PIN_GP and S.PIN_GP[pico_pin] in gp_benutzt:
            sch.netz(ref, str(kontakt), "L", "GP%d" % S.PIN_GP[pico_pin])
        else:
            sch.nc(ref, str(kontakt))
    # PWR_FLAGs: GND/3V3 haben an diesem Blatt keinen power_out-Pin.
    sch.bauteil("#FLG1", "power:PWR_FLAG", (ox + 25.4, oy - 40.64), "PWR_FLAG", "")
    sch.netz("#FLG1", "1", "D", "GND")
    sch.bauteil("#FLG2", "power:PWR_FLAG", (ox + 40.64, oy - 40.64), "PWR_FLAG", "")
    sch.netz("#FLG2", "1", "D", "3V3")


def stecker(sch, ox, oy):
    """J3 Leistungsreihe, J4 Qwiic, J10 User-Header."""
    sch.bauteil("J3", "Connector_Generic:Conn_01x04", (ox, oy),
                "Stapel VIN/GND", S.FP_STAPEL_4, roff=(2.54, -7.62), voff=(2.54, -5.08))
    for k, netz in S.STECKER_POS["leistung"]["pins"].items():
        sch.netz("J3", str(k), "L", netz)
    sch.bauteil("J4", "Connector_Generic:Conn_01x04", (ox, oy + 25.4),
                "Qwiic", S.FP_QWIIC, roff=(2.54, -7.62), voff=(2.54, -5.08))
    qw = {"GND": "GND", "3V3": "3V3", "I2C_SDA": "GP4", "I2C_SCL": "GP5"}
    for k, rolle in S.QWIIC_PINS.items():
        sch.netz("J4", str(k), "L", qw[rolle])
    sch.bauteil("J10", "Connector_Generic:Conn_01x06", (ox, oy + 55.88),
                "User GP0..GP3", S.FP_USER, roff=(2.54, -10.16), voff=(2.54, -7.62))
    for k, rolle in S.USER_PINS.items():
        sch.netz("J10", str(k), "L", rolle)


# ------------------------------------------------------------ Slot-Matrix
def matrix(sch, ox, oy, signale, bank_vorgabe):
    """Je Signal n und Bank b ein 0-Ohm-Platz JB<n><b>: GP -> S<n>."""
    for i, n in enumerate(range(1, signale + 1)):
        for j, bank in enumerate(sorted(S.BAENKE)):
            ref = S.MATRIX_REF(n, bank)
            gp = S.MATRIX_GP(n, bank)
            x, y = ox + 27.94 * j, oy + 15.24 * i
            # rot=90: Pin 1 links, Pin 2 rechts.
            sch.bauteil(ref, "Device:R", (x, y), S.MATRIX_WERT, S.MATRIX_FOOTPRINT,
                        rot=90, roff=(0, -3.81), voff=(0, 3.81),
                        dnp=(bank != bank_vorgabe), felder={"LCSC": S.MATRIX_LCSC})
            sch.netz(ref, "1", "L", "GP%d" % gp)
            sch.netz(ref, "2", "R", "S%d" % n)


# ------------------------------------------------------------ Kanal
def _kanal(sch, n, ox, oy):
    q, rg, rp, d, j = ("Q%d" % n, "RG%d" % n, "RP%d" % n, "D%d" % n, "J%d" % (4 + n))
    sig, led = "S%d" % n, "LED%d" % n

    sch.bauteil(q, "Transistor_FET:Q_NMOS_GDS", (ox, oy), QK_WERT, FP_TO252,
                rot=0, roff=(2.54, 2.54), voff=(2.54, 5.08), felder={"LCSC": QK_LCSC})
    sch.netz(q, "1", "L", sig + "_G")   # G, hinter RGn
    sch.netz(q, "2", "U", led)          # D -> Klemme (Minus der Last)
    sch.netz(q, "3", "D", "GND")        # S

    sch.bauteil(rg, "Device:R", (ox - 17.78, oy + 10.16), RG_WERT, FP_R0805,
                rot=90, roff=(-1.27, -2.54), voff=(1.27, -2.54), felder={"LCSC": RG_LCSC})
    sch.netz(rg, "1", "L", sig)
    sch.netz(rg, "2", "R", sig + "_G")

    sch.bauteil(rp, "Device:R", (ox - 12.7, oy + 12.7), RP_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27), felder={"LCSC": RP_LCSC})
    sch.netz(rp, "1", "U", sig + "_G")
    sch.netz(rp, "2", "D", "GND")

    # Freilauf: Kathode an VIN. LED-Baender sind ohmsch, die Zuleitung
    # ist eine Induktivitaet.
    sch.bauteil(d, "Device:D_Schottky", (ox + 12.7, oy + 10.16), DK_WERT, FP_SMC,
                rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54), felder={"LCSC": DK_LCSC})
    sch.netz(d, "1", "U", "VIN")        # K
    sch.netz(d, "2", "D", led)          # A

    sch.bauteil(j, "Connector:Screw_Terminal_01x02", (ox + 27.94, oy),
                "LED-Kanal %d" % n, FP_KLEMME, rot=0, roff=(2.54, -2.54),
                voff=(2.54, 2.54), felder={"LCSC": "C474892"})
    sch.netz(j, "1", "R", "VIN")
    sch.netz(j, "2", "R", led)


# ------------------------------------------------------------ Blatt
def bauen(sch, ox, oy, kanaele):
    _load_libs(sch)
    bank = S.BANK_VORGABE[FAMILIE]
    pico_reihen(sch, ox, oy, benutzte_gp(kanaele))
    stecker(sch, ox, oy + 165.1)
    matrix(sch, ox + 76.2, oy - 20.32, kanaele, bank)
    versorgung.bauen(sch, ox + 215.9, oy - 20.32)
    for n in range(1, kanaele + 1):
        _kanal(sch, n, ox + 241.3 + 71.12 * (n - 1), oy + 127.0)
    sch.text(ox + 215.9, oy - 45.72,
             "%s %s -- Vertrag v%d -- Bank-Vorgabe %s (JB*%s bestueckt)"
             % (S.PROJEKTNAME, S.MODULTYPEN[VARIANTEN[kanaele]]["name"],
                S.VERTRAG_VERSION, bank, bank), size=2.0, bold=True)


DATUM = "2026-11-15"
_ZIELE = {
    k: os.path.join(HERE, "..", "..", "hardware", "kicad", "dimmer%d" % k,
                    "Dimmer%d.kicad_sch" % k)
    for k in VARIANTEN
}


def erzeugen(ziel=None, kanaele=1):
    """Baut den Schaltplan einer Variante (Vorgabe: Dimmer1)."""
    import gen

    name = S.MODULTYPEN[VARIANTEN[kanaele]]["name"]
    sch = gen.Schaltplan(name, name, DATUM, papier="A2")
    bauen(sch, 60.96, 88.9, kanaele)
    pfad = _ZIELE[kanaele] if ziel is None else ziel
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    return sch.schreiben(pfad)


if __name__ == "__main__":
    for k in sorted(VARIANTEN):
        print(erzeugen(kanaele=k))

# -*- coding: utf-8 -*-
"""Erzeugt BOM und CPL im JLCPCB-Format fuer eine PicoStack-Platine.

    python3 tools/jlc.py sockel
    python3 tools/jlc.py motor

Liest hardware/fertigung/<board>/pos.csv (kicad-cli pcb export pos) und
schreibt hardware/fertigung/<board>/jlc-bom.csv und jlc-cpl.csv.

Konventionen woertlich aus dem LED-Dimmer-Generator uebernommen
(~/Dokumente/Espace_des_Inventions/led_dimmer/hardware/generator/
gen_jlc.py), inklusive der bindenden Regel: LCSC-Nummern stehen nur
dort, wo sie von einer Produktseite stammen (geprueft=True); sonst
bleibt das Feld leer und die Beschreibung so genau, dass JLCs
BOM-Abgleich eindeutig trifft. Nicht bestueckte Positionen fallen aus
BEIDEN Dateien heraus -- steht ein Designator in der CPL, den die BOM
nicht kennt, weist JLC den Auftrag zurueck; fehlt umgekehrt ein
BOM-Designator in der CPL, bricht dieses Skript ab.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stack_spec as S  # noqa: E402  (Kennwiderstaende aus dem Typcode)

REPO = os.path.join(HERE, "..")

# Gepruefte Nummern aus dem LED-Dimmer-Projekt (dort von der
# LCSC-Produktseite uebernommen, Bauform identisch):
LCSC_KLEMME_508_2P = "C395868"    # DB128L-5.08-2P, passt aufs MKDS-3/2-Bild
LCSC_K7805 = "C909765"            # K7805-1000R3 (DEXU), SIP-3, 6-30 V
                                  # Eingang, 5 V / 1 A. ZWEITER Ersatz
                                  # 2026-09-07: C2931187 (DEXU 2 A) ist
                                  # abgekuendigt, und der erste Ersatz
                                  # C5378008 (JETEKPS "K7805-2000R3")
                                  # vertraegt laut LCSC-Rohdaten nur
                                  # 7-18 V -- an 24 V unbrauchbar.
                                  # 1-A-Herleitung und Datenblattzitat in
                                  # tools/sch/sockelplatine.py
LCSC_NMOS_TO252 = "C108639"       # NCE6020AK, 60 V 20 A N-MOSFET,
                                  # TO-252 -- Ersatz 2026-09-04 fuer den
                                  # bei JLC/LCSC ausverkauften NCE6050KA
                                  # (C96013); Herleitung in
                                  # tools/sch/dimmermodul.py

# Gepruefte Nummern aus hardware/bauteile.md / bauteile-1b.md (dort
# jeweils mit LCSC-Produktseite belegt):
LCSC_MCU = "C5456198"             # STM32C011F6P6, TSSOP-20
LCSC_1G175 = "C202238"            # SN74LVC1G175DCKR, SC-70-6
LCSC_2G00 = "C206109"             # SN74LVC2G00DCUR, VSSOP-8
LCSC_1G08 = "C7832"               # SN74LVC1G08DCKR, SC-70-5
LCSC_1G06 = "C7828"               # SN74LVC1G06DCKR, SC-70-5, Open-Drain
LCSC_PMOS_TO252 = "C2624"         # IRFR5305PbF, P-Kanal, D-Pak
LCSC_PC817 = "C97308"             # PC817X1CSP9F, SMD-Gullwing
LCSC_R3K3_1206 = "C26032"         # 1206W4F3301T5E, 3,3 kOhm 250 mW
LCSC_R10K_0805 = "C17414"         # 0805W8F1002T5E, 10 kOhm
LCSC_SMCJ30A = "C340696"          # SMCJ30A, DO-214AB (sockelplatine.py)

# Am 2026-09-04 fuer die Dimmer-Bestellung an der jeweiligen
# LCSC-Produktseite gesichtet:
LCSC_R100R_0805 = "C17408"        # 0805W8F1000T5E, 100 Ohm 1% (8,2 Mio Lager)
LCSC_SS36C = "C16237"             # MDD SS36C -- Achtung: das MDD "SS36"
                                  # (C16015) ist SMA! Der C-Suffix ist SMC
LCSC_ELKO_220U35 = "C45078"       # Chengx GR227M..., 220u 35V D8x12 RM3.5
LCSC_KLEMME_35_2P = "C474892"     # KF350-3.5-2P, 3,5mm 2P 10A 300V --
                                  # THT-Klon zum Phoenix-PT-Footprint,
                                  # Sitz im JLC-Preview gegenpruefen
LCSC_R100K_0805 = "C149504"       # 0805W8F1003T5E, 100 kOhm. Achtung:
                                  # denselben Widerstand gibt es bei LCSC
                                  # doppelt -- C17407 traegt den Vermerk
                                  # "SMT-Geschaeft vorbehalten" und
                                  # meldete im JLC-Dialog trotzdem
                                  # shortfall; C149504 ist der Eintrag
                                  # der JLC-Bestueckungsbibliothek
                                  # (jlcpcb.com/partdetail/160838-.../
                                  # C149504). JLCs Auto-Match C5713386
                                  # war ebenfalls leer
LCSC_R680R_0805 = "C17798"        # 0805W8F6800T5E, 680 Ohm (JLC-Basic)
LCSC_R1K5_0805 = "C4310"          # 0805W8F1501T5E, 1,5 kOhm (JLC-Basic)
LCSC_R0_0805 = "C17477"           # 0805W8F0000T5E, 0-Ohm-Bruecke

# JLC-Bestellrunde 3 (2026-09-07): headless-Chrome-Sichtung der
# JLC-Teileseiten (componentLibraryType/overseasStockCount im
# Seiten-JSON). Alles hier ist "base" (JLC-Basic: keine 3-$-Feeder-
# Gebuehr, matcht und selektiert automatisch):
LCSC_C100N_0805 = "C49678"        # YAGEO CC0805KRX7R9BB104, 100n 50V X7R
LCSC_C1U_0805 = "C28323"          # Samsung CL21B105KBFNNNE, 1u 50V X7R
LCSC_C22U_0805 = "C45783"         # Samsung CL21A226MAQNNNE, 22u 25V X5R
LCSC_R4K7_0805 = "C17673"         # 0805W8F4701T5E, 4,7 kOhm

# Kennwiderstands-Stufen (stack_spec.ID_WIDERSTAENDE) -> gesichtete
# Nummer, soweit eine Stufe von einem existierenden Modultyp gebraucht
# wird. Fehlt eine Stufe hier, bleibt das LCSC-Feld schlicht leer.
LCSC_KENN = {0: LCSC_R0_0805, 680: LCSC_R680R_0805, 1500: LCSC_R1K5_0805}


def _kenn(typcode):
    """BOM-Zeilen fuer die Kennwiderstaende eines Modultyps."""
    r0, r1 = S.TYPCODE_WIDERSTAENDE(typcode)

    def fmt(r):
        if r == 0:
            return "0Ohm Bruecke 0805"
        if r >= 1000:
            return "%gkOhm 0805 1%%" % (r / 1000.0)
        return "%gOhm 0805 1%%" % r

    return [
        (fmt(r0) + " (Kennwiderstand ID0)", ["R100"],
         LCSC_KENN.get(int(r0), ""), int(r0) in LCSC_KENN),
        (fmt(r1) + " (Kennwiderstand ID1)", ["R101"],
         LCSC_KENN.get(int(r1), ""), int(r1) in LCSC_KENN),
    ]


# JLCs Bauteilbibliothek hat fuer einige Gehaeusefamilien eine andere
# Null-Drehung als KiCad -- im Bestueckungs-Preview standen U100-U103
# verdreht (Bestellrunde 2026-09-07). Korrekturwinkel aus den beiden
# Community-Datenbanken, die sich fuer genau diese Familien einig sind
# (JLCKicadTools cpl_rotations_db.csv und Fabrication-Toolkit
# transformations.csv, beide am 2026-09-07 gesichtet); angewandt wie
# dort: (KiCad-Winkel + Korrektur) mod 360. TO-252 steht bewusst in
# KEINER der beiden Tabellen (die NCE-FETs lagen im Preview richtig);
# das verdrehte IRFR5305-Modell ist eine Teil-Eigenheit, die nur im
# Preview selbst zu richten ist. Erster Treffer gewinnt.
ROT_KORREKTUR = (
    ("SOT-353", 180.0),
    ("SOT-363", 180.0),
    ("TSSOP-", 270.0),
    ("VSSOP-8_", 180.0),   # gilt fuer unsere 2.3x2mm-Variante; die
                           # 3.0x3.0-Variante braeuchte laut beiden
                           # Datenbanken 270
)


def _jlc_winkel(package, rot):
    for praefix, delta in ROT_KORREKTUR:
        if package.startswith(praefix):
            return (rot + delta) % 360.0
    return rot


# Stapel-Steckerteile werden IMMER von Hand bestueckt: die Kontakte
# muessen im gesteckten Verbund fluchten (stack_spec.MONTAGE_REGEL --
# erst stecken, dann schrauben), und ein maschinell schief gesetzter
# SMD-Stecker laesst sich nicht nachbiegen.
_STECKER_HAND = ("von Hand - im gesteckten Verbund ausgerichtet, damit "
                 "die Stapelkontakte ohne Zwang fluchten (MONTAGE_REGEL)")

def _dimmer(kanaele, typcode):
    """BOM/Unbestueckt-Definition einer Dimmer-Variante."""
    bom = [
        ("100nF 50V X7R 0805",                ["C100"], LCSC_C100N_0805,
         True),
        ("1uF 50V X7R 0805",                  ["C101"], LCSC_C1U_0805,
         True),
        ("100kOhm 0805 1%",
         ["R102"] + ["RP%d" % n for n in range(1, kanaele + 1)],
         LCSC_R100K_0805, True),
        ("100Ohm 0805 1%",
         ["RG%d" % n for n in range(1, kanaele + 1)],
         LCSC_R100R_0805, True),
        ("10kOhm 0805 1%",
         ["R11", "R12", "R104", "R105"],       LCSC_R10K_0805, True),
        ("220uF 35V Elko radial D8 RM3.5",    ["C12"],
         LCSC_ELKO_220U35, True),
        ("SMCJ30A TVS unidirektional DO-214AB", ["D10"],
         LCSC_SMCJ30A, True),
        ("SS36C Schottky 60V 3A DO-214AB (SMC)",
         ["D%d" % n for n in range(1, kanaele + 1)],
         LCSC_SS36C, True),
        ("IRFR5305 P-MOSFET -55V TO-252",     ["Q10"],
         LCSC_PMOS_TO252, True),
        ("NCE6020AK N-MOSFET 60V 20A TO-252",
         ["Q%d" % n for n in range(1, kanaele + 1)],
         LCSC_NMOS_TO252, True),
        ("KF350-3.5-2P Klemme 3.5mm 2P 10A",
         ["J%d" % (4 + n) for n in range(1, kanaele + 1)],
         LCSC_KLEMME_35_2P, True),
        ("SN74LVC1G08DCKR AND SC-70-5",       ["U103"], LCSC_1G08, True),
        ("SN74LVC1G175DCKR D-Flipflop SC-70-6", ["U101"],
         LCSC_1G175, True),
        ("SN74LVC2G00DCUR Dual-NAND VSSOP-8", ["U102"], LCSC_2G00, True),
        ("STM32C011F6P6 MCU TSSOP-20",        ["U100"], LCSC_MCU, True),
    ] + _kenn(typcode)
    unbestueckt = {
        "J100": "Stapelstecker 2x20 " + _STECKER_HAND,
        "J101": "Kettenstecker Buchse (SMD) " + _STECKER_HAND,
        "J102": "Kettenstecker Stift (SMD) " + _STECKER_HAND,
        "J103": "Leistungsstecker Buchse (SMD) " + _STECKER_HAND,
        "J104": "Leistungsstecker Stift (SMD) " + _STECKER_HAND,
    }
    return {"pcb": "Dimmer%d" % kanaele, "bom": bom,
            "unbestueckt": unbestueckt}


BOARDS = {
    "dimmer1": None,   # unten gefuellt (braucht _kenn/_STECKER_HAND)
    "dimmer3": None,
    "dimmer4": None,
    "sockel": {
        "pcb": "Sockelplatine",
        "bom": [
            ("100nF 50V X7R 0805",                ["C1"],
             LCSC_C100N_0805, True),
            ("22uF 25V X5R 0805",                 ["C2"],
             LCSC_C22U_0805, True),
            ("220uF 35V Elko radial D8 RM3.5",    ["C3"],
             LCSC_ELKO_220U35, True),
            ("SMCJ30A TVS unidirektional DO-214AB", ["D1"],
             LCSC_SMCJ30A, True),
            ("DB128L-5.08-2P-GN-S Klemme 16A 300V", ["J1"],
             LCSC_KLEMME_508_2P, True),
            ("4.7kOhm 0805 1%",                   ["R1", "R2"],
             LCSC_R4K7_0805, True),
            ("K7805-1000R3 DC/DC 5V 1A 6-30V SIP-3", ["U2"],
             LCSC_K7805, True),
        ],
        "unbestueckt": {
            "U1": "Pico-Buchsenleisten von Hand - 2 Streifen, mit "
                  "gestecktem Pico ausgerichtet",
            "J2": "Stapelstecker 2x20 " + _STECKER_HAND,
            "J3": "Kettenstecker (SMD-Stift) " + _STECKER_HAND,
            "J4": "Leistungsstecker (SMD-Stift) " + _STECKER_HAND,
        },
    },
    "motor": {
        "pcb": "Motormodul",
        "bom": [
            ("22nF 50V X7R 0805",                 ["C10"],       "", False),
            ("100nF 50V X7R 0805",
             ["C9", "C11", "C13", "C14", "C15", "C16", "C100"],
             LCSC_C100N_0805, True),
            ("1uF 50V X7R 0805",                  ["C101"],
             LCSC_C1U_0805, True),
            ("100kOhm 0805 1%",                   ["R102"],
             LCSC_R100K_0805, True),
            ("220uF 35V Elko radial D8 RM3.5",    ["C12"],
             LCSC_ELKO_220U35, True),
            ("SMCJ30A TVS unidirektional DO-214AB", ["D1"],
             LCSC_SMCJ30A, True),
            ("DB128L-5.08-2P-GN-S Klemme 16A 300V", ["J5"],
             LCSC_KLEMME_508_2P, True),
            ("Stiftleiste 1x04 2.54mm THT",       ["J3"],        "", False),
            ("IRFR5305 P-MOSFET -55V TO-252",     ["Q1"],
             LCSC_PMOS_TO252, True),
            ("100Ohm 0805 1%",                    ["R7", "R8", "R9"],
             LCSC_R100R_0805, True),
            ("1.3kOhm 0805 1%",                   ["R5"],        "", False),
            ("3.3kOhm 1206 1%",
             ["R16", "R17", "R18", "R19"],         LCSC_R3K3_1206, True),
            ("4.7kOhm 0805 1%",                   ["R20", "R21"],
             LCSC_R4K7_0805, True),
            ("10kOhm 0805 1%",
             ["R11", "R12", "R13", "R15", "R104", "R105"],
             LCSC_R10K_0805, True),
            ("DRV8876PWPR H-Bruecke HTSSOP-16 PowerPAD", ["U1"],  "", False),
            ("SN74LVC1G08DCKR AND SC-70-5",       ["U3", "U103"],
             LCSC_1G08, True),
            ("SN74LVC1G06DCKR Inverter OD SC-70-5", ["U6", "U7"],
             LCSC_1G06, True),
            ("SN74LVC1G175DCKR D-Flipflop SC-70-6", ["U101"],
             LCSC_1G175, True),
            ("SN74LVC2G00DCUR Dual-NAND VSSOP-8", ["U102"],
             LCSC_2G00, True),
            ("STM32C011F6P6 MCU TSSOP-20",        ["U100"], LCSC_MCU, True),
            ("PC817 Optokoppler SMD Gullwing",    ["U4", "U5"],
             LCSC_PC817, True),
        ] + _kenn(0x01),
        "unbestueckt": {
            "R10": "Stromgrenze, ab Werk unbestueckt",
            "J100": "Stapelstecker 2x20 " + _STECKER_HAND,
            "J101": "Kettenstecker Buchse (SMD) " + _STECKER_HAND,
            "J102": "Kettenstecker Stift (SMD) " + _STECKER_HAND,
            "J103": "Leistungsstecker Buchse (SMD) " + _STECKER_HAND,
            "J104": "Leistungsstecker Stift (SMD) " + _STECKER_HAND,
        },
    },
}


BOARDS["dimmer1"] = _dimmer(1, 0x10)
BOARDS["dimmer3"] = _dimmer(3, 0x11)
BOARDS["dimmer4"] = _dimmer(4, 0x12)


def erzeugen(board):
    b = BOARDS[board]
    verz = os.path.join(REPO, "hardware", "fertigung", board)
    bestueckt = [r for _, refs, _, _ in b["bom"] for r in refs]

    platz = {}
    with open(os.path.join(verz, "pos.csv")) as f:
        for r in csv.DictReader(f):
            platz[r["Ref"]] = r

    # KiCads Positionsexport liefert den Footprint-ANKER; bei den
    # THT-Familien liegt der auf Pin 1 statt in der Bauteilmitte, und
    # JLC setzt sein Modell auf Mid X/Y (Elko und Klemmen schwebten im
    # Bestueckungs-Preview 1,75 mm neben ihren Loechern, Runde
    # 2026-09-07). tools/pcb/zentroide.py schreibt die echten
    # Pad-Zentroiden aus pcbnew; nur diese Familien werden ersetzt --
    # bei SMD ist der Anker die Gehaeusemitte und damit schon richtig
    # (TO-252: Pad-Zentroid waere FALSCH, er liegt neben dem Gehaeuse).
    _THT_PIN1_ANKER = ("CP_Radial", "TerminalBlock", "PinHeader",
                       "Converter_DCDC")   # U2 (SIP-3) ankert ebenfalls
                                           # auf Pin 1 -- fiel erst im
                                           # Sockel-Preview auf (2026-09-07)
    betroffen = [ref for ref, r in platz.items()
                 if r["Package"].startswith(_THT_PIN1_ANKER)]
    if betroffen:
        zdatei = os.path.join(verz, "zentroide.csv")
        if not os.path.exists(zdatei):
            raise SystemExit(
                "%s: %s brauchen Pad-Zentroiden, aber %s fehlt -- "
                "tools/pcb/kipy tools/pcb/zentroide.py ausfuehren"
                % (board, ", ".join(sorted(betroffen)), zdatei))
        with open(zdatei) as f:
            mitte = {r["Ref"]: r for r in csv.DictReader(f)}
        for ref in betroffen:
            platz[ref]["PosX"] = mitte[ref]["MidX"]
            platz[ref]["PosY"] = mitte[ref]["MidY"]

    # Vollstaendigkeitsabgleich in beide Richtungen: jede Position der
    # Platine ist entweder bestueckt oder mit Begruendung unbestueckt.
    alle = set(platz) | {"U1"} if board == "sockel" else set(platz)
    # (Der Pico U1 des Sockels ist THT ohne SMD-Pads und fehlt in der
    # pos.csv -- er gehoert trotzdem begruendet in die Liste.)
    offen = alle - set(bestueckt) - set(b["unbestueckt"])
    offen = {r for r in offen if not r.startswith("H")}   # M3-Bohrungen
    if offen:
        raise SystemExit("%s: weder bestueckt noch begruendet: %s"
                         % (board, ", ".join(sorted(offen))))

    with open(os.path.join(verz, "jlc-bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for kommentar, refs, lcsc, _ in b["bom"]:
            fp = platz.get(refs[0], {}).get("Package", "")
            w.writerow([kommentar, ",".join(refs), fp, lcsc])

    rows = []
    for ref in bestueckt:
        r = platz.get(ref)
        if r is None:
            continue
        rows.append([ref, "%.4fmm" % float(r["PosX"]),
                     "%.4fmm" % float(r["PosY"]),
                     "Top" if r["Side"] == "top" else "Bottom",
                     "%.0f" % _jlc_winkel(r["Package"], float(r["Rot"]))])
    gefunden = {r[0] for r in rows}
    fehlend = [r for r in bestueckt if r not in gefunden]

    with open(os.path.join(verz, "jlc-cpl.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows(sorted(rows))

    with open(os.path.join(verz, "UNBESTUECKT.txt"), "w") as f:
        for ref in sorted(b["unbestueckt"]):
            f.write("%-6s %s\n" % (ref, b["unbestueckt"][ref]))

    print("%s: BOM %d Zeilen (%d Bauteile), CPL %d Positionen, "
          "%d unbestueckt (begruendet)"
          % (board, len(b["bom"]), len(bestueckt), len(rows),
             len(b["unbestueckt"])))
    if fehlend:
        raise SystemExit("FEHLER: in der CPL fehlen %s -- JLC wuerde den "
                         "Auftrag zurueckweisen" % ", ".join(fehlend))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in BOARDS:
        raise SystemExit("Aufruf: jlc.py <%s>" % "|".join(sorted(BOARDS)))
    erzeugen(sys.argv[1])

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
LCSC_K7805 = "C2931187"           # K7805-2000R3, SIP-3
LCSC_NMOS_TO252 = "C96013"        # NCE6050KA, 60 V N-MOSFET, TO-252


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
        (fmt(r0) + " (Kennwiderstand ID0)", ["R100"], "", False),
        (fmt(r1) + " (Kennwiderstand ID1)", ["R101"], "", False),
    ]


# Stapel-Steckerteile werden IMMER von Hand bestueckt: die Kontakte
# muessen im gesteckten Verbund fluchten (stack_spec.MONTAGE_REGEL --
# erst stecken, dann schrauben), und ein maschinell schief gesetzter
# SMD-Stecker laesst sich nicht nachbiegen.
_STECKER_HAND = ("von Hand - im gesteckten Verbund ausgerichtet, damit "
                 "die Stapelkontakte ohne Zwang fluchten (MONTAGE_REGEL)")

def _dimmer(kanaele, typcode):
    """BOM/Unbestueckt-Definition einer Dimmer-Variante."""
    bom = [
        ("100nF 50V X7R 0805",                ["C100"],      "", False),
        ("1uF 25V X5R 0805",                  ["C101"],      "", False),
        ("100kOhm 0805 1%",
         ["R102"] + ["RP%d" % n for n in range(1, kanaele + 1)], "", False),
        ("100Ohm 0805 1%",
         ["RG%d" % n for n in range(1, kanaele + 1)],            "", False),
        ("10kOhm 0805 1%",
         ["R11", "R12", "R104", "R105"],                          "", False),
        ("220uF 35V Elko radial D8 RM3.5",    ["C12"],       "", False),
        ("SMCJ30A TVS unidirektional DO-214AB", ["D10"],     "", False),
        ("SS36 Schottky 60V 3A DO-214AB (SMC)",
         ["D%d" % n for n in range(1, kanaele + 1)],              "", False),
        ("IRFR5305 P-MOSFET -55V TO-252",     ["Q10"],       "", False),
        ("NCE6050KA N-MOSFET 60V TO-252",
         ["Q%d" % n for n in range(1, kanaele + 1)],
         LCSC_NMOS_TO252, True),
        ("PT 1,5/2-3,5-H Klemme 3.5mm 2P 13.5A",
         ["J%d" % (4 + n) for n in range(1, kanaele + 1)],        "", False),
        ("SN74LVC1G08DCKR AND SC-70-5",       ["U103"],      "", False),
        ("SN74LVC1G175DCKR D-Flipflop SC-70-6", ["U101"],    "", False),
        ("SN74LVC2G00DCUR Dual-NAND VSSOP-8", ["U102"],      "", False),
        ("STM32C011F6P6 MCU TSSOP-20",        ["U100"],      "", False),
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
            ("100nF 50V X7R 0805",                ["C1"],        "", False),
            ("22uF 25V X5R 0805",                 ["C2"],        "", False),
            ("220uF 35V Elko radial D8 RM3.5",    ["C3"],        "", False),
            ("SMCJ30A TVS unidirektional DO-214AB", ["D1"],      "", False),
            ("DB128L-5.08-2P-GN-S Klemme 16A 300V", ["J1"],
             LCSC_KLEMME_508_2P, True),
            ("4.7kOhm 0805 1%",                   ["R1", "R2"],  "", False),
            ("K7805-2000R3 DC/DC 5V 2A SIP-3",    ["U2"],
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
             ["C9", "C11", "C13", "C14", "C15", "C16", "C100"],  "", False),
            ("1uF 25V X5R 0805",                  ["C101"],      "", False),
            ("100kOhm 0805 1%",                   ["R102"],      "", False),
            ("220uF 35V Elko radial D8 RM3.5",    ["C12"],       "", False),
            ("SMCJ30A TVS unidirektional DO-214AB", ["D1"],      "", False),
            ("DB128L-5.08-2P-GN-S Klemme 16A 300V", ["J5"],
             LCSC_KLEMME_508_2P, True),
            ("Stiftleiste 1x04 2.54mm THT",       ["J3"],        "", False),
            ("IRFR5305 P-MOSFET -55V TO-252",     ["Q1"],        "", False),
            ("100Ohm 0805 1%",                    ["R7", "R8", "R9"], "", False),
            ("1.3kOhm 0805 1%",                   ["R5"],        "", False),
            ("3.3kOhm 1206 5%",
             ["R16", "R17", "R18", "R19"],                        "", False),
            ("4.7kOhm 0805 1%",                   ["R20", "R21"], "", False),
            ("10kOhm 0805 1%",
             ["R11", "R12", "R13", "R15", "R104", "R105"],        "", False),
            ("DRV8876PWPR H-Bruecke HTSSOP-16 PowerPAD", ["U1"],  "", False),
            ("SN74LVC1G08DCKR AND SC-70-5",       ["U3", "U103"], "", False),
            ("SN74LVC1G06DCKR Inverter OD SC-70-5", ["U6", "U7"], "", False),
            ("SN74LVC1G175DCKR D-Flipflop SC-70-6", ["U101"],     "", False),
            ("SN74LVC2G00DCUR Dual-NAND VSSOP-8", ["U102"],      "", False),
            ("STM32C011F6P6 MCU TSSOP-20",        ["U100"],      "", False),
            ("PC817 Optokoppler SMD Gullwing",    ["U4", "U5"],  "", False),
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
                     "%.0f" % float(r["Rot"])])
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

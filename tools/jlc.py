# -*- coding: utf-8 -*-
"""Erzeugt BOM und CPL im JLCPCB-Format fuer eine PicoStack-v3-Platine.

    python3 tools/jlc.py dimmer4

Liest hardware/fertigung/<board>/pos.csv (kicad-cli pcb export pos) und
zentroide.csv (tools/pcb/zentroide.py) und schreibt jlc-bom.csv,
jlc-cpl.csv und UNBESTUECKT.txt. Bindende Regel: LCSC-Nummern stehen
nur dort, wo sie von einer Produktseite stammen (geprueft=True); sonst
bleibt das Feld leer und die Beschreibung so genau, dass JLCs
BOM-Abgleich eindeutig trifft. Jede Position der Platine ist entweder
bestueckt oder mit Begruendung unbestueckt -- sonst bricht das Skript ab.

Die Stueckliste selbst kommt NICHT aus einer zweiten Liste hier, sondern
aus den Generatoren (tools/sch/versorgung.py TEILE, tools/sch/
dimmermodul.py): Wert und LCSC-Feld jedes Bauteils stehen dort einmal.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "sch"))
import stack_spec as S   # noqa: E402
import versorgung        # noqa: E402
import dimmermodul       # noqa: E402

REPO = os.path.join(HERE, "..")

# JLCs Bauteilbibliothek hat fuer einige Gehaeusefamilien eine andere
# Null-Drehung als KiCad (Bestellrunde 2026-09-07; JLCKicadTools
# cpl_rotations_db.csv und Fabrication-Toolkit transformations.csv).
ROT_KORREKTUR = (
    ("SOT-353", 180.0),
    ("SOT-363", 180.0),
    ("TSSOP-", 270.0),
    ("VSSOP-8_", 180.0),
    ("SOIC-8", 270.0),      # TI SOIC-8 in JLCs Bibliothek: Pin 1 links oben
                            # -> im Preview GEGENPRUEFEN (noch nicht bestellt)
)


def _jlc_winkel(package, rot):
    for praefix, delta in ROT_KORREKTUR:
        if package.startswith(praefix):
            return (rot + delta) % 360.0
    return rot


_STECKER_HAND = ("von Hand -- im gesteckten Verbund ausgerichtet, damit "
                 "die Stapelkontakte ohne Zwang fluchten (MONTAGE_REGEL)")


def _dimmer(kanaele):
    """BOM/Unbestueckt-Definition einer Dimmer-Variante (v3).

    Zeilen: (Kommentar, [Refs], LCSC, geprueft). Gleiche Teile werden
    zu einer Zeile gemergt (JLC will je Teil eine Zeile).
    """
    T = versorgung.TEILE
    zeilen = {}

    def add(kommentar, ref, lcsc):
        zeilen.setdefault((kommentar, lcsc), []).append(ref)

    # Versorgungszelle, Beschreibung aus TEILE (Wert) + Bauform
    beschreibung = {
        "Q90": "AOD409 P-MOSFET -60V 26A TO-252",
        "R91": "100kOhm 0805 1%",
        "D92": "BZT52C12 Zener 12V SOD-123",
        "D90": "SMCJ30A TVS unidirektional DO-214AB",
        "C90": "47uF 50V SMD-Elko 6.3x7.7",
        "C91": "10uF 50V X7R 1210",
        "C92": "10uF 50V X7R 1210",
        "U90": "TPS5430DDAR Buck 3A SOIC-8-EP",
        "C93": "10nF 50V X7R 0805",
        "L90": "SWPA6045S150MT 15uH 2A 6x6mm",
        "D93": "SS36C Schottky 60V 3A DO-214AB (SMC)",
        "C94": "100uF 16V SMD-Elko 6.3x7.7",
        "R92": "10kOhm 0603 1%",
        "R93": "3.3kOhm 0603 1%",
        "D91": "SS36C Schottky 60V 3A DO-214AB (SMC)",
        "LED90": "LED gruen 0805",
        "R94": "10kOhm 0805 1%",
        "J90": "KF350-3.5-2P Klemme 3.5mm 2P 10A",
    }
    for ref, text in beschreibung.items():
        add(text, ref, T[ref][2])
    for n in range(1, kanaele + 1):
        add("NCE6020AK N-MOSFET 60V 20A TO-252", "Q%d" % n, dimmermodul.QK_LCSC)
        add("SS36C Schottky 60V 3A DO-214AB (SMC)", "D%d" % n, dimmermodul.DK_LCSC)
        add("100Ohm 0603 1%", "RG%d" % n, dimmermodul.RG_LCSC)
        add("100kOhm 0603 1%", "RP%d" % n, dimmermodul.RP_LCSC)
        add("KF350-3.5-2P Klemme 3.5mm 2P 10A", "J%d" % (4 + n), "C474892")
        add("0Ohm 0603 Bruecke (Slot-Matrix, Bank %s)" % S.BANK_VORGABE["Dimmer"],
            S.MATRIX_REF(n, S.BANK_VORGABE["Dimmer"]), S.MATRIX_LCSC)
    add("JST SH SM04B-SRSS-TB 4P 1.0mm (Qwiic)", "J4", "C160404")

    bom = [(k[0], refs, k[1], bool(k[1])) for k, refs in zeilen.items()]
    unbestueckt = {
        "J1": "Stapelbuchse 1x20, Pico-Pins 1..20 " + _STECKER_HAND,
        "J2": "Stapelbuchse 1x20, Pico-Pins 21..40 " + _STECKER_HAND,
        "J3": "Stapelbuchse 1x4 (VIN/GND), aus 1x20 abgelaengt " + _STECKER_HAND,
        "J10": "Stiftleiste 1x6 (User GP0..3, 3V3, GND), von Hand",
    }
    for n in range(1, kanaele + 1):
        for bank in S.BAENKE:
            if bank != S.BANK_VORGABE["Dimmer"]:
                unbestueckt[S.MATRIX_REF(n, bank)] = (
                    "Slot-Matrix Bank %s: unbestueckt (0 Ohm 0603 "
                    "umloeten, um die Bank zu wechseln)" % bank)
    return {"pcb": "Dimmer%d" % kanaele, "bom": sorted(bom), "unbestueckt": unbestueckt}


BOARDS = {"dimmer1": _dimmer(1), "dimmer3": _dimmer(3), "dimmer4": _dimmer(4)}

# THT-Familien, deren KiCad-Anker auf Pin 1 liegt statt in der Mitte --
# JLC setzt sein Modell auf Mid X/Y (Bestellrunde 2026-09-07).
_THT_PIN1_ANKER = ("CP_Radial", "TerminalBlock", "PinHeader", "PinSocket")


def erzeugen(board):
    b = BOARDS[board]
    verz = os.path.join(REPO, "hardware", "fertigung", board)
    bestueckt = [r for _, refs, _, _ in b["bom"] for r in refs]

    platz = {}
    with open(os.path.join(verz, "pos.csv")) as f:
        for r in csv.DictReader(f):
            platz[r["Ref"]] = r

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

    offen = set(platz) - set(bestueckt) - set(b["unbestueckt"])
    offen = {r for r in offen if not r.startswith("H")}   # M3-Bohrungen
    if offen:
        raise SystemExit("%s: weder bestueckt noch begruendet: %s"
                         % (board, ", ".join(sorted(offen))))
    fehlt = set(bestueckt) - set(platz)
    if fehlt:
        raise SystemExit("%s: in der BOM, aber nicht auf der Platine: %s"
                         % (board, ", ".join(sorted(fehlt))))

    with open(os.path.join(verz, "jlc-bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for kommentar, refs, lcsc, _ in b["bom"]:
            fp = platz.get(refs[0], {}).get("Package", "")
            w.writerow([kommentar, ",".join(refs), fp, lcsc])

    rows = []
    for ref in bestueckt:
        r = platz[ref]
        rows.append([ref, "%.4fmm" % float(r["PosX"]), "%.4fmm" % float(r["PosY"]),
                     "Top" if r["Side"] == "top" else "Bottom",
                     "%.0f" % _jlc_winkel(r["Package"], float(r["Rot"]))])
    with open(os.path.join(verz, "jlc-cpl.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows(sorted(rows))

    with open(os.path.join(verz, "UNBESTUECKT.txt"), "w") as f:
        for ref in sorted(b["unbestueckt"]):
            f.write("%-6s %s\n" % (ref, b["unbestueckt"][ref]))

    ohne = [k for k, _r, l, _g in b["bom"] if not l]
    print("%s: BOM %d Zeilen (%d Bauteile), CPL %d Positionen, %d unbestueckt; "
          "ohne LCSC-Nummer: %s"
          % (board, len(b["bom"]), len(bestueckt), len(rows), len(b["unbestueckt"]),
             ", ".join(ohne) or "keine"))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in BOARDS:
        raise SystemExit("Aufruf: jlc.py <%s>" % "|".join(sorted(BOARDS)))
    erzeugen(sys.argv[1])

# -*- coding: utf-8 -*-
"""Erzeugt docs/vertrag.md aus tools/stack_spec.py (Vertrag v4).

    python3 tools/vertrag_doku.py

Das Dokument ist die lesbare Fassung des Vertrags fuer Modulbauer; die
Zahlen stammen ausschliesslich aus stack_spec.py. tests/
test_erzeugte_dateien.py prueft, dass die eingecheckte Datei dem
Generator entspricht.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stack_spec as S  # noqa: E402

ZIEL = os.path.join(HERE, "..", "docs", "vertrag.md")


def tabelle(kopf, zeilen):
    aus = ["| " + " | ".join(kopf) + " |", "|" + "---|" * len(kopf)]
    for z in zeilen:
        aus.append("| " + " | ".join(str(x) for x in z) + " |")
    return "\n".join(aus)


def erzeugen(ziel=None):
    pfad = ZIEL if ziel is None else ziel
    o = []
    o.append("# PicoStack -- Vertrag v%d" % S.VERTRAG_VERSION)
    o.append("")
    o.append("Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.")
    o.append("")
    o.append("## Umriss und Mechanik")
    o.append("")
    o.append(tabelle(("Groesse", "Wert"), [
        ("Platine", "%g x %g mm, Ecken R%g" % (S.BOARD_W, S.BOARD_H, S.CORNER_R)),
        ("Dicke", "%g mm" % S.PLATINE_DICKE),
        ("M3-Loecher", ", ".join("(%g\\|%g)" % h for h in S.M3_HOLES)
         + " -- Bohrung %g mm, Freihaltekreis %g mm" % (S.M3_DRILL, S.M3_KEEPOUT)),
        ("Stapelabstand", "%g mm (M3-Bolzen %g mm)" % (S.STAPEL_ABSTAND, S.STAPEL_ABSTAND)),
        ("Einstecktiefe", "%.1f mm; Luft Stiftende %.1f mm, Luft Buchsenoberkante %.1f mm"
         % (S.EINSTECKTIEFE_STAPEL(), S.LUFT_STIFTENDE(), S.LUFT_BUCHSENOBERKANTE())),
        ("Bauteilhoehe", "oben <= %g mm, unter dem Pico <= %g mm"
         % (S.BAUTEILHOEHE_OBEN_MAX, S.BAUTEILHOEHE_PICO_SCHATTEN_MAX)),
        ("Stapelleiste", "%s; %g A je Kontakt; Buchse %g mm, Stift %g mm"
         % (S.STECKER_STAPEL["mpn"], S.STECKER_STAPEL["strom_pro_kontakt_a"],
            S.STECKER_STAPEL["gehaeusehoehe_mm"],
            S.STECKER_STAPEL["stiftlaenge_unter_gehaeuse_mm"])),
        ("Verdreht aufgesetzt", "steckt nirgends (kleinster Stift-Kontakt-Abstand %.2f mm)"
         % S.VERDREHT_STECKT_NIRGENDS()[0]),
    ]))
    o.append("")
    o.append("## Pico-Lage")
    o.append("")
    o.append("Der Pico liegt quer, USB zur linken Kante, Antenne nach rechts. "
             "Pin 1 bei (%g\\|%g), Reihe 1..20 nach +x; Pin 21 bei (%g\\|%g), "
             "Reihe 21..40 nach -x. Reihenabstand %g mm."
             % (S.PICO_PIN1 + S.PICO_PIN21 + (S.PICO_REIHENABSTAND,)))
    o.append("")
    o.append("* Pico-Schatten (R1/R3): (%g\\|%g)-(%g\\|%g)" % S.PICO_SCHATTEN)
    o.append("* Antennenzone, kupferfrei auf beiden Lagen (P5): (%g\\|%g)-(%g\\|%g)" % S.ANTENNE_FREI)
    o.append("* Klemmenzone (R2): (%g\\|%g)-(%g\\|%g)" % S.KLEMMENZONE)
    o.append("")
    o.append("## Stapelstecker")
    o.append("")
    o.append(tabelle(("Platz", "Zweck", "Kontakt 1", "Drehung", "Hof"),
                     [(n, e["zweck"], "(%g\\|%g)" % e["pin1"], e["drehung"],
                       "(%g\\|%g)-(%g\\|%g)" % e["flaeche"])
                      for n, e in S.STECKER_POS.items()]))
    o.append("")
    o.append("Leistungsreihe: " + ", ".join("%d = %s" % kv for kv in
                                             sorted(S.STECKER_POS["leistung"]["pins"].items()))
             + " (%g A Durchleitung)." % S.STROMBUDGET["stapel_durchleitung_a"])
    o.append("Qwiic: " + ", ".join("%d = %s" % kv for kv in sorted(S.QWIIC_PINS.items())) + ".")
    o.append("User-Header: " + ", ".join("%d = %s" % kv for kv in sorted(S.USER_PINS.items())) + ".")
    o.append("")
    o.append("## Pinrollen")
    o.append("")
    o.append(tabelle(("Pico-Pin", "GP", "Rolle"),
                     [(p, "GP%d" % S.PIN_GP[p] if p in S.PIN_GP else "", S.PIN_ROLLE[p])
                      for p in range(1, 41)]))
    o.append("")
    o.append("Nicht belegbar: " + "; ".join("Pin %d: %s" % kv for kv in sorted(S.NICHT_BELEGBAR.items())))
    o.append("")
    o.append("## Baenke und Slot-Matrix")
    o.append("")
    o.append(tabelle(("Bank", "Signal 1", "Signal 2", "Signal 3", "Signal 4"),
                     [(b,) + tuple("GP%d" % g for g in gps) for b, gps in sorted(S.BAENKE.items())]
                     + [("ADC",) + tuple("GP%d" % g for g in S.ADC_BANK) + ("",)]))
    o.append("")
    o.append("Ein Modul belegt genau eine Bank; die Wahl trifft eine 0603-Matrix "
             "(%s, %s) mit den Referenzen J<Bank><Signal>, genau ein Platz je Signal "
             "bestueckt. Vorgabe ab Werk: %s; ADC: %s."
             % (S.MATRIX_WERT + " Ohm", S.MATRIX_LCSC,
                ", ".join("%s = %s" % kv for kv in sorted(S.BANK_VORGABE.items())),
                ", ".join("%s = GP%d" % kv for kv in sorted(S.ADC_VORGABE.items()))))
    o.append("")
    o.append("## Versorgung")
    o.append("")
    o.append(tabelle(("Zusage", "Wert"), [(k, v) for k, v in S.VERSORGUNG.items()]))
    o.append("")
    o.append(tabelle(("Strombudget", "Wert"),
                     [(k, v) for k, v in S.STROMBUDGET.items() if not k.endswith("quelle")]))
    o.append("")
    o.append("## Layoutregeln")
    o.append("")
    for k, r in S.LAYOUT_REGELN.items():
        o.append("* **%s** %s *(%s)*" % (k, r["text"], r["beleg"]))
    o.append("")
    o.append("## Auflagen")
    o.append("")
    for a in S.LAYOUT_AUFLAGEN:
        o.append("* " + a)
    o.append("")
    o.append("## Modultypen")
    o.append("")
    o.append(tabelle(("Code", "Name", "Familie", "Kanaele", "Signale", "ADC"),
                     [("0x%02X" % c, m["name"], m["familie"], m["kanaele"], m["signale"],
                       "ja" if m["adc"] else "nein") for c, m in sorted(S.MODULTYPEN.items())]))
    o.append("")
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    return pfad


if __name__ == "__main__":
    print("geschrieben:", erzeugen())

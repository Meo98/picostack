"""Erzeugt docs/vertrag.md aus tools/stack_spec.py.

Von Hand gepflegte Doppelungen laufen auseinander. Wer die
Steckerbelegung aendert, aendert stack_spec.py und laesst dieses
Skript laufen -- das Dokument hat keine eigene Wahrheit.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stack_spec as S

ZIEL = os.path.join(HERE, "..", "docs", "vertrag.md")


def tabelle(kopf, zeilen):
    aus = ["| " + " | ".join(kopf) + " |",
           "|" + "|".join(["---"] * len(kopf)) + "|"]
    aus += ["| " + " | ".join(str(z) for z in zeile) + " |"
            for zeile in zeilen]
    return "\n".join(aus)


def main():
    teile = ["# PicoStack — der Vertrag",
             "",
             "Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.",
             "",
             "## Status",
             "",
             "Die Zusagen rund um das Flashen -- die Leitungen "
             "`FLASH_TX`, `FLASH_RX`, `SEL`, `SEL_CLK` und `FLASH_MODE` "
             "(SEL seit 2026-08-31 auf dem eigenen Kettenstecker, alle "
             "anderen auf dem 2x20-Stapelstecker) und alles, "
             "was daran haengt -- ruhen auf einer Annahme, die noch "
             "**nicht auf Hardware belegt** ist: dass der Pico einen "
             "Modul-MCU ueber dessen ROM-Bootlader wirklich beschreiben "
             "kann. Geprueft ist bisher nur das Protokoll gegen eine "
             "Attrappe, nicht gegen echtes Silizium. Stand und offene "
             "Schritte: `docs/nachweis-2026-08.md`.",
             "",
             "## Umriss",
             "",
             "%.1f x %.1f mm, Ecken %.1f mm gerundet, %.1f mm zwischen "
             "den Platinen." % (S.BOARD_W, S.BOARD_H, S.CORNER_R,
                                S.STAPEL_ABSTAND),
             "",
             tabelle(["M3-Bohrung", "x", "y", "Bohrdurchmesser"],
                     [(i + 1, x, y, S.M3_DRILL) for i, (x, y) in
                      enumerate(S.M3_HOLES)]),
             "",
             "## Steckerbelegung",
             "",
             tabelle(["Pin", "Rolle"],
                     [(p, S.PIN_ROLLE[p]) for p in sorted(S.PIN_ROLLE)
                      if S.PIN_ROLLE[p] != "frei"]),
             "",
             "Alle nicht aufgefuehrten Pins gehen unveraendert durch "
             "und stehen Modulen frei zur Verfuegung.",
             "",
             "## Stapelstecker und Kettenstecker",
             "",
             "Der 2x20-Signalstecker (Steckerbelegung oben) ist ein "
             "**Stapelstecker**: %s. Bauteil: LCSC `%s`, "
             "Gehaeusehoehe %.2f mm, Stiftlaenge unterhalb des Gehaeuses "
             "%.2f mm. Quelle: %s." % (
                 S.STECKER_STAPEL["typ"], S.STECKER_STAPEL["buchse_lcsc"],
                 S.STECKER_STAPEL["gehaeusehoehe_mm"],
                 S.STECKER_STAPEL["stiftlaenge_unter_gehaeuse_mm"],
                 S.STECKER_STAPEL["quelle"]),
             "",
             "Einzige Ausnahme ist die Auswahlkette (`SEL`): sie muss "
             "von Modul zu Modul aufgetrennt werden (Schieberegister, "
             "`tools/kette.py`) und ist deshalb kein Pin des "
             "Stapelsteckers mehr. Sie laeuft ueber einen eigenen, "
             "zweipoligen **Kettenstecker** (%s): %s." % (
                 S.STECKER_KETTE["typ"], S.STECKER_KETTE["zweck"]),
             "",
             tabelle(["Pin (Kettenstecker)", "Rolle"],
                     [(p, r) for p, r in
                      sorted(S.STECKER_KETTE["pins"].items())]),
             "",
             "Ketten- und Leistungsstecker sind seit 2026-08-31 "
             "**SMD-Paare**: Buchse auf der Oberseite, Stiftleiste auf "
             "der Unterseite, am selben Ort. Zwei bedrahtete Haelften "
             "am selben Ort brauchten dieselben Bohrungen -- und "
             "dieselbe Bohrung ist derselbe Leiter, was beim "
             "Kettenstecker `SEL_IN` und `SEL_OUT` kurzschliessen "
             "wuerde. Einstecktiefe je %.2f mm, Luft zwischen "
             "Stiftkoerper und Buchsenoberkante %.2f mm." % (
                 S.EINSTECKTIEFE_KETTE(),
                 S.LUFT_STIFTKOERPER(S.STECKER_KETTE)),
             "",
             tabelle(["Stecker", "Bauart", "oben", "unten",
                      "Buchse LCSC", "Stift LCSC"],
                     [(name, st["typ"], st["montage_oben"],
                       st["montage_unten"],
                       "`%s`" % st["buchse_lcsc"] if st["buchse_lcsc"]
                       else "offen: " + st.get("buchse_spec", ""),
                       "`%s`" % st["stift_lcsc"] if st["stift_lcsc"]
                       else "offen: " + st.get("stift_spec", ""))
                      for name, st in (("stapel", S.STECKER_STAPEL),
                                       ("kette", S.STECKER_KETTE),
                                       ("leistung", S.STECKER_LEISTUNG))]),
             "",
             "Quellen: %s / %s / %s." % (S.STECKER_STAPEL["quelle"],
                                         S.STECKER_KETTE["quelle"],
                                         S.STECKER_LEISTUNG["quelle"]),
             "",
             "## Wo die Stecker sitzen",
             "",
             "Alle Masse in mm, Ursprung linke obere Ecke, x nach "
             "rechts, y nach unten. Diese Lage gilt fuer **jede** "
             "Platine im Stapel -- der Stapelstecker der Sockelplatine "
             "steht senkrecht ueber dem jedes Moduls, Ketten- und "
             "Leistungsstecker ebenso. Wer sie verschiebt, macht alle "
             "bereits gebauten Module unbrauchbar.",
             "",
             tabelle(["Stecker", "Zweck", "Mitte x", "Mitte y",
                      "Drehung", "belegte Flaeche (x0 y0 x1 y1)"],
                     [(name, S.STECKER_POS[name]["zweck"],
                       S.STECKER_POS[name]["mitte"][0],
                       S.STECKER_POS[name]["mitte"][1],
                       "%d Grad" % S.STECKER_POS[name]["drehung"],
                       " ".join("%.2f" % v
                                for v in S.STECKER_POS[name]["flaeche"]))
                      for name in ("stapel", "kette", "leistung")]),
             "",
             "Die belegte Flaeche ist die Vereinigung der Hoefe "
             "(F.CrtYd) aller Footprints an diesem Platz, nach der "
             "Drehung. Ketten- und Leistungsstecker bestehen "
             "auf jedem Modul aus zwei Haelften (SMD-Buchse oben, "
             "SMD-Stiftleiste unten); beide Haelften belegen "
             "**denselben** Platz, sonst treffen sie sich im Stapel "
             "nicht.",
             "",
             "Der Pico sitzt nur auf der Sockelplatine, mit Mitte "
             "(%.2f | %.2f), Drehung %d Grad, Flaeche %s. Unter seiner "
             "WLAN-Antenne liegt der Sperrbereich %s (%.1f x %.1f mm) "
             "-- dort darf kein Kupfer und kein Bauteil liegen "
             "(Raspberry Pi Pico W Datasheet, Release 7, Abschnitt "
             "2.2.1 \"Keep-out area\": Ausschnitt 14 x 9 mm)." % (
                 S.PICO_POS["mitte"][0], S.PICO_POS["mitte"][1],
                 S.PICO_POS["drehung"],
                 " ".join("%.2f" % v for v in S.PICO_POS["flaeche"]),
                 " ".join("%.2f" % v for v in S.ANTENNE_SPERRBEREICH),
                 S.ANTENNE_SPERRBEREICH[2] - S.ANTENNE_SPERRBEREICH[0],
                 S.ANTENNE_SPERRBEREICH[3] - S.ANTENNE_SPERRBEREICH[1]),
             "",
             "Um jede M3-Bohrung bleibt ein Freihaltebereich von "
             "%.1f mm Durchmesser fuer Schraubenkopf und "
             "Abstandsbolzen frei." % S.M3_KEEPOUT,
             "",
             "Das Lochbild ist punktsymmetrisch -- ein Modul laesst "
             "sich um 180 Grad verdreht anschrauben. Die Steckerlage "
             "ist deshalb bewusst unsymmetrisch: verdreht liegt kein "
             "Stift naeher als %.2f mm an einem Kontakt (halbes Raster "
             "waeren %.2f mm), ein verdreht aufgesetztes Modul steckt "
             "also nirgends und bleibt tot statt kaputt." % (
                 S.VERDREHT_MINDESTABSTAND_MM, S.RASTER / 2.0),
             "",
             "## Auflagen an die Modulfirmware",
             "",
             "\n\n".join("- " + a for a in S.AUFLAGEN),
             "",
             "## Auflagen an das Modul-Layout",
             "",
             "\n\n".join("- " + a for a in S.LAYOUT_AUFLAGEN),
             "",
             "## Modultypen",
             "",
             tabelle(["Nummer", "Name", "Kanaele"],
                     [("0x%02X" % nr, t["name"], t["kanaele"])
                      for nr, t in sorted(S.MODULTYPEN.items())]),
             "",
             "Nummern ab `0x80` bleiben fremden Modulen vorbehalten.",
             "",
             "## Kennwiderstaende",
             "",
             tabelle(["Stufe", "Widerstand", "Spannungsanteil"],
                     [(i, "%.0f" % r, "%.3f" % S.ID_ANTEIL(r))
                      for i, r in enumerate(S.ID_WIDERSTAENDE)]),
             ""]
    with open(ZIEL, "w", encoding="utf-8") as f:
        f.write("\n".join(teile))
    print("geschrieben:", ZIEL)


if __name__ == "__main__":
    main()

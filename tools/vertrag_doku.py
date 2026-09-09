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


def teil(stecker, seite):
    """LCSC-Nummer einer Steckerhaelfte -- oder die Spezifikation.

    Ein leeres Feld ist erlaubt (dann steht die Spezifikation da),
    aber es bedeutet: diese Platine ist NICHT bestueckt bestellbar.
    Deshalb wird es als "offen" ausgewiesen und nicht als leere
    Backticks verschwiegen. Seit 2026-08-31 ist kein Feld mehr leer;
    der Zweig bleibt, damit ein kuenftiges Loch wieder sichtbar wird.
    """
    nummer = stecker[seite + "_lcsc"]
    if nummer:
        return "`%s`" % nummer
    return "offen: " + stecker.get(seite + "_spec", "")


def erzeugen(ziel=None):
    """Schreibt das Vertragsdokument nach `ziel` (Vorgabe: ZIEL).

    Der Parameter existiert fuer tests/test_erzeugte_dateien.py: der
    Test muss das Dokument neu erzeugen koennen, ohne die
    eingecheckte Datei anzufassen. docs/vertrag.md gehoert zu
    derselben Gattung wie die erzeugten Schaltplaene -- ein Erzeugnis
    im Repo, das von seiner Quelle abweichen kann, ohne dass es
    jemandem auffaellt.
    """
    teile = ["# PicoStack — der Vertrag",
             "",
             "Erzeugt aus `tools/stack_spec.py`. Nicht von Hand aendern.",
             "",
             "## Status",
             "",
             "Die Zusagen rund um das Flashen -- die Leitungen "
             "`FLASH_TX`, `FLASH_RX`, `SEL`, `SEL_CLK` und `FLASH_MODE` "
             "(SEL seit 2026-08-31 auf dem eigenen Kettenstecker, alle "
             "anderen auf den beiden 1x20-Stapelstecker-Reihen) und alles, "
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
             "### Pins, die eine Rolle tragen und trotzdem NICHT "
             "benutzbar sind",
             "",
             "Diese Pins fuehren eine Bezeichnung, liegen aber auf "
             "keiner Platine des Stapels an einem Netz. Wer sich auf "
             "die Rolle allein verlaesst, haelt sie faelschlich fuer "
             "belegt.",
             "",
             tabelle(["Pin", "Rolle", "Warum nicht benutzbar"],
                     [(p, S.PIN_ROLLE[p],
                       # Die Begruendung beginnt in stack_spec mit dem
                       # Rollennamen, damit sie dort allein lesbar ist.
                       # In der Tabelle steht er schon in der Spalte
                       # davor -- hier abschneiden.
                       S.NICHT_BELEGBAR[p].split(" -- ", 1)[-1])
                      for p in sorted(S.NICHT_BELEGBAR)]),
             "",
             "## Stapelstecker und Kettenstecker",
             "",
             "Die Steckerbelegung oben laeuft seit Vertragsversion %d "
             "nicht mehr ueber einen einzelnen 2x20-Block, sondern ueber "
             "**zwei 1x20-Buchsenreihen in echter Pico-Geometrie** "
             "(Reihenabstand 17,78 mm, Raster 2,54 mm): `stapel_links` "
             "traegt Pico-Pin 1..20, `stapel_rechts` Pico-Pin 21..40. "
             "Der Pico steckt dadurch direkt oben in den Stapel; die "
             "Pin-Rollen aus der Tabelle oben aendern sich dadurch NICHT, "
             "nur ihre Steckergeometrie. Beide Reihen sind "
             "**Stapelstecker**: %s. Bauteil: %s, "
             "Gehaeusehoehe %.2f mm, Stiftlaenge unterhalb des Gehaeuses "
             "%.2f mm. Quelle: %s." % (
                 S.VERTRAG_VERSION,
                 S.STECKER_STAPEL["typ"],
                 ("LCSC `%s`" % S.STECKER_STAPEL["buchse_lcsc"]
                  if S.STECKER_STAPEL["buchse_lcsc"]
                  else "offen bis Fertigungs-Sichtung (1x20-Sourcing-"
                       "Ruling s. Kommentar oben)"),
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
                      "Buchse LCSC", "Buchse Typ",
                      "Stift LCSC", "Stift Typ"],
                     [(name, st["typ"], st["montage_oben"],
                       st["montage_unten"],
                       teil(st, "buchse"), st.get("buchse_mpn", ""),
                       teil(st, "stift"), st.get("stift_mpn", ""))
                      for name, st in (("stapel", S.STECKER_STAPEL),
                                       ("kette", S.STECKER_KETTE),
                                       ("leistung", S.STECKER_LEISTUNG))]),
             "",
             "Alle sechs Steckerhaelften tragen seit 2026-08-31 eine "
             "Bauteilnummer von einer gesehenen LCSC-Produktseite; alle "
             "sind in der JLCPCB-Bestueckungsbibliothek gefuehrt. Damit "
             "sind Sockelplatine und Module bestueckt bestellbar -- ein "
             "einziges leeres Feld haette das verhindert.",
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
                      for name in ("stapel_links", "stapel_rechts",
                                   "kette", "leistung")]),
             "",
             "Die belegte Flaeche ist die Vereinigung der Hoefe "
             "(F.CrtYd) aller Footprints an diesem Platz, nach der "
             "Drehung. Ketten- und Leistungsstecker bestehen "
             "auf jedem Modul aus zwei Haelften (SMD-Buchse oben, "
             "SMD-Stiftleiste unten); beide Haelften belegen "
             "**denselben** Platz, sonst treffen sie sich im Stapel "
             "nicht.",
             "",
             "Seit Vertragsversion %d steckt der Pico nicht mehr nur auf "
             "einer eigenen Sockelplatine, sondern oben auf **jedem** "
             "Modul, in `stapel_links`/`stapel_rechts`. Sein Umriss "
             "(`PICO_SCHATTEN`, 51 x 21 mm laut Datenblatt) liegt bei "
             "%s. Am Pico-Ende gegenueber der USB-Buchse liegt der "
             "WLAN-Antennen-Sperrbereich `ANTENNE_FREI` %s (%.1f x "
             "%.1f mm) -- dort darf auf der Seite, auf der der Pico "
             "steckt, weder Kupfer noch ein Bauteil liegen (Raspberry Pi "
             "Pico W Datasheet, RP-008312-DS-2, Abschnitt 2.2.1 "
             "\"Keep-out area\": Ausschnitt 14 x 9 mm)." % (
                 S.VERTRAG_VERSION,
                 " ".join("%.2f" % v for v in S.PICO_SCHATTEN),
                 " ".join("%.2f" % v for v in S.ANTENNE_FREI),
                 S.ANTENNE_FREI[2] - S.ANTENNE_FREI[0],
                 S.ANTENNE_FREI[3] - S.ANTENNE_FREI[1]),
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
             "Kein freiliegendes Kupfer naeher als %.1f mm an einem der "
             "%d Landepunkte aus `LANDEPUNKTE_VERDREHT()` (das sind die "
             "um 180 Grad gedrehten Lagen aller Steckerkontakte)."
             % (S.LANDE_SPERRRADIUS, len(S.LANDEPUNKTE_VERDREHT())),
             "",
             "## Versorgung je Board",
             "",
             "Seit Vertragsversion %d hat jedes Modul seine eigene "
             "Versorgungszelle statt einer gemeinsamen Sockelplatine: "
             "Klemme (%.1f-%.1f V), Verpolschutz (P-FET, Drain am Netz "
             "`%s`), TVS, K7805-1000R3 und ein Schottky-OR%s vor VSYS. "
             "Beliebig viele bestueckte Regler koennen im selben Stapel "
             "koexistieren; ein einziges eingespeistes Board versorgt "
             "die ganze Kette. Der Gate-Teiler des Verpolschutzes haengt "
             "an `%s`, nicht an der Einspeisung selbst -- das ist der "
             "aus v1 uebernommene Blocker-Fix: lag der Teiler am "
             "Eingang, bildeten Bodydiode und TVS bei verpolter "
             "Einspeisung einen Kurzschluss statt zu sperren." % (
                 S.VERTRAG_VERSION,
                 S.VERSORGUNG["eingang_v"][0], S.VERSORGUNG["eingang_v"][1],
                 S.VERSORGUNG["schutz_drain_an"],
                 " (vsys_diode)" if S.VERSORGUNG["vsys_diode"] else "",
                 S.VERSORGUNG["gate_teiler_an"]),
             "",
             "## Randpads",
             "",
             "Jeder als \"frei\" deklarierte Pico-Pin (und mehrere "
             "3V3-/GND-Pads) liegt zusaetzlich als beschriftetes "
             "Loetpad auf der Plattenkante -- Position vertraglich "
             "fixiert, identisch auf jedem Modul, auf der "
             "Unterseite (B.Cu), damit die Verdreh-Sicherheit der "
             "Landepunkte unangetastet bleibt. %d Pads insgesamt." % (
                 len(S.RANDPADS)),
             "",
             tabelle(["Pico-Pin", "Beschriftung", "x", "y"],
                     [(p, label, x, y)
                      for p, label, (x, y) in S.RANDPADS]),
             "",
             "## Montage",
             "",
             S.MONTAGE_REGEL,
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
    pfad = ZIEL if ziel is None else ziel
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(teile))
    return pfad


if __name__ == "__main__":
    print("geschrieben:", erzeugen())

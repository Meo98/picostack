"""Traegt die Netzklassen ins Projekt ein.

Herkunft: PecheAuxCanards/tools/pcb/netclasses.py (Etappe 1b, Aufgabe 1).
Die Datei importierte dort ebenfalls ein globales Modul "spec" der
Einzelplatine -- derselbe Fehler wie in geometry.py, build.py und
autoroute.py, auch wenn der Auftrag ihn nicht namentlich nannte: main()
nimmt die Leistungsnetze jetzt als Parameter, nicht mehr aus einem
Import, damit sich Sockel- und Motorplatine im selben Lauf bedienen
lassen, ohne dieses Modul zu kopieren.

Die Bahnbreiten selbst (Signal/Leistung) sind dagegen wirklich global --
sie stehen wortwoertlich in jeder Aufgabenbeschreibung als Vertragswert,
nicht je Platine verschieden. Sie kommen aus tools/pcb/fertigung.py,
derselben Quelle, aus der auch autoroute.py sie liest -- NICHT aus
tools/stack_spec.py: der Vertrag ist die Zusage an fremde Modulbauer
(Umriss, Lochbild, Steckerbelegung, Typnummern, sicherer Zustand), eine
Bahnbreite ist dagegen eine Fertigungsentscheidung dieser konkreten
Platinen. Sie stand hier zunaechst versehentlich in stack_spec.py, was
tools/vertrag_doku.py aber nie in docs/vertrag.md gezeigt hat --
dasselbe Auseinanderlaufen wie unten beschrieben, nur zwischen Modul und
Doku statt zwischen netclasses.py und autoroute.py (siehe
tools/pcb/fertigung.py fuer die Begruendung). Zwei getrennte Kopien
derselben Zahl waren im Vorlaeuferprojekt genau der Fehler, der das
Muttern-Redesign noetig gemacht hat: netclasses.py setzte die
Projekt-Netzklasse, aber autoroute.py schrieb beim DSN-Export
unabhaengig davon 0,20 mm, weil eine frisch erzeugte pcbnew.BOARD() die
Netzklassen des Projekts nicht kennt.

Aufruf: python3 tools/pcb/netclasses.py <projekt.kicad_pro> <spec_modul>
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import fertigung
import stack_spec as S


# Die Vorgabe-Netzklasse, wie KiCad 10.0.5 sie selbst schreibt.
#
# Warum sie hier steht (2026-09-01, Aufgabe 6). Eine frisch angelegte
# .kicad_pro traegt "net_settings": {} -- ohne jede Klasse. KiCad
# ergaenzt die Vorgaben erst, wenn es das Projekt einmal geoeffnet hat;
# in dieser Werkzeugkette passiert das beiläufig beim Netzlisten-Export
# in build.read_netlist(). Der Aufgabenbrief schreibt aber die
# Reihenfolge netclasses -> build vor, und in DIESER Reihenfolge brach
# netclasses.py ab. Wer die Meldung uebersieht (oder sie in einem
# Skript verschluckt), verlegt anschliessend mit der KiCad-Vorgabe
# 0,20 mm -- genau der Fehler, dessentwegen der Muttern-Print neu
# entstehen musste. Beide PicoStack-Projekte hatten das leere Feld,
# Aufgabe 7 waere in dieselbe Falle gelaufen.
#
# Die Werte sind die von KiCad selbst erzeugten (aus einer von
# kicad-cli angefassten .kicad_pro uebernommen), NICHT geraten -- die
# vier, auf die es ankommt, werden unten ohnehin ueberschrieben.
_KICAD_DEFAULT = {
    "bus_width": 12,
    "clearance": 0.2,
    "diff_pair_gap": 0.25,
    "diff_pair_via_gap": 0.25,
    "diff_pair_width": 0.2,
    "line_style": 0,
    "microvia_diameter": 0.3,
    "microvia_drill": 0.1,
    "name": "Default",
    "pcb_color": "rgba(0, 0, 0, 0.000)",
    "priority": 2147483647,
    "schematic_color": "rgba(0, 0, 0, 0.000)",
    "track_width": 0.2,
    "tuning_profile": "",
    "via_diameter": 0.6,
    "via_drill": 0.3,
    "wire_width": 6,
}


def main(pro, leistungsnetze):
    d = json.load(open(pro, encoding="utf-8"))
    ns = d.setdefault("net_settings", {})

    vorlage = None
    for c in ns.get("classes", []):
        if c.get("name") == "Default":
            vorlage = c
    if vorlage is None:
        # Anlegen statt abbrechen -- s. Begruendung bei _KICAD_DEFAULT.
        vorlage = dict(_KICAD_DEFAULT)
        ns.setdefault("classes", []).append(vorlage)
        print("keine Default-Netzklasse im Projekt -- angelegt")

    vorlage["track_width"] = fertigung.TRACK_SIGNAL
    vorlage["clearance"] = 0.2
    vorlage["via_diameter"] = fertigung.VIA_PAD
    vorlage["via_drill"] = fertigung.VIA_DRILL

    leistung = dict(vorlage)
    leistung.update({
        "name": "Leistung",
        "track_width": fertigung.TRACK_POWER,
        "via_diameter": 0.8,
        "via_drill": 0.4,
    })
    # v2.1, Aufgabe D3: dritte Klasse fuer den 24-V-Stamm.
    #
    # Bis v2.1 trugen /PWR_IN und /+24V dieselbe Klasse wie ein
    # einzelner Kanal. Das war der Entwurfsfehler, den
    # tools/pcb/strombelastung.py gefunden hat: durch den Stamm muss die
    # SUMME (stack_spec.STROMBUDGET["modul_gesamt_a"] = 4,0 A), durch
    # einen Kanal nur der Kanalstrom. Eine Klasse fuer beides heisst,
    # eine der beiden Zahlen ist falsch -- 1,00 mm traegt 3,25 A.
    stamm = dict(vorlage)
    stamm.update({
        "name": "Stamm",
        "track_width": fertigung.TRACK_STAMM,
        "via_diameter": 0.8,
        "via_drill": 0.4,
    })
    ns["classes"] = [vorlage, leistung, stamm]

    # Zuordnung ueber Muster, damit sie auch fuer spaeter neu
    # hinzukommende Netze gilt und nicht per Hand nachgezogen werden muss.
    # Reihenfolge zaehlt: KiCad nimmt das ERSTE passende Muster, also
    # muessen die Stammnetze VOR den uebrigen Leistungsnetzen stehen --
    # sonst bekaeme /+24V die schmalere Leistungsklasse.
    stammnetze = [n for n in S.STROMBUDGET["stamm_netze"] if n in set(leistungsnetze)]
    uebrige = sorted(set(leistungsnetze) - set(stammnetze))
    ns["netclass_patterns"] = (
        [{"netclass": "Stamm", "pattern": n} for n in stammnetze]
        + [{"netclass": "Leistung", "pattern": n} for n in uebrige])
    ns.pop("netclass_assignments", None)

    json.dump(d, open(pro, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("Default %.2f mm | Stamm %.2f mm fuer %s | Leistung %.2f mm fuer %s"
          % (fertigung.TRACK_SIGNAL,
             fertigung.TRACK_STAMM, ", ".join(stammnetze) or "(keine)",
             fertigung.TRACK_POWER, ", ".join(uebrige) or "(keine)"))
    return 0


if __name__ == "__main__":
    import importlib

    if len(sys.argv) != 3:
        raise SystemExit(
            "Aufruf: netclasses.py <projekt.kicad_pro> <spec_modul>")
    beschreibung = importlib.import_module(sys.argv[2])
    raise SystemExit(main(sys.argv[1], beschreibung.POWER_NETS))

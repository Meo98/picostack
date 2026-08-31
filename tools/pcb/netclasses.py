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
sys.path.insert(0, HERE)
import fertigung


def main(pro, leistungsnetze):
    d = json.load(open(pro, encoding="utf-8"))
    ns = d.setdefault("net_settings", {})

    vorlage = None
    for c in ns.get("classes", []):
        if c.get("name") == "Default":
            vorlage = c
    if vorlage is None:
        raise SystemExit("keine Default-Netzklasse im Projekt")

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
    ns["classes"] = [vorlage, leistung]

    # Zuordnung ueber Muster, damit sie auch fuer spaeter neu
    # hinzukommende Netze gilt und nicht per Hand nachgezogen werden muss.
    leistungsnetze = set(leistungsnetze)
    ns["netclass_patterns"] = [
        {"netclass": "Leistung", "pattern": n} for n in sorted(leistungsnetze)
    ]
    ns.pop("netclass_assignments", None)

    json.dump(d, open(pro, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("Default %.2f mm, Leistung %.2f mm fuer: %s"
          % (fertigung.TRACK_SIGNAL, fertigung.TRACK_POWER,
             ", ".join(sorted(leistungsnetze))))
    return 0


if __name__ == "__main__":
    import importlib

    if len(sys.argv) != 3:
        raise SystemExit(
            "Aufruf: netclasses.py <projekt.kicad_pro> <spec_modul>")
    beschreibung = importlib.import_module(sys.argv[2])
    raise SystemExit(main(sys.argv[1], beschreibung.POWER_NETS))

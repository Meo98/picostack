"""Misst an der FERTIGEN Platine nach, ob jede Klemme bedienbar ist.

Warum das eine eigene Pruefung ist. DRC prueft Abstaende, ERC prueft
Netze, steckerprobe.py prueft die Stapelkontakte -- keines von ihnen
weiss, wo bei einer Anschlussklemme VORNE ist. Eine um 180 Grad
verdrehte Klemme ist DRC-sauber, schaltplantreu und faellt in jeder
Netzliste durch; sie faellt erst auf, wenn jemand ein Kabel anschliessen
will und die Drahtoeffnung in die Platine zeigt.

Genau das ist in v2.1 passiert. Vertragsregel R1 ("Klemmenkoerper
buendig zur Platinenkante, Drahtoeffnung nach aussen") stand seit
Aufgabe B im Vertrag, hatte aber KEINE Pruefung -- sie wurde beim
Platzieren von Hand befolgt. Bei den Lastklemmen der Dimmer ging das
gut, bei der Einspeiseklemme J90 auf allen vier Brettern und bei der
Motorklemme J5 nicht: dort zeigte die Oeffnung nach innen. Gefunden hat
es ein Mensch im 3D-Bild, nicht das Werkzeug. Diese Datei holt das nach.

Drei Zusagen je Klemme, jede einzeln rot-faehig:

  K1 RICHTUNG   Die Drahtoeffnung zeigt zu der Platinenkante, die dem
                Bauteil am naechsten liegt. Eine Klemme, die zur
                gegenueberliegenden Kante oeffnet, ist nicht
                anschliessbar -- das Kabel muesste quer ueber die
                Platine.
  K2 KANTE      Die Hof-Vorderkante steht hoechstens
                stack_spec.KLEMME_KANTENABSTAND_MAX hinter der
                Platinenkante zurueck und ragt nicht darueber hinaus.
  K3 SCHATTEN   Der Hof der Klemme schneidet PICO_SCHATTEN nicht. Der
                zweite Halbsatz von R1: wo ein Pico darueber steckt,
                kommt kein Schraubendreher hin.

Die Oeffnungsrichtung wird NICHT geraten, sondern aus
stack_spec.KLEMME_OEFFNUNG geholt -- dort steht sie je Bauform als
gemessene Zahl mit ihrer Herleitung aus dem STEP-Modell. Eine Bauform
ohne Eintrag ist ein FEHLER, keine stille Ausnahme: lieber rot und
nachmessen als gruen und geraten.

Aufruf ueber den kipy-Starter:
  tools/pcb/kipy tools/pcb/klemmenprobe.py <board.kicad_pcb>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import pcbnew          # noqa: E402
import build           # noqa: E402
import stack_spec as S  # noqa: E402

# Ab wann eine Richtung nicht mehr achsparallel ist. Klemmen werden in
# diesem Projekt ausschliesslich in 90-Grad-Schritten gesetzt; alles
# andere waere eine schraege Klemme an einer geraden Kante und ist als
# Fehler gemeint, nicht als Toleranzfrage.
WINKELTOLERANZ = 1e-6


def _oeffnungsrichtung(fp):
    """Oeffnungsvektor in PLATINENkoordinaten, oder (None, Grund).

    Die Rechnung selbst steht im Vertrag
    (stack_spec.KLEMME_OEFFNUNG_GLOBAL), damit sie ohne KiCad pruefbar
    ist; hier wird nur die tatsaechliche Bauteillage hineingereicht.
    """
    name = fp.GetFPIDAsString().split(":")[-1]
    try:
        return S.KLEMME_OEFFNUNG_GLOBAL(
            name, fp.GetOrientationDegrees(), fp.IsFlipped()), None
    except KeyError:
        return None, ("Bauform %s steht nicht in stack_spec."
                      "KLEMME_OEFFNUNG -- Oeffnungsrichtung unbekannt, "
                      "erst nachmessen (s. Herleitung dort)" % name)
    except NotImplementedError as e:
        return None, "%s: %s" % (name, e)


def _achse(v):
    """Macht aus einem Richtungsvektor eine der vier Kantenrichtungen."""
    gx, gy = v
    if abs(gx) < WINKELTOLERANZ and abs(abs(gy) - 1.0) < WINKELTOLERANZ:
        return "unten" if gy > 0 else "oben"
    if abs(gy) < WINKELTOLERANZ and abs(abs(gx) - 1.0) < WINKELTOLERANZ:
        return "rechts" if gx > 0 else "links"
    return None


def _ueberlappt(a, b):
    """Schneiden sich zwei Rechtecke (links, oben, rechts, unten)?"""
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def pruefen(pfad):
    board = pcbnew.LoadBoard(pfad)
    bb = board.GetBoardEdgesBoundingBox()
    rand = (bb.GetLeft() / 1e6, bb.GetTop() / 1e6,
            bb.GetRight() / 1e6, bb.GetBottom() / 1e6)
    print("Platine  x %.2f..%.2f  y %.2f..%.2f"
          % (rand[0], rand[2], rand[1], rand[3]))

    klemmen = [f for f in board.GetFootprints()
               if "TerminalBlock" in f.GetFPIDAsString()]
    if not klemmen:
        return ["keine einzige Klemme gefunden -- entweder hat diese "
                "Platine wirklich keine (dann gehoert sie nicht durch "
                "diese Probe) oder der Bauformfilter 'TerminalBlock' "
                "greift nicht mehr"]

    fails = []
    for fp in sorted(klemmen, key=lambda f: f.GetReference()):
        ref = fp.GetReference()
        hof = build.courtyard_bbox(fp)
        if hof is None:
            fails.append("%s: kein Hof (F.CrtYd) -- nicht messbar" % ref)
            continue
        hof = tuple(v / 1e6 for v in hof)

        richtung, grund = _oeffnungsrichtung(fp)
        if richtung is None:
            fails.append("%s: %s" % (ref, grund))
            continue
        seite = _achse(richtung)
        if seite is None:
            fails.append(
                "%s: Oeffnung zeigt nach (%.3f|%.3f), das ist keine der "
                "vier Kantenrichtungen (Drehung %.1f Grad)"
                % (ref, richtung[0], richtung[1], fp.GetOrientationDegrees()))
            continue

        # K1 -- zeigt die Oeffnung zur NAECHSTEN Kante?
        weg = {"oben": hof[1] - rand[1], "unten": rand[3] - hof[3],
               "links": hof[0] - rand[0], "rechts": rand[2] - hof[2]}
        naechste = min(weg, key=weg.get)
        if seite != naechste:
            fails.append(
                "%s (K1): Drahtoeffnung zeigt nach %s -- dorthin sind es "
                "%.2f mm, zur naechsten Kante (%s) aber nur %.2f mm. Die "
                "Klemme steht verdreht; ein Kabel muesste quer ueber die "
                "Platine."
                % (ref, seite, weg[seite], naechste, weg[naechste]))
            continue

        # K2 -- buendig?
        abstand = weg[seite]
        if abstand > S.KLEMME_KANTENABSTAND_MAX:
            fails.append(
                "%s (K2): Hof-Vorderkante steht %.2f mm hinter der Kante "
                "%s zurueck, erlaubt sind %.2f mm (R1 verlangt buendig)"
                % (ref, abstand, seite, S.KLEMME_KANTENABSTAND_MAX))
        elif abstand < -S.KLEMME_UEBERSTAND_MAX:
            fails.append(
                "%s (K2): Hof ragt %.2f mm ueber die Kante %s hinaus -- "
                "im Nutzen sitzt dort der Fraesschlitz"
                % (ref, -abstand, seite))

        # K3 -- Schraubendreherzugang, zweiter Halbsatz von R1
        if _ueberlappt(hof, S.PICO_SCHATTEN):
            fails.append(
                "%s (K3): Hof (%.2f, %.2f, %.2f, %.2f) schneidet "
                "PICO_SCHATTEN %s -- unter einem gesteckten Pico kommt "
                "kein Schraubendreher an die Klemme"
                % ((ref,) + hof + (S.PICO_SCHATTEN,)))

        if not any(f.startswith(ref + " ") for f in fails):
            print("  %-5s oeffnet nach %-7s buendig (%.2f mm), Zugang frei"
                  % (ref, seite, abstand))

    return fails


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Aufruf: klemmenprobe.py <board.kicad_pcb>")
    schlecht = pruefen(sys.argv[1])
    if schlecht:
        print("FEHLER:")
        for f in schlecht:
            print("  -", f)
        raise SystemExit(1)
    print("Alle Klemmen kantenbuendig, Oeffnung nach aussen, Zugang frei.")

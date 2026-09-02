"""Misst an der FERTIGEN Platine nach, ob die Vertragsstecker sitzen.

Warum das eine eigene Pruefung ist. DRC prueft Abstaende, der
Schaltplan-Abgleich prueft Netze -- keines von beiden weiss, WO ein
Stecker sitzen muss. Ein um 180 Grad gedrehter, ein gespiegelter oder
ein um zwei Millimeter verschobener Stapelstecker ist DRC-sauber und
schaltplantreu; er faellt erst auf, wenn zwei gefertigte Platinen nicht
aufeinanderpassen. Genau dafuer gibt es tools/stack_spec.STECKER_POS,
und genau deshalb muss jemand nachsehen, ob die gebaute Datei ihn auch
einhaelt.

Zwei unabhaengige Messungen je Stecker:

1. PAD-SCHWERPUNKT. Aus der gebauten Datei die tatsaechlichen
   Pad-Mittelpunkte holen und ihren Mittelpunkt gegen den Mittelpunkt
   des Kontaktrasters aus stack_spec.PAD_LAGEN() halten. Das ist die
   aussagekraeftige Messung: sie benutzt echte Kupferkoordinaten, nicht
   die Zahl, mit der platziert wurde, und schlaegt bei falscher Drehung,
   Spiegelung oder Verschiebung an.
   Sie geht auf, weil die Loetpads aller drei Steckerfootprints
   symmetrisch um ihr Kontaktfeld liegen -- bei den bedrahteten sind Pad
   und Kontakt derselbe Punkt, bei den SMD-Paaren liegen die Pads
   seitlich, aber paarweise gegenueber (nachgesehen in den
   .kicad_mod-Dateien, s. Kommentar bei stack_spec.FOOTPRINT_HOF).

2. HOF. Der Hof des platzierten Bauteils gegen stack_spec.HOF(). Diese
   Messung ist die schwaechere -- build.py platziert nach genau diesem
   Rechteck --, aber sie prueft die eine Stelle, an der die beiden
   Hof-Messungen des Projekts auseinanderlaufen koennen:
   fertigung.HOF_STRICH. Ist die Zahl falsch, liegt hier ein Rest.

Aufruf ueber den kipy-Starter:
  ~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy \\
      tools/pcb/steckerprobe.py <spec_modul> <board.kicad_pcb>
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import pcbnew          # noqa: E402
import build           # noqa: E402  (courtyard_bbox: dieselbe Messung wie beim Bauen)
import stack_spec as S  # noqa: E402

# Wieviel Abweichung durchgeht. 0,001 mm ist die Aufloesung, in der
# stack_spec rundet -- alles darueber ist ein echter Versatz und keine
# Rundung. Bewusst NICHT grosszuegiger: die Fehler, gegen die diese
# Probe steht (Drehung, Spiegelung, Verschiebung), sind Millimeter
# gross, nicht Mikrometer.
TOLERANZ = 0.0015


def mitte(punkte):
    xs = [p[0] for p in punkte]
    ys = [p[1] for p in punkte]
    return ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0)


def kontaktprobe(ref, name, pads, soll_raster):
    """Liegt KONTAKT k dort, wo der Vertrag ihn haben will?

    Nicht der Schwerpunkt, sondern die Zuordnung Nummer -> Ort: der
    Schwerpunkt ist spiegelinvariant, die Nummerierung nicht. Genau an
    dieser Luecke ist am 2026-09-01 aufgefallen, dass der Vertrag die
    Kontaktnummern des 2x02-SMD-Paars spiegelverkehrt veroeffentlichte
    (s. stack_spec.SPALTEN_GESPIEGELT) -- diese Probe stand deshalb
    einen Commit lang bewusst NICHT im Baum: sie haette gegen ein
    nachweislich falsches Modell gemessen. Erst wurde der Vertrag
    entschieden, jetzt misst sie gegen die korrigierte Fassung.

    Zuordnung ueber den naechsten Sollkontakt. Das geht auf, weil der
    seitliche Versatz zwischen Loetpad und Kontakt bei jedem der fuenf
    Steckerfootprints kleiner ist als der Abstand zum NAECHSTEN fremden
    Kontakt: 2x02 SMD 1,255 mm eigener gegen 3,795 mm fremder Kontakt,
    1x02 SMD 1,655 gegen 3,03, THT 0 gegen 2,54. Nachgemessen an den
    .kicad_mod-Dateien, nicht angenommen.
    """
    fails = []
    for num, pos in sorted(pads.items(), key=lambda kv: int(kv[0])):
        n = int(num)
        if n not in soll_raster:
            continue
        nah = min(soll_raster,
                  key=lambda k: (soll_raster[k][0] - pos[0]) ** 2
                  + (soll_raster[k][1] - pos[1]) ** 2)
        if nah != n:
            fails.append(
                "%s (%s): Pad %s liegt am Ort von Kontakt %d "
                "(%.2f|%.2f), gehoert aber zu Kontakt %d (%.2f|%.2f) -- "
                "Nummerierung verdreht oder gespiegelt"
                % (ref, name, num, nah, soll_raster[nah][0],
                   soll_raster[nah][1], n, soll_raster[n][0],
                   soll_raster[n][1]))
    return fails[:2]        # zwei Beispiele genuegen, der Rest folgt daraus


def _abstand_zu_kante(punkt, kanten):
    """Kuerzester Abstand eines Punktes zu allen Edge.Cuts-Elementen.

    Boegen werden abgetastet statt ueber |Abstand zum Mittelpunkt| - r
    gerechnet: diese Formel gilt nur, wenn der naechste Punkt des
    VOLLKREISES auch auf dem Bogenstueck liegt. Bei einem Viertelkreis
    in der Ecke ist er das meistens NICHT -- die Formel meldet dann
    einen Abstand zu einem Punkt, den es auf der Platine gar nicht gibt.
    Genau dieser Kurzschluss hat mich am 2026-09-01 zuerst einen
    Eckenfehler an der falschen Stelle vermuten lassen.
    """
    px, py = punkt
    best = float("inf")
    for d in kanten:
        if d.GetShape() == pcbnew.SHAPE_T_ARC:
            c = d.GetCenter(); s = d.GetStart(); e = d.GetEnd()
            cx, cy, r = c.x / 1e6, c.y / 1e6, d.GetRadius() / 1e6
            a0 = math.atan2(s.y / 1e6 - cy, s.x / 1e6 - cx)
            a1 = math.atan2(e.y / 1e6 - cy, e.x / 1e6 - cx)
            if abs(a1 - a0) > math.pi:
                if a1 < a0:
                    a1 += 2 * math.pi
                else:
                    a0 += 2 * math.pi
            for k in range(201):
                a = a0 + (a1 - a0) * k / 200.0
                best = min(best, math.hypot(px - (cx + r * math.cos(a)),
                                            py - (cy + r * math.sin(a))))
        else:
            ax, ay = d.GetStart().x / 1e6, d.GetStart().y / 1e6
            bx, by = d.GetEnd().x / 1e6, d.GetEnd().y / 1e6
            vx, vy = bx - ax, by - ay
            L = vx * vx + vy * vy
            t = 0.0 if L == 0 else max(0.0, min(
                1.0, ((px - ax) * vx + (py - ay) * vy) / L))
            best = min(best, math.hypot(px - (ax + t * vx), py - (ay + t * vy)))
    return best


def umrissprobe(board, beschreibung):
    """Umriss und Bohrungen gegen die zugesicherte Geometrie.

    Zwei Pruefungen, die bis 2026-09-01 (Aufgabe 6) niemand gemacht hat
    und die beide an derselben Ursache haengen -- s. build.bogenmitte():

    1. Jeder Bogen auf Edge.Cuts hat den Radius, der gemeint war. Die
       Eckbogen den CORNER_R des Vertrags, die Ecken des
       Antennenschlitzes den Fraeserradius. Gebaut wurden r/sqrt(2):
       2,121 statt 3,00 und 0,707 statt 1,00.

    2. Jede Bohrung haelt EDGE_CLEARANCE zur Kante. Der Umriss stimmte
       in der Bounding Box weiterhin auf den Millimeter genau -- der
       Fehler sass allein in der Kruemmung, und zwei der vier
       M3-Bohrungen lagen dadurch AUSSERHALB der Platine.
    """
    fails = []
    kanten = [d for d in board.GetDrawings()
              if d.GetLayer() == pcbnew.Edge_Cuts]
    boegen = [d for d in kanten if d.GetShape() == pcbnew.SHAPE_T_ARC]

    erwartet = {round(beschreibung.CORNER_R, 3)}
    if getattr(beschreibung, "ANTENNA_SLOT", None) is not None:
        erwartet.add(1.0)              # Fraeserradius, s. build.antenna_slot
    for d in boegen:
        r = round(d.GetRadius() / 1e6, 3)
        if not any(abs(r - w) <= TOLERANZ for w in erwartet):
            s = d.GetStart()
            fails.append(
                "Eckbogen bei (%.2f|%.2f): Radius %.3f mm, erwartet %s"
                % (s.x / 1e6, s.y / 1e6, r,
                   " oder ".join("%.2f" % w for w in sorted(erwartet))))
    if not fails:
        print("  Umriss    %d Boegen, alle mit dem zugesicherten Radius"
              % len(boegen))

    e = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
    knapp = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetDrillSize().x <= 0:
                continue
            p = (pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6)
            r = pad.GetSize().x / 2e6
            steg = _abstand_zu_kante(p, kanten) - r
            if steg < e - TOLERANZ:
                knapp.append("%s.%s (%.2f|%.2f): nur %.3f mm Steg zur Kante, "
                             "gefordert %.2f"
                             % (fp.GetReference(), pad.GetNumber() or "-",
                                p[0], p[1], steg, e))
    fails += knapp
    if not knapp:
        print("  Bohrungen alle mit Kantenabstand >= %.2f mm" % e)
    return fails


def kennzeichnungsprobe(board, beschreibung):
    """Traegt die Platine die Pflicht-Kennzeichnung des Vertrags?

    Dreieck plus "1" neben Pin 1 des Stapelsteckers, "KLEMMEN" an der
    Klemmenkante (stack_spec.LAYOUT_AUFLAGEN, erste Auflage). Die erste
    Fassung der Sockelplatine wurde OHNE committet, weil kein Werkzeug
    die Auflage umsetzte und keine Pruefung sie kannte -- eine Auflage
    in Prosa, die niemand misst, ist keine.
    """
    fails = []
    texte = [(d.GetText(), d.GetPosition().x / 1e6, d.GetPosition().y / 1e6)
             for d in board.GetDrawings()
             if isinstance(d, pcbnew.PCB_TEXT)
             and d.GetLayer() == pcbnew.F_SilkS]

    klemmen = [t for t in texte if t[0] == "KLEMMEN"]
    if not klemmen:
        fails.append("Kennzeichnung: kein \"KLEMMEN\" auf dem "
                     "Bestueckungsdruck")
    elif all(t[2] < S.BOARD_H - 6.0 for t in klemmen):
        fails.append("Kennzeichnung: \"KLEMMEN\" liegt nicht an der "
                     "Klemmenkante (y = %.1f)" % klemmen[0][2])

    ax, ay = S.STECKER_POS["stapel"]["pin1"]
    einsen = [t for t in texte if t[0] == "1"
              and math.hypot(t[1] - ax, t[2] - ay) < 6.0]
    if not einsen:
        fails.append("Kennzeichnung: kein \"1\" neben Pin 1 des "
                     "Stapelsteckers (%.1f|%.1f)" % (ax, ay))

    dreieck = [d for d in board.GetDrawings()
               if not isinstance(d, pcbnew.PCB_TEXT)
               and d.GetLayer() == pcbnew.F_SilkS
               and math.hypot(d.GetPosition().x / 1e6 - ax,
                              d.GetPosition().y / 1e6 - ay) < 6.0]
    if len(dreieck) < 3:
        fails.append("Kennzeichnung: kein Dreieck neben Pin 1 des "
                     "Stapelsteckers")
    if not fails:
        print("  Kennzeich Dreieck+1 an Pin 1, KLEMMEN an der Kante")
    return fails


def verdrehtprobe(board, beschreibung):
    """Kein freiliegendes Kupfer an den Landepunkten eines verdreht
    aufgesteckten Aufbaus -- die Kupferklausel des Vertrags, an der
    gebauten Platine gemessen.

    Nur fuer Module (beschreibung.IST_MODUL): die Sockelplatine sitzt
    zuoberst, auf ihre Oberseite drueckt nie ein Stift -- der Vertrag
    nimmt sie ausdruecklich aus.

    Freiliegend heisst: jedes Pad, das auf F.Cu Kupfer traegt (SMD auf
    der Oberseite oder durchkontaktiert -- der Loetstopplack spart Pads
    immer aus), und jede Via, die nicht AUSDRUECKLICH abgedeckt ist.
    Bahnen und Gussflaechen liegen unter dem Lack und zaehlen nicht.
    """
    if not getattr(beschreibung, "IST_MODUL", False):
        print("  Verdreht  Sockelplatine -- Kupferregel gilt nicht "
              "(zuoberst)")
        return []

    punkte = S.LANDEPUNKTE_VERDREHT()
    fails = []

    def zu_nah(cx, cy, radius, was):
        for px, py in punkte:
            d = math.hypot(cx - px, cy - py) - radius
            if d < S.LANDE_SPERRRADIUS - TOLERANZ:
                fails.append(
                    "Verdreht: %s bei (%.2f|%.2f) nur %.2f mm Kupferkante "
                    "vom Landepunkt (%.2f|%.2f) -- Vertrag verlangt %.1f"
                    % (was, cx, cy, d, px, py, S.LANDE_SPERRRADIUS))
                return

    for fp in board.GetFootprints():
        for pad in fp.Pads():
            oben = (pad.GetDrillSize().x > 0
                    or (not fp.IsFlipped()
                        and pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD))
            if not oben or not pad.GetNumber():
                continue
            r = max(pad.GetSize().x, pad.GetSize().y) / 2e6
            zu_nah(pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6, r,
                   "Pad %s.%s" % (fp.GetReference(), pad.GetNumber()))

    for t in board.Tracks():
        if t.Type() != pcbnew.PCB_VIA_T:
            continue
        if t.GetFrontTentingMode() == pcbnew.TENTING_MODE_TENTED:
            continue
        zu_nah(t.GetPosition().x / 1e6, t.GetPosition().y / 1e6,
               t.GetWidth() / 2e6, "unbedeckte Via")

    if not fails:
        print("  Verdreht  %d Landepunkte, alle >= %.1f mm von "
              "freiliegendem Kupfer" % (len(punkte), S.LANDE_SPERRRADIUS))
    return fails


def pruefen(beschreibung, board_pfad):
    board = pcbnew.LoadBoard(board_pfad)
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    fails = []

    for name, eintrag in sorted(S.STECKER_POS.items()):
        # Welche Referenz auf DIESER Platine an diesem Vertragsplatz
        # sitzt, weiss nur die Beschreibung -- der Sockel traegt an den
        # SMD-Plaetzen nur die Stiftseite, ein Modul beide Haelften.
        refs = [r for r, fp in beschreibung.FOOTPRINTS.items()
                if fp in eintrag["footprints"] and r in beschreibung.PLACEMENT]
        if not refs:
            print("  %-9s kein Bauteil auf dieser Platine" % name)
            continue

        for ref in sorted(refs):
            fp_name = beschreibung.FOOTPRINTS[ref]
            pin1, drehung = eintrag["pin1"], eintrag["drehung"]
            fp = fps.get(ref)
            if fp is None:
                fails.append("%s (%s): nicht auf der Platine" % (ref, name))
                continue

            # 1. Pad-Schwerpunkt gegen Kontaktraster
            pads = {p.GetNumber(): (p.GetPosition().x / 1e6,
                                    p.GetPosition().y / 1e6)
                    for p in fp.Pads() if p.GetNumber()}
            soll_raster = S.PAD_LAGEN(fp_name, pin1, drehung)
            soll = mitte(list(soll_raster.values()))
            ist = mitte(list(pads.values()))
            dx, dy = ist[0] - soll[0], ist[1] - soll[1]
            if abs(dx) > TOLERANZ or abs(dy) > TOLERANZ:
                fails.append(
                    "%s (%s): Pad-Mitte bei (%.4f|%.4f), Vertrag verlangt "
                    "(%.4f|%.4f) -- Versatz (%+.4f|%+.4f) mm"
                    % (ref, name, ist[0], ist[1], soll[0], soll[1], dx, dy))

            # 1b. WELCHER Kontakt wo liegt -- s. kontaktprobe().
            fails += kontaktprobe(ref, name, pads, soll_raster)

            # 1c. Die richtige Platinenseite. Der Vertrag sagt "Buchse
            # oben, Stiftleiste unten"; welche Haelfte dieses Bauteil
            # ist, steht im Footprintnamen.
            ist_unten = fp.IsFlipped()
            soll_unten = "PinHeader" in fp_name and "SMD" in fp_name
            if ist_unten != soll_unten:
                fails.append(
                    "%s (%s): sitzt %s, der Vertrag verlangt %s"
                    % (ref, name, "unten" if ist_unten else "oben",
                       "unten" if soll_unten else "oben"))

            # 2. Hof gegen stack_spec.HOF()
            box = build.courtyard_bbox(fp)
            ist_hof = tuple(v / 1e6 for v in box)
            soll_hof = S.HOF(fp_name, pin1, drehung)
            ab = [abs(a - b) for a, b in zip(ist_hof, soll_hof)]
            if max(ab) > TOLERANZ:
                fails.append(
                    "%s (%s): Hof (%.4f, %.4f, %.4f, %.4f), Vertrag "
                    "(%.4f, %.4f, %.4f, %.4f) -- groesste Abweichung %.4f mm"
                    % ((ref, name) + ist_hof + soll_hof + (max(ab),)))

            if not fails or fails[-1].split()[0] != ref:
                print("  %-9s %-3s Pad-Mitte und Hof auf der Vertragslage"
                      % (name, ref))

    fails += umrissprobe(board, beschreibung)
    fails += kennzeichnungsprobe(board, beschreibung)
    fails += verdrehtprobe(board, beschreibung)

    # Die M3-Bohrungen gehoeren zum selben Vertrag und kosten nichts.
    loecher = sorted((p.GetPosition().x / 1e6, p.GetPosition().y / 1e6)
                     for f in board.GetFootprints() for p in f.Pads()
                     if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH)
    if loecher != sorted(tuple(map(float, h)) for h in S.M3_HOLES):
        fails.append("M3-Lochbild: %s statt %s" % (loecher, S.M3_HOLES))
    else:
        print("  Lochbild  vier M3-Bohrungen auf der Vertragslage")

    return fails


if __name__ == "__main__":
    import importlib

    if len(sys.argv) != 3:
        raise SystemExit(
            "Aufruf: steckerprobe.py <spec_modul> <board.kicad_pcb>")
    b = importlib.import_module(sys.argv[1])
    schlecht = pruefen(b, sys.argv[2])
    if schlecht:
        print("FEHLER:")
        for f in schlecht:
            print("  -", f)
        raise SystemExit(1)
    print("Stecker sitzen auf der Vertragslage.")

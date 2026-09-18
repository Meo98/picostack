"""Trennt die Kleinstrom-Abzweige vom Leistungsstamm -- fuer zwei Laeufe.

## Das Problem, das dieses Werkzeug loest (Aufgabe D3, v2.1)

`KiCadRoutingTools` verlegt ein Netz mit mehreren Pads ueber einen
MINIMALEN SPANNBAUM seiner Pad-Koordinaten. Der Spannbaum kennt nur
Geometrie, keinen Strom -- und auf dem Dimmer1 legte er den 24-V-Strang
deshalb als Kette

    Q90 -> D90 -> R90 -> D1 -> J5

also QUER DURCH den Gateteiler R90 (1,3 mA) und die Freilaufdiode D1.
Das Kupfer zwischen diesen Pads fuehrt dann den vollen Modulstrom, muss
also 1,335 mm breit sein -- an Pads, an denen 0,25 mm voellig reichen
wuerde und wo zwischen Bauteilhoefen gar kein Platz fuer 1,8 mm
Korridor ist. Der Router meldete in jedem Lauf "Wide route blocked -
retrying at default track width" und lieferte 60-90 mm Stamm mit
0,25 mm. Zehn Parametervarianten in Aufgabe D2 und noch einmal sechs in
D3 aenderten daran nichts: es ist kein Parameterproblem, sondern die
falsche TOPOLOGIE.

## Die Loesung: mehrere kurze Laeufe statt eines langen

1. `--kupfer-weg` + `--vorverdrahtung`: blankes Brett, aber mit der
   Handverdrahtung der Beschreibung (s. unten -- sie wegzuraeumen war
   der zweite Fehler dieser Aufgabe).
2. `--abtrennen`: die Kleinstrom-Pads der Leistungsnetze bekommen
   VORUEBERGEHEND kein Netz. Damit sieht der Router nur noch die Pads,
   die wirklich Strom fuehren -- sein Spannbaum wird automatisch zum
   Stamm, ohne Handkoordinaten. (Die Pads bleiben als Kupfer stehen und
   damit als Hindernis sichtbar; nur ihre Netzzugehoerigkeit ruht.)
3. Lauf 1 verlegt NUR die Leistungsnetze, in voller Breite, auf sonst
   blankem Kupfer.
4. `--anheften` und Lauf 2 haengen die Abzweige mit Signalbreite an --
   noch bevor die Signale da sind, weil danach kein Platz mehr ist.
5. `--sperren`, dann Lauf 3 (alles uebrige) und Lauf 4 (die Nachzuegler).
   Gesperrtes Kupfer ruehrt der Router nicht an.
6. `--entsperren`.

## Was "Kleinstrom" heisst -- hergeleitet, nicht ausgesucht

Ein Pad ist ein ABZWEIG, wenn der fuer es deklarierte Strom
(`strombelastung.pad_stroeme()`) nach IPC-2221 mit der Signalbreite
`fertigung.TRACK_SIGNAL` auskommt. Alles darueber ist STAMM. Bei
0,25 mm und 20 K sind das 1,19 A -- der Gateteiler (0,05 A), die
Freilaufdiode (0,5 A) und der Reglereingang (0,3 A) fallen darunter,
die Klemmen (3,0 A), der Stuetz-Elko (2,0 A) und der Leistungsstecker
(3,0 A) darueber. Die Trennlinie kommt also aus derselben Rechnung wie
das Gate selbst; niemand waehlt hier Pads von Hand aus.

Die Quellpads bleiben IMMER am Netz -- ohne sie haette der Stamm keinen
Anfang.

## Der vollstaendige Ablauf

    kipy stammtrennung.py --kupfer-weg     <board.kicad_pcb>
    kipy stammtrennung.py --vorverdrahtung <board.kicad_pcb> <spec>
    kipy stammtrennung.py --abtrennen   <board.kicad_pcb> <spec> <liste.json>
    <Lauf 1: nur die Leistungsnetze, volle Breite>
    kipy stammtrennung.py --sperren     <board.kicad_pcb> <spec>
    <Lauf 2: alles uebrige>
    kipy stammtrennung.py --anheften    <board.kicad_pcb> <liste.json>
    <Lauf 3: die Abzweige mit Signalbreite anhaengen>
    kipy stammtrennung.py --entsperren  <board.kicad_pcb> <spec>
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import fertigung
import strombelastung as SB

import pcbnew


def abzweig_pads(spec):
    """{(ref, pad): netzname} aller Pads, die mit Signalbreite auskommen.

    Nur fuer Netze, bei denen ueberhaupt ein Stamm UEBRIG BLEIBT: haengt
    an einem Netz nur Kleinstrom (z.B. /+5V_LOKAL mit 1,0 A, was bei
    0,25 mm noch durchgeht), gibt es nichts zu trennen -- die Trennung
    wuerde das Netz im ersten Lauf ganz verschwinden lassen und dem
    zweiten Lauf unnoetige Arbeit machen, ohne dass irgendwo ein
    breiterer Stamm entstuende.
    """
    grenze = fertigung.TRACK_SIGNAL
    aus = {}
    for netz, (quellen, senken, _deckel, _gruppen) in SB.pad_stroeme(spec).items():
        klein, gross = {}, 0
        for pad, I in senken.items():
            if pad in quellen:
                continue
            if SB.erf_breite(I) <= grenze + 1e-9:
                klein[pad] = netz
            else:
                gross += 1
        if gross:
            aus.update(klein)
    return aus


def abtrennen(pfad, spec_name, liste_pfad):
    spec = importlib.import_module(spec_name)
    board = pcbnew.LoadBoard(pfad)
    ziel = abzweig_pads(spec)
    notiert = []
    for f in board.GetFootprints():
        for p in f.Pads():
            schl = (f.GetReference(), p.GetPadName())
            if schl not in ziel:
                continue
            if p.GetNetname() != ziel[schl]:
                continue
            notiert.append([schl[0], schl[1], p.GetNetname()])
            p.SetNetCode(0)
    if not notiert:
        print("ROT: kein einziges Abzweig-Pad gefunden -- Deklaration "
              "und Platine passen nicht zusammen")
        return 1
    # Bahnen, die an diesen Pads haengen, wuerden sonst als fremdes
    # Kupfer den Stamm blockieren. Sie gehoeren zum alten Lauf und
    # werden ohnehin neu verlegt -- aber nur, wenn der Aufrufer
    # --force-reroute benutzt. Hier NICHT angefasst: das Werkzeug soll
    # genau eine Sache tun.
    board.Save(pfad)
    json.dump(notiert, open(liste_pfad, "w", encoding="utf-8"), indent=1)
    print("%d Abzweig-Pad(s) vom Netz getrennt: %s"
          % (len(notiert), ", ".join("%s.%s" % (a, b) for a, b, _n in notiert)))
    return 0


def anheften(pfad, liste_pfad):
    board = pcbnew.LoadBoard(pfad)
    notiert = json.load(open(liste_pfad, encoding="utf-8"))
    n = 0
    for ref, pad, netz in notiert:
        code = board.GetNetcodeFromNetname(netz)
        if code < 0:
            print("ROT: Netz %r gibt es auf dieser Platine nicht" % netz)
            return 1
        gefunden = False
        for f in board.GetFootprints():
            if f.GetReference() != ref:
                continue
            for p in f.Pads():
                if p.GetPadName() == pad:
                    p.SetNetCode(code)
                    gefunden = True
                    n += 1
        if not gefunden:
            print("ROT: Pad %s.%s nicht gefunden" % (ref, pad))
            return 1
    board.Save(pfad)
    print("%d Abzweig-Pad(s) wieder am Netz" % n)
    return 0


def sperren(pfad, spec_name, frei=False):
    """Sperrt (oder entsperrt) alles Kupfer der Leistungsnetze.

    WARUM (Aufgabe D3, gemessen am Motormodul): Lauf 2 des Rezepts
    verlegt "alles uebrige". Der Router darf dabei Netze aufreissen, die
    ihm im Weg sind -- auch solche, die er gar nicht verlegen soll.
    Gemessen: nach Lauf 1 trug `/Out1` 23,3 mm bei 1,00 mm; nach Lauf 2
    war von dem Netz praktisch nichts mehr uebrig. Damit war die ganze
    Arbeit von Lauf 1 weg, und die Messung danach sagte "nicht
    erreichbar" statt "zu schmal".

    KiCad-gesperrtes Kupfer ruehrt der Router laut eigener
    Dokumentation nie an ("KiCad-locked copper is never ripped") --
    also wird es hier gesperrt und nach Lauf 3 wieder freigegeben, damit
    die committete Platine keine Sperren traegt, die spaetere Werkzeuge
    ueberraschen.
    """
    spec = importlib.import_module(spec_name)
    board = pcbnew.LoadBoard(pfad)
    netze = set(SB.pad_stroeme(spec))
    n = 0
    for t in board.GetTracks():
        if t.GetNetname() in netze:
            t.SetLocked(not frei)
            n += 1
    board.Save(pfad)
    print("%d Kupferobjekt(e) der Leistungsnetze %s"
          % (n, "freigegeben" if frei else "gesperrt"))
    return 0


def kupfer_weg(pfad):
    """Alle Bahnen und Vias entfernen -- der Nullpunkt des Rezepts.

    ABER: die Vorverdrahtung der Platinenbeschreibung (`PRE_TRACKS`,
    `PRE_VIAS`) wird danach WIEDER GELEGT, mit denselben Funktionen, die
    `build.py` beim Bauen benutzt.

    WARUM (Aufgabe D3, gemessen): die erste Fassung riss wirklich alles
    weg. Die Folge war, dass in JEDEM Lauf und auf JEDEM Brett dieselben
    Nest-Netze durchfielen (`/SEL_OUT`, `/NRST`, `3V3`, `/NQ`) -- genau
    die, fuer die die Beschreibung ihre Handverdrahtung enthaelt. Der
    Kommentar dort sagt seit Aufgabe 7, warum: "vorverdrahtet wird nur,
    was der Router grundsaetzlich nicht kann" (benachbarte
    gleichnetzige Pads eines VSSOP-8 im 0,5-mm-Raster, eingemauerte
    SOT-353-Massepads). Wer diese Stuecke wegraeumt, gibt dem Router
    eine Aufgabe, von der belegt ist, dass er sie nicht loesen kann --
    und bekommt jedes Mal dieselbe Fehlerliste zurueck.

    Warum das ein eigener Schritt ist und nicht `route.py
    --force-reroute`: dieses Rezept verlegt die LEISTUNGSNETZE ZUERST,
    ALLEIN, auf blankem Kupfer. `--force-reroute` reisst zwar auch alles
    auf, aber nur die Netze, die derselbe Lauf auch wieder verlegt --
    laesst man ihn nur ueber die Leistungsnetze laufen, bleiben alle
    Signalbahnen des vorigen Standes liegen und verbauen genau die
    Korridore, um die es geht. GEMESSEN (Dimmer1, Aufgabe D3): mit
    liegengebliebenen Signalbahnen lieferte der Router den 24-V-Stamm zu
    133 mm mit 0,25 mm Engstelle; auf blankem Kupfer 71 von 79 mm in
    voller 1,40-mm-Breite, ohne eine einzige "Wide route blocked"-
    Meldung. Der Korridor war die ganze Zeit da (nachgemessen), er war
    nur belegt.
    """
    board = pcbnew.LoadBoard(pfad)
    n = 0
    for t in list(board.GetTracks()):
        board.Remove(t)
        n += 1
    board.Save(pfad)
    print("%d Bahn-/Via-Objekte entfernt -- jetzt --vorverdrahtung "
          "aufrufen, sonst fehlt die Handverdrahtung der Beschreibung"
          % n)
    return 0


def vorverdrahtung(pfad, spec_name):
    """Legt PRE_TRACKS/PRE_VIAS der Beschreibung neu -- eigener Aufruf.

    Warum ein zweiter Prozess und nicht derselbe: nach dem Entfernen von
    ueber tausend Bahnobjekten ist die pcbnew-Instanz nicht mehr
    belastbar (`board.GetFootprints()` wirft, ein Neuladen im selben
    Prozess stuerzt ab). Ueber die Datei zu gehen kostet eine Sekunde
    und ist stabil -- dieselbe Ueberlegung wie bei den anderen
    kipy-Werkzeugen, die jeder genau eine Sache tun.
    """
    spec = importlib.import_module(spec_name)
    board = pcbnew.LoadBoard(pfad)
    import build        # erst hier: build.py zieht pcbnew und viel mehr
    b = build.pre_tracks(board, spec)
    v = build.pre_vias(board, spec)
    board.Save(pfad)
    print("Vorverdrahtung gelegt: %d Draehte, %d Vias" % (b, v))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] in ("--sperren", "--entsperren"):
        raise SystemExit(sperren(sys.argv[2], sys.argv[3],
                                  frei=sys.argv[1] == "--entsperren"))
    if len(sys.argv) == 3 and sys.argv[1] == "--kupfer-weg":
        raise SystemExit(kupfer_weg(sys.argv[2]))
    if len(sys.argv) == 4 and sys.argv[1] == "--vorverdrahtung":
        raise SystemExit(vorverdrahtung(sys.argv[2], sys.argv[3]))
    if len(sys.argv) >= 2 and sys.argv[1] == "--abtrennen" and len(sys.argv) == 5:
        raise SystemExit(abtrennen(sys.argv[2], sys.argv[3], sys.argv[4]))
    if len(sys.argv) == 4 and sys.argv[1] == "--anheften":
        raise SystemExit(anheften(sys.argv[2], sys.argv[3]))
    raise SystemExit(__doc__.strip().splitlines()[-3].strip() + "\n"
                     + __doc__.strip().splitlines()[-2].strip())

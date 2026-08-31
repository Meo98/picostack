"""Baut eine Platine aus Schaltplan-Netzliste und Platinenbeschreibung neu auf.

Herkunft: PecheAuxCanards/tools/pcb/build.py (Etappe 1b, Aufgabe 1). Zwei
Aenderungen gegenueber dem Original:

1. Das Modul importierte dort "spec" global und trug Pfad und Dateiname
   der dortigen Einzelplatine fest als Modulkonstanten ein. PicoStack
   braucht dieselbe Kette zweimal in einem Lauf
   (Sockel- und Motorplatine, spaeter weitere) -- eine Modulkonstante fuer
   "die eine Platine" ginge nicht mehr auf. bauen(beschreibung, board_pfad,
   sch_pfad) ersetzt darum das alte main() mit fest eingetragenem Pfad: die
   Platinenbeschreibung, der Zielpfad der .kicad_pcb und der Pfad des
   Schaltplans sind jetzt Parameter statt Modulkonstanten.

2. Board-spezifische Texte (Versionsvermerk, Bauhinweise) waren im
   Original eingebrannt ("v2 / 2026-08", ein Warnhinweis zu einem
   bestimmten Bauteil C12). mark_version() nimmt sie jetzt als Parameter.

Die Datei selbst wird geladen statt neu erzeugt, damit Lagenaufbau und
Entwurfsregeln aus dem KiCad-Projekt erhalten bleiben.

Aufruf ueber den kipy-Starter:
  ~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy tools/pcb/build.py \\
      <spec_modul, z.B. spec_sockel> <board.kicad_pcb> <schaltplan.kicad_sch>
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pcbnew
import geometry, kicadlibs


def mm(v):
    return pcbnew.FromMM(v)


# ---------------------------------------------------------------- Netzliste

def read_netlist(sch):
    """(bauteile, netze) aus der von KiCad exportierten Netzliste.

    bauteile: ref -> {"value":..., "footprint":...}
    netze:    netzname -> [(ref, pin), ...]
    """
    out = "/tmp/build_netlist.net"
    r = subprocess.run(["kicad-cli", "sch", "export", "netlist",
                        "--output", out, sch], capture_output=True, text=True)
    if not os.path.exists(out):
        raise SystemExit("Netzliste nicht exportierbar:\n" + r.stderr)
    if "annotation" in (r.stdout + r.stderr).lower():
        raise SystemExit("Schaltplan ist nicht sauber annotiert -- "
                         "erst die Annotation reparieren.")
    s = open(out, encoding="utf-8").read()

    comps = {}
    block = s[s.find("(components"):s.find("(libparts")]
    for b in re.split(r'\(comp\n', block)[1:]:
        ref = re.search(r'\(ref "([^"]+)"\)', b)
        val = re.search(r'\(value "([^"]*)"\)', b)
        fpr = re.search(r'\(footprint "([^"]*)"\)', b)
        if ref:
            comps[ref.group(1)] = {
                "value": val.group(1) if val else "",
                "footprint": fpr.group(1) if fpr else "",
            }

    nets = {}
    for b in re.split(r'\n\t\t\(net\n', s[s.find("(nets"):]):
        nm = re.search(r'\(name "([^"]+)"\)', b)
        if not nm:
            continue
        nets[nm.group(1)] = re.findall(
            r'\(ref "([^"]+)"\)\s*\n\s*\(pin "([^"]+)"\)', b)
    return comps, nets


# ------------------------------------------------------------------ Platine

def new_board(path):
    """Eine frische, leere Platine statt einer geleerten alten.

    Eine bestehende Platine laden und ausraeumen geht nicht: nach
    board.Remove() liefert board.Tracks() ein nicht mehr iterierbares
    Objekt und frisch erzeugte Footprints verlieren die Typinformation
    ihrer Textfelder -- der Prozess stirbt mitten im Bauen. Eine neue
    BOARD() hat ohnehin genau das, was hier gebraucht wird: zwei
    Kupferlagen, 1,6 mm. Netzklassen und Entwurfsregeln stehen im
    .kicad_pro und bleiben davon unberuehrt (siehe netclasses.py und
    autoroute.dsn_netzklassen: eine frische BOARD() kennt sie NICHT,
    darum muessen sie an anderer Stelle nachgezogen werden).
    """
    board = pcbnew.BOARD()
    board.SetFileName(path)
    return board


def draw_outline(board, beschreibung):
    """Rechteck mit abgerundeten Ecken auf Edge.Cuts."""
    w, h, r = beschreibung.BOARD_W, beschreibung.BOARD_H, beschreibung.CORNER_R
    for (x0, y0), (x1, y1) in [((r, 0), (w - r, 0)), ((w, r), (w, h - r)),
                               ((w - r, h), (r, h)), ((0, h - r), (0, r))]:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
        s.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.05))
        board.Add(s)
    # Mittelpunkt, Start und Ende explizit -- ein Winkel liesse den
    # Drehsinn offen und ergaebe im Zweifel den 270-Grad-Bogen.
    arcs = [((r, r),         (0.0, r),     (r, 0.0)),
            ((w - r, r),     (w - r, 0.0), (w, r)),
            ((w - r, h - r), (w, h - r),   (w - r, h)),
            ((r, h - r),     (r, h),       (0.0, h - r))]
    for (cx, cy), (x0, y0), (x1, y1) in arcs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(pcbnew.VECTOR2I(mm(x0), mm(y0)),
                         pcbnew.VECTOR2I(mm(cx), mm(cy)),
                         pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.05))
        board.Add(s)


def add_mounting_holes(board, beschreibung):
    for i, (x, y) in enumerate(beschreibung.M3_HOLES, start=1):
        fp = pcbnew.FOOTPRINT(board)
        fp.SetReference("H%d" % i)
        fp.Reference().SetVisible(False)
        fp.SetValue("M3")
        fp.Value().SetVisible(False)
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(pcbnew.VECTOR2I(mm(beschreibung.M3_DRILL),
                                    mm(beschreibung.M3_DRILL)))
        pad.SetDrillSize(pcbnew.VECTOR2I(mm(beschreibung.M3_DRILL),
                                         mm(beschreibung.M3_DRILL)))
        pad.SetLayerSet(pcbnew.PAD.UnplatedHoleMask())
        fp.Add(pad)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        board.Add(fp)


# ZONE.SetOutline() uebernimmt das SHAPE_POLY_SET NICHT -- es merkt sich
# nur den Zeiger. Sobald Python das Objekt einsammelt (bei einer lokalen
# Variablen also beim Verlassen der Funktion), zeigt die Zone ins Leere
# und der naechste Konnektivitaetsaufbau stirbt mit SIGSEGV. Der Absturz
# wirkt zufaellig, weil er davon abhaengt, wann der Sammler laeuft.
# Darum bleiben alle Umrisse hier am Leben.
_UMRISSE = []

# Entfernte Pads ebenso festhalten -- fp.Remove() gibt sie an Python ab,
# die Platine kennt sie danach aber noch. Werden sie eingesammelt,
# stirbt board.Save().
_ENTFERNT = []


def _outline(pts):
    o = pcbnew.SHAPE_POLY_SET()
    o.NewOutline()
    for x, y in pts:
        o.Append(mm(x), mm(y))
    _UMRISSE.append(o)
    return o


def _zone(board, netname, layers, pts, name=""):
    z = pcbnew.ZONE(board)
    z.SetLayerSet(layers)
    code = board.GetNetcodeFromNetname(netname)
    if code < 0:
        # Eine Regelflaeche ohne gueltigen Netzcode laesst den
        # Konnektivitaetsaufbau (board.BuildConnectivity()) abstuerzen --
        # darum hier hart abbrechen, statt eine kaputte Zone anzulegen.
        raise ValueError("Netz %r gibt es auf der Platine nicht" % netname)
    z.SetNetCode(code)
    z.SetOutline(_outline(pts))
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.2))
    if name:
        z.SetZoneName(name)
    board.Add(z)
    return z


def add_zones(board, beschreibung):
    """GND auf beiden Lagen giessen.

    Zwei Zonen statt einer ueber beide Lagen, weil sie sich in der
    Pad-Anbindung unterscheiden sollen: auf B.Cu voll angebunden, damit
    Bauteile mit thermischem Pad (im Vorlaeuferprojekt der DRV8876 mit
    zwoelf Waermevias) die Waerme wirklich in die Flaeche bekommen; auf
    F.Cu mit Waermefalle, damit bedrahtete Teile von Hand loetbar
    bleiben. Leistungsnetze laufen stattdessen als eigene, breitere
    Bahnen (siehe netclasses.py).
    """
    e = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
    w, h = beschreibung.BOARD_W, beschreibung.BOARD_H
    full = [(e, e), (w - e, e), (w - e, h - e), (e, h - e)]
    zs = []
    for lay, conn, name in (
            (pcbnew.F_Cu, pcbnew.ZONE_CONNECTION_THERMAL, "GND F.Cu"),
            (pcbnew.B_Cu, pcbnew.ZONE_CONNECTION_FULL, "GND B.Cu")):
        ls = pcbnew.LSET()
        ls.addLayer(lay)
        z = _zone(board, "GND", ls, full, name)
        z.SetPadConnection(conn)
        zs.append(z)
    return zs


def antenna_slot(board, beschreibung):
    """Den Schlitz unter der Pico-Antenne in Edge.Cuts fraesen.

    Nur aufrufen, wenn beschreibung.ANTENNA_SLOT gesetzt ist -- ein Modul
    ohne gesockelten Pico (z.B. das Motormodul) hat keine Antenne und
    keinen Schlitz. Eine Regelflaeche haette nur Kupfer verboten -- die
    Antenne saesse weiter ueber FR4. Hier fehlt stattdessen die Platine
    selbst. Die Ecken sind gerundet, weil gefraest wird und ein Fraeser
    keine Innenecke schneidet.
    """
    x0, y0, x1, y1 = beschreibung.ANTENNA_SLOT
    r = 1.0                                   # Fraeserradius
    for (ax, ay), (bx, by) in [((x0 + r, y0), (x1 - r, y0)),
                               ((x1, y0 + r), (x1, y1 - r)),
                               ((x1 - r, y1), (x0 + r, y1)),
                               ((x0, y1 - r), (x0, y0 + r))]:
        sh = pcbnew.PCB_SHAPE(board)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(pcbnew.VECTOR2I(mm(ax), mm(ay)))
        sh.SetEnd(pcbnew.VECTOR2I(mm(bx), mm(by)))
        sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetWidth(mm(0.05))
        board.Add(sh)
    for (cx, cy), (sx, sy), (ex, ey) in [
            ((x0 + r, y0 + r), (x0, y0 + r), (x0 + r, y0)),
            ((x1 - r, y0 + r), (x1 - r, y0), (x1, y0 + r)),
            ((x1 - r, y1 - r), (x1, y1 - r), (x1 - r, y1)),
            ((x0 + r, y1 - r), (x0 + r, y1), (x0, y1 - r))]:
        sh = pcbnew.PCB_SHAPE(board)
        sh.SetShape(pcbnew.SHAPE_T_ARC)
        sh.SetArcGeometry(pcbnew.VECTOR2I(mm(sx), mm(sy)),
                          pcbnew.VECTOR2I(mm(cx), mm(cy)),
                          pcbnew.VECTOR2I(mm(ex), mm(ey)))
        sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetWidth(mm(0.05))
        board.Add(sh)


def courtyard_bbox(fp):
    """Hof-Rechteck des platzierten Bauteils in mm (links, oben, rechts, unten)."""
    box = None
    for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        poly = fp.GetCourtyard(lay)
        if poly.OutlineCount() == 0:
            continue
        bb = poly.BBox()
        cur = (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())
        box = cur if box is None else (min(box[0], cur[0]), min(box[1], cur[1]),
                                       max(box[2], cur[2]), max(box[3], cur[3]))
    return box


def place(board, comps, beschreibung, kicad_dir):
    """Footprints laden, drehen und so schieben, dass der Hof auf der
    Beschreibung sitzt. kicad_dir ist das Projektverzeichnis, in dem
    kicadlibs.footprint_libs() nach einer projekteigenen fp-lib-table
    sucht (typischerweise der Ordner der Ziel-.kicad_pcb)."""
    libs = kicadlibs.footprint_libs(kicad_dir)
    placed, problems = [], []
    for ref in sorted(beschreibung.PLACEMENT):
        p = beschreibung.PLACEMENT[ref]
        name = beschreibung.FOOTPRINTS[ref]
        lib, fpname = name.split(":")
        if ref in comps and comps[ref]["footprint"] != name:
            problems.append("%s: Schaltplan will %s, Beschreibung %s"
                            % (ref, comps[ref]["footprint"], name))
        fp = pcbnew.FootprintLoad(libs[lib], fpname)
        if fp is None:
            problems.append("%s: %s nicht ladbar" % (ref, name))
            continue
        board.Add(fp)
        fp.SetReference(ref)
        fp.SetValue(comps.get(ref, {}).get("value", ""))
        fp.SetOrientationDegrees(p.rot)

        # Der Footprint-Ursprung liegt nicht zwangslaeufig in der Mitte
        # des Hofes. Darum erst drehen, dann den Hof messen und um die
        # Differenz schieben -- sonst sitzt das Teil um den Versatz
        # zwischen Ursprung und Hofmitte daneben.
        box = courtyard_bbox(fp)
        if box is None:
            problems.append("%s: kein Courtyard" % ref)
            continue
        dx = mm(p.x) - box[0]
        dy = mm(p.y) - box[1]
        fp.Move(pcbnew.VECTOR2I(dx, dy))
        placed.append(ref)

    fehlt = sorted(set(comps) - set(beschreibung.PLACEMENT))
    if fehlt:
        problems.append("ohne Platzierung in der Beschreibung: " + ", ".join(fehlt))
    return placed, problems


def tidy_silkscreen(board, beschreibung):
    """Beschriftung aufraeumen.

    Die Vorgabe der Bibliotheken ist fuer grosszuegige Platinen gedacht:
    1-mm-Text neben jedem Bauteil. Auf einer dicht bestueckten Platine
    ergibt das ein Gewirr, das keiner mehr lesen kann und das die DRC
    zu Recht bemaengelt.

    Darum: Werte wandern auf F.Fab (die Bestueckungszeichnung, wo sie
    hingehoeren), Referenzen werden kleiner, und die Referenzen von
    SMD-Teilen (p.tht == False) wandern ebenfalls auf F.Fab -- gedruckt
    waeren sie ohnehin oft verdeckt, gebraucht werden sie nur beim
    Bestuecken, und dafuer ist die Zeichnung da.
    """
    klein = pcbnew.VECTOR2I(mm(0.7), mm(0.7))
    n_fab = 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        p = beschreibung.PLACEMENT.get(ref)

        wert = fp.Value()
        wert.SetLayer(pcbnew.F_Fab)
        wert.SetVisible(False)

        r = fp.Reference()
        r.SetTextSize(klein)
        r.SetTextThickness(mm(0.12))
        if p is not None and not p.tht:
            r.SetLayer(pcbnew.F_Fab)
            n_fab += 1
        elif ref.startswith("H"):
            r.SetVisible(False)
        else:
            r.SetLayer(pcbnew.F_SilkS)
            # ueber das Bauteil setzen, dort ist am ehesten Platz
            box = courtyard_bbox(fp)
            if box is not None:
                r.SetPosition(pcbnew.VECTOR2I(
                    (box[0] + box[2]) // 2, box[1] - mm(0.9)))
    return n_fab


def mark_version(board, versionstext, beschreibung, hinweise=()):
    """Versionsvermerk und optionale Bauhinweise aufs Silkscreen drucken.

    Verallgemeinert aus dem Vorlaeuferprojekt, das hier fest "v2 /
    2026-08" und einen Warnhinweis zur Elko-Polaritaet eines bestimmten
    Bauteils eintrug (auf der Vorgaengerversion jener Platine waren an
    einer falschen Polung zwei Elkos explodiert, weil der Silkscreen-
    Aufdruck nicht zur tatsaechlichen Polung passte -- ohne sichtbaren
    Hinweis haette jemand die alte Anweisung wiederholt). Text und
    Hinweise sind hier Parameter statt eingebrannt, weil die Platine je
    Aufruf wechselt: nicht jede PicoStack-Platine braucht denselben
    Hinweis, manche brauchen gar keinen.

    hinweise: Liste von (text, x, y, groesse_mm)-Tupeln, zusaetzlich zum
    Versionsvermerk.
    """
    zeilen = [(versionstext, 2.0, beschreibung.BOARD_H - 2.0, 1.0)]
    zeilen += list(hinweise)
    for txt, x, y, groesse in zeilen:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(mm(groesse), mm(groesse)))
        t.SetTextThickness(mm(0.15))
        t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        board.Add(t)
        _UMRISSE.append(t)


def drop_offboard_pads(board, beschreibung):
    """Pads ausserhalb des Umrisses entfernen.

    Ein Ueberhang (z.B. fuer eine Antenne) kann Pad-Positionen mit
    hinausnehmen. Blieben sie stehen, stuenden im Bohrprogramm Loecher
    neben der Platine -- die Fertigung bohrt dann ins Leere oder weist
    die Daten zurueck. Entfernen ist der einzige Weg, der die
    Abstandsregel zuverlaessig einhaelt.
    """
    e = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
    w, h = beschreibung.BOARD_W, beschreibung.BOARD_H
    weg, mit_netz = [], []
    for fp in board.GetFootprints():
        for pad in list(fp.Pads()):
            bb = pad.GetBoundingBox()
            if (bb.GetLeft() / 1e6 < e or bb.GetTop() / 1e6 < e or
                    bb.GetRight() / 1e6 > w - e or
                    bb.GetBottom() / 1e6 > h - e):
                ref = "%s.%s" % (fp.GetReference(), pad.GetNumber())
                # Ein Pad mit Netz darf nicht einfach verschwinden: das
                # Signal waere danach unverdrahtbar, ohne dass DRC oder
                # Schaltplan-Abgleich es meldet -- der Netzname bleibt,
                # nur das Pad fehlt.
                if pad.GetNetCode() > 0:
                    mit_netz.append("%s (%s)" % (ref, pad.GetNetname()))
                weg.append(ref)
                fp.Remove(pad)
                _ENTFERNT.append(pad)
    return weg, mit_netz


def assign_nets(board, nets, ohne_pad=frozenset()):
    """Netze anlegen und den Pads zuweisen.

    Eine Pad-Nummer kann mehrfach vorkommen: z.B. tragen die Waermevias
    eines Treiber-ICs alle dieselbe Pad-Nummer des Waermepads und muessen
    alle auf dessen Netz landen.

    ohne_pad: Menge von (ref, pin)-Paaren, die bekanntermassen keinen
    Footprint-Pad haben (z.B. Debug-Pads, die im THT-Footprint fehlen)
    und deshalb nicht als Fehler, sondern nur als Hinweis gezaehlt
    werden.
    """
    pads = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num:
                pads.setdefault((fp.GetReference(), num), []).append(pad)

    problems, unbekannt, n_assigned = [], [], 0
    for name, pins in sorted(nets.items()):
        net = board.FindNet(name)
        if net is None:
            net = pcbnew.NETINFO_ITEM(board, name)
            board.Add(net)
        for ref, pin in pins:
            got = pads.get((ref, pin))
            if not got:
                (problems if (ref, pin) not in ohne_pad
                 else unbekannt).append(
                    "Pad %s.%s gibt es auf der Platine nicht" % (ref, pin))
                continue
            for pad in got:
                pad.SetNet(net)
                n_assigned += 1

    ohne = sorted("%s.%s" % k for k, ps in pads.items()
                  if any(p.GetNetCode() == 0 for p in ps))
    return n_assigned, problems, ohne, len(unbekannt)


def bauen(beschreibung, board_pfad, sch_pfad, kicad_dir=None,
         ohne_pad=frozenset(), versionstext=None, hinweise=()):
    """Baut eine Platine aus Schaltplan-Netzliste und beschreibung neu auf.

    Ersetzt das alte main(), das eine feste Datei (build.BOARD, samt
    fest eingetragenem KICAD-Verzeichnis) fuer genau eine Platine
    ansprach. board_pfad und sch_pfad sind jetzt Parameter, damit sich
    Sockel- und Motorplatine im selben Lauf bauen lassen, ohne dieses
    Modul zu kopieren.

    kicad_dir: Projektverzeichnis fuer die Footprint-Bibliotheken
    (Standard: der Ordner von board_pfad).
    """
    if kicad_dir is None:
        kicad_dir = os.path.dirname(os.path.abspath(board_pfad))

    bad = geometry.check_all(beschreibung.PLACEMENT, beschreibung)
    if bad:
        print("Platzierung fehlerhaft:")
        for b in bad:
            print("  -", b)
        return 1

    comps, nets = read_netlist(sch_pfad)
    board = new_board(board_pfad)
    draw_outline(board, beschreibung)
    add_mounting_holes(board, beschreibung)
    placed, problems = place(board, comps, beschreibung, kicad_dir)
    n, np_, ohne, n_bekannt = assign_nets(board, nets, ohne_pad)
    # Erst Netze zuweisen, dann die Pads im Ueberhang entfernen: sonst
    # meldet die Zuweisung sie als fehlend und die Netzliste sieht
    # unvollstaendig aus, obwohl nur Loecher neben der Platine wegfallen.
    weg, weg_mit_netz = drop_offboard_pads(board, beschreibung)
    n_fab = tidy_silkscreen(board, beschreibung)
    if versionstext:
        mark_version(board, versionstext, beschreibung, hinweise)
    if getattr(beschreibung, "ANTENNA_SLOT", None) is not None:
        antenna_slot(board, beschreibung)
    add_zones(board, beschreibung)
    board.BuildListOfNets()
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))
    problems += np_
    board.BuildListOfNets()
    board.Save(board_pfad)

    bb = board.GetBoardEdgesBoundingBox()
    print("Platine %.1f x %.1f mm" % (bb.GetWidth() / 1e6, bb.GetHeight() / 1e6))
    print("%d Bauteile platziert, %d Pads an %d Netzen"
          % (len(placed), n, len(nets)))
    if weg:
        print("%d Pads ausserhalb des Umrisses entfernt: %s"
              % (len(weg), ", ".join(weg)))
    for x in weg_mit_netz:
        problems.append("Pad %s traegt ein Netz und faellt trotzdem weg" % x)
    print("Beschriftung: %d SMD-Referenzen auf F.Fab, Werte ausgeblendet"
          % n_fab)
    if n_bekannt:
        print("%d bekannte Pins ohne Pad uebergangen" % n_bekannt)
    if ohne:
        print("Pads ohne Netz (%d): %s" % (len(ohne), ", ".join(ohne[:12])
                                           + (" ..." if len(ohne) > 12 else "")))
    for p in problems:
        print("  ! " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    import importlib

    if len(sys.argv) != 4:
        raise SystemExit(
            "Aufruf: build.py <spec_modul, z.B. spec_sockel> "
            "<board.kicad_pcb> <schaltplan.kicad_sch>")
    beschreibung = importlib.import_module(sys.argv[1])
    raise SystemExit(bauen(beschreibung, sys.argv[2], sys.argv[3]))

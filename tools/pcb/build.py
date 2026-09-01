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
import math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pcbnew
import fertigung, geometry, kicadlibs


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


def bogenmitte(mittelpunkt, start, ende):
    """Der Punkt AUF dem Bogen zwischen Start und Ende, als VECTOR2I-Paar.

    WARUM ES DIESE FUNKTION GIBT (2026-09-01, Aufgabe 6, am Rendering
    gesehen und danach nachgemessen).

    pcbnew.PCB_SHAPE.SetArcGeometry(start, mitte, ende) erwartet DREI
    PUNKTE AUF DEM BOGEN. Das uebernommene draw_outline() uebergab als
    zweites Argument den MITTELPUNKT des Kreises. KiCad legt daraufhin
    den Umkreis durch die drei Punkte -- und der ist ein ganz anderer
    Kreis:

        gewollt: Bogen von (0|3) nach (3|0) um (3|3), Radius 3,00
        gebaut : Umkreis von (3|0), (3|3), (0|3)
                 -> Mittelpunkt (1,5|1,5), Radius 2,121, DURCH (3|3)

    Der Bogen rundet die Ecke dadurch nicht, sondern schneidet in die
    Platine hinein. Zwei Folgen, beide an der gebauten Datei gemessen:

      * Die Ecken sind keine 3-mm-Radien. Das Gehaeuse (Aufgabe 9) wird
        gegen den Vertragswert CORNER_R konstruiert und passte nicht.
      * Die M3-Bohrungen bei (4|4) und (4|56) liegen nur noch 1,414 mm
        von der Kante entfernt, bei 1,60 mm Bohrungsradius: der
        Ausschnitt BRICHT IN DIE BOHRUNG DURCH (-0,186 mm Steg). Eine
        Schraube haette dort keinen geschlossenen Rand mehr.

    Dasselbe galt fuer die vier Ecken des Antennenschlitzes: statt des
    Fraeserradius 1,00 mm entstanden 0,707 mm -- kleiner als der
    Fraeser, also gar nicht herstellbar.

    Keine bestehende Pruefung hat das gesehen: DRC prueft in diesem
    Projekt keinen Loch-Kanten-Abstand, und der Umriss stimmt in der
    Bounding Box (64 x 60 mm) weiterhin genau. Sichtbar wurde es erst
    auf dem 3D-Rendering -- der Schritt "Hinsehen" aus dem Aufgabenbrief.

    Herkunft: build.py stammt aus PecheAuxCanards. Dort ist derselbe
    Aufruf, und dort wurde eine Platine tatsaechlich gefertigt.
    """
    cx, cy = mittelpunkt
    r = math.hypot(start[0] - cx, start[1] - cy)
    # Richtung vom Mittelpunkt zur Sehnenmitte: dorthin zeigt der
    # kurze Bogen. Bei einem Viertelkreis ist das die Winkelhalbierende.
    sx = (start[0] + ende[0]) / 2.0 - cx
    sy = (start[1] + ende[1]) / 2.0 - cy
    L = math.hypot(sx, sy)
    if L == 0:
        raise ValueError("Start und Ende liegen sich diametral gegenueber -- "
                         "der kurze Bogen ist dann nicht bestimmt")
    return (mm(cx + r * sx / L), mm(cy + r * sy / L))


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
                         pcbnew.VECTOR2I(*bogenmitte((cx, cy), (x0, y0),
                                                     (x1, y1))),
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
    # 0,20 mm statt der geerbten 0,30: der Guss darf so nah an eine
    # Bahn heran, wie die Entwurfsregel es ohnehin erlaubt. Die
    # zusaetzlichen 0,10 mm kosteten unter dem Stapelstecker echte
    # Verbindung -- dort laufen vierzig Bahnen nebeneinander, und der
    # Guss zerfiel zwischen ihnen in Inseln. Eine davon trug den
    # Massepin 28 des Stapelsteckers: er war mit 3 statt 66 Elementen
    # verbunden, also nicht an Masse.
    z.SetLocalClearance(mm(0.2))
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
    # Nachtrag 2026-09-01 (Aufgabe 6): F.Cu bekommt jetzt EBENFALLS
    # volle Anbindung. Die urspruengliche Waermefalle auf F.Cu war fuer
    # die Handloetbarkeit gedacht; auf der fertig verlegten Sockelplatine
    # brachte sie das Gegenteil. Unter dem Stapelstecker laufen vierzig
    # Bahnen, die die F.Cu-Flaeche dort in schmale Streifen zerschneiden.
    # Sieben GND-Pads bekamen deshalb statt der geforderten zwei Speichen
    # nur eine, zwei davon zu einer abgeschnittenen Insel -- also weder
    # gute Loetbarkeit noch gute Leitfaehigkeit.
    # Entscheidend fuer die Loetbarkeit ist ohnehin nicht F.Cu: es sind
    # durchkontaktierte Pads, und auf B.Cu liegt seit jeher die VOLLE
    # Flaeche. Die Waerme laeuft durch die Huelse in diese Flaeche,
    # gleichgueltig was F.Cu tut. Die Waermefalle auf der Oberseite
    # kostete also nur Verbindung.
    for lay, conn, name in (
            (pcbnew.F_Cu, pcbnew.ZONE_CONNECTION_FULL, "GND F.Cu"),
            (pcbnew.B_Cu, pcbnew.ZONE_CONNECTION_FULL, "GND B.Cu")):
        ls = pcbnew.LSET()
        ls.addLayer(lay)
        z = _zone(board, "GND", ls, full, name)
        z.SetPadConnection(conn)
        # Abgeschnittene Kupferinseln entfernen statt stehen lassen.
        # Eine Insel ohne Anbindung ist keine Masse, sondern ein Stueck
        # Blech, das mitschwingt -- und die DRC meldet sie zu Recht als
        # fehlende Verbindung der Flaeche mit sich selbst.
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
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
        # Punkt AUF dem Bogen, nicht der Mittelpunkt -- s. bogenmitte().
        # Hier waren aus dem Fraeserradius 1,00 mm sonst 0,707 mm
        # geworden: enger als der Fraeser, also nicht herstellbar.
        sh.SetArcGeometry(pcbnew.VECTOR2I(mm(sx), mm(sy)),
                          pcbnew.VECTOR2I(*bogenmitte((cx, cy), (sx, sy),
                                                      (ex, ey))),
                          pcbnew.VECTOR2I(mm(ex), mm(ey)))
        sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetWidth(mm(0.05))
        board.Add(sh)


def antenna_slot_keepout(board, beschreibung):
    """Sperrflaeche um den Antennenschlitz, um die Kantenabstandsregel.

    Der Schlitz ist ein Innenausschnitt in Edge.Cuts. pcbnew exportiert
    ihn in die DSN als Sperrflaeche mit GENAU seinem Umriss -- freerouting
    haelt daran nur seinen eigenen Bahnabstand (0,2 mm) ein, nicht die
    Kantenabstandsregel der Platine (0,5 mm). Ergebnis waren vier
    DRC-Fehler: zwei Bahnen liefen auf 0,34 bzw. 0,44 mm an die
    Fraeskante heran. An einer gefraesten Kante ist das kein
    Schoenheitsfehler -- der Fraeser hat Spiel, und eine angeschnittene
    Bahn ist ein offener Stromkreis.
    Diese Regelflaeche sagt es dem Router ausdruecklich.
    """
    x0, y0, x1, y1 = beschreibung.ANTENNA_SLOT
    e = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
    pts = [(x0 - e, y0 - e), (x1 + e, y0 - e), (x1 + e, y1 + e), (x0 - e, y1 + e)]
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    ls = pcbnew.LSET()
    ls.addLayer(pcbnew.F_Cu)
    ls.addLayer(pcbnew.B_Cu)
    z.SetLayerSet(ls)
    z.SetOutline(_outline(pts))
    z.SetZoneName("Antennenschlitz Kantenabstand")
    board.Add(z)
    return z


def stitching_vias(board, beschreibung):
    """GND-Vias, die die beiden Masseflaechen miteinander vernaehen.

    Ohne sie meldete die DRC "Missing connection" zwischen der
    F.Cu- und der B.Cu-Massflaeche: die bedrahteten GND-Pads verbinden
    zwar beide Lagen, ihre Waermefallen auf F.Cu zerfielen aber in
    Inseln, von denen eine keinen Weg zum Rest hatte. Die Vias stehen in
    der Beschreibung (STITCH_VIAS) und nicht hier, weil ihre Lage von
    der freien Flaeche der jeweiligen Platine abhaengt; sie werden VOR
    dem Verlegen gesetzt, damit der Router sie als Hindernis kennt statt
    hinterher darueber zu stolpern.
    """
    stellen = getattr(beschreibung, "STITCH_VIAS", ())
    code = board.GetNetcodeFromNetname("GND")
    if not stellen or code < 0:
        return 0
    for x, y in stellen:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        v.SetWidth(mm(fertigung.VIA_PAD))
        v.SetDrill(mm(fertigung.VIA_DRILL))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(code)
        board.Add(v)
    return len(stellen)


def courtyard_bbox(fp):
    """Hof-Rechteck des platzierten Bauteils in mm (links, oben, rechts, unten).

    Um fertigung.HOF_STRICH geschrumpft, damit dieses Rechteck DASSELBE
    ist, das tools/stack_spec.py (FOOTPRINT_HOF, STECKER_POS) aus der
    .kicad_mod-Datei liest: pcbnew liefert den mit der Strichbreite
    gestrichelten Umriss und rundet nach aussen, der Vertrag die rohen
    Polygonkoordinaten. Ohne das Schrumpfen laege jeder Stecker
    0,045 mm neben seiner Vertragskoordinate -- s. die Herleitung bei
    fertigung.HOF_STRICH. Hier und nicht in den einzelnen
    Platinenbeschreibungen, weil sonst jede kuenftige Beschreibung die
    Korrektur erneut von Hand mitbringen muesste (Aufgabe 7 waere die
    erste, die es vergessen koennte).
    """
    box = None
    for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        poly = fp.GetCourtyard(lay)
        if poly.OutlineCount() == 0:
            continue
        bb = poly.BBox()
        cur = (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())
        box = cur if box is None else (min(box[0], cur[0]), min(box[1], cur[1]),
                                       max(box[2], cur[2]), max(box[3], cur[3]))
    if box is None:
        return None
    s = mm(fertigung.HOF_STRICH)
    return (box[0] + s, box[1] + s, box[2] - s, box[3] - s)


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
        if getattr(p, "unten", False):
            # Auf die Rueckseite spiegeln, BEVOR der Hof gemessen wird --
            # beim Spiegeln wandert der Hof von F.CrtYd nach B.CrtYd und
            # die Geometrie kippt um die y-Achse. Danach messen und
            # schieben stellt sicher, dass das Rechteck trotzdem auf der
            # vorgesehenen Stelle landet. Warum ueberhaupt gespiegelt
            # wird, steht bei Platz.unten in der Platinenbeschreibung.
            fp.Flip(fp.GetPosition(), False)

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
    klein = pcbnew.VECTOR2I(mm(fertigung.SILK_TEXT), mm(fertigung.SILK_TEXT))
    hoehe = fertigung.SILK_TEXT

    # Die Hoefe aller Bauteile, gegen die eine Beschriftung nicht stossen
    # darf. Aus der Beschreibung statt aus der Platine, weil der Text
    # gesetzt wird, bevor die Konnektivitaet steht.
    hoefe = [(q.x, q.y, q.x + q.w, q.y + q.h)
             for q in beschreibung.PLACEMENT.values()]

    def frei(x0, y0, x1, y1, eigener):
        """Passt ein Textkasten dorthin, ohne fremde Hoefe oder die Kante?"""
        e = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
        if (x0 < e or y0 < e or x1 > beschreibung.BOARD_W - e
                or y1 > beschreibung.BOARD_H - e):
            return False
        for k, h in enumerate(hoefe):
            if k == eigener:
                continue
            if x0 < h[2] and h[0] < x1 and y0 < h[3] and h[1] < y1:
                return False
        return True

    n_fab = 0
    refs = list(beschreibung.PLACEMENT)
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        p = beschreibung.PLACEMENT.get(ref)

        # Auf der Rueckseite gehoert die Beschriftung auf die RUECKSEITIGEN
        # Lagen. Ein Text auf F.Fab/F.SilkS bei einem gespiegelten
        # Bauteil steht seitenverkehrt -- die DRC meldet ihn als
        # "Mirrored text on front layer", und gedruckt waere er
        # unlesbar. Aufgefallen, als die Steckerhaelften auf die
        # Unterseite wanderten (2026-09-01).
        unten = getattr(p, "unten", False) if p is not None else False
        fab = pcbnew.B_Fab if unten else pcbnew.F_Fab
        silk = pcbnew.B_SilkS if unten else pcbnew.F_SilkS

        wert = fp.Value()
        wert.SetLayer(fab)
        wert.SetVisible(False)

        r = fp.Reference()
        r.SetTextSize(klein)
        r.SetTextThickness(mm(fertigung.SILK_DICKE))
        if p is not None and not p.tht:
            r.SetLayer(fab)
            n_fab += 1
        elif ref.startswith("H"):
            r.SetVisible(False)
        elif p is None:
            r.SetLayer(silk)
        else:
            r.SetLayer(silk)
            # Ueber das Bauteil setzen -- aber nur, wenn dort wirklich
            # Platz ist. Beim Pico (53,85 mm breit, direkt unter dem
            # Stapelstecker) landete die Beschriftung sonst mitten auf
            # dessen Silkscreen und ueber einem seiner Pads: zwei
            # DRC-Fehler, die erst am gerouteten Board auffielen.
            # Faellt der Platz darueber weg, wandert der Text in den
            # eigenen Hof -- der gehoert dem Bauteil ohnehin.
            breite = 0.75 * hoehe * max(2, len(ref))   # grob, reicht hier
            mitte_x = p.x + p.w / 2.0
            eigener = refs.index(ref)
            oben = (mitte_x - breite / 2, p.y - 0.9 - hoehe / 2,
                    mitte_x + breite / 2, p.y - 0.9 + hoehe / 2)
            if frei(*oben, eigener):
                r.SetPosition(pcbnew.VECTOR2I(mm(mitte_x), mm(p.y - 0.9)))
            else:
                # Kein Platz daneben: dann gehoert die Kennung auf die
                # Bestueckungszeichnung, nicht mit Gewalt auf den Druck.
                # In den eigenen Hof zu schieben half nicht -- dort liegt
                # der Silkscreen-Umriss des Bauteils selbst (bei der
                # Klemme J1 nachgewiesen), und ein Text ueber dem eigenen
                # Umriss ist genauso unlesbar wie einer ueber dem
                # fremden.
                r.SetLayer(fab)
                r.SetPosition(pcbnew.VECTOR2I(mm(mitte_x),
                                              mm(p.y + p.h / 2)))
                n_fab += 1
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
        antenna_slot_keepout(board, beschreibung)
    n_stich = stitching_vias(board, beschreibung)
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
    if n_stich:
        print("%d GND-Vias zum Vernaehen der Masseflaechen gesetzt" % n_stich)
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

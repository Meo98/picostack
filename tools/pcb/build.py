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
import math, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import pcbnew
import fertigung, geometry, gusslage, kicadlibs
import stack_spec as S    # noqa: E402  -- RANDPADS/VERTRAG_VERSION/
                           # PROJEKTNAME/MODULTYPEN fuer die Beschriftung
                           # (R7-R9), s. randpad_labels()/board_identity()


def mm(v):
    return pcbnew.FromMM(v)


# ---------------------------------------------------------------- Netzliste

def read_netlist(sch):
    """(bauteile, netze) aus der von KiCad exportierten Netzliste.

    bauteile: ref -> {"value":..., "footprint":...}
    netze:    netzname -> [(ref, pin), ...]
    """
    # Zielname EINDEUTIG je Schaltplan, und vorher weggeraeumt.
    #
    # WARUM (Fix-Runde 2 zu Aufgabe 7, Zusatz-Ruling). Hier stand ein
    # FESTER Pfad /tmp/build_netlist.net, und geprueft wurde nur, ob die
    # Datei EXISTIERT. Beides zusammen ist eine stille Falle: schlaegt
    # der Export fehl (falscher Pfad, kaputter Schaltplan, kicad-cli
    # nicht da), liegt die Datei vom LETZTEN Lauf noch da -- und
    # build.py baut die Platine seelenruhig aus einer veralteten
    # Netzliste weiter. Kein Fehler, keine Warnung, falsche Daten.
    # Mir ist das in dieser Aufgabe einmal passiert: ich habe mit einem
    # nicht existierenden Schaltplanpfad gebaut und trotzdem 252 Pads an
    # 72 Netzen bekommen. Dieselbe Fehlerklasse wie die abstuerzende
    # Steckerprobe -- falsche oder fehlende Pruefung, die als "in
    # Ordnung" durchgeht.
    #
    # Jetzt: Name aus dem Schaltplan abgeleitet (zwei Platinen im selben
    # Lauf koennen sich nicht mehr in die Quere kommen), Altbestand
    # geloescht, UND der Rueckgabewert von kicad-cli ausgewertet.
    out = os.path.join(
        tempfile.gettempdir(),
        "build_netlist_%s.net" % os.path.splitext(os.path.basename(sch))[0])
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run(["kicad-cli", "sch", "export", "netlist",
                        "--output", out, sch], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        raise SystemExit(
            "Netzliste nicht exportierbar (kicad-cli Rueckgabe %d) fuer %s\n"
            "%s%s" % (r.returncode, sch, r.stdout[-800:], r.stderr[-800:]))
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
    # Mindest-Maskensteg auf 0,10 mm: die KiCad-Vorgabe (0,25) ist bei
    # 0,5-mm-Raster (VSSOP-8, Padluecke 0,20 mm) unerfuellbar -- die
    # Maskenoeffnungen verschmelzen und die DRC meldet Bruecken
    # zwischen fremden Netzen. 0,10 mm ist eine FERTIGUNGSANNAHME fuer
    # gruenen LPI-Lack und beim Fertiger zu bestaetigen, bevor bestellt
    # wird -- sie steht deshalb im Bericht der Aufgabe, nicht nur hier.
    board.GetDesignSettings().m_SolderMaskMinWidth = mm(0.1)
    # Mindestabstand auf 0,15 mm: die Padluft der Feinraster-Gehaeuse
    # (VSSOP-8 im 0,5-mm-Raster: 0,35er-Pads -> 0,15 Luft) ist
    # KONSTRUKTIONSBEDINGT kleiner als die 0,20 der Netzklassen. Die
    # Netzklassen fordern weiterhin 0,20 zwischen Bahnen; hier faellt
    # nur die harte Untergrenze der Platine auf das, was der Fertiger
    # kann (JLCPCB: 0,127). Ohne beides -- Untergrenze UND die
    # Pad-Ausnahme in feinraster_pads() -- meldet die DRC die vier
    # Nachbarpad-Paare des VSSOP-8 als Verletzung.
    board.GetDesignSettings().m_MinClearance = mm(0.15)
    return board


def feinraster_pads(board):
    """Pad-Ausnahmen fuer Gehaeuse, deren Raster enger ist als die Regel.

    Zwei Faelle, beide 2026-09-02 an der DRC des Motormoduls gefunden:

    * Padluft unter Netzklassen-Abstand: beim VSSOP-8 (0,5-mm-Raster)
      liegen Nachbarpads 0,15 mm auseinander -- die DRC forderte 0,20
      und meldete alle vier Paare. Die Ausnahme gilt NUR fuer diese
      Pads (SetLocalClearance), nicht fuer die Platine.
    * Maskenrand im Footprint: die TI-Vorlage des DRV8876 gibt jedem
      Pad solder_mask_margin 0,102 mm mit. Bei 0,20 Padluft
      ueberlappen sich die Maskenoeffnungen (0,20 - 2*0,102 < 0) --
      dreizehn Masken-Bruecken zwischen fremden Netzen, die KEINE
      Einstellung der Platine beheben kann, weil der Pad-Wert alles
      uebersteuert. Der Rand wird auf 0 gesetzt (Oeffnung = Padform,
      wie ueberall sonst auf der Platine).
    """
    n_luft, n_maske = 0, 0
    for f in board.GetFootprints():
        fein = "P0.5mm" in str(f.GetFPID().GetLibItemName())
        for p in f.Pads():
            if fein:
                p.SetLocalClearance(mm(0.15))
                n_luft += 1
            rand = p.GetLocalSolderMaskMargin()
            if rand is not None and rand != 0:
                p.SetLocalSolderMaskMargin(0)
                n_maske += 1
    if n_luft or n_maske:
        print("Feinraster-Ausnahmen: %d Pads Luft 0,15; %d Maskenraender "
              "genullt" % (n_luft, n_maske))


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
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    ls.addLayer(pcbnew.F_Cu)
    ls.addLayer(pcbnew.B_Cu)
    z.SetLayerSet(ls)
    z.SetOutline(_outline(pts))
    z.SetZoneName("Antennenschlitz Kantenabstand")
    board.Add(z)
    return z


def pre_tracks(board, beschreibung):
    """Vorverdrahtung aus der Beschreibung (PRE_TRACKS) auf die Platine.

    Eintraege: (netzname, lagenname, [(x, y), ...]). Gelegt VOR dem
    Verlegen, damit freerouting sie als Hindernis kennt und die
    Signalbahnen darum herum fuehrt -- genau wie die Naehvias.

    Gebraucht fuer die GND-Stummel der Sockelplatine: unter dem
    Stapelstecker zerschneiden vierzig Bahnen den Masseguss auf beiden
    Lagen, und ohne garantierten Weg strandete in jedem Router-Lauf ein
    anderer Massepin auf seiner eigenen Insel (Herleitung bei
    spec_sockel.PRE_TRACKS).
    """
    eintraege = getattr(beschreibung, "PRE_TRACKS", ())
    lagen = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    pads = {(f.GetReference(), p.GetNumber()): p.GetPosition()
            for f in board.GetFootprints() for p in f.Pads()}

    def punkt(q):
        if isinstance(q, tuple) and len(q) == 3 and q[0] == "PAD":
            # ("PAD", ref, nummer): aufgeloest aus der platzierten
            # Platine -- die Beschreibung ist KiCad-frei und kennt die
            # Pad-Lagen der Footprints nicht (gebraucht z.B. fuer die
            # zusammengebundenen Eingaenge des VSSOP-8: benachbarte
            # Pads desselben Netzes, die freerouting bei 0,5-mm-Raster
            # nicht selbst verbinden kann).
            pos = pads[(q[1], q[2])]
            return pos.x, pos.y
        return mm(q[0]), mm(q[1])

    n = 0
    for eintrag in eintraege:
        netz, lage, punkte = eintrag[:3]
        breite = eintrag[3] if len(eintrag) > 3 else fertigung.TRACK_SIGNAL
        code = board.GetNetcodeFromNetname(netz)
        if code < 0:
            raise ValueError("PRE_TRACKS: Netz %r gibt es nicht" % netz)
        for a, b in zip(punkte, punkte[1:]):
            # Nur 0/45/90 Grad, EXAKT. Ein Halsstueck des Motormoduls
            # verfehlte die Pad-Mitte um 5 um -- der fast-gerade Draht
            # liess freerouting 2.2.4 vor Durchgang 1 endlos haengen
            # (Log endet nach "Job started"; achsparallel gemacht lief
            # derselbe Stand in 38 s durch). Handkoordinaten gegen
            # aufgeloeste ("PAD",...)-Punkte sind genau die Falle.
            # Verglichen auf um gerundet: das ist die Aufloesung der
            # DSN, also das, was freerouting wirklich sieht. Nanometer-
            # Reste aus der Float-Arithmetik (10,54+1,27 ergibt
            # 11,809999...) sind KEIN Schiefstand -- der erste, exakte
            # Vergleich meldete genau so einen GND-Stummel, den
            # freerouting nachweislich sauber verlegt hatte.
            (ax, ay), (bx, by) = punkt(a), punkt(b)
            dx = round((bx - ax) / 1000.0)
            dy = round((by - ay) / 1000.0)
            if dx and dy and abs(dx) != abs(dy):
                raise ValueError(
                    "PRE_TRACKS %s: Segment %s -> %s ist weder 0/90 noch "
                    "45 Grad (dx=%d dy=%d um) -- freerouting haengt an "
                    "schiefen Vorverdrahtungs-Draehten; Endpunkt exakt "
                    "auf die Pad-Koordinate legen" % (netz, a, b, dx, dy))
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(ax, ay))
            t.SetEnd(pcbnew.VECTOR2I(bx, by))
            t.SetWidth(mm(breite))
            t.SetLayer(lagen[lage])
            t.SetNetCode(code)
            board.Add(t)
            n += 1
    return n


def pre_vias(board, beschreibung):
    """Vorab gesetzte Vias aus der Beschreibung (PRE_VIAS).

    Eintraege: (netzname, x, y). Gebraucht, sobald eine Vorverdrahtung
    die Lage wechseln muss -- PRE_TRACKS kann nur Draehte legen.
    Erster Fall (Motormodul, 2026-09-02): /SEL_OUT an U103-2 ist auf
    F.Cu vollstaendig eingemauert (westlich die FLASH-Gassenbahn,
    noerdlich/suedlich die Nachbarpads, oestlich der Gehaeusekoerper);
    jeder denkbare F.Cu-Umweg kreuzt eine andere Vorverdrahtung oder
    eine TSSOP-Padreihe. Zwei Vias und ein B.Cu-Stueck loesen das.

    Abgedeckt wie die Naehvias (Verdreh-Kupferregel des Vertrags).
    """
    n = 0
    for netz, x, y in getattr(beschreibung, "PRE_VIAS", ()):
        code = board.GetNetcodeFromNetname(netz)
        if code < 0:
            raise ValueError("PRE_VIAS: Netz %r gibt es nicht" % netz)
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        v.SetWidth(mm(fertigung.VIA_PAD))
        v.SetDrill(mm(fertigung.VIA_DRILL))
        v.SetNetCode(code)
        v.SetFrontTentingMode(pcbnew.TENTING_MODE_TENTED)
        v.SetBackTentingMode(pcbnew.TENTING_MODE_TENTED)
        board.Add(v)
        n += 1
    return n


def rule_areas(board, beschreibung):
    """Regelflaechen aus der Beschreibung (RULE_AREAS) auf die Platine.

    Eintraege: (name, lagen, (x0, y0, x1, y1), verbote) mit lagen als
    Tupel aus "F.Cu"/"B.Cu" und verbote als Menge aus "bahnen", "vias",
    "guss".

    Gebraucht fuer den Waermepfad des DRV8876 (Motormodul, Aufgabe 7):
    unter dem Treiber muss die Masseflaeche auf der Rueckseite
    DURCHGEHEND bleiben -- dort haengen die zwoelf Waermevias des
    Footprints. Eine Regelflaeche, die Bahnen und fremde Vias verbietet,
    den Guss aber erlaubt, sagt das dem Router (sie landet als keepout
    in der DSN); die Footprint-eigenen Waermevias sind Pads und bleiben
    von Regelflaechen unberuehrt.
    """
    lagen_map = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    n = 0
    for name, lagen, (x0, y0, x1, y1), verbote in getattr(
            beschreibung, "RULE_AREAS", ()):
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks("bahnen" in verbote)
        z.SetDoNotAllowVias("vias" in verbote)
        z.SetDoNotAllowZoneFills("guss" in verbote)
        # Pads und Footprints ausdruecklich erlauben: eine frische ZONE
        # verbietet sie sonst mit, und die Waermevias des DRV8876 sind
        # PTH-Pads seines eigenen Footprints -- die Flaeche, die sie
        # schuetzen soll, hat sie in der ersten Fassung selbst gemeldet
        # (12x "Items not allowed").
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET()
        for l in lagen:
            ls.addLayer(lagen_map[l])
        z.SetLayerSet(ls)
        z.SetOutline(_outline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))
        z.SetZoneName(name)
        board.Add(z)
        n += 1
    return n


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

    NAEHPUNKT-FILTER (Aufgabe 7c). `beschreibung._naht_erlaubt()` (falls
    vorhanden -- der 7,5-mm-Raster in _naehte()) und STITCH_EXTRA (die
    von Hand gesuchten Zusatzpunkte) pruefen beide nur Abstand zu
    Bauteil-Hoefen -- KEINER von beiden weiss, ob der Guss die Stelle
    ueberhaupt FUELLT. Der Fund, der diese Aufgabe ausgeloest hat: ein
    STITCH_EXTRA-Punkt des Motormoduls (18,10|32,10) sass 0,07 mm neben
    dem Pad R5-1 (Netz /IPROPI) -- der Kommentar dort behauptete
    ">= 0,50 mm zu jedem Pad", gemessen war es nicht. `board.
    BuildConnectivity()` "heilt" so ein Ueberlappen nicht als DRC-Fehler,
    sondern zieht das Via STILLSCHWEIGEND auf das fremde Netz -- aus dem
    GND-Naehvia wird ein IPROPI-Via, ohne jede Meldung, und die
    Massflaeche bleibt an der Stelle unvernaeht.
    Deshalb jetzt HIER, am gebauten Brett gemessen statt an der
    Beschreibung geschaetzt (dasselbe Prinzip wie masseheiler.py):
    ein Punkt kommt nur durch, wenn (1) beide Guss-Lagen ihn nach dem
    bisherigen Baustand (Bauteile + Regelflaechen + Vorverdrahtung,
    OHNE die Naehvias selbst) tatsaechlich fuellen UND (2) kein fremdes
    Netz in Via-Abstand liegt. Gilt fuer JEDEN Punkt aus STITCH_VIAS
    gleichermassen -- ob er aus dem festen Raster stammt oder von Hand
    gesucht wurde, s. Bericht Aufgabe 7c.
    """
    stellen = getattr(beschreibung, "STITCH_VIAS", ())
    code = board.GetNetcodeFromNetname("GND")
    if not stellen or code < 0:
        return 0
    zonen = gusslage.gnd_zonen(board, code)
    radius = mm(fertigung.VIA_PAD) // 2
    verworfen = []
    gesetzt = 0
    for x, y in stellen:
        px, py = mm(x), mm(y)
        if not gusslage.erreicht(zonen, px, py):
            verworfen.append((x, y, "Guss erreicht die Stelle nicht"))
            continue
        if not gusslage.frei(board, px, py, radius, code):
            verworfen.append((x, y, "fremdes Kupfer zu nah"))
            continue
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(px, py))
        v.SetWidth(mm(fertigung.VIA_PAD))
        v.SetDrill(mm(fertigung.VIA_DRILL))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(code)
        # Ausdruecklich abgedeckt (Loetstopplack ueber der Via), nicht
        # der Board-Vorgabe ueberlassen: die Verdreh-Kupferregel des
        # Vertrags verbietet freiliegendes Kupfer an den Landepunkten,
        # und eine Vorgabe, die jemand im Projekt umstellt, wuerde alle
        # Naehvias auf einmal freilegen. steckerprobe.verdrehtprobe()
        # verlangt an den kritischen Stellen genau diesen Modus.
        v.SetFrontTentingMode(pcbnew.TENTING_MODE_TENTED)
        v.SetBackTentingMode(pcbnew.TENTING_MODE_TENTED)
        board.Add(v)
        gesetzt += 1
    if verworfen:
        print("stitching_vias: %d von %d Naehpunkt(en) verworfen:"
              % (len(verworfen), len(stellen)))
        for x, y, grund in verworfen:
            print("    (%.2f|%.2f) -- %s" % (x, y, grund))
    return gesetzt


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


def _text_extent(board, text, hoehe, dicke):
    """Reale (Breite, Hoehe) eines Silkscreen-Texts in mm, per pcbnew
    gemessen statt geschaetzt.

    Die alte Fassung schaetzte die Breite grob (0,75 * Groesse * Zeichen);
    das reichte fuer die wenigen Faelle, die sie je pruefte (s.
    tidy_silkscreen-Historie). R6 verlangt jetzt eine Platzierung fuer
    JEDES Bauteil, viele davon in Luecken von nur 0,6-1,0 mm -- da muss
    die Schaetzung stimmen, nicht nur "reichen". pcbnew kennt die
    tatsaechliche Zeichensatzbreite (GetBoundingBox()); ein Wegwerf-Text,
    der nie board.Add()ed wird, liefert sie ohne Seiteneffekt.
    """
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetTextSize(pcbnew.VECTOR2I(mm(hoehe), mm(hoehe)))
    t.SetTextThickness(mm(dicke))
    bb = t.GetBoundingBox()
    return (bb.GetRight() - bb.GetLeft()) / 1e6, (bb.GetBottom() - bb.GetTop()) / 1e6


def _pad_rechtecke(board):
    """Alle Pad-Bounding-Boxen der Platine, in mm.

    Die Grundlage fuer "traegt seinen/fremden Pads nicht ueberlappen"
    (R6/R7/R8): ECHTE Kupferflaechen aus der gebauten Platine, nicht die
    Naeherung ueber PLACEMENT-Hoefe (die auch Silkscreen-Umrisse und
    Bauteilkoerper mitzaehlt, also strenger ist als noetig -- ein Pad
    ist typischerweise kleiner als sein Hof).
    """
    aus = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            aus.append((bb.GetLeft() / 1e6, bb.GetTop() / 1e6,
                        bb.GetRight() / 1e6, bb.GetBottom() / 1e6))
    return aus


_SILK_PAD_GAP = 0.15   # mm Mindestabstand Text<->Pad (uebliche
                       # Fertiger-Regel Silk-zu-Kupfer, s. Bericht).


def _schneidet(a, b, gap=0.0):
    return (a[0] - gap < b[2] and b[0] - gap < a[2]
            and a[1] - gap < b[3] and b[1] - gap < a[3])


def tidy_silkscreen(board, beschreibung):
    """Beschriftung aufraeumen -- UND (v2.1, Aufgabe C2, R6/Audit-Befund
    W1) jedem bestueckten Bauteil eine sichtbare, lesbare Referenz auf
    F.Silkscreen/B.Silkscreen verschaffen.

    BIS HIERHIN (v2/vorher): Referenzen von SMD-Teilen (p.tht == False)
    wanderten UNBEDINGT auf F.Fab, unabhaengig davon, ob daneben Platz
    gewesen waere -- "gedruckt waeren sie ohnehin oft verdeckt". Das
    Audit hat gemessen, was das auf den vier fertigen Boards bedeutet:
    auf drei von vieren trug KEIN EINZIGES Bauteil eine lesbare
    Referenz, auf dem vierten nur eines (W1). F.Fab wird nicht
    belichtet -- eine Referenz dort existiert auf der realen Platine
    nicht.

    JETZT: jede Referenz bleibt sichtbar auf der Silkscreen-Lage ihrer
    Seite. Gesucht wird eine freie Stelle in vier Richtungen (oben,
    unten, rechts, links vom EIGENEN PAD-Rechteck -- nicht vom
    PLACEMENT-Hof, s. "ROT-NACHWEIS R15" unten) und mit mehreren
    Textgroessen (absteigend von fertigung.SILK_TEXT) -- die erste
    Kombination, die weder ein fremdes Pad noch die Plattenkante trifft,
    gewinnt. Zwei Suchstufen:
      1. bevorzugt: auch ausserhalb jedes NACHBAR-Hofs (PLACEMENT-
         Rechtecke) -- vermeidet, dass der Text auf einem fremden
         Bauteilkoerper/dessen eigener Silkscreen-Zeichnung landet.
      2. Fallback, nur wenn Stufe 1 bei KEINER Groesse/Richtung passt:
         Hof-Ueberlappung erlaubt, PAD-Ueberlappung (eigene wie fremde)
         bleibt verboten -- das ist die einzige harte Regel aus R6
         ("nicht ueberlappend mit eigenen oder Nachbar-Pads"). Ohne
         Fallback bliebe sonst irgendeine dicht gepackte Nest-Reihe ohne
         Referenz, und das Projekt haette wieder eine stille Ausnahme.
      Bleibt auch Stufe 2 bei jeder Groesse erfolglos (in keinem der
      vier Boards beobachtet, s. Bericht), bricht das Bauen mit
      SystemExit ab -- lieber ein lauter Fehler als eine Referenz, die
      klammheimlich wieder auf F.Fab landet.

    Werte bleiben wie bisher auf F.Fab/unsichtbar (Bestueckungs-
    zeichnung, nicht Kennzeichnung); H-Bohrungen bleiben ohne Referenz
    (keine echten Bauteile).

    ROT-NACHWEIS R15 (Motormodul, erster Wurf dieser Aufgabe): der
    erste Anlauf verankerte jede Kandidatenbox am PLACEMENT-Hof (der
    Platz-Naeherung "linke obere Ecke plus Groesse"), nicht am
    tatsaechlichen Pad. In der neun Widerstaende dichten Gruppe
    (R5/R7/R8/R9/R10/R13/R15/R20/R21, COURTYARD_GAP=0,6 mm) frisst genau
    dieser Naeherungsfehler den einzigen freien Spalt auf: R15s realer
    Pad-Nordrand liegt bei y=34,91, der Hof-Nordrand aber bei y=34,66
    (0,25 mm hoehere Naeherung) -- auf einer Luecke von nur 1,16 mm
    zwischen R15s Pad und R5s Pad blieb dadurch keine Kombination aus
    Groesse/Richtung mehr uebrig (ALLE 40 Kombinationen aus beiden
    Stufen schlugen fehl, s. Bericht). Fix: die Kandidatenbox ankert
    jetzt am EIGENEN PAD-Rechteck (eigene_pads() unten, aus denselben
    echten Pads wie trifft_pad()) und spalt sinkt von 0,30 auf 0,20 mm
    (der harte Mindestabstand bleibt _SILK_PAD_GAP=0,15 mm, unveraendert
    -- 0,20 mm Standardabstand plus 0,15 mm Pruefung ergaben vorher
    0,45 mm Luft, die diese Engstelle nicht hat). Mit beiden Aenderungen
    findet R15 bei h=0,35 mm eine Stelle (N/S), 0,09 mm Reserve zur
    Nachbarpad-Kante -- knapp, aber gemessen, nicht geraten.
    """
    hoehen = (fertigung.SILK_TEXT, 0.65, 0.55, 0.45, 0.35)
    dicke = fertigung.SILK_DICKE

    # Hoefe (PLACEMENT-Rechtecke, "weicher" Nachbar-Ausschluss, Stufe 1)
    # und echte Pads (harter Ausschluss, beide Stufen) -- zwei getrennte
    # Quellen, s. Docstring.
    refs = list(beschreibung.PLACEMENT)
    hoefe = [(q.x, q.y, q.x + q.w, q.y + q.h)
             for q in beschreibung.PLACEMENT.values()]
    pads = _pad_rechtecke(board)
    e = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
    bw, bh = beschreibung.BOARD_W, beschreibung.BOARD_H

    # Eigenes Pad-Rechteck je Referenz (Vereinigung aller eigenen Pads) --
    # die Kandidatenbox ankert HIER, nicht am PLACEMENT-Hof (s. "ROT-
    # NACHWEIS R15" oben): der Hof ist eine Naeherung (Vertragswert,
    # nicht die reale Footprint-Geometrie) und in dicht gepackten
    # Gruppen oft grosszuegiger als das tatsaechliche Pad, was genau dort
    # den einzigen freien Millimeter kostet, wo er gebraucht wird.
    eigene_pads = {}
    for _fp in board.GetFootprints():
        _boxen = [pad.GetBoundingBox() for pad in _fp.Pads()]
        if not _boxen:
            continue
        eigene_pads[_fp.GetReference()] = (
            min(b.GetLeft() for b in _boxen) / 1e6,
            min(b.GetTop() for b in _boxen) / 1e6,
            max(b.GetRight() for b in _boxen) / 1e6,
            max(b.GetBottom() for b in _boxen) / 1e6)

    # Eigene Silkscreen-ZEICHNUNG je Referenz (Linien/Boegen/Polygone,
    # NICHT die Referenz/Wert-Texte selbst) -- s. "ROT-NACHWEIS C90"
    # unten: der Pad-Anker allein erkennt nicht, dass ein grosser/runder
    # Bauteilkoerper (Elko-Kreis, IC-Umriss) viel weiter reicht als seine
    # eigenen Pads. Diese Liste ist der direkte, geometrische Nachweis
    # dafuer -- dieselbe Fragestellung, die kicad-cli drc als
    # "silk_overlap" meldet, hier VOR dem Bauen statt hinterher.
    eigene_grafik = {}
    for _fp in board.GetFootprints():
        _gboxen = [it.GetBoundingBox() for it in _fp.GraphicalItems()
                  if it.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)]
        if _gboxen:
            eigene_grafik[_fp.GetReference()] = [
                (b.GetLeft() / 1e6, b.GetTop() / 1e6,
                 b.GetRight() / 1e6, b.GetBottom() / 1e6) for b in _gboxen]

    def trifft_eigene_grafik(box, ref):
        return any(_schneidet(box, g, _SILK_PAD_GAP)
                  for g in eigene_grafik.get(ref, ()))

    def kandidat(richtung, rect, breite, hoehe_txt, spalt=0.20):
        x0, y0, x1, y1 = rect
        mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        if richtung == "N":
            return (mx - breite / 2, y0 - spalt - hoehe_txt,
                    mx + breite / 2, y0 - spalt)
        if richtung == "S":
            return (mx - breite / 2, y1 + spalt,
                    mx + breite / 2, y1 + spalt + hoehe_txt)
        if richtung == "O":
            return (x1 + spalt, my - hoehe_txt / 2,
                    x1 + spalt + breite, my + hoehe_txt / 2)
        return (x0 - spalt - breite, my - hoehe_txt / 2,
                x0 - spalt, my + hoehe_txt / 2)

    def auf_platine(box):
        return (box[0] >= e and box[1] >= e
                and box[2] <= bw - e and box[3] <= bh - e)

    def trifft_pad(box):
        return any(_schneidet(box, q, _SILK_PAD_GAP) for q in pads)

    def trifft_hof(box, eigener):
        for k, h in enumerate(hoefe):
            if k == eigener:
                continue
            if _schneidet(box, h):
                return True
        return False

    n_klein = 0     # Referenzen, die nicht in voller SILK_TEXT-Groesse
                    # passten (zaehlmetrik fuers Log, kein Fehler)
    n_fallback = 0  # Referenzen, die Stufe 2 (Hof-Ueberlappung erlaubt)
                    # brauchten

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
        r.SetTextThickness(mm(dicke))

        if ref.startswith("H"):
            # Bohrungsmarke, kein Bauteil -- R6 gilt nur fuer bestueckte
            # (bzw. laut Aufgabenzettel: "wo ein Label hilft") Positionen.
            r.SetVisible(False)
            continue
        if p is None:
            # Sollte durch build.place()s eigene Vollstaendigkeitspruefung
            # nie vorkommen (jede Referenz aus der Netzliste braucht einen
            # PLACEMENT-Eintrag) -- fallback bleibt sichtbar am
            # Ursprungsort statt still zu verschwinden.
            r.SetLayer(silk)
            continue

        r.SetLayer(silk)
        eigener = refs.index(ref)
        # Zwei Anker, in dieser Reihenfolge versucht -- s. "ROT-NACHWEIS
        # C90" unten fuer den Grund, warum einer allein nicht reicht:
        #   1. das eigene PAD-Rechteck (eng, s. "ROT-NACHWEIS R15" unten)
        #   2. der PLACEMENT-Hof (weiter, aber IMMER ausserhalb des
        #      eigenen Koerpers -- wichtig fuer grosse/runde Bauteile,
        #      deren Pads nur einen Bruchteil der sichtbaren Flaeche
        #      einnehmen).
        rect_pad = eigene_pads.get(ref, (p.x, p.y, p.x + p.w, p.y + p.h))
        rect_hof = (p.x, p.y, p.x + p.w, p.y + p.h)
        anker_liste = (rect_pad, rect_hof) if rect_pad != rect_hof else (rect_pad,)
        # ROT-NACHWEIS C90 (Motormodul + alle drei Dimmer, zweiter Fund
        # dieser Aufgabe): mit NUR dem Pad-Anker (Fix fuer R15 oben)
        # landete C90s Referenz zwischen den beiden winzigen THT-Pads --
        # geometrisch pad-frei, aber mitten im gezeichneten RUNDEN
        # Elko-Koerper (8,5 x 8,5 mm Hof, die Pads nehmen davon nur einen
        # Bruchteil ein). kicad-cli pcb render zeigte gar keine "C90"
        # lesbar, nur den blauen Kondensator-Kreis; kicad-cli pcb drc
        # bestaetigte "Reference field of C90" ueberlappt "Segment of
        # C90" (den eigenen Polaritaets-Bogen). Der Hof-Anker (zweiter
        # Versuch) reichte ALLEIN nicht: er wird erst probiert, wenn der
        # (immer zuerst versuchte) Pad-Anker in Stufe 1 fehlschlaegt --
        # aber der Pad-Anker "schlaegt" per Definition nie an der EIGENEN
        # Grafik fehl (trifft_hof() nimmt den eigenen Index ausdruecklich
        # aus), er fand also klaglos eine (falsche) Stelle direkt neben
        # den Pads, noch bevor der Hof-Anker ueberhaupt drankam. Der
        # eigentliche Fix ist deshalb trifft_eigene_grafik() oben: eine
        # dritte, in STUFE 1 (nicht Stufe 2, s.u.) geprueft Schranke, die
        # direkt (wie kicad-cli drc) gegen die eigene Silkscreen-Zeichnung
        # (Linien/Boegen/Polygone, nicht nur Pads) misst. Mit ihr
        # scheitert der Pad-Anker fuer C90 tatsaechlich, der Hof-Anker
        # greift und findet die freie Stelle westlich des eigenen Hofs
        # (Luecke zu J105, 0,92 mm Reserve) -- ohne Stufe 2.
        #
        # WARUM NUR STUFE 1: als HARTE Regel in beiden Stufen scheiterte
        # U3 (SOT-353, Notaus-Kette) an JEDER Kombination -- ein derart
        # kleines Gehaeuse zeichnet seinen Koerperumriss so dicht an den
        # eigenen Pads, dass keine Richtung/Groesse/Anker beides zugleich
        # meidet. Genau dafuer ist Stufe 2 da: der allerletzte Ausweg,
        # bei dem ein bisschen eigene (oder fremde) Grafik ueberdeckt
        # sein darf, weil die Alternative ein Bauabbruch waere.
        #
        # ROT-NACHWEIS (Motormodul J96/C10/C14/C16, erster Wurf dieser
        # Aufgabe): eine Footprint-Referenz dreht sich MIT ihrem
        # Footprint (kein "keep upright" gesetzt) -- bei einem um 90 Grad
        # gedrehten Bauteil (alle Randpads J95/J96, mehrere gedrehte
        # 0805-Kondensatoren) tauschen Breite und Hoehe auf der Platine
        # ihre Rollen, aber _text_extent() misst IMMER ungedreht (der
        # Wegwerf-Text hat keine Rotation). Ungeprueft haelt der
        # Kandidat dann eine Luecke fuer die ungedrehte (schmale, hohe)
        # Form frei, waehrend real die gedrehte (breite, niedrige) Form
        # gedruckt wird -- kicad-cli drc (alle Stufen) meldete danach
        # "Reference field of J96 ... Silkscreen clipped by solder
        # mask": die echte, gedrehte Referenz ragte 0,29 mm in J96s
        # eigenes Pad 1 hinein, obwohl der (ungedreht gerechnete)
        # Kandidat 0,20 mm Abstand auswies. Fix: Breite/Hoehe VOR der
        # Kandidatensuche tauschen, wenn der Footprint um (ann.) 90 Grad
        # gedreht ist -- ab dann rechnet kandidat()/trifft_pad() mit der
        # tatsaechlich auf der Platine projizierten Form.
        gedreht90 = abs(fp.GetOrientationDegrees() % 180 - 90) < 1.0
        gefunden = None
        for stufe in (1, 2):
            for anker in anker_liste:
                for hoehe_txt in hoehen:
                    breite, txt_h = _text_extent(board, ref, hoehe_txt, dicke)
                    if gedreht90:
                        breite, txt_h = txt_h, breite
                    for richtung in ("N", "S", "O", "W"):
                        box = kandidat(richtung, anker, breite, txt_h)
                        if not auf_platine(box) or trifft_pad(box):
                            continue
                        if stufe == 1 and (trifft_hof(box, eigener)
                                          or trifft_eigene_grafik(box, ref)):
                            continue
                        gefunden = (box, hoehe_txt)
                        break
                    if gefunden:
                        break
                if gefunden:
                    break
            if gefunden:
                if stufe == 2:
                    n_fallback += 1
                break
        if gefunden is None:
            raise SystemExit(
                "%s: keine freie Silkscreen-Stelle fuer die Referenz "
                "gefunden (R6) -- Platzierung zu dicht, Naeheres in "
                "tidy_silkscreen()" % ref)

        box, hoehe_txt = gefunden
        if hoehe_txt < fertigung.SILK_TEXT - 1e-6:
            n_klein += 1
        r.SetTextSize(pcbnew.VECTOR2I(mm(hoehe_txt), mm(hoehe_txt)))
        cx, cy = (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0
        r.SetPosition(pcbnew.VECTOR2I(mm(cx), mm(cy)))

    return n_klein, n_fallback


def kennzeichnung(board, beschreibung):
    """Die Pflicht-Kennzeichnung aus stack_spec.LAYOUT_AUFLAGEN.

    Dreieck plus "1" neben Pin 1 des Stapelsteckers und "UNTEN" an
    der Klemmenkante (v2.1: vorher "KLEMMEN" -- umbenannt, Audit-Befund
    W4: der Text ist eine reine Verdreh-Orientierungsmarke, keine
    Klemmen-Beschriftung, und hiess trotzdem so, obwohl er auf keinem
    der vier Boards neben einer echten Klemme stand. Jede Klemme
    bekommt jetzt ihre eigene Funktionsbeschriftung, s.
    funktionsbeschriftung() unten). Grund fuer die Marke selbst steht
    im Vertrag: das M3-Lochbild ist punktsymmetrisch, ein um 180 Grad
    verdreht angeschraubtes Modul steckt nicht -- aber ohne
    Kennzeichnung sieht niemand, WARUM es nicht steckt. Bis 2026-09-01
    hat kein Werkzeug diese Auflage umgesetzt und keine Pruefung sie
    angemahnt; die erste Fassung der Sockelplatine wurde ohne
    committet.

    PIN1_MARKE und KLEMMEN_POS kommen aus der Platinenbeschreibung
    (die Platzverhaeltnisse sind je Platine verschieden) und sind
    PFLICHT -- fehlt eines, bricht das Bauen ab, statt still eine
    Platine ohne Kennzeichnung zu erzeugen.
    """
    for feld in ("PIN1_MARKE", "KLEMMEN_POS"):
        if getattr(beschreibung, feld, None) is None:
            raise SystemExit(
                "%s fehlt in der Platinenbeschreibung -- die "
                "Kennzeichnung ist Vertragsauflage (stack_spec."
                "LAYOUT_AUFLAGEN)" % feld)

    mx, my = beschreibung.PIN1_MARKE
    # Dreieck, Spitze nach rechts auf Pin 1 zeigend, ~1,2 mm hoch.
    ecken = [(mx - 0.6, my - 0.6), (mx - 0.6, my + 0.6), (mx + 0.6, my)]
    for a, b in zip(ecken, ecken[1:] + ecken[:1]):
        sh = pcbnew.PCB_SHAPE(board)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
        sh.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
        sh.SetLayer(pcbnew.F_SilkS)
        sh.SetWidth(mm(0.2))
        board.Add(sh)
        _UMRISSE.append(sh)

    for txt, (x, y) in (("1", (mx, my + 1.6)),
                        ("UNTEN", beschreibung.KLEMMEN_POS)):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(mm(fertigung.SILK_TEXT),
                                      mm(fertigung.SILK_TEXT)))
        t.SetTextThickness(mm(0.15))
        t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        board.Add(t)
        _UMRISSE.append(t)


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


def _silk_text_rechtecke(board):
    """Bounding-Boxen aller schon sichtbaren Silkscreen-Texte -- Referenz-
    Felder (von tidy_silkscreen() gesetzt) UND bereits vom Bauen
    hinzugefuegte PCB_TEXT-Objekte (Dreieck+1/UNTEN aus kennzeichnung(),
    fruehere _text_pruefen()-Aufrufe).

    ROT-NACHWEIS (Motormodul, dritter Fund dieser Aufgabe): "NOTAUS"
    (Koordinaten unabhaengig gegen J3s PADS gerechnet, s.
    spec_motor.FUNKTIONS_LABELS) landete deckungsgleich mit J3s EIGENER
    Referenz -- tidy_silkscreen() sucht J3s Platz unabhaengig von
    FUNKTIONS_LABELS und fand zufaellig dieselbe kleine Luecke. Der reine
    Pad-Rot-Nachweis sieht das nicht: keiner der beiden Texte liegt auf
    einem Pad. kicad-cli pcb render zeigte "J3" mitten durch "NOTAUS"
    hindurchgedruckt, kicad-cli pcb drc bestaetigte "Reference field of
    J3" ueberlappt "PCB text 'NOTAUS'". Deshalb jetzt ein zusaetzlicher
    Rot-Nachweis in _text_pruefen() gegen ALLE bereits sichtbaren Texte,
    nicht nur gegen Pads -- frisch bei jedem Aufruf gelesen, damit auch
    zwei FUNKTIONS_LABELS-Eintraege sich gegenseitig meiden.
    """
    aus = []
    for fp in board.GetFootprints():
        r = fp.Reference()
        if r.IsVisible():
            bb = r.GetBoundingBox()
            aus.append((bb.GetLeft() / 1e6, bb.GetTop() / 1e6,
                       bb.GetRight() / 1e6, bb.GetBottom() / 1e6))
    for d in board.GetDrawings():
        if (isinstance(d, pcbnew.PCB_TEXT)
                and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)):
            bb = d.GetBoundingBox()
            aus.append((bb.GetLeft() / 1e6, bb.GetTop() / 1e6,
                       bb.GetRight() / 1e6, bb.GetBottom() / 1e6))
    return aus


def _text_pruefen(board, beschreibung, pads, ref, text, x, y, hoehe, dicke,
                  halign="C", valign="C"):
    """Ein Silkscreen-Text an (x, y) -- mit einem Rot-Nachweis, dass er
    weder von der Platine faellt noch ein Pad oder einen anderen
    sichtbaren Silkscreen-Text trifft.

    Gemeinsame Grundlage fuer funktionsbeschriftung(), stecker_funktion(),
    randpad_labels() und board_identity() (R7/R8/R9): alle vier setzen
    Texte an fest ausgerechnete, in den spec_*.py-Dateien begruendete
    Koordinaten (anders als tidy_silkscreen()s Referenzen, die eine
    freie Stelle erst SUCHEN muessen) -- aber "fest ausgerechnet" ist
    keine Garantie, wenn sich eine Platzierung anderswo aendert. Deshalb
    hier derselbe Pad-Rot-Nachweis wie bei den Referenzen: liegt der
    Text auf einem Pad, ausserhalb der Platine oder ueber einem anderen
    Text, bricht das Bauen laut ab, statt eine kaputte Beschriftung
    stillschweigend zu drucken (s. _silk_text_rechtecke()-Docstring fuer
    den Fund, der den Text-Rot-Nachweis noetig machte).

    pads: vorab aus _pad_rechtecke(board) geholt (einmal je bauen()-Lauf
    reicht, alle Aufrufer teilen sich dieselbe Liste ueber ihren
    eigenen Parameter statt ueber ein Modul-Global).
    """
    breite, texthoehe = _text_extent(board, text, hoehe, dicke)
    hx = {"L": (x, x + breite), "C": (x - breite / 2, x + breite / 2),
         "R": (x - breite, x)}[halign]
    vy = {"T": (y, y + texthoehe), "C": (y - texthoehe / 2, y + texthoehe / 2),
         "B": (y - texthoehe, y)}[valign]
    box = (hx[0], vy[0], hx[1], vy[1])
    e = getattr(beschreibung, "EDGE_CLEARANCE", 0.5)
    bw, bh = beschreibung.BOARD_W, beschreibung.BOARD_H
    if not (box[0] >= e and box[1] >= e and box[2] <= bw - e
            and box[3] <= bh - e):
        raise SystemExit(
            "%s: Text %r bei (%.2f|%.2f) ragt ueber die Plattenkante "
            "hinaus (Box %s)" % (ref, text, x, y, box))
    for q in pads:
        if _schneidet(box, q, _SILK_PAD_GAP):
            raise SystemExit(
                "%s: Text %r bei (%.2f|%.2f) liegt auf einem Pad %s "
                "(R7/R8/R9 verlangen pad-frei)" % (ref, text, x, y, q))
    for q in _silk_text_rechtecke(board):
        if _schneidet(box, q, _SILK_PAD_GAP):
            raise SystemExit(
                "%s: Text %r bei (%.2f|%.2f) ueberlappt einen anderen "
                "Silkscreen-Text %s (R7/R8/R9 verlangen textfrei)"
                % (ref, text, x, y, q))

    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(hoehe), mm(hoehe)))
    t.SetTextThickness(mm(dicke))
    hj = {"L": pcbnew.GR_TEXT_H_ALIGN_LEFT, "C": pcbnew.GR_TEXT_H_ALIGN_CENTER,
         "R": pcbnew.GR_TEXT_H_ALIGN_RIGHT}[halign]
    vj = {"T": pcbnew.GR_TEXT_V_ALIGN_TOP, "C": pcbnew.GR_TEXT_V_ALIGN_CENTER,
         "B": pcbnew.GR_TEXT_V_ALIGN_BOTTOM}[valign]
    t.SetHorizJustify(hj)
    t.SetVertJustify(vj)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    board.Add(t)
    _UMRISSE.append(t)
    return box


def funktionsbeschriftung(board, beschreibung):
    """R7: Funktionsbeschriftung an jeder Klemme/jedem Stecker.

    Liest beschreibung.FUNKTIONS_LABELS -- eine Liste von
    (text, x, y[, halign, valign, groesse])-Eintraegen, in der jede
    spec_*.py-Datei ihre eigenen, gegen die eigene Platzierung
    ausgerechneten Koordinaten mitbringt (derselbe Stil wie PIN1_MARKE/
    KLEMMEN_POS: die Platzverhaeltnisse sind je Board verschieden, also
    gehoert die Zahl in die Beschreibung, nicht hierher). Fehlt das
    Attribut, passiert nichts -- Motor/Dimmer setzen es, aber die
    (bereits auf v1 eingefrorene) Sockelplatine muss es nicht.

    KETTE/LEISTUNG (die beiden Stapelstecker-Funktionslabels) sind KEIN
    Teil von FUNKTIONS_LABELS: ihre Position haengt nur an
    stack_spec.STECKER_POS (Vertrag, fuer alle Module gleich), nicht an
    einer modul-eigenen Platzierung -- s. board_identity()-Nachbar
    stecker_funktion() unten, das sie einmalig, generisch fuer jedes
    Modul erzeugt.
    """
    pads = _pad_rechtecke(board)
    n = 0
    for eintrag in getattr(beschreibung, "FUNKTIONS_LABELS", ()):
        text, x, y = eintrag[0], eintrag[1], eintrag[2]
        halign = eintrag[3] if len(eintrag) > 3 else "C"
        valign = eintrag[4] if len(eintrag) > 4 else "C"
        groesse = eintrag[5] if len(eintrag) > 5 else fertigung.SILK_TEXT
        _text_pruefen(board, beschreibung, pads, "FUNKTIONS_LABELS", text,
                     x, y, groesse, fertigung.SILK_DICKE, halign, valign)
        n += 1
    return n


def stecker_funktion(board, beschreibung):
    """R7 fuer Ketten-/Leistungsstecker: "KETTE"/"LEISTUNG", einmalig aus
    stack_spec.STECKER_POS abgeleitet -- gilt fuer JEDES Modul gleich,
    weil beide Stecker Vertragskoordinaten sind (STECKER_POS["kette"]/
    ["leistung"]), nicht modul-eigene Platzierung. Deshalb hier und
    nicht in FUNKTIONS_LABELS jeder einzelnen spec_*.py.

    Positionen: unter dem Nest bzw. unter dem Leistungsstecker, in
    Luecken, die auf allen vier Boards frei sind (nachgemessen gegen
    die tatsaechliche PLACEMENT jedes Boards, s. Bericht):
      KETTE   -- Mitte von STECKER_POS["kette"]["flaeche"] in x,
                 y=9,80 (Luecke J101/J102-Hof-Unterkante 7,17 bis
                 U100-Hof-Oberkante 12,80 -- 5,63 mm frei, auf allen
                 vier Boards identisch, weil das MCU-Nest woertlich
                 uebernommen ist).
      LEISTUNG-- Mitte von STECKER_POS["leistung"]["flaeche"] in x,
                 y=52,50 (Luecke Leistungsstecker-Unterkante 49,82 bis
                 KLEMMENZONE-Oberkante 60,80 -- 10,98 mm frei, auf allen
                 vier Boards frei: die Kanalzonen der Dimmer bleiben
                 x < 20 bzw. enden mit D4/Q4 bei y <= 42,0, s.
                 spec_dimmer_basis._KANAL_TASCHEN).
    """
    if not getattr(beschreibung, "IST_MODUL", False):
        return 0
    pads = _pad_rechtecke(board)
    kette = S.STECKER_POS["kette"]["flaeche"]
    leistung = S.STECKER_POS["leistung"]["flaeche"]
    kx = (kette[0] + kette[2]) / 2.0
    lx = (leistung[0] + leistung[2]) / 2.0
    _text_pruefen(board, beschreibung, pads, "STECKER_FUNKTION", "KETTE",
                 kx, 9.80, fertigung.SILK_TEXT, fertigung.SILK_DICKE)
    _text_pruefen(board, beschreibung, pads, "STECKER_FUNKTION", "LEISTUNG",
                 lx, 52.50, fertigung.SILK_TEXT, fertigung.SILK_DICKE)
    return 2


def randpad_labels(board, beschreibung):
    """R8: jedes der 22 Randpads traegt sein GP-/Netzlabel im Siebdruck.

    Direkt aus stack_spec.RANDPADS (die Pin->Label-Zuordnung, die der
    Vertrag ohnehin schon fuehrt, s. Audit-Befund W3: "keine neue
    Entscheidung noetig, nur Umsetzung der bereits gemachten Zusage") --
    NICHT aus der jeweiligen spec_*.py, weil die Positionen selbst schon
    Vertragskoordinaten sind (RAND_X/RAND_Y0/RAND_RASTER), fuer alle vier
    Boards identisch.

    LAGE: rechts NEBEN jedem Pad (x = Pad-Ostkante + 0,20 mm), nicht
    darueber/darunter -- die Randpad-Reihe steht im 2,54-mm-Raster,
    aber jedes einzelne Pad ist nur 0,90 mm (nach der v2.1-Drehung: in
    y) hoch, waehrend ein Label seitlich in x reichlich Platz hat (die
    Zone endet erst bei BOARD_W, 2,4 mm rechts vom Pad). Textgroesse
    0,5 mm (kleiner als SILK_TEXT=0,8): bei 0,8 mm ist selbst "GP10"
    (3,32 mm breit, real gemessen) breiter als die 2,4 mm Reserve
    zwischen Padkante (78,90) und der um EDGE_CLEARANCE geschrumpften
    Plattenkante (81,50) -- bei 0,5 mm sind es 2,15 mm, das passt (s.
    Bericht fuer die volle Messreihe). Nur fuer diese 22 Labels kleiner
    als sonst im Projekt ueblich: das 2,54-mm-Raster laesst nichts
    anderes zu, ohne die Kupferregel (R8-Layer = RAND_LABEL_LAYER,
    dieselbe Seite wie das Kupfer) zu verlassen.
    """
    if not getattr(beschreibung, "PLACEMENT", None) or (
            "J95" not in beschreibung.PLACEMENT
            and "J96" not in beschreibung.PLACEMENT):
        return 0
    pads = _pad_rechtecke(board)
    groesse = 0.5
    dicke = 0.10
    x = S.RAND_X + S.RAND_PAD_B * (2.6 / 0.9) / 2.0 + 0.20
    # Padbreite nach der v2.1-Drehung ist nicht RAND_PAD_B selbst
    # (0,90 mm, die NATIVE, ungedrehte Padbreite aus dem Vertrag),
    # sondern die um 90 Grad gedrehte GESAMTBREITE der Randpad-Footprints
    # (2,60 mm, s. spec_motor.PLACEMENT["J95"]-Kommentar, "natives
    # F.CrtYd ... Breite 2,60 mm") -- deshalb der Skalierungsfaktor
    # 2,6/0,9 auf RAND_PAD_B statt einer zweiten, hartkodierten Zahl.
    for pin, label, (px, py) in S.RANDPADS:
        _text_pruefen(board, beschreibung, pads, "J95/J96 Pin %d" % pin,
                     label, x, py, groesse, dicke, halign="L", valign="C")
    return len(S.RANDPADS)


def board_identity(board, beschreibung):
    """R9: Modulname, Vertragsversion und Modultyp lesbar im Siebdruck.

    Verlangt beschreibung.MODULNAME und .MODULTYP (Pflichtfelder wie
    PIN1_MARKE/KLEMMEN_POS in kennzeichnung() -- fehlt eines, bricht das
    Bauen ab, statt eine Platine ohne Identitaet zu erzeugen, genau die
    Luecke, die Audit-Befund W7 gefunden hat: "alle vier Boards trugen
    identischen, unetikettierten Text").

    LAGE: (2,0 | BOARD_H-2,0), linksbuendig, OBENBUENDIG (valign="T") --
    dieselbe Stelle, die mark_version() seit jeher fuer einen
    Versionsvermerk vorsieht (hier aber unbedingt aufgerufen, nicht nur
    wenn ein Aufrufer einen versionstext uebergibt -- das tat bisher NIE
    jemand, s. build.py __main__, deshalb war W7 ueberhaupt offen). Die
    Zeile x=2,0..~23 ist auf allen vier Boards frei (naechste Bebauung
    ist KLEMMENZONE ab x=23,80 bzw. Dimmer1s J5 bei x=37,00) UND liegt
    nicht unter einem Stecker (Auftrag: "nicht unter einem Anschluss").

    ROT-NACHWEIS (erster Wurf dieser Aufgabe, valign="C"): bei y=BOARD_H
    -2,0=71,0 und Standard-Vertikalzentrierung reicht der Text nach OBEN
    bis y=70,5 -- mitten in das Pad der linken unteren Bohrung H2 (x=4,
    Pad-Box 67,40..70,60, auf allen vier Boards identisch, Vertrags-
    lochbild). valign="T" laesst den Text stattdessen NACH UNTEN von
    y=71,0 wachsen -- H2s Pad-Unterkante (70,60) bleibt klar oberhalb der
    Textbox.

    ZWEITER ROT-NACHWEIS (Texthoehe): bei nominell 1,0 mm misst
    _text_extent() die REALE Boundingbox mit 1,70 mm Hoehe (Ober-/
    Unterlaengen von "P"/"0" etc., pcbnew rechnet grober als das
    nominelle Textmass) -- von y=71,0 abwaerts reicht das bis 72,70,
    ueber BOARD_H-EDGE_CLEARANCE (72,5) hinaus. Texthoehe deshalb
    fertigung.SILK_TEXT (0,8 mm, das im ganzen Projekt uebliche
    Silkscreen-Mass) statt der zunaechst versuchten 1,0 mm -- reale Hoehe
    dann 1,36 mm, endet bei 72,36, 0,14 mm Reserve.
    """
    for feld in ("MODULNAME", "MODULTYP"):
        if getattr(beschreibung, feld, None) is None:
            raise SystemExit(
                "%s fehlt in der Platinenbeschreibung -- die "
                "Board-Identitaet ist Vertragsauflage (R9)" % feld)
    pads = _pad_rechtecke(board)
    text = "%s %s v%s 0x%02X" % (S.PROJEKTNAME, beschreibung.MODULNAME,
                                 S.VERTRAG_VERSION, beschreibung.MODULTYP)
    _text_pruefen(board, beschreibung, pads, "BOARD_IDENTITY", text, 2.0,
                 beschreibung.BOARD_H - 2.0, fertigung.SILK_TEXT,
                 fertigung.SILK_DICKE, halign="L", valign="T")
    return text


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
    feinraster_pads(board)
    n, np_, ohne, n_bekannt = assign_nets(board, nets, ohne_pad)
    # Erst Netze zuweisen, dann die Pads im Ueberhang entfernen: sonst
    # meldet die Zuweisung sie als fehlend und die Netzliste sieht
    # unvollstaendig aus, obwohl nur Loecher neben der Platine wegfallen.
    weg, weg_mit_netz = drop_offboard_pads(board, beschreibung)
    n_klein, n_fallback = tidy_silkscreen(board, beschreibung)
    kennzeichnung(board, beschreibung)
    # v2.1 (Aufgabe C2, R7-R9): Funktionsbeschriftung, Randpad-Labels und
    # Board-Identitaet -- alle drei lesen feste, in der jeweiligen
    # spec_*.py/stack_spec.py begruendete Koordinaten (anders als
    # tidy_silkscreen()s Referenzen) und pruefen sich selbst gegen die
    # ECHTEN Pads dieses Baus (_text_pruefen, s. dort). Reihenfolge nach
    # kennzeichnung(), damit "UNTEN" zuerst steht und diese vier
    # zusaetzlichen Texte im selben Silkscreen-Bild wie die uebrige
    # Kennzeichnung entstehen; untereinander ist die Reihenfolge egal,
    # keine der vier haengt von einer anderen ab.
    n_funktion = funktionsbeschriftung(board, beschreibung)
    n_stecker_funktion = stecker_funktion(board, beschreibung)
    n_randpads = randpad_labels(board, beschreibung)
    board_identity(board, beschreibung)
    if versionstext:
        mark_version(board, versionstext, beschreibung, hinweise)
    if getattr(beschreibung, "ANTENNA_SLOT", None) is not None:
        antenna_slot(board, beschreibung)
        antenna_slot_keepout(board, beschreibung)
    n_regel = rule_areas(board, beschreibung)
    n_vor = pre_tracks(board, beschreibung)
    n_vorvia = pre_vias(board, beschreibung)
    if n_vorvia:
        print("%d Vorverdrahtungs-Vias gesetzt" % n_vorvia)
    # Zonen JETZT anlegen und einmal fuellen -- VOR den Naehvias, nicht
    # danach. Der Naehpunkt-Filter in stitching_vias() muss gegen den
    # tatsaechlich gefuellten Guss pruefen koennen (Aufgabe 7c); ohne
    # diesen Vorablauf gaebe es beim Filtern noch gar keine Zone.
    add_zones(board, beschreibung)
    board.BuildListOfNets()
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))
    n_stich = stitching_vias(board, beschreibung)
    problems += np_
    # Zweiter Fuelllauf: bezieht die (gefilterten) Naehvias mit ein.
    board.BuildListOfNets()
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))
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
    print("Beschriftung: alle Referenzen sichtbar auf Silkscreen "
          "(%d verkleinert, %d mit Hof-Ueberlappung), Werte ausgeblendet"
          % (n_klein, n_fallback))
    if n_funktion or n_stecker_funktion:
        print("%d Funktionslabel + %d Stapelstecker-Label gesetzt (R7)"
              % (n_funktion, n_stecker_funktion))
    if n_randpads:
        print("%d Randpad-Labels gesetzt (R8)" % n_randpads)
    if n_stich:
        print("%d GND-Vias zum Vernaehen der Masseflaechen gesetzt" % n_stich)
    if n_vor:
        print("%d Segmente Vorverdrahtung gelegt" % n_vor)
    if n_regel:
        print("%d Regelflaechen angelegt" % n_regel)
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

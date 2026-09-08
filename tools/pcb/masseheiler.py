"""Heilt zerschnittene Masseflaechen: Vias fuer isolierte GND-Cluster.

WARUM ES DIESES WERKZEUG GIBT (2026-09-02, Aufgabe 7). Auf dem
Motormodul zerschneiden ~450 Bahnen den Masseguss der Oberseite in ein
Dutzend Stuecke. Feste Naehvia-Listen in der Beschreibung (STITCH_VIAS/
STITCH_EXTRA) koennen das nicht abschliessend loesen: freerouting ist
auch mit einem Thread nicht deterministisch, jeder Lauf schneidet den
Guss ANDERS, und ein Via, das fuer den einen Schnitt passt, sitzt beim
naechsten im falschen Stueck. Sechs Wuerfellaeufe schwankten zwischen
3 und 12 offenen Masse-Kanten.

Dieses Werkzeug arbeitet deshalb NACH dem Verlegen am fertigen Board:

1. Union-Find ueber alle GND-Kupferteile: Zonen-Fuellstuecke beider
   Lagen, Vias, Pads (THT verbindet beide Lagen), Bahnsegmente
   (verbunden ueber gemeinsame Endpunkte und die Stuecke, in denen
   ihre Endpunkte liegen).
2. Jeder Cluster ohne Verbindung zum Hauptcluster (dem groessten)
   bekommt ein Via an einer Stelle, an der BEIDE Lagen im jeweils
   richtigen Stueck liegen und die frei von fremdem Kupfer ist
   (Pads, Bahnen, Vias, Regelflaechen, M3, Rand -- am Board gemessen,
   nicht an der Beschreibung geschaetzt).
3. Zonen neu fuellen, von vorn -- bis kein isolierter Cluster mehr da
   ist oder sich nichts mehr heilen laesst (dann Fehler, ROT).

Aufruf:  kipy masseheiler.py <board.kicad_pcb> [--nur-pruefen]
Mit --nur-pruefen wird nichts geschrieben, nur der Zustand gemeldet
(Rueckgabe 1 bei isolierten Clustern) -- das ist der Wachhund fuer die
Kette; ohne die Option wird geheilt und gespeichert.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pcbnew
import fertigung

mm = lambda v: int(round(v * 1e6))

FREI = 0.2          # Abstand zu fremdem Kupfer (Netzklassen-Clearance)
VIA_R = None        # gesetzt in main aus fertigung


def _gnd_zonen(board, gnd):
    zonen = {}
    for z in board.Zones():
        if z.GetNetCode() != gnd or z.GetIsRuleArea():
            continue
        for lage in (pcbnew.F_Cu, pcbnew.B_Cu):
            if z.IsOnLayer(lage):
                zonen[lage] = z.GetFilledPolysList(lage)
    return zonen


def _stueck(zonen, lage, x, y):
    polys = zonen.get(lage)
    if polys is None:
        return None
    for i in range(polys.OutlineCount()):
        if polys.Contains(pcbnew.VECTOR2I(int(x), int(y)), i):
            return i
    return None


def cluster(board):
    """(zonen, eltern, wurzel, find): Union-Find der GND-Kupferteile."""
    gnd = board.GetNetcodeFromNetname("GND")
    zonen = _gnd_zonen(board, gnd)
    eltern = {}

    def find(a):
        while eltern.setdefault(a, a) != a:
            a = eltern[a]
        return a

    def union(a, b):
        eltern[find(a)] = find(b)

    punkte = {}          # Position -> Knoten (Vias/Pads fuer Bahn-Enden)
    for t in board.Tracks():
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gnd:
            pos = (t.GetPosition().x, t.GetPosition().y)
            k = ("via",) + pos
            punkte[pos] = k
            for lage in (pcbnew.F_Cu, pcbnew.B_Cu):
                s = _stueck(zonen, lage, *pos)
                if s is not None:
                    union(k, (lage, s))
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() != gnd:
                continue
            pos = (p.GetPosition().x, p.GetPosition().y)
            k = ("pad", f.GetReference(), p.GetNumber())
            punkte[pos] = k
            lagen = ((pcbnew.F_Cu, pcbnew.B_Cu)
                     if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
                     else ((pcbnew.F_Cu,) if p.IsOnLayer(pcbnew.F_Cu)
                           else (pcbnew.B_Cu,)))
            for lage in lagen:
                s = _stueck(zonen, lage, *pos)
                if s is not None:
                    union(k, (lage, s))
    for t in board.Tracks():
        if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetCode() == gnd:
            lage = t.GetLayer()
            a = (t.GetStart().x, t.GetStart().y)
            b = (t.GetEnd().x, t.GetEnd().y)
            ka = punkte.get(a, ("pt", lage) + a)
            kb = punkte.get(b, ("pt", lage) + b)
            union(ka, kb)
            # Die GANZE Bahn abtasten, nicht nur die Enden: eine Bahn,
            # die durch ein Zonenstueck LAEUFT, verbindet es (die Zone
            # fuellt an gleiches Netz heran). Die Endpunkt-Fassung
            # meldete Stuecke als isoliert, deren Pads laut KiCad-DRC
            # laengst verbunden waren.
            laenge = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
            schritte = max(1, int(laenge / mm(0.5)))
            for n in range(schritte + 1):
                x = a[0] + (b[0] - a[0]) * n // schritte
                y = a[1] + (b[1] - a[1]) * n // schritte
                s = _stueck(zonen, lage, x, y)
                if s is not None:
                    union(ka, (lage, s))

    # Hauptcluster: das flaechengroesste Stueck (B.Cu ist praktisch
    # immer die durchgehende Ebene).
    groesste = None
    for lage, polys in zonen.items():
        for i in range(polys.OutlineCount()):
            bb = polys.Outline(i).BBox()
            a = bb.GetWidth() * bb.GetHeight()
            if groesste is None or a > groesste[0]:
                groesste = (a, (lage, i))
    return zonen, eltern, find(groesste[1]), find


def isolierte(board):
    """(zonen, offen, wurzel, find) -- offen: [(lage, index, bbox)]."""
    zonen, eltern, wurzel, find = cluster(board)
    aus = []
    for lage, polys in zonen.items():
        for i in range(polys.OutlineCount()):
            if find((lage, i)) != wurzel:
                aus.append((lage, i, polys.Outline(i).BBox()))
    return zonen, aus, wurzel, find


def _frei(board, x, y, radius=None):
    """Darf hier GND-Kupfer mit diesem Radius hin? Am Board gemessen."""
    gnd = board.GetNetcodeFromNetname("GND")
    pos = pcbnew.VECTOR2I(int(x), int(y))
    kante = (VIA_R if radius is None else radius) + mm(FREI)
    bb = board.GetBoardEdgesBoundingBox()
    if not (bb.GetLeft() + mm(0.8) < x < bb.GetRight() - mm(0.8)
            and bb.GetTop() + mm(0.8) < y < bb.GetBottom() - mm(0.8)):
        return False
    for f in board.GetFootprints():
        for p in f.Pads():
            d = p.GetBoundingBox()
            d.Inflate(kante)
            if d.Contains(pos) and p.GetNetCode() != gnd:
                return False
            if (p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD
                    and d.Contains(pos)):
                return False        # Loecher auch bei gleichem Netz meiden
    for t in board.Tracks():
        if t.GetNetCode() == gnd:
            if t.Type() == pcbnew.PCB_VIA_T:
                d = t.GetBoundingBox()
                d.Inflate(mm(0.2))
                if d.Contains(pos):
                    return False    # nicht auf ein vorhandenes Via
            continue
        d = t.GetBoundingBox()
        d.Inflate(kante)
        if d.Contains(pos) and t.HitTest(pos, kante):
            return False
    for z in board.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias():
            d = z.GetBoundingBox()
            d.Inflate(kante)
            if d.Contains(pos):
                return False
    return True


def _bruecke_suchen(board, zonen, offen, wurzel, find):
    """((x1,y1),(x2,y2),lage) fuer eine freie GND-Bahn Splitter->Haupt.

    Von Rasterpunkten im Splitter aus in acht Richtungen (0/45/90) bis
    3 mm laufen; erreicht der Strahl einen Punkt im Haupt-Stueck
    derselben Lage und ist der ganze Korridor frei von fremdem Kupfer,
    ist das die Bruecke.
    """
    halb = mm(fertigung.TRACK_SIGNAL) // 2
    for lage, i, bb in offen:
        polys = zonen[lage]
        schritt = mm(0.25)
        y = bb.GetTop() + schritt
        while y < bb.GetBottom():
            x = bb.GetLeft() + schritt
            while x < bb.GetRight():
                if (polys.Contains(pcbnew.VECTOR2I(int(x), int(y)), i)
                        and _frei(board, x, y, halb)):
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                                   (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        n = 1
                        while n * 0.25 <= 3.0:
                            px = x + dx * n * schritt
                            py = y + dy * n * schritt
                            if not _frei(board, px, py, halb):
                                break
                            s2 = _stueck(zonen, lage, px, py)
                            if (s2 is not None
                                    and find((lage, s2)) == wurzel):
                                return (x, y), (px, py), lage
                            n += 1
                x += schritt
            y += schritt
    return None


def heilen(board_pfad, nur_pruefen=False):
    global VIA_R
    VIA_R = mm(fertigung.VIA_PAD) // 2
    board = pcbnew.LoadBoard(board_pfad)
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))

    runde, gesetzt, letzte_anzahl = 0, [], None
    while True:
        runde += 1
        zonen, offen, wurzel, find = isolierte(board)
        if not offen:
            break
        if nur_pruefen:
            for lage, i, bb in offen:
                print("ISOLIERT: %s-Stueck %d  x %.1f..%.1f y %.1f..%.1f"
                      % (board.GetLayerName(lage), i,
                         bb.GetLeft() / 1e6, bb.GetRight() / 1e6,
                         bb.GetTop() / 1e6, bb.GetBottom() / 1e6))
            return 1
        # Konvergenz-Wache: jede Runde muss die Zahl der CLUSTER
        # senken (nicht der Stuecke -- die kann beim Fuellen
        # schwanken). Die erste Fassung verband Inseln mit dem
        # eigenen Cluster und kettete nur, ohne zu heilen.
        anzahl_cluster = len({find((l, i)) for l, p in zonen.items()
                              for i in range(p.OutlineCount())})
        if letzte_anzahl is not None and anzahl_cluster >= letzte_anzahl:
            raise SystemExit(
                "masseheiler: Runde %d senkt die Clusterzahl nicht "
                "(%d) -- Layout pruefen" % (runde, anzahl_cluster))
        letzte_anzahl = anzahl_cluster

        # Zweistufige Suche: am liebsten ein Punkt, unter dem die
        # andere Lage schon zum Hauptcluster gehoert; sonst irgendein
        # FREMDER Cluster (Insel an Insel -- der Verbund waechst, bis
        # er irgendwo ueber Hauptkupfer liegt; die Clusterzahl sinkt
        # in jedem Fall um eins).
        ziel = None
        for nur_haupt in (True, False):
            for lage, i, bb in offen:
                andere = (pcbnew.B_Cu if lage == pcbnew.F_Cu
                          else pcbnew.F_Cu)
                polys = zonen[lage]
                eigen = find((lage, i))
                schritt = mm(0.25)
                y = bb.GetTop() + schritt
                while y < bb.GetBottom() and ziel is None:
                    x = bb.GetLeft() + schritt
                    while x < bb.GetRight():
                        s2 = _stueck(zonen, andere, x, y)
                        if s2 is not None:
                            dort = find((andere, s2))
                            passt = (dort == wurzel if nur_haupt
                                     else dort != eigen)
                            if (passt and polys.Contains(
                                    pcbnew.VECTOR2I(int(x), int(y)), i)
                                    and _frei(board, x, y)):
                                ziel = (x, y)
                                break
                        x += schritt
                    y += schritt
                if ziel is not None:
                    break
            if ziel is not None:
                break
        if ziel is None:
            # Bruecken-Stufe: eine kurze GND-Bahn vom Splitter zum
            # Haupt-Guss DERSELBEN Lage. Noetig, wenn unter einem
            # Splitter kein Haupt-Kupfer der anderen Lage liegt (das
            # Nest zersplittert beide Lagen uebereinander) -- Stueck 7
            # des Motormoduls hatte 505 Kandidaten und keinen einzigen
            # freien Via-Punkt.
            # Via-in-Pad-Stufe: die Zone fuellt NICHT ueber den
            # SMD-Pads -- ein Splitter, der nur aus dem Kupferkragen
            # um ein Massepad besteht (R5 auf dem Motormodul), bietet
            # der Punktsuche keinen einzigen Kandidaten. Ein Via im
            # Pad-Zentrum ist bei Handloetung unbedenklich und
            # verbindet das Pad direkt mit der Rueckseite.
            gnd = board.GetNetcodeFromNetname("GND")
            _z2, _e2, _w2, _f2 = cluster(board)
            ziel_pad = None
            for f in board.GetFootprints():
                for pd in f.Pads():
                    if (pd.GetNetCode() != gnd
                            or pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD):
                        continue
                    k = ("pad", f.GetReference(), pd.GetNumber())
                    if _f2(k) == _w2:
                        continue
                    lage = (pcbnew.F_Cu if pd.IsOnLayer(pcbnew.F_Cu)
                            else pcbnew.B_Cu)
                    andere = (pcbnew.B_Cu if lage == pcbnew.F_Cu
                              else pcbnew.F_Cu)
                    # Die ganze Pad-Flaeche abrastern, so dass das Via
                    # vollstaendig im Pad-Kupfer bleibt: unter dem
                    # ZENTRUM von R5-2 lag gar kein Rueckseiten-Kupfer
                    # (Bahnbuendel-Freistellung), knapp daneben schon.
                    pb = pd.GetBoundingBox()
                    pb.Inflate(-VIA_R)
                    y = pb.GetTop()
                    while y <= pb.GetBottom() and ziel_pad is None:
                        x = pb.GetLeft()
                        while x <= pb.GetRight():
                            s2 = _stueck(zonen, andere, x, y)
                            if (s2 is not None
                                    and find((andere, s2)) != _f2(k)
                                    and _frei(board, x, y)):
                                ziel_pad = (int(x), int(y))
                                break
                            x += mm(0.1)
                        y += mm(0.1)
                    if ziel_pad:
                        break
                if ziel_pad:
                    break
            if ziel_pad is not None:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I(*ziel_pad))
                v.SetWidth(mm(fertigung.VIA_PAD))
                v.SetDrill(mm(fertigung.VIA_DRILL))
                v.SetNetCode(gnd)
                v.SetFrontTentingMode(pcbnew.TENTING_MODE_TENTED)
                v.SetBackTentingMode(pcbnew.TENTING_MODE_TENTED)
                board.Add(v)
                gesetzt.append((ziel_pad[0], ziel_pad[1]))
                board.BuildConnectivity()
                pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))
                continue
            bruecke = _bruecke_suchen(board, zonen, offen, wurzel, find)
            if bruecke is not None:
                (x1, y1), (x2, y2), lage = bruecke
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(int(x1), int(y1)))
                t.SetEnd(pcbnew.VECTOR2I(int(x2), int(y2)))
                t.SetWidth(mm(fertigung.TRACK_SIGNAL))
                t.SetLayer(lage)
                t.SetNetCode(board.GetNetcodeFromNetname("GND"))
                board.Add(t)
                gesetzt.append(("bruecke", (x1, y1, x2, y2)))
                board.BuildConnectivity()
                pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))
                continue
            # Sackgasse. Cluster MIT Massepads sind ein Layoutfehler
            # (das Pad hinge in der Luft). Cluster OHNE Pads sind
            # toter Zierrat, den nur seine eigenen Naehvias am Leben
            # halten: Vias raus, und die Inselentfernung des Fuellers
            # raeumt die Splitter ab.
            _z, _eltern, _w, _find = cluster(board)
            pad_cluster = {_find(k) for k in list(_eltern)
                           if k and k[0] == "pad"}
            geloescht = 0
            # Sackgasse an einem Stueck MIT Massepads: das ist ein
            # Layoutfehler und bleibt ROT (Rueckgabe 1).
            #
            # Die erste Fassung warf hier SystemExit -- und damit ALLES
            # weg, was in den Runden davor schon geheilt war (die
            # Platine wird erst am Ende gespeichert). Auf dem Motormodul
            # kostete das in fast jedem Wuerfellauf ein Dutzend
            # Masse-Kanten, die dieses Werkzeug hatte heilen KOENNEN:
            # ein einziges nicht heilbares Stueck liess auch die
            # heilbaren ungeheilt, und die DRC meldete hinterher beides
            # gemeinsam als "missing connection". Ein Lauf mit einer
            # restlos verlegten Platine (0 offene Verbindungen im
            # Router) kam so trotzdem mit 11 offenen DRC-Posten heraus.
            #
            # Jetzt wird das Geheilte gespeichert und ALLE verbliebenen
            # Stuecke gemeldet, nicht nur das erste. Rot bleibt rot --
            # aber die Meldung nennt jetzt den ganzen Befund, und die
            # DRC danach zeigt nur noch die echten Layoutfehler.
            steckengeblieben = [(lage, i, bb) for lage, i, bb in offen
                                if _find((lage, i)) in pad_cluster]
            if steckengeblieben:
                if gesetzt:
                    board.Save(board_pfad)
                    print("masseheiler: %d Heilung(en) gespeichert, bevor "
                          "die Sackgasse kam" % len(gesetzt))
                for lage, i, bb in steckengeblieben:
                    print("  ! masseheiler: %s-Stueck %d (x %.1f..%.1f y "
                          "%.1f..%.1f) traegt Massepads, hat aber keinen "
                          "freien Heilpunkt -- Layout pruefen"
                          % (board.GetLayerName(lage), i,
                             bb.GetLeft() / 1e6, bb.GetRight() / 1e6,
                             bb.GetTop() / 1e6, bb.GetBottom() / 1e6))
                return 1
            for t in list(board.Tracks()):
                if (t.Type() == pcbnew.PCB_VIA_T
                        and t.GetNetCode()
                        == board.GetNetcodeFromNetname("GND")):
                    k = ("via", t.GetPosition().x, t.GetPosition().y)
                    if k in _eltern and _find(k) != _w:
                        board.Remove(t)
                        geloescht += 1
            if not geloescht:
                raise SystemExit(
                    "masseheiler: Sackgasse ohne loeschbare Vias -- "
                    "Layout pruefen")
            print("masseheiler: %d nutzlose Splitter-Vias entfernt"
                  % geloescht)
            board.BuildConnectivity()
            pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))
            gesetzt.append(("geloescht", geloescht))
            continue
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(int(ziel[0]), int(ziel[1])))
        v.SetWidth(mm(fertigung.VIA_PAD))
        v.SetDrill(mm(fertigung.VIA_DRILL))
        v.SetNetCode(board.GetNetcodeFromNetname("GND"))
        v.SetFrontTentingMode(pcbnew.TENTING_MODE_TENTED)
        v.SetBackTentingMode(pcbnew.TENTING_MODE_TENTED)
        board.Add(v)
        gesetzt.append((ziel[0], ziel[1]))
        board.BuildConnectivity()
        pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))

    if gesetzt:
        board.Save(board_pfad)
        print("masseheiler: fertig -- %s"
              % ", ".join(
                  ("%d Vias geloescht" % n) if a == "geloescht"
                  else ("Bruecke %s" % (n,)) if a == "bruecke"
                  else "(%.2f|%.2f)" % (a / 1e6, n / 1e6)
                  for a, n in gesetzt))
    else:
        print("masseheiler: alle Masseflaechen haengen zusammen, "
              "nichts zu tun")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        raise SystemExit(
            "Aufruf: masseheiler.py <board.kicad_pcb> [--nur-pruefen]")
    raise SystemExit(heilen(args[0], "--nur-pruefen" in sys.argv))

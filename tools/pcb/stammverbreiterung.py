"""Verbreitert zu schmale Leistungssegmente so weit, wie Platz ist.

## Warum es dieses Werkzeug gibt (Aufgabe D3, v2.1)

Nach dem Dreilauf-Rezept (s. CONTRIBUTING.md und
`tools/pcb/stammtrennung.py`) liegt der 24-V-Stamm auf allen vier
Brettern zu ueber 90 % in voller Breite -- aber es bleiben einzelne,
kurze Stuecke von 1-5 mm bei 0,25 mm. Sie stammen NICHT aus einem
Platzmangel: der Router legt sie schon auf dem BLANKEN Brett so an
(nachgemessen: Dimmer1, Lauf 1 ohne jedes andere Kupfer, 71,3 mm bei
1,40 mm und 8,0 mm bei 0,25 mm), naemlich dort, wo er eine
Stichverbindung an vorhandenes Kupfer haengt. Um sie herum ist oft
reichlich Platz.

Das ist genau dasselbe Muster wie bei `tools/pcb/via_weld.py`: der
Router liefert etwas, das fast richtig ist, und es ist billiger und
ehrlicher, das Kupfer NACHTRAEGLICH zu vervollstaendigen, als die
Pruefung aufzuweichen. Kein Toleranztrick -- echtes zusaetzliches
Kupfer.

## Wie breit ist "so weit, wie Platz ist"

Fuer jedes zu schmale Segment wird die Breite schrittweise erhoeht und
JEDES MAL am Board geprueft, ob das breitere Kupfer noch den
Netzklassen-Abstand zu FREMDEM Kupfer (Pads, Bahnen, Vias anderer
Netze) haelt und innerhalb des Platinenrands bleibt. Genommen wird die
groesste Breite, die besteht -- hoechstens die vom Gate geforderte
(mehr waere Verschwendung, nicht Sicherheit). Eigenes Netz wird NICHT
als Hindernis gezaehlt: das ist derselbe Leiter.

Gefunden werden die Segmente ueber `strombelastung.py` selbst -- also
ueber denselben Strom je Kante, gegen den auch das Gate urteilt. Zwei
getrennte Vorstellungen davon, welches Segment zu schmal ist, waeren
genau das Auseinanderlaufen, vor dem `tools/pcb/fertigung.py` warnt.

Bleibt danach etwas uebrig, meldet das Werkzeug es NAMENTLICH und gibt
1 zurueck. Es ist kein Ersatz fuer das Gate, sondern ein Schritt davor.

Aufruf: kipy stammverbreiterung.py <board.kicad_pcb> <spec_modul>
"""
import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import strombelastung as SB

import pcbnew

ABSTAND = 0.2      # mm, Netzklassen-Clearance (netclasses.py setzt 0,2)
RAND = 0.5         # mm, Platinenrand-Abstand (Board-Constraint)
SCHRITT = 0.05     # mm, Raster, in dem die Breite gesucht wird
# Wie weit ein Segment hoechstens zur Seite ruecken darf (mm). Die
# Nachbarsegmente wandern NICHT mit -- sie bleiben nur so lange
# verbunden, wie ihre Endpunkte im Kupfer dieser Bahn liegen. 0,5 mm
# ist deutlich weniger als die halbe Stammbreite (1,335/2 = 0,667) und
# damit auch bei der schmalsten hier verbreiterten Bahn sicher; die
# zweite Schranke noetig/2 steht unten im Code.
VERSATZ_MAX = 0.50 # mm
# Feinraster fuer den zweiten Durchgang der Breitensuche (mm). 0,01 mm
# ist KiCads eigene Anzeigeauflusung und deutlich groesser als die
# Fertigungstoleranz -- feiner zu suchen waere Scheingenauigkeit.
FEIN = 0.01        # mm


def _fremde(board, netcode, _cache={}):
    """Kupfer anderer Netze als Kollisionsformen.

    Gemerkt je Netz: auf einer fertig verlegten Platine sind das ueber
    tausend Objekte, und die Liste haengt nur vom Netz ab. Sie bei jedem
    einzelnen Segment neu zu bauen hat den Lauf von Sekunden auf viele
    Minuten gestreckt.
    """
    if netcode in _cache:
        return _cache[netcode]
    aus = []
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() != netcode:
                aus.append(p)
    for t in board.GetTracks():
        if t.GetNetCode() != netcode:
            aus.append(t)
    _cache[netcode] = aus
    return aus


def _sperrflaechen(board, _cache=[]):
    """Regelflaechen, die auf ihrer Lage keine Bahnen erlauben.

    WARUM DAS HIERHER GEHOERT (Aufgabe D3, gemessen am Motormodul).
    Dieses Werkzeug macht Kupfer BREITER und verschiebt es -- beides
    kann es in eine Sperrflaeche hineinwachsen lassen, ohne dass ein
    einziges fremdes Kupferstueck beruehrt wird. Genau das passierte:
    `/Out2` wurde auf 0,713 mm gebracht und 0,05 mm zur Seite gerueckt,
    wodurch seine KANTE in `spec_motor.RULE_AREAS`' ANTENNE_FREI
    (F.Cu, x 29,0..50,0) geriet -- drei `items_not_allowed`-Verstoesse,
    die kicad-cli danach meldete. Die Antennenfreiheit ist eine
    Vertragszusage (steckerprobe/pcb_checks pruefen sie), kein
    Schoenheitswunsch; ein Werkzeug, das sie beim Verbreitern nicht
    kennt, darf nicht verbreitern.
    """
    if _cache:
        return _cache[0]
    aus = []
    for z in board.Zones():
        if not z.GetIsRuleArea():
            continue
        if not z.GetDoNotAllowTracks():
            continue
        aus.append(z)
    _cache.append(aus)
    return aus


def _passt(board, track, breite_mm, fremde, bb):
    """Kollidiert das Segment bei dieser Breite mit fremdem Kupfer?"""
    alt = track.GetWidth()
    track.SetWidth(int(round(breite_mm * 1e6)))
    try:
        lage = track.GetLayer()
        form = track.GetEffectiveShape(lage)
        # Sperrflaechen zuerst: sie sind wenige und schliessen am
        # haertesten aus.
        for z in _sperrflaechen(board):
            if not z.IsOnLayer(lage):
                continue
            if form.Collide(z.Outline(), 0):
                return False
        # Nur Hindernisse in der Naehe pruefen: die Bounding-Box des
        # Segments plus reichlich Rand. Sonst kostet jede Breitenstufe
        # einen Kollisionstest gegen jedes Kupferstueck der Platine.
        nah = track.GetBoundingBox()
        nah.Inflate(int((ABSTAND + 2.0) * 1e6))
        # Platinenrand
        k = track.GetBoundingBox()
        if not (bb.GetLeft() + int(RAND * 1e6) <= k.GetLeft()
                and k.GetRight() <= bb.GetRight() - int(RAND * 1e6)
                and bb.GetTop() + int(RAND * 1e6) <= k.GetTop()
                and k.GetBottom() <= bb.GetBottom() - int(RAND * 1e6)):
            return False
        for o in fremde:
            if not nah.Intersects(o.GetBoundingBox()):
                continue
            if isinstance(o, pcbnew.PAD):
                if (o.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
                        and not o.IsOnLayer(lage)):
                    continue        # SMD-Pad der Gegenlage: kein Hindernis
                of = o.GetEffectiveShape(lage)
            elif o.Type() == pcbnew.PCB_TRACE_T:
                if o.GetLayer() != lage:
                    continue        # Bahn der Gegenlage
                of = o.GetEffectiveShape(lage)
            else:
                of = o.GetEffectiveShape(lage)   # Via: beide Lagen
            if form.Collide(of, int(ABSTAND * 1e6)):
                return False
        return True
    finally:
        track.SetWidth(alt)


def breiteste(board, t, noetig, fremde, bb):
    """Groesste Breite, die dieses Segment an seinem Platz noch haelt.

    Zwei Durchgaenge: grob im SCHRITT-Raster, dann fein im FEIN-Raster
    ueber die letzte grobe Stufe hinaus, und zum Schluss GENAU `noetig`.

    WARUM DER FEINE DURCHGANG (Aufgabe D3, gemessen am Motormodul). Das
    Raster ist eine Suchhilfe, kein Ziel -- aber es verschenkt genau
    das, was ueber der letzten Stufe noch frei ist. Und bei einer
    Engstelle zaehlt jedes Zehntel doppelt, weil die Kurzhals-Grenze
    PROPORTIONAL zur Breite waechst: der Stamm neben der Stiftreihe
    J105 kam grob auf 0,400 mm (Grenze 4,711 mm) und war auf 5,223 mm
    Laenge ROT -- 0,450 mm haetten die Grenze auf 5,30 mm gehoben und
    dieselbe Engstelle gruen gemacht. Wer hier auf 0,05 mm rundet,
    verwirft eine Loesung, die auf der Platine vorhanden ist.
    """
    beste = t.GetWidth() / 1e6
    breite = beste
    while breite + SCHRITT <= noetig + 1e-9:
        breite += SCHRITT
        if _passt(board, t, breite, fremde, bb):
            beste = breite
        else:
            break
    feiner = beste
    while feiner + FEIN <= noetig + 1e-9:
        feiner += FEIN
        if _passt(board, t, feiner, fremde, bb):
            beste = feiner
        else:
            break
    if beste < noetig - 1e-9 and _passt(board, t, noetig, fremde, bb):
        beste = noetig
    return beste


def durchgang(board_pfad, spec_pfad):
    spec = importlib.import_module(spec_pfad)
    board = pcbnew.LoadBoard(board_pfad)
    bb = board.GetBoardEdgesBoundingBox()
    plan = SB.pad_stroeme(spec)

    # Soll-Breite je zu schmaler Graph-Kante, abgelegt als MITTELPUNKT.
    #
    # Nicht ueber die Endpunkte: `strombelastung.baue_graph()` zerlegt
    # eine Bahn an jedem T-Abzweig, der auf ihr liegt -- eine
    # Graph-Kante ist dann nur ein STUECK des Bahnobjekts und hat
    # andere Endpunkte als dieses. Wer ueber Endpunkte zuordnet,
    # verbreitert genau die zerlegten (und damit meist die langen)
    # Stuecke NICHT. Der Mittelpunkt liegt dagegen immer auf dem
    # Bahnobjekt und ordnet beide Faelle richtig zu.
    soll = []           # (netz, lage, mx_nm, my_nm, noetig_mm)
    for netz, (quellen, senken, deckel, gruppen) in sorted(plan.items()):
        g, _pads = SB.baue_graph(board, netz)
        if not g.kanten:
            continue
        q = [("PAD",) + tuple(x) for x in quellen]
        s = {("PAD",) + tuple(k): v for k, v in senken.items()}
        # Dieselbe Erreichbarkeitspruefung wie im Gate -- und aus dem
        # gleichen Grund: eine Senke, die der Graph nicht kennt, gilt in
        # kantenstroeme() als "muss durch JEDE Kante" und treibt damit
        # jede Kante auf den Deckel. GEMESSEN (Aufgabe D3): auf einem
        # Brett, dessen Abzweig-Pads noch abgetrennt waren, verlangte
        # dieses Werkzeug 1,335 mm fuer einen Zweig, der 0,713 mm
        # braucht. Dieses Werkzeug gehoert also NACH --anheften.
        adj = SB._nachbarn(g)
        # Haengt die QUELLE selbst schon an Kupfer? Wenn nicht, ist
        # dieses Netz noch gar nicht verlegt -- es hat dann hoechstens
        # Escape-Stege am Bauteil (qfn_fanout.py), und ein Steg ohne
        # Zuleitung fuehrt noch keinen Strom.
        #
        # WARUM DAS EIN EIGENER FALL IST (Aufgabe D3, gemessen am
        # Motormodul). Dieses Werkzeug laeuft im Rezept ZWISCHEN den
        # Routing-Laeufen, nicht erst am Ende -- nur dort ist noch Platz
        # zum Verbreitern. Zu diesem Zeitpunkt sind die Ausgaenge
        # verlegt, der 24-V-Stamm aber noch nicht. Ohne diese
        # Unterscheidung brach der Lauf mit "von der Quelle nicht
        # erreichbar: U90.1, C90.1, ..." ab -- und meldete damit einen
        # Fehler, wo bloss die Reihenfolge noch nicht durch war.
        #
        # Die Schutzwirkung bleibt: sobald die Quelle Kupfer hat, ist
        # eine unerreichbare Senke wieder ein harter Befund (sonst
        # rechnet kantenstroeme() sie als "muss durch JEDE Kante" und
        # treibt jede Kante auf den Deckel -- GEMESSEN: 1,335 mm
        # verlangt fuer einen Zweig, der 0,713 mm braucht).
        quelle_haengt = any(g.find(x) in adj for x in q)
        if not quelle_haengt:
            print("  %s uebersprungen -- noch nicht verlegt (die Quelle "
                  "haengt an keinem Kupfer)" % netz)
            continue
        erreichbar = SB._erreichbar(adj, [g.find(x) for x in q])
        lose = [p for p, I in s.items()
                if I > 0 and g.find(p) not in erreichbar]
        if lose:
            print("ROT: %s -- von der Quelle nicht erreichbar: %s "
                  "(erst nach --anheften aufrufen)"
                  % (netz, ", ".join("%s.%s" % (p[1], p[2]) for p in lose)))
            return 0, ["ROT: %s von der Quelle nicht erreichbar" % netz]
        stroeme = SB.kantenstroeme(g, q, s, deckel, gruppen)
        for i, (a, b, w, L, art, ort) in enumerate(g.kanten):
            if art != "Bahn" or stroeme[i] <= 0:
                continue
            noetig = SB.erf_breite(stroeme[i])
            if w >= noetig - 1e-9:
                continue
            mx = (a[0] + b[0]) * SB.TOL / 2.0
            my = (a[1] + b[1]) * SB.TOL / 2.0
            soll.append((netz, a[2], mx, my, noetig))

    if not soll:
        print("nichts zu verbreitern -- jedes Leistungssegment traegt "
              "seinen Strom bereits")
        return 0, []

    geaendert = 0
    uebrig = []
    versetzt = []
    for t in board.GetTracks():
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        ax, ay = t.GetStart().x, t.GetStart().y
        bx, by = t.GetEnd().x, t.GetEnd().y
        noetig = 0.0
        for (netz, lage, mx, my, n) in soll:
            if netz != t.GetNetname() or lage != t.GetLayer():
                continue
            # Mittelpunkt der Graph-Kante auf diesem Bahnobjekt?
            if (abs(mx - ax) < 2 and abs(my - ay) < 2) or \
               (abs(mx - bx) < 2 and abs(my - by) < 2) or \
               SB._auf_strecke(mx, my, ax, ay, bx, by, tol_nm=2000):
                noetig = max(noetig, n)
        if noetig <= 0:
            continue
        fremde = _fremde(board, t.GetNetCode())
        beste = breiteste(board, t, noetig, fremde, bb)
        # Und zum Schluss GENAU die geforderte Breite probieren.
        #
        # Ohne diesen Schritt endet die Rasterschleife bei der letzten
        # Stufe UNTER dem Soll -- gemessen am Motormodul: 0,700 statt
        # 0,713 mm, also 1,8 % zu wenig, und damit auf 26 mm Laenge ROT,
        # obwohl der Platz da war. Ein Raster ist eine Suchhilfe, kein
        # Ziel; das Ziel steht in erf_breite().
        if beste < noetig - 1e-9 and _passt(board, t, noetig, fremde, bb):
            beste = noetig
        # Reicht der Platz MITTIG nicht, dann zur Seite ruecken.
        #
        # WARUM (Aufgabe D3, gemessen am Motormodul). Eine KiCad-Bahn
        # waechst immer um ihre Mittellinie -- sie kann nicht auf einer
        # Seite breiter werden als auf der anderen. Der 24-V-Stamm lief
        # 26 mm lang dicht an der Stiftreihe J105 (Pads 1,70 mm, Mitte
        # x = 48,39, also Rand bei 49,24) mit der Mittellinie auf
        # x = 50,10. Bis zum Pad blieben 0,86 mm, abzueglich 0,2 mm
        # Abstand also 0,66 mm halbe Breite = 1,320 mm -- gegen 1,335 mm
        # gefordert. RECHTS daneben war auf dieser Lage nichts. Es
        # fehlte kein Platz, es fehlte nur die MITTE an der richtigen
        # Stelle: 0,15 mm zur Seite, und dieselbe Bahn passt.
        #
        # Verschoben wird NUR dieses Segment, nicht die Nachbarn. Die
        # bleiben verbunden, weil ihre Endpunkte weiterhin INNERHALB
        # des (jetzt breiten) Kupfers liegen -- genau die Ueberlegung,
        # mit der strombelastung.baue_graph() auch den Via-Versatz des
        # Routers als dasselbe Kupfer zaehlt. Damit das sicher gilt,
        # wird hoechstens um die halbe Zielbreite verrueckt (und nie
        # weiter als GRENZE), und danach prueft ohnehin DRC nach.
        if beste < noetig - 1e-9:
            dx, dy = (bx - ax), (by - ay)
            laenge = math.hypot(dx, dy)
            if laenge > 0:
                nx, ny = -dy / laenge, dx / laenge     # Einheitsnormale
                grenze = min(VERSATZ_MAX, noetig / 2.0)
                schritte = int(grenze / SCHRITT)
                alt_a = pcbnew.VECTOR2I(int(ax), int(ay))
                alt_b = pcbnew.VECTOR2I(int(bx), int(by))
                bester_versatz = 0.0
                for i in range(1, schritte + 1):
                    for vz in (+1, -1):
                        d = vz * i * SCHRITT * 1e6
                        t.SetStart(pcbnew.VECTOR2I(int(round(ax + nx * d)),
                                                   int(round(ay + ny * d))))
                        t.SetEnd(pcbnew.VECTOR2I(int(round(bx + nx * d)),
                                                 int(round(by + ny * d))))
                        # An DIESER Stelle die Breite genauso suchen wie
                        # mittig -- nicht nur die volle Zielbreite
                        # probieren.
                        #
                        # WARUM (Aufgabe D3, gemessen am Motormodul).
                        # Die erste Fassung nahm einen Versatz nur an,
                        # wenn dort SOFORT die volle Breite passte. Wo
                        # das nie gelingt, verschenkte sie jede
                        # Teilverbesserung: der Stamm lag zwischen
                        # J105.11 und J105.12 (Luecke 0,84 mm, nie genug
                        # fuer 1,335 mm) mit 0,38 mm Luft zur einen und
                        # 0,46 mm zur anderen Seite -- mittig also
                        # 0,350 mm. 0,05 mm zur Seite macht daraus
                        # 0,44 mm, und weil die Kurzhals-Grenze
                        # proportional zur Breite waechst (4,12 mm bei
                        # 0,35 mm, 5,18 mm bei 0,44 mm), traegt dieselbe
                        # 4,3-mm-Engstelle damit ihren Strom. Breiter
                        # ist besser, auch wenn es nicht voll reicht.
                        hier = breiteste(board, t, noetig, fremde, bb)
                        if hier > beste + 1e-9:
                            beste = hier
                            bester_versatz = d
                        t.SetStart(alt_a)
                        t.SetEnd(alt_b)
                    if beste >= noetig - 1e-9:
                        break
                if bester_versatz:
                    t.SetStart(pcbnew.VECTOR2I(
                        int(round(ax + nx * bester_versatz)),
                        int(round(ay + ny * bester_versatz))))
                    t.SetEnd(pcbnew.VECTOR2I(
                        int(round(bx + nx * bester_versatz)),
                        int(round(by + ny * bester_versatz))))
                    versetzt.append(
                        "%s (%.2f|%.2f)-(%.2f|%.2f) %s um %.2f mm zur "
                        "Seite -> %.3f mm" % (t.GetNetname(), ax / 1e6,
                                              ay / 1e6, bx / 1e6, by / 1e6,
                                              pcbnew.LayerName(t.GetLayer()),
                                              abs(bester_versatz) / 1e6, beste))
        if beste > t.GetWidth() / 1e6 + 1e-9:
            print("  %s (%.2f|%.2f)-(%.2f|%.2f) %s: %.3f -> %.3f mm "
                  "(noetig %.3f)"
                  % (t.GetNetname(), t.GetStart().x / 1e6, t.GetStart().y / 1e6,
                     t.GetEnd().x / 1e6, t.GetEnd().y / 1e6,
                     pcbnew.LayerName(t.GetLayer()), t.GetWidth() / 1e6,
                     beste, noetig))
            # Aufrunden: eine abgerundete Breite waere um Bruchteile
            # eines Nanometers ZU SCHMAL und wuerde vom Gate wieder
            # gemeldet.
            t.SetWidth(int(math.ceil(beste * 1e6)))
            geaendert += 1
        if beste < noetig - 1e-9:
            uebrig.append("%s (%.2f|%.2f)-(%.2f|%.2f) %s: %.3f statt %.3f mm"
                          % (t.GetNetname(), t.GetStart().x / 1e6,
                             t.GetStart().y / 1e6, t.GetEnd().x / 1e6,
                             t.GetEnd().y / 1e6, pcbnew.LayerName(t.GetLayer()),
                             beste, noetig))

    if geaendert:
        board.Save(board_pfad)
    print("%d Segment(e) verbreitert" % geaendert)
    if versetzt:
        print("davon zur Seite gerueckt, weil mittig kein Platz war:")
        for z in versetzt:
            print("  " + z)
    return geaendert, uebrig


DURCHGAENGE_MAX = 6


def main(board_pfad, spec_pfad):
    """Verbreitert, bis sich nichts mehr aendert.

    WARUM MEHRERE DURCHGAENGE (Aufgabe D3, gemessen am Motormodul).
    Welches Segment als "zu schmal" gilt, haengt an der KETTE, in der es
    steckt: `strombelastung.ketten()` beurteilt eine Engstelle mit der
    Laenge der GANZEN zusammenhaengenden Kette und der SCHMALSTEN Breite
    darin. Wird ein Glied breiter, zerfaellt die Kette -- die
    verbleibenden Stuecke sind kuerzer, brauchen also eine andere
    Mindestbreite, und ein Nachbar, der vorher nicht in `soll` stand,
    kann jetzt hineinfallen.

    GEMESSEN: der Stamm des Motormoduls war nach EINEM Durchgang noch
    ROT (5,223 mm bei 0,400 mm gegen 4,711 mm Grenze); der ZWEITE
    Durchgang verbreiterte ein einziges weiteres Segment, und dieselbe
    Engstelle war 3,950 mm lang und gruen. Ein Werkzeug, das man zweimal
    aufrufen MUSS, ist eine Falle -- deshalb laeuft die Wiederholung
    hier drin, nicht in der Anleitung.
    """
    uebrig = []
    for nr in range(1, DURCHGAENGE_MAX + 1):
        print("-- Durchgang %d" % nr)
        geaendert, uebrig = durchgang(board_pfad, spec_pfad)
        if not geaendert:
            break
    if uebrig:
        print("NICHT auf volle Breite gebracht (Platz fehlt):")
        for z in uebrig:
            print("  " + z)
        print("Das heisst NICHT automatisch ROT -- kurze Engstellen "
              "duerfen bleiben (Kurzhals-Regel). Das Urteil faellt "
              "strombelastung.py.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Aufruf: stammverbreiterung.py <board.kicad_pcb> "
                          "<spec_modul>")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))

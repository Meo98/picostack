"""Strombelastbarkeit der Leistungsnetze -- misst nach, statt zu glauben.

Herkunft: Aufgabe D2 (v2.1) hat dieses Gate angelegt und damit vier rote
Bretter gefunden; Aufgabe D3 (2026-09-15) hat es umgebaut, weil die
ERSTE Fassung an zwei Stellen die falsche Zahl prueft. Beide Korrekturen
stehen unten ausgeschrieben, weil sie das Urteil umdrehen.

## Was die erste Fassung richtig gemacht hat (bleibt)

Sie misst ZUSAMMENHAENGENDE Ketten schmaler Bahnsegmente statt einzelner
pcbnew-Objekte -- das schmalste Einzelsegment ist oft nur ein Eckpunkt
einer viel laengeren Kette gleicher Breite. Und sie kennt zwei
Beurteilungen statt einer:

1. **Lang**: Standard-IPC-2221-Ampacity (`erf_breite()`).
2. **Kurz**: eine sehr kurze Engstelle zwischen zwei breiten
   Kupferflaechen wird durch AXIALE WAERMELEITUNG in dieses Nachbarkupfer
   gekuehlt, nicht durch eigene Konvektion. IPC-2221 nimmt Konvektion
   ueber die eigene, lange Oberflaeche an und ist fuer sehr kurze
   Strecken unrealistisch pessimistisch. `kurzhals_grenze()` ist die
   Laenge, bei der die Leitungsrechnung genau SCHWELLE_K ergibt.

Die zweite Rechnung ist eine dokumentierte Annahme (Waermeleitung Kupfer
385 W/(m*K), keine FEA), keine Norm. Sollte sie sich als falsch erweisen,
ist die Korrektur: SCHWELLE_K senken oder die Kurzhals-Ausnahme streichen
(dann wird jede Engstelle nach Fall 1 beurteilt -- strenger, nie das
Gegenteil).

## Korrektur 1 (D3): ein Netz ist kein Strom, sondern ein BAUM

Die erste Fassung gab jedem Netz EINEN Strom und verlangte ihn auf JEDEM
Segment. Fuer `/+24V` heisst das: der Abzweig zum Gateteiler R90
(1,3 mA, gemessen: 24 V / 2 x 10 kOhm) haette dieselbe Breite gebraucht
wie der Stamm zur Klemme. Das ist physikalisch falsch, nicht nur
konservativ -- und es war der Grund, warum in Aufgabe D2 zehn
Routing-Varianten scheiterten: das Werkzeug verlangte 1,3 mm Kupfer fuer
einen Milliampere-Zweig quer ueber ein volles Brett.

Diese Fassung deklariert deshalb den Strom JE PAD (`pad_stroeme()`),
baut aus den verlegten Bahnen, Vias und Pads den Leitungsgraphen des
Netzes und rechnet fuer JEDE Kante aus, welcher Strom durch sie MUSS:

    I(Kante) = min( Summe aller Senken, die ueber diese Kante erreichbar
                    sind, Deckel ),

wobei "ueber diese Kante erreichbar" heisst: entfernt man die Kante,
verliert die Senke die Verbindung zur Quelle -- ODER die Kante liegt auf
irgendeinem Pfad Quelle->Senke (bei parallelen Pfaden; dann bekommt jeder
Pfad den vollen Strom zugeschrieben, was konservativ ist, weil er sich in
Wahrheit teilt). Fuer einen Baum -- und mehr erzeugt ein Router hier
nicht -- ist die Rechnung exakt.

Der `Deckel` ist die Zusage aus dem Vertrag
(`stack_spec.STROMBUDGET["modul_gesamt_a"]`): mehr als das darf ein Modul
gar nicht ziehen, also muss auch keine Kante mehr tragen. Ohne ihn ergaebe
die Summe der vier Dimmer4-Kanaele wieder die 12 A, die das Brett nie
erreichen kann (Herleitung: stack_spec.STROMBUDGET).

## Korrektur 2 (D3): ein Via ist ein Leiter, kein Punkt

Die erste Fassung sah nur `PCB_TRACE_T`. Ein Via mit 0,4 mm Bohrung hat
aber nur pi x 0,4 mm x 0,018 mm = 0,023 mm^2 Querschnitt -- als LANGE
Bahn gerechnet truege es 2,3 A, also weniger als der Stamm fuehrt. Diese
Fassung nimmt Vias als Kanten mit auf: Ersatzbreite
`pi x Bohrung x VIA_KUPFER / KUPFER_AUSSEN`, Laenge = Plattendicke
(1,6 mm). Damit gilt fuer sie DIESELBE Zweiteilung wie fuer jede andere
Engstelle -- und sie fallen unter die Kurzhals-Ausnahme (bei 4,0 A und
0,4 mm Bohrung liegt die Grenze bei 7,6 mm, die Barriere ist 1,6 mm lang),
NICHT weil Vias ausgenommen waeren, sondern weil dieselbe Rechnung sie
bestehen laesst. Ein 0,2-mm-Via bei 8 A faellt durch.

## Kupfer und Temperaturanstieg

1 oz (35 um) Aussenlage (`fertigung.KUPFER_AUSSEN`), JLCs Vorgabe fuer
ein 2-Lagen-Brett ohne Sonderwunsch.

SCHWELLE_K = 20 K, NICHT 10 K -- bewusst, mit Zahlen (volle Herleitung:
task-v21d2-report.md Abschnitt 3). Die "Recommended"-Spalte von
KiCadRoutingTools `docs/power-nets.md`, nach der `fertigung.TRACK_POWER`
gewaehlt wurde, ist selbst bei 20 K hergeleitet (nachgerechnet: 1,00 mm
traegt bei 20 K 3,25 A, bei 10 K nur 2,40 A). Wer den strengeren Massstab
will, aendert diese eine Konstante -- dann steigen die noetigen Breiten um
rund 52 %, und das Brett braucht eine andere Bauteilanordnung.

## Woher die Stroeme kommen (jede Zahl mit Quelle)

Das Modul-Gesamtbudget, die Stapel-Durchleitung, der Kanal- und der
Motorstrom stehen im VERTRAG (`tools/stack_spec.py::STROMBUDGET`) --
nicht hier, weil sie eine Zusage an fremde Modulbauer sind und auf dem
Bestueckungsdruck landen. Die Aufteilung auf die einzelnen PADS steht
dagegen hier, weil sie aus dem Schaltplan dieses konkreten Moduls folgt
(s. `pad_stroeme()`, jede Zeile mit Begruendung).

Aufruf: kipy strombelastung.py <board.kicad_pcb> <spec_modul>
Rueckgabe 1, sobald eine Kante ROT gemeldet wird.
"""
import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import fertigung
import stack_spec as S

import pcbnew

# ---------------------------------------------------------------- Physik
K_AUSSEN = 0.048           # IPC-2221, Aussenlage (docs/power-nets.md)
SCHWELLE_K = 20.0          # bewusst NICHT 10 K -- Begruendung im Docstring
RHO_CU = 1.7e-8            # Ohm*m, spezifischer Widerstand Kupfer (~20 C)
K_CU = 385.0               # W/(m*K), Waermeleitfaehigkeit Kupfer

BUDGET = S.STROMBUDGET


def erf_breite(strom_a, dt_k=SCHWELLE_K, dicke_mm=None):
    """IPC-2221-Mindestbreite (mm) fuer eine LANGE Aussenlagenbahn."""
    t_mm = fertigung.KUPFER_AUSSEN if dicke_mm is None else dicke_mm
    if strom_a <= 0:
        return 0.0
    a_mil2 = (strom_a / (K_AUSSEN * dt_k ** 0.44)) ** (1 / 0.725)
    return (a_mil2 / (t_mm / 0.0254)) * 0.0254


def kurzhals_grenze(strom_a, breite_mm, dt_k=SCHWELLE_K, dicke_mm=None):
    """Laenge (mm), bis zu der eine schmale Stelle als waermeleitungs-
    gekuehlt gelten darf (s. Modul-Docstring).

    Modell: ein Stueck der Laenge L, gleichmaessig bestromt, an BEIDEN
    Enden an thermisch grosses, nahezu umgebungswarmes Kupfer
    angeschlossen. Fuer eine verteilte Waermequelle mit an den Enden
    fixierter Temperatur liegt die groesste Erwaermung in der Mitte bei
    P * L / (4 * k * A). Aufgeloest nach L fuer die Ziel-Erwaermung.
    """
    if strom_a <= 0:
        return float("inf")
    t_mm = fertigung.KUPFER_AUSSEN if dicke_mm is None else dicke_mm
    a_cs = (breite_mm * 1e-3) * (t_mm * 1e-3)
    return ((dt_k * 4 * K_CU * a_cs ** 2 / (strom_a ** 2 * RHO_CU)) ** 0.5) * 1e3


def via_ersatzbreite(bohrung_mm):
    """Breite einer Aussenlagenbahn mit demselben Querschnitt wie das
    Via-Loch: Umfang x Lochkupfer, umgerechnet auf 1-oz-Dicke."""
    return (math.pi * bohrung_mm * fertigung.VIA_KUPFER
            / fertigung.KUPFER_AUSSEN)


# ---------------------------------------- Stroeme je Pad, je Modultyp
# Jeder Wert hier ist eine HERGELEITETE Groesse aus dem Schaltplan
# dieses Moduls, keine Vertragszahl -- die Vertragszahlen (Budget,
# Kanalstrom, Motorstrom, Stapel-Durchleitung) kommen aus
# stack_spec.STROMBUDGET und werden unten nur VERTEILT.
#
# Konvention: (Referenz, Padnummer) -> Strom in A. "quelle" ist das Pad,
# von dem der Strom kommt; alles andere sind Senken.

# Abzweige, die auf JEDEM Modul dieselben sind (Versorgungszelle):
I_REGLER_EIN = 0.30   # U90-Eingang: 5 V x 1,0 A (K7805-1000R3-Nennstrom,
                      # tools/sch/versorgung.py) / 24 V / 0,8 Wirkungsgrad
                      # = 0,26 A; auf 0,30 A aufgerundet.
I_STUETZ = None       # C90: s. unten, haengt am Modulbudget (Welligkeit)
I_KLEINSIGNAL = 0.05  # R90-Gateteiler (24 V / 20 kOhm = 1,3 mA), D90-TVS
                      # (Sperrstrom < 1 uA im Normalbetrieb), 3,3-kOhm-
                      # Pullups: allesamt weit unter 50 mA, hier
                      # einheitlich grosszuegig auf 0,05 A gesetzt statt
                      # auf 0 -- eine Bahn mit Strom 0 waere von der
                      # Pruefung gar nicht mehr erfasst.
I_ABBLOCK = 1.00      # 100-nF-Abblockkondensatoren an der VM-Schiene des
                      # DRV8876 (C9/C11): sie liefern die HF-Anteile des
                      # Bruecken-Schaltstroms. Der Bulk-Anteil laeuft
                      # ueber C90; 1,0 A ist fuer den Keramik-Anteil eines
                      # 2,5-A-Brueckenstroms reichlich bemessen.
I_FREILAUF = 0.50     # Dn (SS36C, Kathode an +24V): fuehrt nur die
                      # Abkommutierung der ZULEITUNGS-Induktivitaet einer
                      # ueberwiegend ohmschen LED-Last
                      # (tools/sch/dimmermodul.py: "LED-Baender sind zwar
                      # ueberwiegend ohmsch, aber die Zuleitung ist eine
                      # Induktivitaet"). Bei 1 uH und 3 A klingt der Strom
                      # in L*I/U = 125 ns ab -- bei LED-PWM (<= 20 kHz)
                      # ein Mittelwert weit unter 50 mA. 0,50 A ist das
                      # Zehnfache davon. WICHTIG: fuer eine WIRKLICH
                      # induktive Last (Magnetventil, Luefter) gilt diese
                      # Zahl nicht -- solche Lasten sind nicht der
                      # zugesagte Zweck des Kanals ("LED-Kanal n").


def _welligkeit(budget_a):
    """C90 (Stuetz-Elko) fuehrt den Wechselanteil des PWM-Stroms.

    Bei einem zwischen 0 und I getasteten, ueberwiegend ohmschen Strom
    ist der Effektivwert des Wechselanteils I*sqrt(D(1-D)) und damit
    hoechstens I/2 (bei 50 % Tastgrad). Konservativ die HAELFTE des
    Modulbudgets, nicht ein geschaetzter Betriebspunkt.
    """
    return budget_a / 2.0


def pad_stroeme(spec):
    """{netz: (quellen, {pad: strom_a}, deckel_a)} fuer dieses Modul.

    `quellen` ist eine Menge von (ref, padnummer); `deckel_a` begrenzt
    den Strom, den eine Kante dieses Netzes ueberhaupt tragen kann --
    das ist die Vertragszusage, nicht eine Bequemlichkeit (s. Docstring).
    """
    budget = BUDGET["modul_gesamt_a"]
    stapel = BUDGET["stapel_durchleitung_a"]
    kanal = BUDGET["kanal_a"]
    motor = BUDGET["motor_a"]
    netze = set(spec.POWER_NETS)
    led_netze = sorted(n for n in netze if n.startswith("/LED"))

    aus = {}

    # --- /PWR_IN: Klemme J90 -> Drain Q90. Traegt ALLES, was das Modul
    #     zieht, inklusive dessen, was es in den Stapel weitergibt.
    aus["/PWR_IN"] = ({("J90", "1")}, {("Q90", "2"): budget}, budget, {})

    # --- /+24V: lokale Schiene hinter Q90. Quelle ist Q90s Source.
    gemeinsam = {
        ("U90", "1"): I_REGLER_EIN,
        ("C90", "1"): _welligkeit(budget),
        ("D90", "1"): I_KLEINSIGNAL,
        ("R90", "2"): I_KLEINSIGNAL,
        # Leistungsstecker: zwei Kontaktstellen je Ader, jede fuer sich
        # auf die volle Stapel-Durchleitung bemessen. Begruendung steht
        # im Vertrag (STROMBUDGET["stapel_durchleitung_a"]): faellt einer
        # der beiden parallelen Kontakte aus, traegt der andere alles --
        # deshalb bekommt JEDE Stelle den ganzen Wert, nicht die Haelfte.
        # Ihre SUMME ist aber trotzdem nur einmal die Durchleitung, nicht
        # zweimal -- dafuer sorgt GRUPPEN unten (ohne die verlangte die
        # Pruefung auf dem gemeinsamen Zulauf 6 A statt 3 A).
        ("J103", "1"): stapel,
        ("J103", "3"): stapel,
        # J104 sitzt Pad auf Pad auf J103 (Buchse oben / Stift unten,
        # derselbe Ort) -- dieselbe Kontaktstelle, kein zweiter Strom.
        ("J104", "1"): 0.0,
        ("J104", "3"): 0.0,
    }
    # Pads, die sich EINEN Strom teilen: erreicht eine Kante mehrere
    # Mitglieder, zaehlt hoechstens der Gruppenwert, nicht die Summe.
    gruppen = {"stapel": ({("J103", "1"), ("J103", "3"),
                            ("J104", "1"), ("J104", "3")}, stapel)}

    if "/Out1" in netze or "/Out2" in netze:
        # ---------------------------------------------------- Motormodul
        v24 = dict(gemeinsam)
        v24[("U1", "11")] = motor        # DRV8876 VM -- speist die ganze
                                          # Endstufe (EIN Strompfad
                                          # VM -> Out -> Motor -> Out -> GND)
        v24[("C9", "1")] = I_ABBLOCK
        v24[("C11", "2")] = I_ABBLOCK
        v24[("R16", "1")] = I_KLEINSIGNAL
        v24[("R17", "1")] = I_KLEINSIGNAL
        aus["/+24V"] = ({("Q90", "3")}, v24, budget, gruppen)
        # Motorausgang: der Strom kommt aus der Bruecke und geht zur
        # Klemme (bzw. umgekehrt -- die Richtung wechselt mit der
        # Drehrichtung, der Betrag nicht).
        aus["/Out1"] = ({("U1", "8")}, {("J5", "1"): motor}, motor, {})
        aus["/Out2"] = ({("U1", "10")}, {("J5", "2"): motor}, motor, {})
    elif led_netze:
        # ---------------------------------------------------- Dimmermodul
        v24 = dict(gemeinsam)
        for n in range(1, len(led_netze) + 1):
            v24[("J%d" % (4 + n), "1")] = kanal    # Klemme, Plus-Seite
            v24[("D%d" % n, "1")] = I_FREILAUF     # Freilaufdiode, Kathode
        aus["/+24V"] = ({("Q90", "3")}, v24, budget, gruppen)
        for n in range(1, len(led_netze) + 1):
            # Geschaltetes Minus: die Last haengt an der Klemme, der
            # Strom laeuft von dort in den Kanal-FET.
            aus["/LED%d" % n] = (
                {("J%d" % (4 + n), "2")},
                {("Q%d" % n, "2"): kanal, ("D%d" % n, "2"): I_FREILAUF},
                kanal, {})
    else:
        raise SystemExit("Unbekannter Brett-Typ: weder /Out1 noch /LEDn "
                          "in POWER_NETS")

    # --- /+5V_LOKAL: steht in KEINEM POWER_NETS (Signalklasse), traegt
    #     aber den vollen Reglerstrom. Genau deshalb wird es hier
    #     mitgeprueft: es ist das Netz, bei dem die Netzklasse allein
    #     nichts zusichert.
    aus["/+5V_LOKAL"] = (
        {("U90", "3")},
        {("D91", "2"): 1.0,        # K7805-1000R3-Nennstrom, ganz ueber
                                    # die VSYS-Diode (tools/sch/versorgung.py)
         ("C91", "1"): 0.3},        # Ausgangskondensator, Welligkeitsanteil
        1.0, {})
    return aus


# --------------------------------------------------------- Leitungsgraph
TOL = 1000          # nm-Raster, in dem zwei Endpunkte als derselbe Knoten
                    # gelten (1 um) -- dieselbe Toleranz wie in D2.


class Graph(object):
    """Bahnen, Vias und Pads EINES Netzes als ungerichteter Graph.

    Knoten: Bahn-Endpunkte je Lage, Vias, Pads. Kanten: Bahnsegmente
    (Breite = Bahnbreite) und Vias (Ersatzbreite = via_ersatzbreite(),
    Laenge = Plattendicke). Zwei Bahnen auf VERSCHIEDENEN Lagen am
    selben Ort sind NICHT verbunden -- nur ein Via verbindet sie.
    """

    def __init__(self):
        self.eltern = {}
        self.kanten = []        # (a, b, breite_mm, laenge_mm, art, ort)

    def find(self, k):
        self.eltern.setdefault(k, k)
        while self.eltern[k] != k:
            self.eltern[k] = self.eltern[self.eltern[k]]
            k = self.eltern[k]
        return k

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.eltern[ra] = rb

    def kante(self, a, b, breite, laenge, art, ort):
        self.kanten.append((a, b, breite, laenge, art, ort))


def _pkt(p, lage):
    return (round(p.x / TOL), round(p.y / TOL), lage)


def _auf_strecke(px, py, ax, ay, bx, by, tol_nm=2000):
    """Liegt (px,py) auf der Strecke a->b (ohne die Endpunkte)?

    Gebraucht, weil KiCad (und jeder Router) eine Bahn MITTEN auf einer
    anderen enden lassen darf: elektrisch ein T-Abzweig, in der Datei
    aber zwei Objekte ohne gemeinsamen Endpunkt. Wer das uebersieht,
    bekommt ein Netz, das in mehrere Inseln zerfaellt -- und prueft
    danach eine Topologie, die es auf der Platine nicht gibt.
    """
    dx, dy = bx - ax, by - ay
    laenge2 = dx * dx + dy * dy
    if laenge2 == 0:
        return False
    s = ((px - ax) * dx + (py - ay) * dy) / laenge2
    if not (0.0 < s < 1.0):
        return False
    qx, qy = ax + s * dx, ay + s * dy
    return (px - qx) ** 2 + (py - qy) ** 2 <= tol_nm ** 2


def _kreuzung(a1, b1, a2, b2):
    """Schnittpunkt zweier Strecken -- nur ECHT INNEN, sonst None.

    Ergaenzt `_auf_strecke`: dort endet eine Bahn auf einer anderen
    (T-Abzweig), hier kreuzen sich zwei, ohne dass ein Endpunkt
    beteiligt ist (X-Kreuz). Beides ist derselbe Leiter; nur die
    Dateiform unterscheidet sie.

    Beruehrungen an den Endpunkten liefern bewusst None -- die sind
    ueber `ansatz` (Bahnenden) und die Kupferradius-Vereinigung schon
    erfasst, und ein zweites Mal denselben Punkt einzutragen erzeugt
    nur Null-Segmente.
    """
    x1, y1, x2, y2 = a1.x, a1.y, b1.x, b1.y
    x3, y3, x4, y4 = a2.x, a2.y, b2.x, b2.y
    nenner = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if nenner == 0:
        return None                 # parallel oder entartet
    s = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / nenner
    t = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / nenner
    # Strikt innen auf BEIDEN Strecken. Der Sicherheitsabstand ist
    # relativ: eine 1-nm-Ecke waere kein Kreuz, sondern ein Endpunkt.
    if not (1e-9 < s < 1.0 - 1e-9 and 1e-9 < t < 1.0 - 1e-9):
        return None
    return (int(round(x1 + s * (x2 - x1))), int(round(y1 + s * (y2 - y1))))


def _beruehrung(a1, b1, w1, a2, b2, w2):
    """Beruehren sich zwei Bahnen SEITLICH? Dann der Kontaktpunkt.

    Dritter Fall neben `_auf_strecke` (T-Abzweig) und `_kreuzung`
    (X-Kreuz): zwei Bahnen laufen NEBENEINANDER, ohne sich zu treffen
    und ohne gemeinsamen Endpunkt -- aber sie sind so BREIT, dass ihr
    Kupfer sich ueberlappt.

    WARUM DAS ZAEHLT (Aufgabe D3, gemessen am Motormodul). Der
    24-V-Stamm ist nach dem Verbreitern 1,335 mm breit (Radius
    0,667 mm); ein Abzweig von 0,4 mm (Radius 0,2 mm) lief 0,743 mm
    daneben. 0,667 + 0,2 = 0,867 > 0,743 -- das ist EIN Leiter, und
    kicad-cli bestaetigte es (das Netz stand NICHT in der
    unconnected-Liste). Dieses Modell sah trotzdem zwei Inseln und
    meldete vier Pads als "von der Quelle nicht erreichbar". Eine
    Pruefung, die verbundenes Kupfer fuer getrennt haelt, misst die
    falsche Topologie -- genauso falsch wie der uebersehene X-Kreuz.

    Zurueck kommt der Punkt der dichtesten Annaeherung auf der ERSTEN
    Strecke; er wird auf beiden Bahnen als Knoten eingetragen, und die
    Kupferradius-Vereinigung in `baue_graph` fuehrt sie dann zusammen.
    """
    # Dichteste Annaeherung zweier Strecken (Standardverfahren ueber die
    # Parameter s, t der beiden Geraden, danach aufs Segment geklemmt).
    ux, uy = b1[0] - a1[0], b1[1] - a1[1]
    vx, vy = b2[0] - a2[0], b2[1] - a2[1]
    wx, wy = a1[0] - a2[0], a1[1] - a2[1]
    a = ux * ux + uy * uy
    bb = ux * vx + uy * vy
    c = vx * vx + vy * vy
    d = ux * wx + uy * wy
    e = vx * wx + vy * wy
    nenner = a * c - bb * bb
    if a == 0 or c == 0:
        return None                      # entartete Bahn
    if abs(nenner) < 1e-9:
        s = 0.0                          # parallel: ein Ende genuegt
    else:
        s = max(0.0, min(1.0, (bb * e - c * d) / nenner))
    t = max(0.0, min(1.0, (bb * s + e) / c))
    s = max(0.0, min(1.0, (bb * t - d) / a))
    p1x, p1y = a1[0] + s * ux, a1[1] + s * uy
    p2x, p2y = a2[0] + t * vx, a2[1] + t * vy
    # Koordinaten sind Nanometer, die Breiten kommen in Nanometern
    # herein -- beides in DERSELBEN Einheit vergleichen.
    abstand = math.hypot(p1x - p2x, p1y - p2y)
    if abstand > (w1 + w2) / 2.0:
        return None                      # Kupfer beruehrt sich nicht
    return (int(round(p1x)), int(round(p1y)),
            int(round(p2x)), int(round(p2y)))


def baue_graph(board, netz):
    g = Graph()
    vias = []
    bahnen = []
    for t in board.GetTracks():
        if t.GetNetname() != netz:
            continue
        if t.Type() == pcbnew.PCB_TRACE_T:
            bahnen.append(t)
        elif t.Type() == pcbnew.PCB_VIA_T:
            vias.append(t)

    # Alle Punkte, an denen etwas ansetzen KANN: Bahnenden und
    # Via-Mitten. Jede Bahn wird an jedem solchen Punkt, der auf ihr
    # liegt, zerlegt (s. _auf_strecke).
    ansatz = {}          # lage -> [(x, y)]
    for t in bahnen:
        for p in (t.GetStart(), t.GetEnd()):
            ansatz.setdefault(t.GetLayer(), set()).add((p.x, p.y))
    for v in vias:
        p = v.GetPosition()
        for lage in (pcbnew.F_Cu, pcbnew.B_Cu):
            ansatz.setdefault(lage, set()).add((p.x, p.y))
            # Und der Punkt, an dem eine Bahn dem Via am naechsten kommt,
            # wenn sie es SEITLICH beruehrt statt durch seine Mitte zu
            # laufen.
            #
            # WARUM (Aufgabe D3, gemessen am Motormodul). Der Via-Ring
            # ist 0,6 mm breit; eine 0,2-mm-Bahn, die 0,3 mm neben der
            # Via-Mitte vorbeilaeuft, liegt mit ihrem Kupfer AUF dem Ring
            # -- elektrisch verbunden (kicad-cli fuehrte das Netz nicht
            # als unconnected), ohne gemeinsamen Endpunkt und ohne
            # Kreuzung der Mittellinien. Gemessen bei (50,05|30,20) auf
            # F.Cu: das Modell zerlegte /+24V daraufhin in zwei Inseln
            # und meldete vier Pads als unerreichbar. Die Bahn wird
            # deshalb am Lotfusspunkt zerlegt; die
            # Kupferradius-Vereinigung weiter unten fuehrt den neuen
            # Knoten und das Via dann zusammen.
            vr = v.GetWidth(lage) / 2.0
            for t in bahnen:
                if t.GetLayer() != lage:
                    continue
                ax, ay = t.GetStart().x, t.GetStart().y
                bx, by = t.GetEnd().x, t.GetEnd().y
                dx, dy = bx - ax, by - ay
                L2 = dx * dx + dy * dy
                if L2 == 0:
                    continue
                s = ((p.x - ax) * dx + (p.y - ay) * dy) / L2
                s = max(0.0, min(1.0, s))
                fx, fy = ax + s * dx, ay + s * dy
                if (math.hypot(p.x - fx, p.y - fy)
                        <= vr + t.GetWidth() / 2.0):
                    ansatz.setdefault(lage, set()).add(
                        (int(round(fx)), int(round(fy))))
    # ... UND die Stellen, an denen sich zwei Bahnen desselben Netzes
    # auf derselben Lage KREUZEN, ohne dass ein Endpunkt beteiligt ist.
    #
    # WARUM DAS NOETIG IST (Aufgabe D3, gemessen am Motormodul). Ein
    # T-Abzweig (Endpunkt der einen liegt auf der anderen) wurde schon
    # zerlegt -- ein X-Kreuz nicht. Kupfer, das sich kreuzt, ist aber
    # genauso EIN Leiter: KiCad zaehlt es als verbunden (kicad-cli DRC
    # meldete 0 unconnected), dieses Modell zerlegte das Netz trotzdem
    # in zwei Inseln. Gemessen: /+24V des Motormoduls hatte nach dem
    # Anheften der Abzweige GENAU ZWEI solche Kreuzungen (59,50|25,00
    # und 57,10|22,60, beide F.Cu) -- und die Pruefung meldete daraufhin
    # sieben Pads als "von der Quelle nicht erreichbar", obwohl das
    # Kupfer durchgehend ist.
    #
    # Der Fehler ist nicht nur kosmetisch: eine uebersehene Kreuzung
    # aendert den Leitungsgraphen. Wo sich der Strom in Wirklichkeit auf
    # zwei Pfade teilt, sieht das Modell einen einzigen -- oder es
    # haelt eine Senke fuer unerreichbar und rechnet sie gar nicht.
    # Beides misst eine Topologie, die es auf der Platine nicht gibt.
    for i, t1 in enumerate(bahnen):
        for t2 in bahnen[i + 1:]:
            if t1.GetLayer() != t2.GetLayer():
                continue
            pt = _kreuzung(t1.GetStart(), t1.GetEnd(),
                           t2.GetStart(), t2.GetEnd())
            if pt is not None:
                ansatz.setdefault(t1.GetLayer(), set()).add(pt)
                continue
            # ... und der seitliche Kontakt breiten Kupfers (s.
            # _beruehrung). Auf BEIDEN Bahnen einen Knoten setzen: die
            # Kupferradius-Vereinigung weiter unten fuehrt sie dann
            # zusammen.
            nah = _beruehrung(
                (t1.GetStart().x, t1.GetStart().y),
                (t1.GetEnd().x, t1.GetEnd().y), t1.GetWidth(),
                (t2.GetStart().x, t2.GetStart().y),
                (t2.GetEnd().x, t2.GetEnd().y), t2.GetWidth())
            if nah is not None:
                ansatz.setdefault(t1.GetLayer(), set()).add((nah[0], nah[1]))
                ansatz.setdefault(t1.GetLayer(), set()).add((nah[2], nah[3]))

    for t in bahnen:
        lage = t.GetLayer()
        ax, ay = t.GetStart().x, t.GetStart().y
        bx, by = t.GetEnd().x, t.GetEnd().y
        teiler = sorted(
            (pt for pt in ansatz.get(lage, ())
             if _auf_strecke(pt[0], pt[1], ax, ay, bx, by)),
            key=lambda pt: (pt[0] - ax) ** 2 + (pt[1] - ay) ** 2)
        kette = [(ax, ay)] + teiler + [(bx, by)]
        for (x1, y1), (x2, y2) in zip(kette, kette[1:]):
            a = (round(x1 / TOL), round(y1 / TOL), lage)
            b = (round(x2 / TOL), round(y2 / TOL), lage)
            L = math.hypot(x2 - x1, y2 - y1) / 1e6
            g.find(a), g.find(b)
            if L <= 1e-6:
                g.union(a, b)       # Null-Segment: nur ein Knoten
            else:
                g.kante(a, b, t.GetWidth() / 1e6, L, "Bahn",
                        (x1 / 1e6, y1 / 1e6))
    radius = {}          # Knoten -> Kupferradius in nm
    for (a, b, w, L, art, o) in g.kanten:
        for k in (a, b):
            radius[k] = max(radius.get(k, 0), w * 1e6 / 2.0)
    for v in vias:
        a = _pkt(v.GetPosition(), pcbnew.F_Cu)
        b = _pkt(v.GetPosition(), pcbnew.B_Cu)
        g.find(a), g.find(b)
        g.kante(a, b, via_ersatzbreite(v.GetDrillValue() / 1e6),
                fertigung.PLATINE_DICKE, "Via",
                (v.GetPosition().x / 1e6, v.GetPosition().y / 1e6))
        for k, lage in ((a, pcbnew.F_Cu), (b, pcbnew.B_Cu)):
            # PCB_VIA.GetWidth() braucht in KiCad 10 die Lage (seit
            # lagenabhaengige Restringe moeglich sind) -- ohne sie
            # meldet pcbnew eine Assertion und liefert trotzdem etwas.
            radius[k] = max(radius.get(k, 0), v.GetWidth(lage) / 2.0)

    # Kupfer, das sich BERUEHRT, ist ein Knoten -- auch ohne exakt
    # gleiche Koordinate.
    #
    # WARUM DAS NOETIG IST: der Router setzt ein Via und laesst die Bahn
    # der Gegenlage 0,05 mm daneben enden. Innerhalb des Via-Restrings
    # ist das physisch dasselbe Kupfer (kicad-cli DRC meldet 0
    # unconnected; tools/pcb/via_weld.py schweisst nur die Faelle, die
    # pcb_checks.py ueberhaupt meldet). Ein Modell, das auf exakter
    # Koordinatengleichheit besteht, zerlegt so ein Netz in Inseln --
    # und misst danach Stroeme in einer Topologie, die es auf der
    # Platine nicht gibt (gemessen: /Out1 des Motormoduls zerfiel in
    # zwei Inseln, obwohl DRC 0 unconnected meldet).
    knoten = sorted(radius)
    for i, k1 in enumerate(knoten):
        for k2 in knoten[i + 1:]:
            if k1[2] != k2[2]:
                continue                    # verschiedene Lagen
            d2 = ((k1[0] - k2[0]) * TOL) ** 2 + ((k1[1] - k2[1]) * TOL) ** 2
            if d2 <= (radius[k1] + radius[k2]) ** 2:
                g.union(k1, k2)

    # Pads: jeder Bahn-Endpunkt und jedes Via, das im Pad liegt, gehoert
    # zum selben Knoten wie das Pad. pcbnew.PAD.HitTest() nimmt die
    # ECHTE Padform (Rechteck, Oval, Rundung, Rotation) -- deshalb hier
    # kein eigenes Geometriemodell.
    pad_knoten = {}
    punkte = list(g.eltern.keys())
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != netz:
                continue
            schl = ("PAD", f.GetReference(), p.GetPadName())
            pad_knoten.setdefault(schl, []).append(schl)
            g.find(schl)
            for (x, y, lage) in punkte:
                if not p.IsOnLayer(lage):
                    continue
                if p.HitTest(pcbnew.VECTOR2I(x * TOL, y * TOL), 0):
                    g.union((x, y, lage), schl)
    return g, sorted(pad_knoten)


def _nachbarn(g, ohne=None):
    """Nachbarschaft ueber die WURZELN der Union-Find-Klassen.

    Wichtig: nicht ueber die rohen Endpunkt-Schluessel. Ein Pad, ein
    Null-Segment und zwei zusammenfallende Endpunkte sind derselbe
    Knoten; wer hier die rohen Schluessel nimmt, bekommt einen Graphen,
    in dem kein Pad an irgendeiner Bahn haengt.
    """
    adj = {}
    for i, (a, b, _w, _l, _art, _o) in enumerate(g.kanten):
        if i == ohne:
            continue
        ra, rb = g.find(a), g.find(b)
        adj.setdefault(ra, []).append(rb)
        adj.setdefault(rb, []).append(ra)
    return adj


def _erreichbar(adj, start):
    gesehen = set(start)
    stapel = list(start)
    while stapel:
        k = stapel.pop()
        for n in adj.get(k, ()):
            if n not in gesehen:
                gesehen.add(n)
                stapel.append(n)
    return gesehen


def kantenstroeme(g, quellen, senken, deckel, gruppen=None):
    """Strom je Kante: Summe der Senken, die ueber sie laufen MUESSEN
    oder KOENNEN, gedeckelt auf die Vertragszusage.

    Fuer jede Kante wird sie entfernt und gefragt, welche Senken dann von
    der Quelle abgeschnitten sind (die muessen hindurch) bzw. welche
    ueber die Kante auf einem anderen Weg noch erreichbar waeren (die
    KOENNEN hindurch, wenn sich der Strom auf mehrere Pfade teilt -- das
    wird konservativ voll gezaehlt).

    `gruppen` = {name: (menge_von_(ref,pad), gesamtstrom)}: Pads, die sich
    EINEN Strom teilen (die zwei parallelen Kontakte des
    Leistungssteckers). Erreicht eine Kante mehrere Mitglieder, zaehlt
    hoechstens der Gruppenwert. Ohne diese Klammer bekaeme der gemeinsame
    Zulauf zu einem zweikontaktigen Stecker die doppelte Durchleitung.
    """
    gruppen = gruppen or {}
    wurzeln = set(g.find(q) for q in quellen)
    # Mehrere Pads koennen auf DENSELBEN Knoten fallen (Buchse und Stift
    # des Leistungssteckers sitzen Pad auf Pad) -- deshalb je Knoten eine
    # Liste, nicht ein Wert; sonst verschwaende ein Pad stillschweigend.
    ziele = {}
    for p, I in senken.items():
        if I > 0:
            ziele.setdefault(g.find(p), []).append((p, I))
    zu_gruppe = {}
    for name, (mitglieder, _cap) in gruppen.items():
        for m in mitglieder:
            zu_gruppe[("PAD",) + tuple(m)] = name

    out = []
    for i, (a, b, w, L, art, ort) in enumerate(g.kanten):
        ra, rb = g.find(a), g.find(b)
        if ra == rb:
            out.append(0.0)
            continue
        adj = _nachbarn(g, ohne=i)
        von_q = _erreichbar(adj, wurzeln)
        von_a = _erreichbar(adj, [ra])
        von_b = _erreichbar(adj, [rb])
        I = 0.0
        gruppen_summe = {}
        for z, eintraege in ziele.items():
            if z in von_q:
                # Ohne diese Kante noch erreichbar -- sie liegt trotzdem
                # auf einem Parallelpfad, wenn beide Kantenenden Quelle
                # UND Ziel sehen. Dann konservativ voll zaehlen.
                if not ((ra in von_q and z in von_b)
                        or (rb in von_q and z in von_a)):
                    continue
            for p, Iz in eintraege:
                name = zu_gruppe.get(p)
                if name is None:
                    I += Iz
                else:
                    gruppen_summe[name] = gruppen_summe.get(name, 0.0) + Iz
        for name, summe in gruppen_summe.items():
            I += min(summe, gruppen[name][1])
        out.append(min(I, deckel))
    return out


def ketten(g, stroeme):
    """Zusammenhaengende Gruppen ZU SCHMALER Kanten.

    Rueckgabe: [(laenge_mm, min_breite_mm, max_strom_a, ort), ...],
    absteigend nach Laenge. Zwei zu schmale Kanten gehoeren zur selben
    Kette, wenn sie einen Knoten teilen -- die fuer die Erwaermung
    massgebliche Laenge ist die der ganzen Kette.
    """
    # Toleranz 1 nm (1e-6 mm): das ist die Aufloesung, in der KiCad eine
    # Bahnbreite ueberhaupt speichern kann. Ohne sie meldet eine Bahn,
    # die auf genau die geforderte Breite gebracht wurde, sich selbst
    # als "zu schmal" -- ein Rundungsartefakt, kein Befund.
    schlecht = [i for i, (a, b, w, L, art, o) in enumerate(g.kanten)
                if stroeme[i] > 0 and w < erf_breite(stroeme[i]) - 1e-6]
    if not schlecht:
        return []
    knoten_kanten = {}
    for i in schlecht:
        a, b = g.find(g.kanten[i][0]), g.find(g.kanten[i][1])
        knoten_kanten.setdefault(a, []).append(i)
        knoten_kanten.setdefault(b, []).append(i)
    gesehen = set()
    gruppen = []
    for i in schlecht:
        if i in gesehen:
            continue
        stapel = [i]
        gruppe = []
        while stapel:
            j = stapel.pop()
            if j in gesehen:
                continue
            gesehen.add(j)
            gruppe.append(j)
            a, b = g.find(g.kanten[j][0]), g.find(g.kanten[j][1])
            for k in knoten_kanten[a] + knoten_kanten[b]:
                if k not in gesehen:
                    stapel.append(k)
        L = sum(g.kanten[j][3] for j in gruppe)
        w = min(g.kanten[j][2] for j in gruppe)
        I = max(stroeme[j] for j in gruppe)
        ort = g.kanten[gruppe[0]][5]
        arten = sorted(set(g.kanten[j][4] for j in gruppe))
        gruppen.append((L, w, I, ort, "+".join(arten)))
    gruppen.sort(reverse=True)
    return gruppen


# ------------------------------------------------------------------ Lauf
class _P(object):
    """Minimaler Punkt fuer den Selbsttest -- pcbnew-frei."""

    def __init__(self, x, y):
        self.x, self.y = x, y


def selbsttest():
    """Rechnet die Geometrie nach, auf der die Topologie beruht.

    WARUM DAS BEI JEDEM LAUF MITLAEUFT. `_kreuzung` und `_auf_strecke`
    entscheiden, WELCHE Kanten der Leitungsgraph ueberhaupt hat -- und
    damit, welcher Strom wo gemessen wird. Ein Fehler darin macht die
    Pruefung nicht laut, sondern STILL FALSCH: sie misst dann eine
    Topologie, die es auf der Platine nicht gibt (genau so ist der
    X-Kreuz-Fehler entstanden, s. baue_graph). Ein Gate, dessen
    Grundrechnung niemand nachprueft, ist kein Gate -- deshalb steht
    der Nachweis hier und laeuft vor jeder Messung, nicht in einem
    Bericht.
    """
    mm = 1000000
    faelle = [
        # X-Kreuz: zwei Bahnen kreuzen sich, kein Endpunkt beteiligt.
        # Das ist der am Motormodul gemessene Fall (Aufgabe D3).
        ((0, 0), (2, 2), (0, 2), (2, 0), (1.0, 1.0)),
        # Beruehrung nur am Endpunkt ist KEIN Kreuz -- sonst entstuenden
        # Null-Segmente an jeder normalen Ecke.
        ((0, 0), (2, 0), (2, 0), (2, 2), None),
        # Parallel, auch deckungsgleich: kein Schnittpunkt.
        ((0, 0), (2, 0), (0, 1), (2, 1), None),
        # Verlaengerungen wuerden sich treffen, die Strecken nicht.
        ((0, 0), (1, 0), (3, -1), (3, 1), None),
    ]
    for (a1, b1, a2, b2, erwartet) in faelle:
        got = _kreuzung(_P(a1[0] * mm, a1[1] * mm), _P(b1[0] * mm, b1[1] * mm),
                        _P(a2[0] * mm, a2[1] * mm), _P(b2[0] * mm, b2[1] * mm))
        if erwartet is None:
            if got is not None:
                raise AssertionError(
                    "Selbsttest _kreuzung: %s/%s x %s/%s sollte KEIN Kreuz "
                    "sein, geliefert %s" % (a1, b1, a2, b2, got))
        else:
            if got is None:
                raise AssertionError(
                    "Selbsttest _kreuzung: %s/%s x %s/%s sollte sich bei %s "
                    "kreuzen, geliefert None" % (a1, b1, a2, b2, erwartet))
            if (abs(got[0] - erwartet[0] * mm) > 1000
                    or abs(got[1] - erwartet[1] * mm) > 1000):
                raise AssertionError(
                    "Selbsttest _kreuzung: erwartet %s mm, geliefert "
                    "(%.4f|%.4f) mm" % (erwartet, got[0] / 1e6, got[1] / 1e6))
    # _beruehrung: zwei parallele Bahnen, deren Kupfer sich seitlich
    # ueberlappt, sind EIN Leiter -- die am Motormodul gemessene Lage
    # (1,335 mm neben 0,400 mm in 0,743 mm Abstand) muss greifen, eine
    # Lage weiter auseinander nicht.
    if _beruehrung((0, 0), (10 * mm, 0), int(1.335 * mm),
                   (0, 743000), (10 * mm, 743000), int(0.400 * mm)) is None:
        raise AssertionError(
            "Selbsttest _beruehrung: 1,335 mm und 0,400 mm in 0,743 mm "
            "Abstand ueberlappen (0,667 + 0,200 = 0,867) -- nicht erkannt")
    if _beruehrung((0, 0), (10 * mm, 0), int(0.250 * mm),
                   (0, 743000), (10 * mm, 743000), int(0.250 * mm)) is not None:
        raise AssertionError(
            "Selbsttest _beruehrung: zwei 0,250-mm-Bahnen in 0,743 mm "
            "Abstand beruehren sich NICHT (0,125 + 0,125 = 0,250)")
    # _auf_strecke: T-Abzweig ja, Endpunkt nein, daneben nein.
    for (p, erwartet) in (((1, 0), True), ((0, 0), False), ((1, 1), False)):
        got = _auf_strecke(p[0] * mm, p[1] * mm, 0, 0, 2 * mm, 0)
        if got != erwartet:
            raise AssertionError(
                "Selbsttest _auf_strecke: %s sollte %s sein, geliefert %s"
                % (p, erwartet, got))
    # IPC-2221 gegen einen von Hand nachgerechneten Punkt: 1,00 mm bei
    # 1 oz und 20 K traegt 3,24 A. Faellt jemand ueber die Konstanten
    # her, wird DAS hier rot, nicht erst eine Platine.
    if abs(erf_breite(3.24) - 1.0) > 0.01:
        raise AssertionError(
            "Selbsttest erf_breite: 3,24 A sollten 1,00 mm brauchen, "
            "geliefert %.3f mm" % erf_breite(3.24))


def main(board_pfad, spec_pfad):
    selbsttest()
    spec = importlib.import_module(spec_pfad)
    board = pcbnew.LoadBoard(board_pfad)
    plan = pad_stroeme(spec)

    # Ein Netz mit eigener Gussflaeche waere von diesem Modell nicht
    # erfasst (der Guss verbindet Pads ohne Bahn). Lieber laut abbrechen
    # als still das Falsche messen.
    gegossen = set(z.GetNetname() for z in board.Zones()
                   if not z.GetIsRuleArea())

    fehler = 0
    print("%-13s %7s %7s %9s %9s  %s"
          % ("Netz", "I_max", "Kanten", "noetig_mm", "min_mm", "Urteil"))
    for netz in sorted(plan):
        quellen_pads, senken_pads, deckel, gruppen = plan[netz]
        vorhanden = set()
        for f in board.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() == netz:
                    vorhanden.add((f.GetReference(), p.GetPadName()))
        if not vorhanden:
            print("  ! %-14s kein Pad dieses Netzes auf der Platine "
                  "(Netzname falsch?)" % netz)
            fehler = 1
            continue
        if netz in gegossen:
            print("  ! %-14s hat eine Gussflaeche -- dieses Modell "
                  "rechnet nur mit Bahnen und Vias" % netz)
            fehler = 1
            continue
        # Deklaration gegen die Platine halten: ein Pad, das die Platine
        # hat und die Deklaration nicht kennt, bekaeme stillschweigend
        # Strom 0. Genau so entsteht eine Pruefung, die nichts prueft.
        deklariert = set(quellen_pads) | set(senken_pads)
        fehlend = vorhanden - deklariert
        if fehlend:
            print("  ! %-14s nicht deklarierte Pads: %s" %
                  (netz, ", ".join("%s.%s" % p for p in sorted(fehlend))))
            fehler = 1
            continue

        g, _pads = baue_graph(board, netz)
        if not g.kanten:
            print("  ! %-14s keine Bahnsegmente gefunden" % netz)
            fehler = 1
            continue
        quellen = [("PAD", r, p) for (r, p) in quellen_pads]
        senken = {("PAD", r, p): I for (r, p), I in senken_pads.items()}
        # Jede Senke muss die Quelle ueberhaupt sehen -- sonst ist der
        # Graph unvollstaendig (fehlende Via-Anbindung) und jede
        # Strommessung darauf waere Unsinn.
        adj = _nachbarn(g)
        erreichbar = _erreichbar(adj, [g.find(q) for q in quellen])
        lose = [s for s, I in senken.items()
                if I > 0 and g.find(s) not in erreichbar]
        if lose:
            print("  ! %-14s von der Quelle aus nicht erreichbar: %s" %
                  (netz, ", ".join("%s.%s" % (s[1], s[2]) for s in lose)))
            fehler = 1
            continue

        stroeme = kantenstroeme(g, quellen, senken, deckel, gruppen)
        i_max = max(stroeme) if stroeme else 0.0
        noetig = erf_breite(i_max)
        min_breite = min(g.kanten[i][2] for i in range(len(g.kanten))
                         if stroeme[i] >= i_max - 1e-9)
        gruppen = ketten(g, stroeme)
        zeilen = []
        urteil = "OK"
        for (L, w, I, ort, art) in gruppen:
            grenze = kurzhals_grenze(I, w)
            rot = L > grenze
            if rot:
                fehler = 1
                urteil = "ROT"
            zeilen.append(
                "  -> %-9s %-8s %.3f mm lang, %.3f mm breit bei %.2f A "
                "(noetig %.3f mm, Kurzhals-Grenze %.3f mm) bei (%.1f|%.1f)"
                % ("ROT" if rot else "OK (kurz)", art, L, w, I,
                   erf_breite(I), grenze, ort[0], ort[1]))
        print("%-13s %7.3f %7d %9.3f %9.3f  %s"
              % (netz, i_max, len(g.kanten), noetig, min_breite,
                 urteil if urteil == "ROT" else
                 ("OK" if not gruppen else "OK (nur kurze Haelse)")))
        for z in zeilen:
            print(z)

    print("\nZusage: %.1f A je Modul, %.1f A Stapel-Durchleitung, "
          "%.1f A je Kanal (stack_spec.STROMBUDGET)"
          % (BUDGET["modul_gesamt_a"], BUDGET["stapel_durchleitung_a"],
             BUDGET["kanal_a"]))
    return fehler


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Aufruf: strombelastung.py <board.kicad_pcb> <spec_modul>")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))

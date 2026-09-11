"""Platinenbeschreibung des Motormoduls (v2.1): Umriss, Lochbild, Platzierung.

Gelesen von tools/pcb/geometry.py (Pruefung), tools/pcb/build.py
(Aufbau) und tools/pcb/netclasses.py (Bahnbreiten). Bewusst OHNE
KiCad-Abhaengigkeit -- `python3 tools/pcb/geometry.py spec_motor` muss
ohne pcbnew laufen.

--- v2.1 (Aufgabe C1, 2026-09-10/11): Klemme an die Kante --------------
Der Vertrag ist wieder gewachsen (82x73 statt 75x65, s. stack_spec.py),
und diese Datei zieht die Platzierung auf die neuen Pflichtzonen
(KLEMMENZONE, RANDPAD_ZONE) nach:

  * J5 (die Motorklemme) verlaesst die Luecke zwischen den Stapelreihen
    (Audit-Befund B1 -- sie sass dort vollstaendig im PICO_SCHATTEN) und
    zieht kantenbuendig in KLEMMENZONE, gedreht 180 Grad (die groessere
    Haelfte der MKDS-3-Bauform zeigt zur Kante, R1). J3 (Notaus) BLEIBT
    am linken Rand, ruckt aber innerhalb der "Notaus"-Gruppe nach unten
    (mehr Abstand zu C17-19, Audit-Befund W2).
  * J95/J96 (Randpads) wechseln von B.Cu/waagrecht auf F.Cu/senkrecht
    (RANDPAD_ZONE, Audit-Befund K4) -- Drehung 90 statt Spiegelung.
  * Die Versorgungszelle wandert um dx=+2,10 mm nach Osten (Audit-Fund
    dieser Aufgabe: der Landepunkt-Spiegel von stapel_links wanderte
    mit dem Boardwachstum in ihren alten Platz).
  * Das MCU-Nest ist NICHT mehr komplett "verbatim": U100/U102/U103/
    C14/C16 ("obere Gruppe") wandern um dy=-3,70 mm, weil derselbe
    Boardwachstum-Effekt den Landepunkt-Spiegel von stapel_rechts in
    ihre alte Lage schob. R100/R101/R102/R104/R105/C100/C101/U101/R13
    bleiben unangetastet. /ID0 und /ID1 (die einzigen Vorverdrahtungen,
    die die "obere Gruppe" mit dem unbeweglichen Rest verbinden) sind
    ENTFERNT -- s. PRE_TRACKS-Kommentar dort. Ebenso entfernt: die
    gesamte Hand-Vorverdrahtung der Motorstufe (Haelse, /Out1, /Out2,
    /+24V, /VCP/CPH/CPL) -- ihre Zielklemme (J5) ist umgezogen, und ihre
    Ostgassen-Kalibrierung gegen die frozen J105-Kontakte vertraegt
    _MOTOR_DX=0 nicht mehr unveraendert. Beides bleibt fuer Aufgabe D.
  * Alle Zahlen und Rot-Nachweise: .superpowers/sdd/
    2026-09-07-picostack-v2/task-v21c1-report.md.

v2-NEUAUFLAGE (Aufgabe 7). Der Vertrag ist gewachsen (75x65 statt
64x60, zwei 1x20-Stapelreihen statt einem 2x20-Block, eine eigene
Versorgungszelle je Modul, 22 Randpads) UND der Schaltplan hat sich
geaendert (Q1/R11/R12/D1(TVS)/C12 sind weg, ersetzt durch die
Versorgungszelle J90/Q90/R90/R91/D90/U90/C90/C91/D91; J100 ist jetzt
nur noch die LINKE Stapelreihe, J105 kommt als rechte dazu; J95/J96
realisieren die Randpad-Reihe). Diese Datei ist deshalb NEU GERECHNET,
nicht aus v1 kopiert -- Herleitung im Bericht zu Aufgabe 7.

WAS AUS v1 UEBERNOMMEN IST (mit Herleitung, warum das sicher ist).
Das MCU-Nest (U100/U101/U102/U103, ihre Abblockung/Kennwiderstaende,
und die Notaus-Kette J3/R16-19/U3/U4/U5/U6/U7) behaelt seine INNERE
Geometrie -- die zueinander gehoerenden Bauteile ruecken NUR gemeinsam
(ein einziger dx=-1.0 fuer die U100/U101-Spalten; die Notaus-Kette
bleibt auf ihren alten Koordinaten, weil sie x < 27 nie verliess).
Grund: PRE_TRACKS unten ist die hart erkaempfte Nest-Vorverdrahtung aus
Aufgabe 6 (SEL_OUT/NRST/3V3/FLASH_MODE/ID0/ID1 -- jede Route hat eine
Herleitung im Kommentar, warum es die einzige kreuzungsfreie ist). Ein
gemeinsamer Verschub aendert an den GASSEN zwischen den Bauteilen
nichts, PAD-Ziele (("PAD", ref, nummer)) loesen sich ohnehin aus der
GEBAUTEN Platine auf (build.pre_tracks()), nur die HANDKOORDINIERTEN
Zwischenpunkte sind hier um denselben Betrag verschoben.

WAS NEU GERECHNET IST. Der Grund: die zwei Stapelreihen (v2) laufen
SENKRECHT durch die Plattenmitte (x 28,06..33,16 und 45,84..50,94, y
1..51,8) -- eine Kante, die es in v1 nicht gab (dort sass der
2x20-Block als Querbalken oben, die Nest-Spalten reichten bis x=32,9
OHNE etwas dahinter zu verlieren). In v2 wuerde die alte Spalte 4 des
Nests (C15/R15/R10/R21, x bis 32,9) mit stapel_links kollidieren; sie
zieht deshalb in eine eigene Zeile (Zeile 4) unterhalb der ersten drei.
Ebenso reicht die alte Notaus-Zeile (U3/U6/U7 bei x 27,5..38,2) in
stapel_links hinein -- sie wird auf drei kompaktere Zeilen umgelegt
(R16-19 / U3+U6+U7 / U4+U5), die alle x <= 27 bleiben.

Der 24-V-Strang (U1, C9/C10/C11) sitzt WEITERHIN in der Luecke
zwischen den beiden Stapelreihen (x 33,16..45,84) -- das ist zulaessig,
weil die Bauhoehe dort (0805-Kondensatoren, TSSOP-Waermepad) weit unter
der Steckhoehe des Pico bleibt (8,5 mm laut STECKER_STAPEL) UND weil
diese y-Lage (18,9..29) ausserhalb von stack_spec.ANTENNE_FREI liegt
(y 42,9..51,9). Die alte Vorverdrahtung fuer diesen Strang (CPH/CPL/
VCP/Out1/Out2/+24V-Aeste) ist NICHT uebernommen: sie war an Q1/D1/die
alte J5-Lage gebunden, die es alle nicht mehr gibt (Q1/D1 entfallen,
J5 zieht in die rechte Spalte). Der Router bekommt diesen Strang frisch
im Wuerfelspiel -- s. Bericht, Dice-Loop-Protokoll.

DIE VERSORGUNGSZELLE (J90 Eingangsklemme -> Q90 P-Kanal-Verpolschutz,
Gate ueber R90/R91 aus /+24V, TVS D90 -> lokales /+24V, das den
Leistungsstecker UND U1 speist -> U90 K7805 -> /+5V_LOKAL -> D91
Schottky -> VSYS) sitzt kompakt rechts oben (x 51,54..72,64,
y 0,5..35,65) -- kurzer Weg zum Leistungsstecker (57,9..69,64,
43,72..49,82) darunter, Eingangsklemme als einziges Bauteil dieser
Zelle mit Kabelzugang (die vier Kleinteile Q90/R90/R91/D90/D91 haengen
nur an Kupfer, keine Aussenverbindung).

DIE KLEMMENKANTE (J5 Motor, J3 Notaus, J90 Versorgung) IST IN v2 KEIN
EINHEITLICHER STREIFEN MEHR. Grund: die 22 Randpads (J95/J96) belegen
bei y ~61..64,5 fast die GESAMTE nutzbare Breite (53,3 mm Kontaktlaenge
plus Hoefe, gegen 60 mm Sicherheitsabstand zwischen den M3-Freihalte-
kreisen) -- eine gebaute Konsequenz des Vertrags, keine Bauteilwahl
dieser Datei. J3 bleibt links (x <= 12, weit vor den Randpads). J90
sitzt rechts oben (Kabelzugang ueber die rechte Kante ist bei der
Gehaeusekonstruktion, Aufgabe 9, genauso gut wie ueber die untere). J5
(Motorklemme) passt unterhalb des Leistungssteckers NICHT mehr hinein
(der Streifen zwischen dessen Unterkante und der Randpad-Reihe ist
0,6..1,2 mm zu kurz fuer J5s 11,17 mm) -- sie sitzt stattdessen in der
Luecke zwischen den beiden Stapelreihen, unterhalb des Motortreiber-
Strangs. Das ist ein bewusst offener MECHANISCHER Punkt (die Flaeche
liegt unter dem eingesteckten Pico, dessen Steckhoehe mit J5s Bauhoehe
kollidieren kann) -- ausformuliert im PLACEMENT-Kommentar bei "J5" und
im Bericht zu Aufgabe 7.

WAERMEPFAD DES DRV8876 (U1). Wie in v1: RULE_AREAS legt unter dem
Treiber eine Regelflaeche an, die Bahnen und fremde Vias verbietet, den
Guss aber erlaubt -- an die neue U1-Lage angepasst (+-1 mm Rand um den
neuen Hof, wie in v1).

ANTENNE_FREI -- BINDENDE ZUSAGE. stack_spec.ANTENNE_FREI (29..50 x
42,9..51,9) ist der Streifen am Pico-Ende der Onboard-Antenne: auf der
Oberseite (der Seite, auf der der Pico steckt) darf dort WEDER ein
Bauteil-Hof NOCH Kupfer (Bahn, Via, Guss) liegen. Durchgesetzt auf
ZWEI Wegen:
  1. PLACEMENT: kein eigenes Bauteil dieser Datei hat einen Hof, der
     ANTENNE_FREI ueberlappt (tests/test_spec_motor.py rechnet das fuer
     JEDES Bauteil AUSSER den vier Vertragssteckern nach -- deren
     eigene Flaechen duerfen ANTENNE_FREI ueberlappen, weil sie selbst
     der Anker sind, in den der Pico steckt).
  2. RULE_AREAS: ein Eintrag auf F.Cu verbietet dort Bahnen, Vias UND
     Guss (build.rule_areas() traegt das als Sperrflaeche in die Platine
     UND in die DSN ein -- der Router haelt sich daran). Die bestehende
     Naht-Vermeidung (_naht_erlaubt, s.u.) liest RULE_AREAS bereits
     generisch (jeder Eintrag mit "vias" in `verbote` sperrt Naehte) --
     der neue Eintrag wirkt dort automatisch mit, ohne eigenen Code.

Fuer die B.Cu-Seite gilt die Regel NICHT (die Antenne sitzt auf dem
aufgesteckten Pico, nicht auf dieser Platine -- s. stack_spec.ANTENNE_FREI-
Kommentar); die Regelflaeche ist deshalb bewusst NUR auf F.Cu gesetzt.

RANDPADS (22 beschriftete Loetpads, stack_spec.RANDPADS): realisiert
durch ZWEI Bauteile aus dem Schaltplan -- J96 (1x04, 2x GND + 2x 3V3)
und J95 (1x18, alle 18 freien GPIO). Der Vertrag denkt sich die 22 Pads
als EINE durchgehende Reihe mit der Versorgung an BEIDEN Enden
("rahmt die GPIO-Strecke symmetrisch ein"); mit zwei GETRENNTEN
Steckerkoerpern ist das nicht buchstaeblich baubar (ein einzelnes
1x04-Bauteil hat vier STARR benachbarte Pins, es kann nicht gleichzeitig
an beiden Enden einer 46-mm-Reihe sitzen). Diese Datei setzt J96 deshalb
an den ANFANG der Reihe (das linke Ende) und J95 direkt danach -- beide
zusammen ergeben weiterhin EINE durchgehende 2,54-mm-Reihe aus 22 Pads
auf y = stack_spec.RAND_Y-naher Hoehe (s.u., warum nicht exakt RAND_Y),
nur mit der Versorgung einseitig statt beidseitig gerahmt. Elektrisch
macht das keinen Unterschied (beide GND-Pads sind dasselbe Netz, ebenso
beide 3V3-Pads); der Docstring-Kommentar von stack_spec.RANDPADS ist
insofern nicht woertlich erfuellt, aber der Zweck (jeder freie GPIO
bekommt sein eigenes beschriftetes Loetpad, Versorgung in Griffnaehe)
ist es. Offener Punkt fuer den Vertrag selbst, s. Bericht.

Y-LAGE DER RANDPADS: stack_spec.RAND_Y ist 63,0 (BOARD_H - 2,0) --
gerechnet fuer eine Reihe aus reinen PADS, ohne die Kante des echten
Steckerkoerpers zu beruecksichtigen. Der reale Hof eines
PinHeader_1x18/1x04 ragt 1,77 mm ueber die Pin-Achse hinaus; bei
y=63,0 reichte die Hofkante bis y=64,77 -- 0,27 mm UEBER die Platinen-
kante (BOARD_H=65, EDGE_CLEARANCE=0,5, also maximal y=64,5). RAND_Y_IST
unten korrigiert das um das Minimum (0,23 mm nach oben, y=62,73) --
die einzige Abweichung von einer Vertragszahl in dieser Datei, aus
genau diesem, nachrechenbaren Grund.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S       # noqa: E402
# Die Bahnbreiten kommen aus fertigung.py, nicht aus einer zweiten
# Zahl hier: die vorverdrahteten Leistungsstuecke muessen exakt so
# breit sein wie das, was autoroute.dsn_netzklassen() daran
# anschliesst -- und das liest dieselbe Datei. Zwei getrennte Kopien
# derselben Zahl waren im Vorlaeuferprojekt genau der Fehler.
import fertigung             # noqa: E402


class Platz:
    """Ein platziertes Bauteil (Kopie der Klasse aus spec_sockel.py).

    spec_sockel.py ist auf dem v1-Vertrag stehen geblieben (STECKER_POS
    ["stapel"]/PICO_POS/ANTENNE_SPERRBEREICH gibt es im v2-Vertrag nicht
    mehr -- das ist der offene Punkt, den tests/test_spec_sockel.py rot
    haelt, s. Aufgabenzettel "erwartete verbleibende Rot-Liste"). Ein
    Import von dort wuerde diese Datei an genau diesem Import zum
    Absturz bringen, bevor sie ueberhaupt ihre eigene, v2-gueltige
    Beschreibung aufbauen kann. Die Klasse selbst hat mit dem Vertrags-
    bruch nichts zu tun -- sie bleibt hier als eigene, identische Kopie,
    bis Aufgabe 7's Nachfolger (Sockelplatine v2) einen gemeinsamen,
    wieder importierbaren Ort dafuer schafft.
    """

    def __init__(self, ref, x, y, w, h, rot=0, tht=False, unten=False):
        self.ref, self.rot, self.tht, self.unten = ref, rot, tht, unten
        self.x, self.y, self.w, self.h = x, y, w, h

    def __repr__(self):
        return "Platz(%s, %.2f, %.2f, %.2fx%.2f, %d%s)" % (
            self.ref, self.x, self.y, self.w, self.h, self.rot,
            ", unten" if self.unten else "")


def _aus_vertrag(ref, flaeche, rot, tht, unten=False):
    """Ein Bauteil, dessen Lage der Vertrag festlegt.

    `flaeche` MUSS der Hof des Footprints sein, der wirklich gebaut wird
    -- also `S.HOF(footprint, pin1, drehung)` bzw. `S.HOEFE(...)`, nie
    ein von Hand gepflegtes Reservierungsrechteck.
    """
    x0, y0, x1, y1 = flaeche
    return Platz(ref, x0, y0, round(x1 - x0, 3), round(y1 - y0, 3), rot, tht,
                 unten)


# Referenz -> Vertragsplatz, von _vertragsstecker() gefuellt.
#
# WARUM DAS NOETIG IST (Fix-Runde 1 zu Aufgabe 7). steckerprobe.py hat
# bisher selbst geraten, welche Referenz an welchem Vertragsplatz sitzt
# -- ueber den FOOTPRINT-NAMEN. In v1 ging das auf, weil jeder Platz
# einen eigenen Footprint hatte. In v2 benutzen stapel_links UND
# stapel_rechts denselben Footprint (dieselbe 1x20-Buchse, nur um 180
# Grad gedreht): das Namensraten fand fuer BEIDE Plaetze BEIDE
# Referenzen und prueste J100 auch gegen stapel_rechts und J105 gegen
# stapel_links. Ergebnis waren acht Falschmeldungen mit einem Versatz
# von 17,78 mm -- exakt dem Reihenabstand, also gerade der Abstand zum
# jeweils FALSCHEN Platz.
# Die Zuordnung weiss nur die Beschreibung. Also sagt sie sie hier,
# statt sie erraten zu lassen.
VERTRAGSPLATZ = {}


def _vertragsstecker(ref, slot, tht, index=0, unten=False):
    """Eine Steckerhaelfte, ueber pin1 des Vertrags platziert.

    WARUM UEBER pin1 UND NICHT UEBER "flaeche" (Fix-Runde 1 zu Aufgabe 7).
    Der Vertrag ist eine Zusage an FREMDE Modulbauer, und zugesagt ist die
    Lage der KONTAKTE (`pin1` plus Raster), nicht die eines Hof-Rechtecks.
    Ein Dritter, der exakt nach `pin1` baut, muss auf unsere Platine
    passen -- deshalb ist pin1 die einzige maßgebliche Referenz.

    Die alte Fassung uebergab fuer die beiden Stapelreihen dagegen
    `STECKER_POS[slot]["flaeche"]`, also eine ZWEITE, von Hand gepflegte
    Zahl. build.place() legt die Hof-Ecke des echten Footprints auf die
    Ecke dieses Rechtecks: stimmte das Rechteck nicht mit dem echten Hof
    ueberein, wanderte das Kupfer um die halbe Differenz. Genau so sassen
    beide Stapelreihen des Motormoduls um (-0,78|+0,50) mm neben dem
    Vertrag (Herleitung bei stack_spec.FOOTPRINT_HOF).

    `S.HOF(...)` aus pin1 und Drehung zu rechnen macht das unmoeglich:
    die Platzierung haengt jetzt an derselben Quelle wie die Zusage. Es
    ist ausserdem genau das Muster, das J101..J104 hier immer schon
    richtig gemacht haben -- neu ist nur, dass die Stapelreihen es auch
    benutzen.
    """
    e = S.STECKER_POS[slot]
    fp = e["footprints"][index]
    VERTRAGSPLATZ[ref] = slot
    return _aus_vertrag(ref, S.HOF(fp, e["pin1"], e["drehung"]),
                        e["drehung"], tht, unten)


# --- Umriss, Lochbild, Regeln: alles aus dem Vertrag -----------------
BOARD_W = S.BOARD_W
BOARD_H = S.BOARD_H
CORNER_R = S.CORNER_R
M3_DRILL = S.M3_DRILL
M3_HOLES = S.M3_HOLES
M3_KEEPOUT = S.M3_KEEPOUT

COURTYARD_GAP = 0.6
EDGE_CLEARANCE = 0.5

# Das Motormodul ist ein MODUL: auf seine Oberseite druecken die Stifte
# eines verdreht aufgesteckten Aufbaus. Die Kupferregel des Vertrags
# gilt (steckerprobe.verdrehtprobe misst sie).
IST_MODUL = True

# --- Footprints (muessen zum Schaltplan passen; build.place meldet) --
FP_SKT_1X20 = "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical"
# Randpad-Reihen: eigene Footprints, Loetpads in EINER Reihe, immer
# GESPIEGELT auf die Rueckseite (s. RANDPAD_* unten und
# stack_spec.RAND_Y-Kommentar). Die Bibliotheks-Stiftleisten gehen nicht:
# die bedrahtete legt zwangslaeufig Kupfer auf F.Cu, die SMD-Variante
# versetzt ihre Pads abwechselnd um +-1,655 mm.
FP_RANDPAD_1X18 = "Randpads:Randpad_Reihe_1x18"
FP_RANDPAD_1X04 = "Randpads:Randpad_Reihe_1x04"
FP_HDR_1X04 = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
FP_SKT_1X02 = ("Connector_PinSocket_2.54mm:"
               "PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left")
FP_HDR_1X02 = ("Connector_PinHeader_2.54mm:"
               "PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left")
FP_SKT_2X02 = "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD"
FP_HDR_2X02 = "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD"
_C = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
_R = "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
_R1206 = "Resistor_SMD:R_1206_3216Metric"
_SOT353 = "Package_TO_SOT_SMD:SOT-353_SC-70-5"
_SMC = "Diode_SMD:D_SMC"

FOOTPRINTS = {
    # -- Vertragsstecker --
    "J100": FP_SKT_1X20, "J105": FP_SKT_1X20,
    "J101": FP_SKT_1X02, "J102": FP_HDR_1X02,
    "J103": FP_SKT_2X02, "J104": FP_HDR_2X02,
    # -- Randpads --
    "J95": FP_RANDPAD_1X18, "J96": FP_RANDPAD_1X04,
    # -- MCU-Nest --
    "U100": "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
    "U101": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
    "U102": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
    "U103": _SOT353,
    "C14": _C, "C15": _C, "C16": _C, "C17": _C, "C18": _C, "C19": _C,
    "C100": _C, "C101": _C, "C13": _C,
    "R7": _R, "R8": _R, "R9": _R, "R10": _R, "R13": _R, "R15": _R,
    "R100": _R, "R101": _R, "R102": _R, "R104": _R, "R105": _R,
    "R20": _R, "R21": _R,
    # -- Notaus --
    "J3": FP_HDR_1X04,
    "R16": _R1206, "R17": _R1206, "R18": _R1206, "R19": _R1206,
    "U3": _SOT353, "U6": _SOT353, "U7": _SOT353,
    "U4": "Optocoupler_PC817:PC817_SMT_Gullwing",
    "U5": "Optocoupler_PC817:PC817_SMT_Gullwing",
    # -- Motorstufe --
    "U1": "DRV8876PWPR:IC_DRV8876PWPR",
    "C9": _C, "C10": _C, "C11": _C,
    "R5": _R,
    "J5": ("TerminalBlock_Phoenix:"
           "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal"),
    # -- Versorgungszelle --
    "J90": ("TerminalBlock_Phoenix:"
            "TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal"),
    "Q90": "Package_TO_SOT_SMD:TO-252-3_TabPin2",
    "R90": _R, "R91": _R,
    "D90": _SMC, "D91": _SMC,
    "U90": "Converter_DCDC:Converter_DCDC_RECOM_R-78B-2.0_THT",
    "C90": "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
    "C91": _C,
}

# --- Platzierung -----------------------------------------------------
# Vertragsteile ausgerechnet; die Buchsen (J101/J103) mit der
# VERTRAGSFLAECHE als Reservierung waere falsch -- jede Haelfte wird
# mit ihrem EIGENEN Hof am selben Kontaktanker platziert (s. Kommentar
# bei spec_sockel.PLACEMENT in v1, dieselbe Begruendung gilt unveraendert).
_S = S.STECKER_POS

# --- Zwei starre Verschiebungen (Fix-Runde 2 zu Aufgabe 7) ------------
#
# Beide dienen EINEM Zweck: der Verdreh-Kupferregel des Vertrags (kein
# freiliegendes Kupfer naeher als LANDE_SPERRRADIUS = 1,5 mm an einem
# Punkt aus LANDEPUNKTE_VERDREHT()). Die Regel konnte vorher niemand
# sehen, weil steckerprobe.py eine Stufe davor abbrach.
#
# Die Landepunkte liegen auf den Spiegelbildern der Steckerkontakte,
# also auf zwei senkrechten Spalten: x = 75 - 48,39 = 26,61 (Spiegel von
# stapel_rechts) und x = 75 - 30,61 = 44,39 (Spiegel von stapel_links).
# Genau an diesen beiden Spalten endete bisher Kupfer.
#
# WARUM STARR UND NICHT BAUTEILWEISE: eine bauteilweise Korrektur haette
# die Vorverdrahtung zerrissen -- jede Bahn, die zwei verschobene Teile
# unterschiedlich weit mitnimmt, braucht neue Zwischenpunkte und neue
# Abstandsrechnungen. Verschiebt man dagegen einen ganzen Block samt
# seiner Bahnen um DENSELBEN Betrag, bleiben alle Abstaende INNERHALB des
# Blocks unveraendert gueltig; nachzurechnen ist nur noch der Rand zu
# dem, was stehen bleibt. Darum unten `_m(...)` an jeder betroffenen
# x-Koordinate der Motorstufe -- auch in PRE_TRACKS und PRE_VIAS.
#
# _NEST_DX GIBT ES NICHT MEHR -- und das ist der interessante Teil.
#
# Der erste Anlauf wollte das ganze MCU-Nest 1,74 mm nach Westen
# schieben (C14/C16 hatten 0,39 mm Abstand zur Landespalte x = 26,61,
# bei R9/R20 lag der Landepunkt IM Pad). Das ist nachgerechnet
# UNMOEGLICH, weil das Nest zwischen ZWEI Landezonen eingeklemmt ist:
#
#   * x = 26,61  -- Spiegel von stapel_rechts (75 - 48,39)
#   * x = 12,50 und 9,96 bei y = 16,96/19,50 -- Spiegel des
#     LEISTUNGSsteckers (75 - 62,50 bzw. 75 - 65,04). Genau in der Hoehe
#     der obersten Nestzeile.
#
# Damit bleibt fuer Kupfer der obersten Zeile nur das Band
# 12,50 + 1,5 = 14,00 bis 26,61 - 1,5 = 25,11, also 11,11 mm. Gebraucht
# haette diese Zeile:
#     U100-Hof >= 13,76 (seine Westpads muessen von 12,50 wegbleiben)
#   + 7,70 Hofbreite + 0,60 COURTYARD_GAP
#   = C14-Hof >= 22,06 -- waehrend C14s Ostpad hoechstens bei
#     Hof 21,60 landen darf. Fehlbetrag 0,46 mm, bei JEDER Verschiebung.
# Der Versuch bestaetigte das praktisch: nach -1,74 mm meldete die
# Steckerprobe statt C14/C16/R9/R20 pluetzlich SIEBEN U100-Pads.
#
# Geloest wird es deshalb NICHT durch Verschieben, sondern indem die
# vier Stoerenfriede schmaler bzw. weiter innen stehen (s. PLACEMENT):
# C14/C16 um 90 Grad gedreht (Kupfer reicht dann nur noch 1,57 statt
# 3,51 mm ueber die Hofkante), R7/R8/R9 und C13/R5/R20 in ihren Zeilen
# zusammengerueckt. KEIN vorverdrahtetes Bauteil bewegt sich dabei --
# die Nest-Vorverdrahtung haengt an U100/U102/U103/U101/R100/R101/
# R102/R13, und die stehen alle still.

# _MOTOR_DX: v2.1 (Aufgabe C1) setzt dies auf 0,0 -- beide Gruende fuer
# den alten Wert (-0,50) sind entfallen.
#
#   (1) Der alte Zweck war, U1 1,74 mm Luft zum Landepunkt-Spiegel von
#       stapel_links zu verschaffen -- der sass in v2 (BOARD_W=75) bei
#       x=44,39. Mit v2.1s BOARD_W=82 liegt dieser Spiegel jetzt bei
#       x=82-30,61=51,39, weit oestlich der Motorstufe (die bei x<=43,4
#       endet) -- U1/C9/C10/C11 beruehren ihn nicht mehr. Der NEUE
#       Landepunkt-Nachbar der Motorstufe ist der Spiegel von
#       stapel_RECHTS, x=82-48,39=33,61 -- dagegen reicht die NOMINELLE
#       (unverschobene) Lage bereits: U1 bei x=35,60 haelt 1,99 mm
#       Kupferkante-Abstand (verlangt 1,5), C9/C10/C11 liegen noch
#       weiter oestlich und damit noch klarer.
#   (2) Der andere Grund war J5 (0,45 mm gebraucht) -- J5 verlaesst
#       diese Luecke komplett (s. PLACEMENT["J5"], jetzt in
#       KLEMMENZONE) und stellt hier keine Anforderung mehr.
#
# Die Hand-Vorverdrahtung dieser Aufgabe (Haelse an U1-10/11, /Out2,
# /+24V, /VCP/CPH/CPL) haengt NICHT mehr an _MOTOR_DX -- sie ist mit
# dieser Aufgabe entfernt (s. PRE_TRACKS/RULE_AREAS-Kommentar dort):
# sie war in 42 Wuerfellaeufen (Aufgabe 7) gegen die ALTE
# Ostgassen-Geometrie (Naehraster, J105-Padkante) auf 0,02..0,23 mm
# genau kalibriert; _MOTOR_DX=0 zieht diese Kalibrierung um 0,50 mm
# zurecht und wuerde mehrere dieser Reserven negativ machen (z. B. lief
# eine /+24V-Rueckseitenspur nach der alten Rechnung bis x=46,80 --
# INNERHALB des frozen J105-Hofs, der bei x=46,62 beginnt). Eine so eng
# austarierte Vorverdrahtung neu zu kalibrieren braucht denselben
# Wuerfel-Prozess, der sie erzeugt hat (Aufgabe 7s Dice-Loop) -- das ist
# Aufgabe D, nicht C1. S. Bericht, Abschnitt Vorverdrahtung.
_MOTOR_DX = 0.0


def _m(x):
    """x-Koordinate in der Motorstufe (mit _MOTOR_DX verschoben)."""
    return round(x + _MOTOR_DX, 3)


PLACEMENT = {
    # -- Vertragsstecker: ausgerechnet, nicht abgeschrieben --
    # ALLE SECHS gehen jetzt ueber _vertragsstecker(), also ueber pin1
    # (Begruendung dort). Vorher zogen J100/J105 ihre Lage aus
    # STECKER_POS[...]["flaeche"] -- die zweite Quelle, an der sich der
    # (-0,78|+0,50)-mm-Versatz eingeschlichen hatte.
    "J100": _vertragsstecker("J100", "stapel_links", True),
    "J105": _vertragsstecker("J105", "stapel_rechts", True),
    "J101": _vertragsstecker("J101", "kette", False, index=0),
    "J102": _vertragsstecker("J102", "kette", False, index=1, unten=True),
    "J103": _vertragsstecker("J103", "leistung", False, index=0),
    "J104": _vertragsstecker("J104", "leistung", False, index=1, unten=True),

    # -- MCU-Nest, "OBERE GRUPPE" (v2.1, Aufgabe C1): NUR U100/U102/U103/
    #    C14/C16 STARR um dy=-3.70 mm (nach NORDEN) verschoben.
    #
    #    WARUM UEBERHAUPT VERSCHOBEN, ENTGEGEN "Nest bleibt verbatim".
    #    v2.1 spiegelt STECKER_POS["leistung"]s vier Kontakte an den
    #    GEWACHSENEN BOARD_W/BOARD_H -- der Landepunkt wanderte dadurch
    #    von (9,96/12,50 | 16,96/19,50) auf (16,96/19,50 | 24,96/27,50),
    #    also GENAU IN dieses Nest hinein (vorher lag er 7 bzw. 8 mm
    #    davor). Rot-Nachweis (ohne diese Verschiebung, gemessen mit
    #    S.LANDEPUNKTE_VERDREHT()): U100 nur 1,46 mm, U102 0,00 mm
    #    (Landepunkt LIEGT im Hof), U103 0,10 mm vom naechsten Landepunkt
    #    -- verlangt sind 1,5. Das ist keine Bauteilwahl dieser Aufgabe,
    #    sondern eine unmittelbare Folge von Aufgabe Bs BOARD_W/H-
    #    Wachstum, die dort nicht gegen den BESTEHENDEN Nest-Grundriss
    #    geprueft wurde.
    #
    #    WARUM NUR DIESE FUENF UND NICHT DAS GANZE NEST. R100/R101/R102/
    #    R104/R105/C100/C101/U101 verletzen die Regel selbst NICHT (naechste
    #    Landepunkt-Distanz >= 4,7 mm, weit ueber 1,5) -- ihre einzige
    #    Beziehung zur Verletzung ist die Vorverdrahtung zu U100 (/ID0,
    #    /ID1, 3V3-Stummel). Ein erster Versuch verschob sie MIT (um
    #    dieselben 0,45/90-Grad-Winkel zu erhalten) -- das riss aber eine
    #    NEUE Kollision auf: R101/R105 sitzen in DERSELBEN Spalte wie R13
    #    (x=8,30..12,10 gegen 8,40..12,10, motor-only, NICHT Teil dieser
    #    Gruppe), und eine Verschiebung um 3,70 mm schob sie direkt in
    #    R13 hinein (Rot-Nachweis: geometry.check_all() meldete
    #    "Ueberlappung R101/R13" und "Ueberlappung R105/R13"). R100/R104
    #    (Spalte x=4,00..7,70, eine Spalte weiter westlich) waeren nicht
    #    betroffen gewesen -- aber R101/R105 schon, und eine Gruppe laesst
    #    sich nicht spaltenweise unterschiedlich verschieben, ohne ihre
    #    eigene 0,6-mm-Zeilenteilung zu zerreissen.
    #
    #    Geloest wird das NICHT durch eine kompliziertere Teilverschiebung,
    #    sondern indem /ID0 und /ID1 (die einzigen beiden Netze, die U100
    #    mit diesem unbeweglichen Teil des Nests verbinden) aus der
    #    Vorverdrahtung entfernt werden -- s. PRE_TRACKS-Kommentar dort.
    #    R100/R101/R102/R104/R105/C100/C101/U101/R13 bleiben dadurch
    #    VOLLSTAENDIG unveraendert (verbatim im woertlichen Sinn); nur
    #    U100/U102/U103/C14/C16 wandern.
    #
    #    dy=-3,70 ist die kleinste Verschiebung, mit der U102 (der
    #    schaerfste Fall, 0,00 mm) auf >= 1,5 mm kommt (rechnerisch reicht
    #    3,54 mm; 3,70 laesst 0,16 mm Reserve). Nachgerechnet bleiben alle
    #    Abstaende zu NICHT verschobenen Nachbarn positiv: Kettenstecker
    #    (Hof endet y=7,17) haelt zu U100 (neu y=12,80) 5,63 mm; U101/
    #    C100/C101/R102 (unveraendert, x <= 12,10) ueberlappen U100/U102/
    #    U103 (x >= 14,00) in x nie, unabhaengig von y.
    "U100": Platz("U100", 14.00, 12.80, 7.70, 7.00, 0, False),
    # C14/C16 um 90 Grad GEDREHT und nach Osten an die Nestkante
    # gerueckt (Verdreh-Kupferregel gegen die ALTE Landezone bei x=26,61,
    # s. Bericht zu Fix-Runde 2/Aufgabe 7 fuer die volle Herleitung). Die
    # x-Lage ist von jener Regel unveraendert (die neue Leistungs-
    # Landezone liegt bei x=16,96/19,50, weit westlich von C14/C16s
    # x=22,90 -- 6,47/3,57 mm Luft, s. Rot-Nachweis oben); nur y wandert
    # mit der "oberen Gruppe" um -3,70 mm.
    "C14": Platz("C14", 22.90, 12.00, 1.96, 3.76, 90, False),
    "C16": Platz("C16", 22.90, 16.40, 1.96, 3.76, 90, False),
    "U102": Platz("U102", 14.00, 20.80, 4.56, 2.50, 0, False),
    "U103": Platz("U103", 19.60, 20.80, 2.90, 2.20, 0, False),
    # R7/R8/R9 -- "UNTERE GRUPPE" (mit C13/R5/R20/C15/R15/R10/C17-19/R21),
    # STARR um dy=+0.90 mm (nach SUEDEN) verschoben. R7/R8 sind
    # UNVERDRAHTET (keine PRE_TRACKS-Referenz) und beide selbst
    # Landepunkt-Verletzer (0,75/0,70 mm statt 1,5, s. Rot-Nachweis oben)
    # -- sie brauchen nur 0,80 mm Sued-Versatz, um unter den Landepunkt
    # (y=27,50) zu ruecken; 0,90 mm laesst 0,10 mm Reserve. R9/C13/R5/R20
    # verletzten die Regel schon vorher nicht (2,21/3,72/3,70/4,25 mm),
    # wandern aber MIT, damit ihr 0,6-mm-COURTYARD_GAP-Abstand zu R7-9
    # exakt erhalten bleibt (reine Parallelverschiebung). C15/R15/R10 und
    # C17-19/R21 wandern aus demselben Grund kaskadierend mit (jede
    # dieser vier Zeilen sass vorher mit GENAU 0,60 mm Luft an der
    # naechsten -- ohne Mitverschiebung waere aus 0,60 mm entweder eine
    # Kollision oder eine unbegruendete Luecke geworden).
    "R7": Platz("R7", 13.00, 29.10, 3.70, 1.90, 0, False),
    "R8": Platz("R8", 17.30, 29.10, 3.70, 1.90, 0, False),
    "R9": Platz("R9", 21.60, 29.10, 3.70, 1.90, 0, False),
    "C13": Platz("C13", 12.80, 32.10, 3.76, 1.96, 0, False),
    "R5": Platz("R5", 17.30, 32.10, 3.70, 1.90, 0, False),
    "R20": Platz("R20", 21.60, 32.10, 3.70, 1.90, 0, False),

    # U101/C100/C101/R100/R101/R102/R104/R105/R13 -- UNVERAENDERT (s.
    # Kommentar bei "obere Gruppe" oben): keiner verletzt die Verdreh-
    # Klausel selbst, und eine Mitverschiebung riss eine neue Kollision
    # mit R13 auf. Woertlich aus v2 uebernommen.
    "U101": Platz("U101", 4.00, 21.00, 2.90, 2.20, 0, False),
    "C101": Platz("C101", 4.00, 24.20, 3.76, 1.96, 0, False),
    "R102": Platz("R102", 8.40, 24.20, 3.70, 1.90, 0, False),
    "C100": Platz("C100", 4.00, 27.10, 3.76, 1.96, 0, False),
    "R13": Platz("R13", 8.40, 27.10, 3.70, 1.90, 0, False),
    "R100": Platz("R100", 4.00, 30.00, 3.70, 1.90, 0, False),
    "R101": Platz("R101", 8.30, 30.00, 3.70, 1.90, 0, False),
    "R104": Platz("R104", 4.00, 32.90, 3.70, 1.90, 0, False),
    "R105": Platz("R105", 8.30, 32.90, 3.70, 1.90, 0, False),

    # Zeile 4 (unveraendert relativ, s. "untere Gruppe" oben).
    "C15": Platz("C15", 12.65, 34.66, 3.76, 1.96, 0, False),
    "R15": Platz("R15", 17.01, 34.66, 3.70, 1.90, 0, False),
    "R10": Platz("R10", 21.31, 34.66, 3.70, 1.90, 0, False),

    # Zeile 5 (unveraendert relativ, s. "untere Gruppe" oben).
    "C17": Platz("C17", 4.00, 37.22, 3.76, 1.96, 0, False),
    "C18": Platz("C18", 8.60, 37.22, 3.76, 1.96, 0, False),
    "C19": Platz("C19", 13.20, 37.22, 3.76, 1.96, 0, False),
    "R21": Platz("R21", 17.80, 37.22, 3.70, 1.90, 0, False),

    # -- Notaus, STARR um dy=+2.30 mm nach Sueden verschoben (v2.1,
    #    Audit-Befund W2: J3 sass mit genau 0,60 mm -- dem nackten
    #    COURTYARD_GAP-Minimum -- zu C17-19 UND zu R16-19 eingeklemmt,
    #    "eng ... unbequem" fuer den sicherheitsrelevanten Notaus-
    #    Steckverbinder). 0,90 mm davon sind die Kaskade der "unteren
    #    Gruppe" (die jetzt bei R21 endet, s.o.); die restlichen 1,40 mm
    #    sind die eigentliche Auflagen-Antwort -- die neue Luecke
    #    C17-19 -> J3 betraegt jetzt 2,06 mm (statt 0,60), mehr als
    #    das Dreifache des Minimums, wie vom Audit gefordert ("mehr waere
    #    hier angemessen"). Genutzt wird dabei ausschliesslich die durch
    #    Aufgabe B neu gewonnene Bodenhoehe (BOARD_H 65 -> 73 mm): U4/U5
    #    enden jetzt bei y=59,70, immer noch 1,10 mm vor KLEMMENZONE
    #    (y=60,80) und weit vor dem GEWANDERTEN M3-Freihaltequadrat der
    #    Bohrung (4|69) (Kante ab y=65,5 -- unrelevant geworden, s.
    #    stack_spec-Docstring). Kein PRE_TRACKS-Eintrag haengt an J3
    #    selbst; die U6-3/U7-3-GND-Stummel und die /NOTAUS-Vias (s.
    #    PRE_TRACKS/PRE_VIAS unten) wandern um denselben Betrag mit.
    "J3": Platz("J3", 0.50, 41.18, 11.16, 3.54, 90, True),
    "R16": Platz("R16", 0.50, 45.32, 4.56, 2.26, 0, False),
    "R17": Platz("R17", 5.66, 45.32, 4.56, 2.26, 0, False),
    "R18": Platz("R18", 10.82, 45.32, 4.56, 2.26, 0, False),
    "R19": Platz("R19", 15.98, 45.32, 4.56, 2.26, 0, False),
    "U3": Platz("U3", 0.50, 48.18, 2.90, 2.20, 0, False),
    "U6": Platz("U6", 4.00, 48.18, 2.90, 2.20, 0, False),
    "U7": Platz("U7", 9.00, 48.18, 2.90, 2.20, 0, False),
    "U4": Platz("U4", 0.50, 52.50, 10.90, 7.20, 0, False),
    "U5": Platz("U5", 12.00, 52.50, 10.90, 7.20, 0, False),

    # -- Motorstufe: in der Luecke zwischen den Stapelreihen
    #    (x 33,16..45,84), y < 42,9 -- ausserhalb ANTENNE_FREI und weit
    #    unter der 8,5-mm-Steckhoehe des Pico (0805/TSSOP-Bauhoehe) --
    "C11": Platz("C11", _m(35.60), 15.80, 3.76, 1.96, 0, False),
    "U1": Platz("U1", _m(35.60), 18.90, 7.80, 5.50, 0, False),
    "C10": Platz("C10", _m(36.40), 25.00, 1.96, 3.76, 90, False),
    "C9": Platz("C9", _m(39.00), 25.00, 1.96, 3.76, 90, False),

    # J5 -- Motorklemme, v2.1 (Aufgabe C1): zieht in KLEMMENZONE
    # (23,80..58,20 x 60,80..73,00), Kante unten (R1) -- loest Audit-
    # Befund B1 (die alte Lage, Runde 2 der v2-Fassung, saß VOLLSTAENDIG
    # im PICO_SCHATTEN, s. Bericht/Vertrag).
    #
    # DREHUNG 180, NICHT 0. Der reale Hof der Bauform
    # (TerminalBlock_Phoenix_MKDS-3-2-5.08, gemessen aus der
    # .kicad_mod-Datei: F.CrtYd (-3,04|-6,4)-(8,13|5,8), Kontakt 1 bei
    # (0|0), Kontakt 2 bei (5,08|0)) ist um die Kontaktachse ASYMMETRISCH
    # (6,40 mm auf der einen, 5,80 mm auf der anderen Seite) -- diese
    # Asymmetrie ist eine reale Bauform-Eigenschaft (Gehaeuse plus
    # Schraub-/Drahtzugang auf einer Seite), keine Zeichenwillkuer.
    # Dieselbe Konvention wie bei allen PT-1,5-Klemmen dieses Projekts
    # (J90, J5..J8 der Dimmer, s. dort): die GROESSERE Haelfte zeigt zur
    # Platinenkante ("Drahtoeffnung nach aussen", R1). Bei der PT-1,5-
    # Bauform faellt das mit Drehung 0 zusammen (ihre groessere Haelfte
    # liegt schon lokal auf +y); bei der MKDS-3-Bauform liegt die
    # groessere Haelfte lokal auf -y -- Drehung 180 dreht sie auf die
    # Suedseite (kantenbuendig), s. Rechnung unten.
    #
    #   Hof bei Drehung 180 (S.LAGE-Formel (px-fx,py-fy)):
    #     x-Bereich [px-8,13, px+3,04], y-Bereich [py-5,8, py+6,4]
    #   Gefordert: Hof-Suedkante (py+6,4) == BOARD_H (kantenbuendig,
    #     R1). Absichtlich OHNE EDGE_CLEARANCE-Marge: R1 verlangt
    #     ausdruecklich einen Klemmenkoerper buendig zur Kante, nicht
    #     0,5 mm davor -- das ist eine EXPLIZITE Ausnahme von der
    #     generischen Randregel, die dieselbe Rolle wie die
    #     Vertragsstecker-Ausnahme bei ANTENNE_FREI spielt (s.
    #     test_spec_motor.py, "geometry: check_all()"-Filter). Die
    #     generische Regel schuetzt vor abgeschnittenen Siebdruck-/
    #     Bestueckungsflaechen im Nutzen; eine Klemme, die genau dafuer
    #     gebaut ist, am Rand zu sitzen, ist keine solche Flaeche.
    #     -> py = 73,00 - 6,40 = 66,60
    #   Zentriert in KLEMMENZONE (Breite 11,17 mm Hof):
    #     x0 = 23,80 + (34,40-11,17)/2 = 35,415 -> px = 35,415+8,13
    #        = 43,545
    #
    # R5-MESSUNG (Kupferabstand zur Kante, Task-B-Bedenken): beide
    # Kontakte liegen lokal auf y=0, also bei Drehung 180 auf globalem
    # y = py = 66,60 -- 73,00-66,60 = 6,40 mm von der Kante. Padradius
    # (2,6 mm rund/roundrect) = 1,30 mm -> naechste Kupferkante 5,10 mm
    # von der Kante entfernt, weit ueber den geforderten 2,0 mm (R5
    # HAELT, mit 3,10 mm Reserve). Selbst in der UNGUENSTIGEREN
    # Alternativlesart (kleinere Haelfte, 5,8 mm, kantenbuendig) bliebe
    # die Kupferkante noch 4,50 mm von der Kante -- R5 haelt in JEDER
    # denkbaren Zuordnung von "vorne"/"hinten" bei dieser Bauform.
    "J5": Platz("J5", 35.415, 60.80, 11.17, 12.20, 180, True),

    # -- Versorgungszelle, rechts oben. v2.1: um dx=+2,10 mm nach OSTEN
    # verschoben (x 53,64..74,74 statt 51,54..72,64), y-Lagen sonst
    # UNVERAENDERT ("Versorgung behaelt ihre innere Anordnung", wie
    # gefordert).
    #
    # WARUM UEBERHAUPT VERSCHOBEN. Derselbe Mechanismus wie beim
    # MCU-Nest oben: der Landepunkt-Spiegel von stapel_links wanderte
    # durch Aufgabe Bs BOARD_W-Wachstum von x=44,39 (v2) auf x=51,39
    # (v2.1) -- direkt an den alten Zellenrand (x=51,54, nur 0,15 mm
    # Luft). D4 (Dimmer-Kanal-4-Diode, dieselbe Spalte, s.
    # spec_dimmer_basis.py) waere mit ihrem alten x=51,00 sogar
    # UEBERLAPPT worden (Landepunkt LIEGT im Hof). Rot-Nachweis (ohne
    # Verschiebung): R90/J90/D90/C90/U90/C91 je 0,00..0,15 mm statt
    # 1,5 mm; D4 (Dimmer) 0,00 mm.
    #
    # dx=+2,10 ist so gewaehlt, dass der LINKESTE Nachbar dieser Spalte
    # (D4 beim Dimmer, x=51,00) auf >= 1,5 mm Kupferkante kommt:
    # 51,00+2,10 = 53,10, Abstand zu 51,39 = 1,71 mm (0,21 mm Reserve).
    # Fuer die Motor-eigene Spalte (R90 bei 51,54) bleiben nach demselben
    # Versatz 2,15 mm Reserve. Nach OSTEN bleibt die Zelle klar von der
    # RANDPAD_ZONE (bzw. dem echten J95/J96-Hof, x ab 76,30) getrennt:
    # U90 (motor, breitester Nachbar) endet bei x=74,74, 1,56 mm Luft;
    # Q4 (Dimmer, s. dort) endet bei x=75,20, 1,10 mm Luft -- beide ueber
    # COURTYARD_GAP (0,6). Zum (ebenfalls gewachsenen, aber weiterhin
    # x < 74,5 bleibenden) rechten M3-Freihaltequadrat der Bohrung
    # (78|4) bleibt Q90 mit x1=73,34 unveraendert klar (K1, s. Vertrag/
    # Bericht) -- 1,16 mm Reserve statt der urspruenglichen 3,26 mm,
    # aber weiterhin positiv.
    "R90": Platz("R90", 53.64, 0.50, 3.70, 1.90, 0, False),
    "R91": Platz("R91", 57.94, 0.50, 3.70, 1.90, 0, False),
    "J90": Platz("J90", 53.64, 7.70, 8.00, 8.60, 0, True),
    "Q90": Platz("Q90", 62.24, 7.70, 11.10, 7.00, 0, False),
    "D90": Platz("D90", 53.64, 17.20, 9.80, 6.70, 0, False),
    "D91": Platz("D91", 64.10, 17.20, 9.80, 6.70, 0, False),
    "C90": Platz("C90", 53.64, 24.50, 8.50, 8.50, 0, True),
    "U90": Platz("U90", 62.74, 24.50, 12.00, 9.00, 0, True),
    "C91": Platz("C91", 53.64, 33.60, 3.85, 2.05, 0, False),

    # -- Randpads (RANDPADS-Realisierung, s. Moduldocstring). v2.1:
    # SEITENWECHSEL UND ACHSENWECHSEL (s. stack_spec.RANDPADS-Kommentar
    # und RANDPAD_ZONE). Die Reihe liegt jetzt SENKRECHT auf F.Cu, nahe
    # der rechten Kante, statt waagrecht auf B.Cu nahe der unteren.
    #
    # DREHUNG 90, `unten` ENTFAELLT (unten=False -- Standard). Der
    # Footprint bringt seine 18/4 Pads nativ in einer waagrechten Reihe
    # entlang der lokalen -x-Achse (Kontakt 1 bei lokal (0|0), Kontakt k
    # bei (-(k-1)*2,54|0)); bei Drehung 90 (S.LAGE-Formel
    # (px+fy,py-fx)) wird daraus eine SENKRECHTE Reihe, die mit
    # wachsendem k nach SUEDEN laeuft (globales y = py+(k-1)*2,54) --
    # exakt die "RAND_Y0 + i*RAND_RASTER"-Reihenfolge des Vertrags, ohne
    # dass irgendein Aufrufer die Zaehlrichtung umdrehen muesste. Der
    # Footprint-Docstring ("gehoert GESPIEGELT auf die Rueckseite") ist
    # damit VERALTET -- er beschreibt die v2-B.Cu-Lage; v2.1 braucht
    # keine Spiegelung mehr (RAND_LAYER ist jetzt F.Cu, derselbe wie der
    # native Footprint), s. Bericht, Bedenken.
    #
    # HOF-RECHNUNG (gemessen aus Randpad_Reihe_1x18/1x04.kicad_mod, nicht
    # geschaetzt): natives F.CrtYd ist x [-((n-1)*2,54+0,45), 0,45],
    # y [-1,3, 1,3] (Kontakt 1 im Ursprung). Bei Drehung 90 wird daraus
    # (S.LAGE angewendet auf die vier Eckpunkte):
    #   x-Bereich [px-1,3, px+1,3]              (Breite 2,60 mm)
    #   y-Bereich [py-0,45, py+(n-1)*2,54+0,45]  (Hoehe (n-1)*2,54+0,90)
    # mit (px,py) = globale Lage von Kontakt 1 dieses Teilstuecks.
    #
    # J96 (die 4 Versorgungspads) beginnt am ERSTEN Vertragsplatz
    # (px=RAND_X=77,60, py=RAND_Y0=9,83); J95 (die 18 GPIO) beginnt DIREKT
    # danach, am 5. Vertragsplatz (py=9,83+4*2,54=19,99) -- zusammen
    # exakt die 22 Positionen aus S.RANDPADS, ohne Luecke (dieselbe
    # "einseitig statt beidseitig gerahmt"-Abweichung vom Vertragstext
    # wie in v2, s. Moduldocstring oben und stack_spec.RANDPADS-Kommentar
    # -- elektrisch ohne Wirkung, beide GND- und beide 3V3-Pads sind
    # dasselbe Netz).
    #
    # ZONEN-PRUEFUNG (S.RANDPAD_ZONE = 75,60..79,60 x 8,56..64,44):
    # J96-Hof x[76,30, 78,90] y[9,38, 17,90]; J95-Hof x[76,30, 78,90]
    # y[19,54, 63,62] -- beide vollstaendig innerhalb der Zone (0,70 mm
    # Rand in x, 0,82 mm in y an beiden Enden). R5 (Kantenabstand):
    # 82,00-78,90 = 3,10 mm >= 2,0 mm.
    "J96": Platz("J96", 77.60 - 1.30, 9.83 - 0.45,
                 2.60, 3 * 2.54 + 0.90, 90, False),
    "J95": Platz("J95", 77.60 - 1.30, 19.99 - 0.45,
                 2.60, 17 * 2.54 + 0.90, 90, False),
}

# --- Pflicht-Kennzeichnung (stack_spec.LAYOUT_AUFLAGEN) --------------
# Pin-1-Marke neben Kontakt 1 von stapel_links (Pico-Pin 1, FLASH_TX) --
# der primaere Bezug, weil dort das Pico-Datenblatt selbst Pin 1 zaehlt.
# UNVERAENDERT: stapel_links' pin1 ist Vertrag (frozen), diese Marke
# haengt nicht an BOARD_W/H.
PIN1_MARKE = (25.50, 2.27)
# KLEMMEN_POS, v2.1 (Aufgabe C1): steckerprobe.kennzeichnungsprobe()
# verlangt y >= BOARD_H - 6,0 = 67,0 mm (frueher 59,0 bei BOARD_H=65).
# x=14,00 liegt in der Gasse zwischen dem M3-Freihaltequadrat der
# linken unteren Bohrung (4|69, Kante bis x=7,5) und KLEMMENZONE
# (Kante ab x=23,80) -- ausserhalb JEDER Klemmenreihe aller vier
# Boards (Dimmer4 fuellt die Zone lueckenlos aus, s. spec_dimmer_basis
# .py), also ein sicherer, board-unabhaengiger Platz. y=68,00 liegt
# innerhalb von KLEMMENZONE (60,80..73,00) und damit ueber der
# Reissleine; auf dem Motormodul ausserdem klar unterhalb von U4/U5
# (Hof endet y=59,70, 8,30 mm Luft).
KLEMMEN_POS = (14.00, 68.00)

# --- Waermepfad des DRV8876 -------------------------------------------
# U1-Hof plus 1 mm Rand, wie in v1 -- x wandert mit _MOTOR_DX mit
# (jetzt 0,0, s. dort), sonst laege die Waermeschutzflaeche neben dem
# Baustein, den sie schuetzen soll.
RULE_AREAS = (
    ("Waermepfad DRV8876", ("B.Cu",),
     (_m(34.60), 17.90, _m(44.40), 25.40), frozenset(("bahnen", "vias"))),

    # ANTENNE_FREI -- BINDEND (s. Moduldocstring): auf F.Cu (der Seite,
    # auf der der Pico steckt) weder Bahn noch Via noch Guss.
    ("Antennenfreiheit (Pico-Schatten)", ("F.Cu",), S.ANTENNE_FREI,
     frozenset(("bahnen", "vias", "guss"))),

    # Die alte "Naehtfrei in der DRV8876-Ausleitung"-Regelflaeche (v2,
    # Aufgabe 7) ist mit dieser Aufgabe ENTFERNT -- sie schuetzte einen
    # Rasterpunkt (45|21,25), den die JETZT ENTFERNTE Hand-Vorverdrahtung
    # (/VCP/CPH/CPL/Out2/+24V, s. PRE_TRACKS-Kommentar unten) fuer sich
    # brauchte. Ohne diese Vorverdrahtung ist die Sperre gegenstandslos;
    # Aufgabe D darf sie bei Bedarf aus ihrem eigenen Dice-Loop heraus
    # neu einfuehren, mit einer fuer die NEUE Ostgassen-Geometrie
    # gueltigen Rechnung.
)

# --- GND-Vorverdrahtung (nur das Nest; s. Moduldocstring) -------------
# Die 40 Stapel-Landepunkte sitzen in v2 auf ZWEI duennen 1x20-Spalten
# statt einem dichten 2x20-Block -- die Masseflaeche hat links und
# rechts jeder Spalte freien Guss, anders als beim 2x20-Block in v1
# (dort sass jedes GND-Pad zwischen zwei Signalpads UND vierzig Bahnen
# darunter). Ob das ohne Stummel auskommt, entscheidet der Dice-Loop
# (autoroute.py) empirisch; nur die NEST-Vorverdrahtung (SEL_OUT/NQ/
# NRST/3V3/FLASH_MODE/ID0/ID1 aus Aufgabe 6, um dx=-1,0 verschoben) ist
# hier uebernommen, weil sie an konkreten, nachgewiesen enge Gassen
# gebunden ist, die der Verschub der Nest-Spalten nicht veraendert.
_HALS = 0.40
# Leistungsbreite wie in fertigung.TRACK_POWER -- hier als eigene
# Konstante, weil die vorverdrahteten Leistungsstuecke dieselbe Breite
# tragen muessen wie das, was der Router daran anschliesst.
_LEISTUNG = fertigung.TRACK_POWER
# v2.1 (Aufgabe C1) -- die Hand-Vorverdrahtung der Motorstufe (Haelse
# an U1-10/11, /Out1, /Out2, /+24V, /VCP, /CPH, /CPL -- Aufgabe 7,
# 42 Wuerfellaeufe) ist HIER ENTFERNT, nicht nur "ein Stueck davon
# gekuerzt". Zwei unabhaengige Gruende, beide zwingend:
#
#   1. /Out1 und /Out2 enden auf J5-Pads -- J5 ist von der
#      Stapelluecke (y~29..41) in KLEMMENZONE (y 60,80..73,00)
#      gewandert. Der bisherige, in 45-Grad-Etappen fein austarierte
#      Weg (Escape -> Leistungsspur -> J5) ERREICHT die neue Klemme gar
#      nicht mehr; eine Fortsetzung waere eine LANGE Querverbindung ueber
#      ein voellig neues Kupferbild -- genau die Kategorie, die dieses
#      Projekt seit Aufgabe 7 ausdruecklich dem Router ueberlaesst
#      ("vorverdrahtet wird nur, was der Router grundsaetzlich nicht
#      kann").
#   2. /+24V, /VCP, /CPH, /CPL beruehren J5 nicht (sie bleiben bei U1/
#      C9/C10/C11), aber ihre Koordinaten sind auf 0,02..0,23 mm genau
#      gegen die ALTE Ostgasse kalibriert (U1-Ostpadkante vs. die
#      FROZEN J105-Kontaktreihe UND das alte 7,5-mm-Naehraster). Mit
#      _MOTOR_DX=0 (s. dort) laege der /+24V-Rueckseitenpunkt
#      (frueher _m(46,80)=46,30) jetzt bei x=46,80 -- INNERHALB des
#      J105-Hofs (beginnt bei x=46,62, frozen). Diese Vorverdrahtung
#      ohne den Dice-Loop neu zu kalibrieren, der sie erzeugt hat, waere
#      genau das Eyeballing, das Aufgabe 7 als Fehlerquelle identifiziert
#      hat ("drei separate Male ... Stunden gekostet").
#
# U1/C9/C10/C11 bleiben platziert (unveraendert, s. PLACEMENT, nur
# _MOTOR_DX geaendert) und sind DRC-frei erreichbar -- Aufgabe D
# verdrahtet die Motorstufe komplett neu, mit derselben Technik
# (Dice-Loop + Vorverdrahtungs-Gate) wie Aufgabe 7, gegen die NEUE
# Geometrie (laengerer Weg zu J5, neue Ostgassen-Masse gegen die frozen
# J105-Kontakte).
#
# Die NEST-Vorverdrahtung unten ist WOERTLICH aus Aufgabe 6/7
# uebernommen, nur um dy=-3,70 mm mitverschoben (s. PLACEMENT-Kommentar
# "obere Gruppe") -- eine reine Parallelverschiebung aendert an keinem
# Winkel oder Abstand innerhalb der Gruppe etwas.
PRE_TRACKS = (
    ("/SEL_OUT", "F.Cu", (("PAD", "U102", "1"), ("PAD", "U102", "2"))),
    ("/NQ", "F.Cu", (("PAD", "U102", "6"), ("PAD", "U102", "7"))),

    # Masse-Ausleitung fuer U100-5 (MCU-GND).
    ("GND", "F.Cu", (("PAD", "U100", "5"), (12.90, 15.975))),

    ("/NRST", "F.Cu", (("PAD", "U102", "3"), (13.50, 22.30)), 0.20),
    ("/NRST", "F.Cu", ((13.50, 22.30), (13.50, 16.625),
                       ("PAD", "U100", "6"))),

    # 3V3 U102-8 -> U103-5 auf der RUECKSEITE (Nordschneise frei
    # halten -- Herleitung wie in v1, nur um dy=-3,70 verschoben).
    ("3V3", "F.Cu", (("PAD", "U102", "8"), (17.68, 20.40))),
    ("3V3", "B.Cu", ((17.68, 20.40), (22.35, 20.40), (22.90, 20.95),
                     (22.90, 21.25))),
    ("3V3", "F.Cu", ((22.90, 21.25), ("PAD", "U103", "5"))),

    ("/FLASH_MODE", "F.Cu", (("PAD", "U102", "5"),
                             (17.68, 23.50), (18.68, 23.50),
                             (18.68, 20.65), (20.212, 20.65),
                             ("PAD", "U103", "1"))),

    ("/SEL_OUT", "F.Cu", (("PAD", "U103", "2"),
                          (19.35, 21.90), (19.35, 23.90))),
    ("/SEL_OUT", "B.Cu", ((19.35, 23.90), (17.98, 23.90),
                          (14.88, 20.80), (14.88, 19.95))),
    ("/SEL_OUT", "F.Cu", ((14.88, 19.95), ("PAD", "U102", "1"))),

    # /ID0 (U100-7 -> R100-1) und /ID1 (U100-8 -> R101-1) sind mit dieser
    # Aufgabe ENTFERNT. Beide verbinden U100 (Teil der "oberen Gruppe",
    # dy=-3,70) mit R100/R101 (UNVERAENDERT, s. PLACEMENT-Kommentar --
    # eine Mitverschiebung von R100/R101 riss die R101/R13-Kollision
    # auf). Die alte Fuehrung (Escape -> 45-Grad-Diagonale -> Senkrechte
    # zum Pad) ist auf die ALTE U100-Position kalibriert; mit U100 3,70 mm
    # weiter noerdlich waere nur die ESCAPE-Etappe (der erste, feste
    # Punkt) noch gueltig zu verschieben -- die Diagonale muesste NEU
    # gerechnet werden, weil ihr Zielpunkt (die Senkrechte zu R100/R101)
    # unveraendert bleibt. Eine Diagonale mit verschobenem Start und
    # festem Ziel ist keine reine Parallelverschiebung mehr und braucht
    # dieselbe Sorgfalt wie die entfernte U1-Ostgassen-Vorverdrahtung
    # (s. Kommentar oben) -- das ist Aufgabe D, nicht C1.
    # -- Masseanbindung der SOT-353-Notausgatter U6/U7 -------------------
    # masseheiler.py brach in JEDEM Wuerfellauf an einem dieser beiden
    # Stuecke ab ("traegt Massepads, hat aber keinen freien Heilpunkt"):
    # das GND-Pad 3 der SC-70-Gehaeuse ist auf F.Cu von den eigenen
    # Escapes eingemauert, und im Umkreis ist kein Fleck frei, der gross
    # genug fuer ein 0,6-mm-Via samt Abstand waere. Kein Zufall des
    # Wuerfels, sondern ein Platzproblem -- also gehoert die Loesung in
    # die Beschreibung, nicht in den Heiler.
    # v2.1: Zielpunkt um dy=+2,30 mm mitverschoben (U6/U7 sind Teil der
    # "Notaus"-Gruppe, s. PLACEMENT-Kommentar) -- die urspruengliche
    # 2,12-mm-Luecke zwischen der U3/U6/U7-Zeile und U4/U5 wandert
    # dabei unveraendert mit (starre Parallelverschiebung), der Stummel
    # bleibt also mit denselben 0,82/0,70 mm Abstand zu beiden Hoefen
    # gueltig.
    ("GND", "F.Cu", (("PAD", "U6", "3"), (4.612, 51.50))),
    ("GND", "F.Cu", (("PAD", "U7", "3"), (9.613, 51.50))),

    # 3V3-Stummel im Kennwiderstands-Nest: R102-1 liegt zwischen U101s
    # Hof (endet x = 6,90) und R13; der direkte Weg zu U101-5 waere
    # schraeg (verboten). Knick bei x = 9,25 ausserhalb des Hofes,
    # Einfahrt auf Pad-5-Hoehe. R13-1 haengt als senkrechter Nachbar-
    # stummel in derselben Spalte daran. v2.1: UNVERAENDERT -- R102 und
    # U101 sind NICHT Teil der "oberen Gruppe" (s. PLACEMENT-Kommentar),
    # beide stehen wie in v2.
    ("3V3", "F.Cu", (("PAD", "R102", "1"), (9.25, 22.1),
                     ("PAD", "U101", "5"))),
    ("3V3", "F.Cu", (("PAD", "R102", "1"), ("PAD", "R13", "1"))),
)

# Die Vias sitzen an den Knickpunkten der Vorverdrahtung. Die
# Nest-Vias der "oberen Gruppe" (U100/U102/U103/C14/C16, dy=-3,70)
# wandern mit; die U6/U7-GND- und /NOTAUS-Vias mit der "Notaus"-Gruppe
# (dy=+2,30) -- sonst laege ein Via neben dem Lagenwechsel, den es
# herstellen soll. /ID0 und /ID1 (und ihre Vias) sind mit dieser
# Aufgabe ENTFERNT (s. PRE_TRACKS-Kommentar); ebenso die neun
# U1-Ostgassen-Vias (/+24V, /CPL, /CPH, /VCP) der v2-Fassung, zusammen
# mit den PRE_TRACKS, an deren Lagenwechseln sie sassen.
PRE_VIAS = (
    ("/SEL_OUT", 19.35, 23.90),
    ("/SEL_OUT", 14.88, 19.95),
    ("3V3", 17.68, 20.40),
    ("3V3", 22.90, 21.25),
    ("GND", 12.90, 15.975),
    # Gegenstuecke der U6/U7-Masse-Ausleitungen (s. PRE_TRACKS): erst
    # das Via bringt das eingemauerte F.Cu-Pad an den B.Cu-Guss.
    # U6/U7 gehoeren NICHT zum Nest, sondern zur "Notaus"-Gruppe.
    ("GND", 4.612, 51.50),
    ("GND", 9.613, 51.50),
    # /NOTAUS quert unter dem GND-Stummel von U6-3 hindurch.
    ("/NOTAUS", 3.70, 50.70),
    ("/NOTAUS", 5.90, 50.70),
)

# --- Masseflaechen vernaehen -------------------------------------------
STITCH_RASTER = 7.5
_STITCH_VIA_R = 0.5


def _naht_erlaubt(vx, vy):
    rand = EDGE_CLEARANCE + _STITCH_VIA_R
    if not (rand <= vx <= BOARD_W - rand and rand <= vy <= BOARD_H - rand):
        return False
    for hx, hy in M3_HOLES:
        if (vx - hx) ** 2 + (vy - hy) ** 2 < (M3_KEEPOUT / 2.0) ** 2:
            return False
    for p in PLACEMENT.values():
        if (p.x - _STITCH_VIA_R < vx < p.x + p.w + _STITCH_VIA_R
                and p.y - _STITCH_VIA_R < vy < p.y + p.h + _STITCH_VIA_R):
            return False
    for _n, _l, (x0, y0, x1, y1), verbote in RULE_AREAS:
        if "vias" in verbote and (x0 - _STITCH_VIA_R < vx < x1 + _STITCH_VIA_R
                                  and y0 - _STITCH_VIA_R < vy
                                  < y1 + _STITCH_VIA_R):
            return False
    return True


def _naehte():
    aus = []
    n_x = int((BOARD_W - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    n_y = int((BOARD_H - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    ox = (BOARD_W - (n_x - 1) * STITCH_RASTER) / 2.0
    oy = (BOARD_H - (n_y - 1) * STITCH_RASTER) / 2.0
    for iy in range(n_y):
        for ix in range(n_x):
            vx = round(ox + ix * STITCH_RASTER, 3)
            vy = round(oy + iy * STITCH_RASTER, 3)
            if _naht_erlaubt(vx, vy):
                aus.append((vx, vy))
    return tuple(aus)


# Gezielte Zusatznaehte fuer Gussfragmente, die das 7,5-mm-Raster
# verschluckt. Der Dice-Loop hat die DRC-Meldung geliefert, auf die
# dieser Block gewartet hat: rund um das MCU-Nest zerschneiden ~500
# Bahnen den F.Cu-Guss in ein Dutzend Stuecke, und `masseheiler.py`
# meldete in Lauf nach Lauf Stuecke, die Massepads tragen, aber keinen
# freien Heilpunkt haben ("Layout pruefen").
#
# WARUM HIER UND NICHT IM HEILER: der Heiler arbeitet am fertig
# verlegten Brett und findet dort keinen Platz mehr. Ein Naehvia, das
# VOR dem Verlegen steht, hat den Platz -- der Router weicht ihm aus.
# Genau das ist der Grund, aus dem v1 hier 17 Punkte fuehrte.
#
# WARUM NICHT AUS DEM RASTER: `_naht_erlaubt()` streicht in der
# Brettmitte fast jeden Rasterpunkt, weil dort die Hoefe dicht an
# dicht liegen. Ein Hof ist aber kein Kupfer. STITCH_EXTRA umgeht den
# Filter bewusst (STITCH_VIAS = _naehte() + STITCH_EXTRA) -- dafuer
# sind die Punkte einzeln gegen das GEBAUTE Brett gerechnet, mit
# denselben Kriterien wie in v1: >= 0,50 mm zu jedem Pad, >= 0,90 mm
# zu jeder Via-Mitte, >= 0,45 mm zu jeder vorverdrahteten Bahn.
# Suchskript: scratchpad/naht_suche.py (rastert die Regionen ab, die
# `masseheiler` gemeldet hat, und nimmt den mittigsten Treffer).
#
# Die Regionen stammen aus den Heiler-Meldungen von 30 Wuerfellaeufen;
# jede Zeile deckt die Stuecke ab, die dort wiederholt auftraten:
# v2.1 (Aufgabe C1): vier Punkte, die direkt neben dem alten Platz von
# U100/U102/U103 lagen (die "obere Gruppe" ist um dy=-3,70 verschoben,
# s. PLACEMENT-Kommentar), sind ERSATZLOS ENTFERNT statt mitverschoben:
# (11,70|23,20), (13,70|19,10), (21,50|27,20), (16,70|19,10). Sie waren
# gegen das GEBAUTE v2-Kupfer (Escapes, Guss-Erreichbarkeit) einzeln
# vermessen -- mit der neuen Nest-Lage UND der entfernten
# U1-Ostgassen-Vorverdrahtung (s. PRE_TRACKS-Kommentar) waere ihre
# Gueltigkeit nur geraten, nicht nachgerechnet. Aufgabe D findet die
# noetigen Ersatzpunkte (falls welche noetig werden) aus ihrem eigenen
# Dice-Loop, wie v1/v2 es fuer diese Stellen schon einmal getan haben.
#
# Die verbleibenden zehn Punkte sind entweder UNVERAENDERT gueltig (sie
# liegen in x < 12 -- der linken, nicht verschobenen Nest-Spalte -- oder
# weit oestlich/noerdlich ausserhalb jeder verschobenen Gruppe) oder mit
# ihrer jeweiligen Gruppe mitverschoben (Kommentar an jedem Punkt).
STITCH_EXTRA = (
    (8.10, 28.50),    # Kennwiderstands-Nest West (x 5,1..15,0), unveraendert:
                      # liegt in der NICHT verschobenen linken Spalte.
    (3.00, 31.00),    # Westband (x 1,0..5,0), unveraendert, s.o.
    (26.00, 18.20),   # Streifen unter dem Kettenstecker, unveraendert:
                      # x=26 liegt oestlich jeder verschobenen Gruppe.
    (25.70, 21.50),   # Ostband am Stapelrand, unveraendert, s.o.
    # Zeile 4/5 (urspruenglich x 19,0..23,6 y 31,4..34,0) -- Teil der
    # "unteren Gruppe" (dy=+0,90, s. PLACEMENT-Kommentar), mitverschoben.
    (21.30, 34.30),
    # Band zwischen Nest und Notaus (urspruenglich y 35,3..45,2) --
    # liegt zwischen der unteren Gruppe (endet jetzt bei R21, y=39,12)
    # und der Notaus-Gruppe (beginnt jetzt bei J3, y=41,18); mit dy=+0,90
    # (der unteren Gruppe, deren unmittelbarer Nachbar dieser Punkt ist)
    # mitverschoben.
    (13.50, 40.10),
    # Die folgenden fuenf Punkte lagen alle in der Notaus-Zeile
    # (U3/U6/U7 <-> U4/U5) bzw. darunter -- Teil der "Notaus"-Gruppe
    # (dy=+2,30, s. PLACEMENT-Kommentar), alle mitverschoben.
    (8.60, 50.00),        # Notaus-Zeile Mitte
    (7.70, 50.00),        # zweiter Punkt in derselben Zeile
    (3.20, 51.80),        # Notaus-Zeile West
    (8.90, 50.90),        # Notaus-Zeile, zwischen U6/U7 und U4/U5
    (7.30, 56.30),        # B.Cu-Insel unter U4/U5
)

STITCH_VIAS = _naehte() + STITCH_EXTRA

# --- Netzklassen -------------------------------------------------------
# /PWR_IN (vor Q90), /+24V (nach Q90 -- speist U1, Leistungsstecker,
# U90-Eingang) und die beiden Motorausgaenge tragen den Motorstrom.
POWER_NETS = ("/PWR_IN", "/+24V", "/Out1", "/Out2")

# v2.1 (Aufgabe C1): R1 verlangt den Klemmenkoerper kantenbuendig (Hof-
# Suedkante == BOARD_H) -- ein bewusster, im Vertrag begruendeter
# Widerspruch zu geometry.check_all()s generischer EDGE_CLEARANCE-Regel
# (0,5 mm Rand fuer JEDEN Hof). Ohne diesen Eintrag verweigert
# build.bauen() den Bau ("J5 ragt unten hinaus"), obwohl die Lage genau
# der Auflage entspricht. S. Kommentar bei PLACEMENT["J5"] und
# geometry.check_all()s EDGE_FLUSH_REFS-Dokumentation.
EDGE_FLUSH_REFS = frozenset(("J5",))

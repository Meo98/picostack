"""Platinenbeschreibung des Motormoduls (v2): Umriss, Lochbild, Platzierung.

Gelesen von tools/pcb/geometry.py (Pruefung), tools/pcb/build.py
(Aufbau) und tools/pcb/netclasses.py (Bahnbreiten). Bewusst OHNE
KiCad-Abhaengigkeit -- `python3 tools/pcb/geometry.py spec_motor` muss
ohne pcbnew laufen.

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
    """Ein Bauteil, dessen Lage der Vertrag festlegt."""
    x0, y0, x1, y1 = flaeche
    return Platz(ref, x0, y0, round(x1 - x0, 3), round(y1 - y0, 3), rot, tht,
                 unten)


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
FP_HDR_1X18 = "Connector_PinHeader_2.54mm:PinHeader_1x18_P2.54mm_Vertical"
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
    "J95": FP_HDR_1X18, "J96": FP_HDR_1X04,
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

PLACEMENT = {
    # -- Vertragsstecker: ausgerechnet, nicht abgeschrieben --
    "J100": _aus_vertrag("J100", _S["stapel_links"]["flaeche"],
                         _S["stapel_links"]["drehung"], True),
    "J105": _aus_vertrag("J105", _S["stapel_rechts"]["flaeche"],
                         _S["stapel_rechts"]["drehung"], True),
    "J101": _aus_vertrag("J101", S.HOF(FP_SKT_1X02, _S["kette"]["pin1"],
                                       _S["kette"]["drehung"]),
                         _S["kette"]["drehung"], False),
    "J102": _aus_vertrag("J102", S.HOF(FP_HDR_1X02, _S["kette"]["pin1"],
                                       _S["kette"]["drehung"]),
                         _S["kette"]["drehung"], False, unten=True),
    "J103": _aus_vertrag("J103", S.HOF(FP_SKT_2X02, _S["leistung"]["pin1"],
                                       _S["leistung"]["drehung"]),
                         _S["leistung"]["drehung"], False),
    "J104": _aus_vertrag("J104", S.HOF(FP_HDR_2X02, _S["leistung"]["pin1"],
                                       _S["leistung"]["drehung"]),
                         _S["leistung"]["drehung"], False, unten=True),

    # -- MCU-Nest (dx=-1.0 gegenueber v1, s. Moduldocstring; Zeilen 1-3
    #    unveraendert relativ zueinander) --
    "U100": Platz("U100", 14.00, 16.50, 7.70, 7.00, 0, False),
    "C14": Platz("C14", 22.70, 16.50, 3.76, 1.96, 0, False),
    "C16": Platz("C16", 22.70, 19.20, 3.76, 1.96, 0, False),
    "U102": Platz("U102", 14.00, 24.50, 4.56, 2.50, 0, False),
    "U103": Platz("U103", 19.60, 24.50, 2.90, 2.20, 0, False),
    "R7": Platz("R7", 14.00, 28.20, 3.70, 1.90, 0, False),
    "R8": Platz("R8", 18.70, 28.20, 3.70, 1.90, 0, False),
    "R9": Platz("R9", 23.40, 28.20, 3.70, 1.90, 0, False),
    "C13": Platz("C13", 14.00, 31.20, 3.76, 1.96, 0, False),
    "R5": Platz("R5", 18.70, 31.20, 3.70, 1.90, 0, False),
    "R20": Platz("R20", 23.40, 31.20, 3.70, 1.90, 0, False),

    "U101": Platz("U101", 4.00, 21.00, 2.90, 2.20, 0, False),
    "C101": Platz("C101", 4.00, 24.20, 3.76, 1.96, 0, False),
    "R102": Platz("R102", 8.40, 24.20, 3.70, 1.90, 0, False),
    "C100": Platz("C100", 4.00, 27.10, 3.76, 1.96, 0, False),
    "R13": Platz("R13", 8.40, 27.10, 3.70, 1.90, 0, False),
    "R100": Platz("R100", 4.00, 30.00, 3.70, 1.90, 0, False),
    "R101": Platz("R101", 8.30, 30.00, 3.70, 1.90, 0, False),
    "R104": Platz("R104", 4.00, 32.90, 3.70, 1.90, 0, False),
    "R105": Platz("R105", 8.30, 32.90, 3.70, 1.90, 0, False),

    # Zeile 4 -- NEU (v1s Spalte 4 kollidierte mit stapel_links, s.
    # Moduldocstring). x>=12,65: bewusst rechts von der R100..R105-Spalte
    # begonnen (die bis x=12,00 reicht), damit dieser Zeile nur EIN
    # Nachbar (Zeile 3 oben) statt zwei Nachbarn mit COURTYARD_GAP
    # genuegen muss.
    "C15": Platz("C15", 12.65, 33.76, 3.76, 1.96, 0, False),
    "R15": Platz("R15", 17.01, 33.76, 3.70, 1.90, 0, False),
    "R10": Platz("R10", 21.31, 33.76, 3.70, 1.90, 0, False),

    # Zeile 5 -- NEU: die drei Gatter-Abblockkondensatoren (C17/C18/C19,
    # Fix-Runde vor Aufgabe 7) plus das verbliebene R21 aus Zeile 4.
    "C17": Platz("C17", 4.00, 36.32, 3.76, 1.96, 0, False),
    "C18": Platz("C18", 8.60, 36.32, 3.76, 1.96, 0, False),
    "C19": Platz("C19", 13.20, 36.32, 3.76, 1.96, 0, False),
    "R21": Platz("R21", 17.80, 36.32, 3.70, 1.90, 0, False),

    # -- Notaus, auf drei kompakte Zeilen umgelegt (v1 reichte bis
    #    x=38,2 -- kollidiert mit stapel_links; alle drei Zeilen bleiben
    #    hier bei x <= 27, weit vor stapel_links bei x=28,06) --
    "J3": Platz("J3", 0.50, 38.88, 11.16, 3.54, 90, True),
    "R16": Platz("R16", 0.50, 43.02, 4.56, 2.26, 0, False),
    "R17": Platz("R17", 5.66, 43.02, 4.56, 2.26, 0, False),
    "R18": Platz("R18", 10.82, 43.02, 4.56, 2.26, 0, False),
    "R19": Platz("R19", 15.98, 43.02, 4.56, 2.26, 0, False),
    "U3": Platz("U3", 0.50, 45.88, 2.90, 2.20, 0, False),
    "U6": Platz("U6", 4.00, 45.88, 2.90, 2.20, 0, False),
    # U7 um +1,50 mm nach rechts (7,50 -> 9,00) gegenueber der ersten
    # Fassung: masseheiler.py fand in JEDEM getesteten Router-Ergebnis
    # (mehrere unabhaengige Boards) im 0,60-mm-Spalt zwischen U6 und U7
    # eine isolierte GND-Restflaeche OHNE freien Heilpunkt (zu klein
    # fuer ein 0,6-mm-Via samt Abstand zu Nachbarkupfer) -- ein reines
    # Platzproblem, kein Zufall des jeweiligen Wuerfellaufs. 2,10 mm
    # Spalt schaffen dort Platz.
    "U7": Platz("U7", 9.00, 45.88, 2.90, 2.20, 0, False),
    # U4/U5 um +1,52 mm nach unten verschoben (48,68 -> 50,20) gegenueber
    # der ersten Fassung dieser Aufgabe: die Luecke zur Zeile darueber
    # (U3/U6/U7, Ende 48,08) war mit 0,60 mm zu schmal, um sowohl
    # /NOTAUS (U3-2 -> U6-4) als auch /U1_NSLEEP (U1-3 -> U3-4, ein
    # Fanout quer durchs halbe Brett) im selben Wuerfellauf durchzu-
    # bringen -- beide blieben deshalb in ZWEI unabhaengigen Laeufen
    # identisch offen (Herleitung bei PRE_TRACKS unten). Die neue Luecke
    # (2,12 mm) reicht fuer beide getrennt. M3-Freihaltebereich (71|61
    # ist hier irrelevant, das gilt nur rechts) bzw. (4|61): U4 bleibt
    # mit y1 = 57,40 unter der 61-3,5 = 57,5-mm-Grenze (0,10 mm Luft).
    "U4": Platz("U4", 0.50, 50.20, 10.90, 7.20, 0, False),
    "U5": Platz("U5", 12.00, 50.20, 10.90, 7.20, 0, False),

    # -- Motorstufe: in der Luecke zwischen den Stapelreihen
    #    (x 33,16..45,84), y < 42,9 -- ausserhalb ANTENNE_FREI und weit
    #    unter der 8,5-mm-Steckhoehe des Pico (0805/TSSOP-Bauhoehe) --
    "C11": Platz("C11", 35.60, 15.80, 3.76, 1.96, 0, False),
    "U1": Platz("U1", 35.60, 18.90, 7.80, 5.50, 0, False),
    "C10": Platz("C10", 36.40, 25.00, 1.96, 3.76, 90, False),
    "C9": Platz("C9", 39.00, 25.00, 1.96, 3.76, 90, False),

    # J5 -- Motorklemme. RUNDE 1 dieser Aufgabe versuchte sie rechts
    # unterhalb des Leistungssteckers (wie im ersten Docstring-Entwurf
    # beschrieben) -- das ueberlappte den Hof von J95 (Randpad-Reihe)
    # um 0,63 mm und liess sich dort nicht mehr gewinnen: der Streifen
    # zwischen Leistungsstecker-Unterkante (49,82) und der Platinenkante
    # (65, minus Randstreifen) ist inklusive der Randpad-Reihe schlicht
    # 0,6..1,2 mm zu kurz fuer J5s 11,17 mm (s. Bericht, Herleitung
    # "J5-Platzsuche"). build.bauen() bricht bei JEDER Ueberlappung hart
    # ab (kein Ausnahme-Mechanismus) -- ein dokumentierter Hof-Ueberlapp
    # waere also nicht einmal baubar gewesen.
    #
    # RUNDE 2 (diese Fassung): J5 sitzt in der Luecke zwischen den
    # beiden Stapelreihen (x 33,16..45,84, y < ANTENNE_FREI-Start=42,9),
    # unterhalb des Motortreiber-Strangs (C9/C10 enden bei y=28,76).
    # Elektrisch unproblematisch (U1-Out1/Out2 muessen ohnehin dorthin
    # geroutet werden). MECHANISCH ist das ein bewusst eingegangener,
    # offener Punkt: die Flaeche liegt unter dem eingesteckten Pico
    # (STECKER_STAPEL-Steckhoehe 8,5 mm), J5 selbst baut aber ca.
    # 10,1 mm hoch (stack_spec.KLEMME_HOEHE_MM) -- eine Klemme dieser
    # Bauhoehe wuerde den Pico anheben oder mit ihm kollidieren. Dieser
    # Zielkonflikt ist NICHT in dieser Aufgabe aufgeloest (er beruehrt
    # STECKER_POS/PICO_SCHATTEN, also den Vertrag selbst, nicht nur
    # dieses Layout) -- s. Bericht, Bedenken, fuer eine ausformulierte
    # Empfehlung an eine Folgeaufgabe.
    "J5": Platz("J5", 33.92, 29.36, 11.17, 12.20, 0, True),

    # -- Versorgungszelle, rechts oben (x 51,54..72,64, y 0,5..35,65) --
    "R90": Platz("R90", 51.54, 0.50, 3.70, 1.90, 0, False),
    "R91": Platz("R91", 55.84, 0.50, 3.70, 1.90, 0, False),
    "J90": Platz("J90", 51.54, 7.70, 8.00, 8.60, 0, True),
    "Q90": Platz("Q90", 60.14, 7.70, 11.10, 7.00, 0, False),
    "D90": Platz("D90", 51.54, 17.20, 9.80, 6.70, 0, False),
    "D91": Platz("D91", 62.00, 17.20, 9.80, 6.70, 0, False),
    "C90": Platz("C90", 51.54, 24.50, 8.50, 8.50, 0, True),
    "U90": Platz("U90", 60.64, 24.50, 12.00, 9.00, 0, True),
    "C91": Platz("C91", 51.54, 33.60, 3.85, 2.05, 0, False),

    # -- Randpads (RANDPADS-Realisierung, s. Moduldocstring) --
    # Beide Werte gedreht (drehung=90): Hof-x0/y0 sind bereits die
    # POST-Rotations-Werte (build.place() dreht zuerst, misst den Hof
    # danach -- Platz.x/y meint immer den fertigen, gedrehten Hof).
    "J96": Platz("J96", 7.73, 60.96, 11.16, 3.54, 90, True),
    "J95": Platz("J95", 19.52, 60.96, 46.73, 3.54, 90, True),
}

# --- Pflicht-Kennzeichnung (stack_spec.LAYOUT_AUFLAGEN) --------------
# Pin-1-Marke neben Kontakt 1 von stapel_links (Pico-Pin 1, FLASH_TX) --
# der primaere Bezug, weil dort das Pico-Datenblatt selbst Pin 1 zaehlt.
# "KLEMMEN" in der Naehe von J5, dem einzigen verbliebenen Bauteil an
# der klassischen unteren Kante mit echtem Kabelzugang (J3/J90 sitzen
# in v2 an anderen Kanten, s. Moduldocstring).
PIN1_MARKE = (25.50, 2.27)
KLEMMEN_POS = (44.00, 58.00)

# --- Waermepfad des DRV8876 -------------------------------------------
# U1-Hof (35,60|18,90)-(43,40|24,40) plus 1 mm Rand, wie in v1.
RULE_AREAS = (
    ("Waermepfad DRV8876", ("B.Cu",),
     (34.60, 17.90, 44.40, 25.40), frozenset(("bahnen", "vias"))),

    # ANTENNE_FREI -- BINDEND (s. Moduldocstring): auf F.Cu (der Seite,
    # auf der der Pico steckt) weder Bahn noch Via noch Guss.
    ("Antennenfreiheit (Pico-Schatten)", ("F.Cu",), S.ANTENNE_FREI,
     frozenset(("bahnen", "vias", "guss"))),
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
PRE_TRACKS = (
    ("/SEL_OUT", "F.Cu", (("PAD", "U102", "1"), ("PAD", "U102", "2"))),
    ("/NQ", "F.Cu", (("PAD", "U102", "6"), ("PAD", "U102", "7"))),

    # Masse-Ausleitung fuer U100-5 (MCU-GND).
    ("GND", "F.Cu", (("PAD", "U100", "5"), (12.90, 19.675))),

    ("/NRST", "F.Cu", (("PAD", "U102", "3"), (13.50, 26.00)), 0.20),
    ("/NRST", "F.Cu", ((13.50, 26.00), (13.50, 20.325),
                       ("PAD", "U100", "6"))),

    # 3V3 U102-8 -> U103-5 auf der RUECKSEITE (Nordschneise frei
    # halten -- Herleitung wie in v1, nur um dx=-1,0 verschoben).
    ("3V3", "F.Cu", (("PAD", "U102", "8"), (17.68, 24.10))),
    ("3V3", "B.Cu", ((17.68, 24.10), (22.35, 24.10), (22.90, 24.65),
                     (22.90, 24.95))),
    ("3V3", "F.Cu", ((22.90, 24.95), ("PAD", "U103", "5"))),

    ("/FLASH_MODE", "F.Cu", (("PAD", "U102", "5"),
                             (17.68, 27.20), (18.68, 27.20),
                             (18.68, 24.35), (20.212, 24.35),
                             ("PAD", "U103", "1"))),

    ("/SEL_OUT", "F.Cu", (("PAD", "U103", "2"),
                          (19.35, 25.60), (19.35, 27.60))),
    ("/SEL_OUT", "B.Cu", ((19.35, 27.60), (17.98, 27.60),
                          (14.88, 24.50), (14.88, 23.65))),
    ("/SEL_OUT", "F.Cu", ((14.88, 23.65), ("PAD", "U102", "1"))),

    ("/ID0", "F.Cu", (("PAD", "U100", "7"), (16.50, 20.975))),
    ("/ID0", "B.Cu", ((16.50, 20.975), (12.50, 20.975),
                      (4.85, 28.625), (4.85, 29.60))),
    ("/ID0", "F.Cu", ((4.85, 29.60), ("PAD", "R100", "1"))),

    ("/ID1", "F.Cu", (("PAD", "U100", "8"), (17.10, 21.625))),
    ("/ID1", "B.Cu", ((17.10, 21.625), (14.30, 21.625),
                      (9.15, 26.775), (9.15, 29.65))),
    ("/ID1", "F.Cu", ((9.15, 29.65), ("PAD", "R101", "1"))),

    # -- Fuenf Verbindungen, die in ZWEI unabhaengigen Dice-Loop-
    # Laeufen (Aufgabe 7) IDENTISCH offen blieben (nicht random --
    # dieselben fuenf, byte-genau) -- dieselbe Klasse Problem wie in
    # v1 ("Fuenf Verbindungen blieben in JEDEM Router-Lauf offen").
    # Vier davon haengen an echten Engstellen WEIT WEG von U1s eigenem
    # Pin-Feld (Herleitung je Route unten); die fuenfte -- die beiden
    # /+24V-Aeste an U1-11 -- ist NICHT mehr hier: eine erste Fassung
    # zog sie hart auf feste Bahnen (x = 43,50/44,60), und genau DAS
    # verstopfte im naechsten Lauf sechs ANDERE U1-Pins (4/5/6/12/13,
    # beide Seiten des Bausteins) -- derselbe Klasse Fehler wie
    # "vorverdrahten verstopft, was der Router noch selbst loesen
    # muss" aus v1s eigener Geschichte. U1-11 bleibt deshalb OHNE
    # Vorverdrahtung; der Router bekommt das ganze Pin-Feld des
    # DRV8876 zusammenhaengend, statt es Bahn fuer Bahn einzuengen.
    #
    #   * J5-1 -> U1-8 und J5-2 -> U1-10 (/Out1, /Out2): J5 sitzt
    #     unterhalb von C9/C10 (y 25,00..28,76); ein direkter, senk-
    #     rechter Weg liefe durch deren Hoefe. Beide Routen weichen
    #     seitlich aus (Out1 links um C10 bei x = 35,70, Out2 rechts
    #     an C9 vorbei bei x = 42,40).
    #   * U6-4 -> U3-2 (/NOTAUS): SOT-353-Fanout im 1,27-mm-Raster.
    #     U3-2 zuerst waagrecht aus U3s Hof heraus (y = 46,98 liegt
    #     zwischen keinem anderen Pad), dann unterhalb der Zeile durch
    #     (y = 48,50, in der auf 2,12 mm erweiterten Luecke zu U4/U5,
    #     s. PLACEMENT-Kommentar bei U4) zu U6-4.
    ("/Out1", "F.Cu", (("PAD", "U1", "8"), (36.60, 24.60),
                       (35.70, 25.50), (35.70, 30.16),
                       (36.96, 31.42), ("PAD", "J5", "1"))),
    ("/Out2", "F.Cu", (("PAD", "U1", "10"), (42.40, 29.72),
                       (42.04, 30.08), ("PAD", "J5", "2"))),
    ("/NOTAUS", "F.Cu", (("PAD", "U3", "2"), (3.40, 46.98),
                         (3.40, 48.50), (6.2875, 48.50),
                         ("PAD", "U6", "4"))),

    # -- Zwei weitere Verbindungen, gefunden in ZWEI FOLGELAEUFEN NACH
    # der ersten Vorverdrahtungs-Runde (dieselben zwei, wieder identisch
    # in beiden Laeufen):
    #
    #   * R102-1 -> U101-5 (3V3): direkter Weg waere diagonal (nicht
    #     0/45/90); Knick ausserhalb von U101s Hof (x = 9,25, Hof endet
    #     bei 6,90) und Einfahrt auf Pad-5-Hoehe (y = 22,1).
    #   * U1-3 -> U3-4 (/U1_NSLEEP): der weiteste Vorverdrahtungs-Weg
    #     dieser Platine -- quer durchs halbe Brett, von der Motorstufe
    #     (Luecke zwischen den Stapelreihen) zur Notaus-Kette links
    #     unten. Kreuzt stapel_links bei y = 39,10 (Kontaktraster ab
    #     y = 2,27, Kontakte bei 37,83/40,37 -- 39,10 ist der Mittelpunkt,
    #     1,27 mm zu beiden, ausserhalb ANTENNE_FREI (< 42,9) UNABHAENGIG
    #     von x). Faehrt dann bei x = 13,00 (rechts von J3/R16-19-Zeile,
    #     links von U3/U6/U7) glatt durch bis in die U4/U5-Luecke
    #     (y = 49,80) und von dort seitlich in U3-4 -- OHNE, wie ein
    #     direkter Weg es taete, U3-Pad 5 (3V3, exakt 1,3 mm darueber
    #     auf derselben Spalte) zu treffen.
    ("3V3", "F.Cu", (("PAD", "R102", "1"), (9.25, 22.1),
                     ("PAD", "U101", "5"))),
    ("/U1_NSLEEP", "F.Cu", (("PAD", "U1", "3"), (35.20, 20.675),
                            (35.20, 39.10), (13.00, 39.10),
                            (13.00, 49.80), (2.7875, 49.80),
                            ("PAD", "U3", "4"))),

    # -- Fuenf weitere, wieder in ZWEI Folgelaeufen identisch offen
    # (dritte Generation -- entstanden GENAU dadurch, dass die zweite
    # Generation die alten +24V/CPL-Bahnen entfernte und dem Router
    # wieder Spielraum um U1-11 gab; drei der fuenf haengen jetzt an
    # U1s NORDSEITE (Pins 4/5/6, /NFAULT-3V3-IPROPI) statt an der
    # Ostseite):
    #
    #   * C16-1 -> U1-5 (3V3), U1-4 -> U100-12 (/NFAULT) und U1-6 ->
    #     U100-13 (/IPROPI) muessen alle drei von der Motorstufe zum
    #     Nest, also an BEIDEN Stapelreihen vorbei (U1 sitzt zwischen
    #     ihnen). Statt sie bei y ~39 zu kreuzen (wie /U1_NSLEEP, das
    #     dort schon eine Bahn belegt), nutzen alle drei den Streifen
    #     y < 2,27 UEBER Kontakt 1 von stapel_links/rechts -- dort ist
    #     GARANTIERT kein Kontakt, unabhaengig vom Raster. Drei parallele
    #     Gassen (y = 0,90 / 1,35 / 1,80, je 0,45 mm auseinander) halten
    #     sie getrennt; jede faehrt seitlich an U100s Kontaktspalten
    #     (x = 14,99 / 20,71) UND an C16 (x 22,70..26,46) vorbei, statt
    #     durch sie hindurch, und biegt erst auf der Ziel-Pad-Hoehe
    #     waagrecht ein (vermeidet die nachbarpads auf demselben
    #     0,65-mm-Raster).
    #   * C9-1 -> U1-11 (/+24V, s.o.): diesmal rechts an U1 vorbei
    #     (x = 44,60, klar vor stapel_rechts bei 45,84) statt durch das
    #     Waermevia-Feld.
    #   * R102-1 -> R13-1 (3V3): direkter Nachbar, senkrechter Stummel,
    #     dieselbe Spalte (x = 9,25).
    ("3V3", "F.Cu", (("PAD", "C16", "1"), (24.50, 20.18),
                     (24.50, 0.90), (34.50, 0.90), (34.50, 21.975),
                     ("PAD", "U1", "5"))),
    ("/NFAULT", "F.Cu", (("PAD", "U1", "4"), (34.00, 21.325),
                         (34.00, 1.35), (22.00, 1.35), (22.00, 22.275),
                         ("PAD", "U100", "12"))),
    ("/IPROPI", "F.Cu", (("PAD", "U1", "6"), (34.20, 22.625),
                         (34.20, 1.80), (22.50, 1.80), (22.50, 21.625),
                         ("PAD", "U100", "13"))),
    ("/+24V", "F.Cu", (("PAD", "C9", "1"), (44.60, 27.9175),
                       (44.60, 22.625), ("PAD", "U1", "11"))),
    ("3V3", "F.Cu", (("PAD", "R102", "1"), ("PAD", "R13", "1"))),

    # -- Vierte Generation: HIER BEWUSST GESTOPPT (Aufgabe 7, Dice-Loop-
    # Protokoll). Zwei Versuche, die verbliebenen U1-Nachbarnetze
    # (U1-11 -> C11-2, dann einzeln auch nur U1-5 -> J105-16)
    # vorzuverdrahten, verschlimmerten die Lage JEDES Mal (zehn, dann
    # sieben, dann wieder sieben offene Verbindungen -- U1s uebrige
    # Pins 1/2/12/13/14 gerieten jedes Mal zusaetzlich ins Stocken).
    # DREI unabhaengige Dice-Laeufe OHNE jede weitere U1-Vorverdrahtung
    # liessen dagegen stabil nur noch GENAU EINE Verbindung offen
    # (U1-5 -> J105-16, 3V3) -- besser als jede von Hand erzwungene
    # Fassung. Diese eine bleibt deshalb bewusst dem Dice-Loop
    # ueberlassen statt vorverdrahtet (s. Bericht, Bedenken, fuer die
    # exakte Restliste und die Begruendung, warum ein Nachziehen von
    # Hand hier zuverlaessig schadet statt nuetzt).
    ("/FLASH_MODE", "F.Cu", (("PAD", "J100", "5"), (27.50, 12.93),
                             (27.50, 26.90), (19.00, 26.90),
                             (19.00, 24.95), ("PAD", "U103", "1"))),
)

PRE_VIAS = (
    ("/SEL_OUT", 19.35, 27.60),
    ("/SEL_OUT", 14.88, 23.65),
    ("/ID0", 16.50, 20.975),
    ("/ID0", 4.85, 29.60),
    ("/ID1", 17.10, 21.625),
    ("/ID1", 9.15, 29.65),
    ("3V3", 17.68, 24.10),
    ("3V3", 22.90, 24.95),
    ("GND", 12.90, 19.675),
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
# verschluckt -- leer bis der Dice-Loop (Schritt 4 der Pipeline) eine
# DRC-Meldung "missing connection between copper items" liefert; dann
# werden hier, wie in v1, per Hand nachgesetzte Punkte ergaenzt
# (Herleitung je Punkt als Kommentar, wie in v1).
STITCH_EXTRA = ()

STITCH_VIAS = _naehte() + STITCH_EXTRA

# --- Netzklassen -------------------------------------------------------
# /PWR_IN (vor Q90), /+24V (nach Q90 -- speist U1, Leistungsstecker,
# U90-Eingang) und die beiden Motorausgaenge tragen den Motorstrom.
POWER_NETS = ("/PWR_IN", "/+24V", "/Out1", "/Out2")

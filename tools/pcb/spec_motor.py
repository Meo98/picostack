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

# _MOTOR_DX: die Motorstufe (U1, C9, C10, C11, J5), 0,50 mm nach Westen.
# Gebraucht haetten U1 0,26 und J5 0,45 mm; beide bekommen 0,50, damit
# der Block STARR bleibt und die Vorverdrahtung zwischen ihnen (Haelse,
# /Out1, /Out2, /+24V, /VCP) unveraendert gilt. Danach: U1-Ostpadkante
# 42,65 (1,74 mm vom Landepunkt 44,39), J5-2 auf 1,573 mm -- beide ueber
# 1,5. Nach Westen bleibt Luft: J5s Hof beginnt bei 33,42, der Hof von
# stapel_links endet bei 32,38 (1,04 mm, COURTYARD_GAP ist 0,6).
_MOTOR_DX = -0.50


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

    # -- MCU-Nest (dx=-1.0 gegenueber v1, s. Moduldocstring; Zeilen 1-3
    #    unveraendert relativ zueinander; ab Fix-Runde 2 zusaetzlich
    #    _NEST_DX nach Westen, s. dort) --
    "U100": Platz("U100", 14.00, 16.50, 7.70, 7.00, 0, False),
    # C14/C16 um 90 Grad GEDREHT und nach Osten an die Nestkante
    # gerueckt (Verdreh-Kupferregel, Herleitung oben bei _MOTOR_DX).
    # Hochkant reicht ihr Kupfer nur 1,57 statt 3,51 mm ueber die
    # Hofkante: Ostpad-Kante 22,90 + 1,57 = 24,47, also 2,14 mm vom
    # Landepunkt (26,61) -- verlangt sind 1,5. Die y-Lagen sind nach
    # unten von U103 begrenzt (Hof ab 24,50): C16 endet bei 23,86,
    # also 0,64 mm davor. Waagrecht war das mit
    # keiner x-Lage zu erreichen, ohne U100 in die Landezone des
    # Leistungssteckers (x = 12,50) zu druecken.
    "C14": Platz("C14", 22.90, 15.70, 1.96, 3.76, 90, False),
    "C16": Platz("C16", 22.90, 20.10, 1.96, 3.76, 90, False),
    "U102": Platz("U102", 14.00, 24.50, 4.56, 2.50, 0, False),
    "U103": Platz("U103", 19.60, 24.50, 2.90, 2.20, 0, False),
    # Zeile zusammengerueckt (statt 1,0 mm Luft nur noch der
    # COURTYARD_GAP von 0,6), damit R9 als letztes Glied auf 21,60
    # kommt: Ostpad-Kante 21,60 + 3,45 = 25,05, knapp unter der
    # Grenze 25,11 (= 26,61 - 1,5). R7 bleibt mit 13,00 noch 0,90 mm
    # hinter R13 (endet 12,10) und damit ueber dem Mindestabstand.
    "R7": Platz("R7", 13.00, 28.20, 3.70, 1.90, 0, False),
    "R8": Platz("R8", 17.30, 28.20, 3.70, 1.90, 0, False),
    "R9": Platz("R9", 21.60, 28.20, 3.70, 1.90, 0, False),
    # Dieselbe Rechnung eine Zeile tiefer fuer R20.
    "C13": Platz("C13", 12.80, 31.20, 3.76, 1.96, 0, False),
    "R5": Platz("R5", 17.30, 31.20, 3.70, 1.90, 0, False),
    "R20": Platz("R20", 21.60, 31.20, 3.70, 1.90, 0, False),

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
    "C11": Platz("C11", _m(35.60), 15.80, 3.76, 1.96, 0, False),
    "U1": Platz("U1", _m(35.60), 18.90, 7.80, 5.50, 0, False),
    "C10": Platz("C10", _m(36.40), 25.00, 1.96, 3.76, 90, False),
    "C9": Platz("C9", _m(39.00), 25.00, 1.96, 3.76, 90, False),

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
    "J5": Platz("J5", _m(33.92), 29.36, 11.17, 12.20, 0, True),

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
    # -- Randpad-Reihen: SMD-Loetpads auf der RUECKSEITE ----------------
    # Ruling Fix-Runde 2 (Herleitung im Vertrag bei stack_spec.RAND_Y):
    # auf der Oberseite ist die Verdreh-Kupferregel mit einer
    # 2,54-mm-Padreihe UNERFUELLBAR (hoechstens 0,42 mm statt 1,5 mm
    # Abstand zu den Landepunkten, bei jedem x-Versatz). Auf B.Cu bleibt
    # die Zusage voll erhalten, weil ein verdreht gestecktes Modul nur
    # die Oberseite beruehrt. Keine Ausnahmeliste.
    #
    # Drehung 0, `unten=True`: die Reihe laeuft waagrecht an der unteren
    # Kante, der Footprint bringt seine Pads bereits gespiegelt mit
    # (s. FP_RANDPAD_* und der Docstring des Footprints), sodass Pad 1
    # nach dem Spiegeln LINKS liegt -- in der Leserichtung der Labels.
    #
    # Lage aus den Vertragszahlen gerechnet, nicht geschaetzt:
    # RAND_X0 = 8,0, RAND_RASTER = 2,54, RAND_Y = 63,0. Der Hof IST die
    # Padflaeche (Loetpad ohne Koerper), reicht also 0,45 mm ueber die
    # Padmitte hinaus und 1,30 mm quer dazu. Also
    #   Platz.x = x(erstes Pad) - 0,45 ; Platz.y = 63,0 - 1,30 = 61,70
    #   Breite = (n-1) * 2,54 + 0,90  ; Hoehe = 2,60
    # Die Padbreite 0,90 ist nicht frei gewaehlt: der M3-Freihaltebereich
    # des Ecklochs (4|61) reicht bis x = 7,5, das erste Pad sitzt laut
    # Vertrag bei 8,0 -- es bleiben 0,5 mm, und breiteres Kupfer laege
    # unter dem Abstandsbolzen (s. Footprint-Docstring).
    # J96 traegt die vier Versorgungspads am ANFANG der Strecke
    # (x 8,00..15,62), J95 die 18 GPIO direkt danach (x 18,16..61,34) --
    # zusammen die 22 Pads und genau die Spanne, die der Vertrag nennt
    # (Ende 61,34). Luecke zwischen den beiden Hoefen: 2,54 - 2x0,95 =
    # 0,64 mm, ueber dem COURTYARD_GAP von 0,6.
    #
    # RAND_Y GILT JETZT UNVERAENDERT. Die alte Fassung musste 0,27 mm
    # nach oben ausweichen (RAND_Y_IST = 62,73), weil der Hof einer
    # echten Stiftleiste 1,77 mm ueber die Pin-Achse ragt und damit die
    # Plattenkante gerissen haette. Der Loetpad-Footprint ragt nur
    # 1,35 mm: 63,0 + 1,35 = 64,35, unter der Grenze 64,5. Damit ist die
    # letzte Abweichung von einer Vertragszahl in dieser Datei weg.
    "J96": Platz("J96", 8.00 - 0.45, 61.70, 3 * 2.54 + 0.90, 2.60, 0, False,
                 unten=True),
    "J95": Platz("J95", 18.16 - 0.45, 61.70, 17 * 2.54 + 0.90, 2.60, 0, False,
                 unten=True),
}

# --- Pflicht-Kennzeichnung (stack_spec.LAYOUT_AUFLAGEN) --------------
# Pin-1-Marke neben Kontakt 1 von stapel_links (Pico-Pin 1, FLASH_TX) --
# der primaere Bezug, weil dort das Pico-Datenblatt selbst Pin 1 zaehlt.
# "KLEMMEN" in der Naehe von J5, dem einzigen verbliebenen Bauteil an
# der klassischen unteren Kante mit echtem Kabelzugang (J3/J90 sitzen
# in v2 an anderen Kanten, s. Moduldocstring).
PIN1_MARKE = (25.50, 2.27)
# y = 59,60 statt 58,00 (Fix-Runde 1 zu Aufgabe 7): steckerprobe.py
# verlangt fuer die Kennzeichnungs-Auflage ein "KLEMMEN" an der
# Klemmenkante, gemessen als y >= BOARD_H - 6,0 = 59,0 mm. Bei 58,00 lag
# die Schrift 1,0 mm zu hoch -- gemeldet hat das niemand, weil die Probe
# vorher an der v1-Vertragszeile abbrach (s. steckerprobe.py). Die neue
# Lage liegt im freien Streifen zwischen J5 (Hof endet y = 41,56) und der
# Randpad-Reihe (Hof beginnt y = 60,96).
KLEMMEN_POS = (44.00, 59.60)

# --- Waermepfad des DRV8876 -------------------------------------------
# U1-Hof plus 1 mm Rand, wie in v1 -- x wandert mit _MOTOR_DX mit,
# sonst laege die Waermeschutzflaeche neben dem Baustein, den sie
# schuetzen soll.
RULE_AREAS = (
    ("Waermepfad DRV8876", ("B.Cu",),
     (_m(34.60), 17.90, _m(44.40), 25.40), frozenset(("bahnen", "vias"))),

    # ANTENNE_FREI -- BINDEND (s. Moduldocstring): auf F.Cu (der Seite,
    # auf der der Pico steckt) weder Bahn noch Via noch Guss.
    ("Antennenfreiheit (Pico-Schatten)", ("F.Cu",), S.ANTENNE_FREI,
     frozenset(("bahnen", "vias", "guss"))),

    # Vias-frei in der Ausleitungsgasse des DRV8876.
    #
    # Zwischen der U1-Ostpadkante (43,15) und der J105-Kontaktreihe
    # (Padkante 46,76) liegen 3,61 mm, und durch diese eine Gasse
    # muessen FUENF Netze nach Sueden: /Out2 und /+24V in
    # Leistungsbreite (1,00 mm) sowie /VCP, /CPH und /CPL (0,25 mm).
    # Das 7,5-mm-Naehraster setzt sein Via aber genau in die Mitte
    # dieser Gasse, auf (45,00|21,25) -- und zerlegt sie damit in zwei
    # Teilgassen von 1,55 und 1,46 mm.
    #
    # ROT-NACHWEIS: mit diesem Via blieb /VCP (U1-12 -> C9-2) in FUENF
    # aufeinanderfolgenden Wuerfellaeufen (e1..e5) offen -- als einzige
    # Verbindung, und in jedem Lauf. Nachgerechnet ist das kein Pech:
    # zwischen der Via-Oberkante (21,55) und der /+24V-Ausleitung auf
    # Pad-11-Hoehe bleiben 0,575 mm, eine 0,25-mm-Bahn braucht mit
    # beidseitigem Abstand 0,65 mm.
    #
    # Ein Naehvia ist hier also teurer als es nuetzt: es verbindet
    # Masseflaechen, die ueber die Nachbarnaehte (45|28,75) und
    # (37,5|21,25) ohnehin zusammenhaengen, und kostet dafuer ein
    # ganzes Netz. Die Flaeche ist knapp um dieses eine Rasterpunkt
    # gelegt (44,2..45,8 x 20,4..22,1); (45|28,75) bleibt bewusst
    # erhalten -- unterhalb von U1 ist die Gasse breiter.
    # _naht_erlaubt() liest RULE_AREAS generisch, der Eintrag wirkt
    # dort also ohne eigenen Code.
    # Eng um den EINEN Rasterpunkt gelegt (44,90..45,10 x 21,15..21,35).
    # Die erste Fassung war 1,6 x 1,7 mm gross und sperrte damit auch die
    # Stellen, an denen die Vorverdrahtung ihre eigenen Lagenwechsel
    # braucht -- sie soll aber nur EIN Naehvia verhindern, nicht eine
    # ganze Gasse.
    ("Naehtfrei in der DRV8876-Ausleitung", ("F.Cu",),
     (44.90, 21.15, 45.10, 21.35), frozenset(("vias",))),
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

    # -- Motorstufe: NUR ORTSNAHE ESCAPES ------------------------------
    #
    # WARUM NUR ORTSNAH. Eine frühere Fassung dieser Aufgabe verdrahtete
    # hier zusaetzlich sieben LANGE Querverbindungen von Hand vor
    # (/NFAULT, /IPROPI und 3V3 durch den Streifen y = 0,90/1,35/1,80
    # ueber den Stapelkontakten; /U1_NSLEEP quer durchs halbe Brett bei
    # y = 39,10; /Out2 senkrecht bei x = 42,40; /NOTAUS bei y = 46,98;
    # /FLASH_MODE von J100-5) -- weil der Router genau diese Kanten
    # offen liess. Der Router meldete danach "1 Verbindung nicht
    # verlegt", und genau das wurde als Erfolg gelesen.
    #
    # NACHGEMESSEN am gebauten Brett (kicad-cli drc auf die Platine OHNE
    # jeden Router-Lauf, s. Bericht "Vorverdrahtungs-Gate"): diese sieben
    # Zuege allein erzeugten 21 DRC-Verletzungen, BEVOR freerouting
    # ueberhaupt startete -- die y=1,35- und y=1,80-Gassen tauchen bei
    # x = 22,00/22,50 senkrecht ab und laufen dabei mitten durch die
    # Pads von J101 (Pad 2, GND, bei (22,240|5,290)) und ueber ein
    # Naehvia; /Out2 faehrt von U1-10 senkrecht nach Sueden und damit
    # durch U1s EIGENES Pad 9 (GND, (42,400|23,925), nur 0,65 mm
    # tiefer); /U1_NSLEEP kreuzt J100-Pad 15 bei (29,830|38,330) --
    # der Kommentar dort behauptete Kontakte bei 37,83/40,37 und ein
    # freies Fenster bei 39,10, das Raster liegt aber anders; /NOTAUS
    # faehrt aus U3-2 waagrecht heraus und trifft U3-4.
    #
    # Alle sieben sind ersatzlos entfernt. Sie sind auch nicht durch
    # korrigierte Langstrecken ersetzt: eine von Hand gelegte
    # Querverbindung nimmt dem Router einen Korridor, den er fuer
    # DREI andere Netze braucht -- das ist genau die Erfahrung, die v1
    # als "vorverdrahten verstopft, was der Router noch selbst loesen
    # muss" festgehalten hat. Vorverdrahtet wird deshalb nur noch, was
    # der Router GRUNDSAETZLICH nicht kann: Escapes aus Feinraster-
    # Gehaeusen und Halsstuecke an Leistungspads.
    #
    # /Out1 (U1-8 -> J5-1) bleibt: U1-8 ist der SUEDLICHSTE Pad der
    # Westspalte, unter ihm liegt kein weiterer -- der Zug faellt frei
    # nach Sueden, weicht westlich an C10 vorbei (x = 35,70; C10-Pads
    # ab x = 36,79, also 0,965 mm Luft) und trifft J5-1 von oben.
    # Nachgemessen: in der Gate-Messung oben ohne Beanstandung.
    ("/Out1", "F.Cu", (("PAD", "U1", "8"), (_m(36.60), 24.60),
                       (_m(35.70), 25.50), (_m(35.70), 30.16),
                       (_m(36.96), 31.42), ("PAD", "J5", "1"))),

    # -- Das gestaffelte Halsstueck-Paar an U1-10/U1-11 ------------------
    #
    # Das ist der EINE Fund aus v1, den die v2-Beschreibung verloren
    # hatte, und der Grund, warum der Router hier ueberhaupt scheitert.
    # v1 hielt ihn woertlich fest: "die Pads 10/11 liegen 0,65 mm
    # auseinander, zwei 1,0-mm-Fortsetzungen brauchen aber 1,2 mm
    # Kappenabstand -- direkt nebeneinander ist das unerfuellbar, der
    # Router fand nie eine Loesung."
    #
    # ROT-NACHWEIS in dieser Aufgabe: drei unabhaengige Wuerfellaeufe
    # ohne dieses Paar liessen 4, 2 und 4 Verbindungen offen -- und
    # /Out2 (J5-2 -> U1-10) UND /+24V (U1-11) waren in ALLEN DREI dabei,
    # als einzige, die nie durchkamen. Alles andere (auch /CPL, /CPH,
    # /VCP, die durch dieselbe Ostgasse muessen) loeste der Router
    # mindestens einmal selbst.
    #
    # /Out2 (Pad 10) und /+24V (Pad 11) tragen beide Leistungsbreite
    # (1,00 mm), sitzen aber auf 0,45 mm hohen Pads im 0,65-mm-Raster.
    # Beide bekommen deshalb ein 0,40-mm-Halsstueck (breiter geht nicht:
    # 0,225 mm Luft zu den Nachbarpads 9 bzw. 12) waagrecht aus dem Pad
    # heraus bis x = 43,55 -- erst DA, ausserhalb des Padfeldes
    # (Ostkante 43,15), knicken sie um 45 Grad AUSEINANDER: /Out2 nach
    # Sueden, /+24V nach Norden. Ihre Enden liegen bei y = 23,975 und
    # 21,925, also 2,05 mm auseinander -- die 1,2 mm, die zwei
    # 1,0-mm-Kappen brauchen, sind damit da, wo der Router sie braucht.
    #
    # NUR das Halsstueck-Paar reichte NICHT: vier weitere Wuerfellaeufe
    # mit Haelsen, aber ohne die Fortsetzung unten, liessen /Out2 und
    # /+24V weiterhin in JEDEM Lauf offen. Der Grund ist die Breite,
    # nicht die Staffelung: eine 1,0-mm-Bahn von U1 bis zur Klemme J5
    # quer durch die Ostgasse findet der Router nicht mehr, wenn er
    # zuvor die Signalnetze durch dieselbe Gasse gelegt hat. v1 hat
    # deshalb den GANZEN /Out2-Weg in Leistungsbreite vorverdrahtet;
    # hier steht dieselbe Loesung mit v2-Geometrie.
    # /Out2 knickt nach Sueden weg. /+24V bleibt dagegen GERADE:
    # sein Hals brauchte den Gegenknick nach Norden nur so lange, wie
    # der Router die 1,0-mm-Fortsetzung selbst suchen musste (dann
    # gelten 1,2 mm Kappenabstand). Seit /+24V unten vollstaendig
    # festgelegt ist und ueber ein Via auf die Rueckseite geht, ist der
    # Knick nicht nur unnoetig, sondern schaedlich: er verschloss die
    # Ausfahrt von Pad 12 (/VCP). Nachgerechnet -- Pad 12 kann erst ab
    # x = 43,475 steigen (0,2 mm Luft zur Padkante 43,15), der
    # Nordknick liess es aber nur bis x = 43,458 waagrecht laufen.
    # 0,017 mm zu wenig; /VCP blieb in ELF Laeufen (e1..e6, f1..f4)
    # ohne Ausnahme offen.
    ("/Out2", "F.Cu", (("PAD", "U1", "10"), (_m(43.55), 23.275),
                       (_m(44.25), 23.975)), _HALS),
    ("/+24V", "F.Cu", (("PAD", "U1", "11"), (_m(44.30), 22.625)), _HALS),

    # /Out2 in Leistungsbreite weiter bis J5-2. Die Suedspur liegt bei
    # x = 43,90, NICHT bei 44,25: die Naehvia-Spalte des 7,5-mm-Rasters
    # sitzt bei x = 45,00 (Via-Rand 44,70) -- eine 1,0-mm-Bahn auf 44,25
    # reicht bis 44,75 und ueberlappte sie um 0,05 mm. Auf 43,90
    # bleiben 0,30 mm zum Via und 0,25 mm zu den U1-Ostpads (Kante
    # 43,15). Der kurze 45-Grad-Versatz direkt unter dem Halsstueck
    # bringt die Bahn von 44,25 auf diese Spur.
    ("/Out2", "F.Cu", ((_m(44.25), 23.975), (_m(44.25), 25.00), (_m(43.90), 25.35),
                       (_m(43.90), 31.60), (_m(42.04), 33.46),
                       ("PAD", "J5", "2")), _LEISTUNG),

    # /+24V bekommt BEWUSST NUR das Halsstueck, keine Fortsetzung.
    #
    # Eine Zwischenfassung zog /+24V in Leistungsbreite nach Norden
    # (Spur x = 43,90, y 18,30..21,575) ueber U1 hinweg nach C11-2. Sie
    # loeste /+24V und /Out2 tatsaechlich -- und riss dafuer DREI neue
    # Loecher auf: /VCP, /CPH und /CPL (U1-12/13/14) blieben danach in
    # beiden Wuerfellaeufen offen. Nachgerechnet ist das kein Pech,
    # sondern Arithmetik: zwischen der U1-Ostpadkante (43,15) und dem
    # Naehvia bei (45|21,25) (Randkante 44,70) liegen 1,55 mm. Eine
    # 1,0-mm-Spur samt Abstaenden braucht davon 1,40 mm; fuer eine
    # 0,25-mm-Ausfahrt der darunter liegenden Pads 13/14 blieben 0,15
    # statt der noetigen 0,65 mm. Die Pads waren eingemauert, und
    # UNTEN durch konnten sie auch nicht: die Waermepfad-Regelflaeche
    # (34,60..44,40 x 17,90..25,40) verbietet dort B.Cu.
    #
    # Also nicht nach Norden. Aber auch "nur der Hals" reichte nicht:
    # in VIER weiteren Wuerfellaeufen (c4, d1, d2, d3) blieb U1-11 ->
    # C9-1 als EINZIGE Verbindung in JEDEM Lauf offen -- der Router
    # fing am Halsende gar nicht erst an.
    #
    # Der Grund steht im Naehraster, nicht im Router: die Ostgasse
    # zwischen U1 (Padkante 43,15) und der J105-Reihe (Padkante 46,76)
    # ist 3,61 mm breit, aber die 7,5-mm-Naehspalte x = 45,00 legt
    # genau in ihre Mitte zwei Vias ((45|21,25) und (45|28,75),
    # Randkante 44,70 bzw. 45,30). Die Gasse zerfaellt damit in zwei
    # Teilgassen von 1,55 und 1,46 mm. Eine 1,0-mm-Bahn braucht mit
    # beidseitigem Abstand 1,40 mm -- in JEDE Teilgasse passt genau
    # EINE, und die westliche gehoert schon /Out2.
    #
    # /+24V bekommt deshalb die OESTLICHE Teilgasse, von Hand:
    # unterhalb des oberen Naehvias (Unterkante 21,55) hinueber auf
    # x = 46,03 (0,23 mm zum Naehvia, 0,23 mm zu den J105-Pads -- eng,
    # aber ueber der Mindestluft 0,20), nach Sueden bis y = 26,50 und
    # dort per Via auf die RUECKSEITE. Erst dort ist der Weg nach
    # Westen frei: die Waermepfad-Regelflaeche sperrt B.Cu nur bis
    # y = 25,40, und unter /Out2s Vorderseiten-Spur (x = 43,90)
    # hindurch geht es nur auf der anderen Lage. Zurueck nach oben
    # bei x = 41,40 (0,53 mm zum /VCP-Pad von C9) und schraeg in C9-1.
    ("/+24V", "F.Cu", ((_m(44.30), 22.625), (_m(45.43), 22.625),
                       (_m(46.03), 23.225), (_m(46.03), 27.40)), _LEISTUNG),
    ("/+24V", "B.Cu", ((_m(46.03), 27.40), (_m(41.40), 27.40)), _LEISTUNG),
    ("/+24V", "F.Cu", ((_m(41.40), 27.40), (_m(40.882), 27.918),
                       ("PAD", "C9", "1")), _LEISTUNG),

    # -- Ausfahrt von U1-12 (/VCP) --------------------------------------
    # Nur die AUSFAHRT, nicht der Weg. Pad 12 liegt zwischen Pad 11
    # (/+24V, dessen Hals nach Osten laeuft) und Pad 13 (/CPH) und ist
    # damit das am engsten eingebaute Pad der Ostspalte: nach Norden
    # und Sueden Nachbarpads, nach Osten der /+24V-Hals.
    # Waagrecht bis x = 43,60 (0,45 mm ausserhalb der Padkante 43,15),
    # dann 45 Grad nach NORDOSTEN in das freie Feld ueber dem
    # /+24V-Strang -- das ist erst seit dem Entfall des Naehvias
    # (45|21,25) freies Gebiet (s. RULE_AREAS). Engste Stellen
    # nachgerechnet: 0,330 mm zur /+24V-Fuehrung (deren 1,0-mm-Kappe
    # sitzt bei (44,30|22,625)), 0,494 mm zur Padecke von Pad 13
    # (43,15|21,55).
    # Wohin /VCP von dort nach C9-2 laeuft, bleibt dem Router -- die
    # Ausfahrt war das, was er nicht fand.
    # /VCP U1-12 -> C9-2, VOLLSTAENDIG. Die blosse Ausfahrt reichte
    # nicht: /VCP blieb ueber alle Wuerfelrunden hinweg das haertnaeckigste
    # Netz, weil es von Pad 12 aus nach SUEDWESTEN muss und ihm auf der
    # Oberseite alles im Weg steht -- noerdlich Pad 13, suedlich die
    # Haelse von /+24V und /Out2, oestlich deren Leistungsspuren.
    # Zwischen U1s Ostpadkante (42,65) und der /Out2-Spur (ab 43,25)
    # bleiben 0,60 mm; eine 0,25-mm-Bahn braucht 0,65.
    #
    # Also ueber die RUECKSEITE. Das Via muss dafuer oestlich von
    # x = 43,90 liegen -- so weit reicht die Waermepfad-Regelflaeche, die
    # B.Cu unter U1 verbietet. Bei (44,30|21,375) ist es 0,45 mm von der
    # /+24V-Fuehrung entfernt und liegt frei. Unten quert die B.Cu-Bahn
    # bei y = 25,60 (0,20 mm unterhalb der Regelflaeche, die bei 25,40
    # endet) nach Westen unter der /Out2-Spur hindurch und kommt bei
    # x = 41,00 wieder hoch -- 0,63 mm neben C9s Pad.
    ("/VCP", "F.Cu", (("PAD", "U1", "12"), (_m(43.60), 21.975),
                      (_m(44.50), 21.075), (_m(44.50), 19.70),
                      (_m(45.20), 19.70))),
    ("/VCP", "B.Cu", ((_m(45.20), 19.70), (_m(44.70), 20.20),
                      (_m(44.70), 26.10), (_m(39.98), 26.10))),

    # /+24V U1-11 -> C11-2, ueber die RUECKSEITE im Norden. Auf der
    # Oberseite gibt es keinen Weg zum Abblock-C: zwischen C11s Pads
    # (Unterkante 17,505) und U1s Padreihe (Oberkante 19,15) sind
    # 1,645 mm, eine 1,0-mm-Leistungsbahn braucht 1,40 -- das ginge --,
    # aber sie muesste zuerst die Ostgasse queren, und die ist von
    # /Out2, /VCP und den Cap-Netzen belegt. Auf B.Cu ist der Streifen
    # noerdlich von y = 17,90 (Ende der Waermepfad-Regelflaeche) frei.
    # Abzweig am vorhandenen Knick (45,53|23,225) -- gemeinsamer
    # Endpunkt, kein Abzweig mitten in einer Bahn.
    # Der Nordast weicht bei (46,03) erst nach OSTEN aus, bevor er
    # hochlaeuft: bliebe er auf der Trassenspur, kaeme das /VCP-Via bei
    # (44,70|19,70) auf 0,83 mm heran -- eine 1,0-mm-Bahn und ein Via
    # brauchen 1,00 (0,5 + 0,2 + 0,3). Auf x = 46,80 sind es 2,10 mm,
    # und zur J105-Reihe (Padkante 47,54) bleiben 0,24 mm.
    # Der Nordast weicht bei (46,03) erst nach OSTEN aus, bevor er
    # hochlaeuft: bliebe er auf der Trassenspur, kaeme das /VCP-Via bei
    # (44,70|19,70) auf 0,83 mm heran -- eine 1,0-mm-Bahn und ein Via
    # brauchen 1,00 (0,5 + 0,2 + 0,3).
    #
    # WARUM 46,80 UND NICHT WEITER WESTLICH: ein Versuch mit 46,30
    # (Lauf s) sollte den Korridor zwischen dieser Spur und der
    # J105-Padreihe von 0,74 auf 1,24 mm verbreitern, weil der Router
    # /CPH und /CPL genau dort nach Sueden fuehrt (in r7 nachgemessen,
    # B.Cu-Spur x = 47,17) und dort nur EINE 0,25-mm-Bahn Platz hat.
    # Gemessen wurde das Gegenteil: die offenen Posten stiegen von 4
    # (r6/r8) auf 9..11 (s1..s3), und /CPL blieb trotzdem offen. Die
    # Spur draengt auf 46,30 zu dicht an die F.Cu-Trasse (45,53) und das
    # /VCP-Via und nimmt dem Router mehr, als der breitere Korridor
    # einbringt. Zurueckgenommen -- s. Bericht, G5.
    ("/+24V", "B.Cu", ((_m(46.03), 23.225), (_m(46.80), 22.455),
                       (_m(46.80), 17.30), (_m(40.10), 17.30)), _LEISTUNG),
    ("/+24V", "F.Cu", ((_m(40.10), 17.30), (_m(39.58), 16.78),
                       ("PAD", "C11", "2")), _LEISTUNG),

    # /NOTAUS U3-2 -> U6-4: SOT-353-Fanout im 1,27-mm-Raster, seit der
    # ersten Runde ein Wackelkandidat. U3-2 waagrecht aus dem Gehaeuse
    # heraus (y = 46,98 trifft kein Nachbarpad), dann SENKRECHT durch die
    # 0,80-mm-Gasse zwischen U3-4 (Ostkante 3,30) und U6-3 (Westkante
    # 4,10) -- x = 3,70 haelt beidseitig 0,275 mm. Unterhalb der Zeile
    # per Via auf die Rueckseite, damit der GND-Stummel von U6-3 (der
    # bei x = 4,612 senkrecht nach unten laeuft) nicht gekreuzt wird,
    # und oestlich davon wieder hoch in U6-4.
    ("/NOTAUS", "F.Cu", (("PAD", "U3", "2"), (3.70, 46.98),
                         (3.70, 48.40))),
    ("/NOTAUS", "B.Cu", ((3.70, 48.40), (5.90, 48.40))),
    ("/NOTAUS", "F.Cu", ((5.90, 48.40), (6.287, 48.013),
                         ("PAD", "U6", "4"))),

    # -- Masseanbindung der SOT-353-Notausgatter U6/U7 -------------------
    # masseheiler.py brach in JEDEM Wuerfellauf an einem dieser beiden
    # Stuecke ab ("traegt Massepads, hat aber keinen freien Heilpunkt"):
    # das GND-Pad 3 der SC-70-Gehaeuse ist auf F.Cu von den eigenen
    # Escapes eingemauert, und im Umkreis ist kein Fleck frei, der gross
    # genug fuer ein 0,6-mm-Via samt Abstand waere. Kein Zufall des
    # Wuerfels, sondern ein Platzproblem -- also gehoert die Loesung in
    # die Beschreibung, nicht in den Heiler.
    # Kurzer Stummel nach Sueden in die auf 2,12 mm erweiterte Luecke
    # zwischen der U3/U6/U7-Zeile (Hof endet y = 48,08) und U4/U5 (Hof
    # ab y = 50,20); Via bei y = 49,20 haelt dort 0,82 bzw. 0,70 mm
    # Abstand zu beiden Hoefen. Seitlich naechster Nachbar ist jeweils
    # Pad 4 desselben Gehaeuses, 1,04 mm entfernt.
    ("GND", "F.Cu", (("PAD", "U6", "3"), (4.612, 49.20))),
    ("GND", "F.Cu", (("PAD", "U7", "3"), (9.613, 49.20))),

    # 3V3-Stummel im Kennwiderstands-Nest: R102-1 liegt zwischen U101s
    # Hof (endet x = 6,90) und R13; der direkte Weg zu U101-5 waere
    # schraeg (verboten). Knick bei x = 9,25 ausserhalb des Hofes,
    # Einfahrt auf Pad-5-Hoehe. R13-1 haengt als senkrechter Nachbar-
    # stummel in derselben Spalte daran.
    ("3V3", "F.Cu", (("PAD", "R102", "1"), (9.25, 22.1),
                     ("PAD", "U101", "5"))),
    ("3V3", "F.Cu", (("PAD", "R102", "1"), ("PAD", "R13", "1"))),
)

# Die Vias sitzen an den Knickpunkten der Vorverdrahtung und wandern
# deshalb mit demselben _m() mit -- sonst laege das Via neben dem
# Lagenwechsel, den es herstellen soll.
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
    # Gegenstuecke der U6/U7-Masse-Ausleitungen (s. PRE_TRACKS): erst
    # das Via bringt das eingemauerte F.Cu-Pad an den B.Cu-Guss.
    # U6/U7 gehoeren NICHT zum Nest und wandern nicht mit.
    ("GND", 4.612, 49.20),
    ("GND", 9.613, 49.20),
    # Lagenwechsel des /+24V-Wegs um /Out2 herum (s. PRE_TRACKS).
    ("/+24V", _m(46.03), 27.40),
    ("/+24V", _m(41.40), 27.40),
    # Nordast des /+24V zum Abblock-C11 (s. PRE_TRACKS).
    ("/+24V", _m(46.03), 23.225),
    ("/+24V", _m(40.10), 17.30),
    # /VCP quert unter /Out2 hindurch.
    ("/VCP", _m(45.20), 19.70),
    # Endvia IM Pad von C9-2 (gleiches Netz): die Waermepfad-Flaeche
    # verbietet Vias bis y = 25,40, C9s Pad reicht von 25,118 bis 26,568
    # -- nur das untere Stueck ab 26,10 ist beides zugleich, frei und im
    # Pad. Via-in-Pad ist bei Handloetung unbedenklich (wie in v1 bei R5).
    ("/VCP", _m(39.98), 26.10),
    # /NOTAUS quert unter dem GND-Stummel von U6-3 hindurch.
    ("/NOTAUS", 3.70, 48.40),
    ("/NOTAUS", 5.90, 48.40),
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
STITCH_EXTRA = (
    # (14,20|24,30) ersetzt: der Punkt lag in der Tasche zwischen U100s
    # Padreihe (endet y 23,575) und U102 (ab 24,825) -- geometrisch
    # zulaessig, aber der Guss fuellt dort nicht hinein, und das Via
    # haing in JEDEM Wuerfellauf isoliert in der Luft (DRC: Via gegen
    # Zone). Ein Naehpunkt muss nicht nur PLATZ haben, sondern auch
    # Kupfer, das ihn erreicht.
    # y = 23,20, nicht 23,40: die /ID1-Diagonale (14,30|21,625)->
    # (9,15|26,775) laeuft hier durch, und ein Via braucht zu ihr
    # 0,62 mm (0,3 Via + 0,2 Luft + 0,125 Bahn). Bei 23,40 waren es
    # 0,583 -- vom Gate gefangen, nicht vom Auge.
    (11.70, 23.20),   # Westband neben U100 (x 10,5..14,0 y 17,0..31,0)
    (13.70, 19.10),   # B.Cu-Insel unter dem Nest (x 11,6..17,4 y 18,2..20,0)
    (21.50, 27.20),   # Nest-Ost (x 19,5..29,3 y 24,6..29,9)
    (21.30, 33.40),   # Zeile 4/5 (x 19,0..23,6 y 31,4..34,0)
    (18.10, 32.10),   # Zwickel westlich davon (x 15,6..18,8 y 31,4..32,9)
    (8.10, 28.50),    # Kennwiderstands-Nest West (x 5,1..15,0 y 22,3..35,3)
    (3.00, 31.00),    # Westband (x 1,0..5,0 y 26,0..36,0)
    (26.00, 18.20),   # Streifen unter dem Kettenstecker (war 26,80|17,70,
                      # ebenfalls ohne Gussanbindung)
    (25.70, 21.50),   # Ostband am Stapelrand (x 22,3..32,0 y 18,6..24,1)
    (13.50, 39.20),   # Band zwischen Nest und Notaus (x 8,9..18,1 y 35,3..45,2)
    (8.60, 47.70),        # Notaus-Zeile Mitte (x 6,6..11,1 y 46,1..49,5)
    (3.20, 49.50),        # Notaus-Zeile West (x 0,5..6,0 y 47,3..51,6)
)

STITCH_VIAS = _naehte() + STITCH_EXTRA

# --- Netzklassen -------------------------------------------------------
# /PWR_IN (vor Q90), /+24V (nach Q90 -- speist U1, Leistungsstecker,
# U90-Eingang) und die beiden Motorausgaenge tragen den Motorstrom.
POWER_NETS = ("/PWR_IN", "/+24V", "/Out1", "/Out2")

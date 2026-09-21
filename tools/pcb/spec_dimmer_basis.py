"""Gemeinsame Platinenbeschreibung der Dimmer-Module (v2.1, Aufgabe C1).

beschreibung(kanaele) liefert alle Attribute, die build.py/geometry.py/
autoroute.py/steckerprobe.py von einem spec-Modul erwarten;
spec_dimmer1/3/4.py sind Dreizeiler, die das Ergebnis in ihren
Modul-Namensraum heben.

--- v2.1 (Aufgabe C1, 2026-09-10/11): Klemmen an die Kante ------------
Alle Kanal-Klemmen (J5..J8) verlassen ihre Kanal-eigenen Taschen und
ziehen gemeinsam in KLEMMENZONE (Audit-Befund B1), kantenbuendig (R1),
in Kanalreihenfolge links->rechts (_klemme_x()). D/Q bleiben in ihren
Taschen (ausser D4/Q4, die mit der Versorgungszelle nach Osten
wandern, s.u.) -- die dadurch frei gewordene Flaeche unter jedem FET
nehmen die Gatewiderstaende RG/RP auf: JEDER Kanal bekommt sein
eigenes Paar direkt beim eigenen FET statt in einem gemeinsamen
Sammelplatz (Audit-Befund W6). Die Versorgungszelle (und mit ihr D4/
Q4) wandert um dx=+2,10 mm nach Osten -- derselbe Landepunkt-Fund wie
in spec_motor.py, s. dort. J95/J96 sind Teil des woertlich
uebernommenen Nests (NEST_REFS) und folgen dessen v2.1-Aenderungen
automatisch (F.Cu/senkrecht statt B.Cu/waagrecht).

WICHTIGER FUND DIESER AUFGABE: KLEMMENZONE selbst musste verbreitert
werden (34,40 -> 46,40 mm, s. stack_spec.KLEMMENZONE) -- eine
gleichmaessige Verteilung der Klemmen (der erste Versuch) trifft
zwangslaeufig einen der drei Landepunkt-Sperrstreifen, die durch die
Zone laufen (Spiegel von stapel_links/-rechts/kette). _klemme_x() traegt
deshalb eine gepruefte Positionstabelle statt einer Formel, s. dort fuer
die volle Herleitung.

v2-NEUAUFLAGE (Aufgabe 8a, wie Aufgabe 7 fuer den Motor). Die alte
Fassung importierte `from spec_sockel import Platz, _aus_vertrag` --
spec_sockel.py ist seit Aufgabe 7 auf dem v1-Vertrag stehengeblieben
(`_S["stapel"]` gibt es in v2 nicht mehr, KeyError bei jedem Import,
s. tests/test_spec_sockel.py) und riss damit JEDEN Import dieser Datei
mit sich. Die alte Platzierung war ausserdem an einem 64x60-Umriss und
an v1-Motor-Referenzen (Q1/D1/J5/J3/U1 als DRV8876-Strang) gerechnet,
die es beide nicht mehr gibt -- das neue Board ist 75x65 (S.BOARD_W/H),
und die Versorgungszelle heisst jetzt J90/Q90/R90/R91/D90/D91/U90/C90/
C91 (tools/sch/versorgung.py-Zelle, dieselbe wie beim Motormodul).
Diese Datei ist deshalb NEU GERECHNET, mit spec_motor.py (der bewaehrte
v2-Nachweis fuer dieselbe Zelle) als einziger Quelle fuer alles, was
sich wortgleich uebernehmen laesst -- kein Rueckgriff auf spec_sockel.

WAS WOERTLICH UEBERNOMMEN IST: das MCU-Nest (U100/U101/U102/U103,
C100/C101, R100/R101/R102/R104/R105) UND alle sechs Vertragsstecker
(J100/J105 Stapelreihen, J101/J102 Kette, J103/J104 Leistung, J95/J96
Randpads) -- Platz fuer Platz aus spec_motor.PLACEMENT, ungeaendert.
Ein Nest, das am Motormodul bereits vollstaendig verlegt wurde
(spec_motor-Docstring, Aufgabe 7), wird nicht neu gewuerfelt; dieselbe
Nest-Vorverdrahtung (SEL_OUT/NQ/NRST/3V3/FLASH_MODE/ID0/ID1) gilt
deshalb unveraendert (s. _pre_tracks_und_vias() unten). Die Netzliste
aller drei Dimmer-Schaltplaene (per `kicad-cli sch export netlist`
nachgesehen) bestaetigt: dieselben 19 Referenzen, dieselben Netznamen,
auf allen drei Kanalzahlen identisch.

WAS NEU IST GEGENUEBER DEM MOTORMODUL:

* Drei zusaetzliche Nest-Stuetzkondensatoren C102/C103/C104 (3V3/GND,
  im Motor-Schaltplan nicht vorhanden -- neu im Dimmer-Schaltplan).
  Sie haben keine feste Pin-Zugehoerigkeit (reine Stuetzkapazitaet),
  und bekommen deshalb einen freien Fleck NEBEN dem Nest (zwischen
  U101 und U100, s. PLACEMENT), statt eine neue Zeile zu eroeffnen.

* Die Versorgungszelle ist NICHT wortgleich vom Motormodul uebernommen,
  sondern eigens (aber mit denselben Bauteilen, demselben Schema und
  derselben Spaltenbreite x=51,54..72,64) VERDICHTET: das Motormodul
  liess zwischen R90/R91 (Gate-Teiler) und J90 (Einspeiseklemme) 5,3 mm
  Luft, weil es sie nicht brauchte (der DRV8876-Strang sass in der
  Stapelluecke, nicht rechts). Der Dimmer braucht diese 4,5 mm, um
  einen vierten Kanal unterzubringen -- s. "Kanalzone" unten. Alle
  Bauteile, alle Netze, dieselbe Spaltenbreite: nur die y-Raster
  ruecken auf den COURTYARD_GAP von 0,6 mm zusammen (vorher bis zu
  5,3 mm Luft). Rot-Nachweis der Kollisionsfreiheit: geometry.check_all()
  unten, gegen die ECHTEN Hoefe derselben Footprints, die spec_motor
  schon benutzt (R_0805/D_SMC/TO-252/CP_Radial/Converter_DCDC).

* Kanalzone: ein Kanal ist Freilaufdiode (oben) + FET (darunter,
  "buendig ueber der Klemme") + Klemme (unten) -- Vorgabe des
  Aufgabenzettels. Vier Zonen sind dafuer frei, weil der Dimmer (anders
  als das Motormodul) KEINE Notaus-Kette braucht (J3/R16-19/U3-U7
  kommen im Dimmer-Schaltplan nicht vor -- ERC-bestaetigt, kein Bauteil
  dieser Namen in der Netzliste):

    Kanal 1 -- die Luecke zwischen den beiden Stapelreihen (x
      32,98..46,02, y < 42,9 -- ausserhalb ANTENNE_FREI), GENAU der
      Platz, an dem das Motormodul seinen DRV8876-Strang hatte. Bereits
      als sicher erprobt (Aufgabe 7): keine Bauteilhoehe dort stoert den
      gesteckten Pico, keine Antennenflaeche wird beruehrt.
    Kanal 2/3 -- die vom fehlenden Notaus frei gewordene linke Flaeche
      (x 0,5..27, y > 35,4, unterhalb des Nests). Zwei Spalten
      nebeneinander (Pitch 11,70 mm, FET-Hofbreite + COURTYARD_GAP).
      Die Klemmen beider Spalten sind gegenueber ihrer Spalte nach
      rechts versetzt (Kanal 2: +7,10 mm, Kanal 3: +4,00 mm) -- Grund:
      das M3-Freihaltequadrat der linken unteren Bohrung (0,5..7,5 mm x
      57,5..64,5 mm) reicht in genau die Hoehe, in der die Klemme von
      Kanal 2 sonst saesse. Ein reiner Ortsversatz (die Leiterbahn
      zwischen FET-Drain und Klemmenpad macht in Lage 8b einen Knick)
      ist billiger als die Spalte zu verschieben und damit die
      Kanal-3-Spalte aus dem verfuegbaren Streifen zu draengen.
    Kanal 4 -- die durch die verdichtete Versorgungszelle frei
      gewordene Tasche rechts (x 50,76..74,5, y 31,75..43,12 fuer
      Diode/FET/Gatewiderstaende, y 51,0..59,6 fuer die Klemme,
      unterhalb des Leistungssteckers). Diode und FET stehen hier
      NEBENEINANDER statt uebereinander (die Tasche ist nur 11,4 mm
      hoch -- fuer den vollen Uebereinander-Stapel braucht es 23,5 mm),
      die Klemme sitzt eine Etage tiefer, unterhalb des
      Leistungssteckers -- derselbe Kompromiss wie bei J5 im
      Motormodul (spec_motor-Docstring, "bewusst offener mechanischer
      Punkt"), hier aber rein raeumlich (kein Pico-Steckhoehen-Konflikt,
      die Zone liegt ausserhalb von PICO_SCHATTEN).

RG/RP (Gatewiderstand + Pulldown) fuer Kanal 1..3 sitzen in der
schmalen Gasse zwischen dem Nest und der Stapelreihe (x 23,20..26,90,
gestapelt statt nebeneinander -- die Gasse ist nur 6,54 mm breit, ein
Widerstand nebeneinander braucht 8,0 mm). Kanal 4 bekommt seine eigenen
RG/RP direkt in seiner Tasche.

VORVERDRAHTUNG. `PRE_TRACKS`/`PRE_VIAS` enthalten die Nest-Vorverdrahtung,
wortgleich vom Motormodul uebernommen und gegen tatsaechlich vorhandene
Referenzen gefiltert (_pre_tracks_und_vias() unten) -- die
U6/U7-Massestummel und der R102-1->R13-1-Steg des Motormoduls haengen an
Bauteilen, die es im Dimmer nicht gibt, und werden deshalb NICHT
mitgenommen (die alte v1-Fassung filterte nur nach NETZNAMEN, nicht nach
Referenz -- das haette genau diese beiden an nicht existierende Pads
gehaengt). DAZU kommen seit Aufgabe 8b zwei EIGENE Bahnen
(EIGENE_PRE_TRACKS unten, /SEL_OUT J102-1 und 3V3 R102-1->C100-1) -- die
beiden Verbindungen, die der Router im Wuerfelspiel nachweislich nicht
von selbst schafft; Zaehlung und Herleitung stehen dort.
RULE_AREAS traegt nur die verbindliche ANTENNE_FREI-Sperre; eine eigene
Waermepfad- oder Gassensperre wie beim DRV8876 braucht es hier nicht
(diskrete FETs statt eines gehaeusten Treiberbausteins, keine bekannte
Engstelle). Der guenstige Vorverdrahtungs-Gate ("bauen + DRC ohne
Router") lief gegen alle drei Varianten gruen -- s. Bericht zu
Aufgabe 8.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S             # noqa: E402
from spec_motor import Platz       # noqa: E402  (identische Kopie wie
                                    # in spec_motor/spec_sockel; hier aus
                                    # spec_motor bezogen, weil spec_sockel
                                    # auf v1 stehengeblieben ist, s. oben)
import spec_motor as M             # noqa: E402  (Nest + Footprint-Quelle)

# -- Footprints, aus den bereits am Motormodul bewiesenen Eintraegen ---
FP_KLEMME_2 = M.FOOTPRINTS["J90"]   # PT-1,5-2-3.5-H, Hof 8,00 x 8,60 mm
FP_TO252 = M.FOOTPRINTS["Q90"]      # TO-252-3_TabPin2, Hof 11,10 x 7,00
FP_SMC = M.FOOTPRINTS["D90"]        # D_SMC, Hof 9,80 x 6,70
_C = M.FOOTPRINTS["C100"]           # 0805 HandSolder, Hof 3,76 x 1,96
_R = M.FOOTPRINTS["R90"]            # 0805 HandSolder, Hof 3,70 x 1,90

# -- Nest + Vertragsstecker: woertlich vom Motormodul (s. Modul-Docstring) --
NEST_REFS = (
    "J100", "J105", "J101", "J102", "J103", "J104", "J95", "J96",
    "U100", "U101", "U102", "U103", "C100", "C101",
    "R100", "R101", "R102", "R104", "R105",
)

# -- Versorgungszelle: gleiche Bauteile, VERDICHTETES eigenes Raster ---
# (s. Modul-Docstring, "WAS NEU IST"). x-Spalte 51,54..72,64 bleibt die
# des Motormoduls -- nur die y-Lagen ruecken auf COURTYARD_GAP=0,6
# zusammen, wo das Motormodul bis zu 5,3 mm Luft liess.
COURTYARD_GAP = M.COURTYARD_GAP
EDGE_CLEARANCE = M.EDGE_CLEARANCE

# v2.1 (Aufgabe C1): die gesamte Spalte um dx=+2,10 mm nach OSTEN
# verschoben (x 53,64.. statt 51,54..) -- WORTGLEICH dieselbe
# Verschiebung und derselbe Grund wie bei spec_motor.PLACEMENT
# (Landepunkt-Spiegel von stapel_links wanderte durch Aufgabe Bs
# BOARD_W-Wachstum von x=44,39 auf x=51,39, direkt an den alten
# Zellenrand -- Rot-Nachweis dort). D4 (unten, x=51,00 vor der
# Verschiebung) war hier sogar der SCHAERFSTE Fall im ganzen Projekt:
# der Landepunkt LAG in seinem Hof (0,00 mm statt 1,5). Nach der
# Verschiebung (D4 neu x=53,10) bleiben 1,71 mm Reserve.
_VERSORGUNG_PLATZ = {
    # -- v2.1 Aufgabe D4: J90 AN DIE OBERKANTE, R90/R91 DARUNTER.
    #
    # Sichtbefund des Nutzers am 3D-Bild: "zwei Wiederstaende vor dem
    # Ausgang ... die Anschlussklemmen sollten wirklich am Boardrand
    # liegen ohne irgendwelche Wiederstaende davor". Nachgemessen war es
    # schlimmer als gemeldet: R90/R91 standen bei y 0,50..2,40 zwischen
    # J90 (ab y 3,00) und der Oberkante, UND J90 selbst war um 180 Grad
    # verdreht -- seine Drahtoeffnung zeigte nach innen (gemessen mit
    # klemmenprobe.py: "dorthin sind es 61,43 mm, zur naechsten Kante
    # nur 3,02 mm"). An diese Klemme war kein Kabel anschliessbar.
    #
    # Die Oeffnungsrichtung der Bauform ist jetzt Vertragsdatum
    # (stack_spec.KLEMME_OEFFNUNG, aus dem STEP-Modell gemessen) und
    # klemmenprobe.py haelt R1 rot -- vorher war R1 eine Regel ohne
    # Pruefung, die beim Platzieren von Hand befolgt wurde.
    #
    # NEUE LAGE, gerechnet statt geschaetzt:
    #   J90  Drehung 180 -> Oeffnung zeigt nach -y (oben). Hof-Oberkante
    #        auf y=0,00, also buendig (R1, K2). Kontakte liegen lokal
    #        auf y=0, bei Drehung 180 also 5,00 mm unter der
    #        Hof-Oberkante -> global y=5,00; Padradius 1,20 -> naechste
    #        Kupferkante 3,80 mm von der Kante, ueber den 2,00 mm aus R5.
    #   R90/R91 wandern in das Band, das J90 dabei freigibt: J90 endet
    #        jetzt bei y=8,60 statt 11,60, darunter liegt bis D90
    #        (y=15,20 Dimmer / 17,20 Motor) freie Flaeche. y=9,20 haelt
    #        COURTYARD_GAP (0,60) zu J90 ein, die x-Lagen bleiben
    #        unveraendert -- der Gate-Teiler behaelt seine kurze
    #        Anbindung an Q90s Gate.
    "J90": Platz("J90", 53.64, 0.00, 8.00, 8.60, 180, True),
    "R90": Platz("R90", 53.64, 9.20, 3.70, 1.90, 0, False),
    "R91": Platz("R91", 57.94, 9.20, 3.70, 1.90, 0, False),
    # Q90 (Hof bis x=73,34) muss y >= 7,51 halten, sonst greift das
    # M3-Freihaltequadrat der rechten oberen Bohrung (78|4, Kante bis
    # x=74,5/y=7,5) -- ROT-NACHWEIS: bei y=3,00 (buendig mit J90) meldet
    # geometry.check_all() "Q90 im Freihaltebereich von M3 (78.0|4.0)".
    "Q90": Platz("Q90", 62.24, 7.60, 11.10, 7.00, 0, False),
    "D90": Platz("D90", 53.64, 15.20, 9.80, 6.70, 0, False),
    "D91": Platz("D91", 64.10, 15.20, 9.80, 6.70, 0, False),
    "C90": Platz("C90", 53.64, 22.50, 8.50, 8.50, 0, True),
    "U90": Platz("U90", 62.74, 22.50, 12.00, 9.00, 0, True),
    "C91": Platz("C91", 53.64, 32.10, 3.85, 2.05, 0, False),
}
# Ende der Zelle (C91-Hofunterkante): 34,15 mm -- das ist die Zahl, an
# der die Kanal-4-Tasche unten haengt (s. _KANAL_TASCHEN). Nur 1,5 mm
# weniger als beim Motormodul (35,65) -- die grosse (5,3 mm) Luecke dort
# sass zwischen R90/R91 und J90 und liess sich verdichten; die Q90-Zeile
# selbst durfte wegen der M3-Bohrung nicht weiter nach oben.
_VERSORGUNG_ENDE_Y = 32.10 + 2.05

# RG4/RP4 (Kanal 4), v2.1 (Aufgabe C1, Audit-Befund W6): sitzen jetzt
# NAHE BEI Q4 -- nicht mehr in der Versorgungszelle, weit von Kanal 4
# entfernt (der alte Platz war eine Raumnot-Loesung: "D4/Q4 fuellen die
# Tasche bereits aus"). x an Q4 ausgerichtet (dieselbe
# +2,10-Verschiebung wie die Versorgungszelle, s.o.).
#
# NICHT unterhalb von Q4 (erster Versuch dieser Aufgabe): der Streifen
# zwischen Q4-Hofende (y=42,00) und dem frozen Leistungsstecker J103
# (Vertragsflaeche 57,90..69,64 x 43,72..49,82, s. stack_spec.
# STECKER_POS["leistung"]) ist nur 1,72 mm hoch -- zu schmal fuer
# RG4/RP4 (1,90 mm) UND deren Mindestabstaende. Rot-Nachweis:
# geometry.check_all() meldete "Ueberlappung J103/RG4" und
# "Ueberlappung J103/RP4". Stattdessen OBERHALB von Q4, in der
# 3,50-mm-Luecke zwischen dem Ende der Versorgungszelle (U90, Hof bis
# y=31,50) und dem Beginn der Kanal-4-Tasche (Q4/D4, y=35,00):
# y=32,10 haelt 0,60 mm (COURTYARD_GAP) zu U90 und 1,00 mm zu Q4.
_RG4RP4_PLATZ = {
    "RG4": Platz("RG4", 64.10, 32.10, 3.70, 1.90, 0, False),
    "RP4": Platz("RP4", 68.40, 32.10, 3.70, 1.90, 0, False),
}

# -- Neue Nest-Stuetzkondensatoren (im Motor-Schaltplan nicht vorhanden) --
#
# ROT-NACHWEIS (erster Wurf dieser Aufgabe): in der Luecke zwischen
# U101 und U100 platziert (x=7,90..11,66, y=16,50..23,58) meldete
# steckerprobe.verdrehtprobe() vier Verletzungen -- diese Luecke liegt
# genau im Spiegelbild der 2x2-Leistungsstecker-Kontakte
# (LANDEPUNKTE_VERDREHT() traegt (9,96|16,96), (9,96|19,50), (12,50|
# 16,96), (12,50|19,50) ein), und die Kupferregel verlangt dort
# LANDE_SPERRRADIUS = 1,5 mm Abstand. Neuer Platz: die schmale Spalte
# links von U101 (x=0,50..2,51, gedreht 90 Grad -- ein 0805 aufrecht
# braucht 3,76 mm, die Spalte ist nur 3,5 mm breit vor der
# M3-Randbohrung), unterhalb von deren Freihaltebereich (0,5..7,5 mm)
# und weit ausserhalb jedes Landepunkt-Streifens.
_C_NEST_PLATZ = {
    "C102": Platz("C102", 0.55, 8.00, 1.96, 3.76, 90, False),
    "C103": Platz("C103", 0.55, 12.36, 1.96, 3.76, 90, False),
    "C104": Platz("C104", 0.55, 16.72, 1.96, 3.76, 90, False),
}


# -- Kanalzonen: (Diode-Ecke, FET-Ecke, Klemmen-Ecke, FET-Drehung) je
# Kanalindex. Reihenfolge Diode oben / FET darunter, buendig ueber der
# Klemme (Aufgabenzettel) -- ausser Kanal 4 (Diode/FET nebeneinander,
# s.u.) und Kanal 1 (FET gedreht, s.u.).
#
# ROT-NACHWEIS Kanal 1 (erster Wurf): Q1 aufrecht (11,10 x 7,00) bei
# x=33,95 reichte bis x=45,05 -- mitten in den Landepunkt-Streifen von
# stapel_links (Spiegelspalte x=44,39, Sperrradius 1,5 mm, also
# verboten bis x=45,89). steckerprobe meldete "Pad Q1.2 ... nur 0.00 mm
# Kupferkante vom Landepunkt (44.39|14.47)". Die Luecke zwischen den
# Stapelreihen ist mit den beiden 1,5-mm-Saeumen nur 9,91 mm frei
# (32,98..42,89) -- schmaler als der TO-252-Hof aufrecht (11,10 mm).
# GEDREHT (90 Grad, Hof dann 7,00 x 11,10) passt er mit 1,89 mm Luft.
# Aus demselben Grund sitzt J5 (die Klemme von Kanal 1) bei x=33,60
# statt buendig unter dem urspruenglichen Diodenanker -- ihr Hof reichte
# bei x=35,50 bis 43,50, ebenfalls in den Streifen hinein (mehrere
# "Verdreht"-Funde entlang der Spalte x=44,39).
# v2.1 (Aufgabe C1): "J" (die Klemmen-Ecke) ist aus diesem Dict
# ENTFERNT -- alle Klemmen ziehen jetzt gemeinsam in KLEMMENZONE
# (Audit-Befund B1/R1/R2), in einer Reihe, links->rechts in
# Kanalreihenfolge (s. _klemme_x() unten). D/Q bleiben, wo sie waren,
# AUSSER D4/Q4 (s. dort, +2,10 mm mit der Versorgungszelle).
_KANAL_TASCHEN = {
    1: {  # Luecke zwischen den Stapelreihen (x 32,98..46,02, y<42,9)
        "D": (34.60, 1.00), "Q": (34.00, 8.30),
        "Q_rot": 90,
    },
    2: {  # linke Zone, Spalte A (x=0,50)
        "D": (0.50, 35.40), "Q": (0.50, 42.70),
    },
    3: {  # linke Zone, Spalte B (x=12,20)
        "D": (12.20, 35.40), "Q": (12.20, 42.70),
    },
    4: {  # rechte Tasche unter der verdichteten Versorgungszelle;
        # Diode/FET NEBENEINANDER (Tasche nur 8,37 mm hoch -- der volle
        # Uebereinander-Stapel braucht 23,5 mm). x um +2,10 mm verschoben,
        # s. _VERSORGUNG_PLATZ-Kommentar (derselbe Landepunkt-Grund; D4
        # war hier vor der Verschiebung der schaerfste Fall im Projekt,
        # 0,00 mm statt 1,5).
        "D": (53.10, 35.00), "Q": (64.10, 35.00),
    },
}


def _klemme_x(n, kanaele):
    """x0 der Klemme fuer Kanal n von insgesamt `kanaele` Kanaelen.

    v2.1 (Aufgabe C1, Audit-Befund B1/R1/R2): alle Klemmen eines Moduls
    liegen in EINER Reihe in KLEMMENZONE, in Kanalreihenfolge
    links->rechts.

    NICHT gleichmaessig verteilt/zentriert -- das war der erste Versuch
    dieser Aufgabe und ist FALSCH: die Landepunkt-Spiegel von
    stapel_links/stapel_rechts (S.LANDEPUNKTE_VERDREHT()) laufen als
    zwei 5,4 mm breite Sperrstreifen (Spaltenmitte x=33,61 bzw. 51,39,
    +-2,7 mm) durch die GESAMTE KLEMMENZONE -- schmaler als der
    3,5-mm-Kontaktabstand des KF350 ist dieser Streifen NICHT, eine
    Klemme kann ihn also nie ueberspannen, nur umgehen. Eine
    gleichmaessige Verteilung trifft ihn zwangslaeufig irgendwo (Rot-
    Nachweis: bei gleichmaessiger Verteilung meldete Dimmer4 "J6 nur
    1,29 mm" und "J8 0,00 mm" -- Landepunkt LIEGT im Pad). Deshalb ist
    KLEMMENZONE selbst mit dieser Aufgabe verbreitert (46,40 statt
    34,40 mm, s. stack_spec.KLEMMENZONE-Kommentar fuer die volle
    Eskalation) UND die Positionen sind hier als gepruefte Tabelle
    hinterlegt, nicht mehr algorithmisch gleichverteilt:
        Kanal 1: x0 = 23,80   Kanal 2: x0 = 34,17
        Kanal 3: x0 = 51,95   Kanal 4: x0 = 61,96
    Jede Position haelt >= 1,6 mm Kupferabstand (0,1 mm Reserve ueber
    der 1,5-mm-Reissleine, gegen die ECHTEN Pad-Mitten, s.
    _klemme_pad_abstand()-Kommentar in tests/test_spec_dimmer.py) zu
    JEDEM der 46 Landepunkte -- nachgerechnet mit einer gierigen
    Links-nach-rechts-Suche (scratchpad, Aufgabe C1), die jede Klemme so
    weit wie moeglich nach links schiebt, aber weder einen Landepunkt-
    Sperrstreifen noch das R4-Mindestmass (0,8 mm) zur Vorgaenger-
    Klemme verletzt. Eine erste Fassung dieser Suche pruefte nur gegen
    die beiden Stapel-Spiegelspalten (33,61/51,39) und uebersah die
    Kette-Spiegelspalte (61,41|67,71..70,25) -- Kanal 4 landete dadurch
    mit x0=60,75 direkt darin (Pad nur 1,12 mm statt 1,5). Kanal 4s
    Position (61,96) und KLEMMENZONEs Breite sind deshalb GEGENUEBER
    dem ersten Rot-Nachweis dieser Aufgabe nochmals nachgezogen. Dieselben
    vier Positionen gelten fuer alle drei Kanalzahlen (Dimmer1 nutzt nur
    eine eigene, mittigere Position, s.u. -- es hat keine Nachbarklemme,
    die die Reihenfolge erzwingt).
    """
    if kanaele == 1:
        # Dimmer1 hat keine Nachbarklemme und keinen Packungszwang --
        # eine ruhige, von allen drei Landepunkt-Spalten weit entfernte
        # Position (x=37,00, s. Kanal-1-Tasche): Pad-Abstand zum
        # naechsten der 46 Landepunkte = 4,44 mm, weit ueber 1,5.
        return 37.00
    return {1: 23.80, 2: 34.17, 3: 51.95, 4: 61.96}[n]


# Klemmen-y: Hof-Suedkante buendig mit BOARD_H (R1, kantenbuendig, wie
# spec_motor.PLACEMENT["J5"] -- dieselbe bewusste Ausnahme von
# EDGE_CLEARANCE, s. Kommentar dort).
_KLEMME_Y = S.KLEMMENZONE[3] - 8.60

# -- Gatewiderstaende je Kanal (Audit-Befund W6, v2.1/Aufgabe C1):
# JEDER Kanal bekommt sein eigenes RG/RP-Paar DIREKT bei seinem EIGENEN
# FET (Q1..Q4), NICHT mehr in einem gemeinsamen Sammelplatz weit vom
# eigenen Kanal entfernt (Audit: "Wer ein Kanalproblem eingrenzt ...
# muss vier verschiedene Board-Ecken absuchen"). Moeglich geworden durch
# denselben Umzug, der B1 loest: die Klemmen (frueher direkt unterhalb
# jedes FETs) sind nach KLEMMENZONE gezogen und haben die Flaeche
# darunter freigemacht.
#
# Kanal 1 (Q1 endet y=19,40, gedreht 90 Grad): RG1/RP1 NICHT bei x=34,00
# (Q1s eigenem x), sondern ab x=36,00 -- der Landepunkt-Spiegel von
# stapel_rechts liegt jetzt bei x=33,61 (s. spec_motor.PLACEMENT-
# Kommentar "obere Gruppe" fuer dieselbe Rechnung), 36,00 haelt 2,39 mm
# Kupferkante-Abstand (>= 1,5, Reserve 0,89 mm) unabhaengig vom
# y-Versatz.
# Kanal 2/3 (Q2/Q3 enden y=49,70): RG/RP direkt darunter, y=50,30
# (COURTYARD_GAP 0,60), weit unterhalb jedes Landepunkt-Streifens.
# Kanal 4: s. _RG4RP4_PLATZ oben (bei Q4, mit derselben +2,10-
# Verschiebung).
_RGRP_PLATZ = {
    1: {"RG": (36.00, 20.00), "RP": (40.30, 20.00)},
    2: {"RG": (0.50, 50.30), "RP": (4.80, 50.30)},
    3: {"RG": (12.20, 50.30), "RP": (16.50, 50.30)},
}


def _kanal_platz(n, kanaele):
    t = _KANAL_TASCHEN[n]
    platz = {
        "D%d" % n: Platz("D%d" % n, t["D"][0], t["D"][1], 9.80, 6.70, 0,
                         False),
        "Q%d" % n: Platz("Q%d" % n, t["Q"][0], t["Q"][1],
                         *((7.00, 11.10) if t.get("Q_rot") == 90
                           else (11.10, 7.00)),
                         t.get("Q_rot", 0), False),
        "J%d" % (4 + n): Platz("J%d" % (4 + n), _klemme_x(n, kanaele),
                               _KLEMME_Y, 8.00, 8.60, 0, True),
    }
    if n == 4:
        platz.update(_RG4RP4_PLATZ)
    else:
        rg, rp = _RGRP_PLATZ[n]["RG"], _RGRP_PLATZ[n]["RP"]
        platz["RG%d" % n] = Platz("RG%d" % n, rg[0], rg[1], 3.70, 1.90, 0,
                                  False)
        platz["RP%d" % n] = Platz("RP%d" % n, rp[0], rp[1], 3.70, 1.90, 0,
                                  False)
    return platz


# -- ANTENNE_FREI: verbindliche Sperre (Kupfer UND Bauteil-Hof, F.Cu) --
RULE_AREAS = (
    ("Antennenfreiheit (Pico-Schatten)", ("F.Cu",), S.ANTENNE_FREI,
     frozenset(("bahnen", "vias", "guss"))),
)


def _naht_erlaubt(vx, vy, platzierung):
    rand = EDGE_CLEARANCE + 0.5
    if not (rand <= vx <= S.BOARD_W - rand and rand <= vy <= S.BOARD_H - rand):
        return False
    for hx, hy in S.M3_HOLES:
        if (abs(vx - hx) < S.M3_KEEPOUT / 2.0
                and abs(vy - hy) < S.M3_KEEPOUT / 2.0):
            return False
    for p in platzierung.values():
        if (p.x - 0.5 < vx < p.x + p.w + 0.5
                and p.y - 0.5 < vy < p.y + p.h + 0.5):
            return False
    for _n, _l, (x0, y0, x1, y1), verbote in RULE_AREAS:
        if "vias" in verbote and (x0 - 0.5 < vx < x1 + 0.5
                                  and y0 - 0.5 < vy < y1 + 0.5):
            return False
    return True


def _naehte(platzierung):
    aus = []
    n_x = int((S.BOARD_W - 2 * EDGE_CLEARANCE) / M.STITCH_RASTER)
    n_y = int((S.BOARD_H - 2 * EDGE_CLEARANCE) / M.STITCH_RASTER)
    ox = (S.BOARD_W - (n_x - 1) * M.STITCH_RASTER) / 2.0
    oy = (S.BOARD_H - (n_y - 1) * M.STITCH_RASTER) / 2.0
    for iy in range(n_y):
        for ix in range(n_x):
            vx = round(ox + ix * M.STITCH_RASTER, 3)
            vy = round(oy + iy * M.STITCH_RASTER, 3)
            if _naht_erlaubt(vx, vy, platzierung):
                aus.append((vx, vy))
    return tuple(aus)


# -- Nest-Vorverdrahtung: woertlich vom Motormodul, aber gegen die
# tatsaechlich vorhandenen Referenzen DIESER Platine gefiltert. --------
#
# WARUM DIE ALTE (v1-)FASSUNG NICHT REICHTE. Sie filterte nur nach
# NETZNAMEN ("GND" in einer Liste) -- das haette den U6-3/U7-3-Massestummel
# und den R102-1->R13-1-Steg des Motormoduls mitgenommen: beide haengen
# an Referenzen (U6, U7, R13), die im Dimmer-Schaltplan gar nicht
# existieren. build.pre_tracks() haette dort eine Pad-Suche gestartet,
# die nichts findet -- entweder ein Absturz oder (schlimmer) eine
# stillschweigend uebersprungene Bahn, je nachdem wie build.py das
# behandelt. Diese Fassung prueft deshalb JEDE Referenz im Pfad gegen
# NEST_REFS, nicht nur den Netznamen.
_NEST_NETZE = ("GND", "/SEL_OUT", "/NQ", "/NRST", "3V3", "/FLASH_MODE",
               "/ID0", "/ID1")


def _pre_tracks_und_vias():
    nest_refs = set(NEST_REFS)
    tracks = []
    for entry in M.PRE_TRACKS:
        netz, lage, pfad = entry[0], entry[1], entry[2]
        if netz not in _NEST_NETZE:
            continue
        refs_im_pfad = {p[1] for p in pfad
                        if isinstance(p, tuple) and len(p) == 3
                        and p[0] == "PAD"}
        if refs_im_pfad - nest_refs:
            continue          # haengt an einer Referenz, die es hier
                              # nicht gibt (z.B. U6/U7/R13 des Motors)
        tracks.append(entry)
    tracks = tuple(tracks)

    # Vias nur dort, wo ein BEHALTENER Track tatsaechlich einen
    # Lagenwechsel an genau diesem Punkt braucht -- verhindert, dass ein
    # Via fuer eine verworfene Bahn (dieselbe Motor-only-Falle wie oben)
    # versehentlich mitkommt.
    kept_points = set()
    for netz, lage, pfad in ((e[0], e[1], e[2]) for e in tracks):
        for p in pfad:
            if isinstance(p, tuple) and len(p) == 3 and p[0] == "PAD":
                continue
            kept_points.add((netz, round(p[0], 3), round(p[1], 3)))
    vias = tuple(v for v in M.PRE_VIAS
                 if (v[0], round(v[1], 3), round(v[2], 3)) in kept_points)
    return tracks + EIGENE_PRE_TRACKS, vias


# Zwei Verbindungen, die der Router in Aufgabe 8b nachweislich NICHT
# von selbst schafft -- beide aus dem Wuerfel-Protokoll, nicht geraten.
#
# Zaehlung ueber die erste Wuerfelserie (je vier Wuerfe pro Variante,
# einer davon durch einen Bauabbruch ungueltig -- also 11 gueltige),
# jeweils die Zeile "! n Verbindung(en) nicht verlegt":
#   /SEL_OUT  J102-1 <-> Nest-Via   in 8 von 11 Wuerfen offen
#   3V3       R102-1 <-> C100-1/U100-4 in 7 von 11 offen
# Alles andere Offene wechselte von Wurf zu Wurf (Wuerfelglueck, s.
# Aufgabe 7, Abschnitt 6: "was persistent offen bleibt, ist immer
# geometrisch begruendet") und bleibt deshalb bewusst unverdrahtet.
#
# WOHER DIE KOORDINATEN KOMMEN: nicht aus einem Raster, sondern vom
# FERTIG VERLEGTEN Motormodul (hardware/kicad/motor/Motormodul.kicad_pcb,
# Commit 8c6c52a, DRC 0/0). Dort hat der Router genau diese beiden
# Verbindungen erfolgreich gelegt, und das Nest ist bauteilgleich:
# U100/U101/U102/U103/R102/C100/C101/J102 stehen im Dimmer auf
# identischer Position (nachgemessen an den Bauteil-Rechtecken beider
# Platinen). Das Kupfer eines Bretts mit 0 Verletzungen ist der
# billigste vorhandene Beweis, dass die Gasse breit genug ist -- und
# der Dimmer ist dort SCHWAECHER belegt als das Motormodul (kein
# C14/C16/R7/R8/R9/R13), also nicht enger.
#
# Warum der Router sie hier trotzdem verfehlt: die Gasse ist in beiden
# Faellen nur EINE Bahn breit, und wer sie zuerst betritt, gewinnt. Beim
# Dimmer laeuft regelmaessig /FLASH_TX diagonal ueber B.Cu von
# (30,24|3,45) nach (18,62|15,07) und schneidet den J102-Korridor ab,
# bevor /SEL_OUT ihn erreicht (gemessen an Wurf d1_1).
EIGENE_PRE_TRACKS = (
    # /SEL_OUT: J102-1 (Kettenstecker-Spiegel, Pad nur auf B.Cu) am
    # Ostrand des Nests hinunter bis an das BESTEHENDE Nest-Via.
    # Damit haengt der Vertragsstecker am selben Netzstueck wie
    # U102/U103; U101-4 laesst der Router (er hat es in jedem der acht
    # Wuerfe geschafft, kurzer Weg innerhalb des Nests).
    # (Die x=22,245 ist die exakte Pad-Mitte von J102-1; das Motormodul
    # hatte hier 22,25/3,58 stehen -- 5 um daneben, was build.pre_tracks
    # als schiefes Segment abweist. Rot-Nachweis: genau daran ist der
    # erste Bauversuch dieser Erweiterung gescheitert.)
    #
    # v2.1 (Aufgabe C1): das Ziel-Via wanderte mit der "oberen Gruppe"
    # des Nests (U100/U102/U103/C14/C16, s. spec_motor.PLACEMENT-
    # Kommentar) von (14,88|23,65) auf (14,88|19,95) -- dy=-3,70. J102
    # selbst ist ein Vertragsstecker (frozen) und bewegt sich nicht; die
    # ERSTEN beiden Punkte (Escape aus dem Pad) bleiben deshalb
    # UNVERAENDERT, die naechste (freie, laengenunabhaengige) Senkrechte
    # nimmt die gesamte Verkuerzung auf (16,49 -> 12,79), und ALLE
    # Punkte danach wandern um denselben dy=-3,70 mit -- eine reine
    # Parallelverschiebung des Restwegs, die jeden Winkel unveraendert
    # laesst (Rot-Nachweis: ohne diese Anpassung meldete kicad-cli drc
    # "shorting_items" zwischen /SEL_OUT und 3V3 bei (17,7|20,6) --
    # der alte, unverschobene Pfad lief mitten durch die NEUE Lage des
    # 3V3-Rueckseitenvias, s. PRE_TRACKS in spec_motor.py).
    ("/SEL_OUT", "B.Cu", (("PAD", "J102", "1"), (22.245, 3.585),
                          (21.17, 4.66), (21.17, 12.79), (17.39, 16.57),
                          (17.73, 16.91), (17.73, 18.48), (16.31, 19.90),
                          (14.93, 19.90), (14.88, 19.95))),

    # 3V3: R102-1 -> C100-1. Der einzige Weg ist die 0,89 mm schmale
    # Gasse zwischen C101 (Hofunterkante 26,18) und C100 (Hofoberkante
    # 27,07) auf y = 26,98; nach Sueden um R102 herum, weil R102-1 das
    # NORD-Pad ist. Ohne diese Bahn blieb der vorverdrahtete
    # 3V3-Stummel (R102-1 -> U101-5) in vier von vier Dimmer1-Wuerfen
    # eine eigene, unverbundene Insel (Wurf d1_4 meldete dieselbe Insel
    # als "U100-4 -> R102-1" -- anderes Gegenstueck, gleiche Ursache).
    ("3V3", "F.Cu", (("PAD", "R102", "1"), (9.25, 28.05), (8.18, 26.98),
                     (5.942, 26.98), ("PAD", "C100", "1"))),
)


# --- Board-Identitaet (R9, Audit-Befund W7) --------------------------
# stack_spec.MODULTYPEN traegt dieselben Namen/Codes bereits (0x10/0x11/
# 0x12 fuer Dimmer1/3/4) -- hier nur nochmal als Kanalzahl->Typcode-
# Tabelle, weil beschreibung() die Kanalzahl kennt, nicht den Namen.
_MODULTYP = {1: 0x10, 3: 0x11, 4: 0x12}


def _funktions_labels(kanaele):
    """R7: LED-Kanal-Beschriftung + Einspeiseklemme (Audit-Befund W5).

    LED%d bei der Pad-Mitte der jeweiligen Kanal-Klemme (_klemme_x(n,
    kanaele) + 2,25 -- das ist FP_KLEMME_2s Pad-1-Versatz innerhalb des
    Hofes, nachgemessen am gebauten Board fuer alle drei Kanalzahlen:
    Dimmer1 J5 x=39,25 bei _klemme_x(1,1)=37,00, Dimmer4 J5..J8 x=26,05/
    36,42/54,20/64,21 bei _klemme_x(1..4,4)=23,80/34,17/51,95/61,96 --
    ueberall exakt +2,25).

    y: KLEMMENZONE (60,80..73,00) ist oberhalb der Klemmen-Pads
    (Pad-Oberkante y=66,80) frei von KANAL-Bauteilen (kein Bauteil reicht
    unter y=50,30 hinaus, s. _RGRP_PLATZ/_RG4RP4_PLATZ oben) -- aber
    NICHT vom Klemmenkoerper selbst (dessen Silkscreen-Kontur beginnt
    schon bei y=64,78, pcbnew nachgemessen, deutlich hoeher als der reine
    Pad-Bereich) UND NICHT von der Klemme EIGENER Referenz: tidy_
    silkscreen() setzt J5/J6/J7/J8s eigene Referenz bei y=65,24..66,60,
    innerhalb des eigenen Koerpers (derselbe Pad-Anker-Kompromiss wie bei
    den dicht gepackten Widerstaenden, s. build.tidy_silkscreen()-
    Kommentar "ROT-NACHWEIS R15"). ROT-NACHWEIS (erster Wurf, y=64,50):
    _text_pruefen()s Text-gegen-Text-Pruefung (seit dieser Aufgabe, s.
    build._silk_text_rechtecke()) lehnte "LED1" ab -- es ueberlappte J5s
    eigene Referenz woertlich; kicad-cli pcb render zeigte "LED1"
    sichtbar, aber "J5" darunter verschwunden (volle Deckung). JETZT:
    y=62,50, klar OBERHALB sowohl des Klemmenkoerpers (64,78, 2,28 mm
    Reserve) als auch der eigenen Referenz (65,24, 2,74 mm Reserve) --
    innerhalb der 4-mm-Luecke zwischen KLEMMENZONE-Oberkante (60,80) und
    dem Klemmenkoerper.
    6-30V bei J90: dieselbe Herleitung wie spec_motor.FUNKTIONS_LABELS --
    Pin 1 (x=55,89) fuehrt PWR_IN/+, Pin 2 (x=59,39) GND/-, aber die
    Polaritaet steht schon auf dem Footprint (Pfeil-Dreieck an Pin 1,
    dieselbe eingebaute Konvention wie C90s "+"), eigene "+"/"-"-Texte
    entfallen deshalb hier wie dort.

    LAGE ist mit v2.1/Aufgabe D4 auf BEIDEN Boardfamilien dieselbe
    geworden (66,00|3,80), weil J90 auf beiden an die Oberkante
    gewandert ist -- die volle Herleitung steht bei
    spec_motor.FUNKTIONS_LABELS und gilt hier wortgleich. Die frueheren,
    je Boardfamilie verschiedenen Lagen (Motor oberhalb, Dimmer
    unterhalb von J90) sind damit hinfaellig; beide lagen an J90s alter,
    nach innen versetzter Stelle.

    ROT-NACHWEIS (verworfener erster Wurf, y=10,50): lag noch INNERHALB
    von J90s Klemmenkoerper (bis y=11,22) -- vom 3D-Rendering verdeckt,
    genau die K2-Falle (pad-frei ist nicht koerper-frei), s.
    spec_motor.FUNKTIONS_LABELS fuer denselben Fund am Motormodul.
    """
    aus = [("6-30V", 66.00, 3.80)]
    for n in range(1, kanaele + 1):
        aus.append(("LED%d" % n, _klemme_x(n, kanaele) + 2.25, 62.50))
    return tuple(aus)


def beschreibung(kanaele):
    assert kanaele in (1, 3, 4)

    platz = {r: M.PLACEMENT[r] for r in NEST_REFS}
    platz.update(_VERSORGUNG_PLATZ)
    platz.update(_C_NEST_PLATZ)
    for n in range(1, kanaele + 1):
        platz.update(_kanal_platz(n, kanaele))

    footprints = {r: M.FOOTPRINTS[r] for r in NEST_REFS}
    footprints.update({r: M.FOOTPRINTS[r] for r in _VERSORGUNG_PLATZ})
    for r in _C_NEST_PLATZ:
        footprints[r] = _C
    for n in range(1, kanaele + 1):
        footprints["D%d" % n] = FP_SMC
        footprints["Q%d" % n] = FP_TO252
        footprints["RG%d" % n] = _R
        footprints["RP%d" % n] = _R
        footprints["J%d" % (4 + n)] = FP_KLEMME_2

    pre_tracks, pre_vias = _pre_tracks_und_vias()

    return {
        "BOARD_W": S.BOARD_W, "BOARD_H": S.BOARD_H,
        "CORNER_R": S.CORNER_R, "M3_DRILL": S.M3_DRILL,
        "M3_HOLES": S.M3_HOLES, "M3_KEEPOUT": S.M3_KEEPOUT,
        "COURTYARD_GAP": COURTYARD_GAP, "EDGE_CLEARANCE": EDGE_CLEARANCE,
        "IST_MODUL": True,
        "MODULNAME": "Dimmer%d" % kanaele, "MODULTYP": _MODULTYP[kanaele],
        "FUNKTIONS_LABELS": _funktions_labels(kanaele),
        "FOOTPRINTS": footprints,
        "PLACEMENT": platz,
        # Welche Referenz an welchem Vertragsplatz sitzt -- dieselbe
        # Zuordnung wie beim Motormodul (dieselben sechs Referenzen,
        # dieselben Plaetze), s. spec_motor.VERTRAGSPLATZ-Docstring
        # (Fix-Runde 1 zu Aufgabe 7: das Raten ueber den Footprint-Namen
        # ordnet sonst J100 auch stapel_rechts zu).
        "VERTRAGSPLATZ": dict(M.VERTRAGSPLATZ),
        "PRE_TRACKS": pre_tracks,
        "PRE_VIAS": pre_vias,
        "RULE_AREAS": RULE_AREAS,
        "STITCH_RASTER": M.STITCH_RASTER,
        "STITCH_VIAS": _naehte(platz),
        "PIN1_MARKE": M.PIN1_MARKE,
        # v2.1: dieselbe Stelle wie beim Motormodul (s.
        # spec_motor.KLEMMEN_POS-Kommentar) -- die Gasse zwischen dem
        # M3-Freihaltequadrat der Bohrung (4|69) und KLEMMENZONE, y in
        # deren letzten 6 mm (steckerprobe-Auflage y >= BOARD_H-6,0
        # =67,0). Bewusst AUSSERHALB KLEMMENZONE (x < 23,80): bei
        # Dimmer4 fuellen die vier Klemmen die Zone lueckenlos aus,
        # jede x-Position INNERHALB der Zone wuerde also eine Klemme
        # treffen.
        "KLEMMEN_POS": (14.00, 68.00),
        "POWER_NETS": tuple(["/PWR_IN", "/+24V"]
                            + ["/LED%d" % n for n in range(1, kanaele + 1)]),
        # v2.1 (Aufgabe C1): dieselbe bewusste Ausnahme wie
        # spec_motor.EDGE_FLUSH_REFS, fuer alle Kanal-Klemmen dieses
        # Boards (R1, kantenbuendig).
        # v2.1 (Aufgabe D4): J90 kommt dazu -- die Einspeise-
        # klemme sitzt jetzt kantenbuendig an der OBERkante,
        # aus demselben Grund wie die Lastklemmen an der
        # unteren (R1).
        "EDGE_FLUSH_REFS": frozenset(
            ["J90"]
            + ["J%d" % (4 + n) for n in range(1, kanaele + 1)]),
    }

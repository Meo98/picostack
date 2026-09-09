"""Gemeinsame Platinenbeschreibung der Dimmer-Module (v2, Aufgabe 8a).

beschreibung(kanaele) liefert alle Attribute, die build.py/geometry.py/
autoroute.py/steckerprobe.py von einem spec-Modul erwarten;
spec_dimmer1/3/4.py sind Dreizeiler, die das Ergebnis in ihren
Modul-Namensraum heben.

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

WAS DIESE AUFGABE NICHT MACHT: Verlegung. `PRE_TRACKS`/`PRE_VIAS`
enthalten NUR die Nest-Vorverdrahtung, wortgleich vom Motormodul
uebernommen und gegen tatsaechlich vorhandene Referenzen gefiltert
(_pre_tracks_und_vias() unten) -- die U6/U7-Massestummel und der
R102-1->R13-1-Steg des Motormoduls haengen an Bauteilen, die es im
Dimmer nicht gibt, und werden deshalb NICHT mitgenommen (die alte
v1-Fassung filterte nur nach NETZNAMEN, nicht nach Referenz -- das
haette genau diese beiden an nicht existierende Pads gehaengt).
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

_VERSORGUNG_PLATZ = {
    "R90": Platz("R90", 51.54, 0.50, 3.70, 1.90, 0, False),
    "R91": Platz("R91", 55.84, 0.50, 3.70, 1.90, 0, False),
    "J90": Platz("J90", 51.54, 3.00, 8.00, 8.60, 0, True),
    # Q90 (Hof bis x=71,24) muss y >= 7,51 halten, sonst greift das
    # M3-Freihaltequadrat der rechten oberen Bohrung (71|4, Kante bis
    # x=67,5/y=7,5) -- ROT-NACHWEIS: bei y=3,00 (buendig mit J90) meldet
    # geometry.check_all() "Q90 im Freihaltebereich von M3 (71.0|4.0)".
    "Q90": Platz("Q90", 60.14, 7.60, 11.10, 7.00, 0, False),
    "D90": Platz("D90", 51.54, 15.20, 9.80, 6.70, 0, False),
    "D91": Platz("D91", 62.00, 15.20, 9.80, 6.70, 0, False),
    "C90": Platz("C90", 51.54, 22.50, 8.50, 8.50, 0, True),
    "U90": Platz("U90", 60.64, 22.50, 12.00, 9.00, 0, True),
    "C91": Platz("C91", 51.54, 32.10, 3.85, 2.05, 0, False),
}
# Ende der Zelle (C91-Hofunterkante): 34,15 mm -- das ist die Zahl, an
# der die Kanal-4-Tasche unten haengt (s. _KANAL_TASCHEN). Nur 1,5 mm
# weniger als beim Motormodul (35,65) -- die grosse (5,3 mm) Luecke dort
# sass zwischen R90/R91 und J90 und liess sich verdichten; die Q90-Zeile
# selbst durfte wegen der M3-Bohrung nicht weiter nach oben.
_VERSORGUNG_ENDE_Y = 32.10 + 2.05

# RG4/RP4 (Kanal 4) haben in der Kanal-4-Tasche selbst keinen Platz
# (s. _KANAL_TASCHEN -- D4/Q4 fuellen deren gesamte Hoehe von 8,37 mm
# bereits aus) und sitzen stattdessen in der ungenutzten Restbreite von
# Zeile 1 der Versorgungszelle (R90/R91 enden bei x=59,54; die Spalte
# reicht bis x=72,64), uebereinander gestapelt VOR Q90 (dessen Zeile
# erst bei y=7,60 beginnt): x1 bleibt mit 63,84 klar unter der
# M3-Reichweite (67,5 mm) der Bohrung (71|4).
_RG4RP4_PLATZ = {
    "RG4": Platz("RG4", 60.14, 0.50, 3.70, 1.90, 0, False),
    "RP4": Platz("RP4", 60.14, 3.00, 3.70, 1.90, 0, False),
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
_KANAL_TASCHEN = {
    1: {  # Luecke zwischen den Stapelreihen (x 32,98..46,02, y<42,9)
        "D": (34.60, 1.00), "Q": (34.00, 8.30), "J": (33.60, 20.00),
        "Q_rot": 90,
    },
    2: {  # linke Zone, Spalte A (x=0,50) -- Klemme nach rechts versetzt
        # (dodgt das M3-Freihaltequadrat der Bohrung (4|61), das bei
        # x<7,5 UND y>57,5 beginnt -- die Klemme reicht bis y=58,90).
        "D": (0.50, 35.40), "Q": (0.50, 42.70), "J": (7.60, 50.30),
    },
    3: {  # linke Zone, Spalte B (x=12,20) -- Klemme auf x=16,20
        # versetzt, sonst ueberlappte sie die von Kanal 2 (s.o.)
        "D": (12.20, 35.40), "Q": (12.20, 42.70), "J": (16.20, 50.30),
    },
    4: {  # rechte Tasche unter der verdichteten Versorgungszelle;
        # Diode/FET NEBENEINANDER (Tasche nur 8,37 mm hoch -- der volle
        # Uebereinander-Stapel braucht 23,5 mm), Klemme eine Etage
        # tiefer unter dem Leistungsstecker, auf x=56,00 versetzt (statt
        # buendig unter der Diode/dem FET) -- bei x=51,00 lag ihre
        # Suedostecke nur 0,11 mm vom Landepunkt-Spiegel des Ketten-
        # steckers entfernt ((54,41|59,71), s. LANDEPUNKTE_VERDREHT()).
        "D": (51.00, 35.00), "Q": (62.00, 35.00), "J": (56.00, 51.00),
    },
}

# -- Gatewiderstaende je Kanal. NICHT in der schmalen Nest<->Stapel-
# Gasse (der erste Wurf setzte sie dorthin und geriet ebenfalls in den
# Landepunkt-Streifen von stapel_rechts, x=26,61 -- "Pad RG1.2 ... nur
# 0.00 mm Kupferkante vom Landepunkt (26.61|17.01)" u.a., weil die Gasse
# zwischen U103 (endet x=22,50) und dem 1,5-mm-Saum (beginnt x=25,11)
# nur 2,01 mm frei laesst -- zu schmal fuer ein 0805, auch gedreht knapp
# unter der ROT-Grenze).
#
# ROT-NACHWEIS (zweiter Wurf): in der Nest-Luecke bei x=12,70/17,00
# platziert, kollidierte RP2 mit dem Nest-Vorverdrahtungs-Via
# (/SEL_OUT, 19,35|27,60) und dessen Rueckseitenband -- DRC meldete
# "shorting_items" (GND gegen /SEL_OUT), Loetstopplack-Bruecke UND
# Bohrabstand, an genau dieser Stelle. Die Nest-Luecke ist von der
# SEL_OUT/NRST/ID0/ID1-Vorverdrahtung durchzogen (spec_motor.PRE_TRACKS)
# und deshalb KEIN freier Fleck, obwohl sie geometrisch leer aussieht.
#
# Alle vier Gatewiderstandspaare sitzen deshalb stattdessen unterhalb
# von Kanal 1 in der Stapelluecke (x 32,98..46,02, y < ANTENNE_FREI-
# Start 42,9) -- dort liegt KEINE Vorverdrahtung (Kanal 1 selbst hat
# keine PRE_TRACKS-Eintraege, s. Moduldocstring), und die Luecke ist mit
# 42,4 mm Hoehe weit groesser, als Kanal 1 allein braucht. Reihenfolge
# von oben: Kanal 1 (unter J5), dann 2, dann 3 -- jeweils dieselbe
# x-Aufteilung wie J5 selbst, damit sie im selben 9,91-mm-Korridor
# (32,98..42,89, s. Kanal-1-Kommentar oben) bleiben.
_RGRP_PLATZ = {
    1: {"RG": (33.60, 29.20), "RP": (37.90, 29.20)},
    2: {"RG": (34.60, 32.30), "RP": (38.90, 32.30)},
    3: {"RG": (34.60, 34.80), "RP": (38.90, 34.80)},
}


def _kanal_platz(n):
    t = _KANAL_TASCHEN[n]
    platz = {
        "D%d" % n: Platz("D%d" % n, t["D"][0], t["D"][1], 9.80, 6.70, 0,
                         False),
        "Q%d" % n: Platz("Q%d" % n, t["Q"][0], t["Q"][1],
                         *((7.00, 11.10) if t.get("Q_rot") == 90
                           else (11.10, 7.00)),
                         t.get("Q_rot", 0), False),
        "J%d" % (4 + n): Platz("J%d" % (4 + n), t["J"][0], t["J"][1],
                               8.00, 8.60, 0, True),
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
    return tracks, vias


def beschreibung(kanaele):
    assert kanaele in (1, 3, 4)

    platz = {r: M.PLACEMENT[r] for r in NEST_REFS}
    platz.update(_VERSORGUNG_PLATZ)
    platz.update(_C_NEST_PLATZ)
    for n in range(1, kanaele + 1):
        platz.update(_kanal_platz(n))

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
        # y = 59,60: dieselbe Kennzeichnungs-Auflage wie beim Motormodul
        # (y >= BOARD_H - 6,0 = 59,0); x=34 liegt im freien Mittelstreifen
        # unterhalb von Kanal 1 und links der Kanal-4-Klemme.
        "KLEMMEN_POS": (34.00, 59.60),
        "POWER_NETS": tuple(["/PWR_IN", "/+24V"]
                            + ["/LED%d" % n for n in range(1, kanaele + 1)]),
    }

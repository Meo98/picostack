"""Platinenbeschreibung der Sockelplatine: Umriss, Lochbild, Platzierung.

Gelesen von tools/pcb/geometry.py (Pruefung), tools/pcb/build.py
(Aufbau) und tools/pcb/netclasses.py (Bahnbreiten). Bewusst OHNE
KiCad-Abhaengigkeit -- `python3 tools/pcb/geometry.py spec_sockel` muss
ohne pcbnew laufen.

WAS HIER STEHT UND WAS NICHT. Umriss, Lochbild und die Lage der drei
Stecker sind KEINE Entscheidung dieser Datei -- sie stehen im Vertrag
(tools/stack_spec.py) und werden hier ausgerechnet, nicht abgeschrieben.
Der Vertrag gilt fuer jede Platine des Stapels; wer ihn hier
ueberschriebe, baute eine Platine, die nicht mehr steckt. Frei
entschieden wird nur die Lage der acht platineneigenen Bauteile
(J1, U2, C1, C2, C3, D1, R1, R2).

KOORDINATEN. PLACEMENT gibt je Bauteil die linke obere Ecke seines
Hofes und dessen Groesse an -- dieselbe Groesse, die
stack_spec.FOOTPRINT_HOF aus der .kicad_mod liest.
build.courtyard_bbox() rechnet die pcbnew-Fassung (um
fertigung.HOF_STRICH aufgeblaeht) darauf zurueck, damit Vertrag und
Platzierung dasselbe Rechteck meinen. tools/pcb/steckerprobe.py misst
das an der fertigen Platine nach.

DIE UEBERLEGUNG HINTER DER PLATZIERUNG, in der Reihenfolge, in der sie
gefallen ist (Werkzeug-Skill: erst die Topologie, dann platzieren):

1. Vier Plaetze sind vergeben, bevor ueberhaupt etwas zu entscheiden
   ist: J2/J3/J4 aus STECKER_POS, U1 aus PICO_POS. Sie belegen den
   oberen Streifen (J3, J2), die Mitte (U1) und unten rechts (J4).

2. Der 24-V-Strang traegt den Motorstrom des ganzen Stapels
   (Motormodul: bis 2,5 A, s. Aufgabe-5-Bericht). Er laeuft von der
   Einspeiseklemme J1 zum Leistungsstecker J4 und muss kurz sein.
   Deshalb sitzt J1 direkt UNTER J4 an der unteren Kante -- Weg rund
   1 mm statt quer ueber die Platine. Die untere Kante ist ohnehin die
   Klemmenkante des ganzen Stapels (s. Kommentar bei
   stack_spec.STECKER_POS): alle Kabel kommen an derselben Seite heraus.

3. J1 darf nicht weiter nach rechts. Der Freihaltebereich der
   M3-Bohrung (60|56) verbietet jede Lage mit x1 > 56,5 -- bei
   x1 = 58,17 (mittig unter J4) meldete geometry.check_all() genau das.
   x = 45,00 ist die weiteste zulaessige Lage nach rechts.

4. Der Reglerzweig (J1 -> D1 -> C3 -> U2 -> C2 -> +5V -> U1 Pin 39)
   zieht nur den Pico-Strom und darf deshalb der lange Weg sein. Er
   laeuft nach links: D1 (TVS, klemmt die Einspeisung) in das schmale
   Band zwischen Pico-Unterkante und Klemmenkante, C3 (220 uF Stuetzung)
   und U2 (K7805) darunter an die untere Kante, C1/C2 unmittelbar an
   den Reglerpins.

5. R1/R2 sind die I2C-Abschlusswiderstaende -- laut Vertrag NUR auf dem
   Sockel. Sie liegen im oberen Streifen neben J3, direkt ueber den
   I2C-Pins von J2 (Pin 6 bei x = 13,08 und Pin 7 bei x = 15,62). Der
   Weg zu 3V3 ist laenger (J2 Pin 36 bei x = 51,18), das ist bei
   100/400 kHz ohne Belang.

6. Unter dem Pico liegt kein BAUTEIL. Der Platz waere da (8,5 mm
   Luft), aber die Platine hat reichlich freie Flaeche, und ein SMD-Teil
   unter einem gesockelten Bauteil ist im Fehlerfall nicht mehr
   erreichbar. Deshalb ist SMD_CORRIDOR hier None -- s. geometry.py,
   warum ein gesetzter Korridor sonst jedes gewoehnliche SMD-Teil melden
   wuerde. Naehvias liegen dort sehr wohl: sie sind flach, stoeren
   niemanden, und genau dort zerfiel die Masseflaeche am haerteste.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S  # noqa: E402


class Platz:
    """Ein platziertes Bauteil.

    x/y ist die linke obere Ecke des Hofes, w/h seine Groesse, rot die
    Drehung in Grad (KiCad-Konvention), tht=True fuer bedrahtete Teile
    (build.tidy_silkscreen laesst nur deren Referenz auf dem Silkscreen
    stehen, SMD-Referenzen wandern auf F.Fab).
    """

    def __init__(self, ref, x, y, w, h, rot=0, tht=False):
        self.ref, self.rot, self.tht = ref, rot, tht
        self.x, self.y, self.w, self.h = x, y, w, h

    def __repr__(self):
        return "Platz(%s, %.2f, %.2f, %.2fx%.2f, %d)" % (
            self.ref, self.x, self.y, self.w, self.h, self.rot)


def _aus_vertrag(ref, flaeche, rot, tht):
    """Ein Bauteil, dessen Lage der Vertrag festlegt."""
    x0, y0, x1, y1 = flaeche
    return Platz(ref, x0, y0, round(x1 - x0, 3), round(y1 - y0, 3), rot, tht)


# --- Umriss, Lochbild, Regeln: alles aus dem Vertrag -----------------
BOARD_W = S.BOARD_W
BOARD_H = S.BOARD_H
CORNER_R = S.CORNER_R
M3_DRILL = S.M3_DRILL
M3_HOLES = S.M3_HOLES
M3_KEEPOUT = S.M3_KEEPOUT

COURTYARD_GAP = 0.6        # mm Mindestabstand zwischen zwei Hoefen
EDGE_CLEARANCE = 0.5       # mm, kein Kupfer und kein Bauteil naeher an
                           # der Kante (JLCPCB-Vorgabe, uebernommen aus
                           # dem Vorlaeuferprojekt)

# --- Footprints ------------------------------------------------------
# Muessen mit dem Schaltplan uebereinstimmen; build.place() meldet jede
# Abweichung. Genau daran ist am 2026-09-01 der veraltete Sockel-
# schaltplan aufgefallen (s. tests/test_erzeugte_dateien.py).
FP_HDR_2X20 = "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical"
FP_HDR_1X02_SMD = ("Connector_PinHeader_2.54mm:"
                   "PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left")
FP_HDR_2X02_SMD = ("Connector_PinHeader_2.54mm:"
                   "PinHeader_2x02_P2.54mm_Vertical_SMD")
FP_PICO = "Module:RaspberryPi_Pico_Common_THT"

FOOTPRINTS = {
    "C1": "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder",
    "C2": "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder",
    "C3": "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
    "D1": "Diode_SMD:D_SMC_Handsoldering",
    "J1": ("TerminalBlock_Phoenix:"
           "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal"),
    "J2": FP_HDR_2X20,
    "J3": FP_HDR_1X02_SMD,
    "J4": FP_HDR_2X02_SMD,
    "R1": "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder",
    "R2": "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder",
    "U1": FP_PICO,
    "U2": "Converter_DCDC:Converter_DCDC_RECOM_R-78B-2.0_THT",
}

# --- Platzierung -----------------------------------------------------
# Die vier Vertragsteile: ausgerechnet, nicht abgeschrieben. Aendert
# jemand STECKER_POS oder PICO_POS, wandern sie mit.
#
# Bei J3 und J4 traegt der Sockel nur die STIFTseite (er empfaengt
# nichts von oben, er treibt nur nach unten -- s. tools/sch/
# sockelplatine.py, Punkt 3). Deshalb hier S.HOF(<Stiftfootprint>, ...)
# statt der Vertragsflaeche: die ist die VEREINIGUNG beider Haelften
# (S.HOEFE), und eine Vereinigung als Platzierungsanker verschoebe das
# Bauteil um die Differenz. Der Platz BLEIBT trotzdem in voller
# Vereinigungsgroesse reserviert -- kein Modul darf ihn belegen --,
# aber das ist eine Aussage des Vertrags, keine dieser Platine.
_S = S.STECKER_POS
PLACEMENT = {
    "J2": _aus_vertrag("J2", _S["stapel"]["flaeche"],
                       _S["stapel"]["drehung"], True),
    "J3": _aus_vertrag("J3", S.HOF(FP_HDR_1X02_SMD, _S["kette"]["pin1"],
                                   _S["kette"]["drehung"]),
                       _S["kette"]["drehung"], False),
    "J4": _aus_vertrag("J4", S.HOF(FP_HDR_2X02_SMD, _S["leistung"]["pin1"],
                                   _S["leistung"]["drehung"]),
                       _S["leistung"]["drehung"], False),
    "U1": _aus_vertrag("U1", S.PICO_POS["flaeche"], S.PICO_POS["drehung"],
                       True),

    # Die acht platineneigenen Bauteile. Hofmasse aus denselben echten
    # .kicad_mod-Dateien gemessen wie stack_spec.FOOTPRINT_HOF.
    # 24-V-Strang, kurz und rechts:
    "J1": Platz("J1", 45.00, 47.20, 11.17, 12.20, 0, True),
    # Reglerzweig, nach links:
    "D1": Platz("D1", 30.00, 39.40, 13.80, 6.70, 0, False),
    "C3": Platz("C3", 34.00, 48.50, 8.50, 8.50, 0, True),
    "U2": Platz("U2", 18.00, 48.50, 12.00, 9.00, 0, True),
    "C1": Platz("C1", 18.50, 45.00, 3.76, 1.96, 0, False),
    "C2": Platz("C2", 25.00, 45.00, 3.76, 1.96, 0, False),
    # I2C-Abschluss, oben neben dem Kettenstecker:
    "R1": Platz("R1", 17.50, 2.60, 3.70, 1.90, 0, False),
    "R2": Platz("R2", 17.50, 5.40, 3.70, 1.90, 0, False),
}

# --- Der Pico und seine Antenne --------------------------------------
PICO_REF = "U1"

# Die beiden Pad-Reihen des Pico in Platinenkoordinaten. Kupfer auf
# beiden Lagen -- ein SMD-Teil darauf waere nicht bloss zu dicht,
# sondern kurzgeschlossen. Gemessen: Pads 1,60 mm rund, Reihen im
# Footprint bei x = 0 und x = 17,78, Raster 2,54 mm ueber 20 Pins;
# PICO_POS dreht das um 90 Grad, aus den Spalten werden Zeilen.
_PICO_PIN1_X, _PICO_PIN1_Y = S.PICO_POS["pin1"]
_PAD_R = 0.80              # halbe Pad-Kantenlaenge (1,60 mm)
PICO_ROW_TOP = (round(_PICO_PIN1_Y - 17.78 - _PAD_R, 3),
                round(_PICO_PIN1_Y - 17.78 + _PAD_R, 3))
PICO_ROW_BOTTOM = (round(_PICO_PIN1_Y - _PAD_R, 3),
                   round(_PICO_PIN1_Y + _PAD_R, 3))
PICO_PAD_X = (round(_PICO_PIN1_X - _PAD_R, 3),
              round(_PICO_PIN1_X + 19 * S.RASTER + _PAD_R, 3))

# Kein SMD-Teil liegt unter dem Pico -- s. Punkt 6 im Moduldocstring.
SMD_CORRIDOR = None

# Der Antennenausschnitt: gefraest, nicht bloss kupferfrei. Die
# Begruendung steht vollstaendig bei stack_spec.ANTENNE_SPERRBEREICH --
# eine Kupferfreihaltung liesse die Antenne weiter ueber FR4 liegen,
# und das Datenblatt sagt "in any dimension".
ANTENNA_SLOT = S.ANTENNE_SPERRBEREICH

# Derselbe Ausschnitt samt Kantenabstand -- so weit muss auch ein
# Naehvia wegbleiben, denn an einer Fraeskante gilt dieselbe Regel
# wie am Aussenrand (build.antenna_slot_keepout sagt es dem Router).
ANTENNE_SPERRBEREICH_MIT_RAND = (
    ANTENNA_SLOT[0] - EDGE_CLEARANCE, ANTENNA_SLOT[1] - EDGE_CLEARANCE,
    ANTENNA_SLOT[2] + EDGE_CLEARANCE, ANTENNA_SLOT[3] + EDGE_CLEARANCE)

# --- Masseflaechen vernaehen -----------------------------------------
# GND-Vias, die die Flaeche auf F.Cu mit der auf B.Cu verbinden.
#
# WARUM ALS RASTER UND NICHT VON HAND (2026-09-01, Aufgabe 6).
# Ohne Naehte meldete die DRC eine fehlende Verbindung zwischen den
# beiden Masseflaechen: die durchkontaktierten GND-Pads verbinden zwar
# die Lagen, aber unter der dichten Verdrahtung zerfaellt der Guss in
# Teilflaechen, und einzelne davon haengen nur noch an EINEM Pico-Pin.
#
# Von Hand nachgesetzte Naehte haben das nicht geloest, sondern
# verschoben: freerouting liefert bei jedem Lauf ein anderes Bild, und
# nach jedem Nachsetzen sass die naechste Insel woanders. Drei Runden
# lang. Ein Raster faengt die Klasse statt des Einzelfalls -- es ist
# egal, wo der Router die Flaeche das naechste Mal zerschneidet.
#
# Gesperrt sind dieselben Bereiche, gegen die auch geometry.check_all()
# prueft, plus die Pad-Reihen des Pico. UNTER dem Pico ist ausdruecklich
# erlaubt (8,5 mm Luft, dieselbe Ausnahme wie fuer SMD-Teile) -- dort
# lagen die hartnaeckigsten Inseln.
# tests/test_spec_sockel.py rechnet jede erzeugte Lage unabhaengig nach.
STITCH_RASTER = 7.5        # mm Abstand der Naehte
_STITCH_VIA_R = 0.5        # halbe Via-Groesse + Bahnabstand (0,30 + 0,20)


def _naht_erlaubt(vx, vy):
    """Darf an (vx|vy) ein Naehvia sitzen?"""
    rand = EDGE_CLEARANCE + _STITCH_VIA_R
    if not (rand <= vx <= BOARD_W - rand and rand <= vy <= BOARD_H - rand):
        return False
    for hx, hy in M3_HOLES:
        if (vx - hx) ** 2 + (vy - hy) ** 2 < (M3_KEEPOUT / 2.0) ** 2:
            return False
    sx0, sy0, sx1, sy1 = ANTENNE_SPERRBEREICH_MIT_RAND
    if sx0 < vx < sx1 and sy0 < vy < sy1:
        return False
    for ref, p in PLACEMENT.items():
        if ref == PICO_REF:
            continue
        if (p.x - _STITCH_VIA_R < vx < p.x + p.w + _STITCH_VIA_R
                and p.y - _STITCH_VIA_R < vy < p.y + p.h + _STITCH_VIA_R):
            return False
    # Die beiden Pad-Reihen des Pico sind Kupfer auf beiden Lagen.
    for ry0, ry1 in (PICO_ROW_TOP, PICO_ROW_BOTTOM):
        if (PICO_PAD_X[0] - _STITCH_VIA_R < vx < PICO_PAD_X[1] + _STITCH_VIA_R
                and ry0 - _STITCH_VIA_R < vy < ry1 + _STITCH_VIA_R):
            return False
    return True


def _naehte():
    aus = []
    n_x = int((BOARD_W - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    n_y = int((BOARD_H - 2 * EDGE_CLEARANCE) / STITCH_RASTER)
    # Mittig ausrichten, damit das Raster nicht an einer Kante klebt.
    ox = (BOARD_W - (n_x - 1) * STITCH_RASTER) / 2.0
    oy = (BOARD_H - (n_y - 1) * STITCH_RASTER) / 2.0
    for iy in range(n_y):
        for ix in range(n_x):
            vx = round(ox + ix * STITCH_RASTER, 3)
            vy = round(oy + iy * STITCH_RASTER, 3)
            if _naht_erlaubt(vx, vy):
                aus.append((vx, vy))
    return tuple(aus)


STITCH_VIAS = _naehte()

# --- Netzklassen -----------------------------------------------------
# Netznamen wie in der von KiCad exportierten Netzliste (mit Blatt-
# Praefix). autoroute.dsn_netzklassen() bricht ab, wenn eines davon in
# der DSN fehlt -- ein umbenanntes Netz wuerde sonst still mit
# Signalbreite verlegt, genau der Fehler aus dem Muttern-Print.
#
# /PWR24V traegt den Motorstrom des ganzen Stapels (J1 -> J4).
# /+5V speist den Pico ueber VSYS; der K7805 kann 2 A liefern, und die
# Bahn ist der einzige Weg dorthin -- deshalb ebenfalls Leistungsbreite,
# obwohl der Pico selbst weniger zieht.
POWER_NETS = ("/PWR24V", "/+5V")

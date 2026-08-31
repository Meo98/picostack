"""Der Vertrag von PicoStack: Steckerbelegung, Umriss, Modultypen.

Bewusst ohne KiCad-Abhaengigkeit, damit er ohne KiCad geprueft werden
kann -- und damit fremde Werkzeuge ihn lesen koennen, ohne KiCad zu
installieren.

Was hier steht, ist die Zusage an alle, die eigene Module bauen.
Aendert sich etwas davon, sind fremde Module unbrauchbar. Alles andere
im System darf sich aendern.

Grundlage: docs/superpowers/specs/2026-08-28-picostack-design.md
"""

BOARD_W = 64.0
BOARD_H = 60.0
CORNER_R = 3.0

PLATINE_DICKE = 1.6      # mm, Standard-PCB-Dicke (JLCPCB); auch Grundlage
# der Spaltrechnung unten und der Gehaeuse-Konstruktion (Aufgabe 9).

M3_DRILL = 3.2
M3_HOLES = [(4.0, 4.0), (4.0, 56.0), (60.0, 4.0), (60.0, 56.0)]

STAPEL_ABSTAND = 13.0     # mm zwischen zwei Platinen (Platinenoberkante
# zu Platinenoberkante). Zweite Runde, 2026-08-31 -- ersetzt den
# urspruenglichen Wert 15,0 mm. Herleitung, siehe hardware/bauteile-1b.md,
# Beleg 6, zweite Runde, und Beleg 1:
#
# Der Kettenstecker (STECKER_KETTE, gewoehnliche Buchse/Stift-Paarung,
# nicht durchgehend, weil er die Auswahlkette SEL auftrennen muss) trug
# bei 15,0 mm nur 1,1 mm Einstecktiefe -- ein zu duenner Rand, und eine
# laengere einreihige Stiftleiste gibt es bei LCSC/JLCPCB nicht (zwei
# unabhaengige Suchen bestaetigt). Deshalb sinkt STAPEL_ABSTAND, bis
# beide Stecker UND die Schraubklemmen (der urspruengliche Grund fuer
# 15,0 mm) noch passen:
#
#   Spalt G = STAPEL_ABSTAND - PLATINE_DICKE = 13,0 - 1,6 = 11,4 mm
#   Kettenstecker : Einstecktiefe = 14,5 - 11,4 = 3,1 mm  (EINSTECKTIEFE_KETTE())
#   Stapelstecker : Einstecktiefe = 19,36 - 11,4 = 7,96 mm (EINSTECKTIEFE_STAPEL())
#
# Klemmenhoehe belegt (nicht geschaetzt) gegen genau diesen Spalt:
#   DB128L-5.08-2P/-3P (C395868/C395869): 10,10 mm -- Datenblatt DORABO
#     "DB128L-5.08-XXP-C-S" (Zeichnung datiert 2022.11.25, Bemassung
#     "10.10" in der Seitenansicht; ein Zeichnungssatz fuer alle
#     Polzahlen, Hoehe unabhaengig von XX). -> Rest ueber der Klemme:
#     11,4 - 10,10 = 1,3 mm.
#   K7805-2000R3 (C2931187), SIP-3, als hoechstes denkbares Bauteil
#     falls ein Modul es je verwendet: 10,2 mm -- Datenblatt DEXU
#     Electronics "K78xx-2000R3", Rev. A0-2018.12, S. 2 (Tabelle
#     "外观尺寸" / Aussenmasse), "长*宽*高 11.6*7.5*10.2mm". Rest:
#     11,4 - 10,2 = 1,2 mm.
# Beide unter der 11,0-mm-Reissleine -- 13,0 mm haelt fuer beide
# Stecker und fuer die Klemmen. Siehe KLEMME_HOEHE_MM / K7805_HOEHE_MM
# unten fuer die maschinenlesbaren Werte.
#
# ACHTUNG: das Gehaeuse (Aufgabe 9 dieser Etappe) wurde gegen den alten
# Wert 15,0 mm entworfen und muss auf 13,0 mm nachgezogen werden.

# --- Steckerbelegung ------------------------------------------------
# Pico-Pins 1..40. Die Nummern folgen dem Pico-Datenblatt, nicht der
# GPIO-Nummer: der Stecker traegt Pins, nicht GPIO.
#
# Dieser 2x20-Stecker ist seit 2026-08-31 der Stapelstecker (Buchse mit
# durchgehendem Stift, STECKER_STAPEL unten) -- passend fuer alle
# Leitungen, die im ganzen Stapel dasselbe Netz sind (Bus- und
# Global-Signale, Versorgung, freie GPIO). Nur die Auswahlkette (SEL)
# muss von Modul zu Modul aufgetrennt werden (Schieberegister,
# tools/kette.py) und laeuft deshalb NICHT mehr ueber diesen Stecker,
# sondern ueber einen eigenen, zweipoligen STECKER_KETTE mit normaler
# Buchse/Stiftleiste. SEL ist deshalb kein Pin dieses Steckers mehr.
RESERVIERT = (
    "I2C_SDA", "I2C_SCL",     # Bus zu den Modulen
    "FLASH_TX", "FLASH_RX",   # Bootlader der Modul-MCU
    "SEL_CLK",                # global: Takt der Auswahlkette. Jedes
                              # Modul haelt die Auswahl in einem
                              # D-Flipflop; ein Takt schiebt sie eine
                              # Position tiefer (tools/kette.py).
    "FLASH_MODE",             # global: Stapel im Flash-Modus
    "NOTAUS",                 # global, wired-OR, wirkt ohne Software
    "SEL_OUT",                # der Pico-Pin, der die Auswahlkette treibt
                              # (Pin 4 / GP2). KEIN Pin des 2x20-Stapel-
                              # steckers -- laeuft ausserhalb davon auf
                              # STECKER_KETTE (s. Kommentar dort). Bis
                              # 2026-08-31 (Aufgabe-4-Fix-1-Runde) stand
                              # dafuer lokal, unreserviert Pin 11 (GP8)
                              # auf der Sockelplatine; das kollidierte,
                              # sobald Befund 1 derselben Runde jeden
                              # freien GPIO -- auch Pin 11 -- zum Stapel
                              # durchreichte (zwei Ausgaenge auf einem
                              # Netz, sobald ein Modul GP8 selbst nutzt).
                              # Pin 4 (GP2) war vor der Steckertrennung
                              # bereits SEL und bekommt die Rolle jetzt
                              # zurueck, s. Kommentar bei PIN_ROLLE[4]
                              # unten und .superpowers/sdd/
                              # 2026-08-31-etappe-1b-sockel-und-motormodul/
                              # aufgabe-4-fix1-report.md.
)

_GND = {3, 8, 13, 18, 23, 28, 33, 38}
_VERSORGUNG = _GND | {36, 37, 39, 40}    # 3V3_OUT, 3V3_EN, VSYS, VBUS


def IST_VERSORGUNG(pin):
    return pin in _VERSORGUNG


PIN_ROLLE = {}
for _p in range(1, 41):
    PIN_ROLLE[_p] = "GND" if _p in _GND else "frei"
PIN_ROLLE.update({
    36: "3V3", 37: "3V3_EN", 39: "VSYS", 40: "VBUS",
    1:  "FLASH_TX",     # GP0
    2:  "FLASH_RX",     # GP1
    # 4 (GP2) war SEL, dann (Etappe 1b, erste Runde) kurz wieder frei --
    # SEL laeuft seit der Steckertrennung ueber STECKER_KETTE, nicht
    # mehr ueber den 2x20-Stapelstecker. "Frei" war dabei nur halb
    # richtig: die vorige Runde liess den Pin zwar ungenutzt am 2x20-
    # Stecker, verdrahtete ihn dann aber lokal auf der Sockelplatine
    # unreserviert an Pin 11 (GP8) als SEL-Treiber -- eine stille
    # Kollision, sobald ein Modul GP8 selbst braucht (Aufgabe-4-Fix-1-
    # Runde, Befund 2). Pin 4 (GP2) traegt die Rolle deshalb jetzt
    # wieder als echte Vertragsrolle SEL_OUT (s. RESERVIERT oben):
    # treibt STECKER_KETTE direkt vom Pico aus, weiterhin KEIN Pin
    # dieses 2x20-Steckers.
    4:  "SEL_OUT",      # GP2
    5:  "FLASH_MODE",   # GP3
    6:  "I2C_SDA",      # GP4
    7:  "I2C_SCL",      # GP5
    9:  "NOTAUS",       # GP6
    10: "SEL_CLK",      # GP7
    # Pin 30 (RUN) und 35 (ADC_VREF) sind KEINE GPIO, obwohl die
    # Voreinstellung oben sie mangels eigener Rolle als "frei" fuehrte.
    # Das ist dieselbe Luecke wie bei Pin 4 (Befund 2 der Aufgabe-4-Fix-1-
    # Runde), nur eine Stufe weiter: ein Modulautor, der sich auf
    # PIN_ROLLE verlaesst, haelt einen Pin fuer benutzbar, der es nicht
    # ist. RUN ist der Reset des RP2040, aktiv-LOW mit eigenem Pullup
    # (Pico Datasheet Release 21, Abschnitt 2.1, S. 7) -- ein Modul, das
    # ihn als GPIO treibt, setzt den Pico zurueck. ADC_VREF ist die
    # analoge Referenz, kein Digitalanschluss. Beide bleiben deshalb vom
    # Stapelstecker getrennt (s. _stapelstecker in tools/sch/modulsockel.py).
    30: "RUN",
    35: "ADC_VREF",
})

# --- Stapelstecker und Kettenstecker ---------------------------------
# Zwei getrennte Steckverbinder, seit der Entscheidung vom 2026-08-31
# (siehe hardware/bauteile-1b.md): der 2x20-Signalstecker oben ist ein
# echter Stapelstecker (Buchse mit durchgehendem Stift) geworden, weil
# 39 der 40 Leitungen im ganzen Stapel dasselbe Netz sind und daher
# nicht aufgetrennt werden muessen. Nur die Auswahlkette (SEL) muss
# das, und bekommt dafuer einen eigenen kleinen Stecker mit normaler
# (nicht durchgehender) Buchse/Stiftleiste.
STECKER_STAPEL = {
    "typ": "Buchse mit durchgehendem Stift (Stapelstecker), 2x20, 2,54 mm",
    "buchse_lcsc": "C35165",       # ZHOURI/BOOMELE "PC104-2*NA+1"
    "gehaeusehoehe_mm": 8.5,       # Datenblatt, Masszeichnung "8.5+-0.2"
    "stiftlaenge_unter_gehaeuse_mm": 12.46,  # Datenblatt, "12.46+-0.2"
    "quelle": "hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31)",
}

STECKER_KETTE = {
    "typ": "Buchse oben / Stiftleiste unten (auftrennbar), 1x2, 2,54 mm",
    "zweck": "traegt SEL (Auswahlkette) und eine GND daneben",
    "buchse_lcsc": "C541849",      # XFCN PM254V-11-02-H85
    "stift_lcsc": "C492401",       # XFCN PZ254V-11-02P
    "pins": {1: "SEL", 2: "GND"},
    "buchsenhoehe_mm": 8.5,        # Datenblatt, Gehaeuse ueber Platine (F)
    "stiftlaenge_mm": 6.0,         # Datenblatt, Steckende unter Isolier-
                                   # koerper, oberhalb des 3,0 mm Loet-
                                   # schwanzes (M)
    "quelle": "hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31)",
}


def EINSTECKTIEFE_STAPEL():
    """Rechnerische Einstecktiefe des Stapelsteckers bei STAPEL_ABSTAND.

    M+F ueberbruecken den Spalt G = STAPEL_ABSTAND - PLATINE_DICKE; der
    Stift von Modul A fuehrt zuerst durch dessen eigene Platine (M wird
    dadurch um PLATINE_DICKE kuerzer), siehe hardware/bauteile-1b.md,
    Beleg 1, Nachtrag.
    """
    g = STAPEL_ABSTAND - PLATINE_DICKE
    m = STECKER_STAPEL["stiftlaenge_unter_gehaeuse_mm"] - PLATINE_DICKE
    f = STECKER_STAPEL["gehaeusehoehe_mm"]
    return (m + f) - g


def EINSTECKTIEFE_KETTE():
    """Rechnerische Einstecktiefe des Kettensteckers bei STAPEL_ABSTAND.

    Normales Buchse/Stift-Paar (nicht durchgehend): M+F ueberbruecken den
    Spalt G direkt, keine Platinendurchfuehrung wie beim Stapelstecker.
    """
    g = STAPEL_ABSTAND - PLATINE_DICKE
    m = STECKER_KETTE["stiftlaenge_mm"]
    f = STECKER_KETTE["buchsenhoehe_mm"]
    return (m + f) - g



# --- Wo die Stecker auf der Platine sitzen ---------------------------
# Bis hierher legte der Vertrag fest, WELCHE Rolle auf welchem Pin
# liegt und WIE HOCH die Stecker bauen -- aber nirgends, WO sie sitzen.
# Zwei unabhaengig entstehende Layouts (Sockel, Motormodul) passen
# damit nicht zusammen, ein fremdes Modul erst recht nicht. Deshalb
# gehoert die Lage hierher und nicht in die einzelnen
# Platinenbeschreibungen: es gibt EINE Koordinatenmenge fuer ALLE
# Platinen des Stapels. Der Stapelstecker der Sockelplatine steht
# senkrecht ueber dem jedes Moduls, Ketten- und Leistungsstecker
# ebenso -- sonst steckt der Stapel mechanisch nicht.
#
# Koordinatensystem: mm, Ursprung linke obere Ecke der Platine, x nach
# rechts, y nach unten (KiCad-Konvention). Dasselbe System wie
# M3_HOLES oben.
#
# Nur die Lage des Pico (PICO_POS) gilt ausschliesslich fuer die
# Sockelplatine -- er ist das einzige Bauteil, das genau eine Platine
# im Stapel traegt. Er steht trotzdem hier und nicht in
# tools/pcb/spec_sockel.py, weil sein Antennen-Sperrbereich
# (ANTENNE_SPERRBEREICH) gegen dieselben Stecker geprueft werden muss.

M3_KEEPOUT = 7.0   # mm Durchmesser Freihaltebereich um jede M3-Bohrung.
# Nicht der Bohrdurchmesser (M3_DRILL = 3,2 mm), sondern der Platz fuer
# Schraubenkopf/Unterlegscheibe und den Abstandsbolzen. Uebernommen aus
# der gebauten Platine des Vorlaeuferprojekts
# (PecheAuxCanards/tools/pcb/spec.py, M3_KEEPOUT = 7.0); dort gegen
# echte M3-Bolzen erprobt. tools/pcb/geometry.py liest den Wert ueber
# getattr aus der Platinenbeschreibung und faellt sonst auf dieselbe
# 7,0 zurueck -- hier steht er, damit beide PicoStack-Platinen ihn aus
# EINER Quelle bekommen.

# Hoefe (F.CrtYd) der Footprints, jeweils (x0, y0, x1, y1) relativ zum
# Footprint-Ursprung; bei allen vier ist das die Mitte von Pad 1.
# GEMESSEN, nicht geschaetzt: aus den echten .kicad_mod-Dateien der
# KiCad-Standardbibliothek (kicad-footprints, nixpkgs-Ableitung
# a2d01395d2, gelesen mit KiCad 10.0.5), aufgeloest ueber
# tools/pcb/kicadlibs.py. Als Konstanten hier eingetragen und nicht per
# Aufruf geholt, damit der Vertrag ohne KiCad lesbar bleibt.
#
# ACHTUNG, das ist der wunde Punkt dieser Masse: die drei
# Header-Footprints sind PLATZHALTER (dieselben, die
# tools/sch/modulsockel.py als FP_HDR_* eintraegt). Die wirklichen
# Bauteile sind der PC104-Stapelstecker (STECKER_STAPEL, LCSC C35165)
# und die XFCN-Paarung des Kettensteckers (STECKER_KETTE) -- fuer beide
# muss noch ein eigener .kicad_mod gezeichnet werden. Deren Isolier-
# koerper koennen breiter sein als die 6,09 mm der Standard-Stiftleiste.
# tests/test_stack_spec.py prueft deshalb, dass die hier genannten
# Footprint-Namen noch dieselben sind wie in modulsockel.py: wer sie
# gegen die echten austauscht, faellt in den roten Test und muss die
# Lage neu nachrechnen, statt sie stillschweigend zu erben.
FOOTPRINT_HOF = {
    "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical":
        (-1.77, -1.78, 4.32, 50.03),     # 6,09 x 51,81 mm
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical":
        (-1.77, -1.77, 1.77, 4.32),      # 3,54 x 6,09 mm
    "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical":
        (-1.77, -1.77, 4.32, 4.32),      # 6,09 x 6,09 mm
    "Module:RaspberryPi_Pico_Common_THT":
        (-2.65, -3.17, 20.43, 50.68),    # 23,08 x 53,85 mm
}


def LAGE(rechteck, pin1, drehung):
    """Ein footprint-relatives Rechteck in Platinenkoordinaten drehen.

    `drehung` in Grad, KiCad-Konvention (im Bildschirmbild gegen den
    Uhrzeigersinn; die gespeicherte y-Achse zeigt nach unten). Ein
    Punkt (fx, fy) des Footprints landet bei
        0 Grad   -> (px + fx, py + fy)
        90 Grad  -> (px + fy, py - fx)
        180 Grad -> (px - fx, py - fy)
        270 Grad -> (px - fy, py + fx)
    mit (px, py) = Lage von Pad 1. Die Formel ist der Grund, warum die
    Eintraege unten sowohl `pin1`/`drehung` als auch `flaeche` tragen:
    der Test rechnet die eingetragene Flaeche aus den ersten beiden
    nach und faengt so einen Zahlendreher ab.
    """
    x0, y0, x1, y1 = rechteck
    px, py = pin1
    ecken = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    aus = []
    for fx, fy in ecken:
        if drehung == 0:
            aus.append((px + fx, py + fy))
        elif drehung == 90:
            aus.append((px + fy, py - fx))
        elif drehung == 180:
            aus.append((px - fx, py - fy))
        elif drehung == 270:
            aus.append((px - fy, py + fx))
        else:
            raise ValueError("nur 0/90/180/270 Grad, nicht %r" % (drehung,))
    xs = [p[0] for p in aus]
    ys = [p[1] for p in aus]
    return (round(min(xs), 3), round(min(ys), 3),
            round(max(xs), 3), round(max(ys), 3))


def HOF(footprint, pin1, drehung):
    """Hof (F.CrtYd) eines Footprints in Platinenkoordinaten."""
    return LAGE(FOOTPRINT_HOF[footprint], pin1, drehung)


RASTER = 2.54      # mm Rastermass aller drei Stecker (2,54 mm / 0,1")

# Footprint -> (Spalten, Reihen). Zusammen mit RASTER ergibt das die
# Pad-Lagen; die Nummerierung ist die von KiCad fuer die
# Conn_0NxNN_Odd_Even-Familie: Pad 1 links oben, danach zeilenweise
# (Pin 1 und 2 nebeneinander, Pin 3 und 4 die naechste Reihe). An den
# echten .kicad_mod-Dateien nachgesehen, nicht angenommen -- bei
# PinHeader_2x20 liegt Pad 1 bei (0|0), Pad 2 bei (2,54|0), Pad 3 bei
# (0|2,54).
FOOTPRINT_RASTER = {
    "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical": (2, 20),
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical": (1, 2),
    "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical": (2, 2),
}


def PAD_LAGEN(footprint, pin1, drehung):
    """Pin-Nummer -> (x, y) in Platinenkoordinaten.

    Gebraucht fuer die Verdreh-Probe: ob ein um 180 Grad verdreht
    aufgesetztes Modul steckt, entscheidet nicht die Flaeche, sondern
    ob ein Stift ein Rasterloch trifft.
    """
    spalten, reihen = FOOTPRINT_RASTER[footprint]
    aus = {}
    for reihe in range(reihen):
        for spalte in range(spalten):
            pin = reihe * spalten + spalte + 1
            ecke = LAGE((spalte * RASTER, reihe * RASTER,
                         spalte * RASTER, reihe * RASTER), pin1, drehung)
            aus[pin] = (ecke[0], ecke[1])
    return aus


def MITTE(flaeche):
    """Mittelpunkt einer Flaeche (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = flaeche
    return (round((x0 + x1) / 2.0, 3), round((y0 + y1) / 2.0, 3))


def VERDREHT(flaeche):
    """Dieselbe Flaeche, nachdem die Platine um 180 Grad gedreht wurde.

    Das Lochbild M3_HOLES ist punktsymmetrisch zur Platinenmitte -- ein
    Modul laesst sich also verdreht anschrauben. Diese Funktion sagt,
    wo ein Stecker dann liegt; s. Kommentar bei STECKER_POS.
    """
    x0, y0, x1, y1 = flaeche
    return (round(BOARD_W - x1, 3), round(BOARD_H - y1, 3),
            round(BOARD_W - x0, 3), round(BOARD_H - y0, 3))


# Die drei Vertragsstecker. `mitte`, `drehung` und `flaeche` (der
# belegte Hof) sind das, was jede Platine einhalten muss; `pin1` und
# `footprint` sind die Herleitung dazu.
#
# Warum genau diese drei Plaetze:
#
# * Der Stapelstecker liegt QUER (Drehung 90 Grad) und oben. Quer, weil
#   er 51,81 mm lang ist: laege er laengs, belegte er fast die ganzen
#   60 mm Hoehe und zerschnitte jede Platine in zwei schmale Spalten.
#   Oben, weil die untere Kante allen Modulen fuer die Schraubklemmen
#   gehoert (12,20 mm tief, Footprint-Hof der DB128L-Klemmen) -- so
#   bleibt unter ihm EINE grosse zusammenhaengende Flaeche statt zweier
#   halber. Sein Hof haelt 1,18 mm Abstand zum Freihaltebereich der
#   oberen M3-Bohrungen.
# * Der Leistungsstecker sitzt unten rechts, so weit vom Signalstecker
#   weg, wie es auf 64 x 60 mm geht (Design-Doc, Abschnitt "Die beiden
#   Stecker": "Getrennt vom Signalstecker gefuehrt, damit Motorstroeme
#   nicht neben empfindlichen Leitungen liegen"). Er liegt zugleich
#   ausserhalb des Antennen-Sperrbereichs des Pico (6,09 mm Abstand in
#   y) und knapp ueber dem Klemmenstreifen.
# * Der Kettenstecker sitzt im schmalen Streifen ueber dem Stapel-
#   stecker, links. SEL laeuft von dort auf kurzem Weg zum D-Flipflop
#   des Moduls, das seinerseits neben dem Stapelstecker liegt.
#
# ZWEI HAELFTEN AUF EINEM PLATZ -- offener Punkt, nicht uebersehen:
# Ketten- und Leistungsstecker sind laut hardware/bauteile-1b.md
# (Beleg 1, Beleg 4) KEINE Stapelstecker, sondern Buchse-oben/Stift-
# unten-Paare; jedes Modul traegt beide Haelften (J101/J102 bzw.
# J103/J104 in tools/sch/modulsockel.py). Beide Haelften MUESSEN
# denselben Platz belegen, sonst trifft der Stift an der Unterseite von
# Modul N nicht die Buchse an der Oberseite von Modul N+1: alle
# Platinen sind gleich, und eine Verschiebung hebt sich zwischen zwei
# gleichen Platinen nicht auf. Genau deshalb steht hier je EINE
# Flaeche, nicht zwei. Zwei bedrahtete Bauteile koennen sich aber keine
# Bohrungen teilen -- der Widerspruch ist mit den heute gewaehlten
# THT-Bauteilen nicht aufloesbar und im Bericht zu Aufgabe 5c als
# Befund festgehalten (Auswege: SMD-Buchse oben / SMD-Stiftleiste unten
# auf derselben Stelle, oder fuer den Leistungsstecker -- dessen beide
# Haelften ohnehin Pin fuer Pin dieselben Netze fuehren -- ein echter
# 2x2-Stapelstecker wie beim 2x20). Die Lage aendert sich dadurch
# nicht, nur das Bauteil.
STECKER_POS = {
    "stapel": {
        "zweck": "2x20-Stapelstecker, Pico-Pinbild (PIN_ROLLE)",
        "footprint":
            "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical",
        "pin1": (8.00, 13.00),
        "drehung": 90,
        "mitte": (32.125, 11.725),
        "flaeche": (6.22, 8.68, 58.03, 14.77),
    },
    "kette": {
        "zweck": "zweipoliger Kettenstecker, SEL + GND (STECKER_KETTE)",
        "footprint":
            "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        "pin1": (12.50, 2.75),
        "drehung": 0,
        "mitte": (12.5, 4.025),
        "flaeche": (10.73, 0.98, 14.27, 7.07),
    },
    "leistung": {
        "zweck": "2x2-Leistungsstecker, 24 V und GND je doppelt",
        "footprint":
            "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical",
        "pin1": (57.50, 42.00),
        "drehung": 0,
        "mitte": (58.775, 43.275),
        "flaeche": (55.73, 40.23, 61.82, 46.32),
    },
}

# Der Pico -- NUR auf der Sockelplatine.
# Drehung 90 Grad legt seine Laengsachse nach rechts: die USB-Buchse
# zeigt zur linken Platinenkante (ihre Stirnflaeche liegt 1,10 mm
# hinter der Kante, der Stecker erreicht sie also), die Antenne zeigt
# nach rechts. Das ist die Gegenrichtung zur unteren Klemmenkante --
# das USB-Kabel kommt damit nicht dort heraus, wo die Exponat-
# Verkabelung liegt.
PICO_POS = {
    "zweck": "Raspberry Pi Pico, nur auf der Sockelplatine",
    "footprint": "Module:RaspberryPi_Pico_Common_THT",
    "pin1": (3.80, 36.00),
    "drehung": 90,
    "mitte": (27.555, 27.11),
    "flaeche": (0.63, 15.57, 54.48, 38.65),
}

# Sperrbereich unter der WLAN-Antenne des Pico: kein Kupfer, keine
# Bauteile. Auf der Sockelplatine wird daraus im Layout entweder eine
# Kupferfreihaltung oder (wie im Vorlaeuferprojekt) ein gefraester
# Schlitz.
#
# Das ist die teuerste Lektion des Vorgaengerprojekts: die Antenne
# sitzt ZWISCHEN den beiden Pin-Reihen, nicht am Rand -- ein Ueberhang,
# der sie ins Freie bringen soll, nimmt zwangslaeufig acht Pins mit
# hinaus (PecheAuxCanards, docs/.../2026-08-27-board-redesign-design.md,
# "Nachtrag 2026-08-28: Schlitz statt Ueberhang").
#
# Masse, belegt statt geschaetzt -- (x0, y0, x1, y1) relativ zu Pad 1
# des Pico-Footprints:
#
# 1. Groesse aus dem Datenblatt: "Raspberry Pi Pico W Datasheet",
#    Raspberry Pi Ltd, Release 7, Build date 03/07/2026, Abschnitt
#    2.2.1 "Keep-out area": "There is a cutout for the antenna
#    (14 mm x 9 mm). If anything is placed close to the antenna (in any
#    dimension) the effectiveness of the antenna is reduced."
#    Wortgleich im "Raspberry Pi Pico 2 W Datasheet", Release 2,
#    Build date 03/07/2026, ebenfalls Abschnitt 2.2.1.
# 2. Lage: Abschnitt 2 "Mechanical specification" desselben
#    Datenblatts -- "a single sided 51 mm x 21 mm x 1 mm PCB with a
#    micro USB port overhanging the top edge ... The onboard wireless
#    antenna is located on the bottom edge." Der Ausschnitt liegt also
#    buendig an der der USB-Buchse gegenueberliegenden Kante und mittig
#    ueber die 21 mm Breite. Im Footprint Module:RaspberryPi_Pico_
#    Common_THT liegt diese Platinenkante bei y = 49,63 und die Mitte
#    der 21 mm bei x = 8,89 (F.Fab-Umriss x -1,61..19,39,
#    y -1,37..49,63, relativ zu Pad 1).
# 3. Breite: die offizielle KiCad-Fassung des Pico W
#    (Module:RaspberryPi_Pico_W_SMD.kicad_mod, kicad-footprints
#    a2d01395d2) traegt eine benannte Sperrzone "Antenna Copper Keep
#    Out"; ihr umschliessendes Rechteck ist 14,2 x 8,0 mm -- 0,2 mm
#    breiter, aber 1,0 mm flacher als die Datenblattangabe. Der Vertrag
#    nimmt die VEREINIGUNG beider Angaben: 14,2 mm breit (KiCad),
#    9,0 mm tief (Datenblatt). Keine der beiden Zahlen ist geraten.
#
#    -> x: 8,89 +- 7,1  = 1,79 .. 15,99
#    -> y: 49,63 - 9,00 = 40,63 .. 49,63
PICO_ANTENNE_HOF = (1.79, 40.63, 15.99, 49.63)

# Derselbe Bereich in Platinenkoordinaten der Sockelplatine, aus
# PICO_POS gedreht (9,00 x 14,20 mm, weil PICO_POS 90 Grad gedreht
# ist). Geprueft in tests/test_stack_spec.py: er ueberschneidet weder
# einen der drei Stecker noch einen Freihaltebereich der M3-Bohrungen.
ANTENNE_SPERRBEREICH = (44.43, 20.01, 53.43, 34.21)

# --- Wieviel Platz bleibt uebrig ------------------------------------
# Ein Vertrag, der die Stecker so hinlegt, dass kein Modul mehr
# hineinpasst, ist wertlos. Untergrenze, hergeleitet statt geraten:
#
# MODUL_HOF_SUMME_MM2 ist die Summe der Bauteil-Hoefe des heute
# anspruchsvollsten Moduls (Motormodul, hardware/kicad/motor/
# Motormodul.kicad_sch, 43 Bauteile) OHNE die drei Vertragsstecker --
# gemessen aus denselben echten Footprints wie FOOTPRINT_HOF oben.
MODUL_HOF_SUMME_MM2 = 956.8
# BELEGUNGSGRAD_ERPROBT ist der Anteil der Platinenflaeche, den die
# Hoefe auf einer WIRKLICH gebauten, verlegten und DRC-sauberen
# 2-Lagen-Platine desselben Umrisses belegen: die Vereinigung aller
# Hoefe in PecheAuxCanards/tools/pcb/spec.py (PLACEMENT) deckt
# 2172,8 mm2 von 64 x 60 = 3840 mm2. Mehr als das passt erfahrungs-
# gemaess nicht mehr, ohne dass die Verdrahtung nicht mehr aufgeht.
BELEGUNGSGRAD_ERPROBT = 0.566
# Daraus die Untergrenze: 956,8 / 0,566 = 1690,5 mm2, aufgerundet.
FREIE_FLAECHE_MINDEST = 1700.0
# Dieselbe Rechnung fuer die Sockelplatine, die zusaetzlich den Pico
# und dessen Antennen-Sperrbereich verliert: ihre eigenen acht Bauteile
# (J1, D1, C3, C1, C2, R1, R2, U2 -- ohne die drei Vertragsstecker und
# ohne den Pico selbst) summieren sich auf 437,8 mm2 Hof, das sind bei
# demselben erprobten Belegungsgrad 773,5 mm2 Bedarf. Sie hat nach
# Abzug von Pico und Sperrbereich noch 1776,2 mm2 am Stueck.
SOCKEL_HOF_SUMME_MM2 = 437.8
# Die hier festgelegte Anordnung laesst einem Modul 3077,7 mm2 am
# Stueck (80,1 % der Platine), groesstes freies Rechteck 47,6 x 44,1 mm
# -- Faktor 1,8 ueber der Untergrenze. Nachgerechnet in
# tests/test_stack_spec.py mit tools/pcb/geometry.freie_flaeche().

# --- Verdreht aufgesteckt --------------------------------------------
# M3_HOLES ist punktsymmetrisch zur Platinenmitte: (4|4) und (60|56)
# tauschen unter einer 180-Grad-Drehung die Plaetze, (4|56) und (60|4)
# ebenso. Ein Modul laesst sich also seitenrichtig, aber um 180 Grad
# verdreht auf die Abstandsbolzen schrauben. Auf dem Stapelstecker
# wuerde das Pin 1 auf Pin 40 legen -- VBUS auf FLASH_TX -- und den
# Stapel zerstoeren. Der Umriss ist Vertrag und laesst sich nicht
# unsymmetrisch machen; die Steckerlage dagegen schon, und genau dafuer
# liegen die drei Stecker oben BEWUSST UNSYMMETRISCH:
#
#   VERDREHT(...) der drei Flaechen ergibt
#     stapel   -> (5.97, 45.23, 57.78, 51.32)
#     kette    -> (49.73, 52.93, 53.27, 59.02)
#     leistung -> (2.18, 13.68,  8.27, 19.77)
#
#   Keine dieser drei Flaechen deckt sich mit der eines Steckers.
#   Entscheidend ist aber nicht die Flaeche, sondern das Raster: der
#   kleinste Abstand zwischen einem verdrehten Pad und irgendeinem Pad
#   betraegt 2,881 mm. Das ist mehr als das halbe Raster (1,27 mm), das
#   ein Stift braucht, um in einen Buchsenkontakt zu finden -- ein
#   verdreht aufgesetztes Modul steckt NIRGENDS. Es bleibt tot, statt
#   kaputtzugehen. tests/test_stack_spec.py rechnet beides nach, damit
#   eine kuenftige Verschiebung das nicht stillschweigend aufhebt.
#
# Tot ist besser als kaputt, aber nicht gut genug: sichtbar wird der
# Fehler dadurch nicht. Die zugehoerige Layout-Auflage steht in
# AUFLAGEN unten (Pin-1-Kennzeichnung, kein freiliegendes Kupfer in den
# drei verdrehten Flaechen).
VERDREHT_MINDESTABSTAND_MM = 2.881   # gerechnet, s. Test

# --- Belegte Bauhoehen im Stapelspalt (gegen STAPEL_ABSTAND) --------
# Beide Werte aus echten Datenblaettern gelesen, nicht geschaetzt --
# Herleitung siehe Kommentar bei STAPEL_ABSTAND und hardware/bauteile-1b.md,
# Beleg 6, zweite Runde.
KLEMME_HOEHE_MM = 10.10   # DB128L-5.08-2P/-3P (C395868/C395869), Datenblatt
                          # DORABO "DB128L-5.08-XXP-C-S" (2022.11.25),
                          # Seitenansicht, Bemassung "10.10" -- ein
                          # Zeichnungssatz fuer alle Polzahlen, Hoehe
                          # unabhaengig von der Polzahl XX.
K7805_HOEHE_MM = 10.2     # K7805-2000R3 (C2931187), SIP-3, Datenblatt DEXU
                          # Electronics "K78xx-2000R3", Rev. A0-2018.12,
                          # S. 2, Tabelle "外观尺寸": "长*宽*高
                          # 11.6*7.5*10.2mm" (Laenge*Breite*Hoehe).

# --- Auflagen an die Modulfirmware ----------------------------------
# Teil des Vertrags, aber keine Geometrie und keine Pinnummer: Regeln,
# die Modulfirmware einhalten muss, damit ein fremdes Modul den Stapel
# nicht lahmlegt.
AUFLAGEN = (
    "Ausserhalb des Flash-Modus darf ein Modul die Leitung FLASH_RX "
    "nicht treiben. FLASH_RX ist der Empfangspin des Pico und damit "
    "die gemeinsame Sendeleitung aller Module. Im Normalbetrieb sind "
    "alle Module gleichzeitig wach; treibt mehr als eines diese "
    "Leitung, fallen sie einander ins Wort und koennen einander im "
    "Gegentakt beschaedigen. Senden darf ein Modul nur, solange es "
    "ueber die Auswahlkette ausgewaehlt ist (FLASH_MODE = 1 und das "
    "eigene Flipflop Q = 1). Sonst bleibt der Pin hochohmig.",
)

# Auflagen an das LAYOUT eines Moduls -- ebenfalls Vertrag, aber
# Kupfer und Bestueckungsdruck statt Software. Getrennt von
# AUFLAGEN, weil das eine der Firmware gilt und das andere der
# Platine.
LAYOUT_AUFLAGEN = (
    "Jede Platine traegt neben Pin 1 des Stapelsteckers eine "
    "Kennzeichnung im Bestueckungsdruck (Dreieck plus Text \"1\") und "
    "an der Klemmenkante (untere Kante, y = BOARD_H) die "
    "Beschriftung \"KLEMMEN\". Grund: das "
    "M3-Lochbild ist punktsymmetrisch, ein Modul laesst sich also um "
    "180 Grad verdreht anschrauben. Die Steckerlage (STECKER_POS) ist "
    "bewusst so unsymmetrisch, dass dann kein einziger Stift in einen "
    "Buchsenkontakt findet -- das verhindert den Schaden, macht den "
    "Fehler aber nicht sichtbar. Ausserdem darf in den drei Flaechen "
    "VERDREHT(STECKER_POS[...][\"flaeche\"]) kein freiliegendes Kupfer "
    "liegen (keine Testpunkte, keine offenen Pads): dort setzen die "
    "Stifte eines verdreht aufgesteckten Moduls auf.",
)

# --- Modultypen -----------------------------------------------------
# 0x00 ist ungueltig (ein unbeschriebener Kennwiderstand liest 0).
# 0x80 und darueber bleibt fremden Modulen vorbehalten.
MODULTYPEN = {
    0x01: {"name": "Motor",    "kanaele": 1},
    0x10: {"name": "Dimmer1",  "kanaele": 1},
    0x11: {"name": "Dimmer3",  "kanaele": 3},
    0x12: {"name": "Dimmer4",  "kanaele": 4},
}

# --- Kennwiderstaende -----------------------------------------------
# Zwei Teiler gegen einen festen Oberwiderstand, je 16 Stufen aus der
# E24-Reihe. Die Stufen sind so gewaehlt, dass sich benachbarte
# Spannungsteiler um mehr als 3 % unterscheiden -- weit mehr als die
# Streuung von 1-%-Widerstaenden und die Aufloesung des ADC.
# Die Werte sind nicht die E24-Reihe der Reihe nach, sondern so
# gewaehlt, dass die SPANNUNGSTEILER gleichmaessig liegen. Nimmt man
# stumpf E24, draengen sich die oberen Stufen: zwischen 150 k und 220 k
# liegen nur 1,9 % Spannungsunterschied, weniger als die Streuung von
# 1-%-Widerstaenden zusammen mit dem ADC-Fehler.
ID_OBEN = 10000.0
ID_WIDERSTAENDE = (
    0.0, 680.0, 1500.0, 2200.0, 3300.0, 4700.0, 6200.0, 7500.0,
    10000.0, 13000.0, 16000.0, 22000.0, 30000.0, 43000.0, 68000.0,
    150000.0,
)


def ID_ANTEIL(r):
    """Spannungsanteil am ADC fuer einen Kennwiderstand."""
    return r / (r + ID_OBEN)

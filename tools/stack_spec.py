"""Der Vertrag von PicoStack v3: Umriss, Pico-Lage, Pinrollen, Baenke.

Bewusst ohne KiCad-Abhaengigkeit, damit er ohne KiCad geprueft werden
kann -- und damit fremde Werkzeuge ihn lesen koennen.

Was hier steht, ist die Zusage an alle, die eigene Module bauen.
Aendert sich etwas davon, sind fremde Module unbrauchbar. Alles andere
im System darf sich aendern.

Grundlage: docs/superpowers/specs/2026-11-15-picostack-v3-design.md.
Vorgaenger (v1-v2.1, VERTRAG_VERSION 1-3) im Git-Verlauf und im Tag
v0.2.0. Was v3 gegenueber v2.1 streicht und warum, steht in der Spec,
Abschnitt "Warum v3"; kurz: kein Modul-MCU, keine Auswahlkette, keine
SMD-Steckerpaare, keine Randpads. Der Pico treibt jeden Kanal direkt
ueber GPIO-Baenke.

Koordinaten: Millimeter, Ursprung (0|0) = linke obere Ecke der
Platine, x nach rechts, y nach UNTEN (KiCad-Konvention).
"""
import math

VERTRAG_VERSION = 4
PROJEKTNAME = "PicoStack"

# --- Umriss und Mechanik ---------------------------------------------
BOARD_W = 74.0
BOARD_H = 50.0
CORNER_R = 3.0
PLATINE_DICKE = 1.6      # mm, JLCPCB-Standard; Basis der Stapelrechnung

M3_DRILL = 3.2
M3_RAND_ABSTAND = 4.0    # mm von jeder Kante
M3_KEEPOUT = 7.0         # mm Durchmesser Freihaltekreis (Bolzen/Schraubenkopf)


def M3_HOLES_FUER(w, h):
    """Die vier M3-Eckloecher eines w x h-Umrisses, 4,0 mm von jeder Kante.
    Punktsymmetrisch zur Plattenmitte -- deshalb muss STECKER_POS so
    liegen, dass ein verdreht angeschraubtes Modul nirgends steckt
    (s. VERDREHT_STECKT_NIRGENDS)."""
    a = M3_RAND_ABSTAND
    return [(a, a), (a, h - a), (w - a, a), (w - a, h - a)]


M3_HOLES = M3_HOLES_FUER(BOARD_W, BOARD_H)
# (4|4) (4|46) (70|4) (70|46)

# --- Stapel -----------------------------------------------------------
# Ein Bauteiltyp fuer alle Stapelverbindungen: Buchsenleiste mit langem,
# durchgehendem Stift (Arduino-/Pimoroni-"Stacking Header"). Die
# Pico-Reihen sind 1x20, die Leistungsreihe ein auf 1x4 abgelaengtes
# Stueck derselben Leiste.
STECKER_STAPEL = {
    "typ": "Buchsenleiste 2,54 mm mit durchgehendem Stift (Stacking Header)",
    "durchgehend": True,
    "montage_oben": "THT",
    "montage_unten": "THT",
    "haelften_gleiche_netze": True,
    "mpn": "Pimoroni Pico Stacking Headers (Paar 1x20)",
    "lcsc": None,                  # keine LCSC-Quelle; Handbestueckung
    "strom_pro_kontakt_a": 3.0,    # Pimoroni-Produktseite: "3A"
    "gehaeusehoehe_mm": 8.5,       # Pimoroni: "female header height 8.5mm"
    "stiftlaenge_unter_gehaeuse_mm": 11.0,   # Pimoroni: "pin length 11mm"
    "quelle": "https://shop.pimoroni.com/products/pico-stacking-headers "
              "(Spec-Tabelle, 2026-11-15); ZU VERIFIZIEREN am Teil",
}

STAPEL_ABSTAND = 12.0     # mm Platinenoberkante zu Platinenoberkante
# Warum 12 und nicht 11: der Stift fuehrt erst durch die eigene Platine
# (11,0 - 1,6 = 9,4 mm bleiben), dann in die Buchse darunter. Bei 11,0
# waere der Spalt 9,4 mm -- der Stift stiesse genau auf die Platine
# darunter. Bei 12,0 bleiben 1,0 mm Luft unter dem Stift, 7,5 mm
# Einstecktiefe und 1,9 mm zwischen Buchsenoberkante und Platine
# darueber (Loetstellen). M3-Bolzen 12 mm sind Katalogware.


def SPALT():
    """Luft zwischen zwei Platinen (Oberkante unten bis Unterkante oben)."""
    return STAPEL_ABSTAND - PLATINE_DICKE


def STIFT_UNTER_PLATINE():
    """Stiftlaenge, die unter der eigenen Platine herausragt."""
    return STECKER_STAPEL["stiftlaenge_unter_gehaeuse_mm"] - PLATINE_DICKE


def EINSTECKTIEFE_STAPEL():
    """Wie tief der Stift in die Buchse darunter eintaucht."""
    return STIFT_UNTER_PLATINE() + STECKER_STAPEL["gehaeusehoehe_mm"] - SPALT()


def LUFT_STIFTENDE():
    """Abstand Stiftende zur Platine darunter (muss > 0 sein)."""
    return SPALT() - STIFT_UNTER_PLATINE()


def LUFT_BUCHSENOBERKANTE():
    """Abstand Buchsenoberkante zur Platine darueber (muss > 0 sein)."""
    return SPALT() - STECKER_STAPEL["gehaeusehoehe_mm"]


BAUTEILHOEHE_OBEN_MAX = 9.5     # mm: SPALT() 10,4 minus 0,9 Reserve
BAUTEILHOEHE_PICO_SCHATTEN_MAX = 8.0   # mm unter dem Pico (Buchse 8,5)

# --- Pico-Lage ----------------------------------------------------------
# Der Pico liegt QUER: USB zeigt zur linken Kante (x=0), Antenne nach
# rechts. Reihe "unten" (Pins 1..20) laeuft nach +x, Reihe "oben"
# (Pins 21..40) nach -x -- das ist das Pico-Pinbild von oben gesehen,
# um 90 Grad gegen den Uhrzeigersinn gedreht.
RASTER = 2.54
PICO_REIHENABSTAND = 17.78     # Pico-Datenblatt
PICO_LAENGE = 51.0
PICO_BREITE = 21.0
PICO_PIN1 = (9.00, 27.78)      # Pin 1 (GP0), Reihe unten
PICO_PIN21 = (57.26, 10.00)    # Pin 21 (GP16), Reihe oben
USB_UEBERSTAND = 1.3           # mm, Micro-USB ragt ueber die Pico-Kante

# Das Pico-Brett ragt 1,37 mm ueber die Endpins und 1,61 mm ueber die
# Reihen hinaus ((51-48,26)/2 bzw. (21-17,78)/2).
PICO_SCHATTEN = (7.63, 8.39, 58.63, 29.39)
# Pico W: Antenne am USB-fernen Ende zwischen den Reihen. Datenblatt
# 2.2.1 verlangt eine kupferfreie Zone unter der Antenne; hier beide
# Lagen, bis 2 mm ueber das Brettende hinaus.
ANTENNE_FREI = (46.0, 8.39, 60.6, 29.39)

# --- Pinrollen (Pico-Pinnummern 1..40) -------------------------------------
_GND = {3, 8, 13, 18, 23, 28, 33, 38}
NICHT_BELEGBAR = {
    30: "RUN -- Reset des RP2040, aktiv-LOW mit eigenem Pullup.",
    33: "AGND -- analoge Masse, nicht als Rueckleiter fuer Lasten.",
    35: "ADC_VREF -- analoge Referenzspannung, kein Digitalanschluss.",
    37: "3V3_EN -- schaltet den Pico-Regler ab; ein Ausschalter fuer "
        "den ganzen Stapel, den jedes Modul versehentlich ziehen koennte.",
    40: "VBUS -- liegt nur an, wenn am Pico ein USB-Kabel steckt.",
}


def IST_BELEGBAR(pin):
    return pin not in NICHT_BELEGBAR and pin not in _GND


# GP-Nummer -> Pico-Pin (alle 26 GPIO des Pico).
GP_PIN = {
    0: 1, 1: 2, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 11, 9: 12,
    10: 14, 11: 15, 12: 16, 13: 17, 14: 19, 15: 20, 16: 21, 17: 22,
    18: 24, 19: 25, 20: 26, 21: 27, 22: 29, 26: 31, 27: 32, 28: 34,
}
PIN_GP = {pin: gp for gp, pin in GP_PIN.items()}

RESERVIERT = {
    4: "I2C_SDA",     # Qwiic-Port
    5: "I2C_SCL",
    6: "NOTAUS",      # open-drain, wired-AND, LOW = gesperrt
}

# Baenke: vier PWM-faehige GPIO je Bank. Ein Modul belegt genau EINE
# Bank, gewaehlt ueber seine Slot-Matrix (s. unten).
BAENKE = {
    "A": (8, 9, 10, 11),
    "B": (12, 13, 14, 15),
    "C": (16, 17, 18, 19),
    "D": (20, 21, 22, 7),
}
ADC_BANK = (26, 27, 28)
USER_GP = (0, 1, 2, 3)      # am User-Header, kein Modul belegt sie

# Vorgabe ab Werk, damit "ein Motor + ein Dimmer" ohne Loeten laeuft.
BANK_VORGABE = {"Motor": "A", "Dimmer": "B"}
ADC_VORGABE = {"Motor": 26}


def PWM_KANAL(gp):
    """(Slice, Kanal) des RP2040-PWM fuer einen GPIO. Zwei GPIO mit
    demselben Paar teilen sich einen Zaehler und koennen nicht
    unabhaengig dimmen -- die Baenke sind so gewaehlt, dass das nie
    vorkommt (Test)."""
    return ((gp >> 1) & 7, gp & 1)


PIN_ROLLE = {}
for _p in range(1, 41):
    PIN_ROLLE[_p] = "GND" if _p in _GND else "frei"
PIN_ROLLE.update({36: "3V3", 37: "3V3_EN", 39: "VSYS", 40: "VBUS",
                  30: "RUN", 35: "ADC_VREF", 33: "AGND"})
for _gp, _rolle in RESERVIERT.items():
    PIN_ROLLE[GP_PIN[_gp]] = _rolle
for _bank, _gps in BAENKE.items():
    for _i, _gp in enumerate(_gps):
        PIN_ROLLE[GP_PIN[_gp]] = "BANK_%s_S%d" % (_bank, _i + 1)
for _i, _gp in enumerate(ADC_BANK):
    PIN_ROLLE[GP_PIN[_gp]] = "ADC_%d" % _gp
for _gp in USER_GP:
    PIN_ROLLE[GP_PIN[_gp]] = "USER_GP%d" % _gp

# --- Slot-Matrix ----------------------------------------------------------
# Je Modulsignal S_k (k = 1..4) vier 0603-Plaetze JB<k><Bank> nach
# BAENKE[Bank][k-1]; genau einer ist mit 0 Ohm bestueckt. Fuer das
# Analogsignal drei Plaetze JA26/JA27/JA28.
MATRIX_FOOTPRINT = "Resistor_SMD:R_0603_1608Metric"
MATRIX_WERT = "0"
MATRIX_LCSC = "C21189"       # 0 Ohm 0603, JLCPCB-Basic


def MATRIX_REF(signal, bank):
    return "JB%d%s" % (signal, bank)


def MATRIX_GP(signal, bank):
    """GPIO, den Signal `signal` (1..4) auf Bank `bank` bekommt."""
    return BAENKE[bank][signal - 1]


def ADC_REF(gp):
    return "JA%d" % gp


# --- Versorgung -------------------------------------------------------------
VERSORGUNG = {
    "eingang_v": (6.0, 30.0),          # Zusage an der Klemme
    "regler": "TPS5430DDAR",           # JLCPCB-Basic C9864, 5,5-36 V, 3 A
    "regler_eingang_v": (5.5, 36.0),   # TI SLVS632L, S. 4
    "regler_abs_max_v": 40.0,
    "ausgang_v": 4.92,                 # 1,221 V x (1 + 10 k / 3,3 k)
    "schutz_fet": "AOD409",            # P-Kanal TO-252, LCSC C36220
    "schutz_drain_an": "PWR_IN",       # Drain an der Einspeisung (Body-
                                       # diode sperrt bei Verpolung)
    "gate_klemmung": "Zener 12 V Gate-Source",   # Vgs = -min(Vin, 12 V)
    "vsys_diode": True,                # Schottky zwischen Regler und VSYS
    "usb_parallel": True,              # USB am Pico darf gleichzeitig anliegen
    "tvs": "SMCJ30A",                  # nur Transienten; klemmt > 36 V
}

STROMBUDGET = {
    "modul_gesamt_a": 4.0,
    "stamm_netze": ("/PWR_IN", "/VIN"),
    "stapel_durchleitung_a": 3.0,
    "kanal_a": 3.0,
    "motor_a": 2.538,
    "q90_rdson_ohm": 0.040,
    "q90_verlust_max_w": 1.5,
    "q90_quelle": "AOD409 (AOS), RDS(on) 40 mOhm @ 10 V (LCSC-Attribut "
                  "C36220); 1,5 W fuer TO-252 auf Kupferflaeche "
                  "(konservativ, wie IRFR5305-Datenblatt PD-95025A)",
    "klemme_a": 10.0,
    "klemme_quelle": "LCSC C474892 (KF350-3.5-2P): '10A'",
}

# --- Steckerlagen -----------------------------------------------------------
FP_STAPEL_20 = "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical"
FP_STAPEL_4 = "Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical"
FP_QWIIC = "Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal"
FP_USER = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"

# Hoefe (F.CrtYd) footprint-lokal, mit pcbnew gemessen (2026-11-15,
# KiCad-Bibliothek 25a0b01dd7), um HOF_STRICH 0,045 geschrumpft.
FOOTPRINT_HOF = {
    FP_STAPEL_20: (-1.77, -1.77, 1.77, 50.03),
    FP_STAPEL_4: (-1.77, -1.77, 1.77, 9.39),
    FP_QWIIC: (-3.90, -3.28, 3.90, 3.28),
    FP_USER: (-1.77, -1.77, 1.77, 14.47),
}
FOOTPRINT_RASTER = {
    FP_STAPEL_20: (1, 20),
    FP_STAPEL_4: (1, 4),
    FP_USER: (1, 6),
}
SPALTEN_GESPIEGELT = frozenset()
PAD_SCHWERPUNKT_VERSATZ = {}


def LAGE(rechteck, pin1, drehung):
    """Footprint-relatives Rechteck in Platinenkoordinaten drehen.
    KiCad-Konvention: Drehung gegen den Uhrzeigersinn in der Aufsicht,
    y-Achse nach unten. Ein Punkt (fx, fy) landet bei
        0   -> (px + fx, py + fy)      90  -> (px + fy, py - fx)
        180 -> (px - fx, py - fy)      270 -> (px - fy, py + fx)
    mit (px, py) = Lage von Kontakt 1."""
    x0, y0, x1, y1 = rechteck
    px, py = pin1
    aus = []
    for fx, fy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
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
    return LAGE(FOOTPRINT_HOF[footprint], pin1, drehung)


def HOEFE(footprints, pin1, drehung):
    k = [HOF(f, pin1, drehung) for f in footprints]
    return (round(min(x[0] for x in k), 3), round(min(x[1] for x in k), 3),
            round(max(x[2] for x in k), 3), round(max(x[3] for x in k), 3))


def PAD_LAGEN(footprint, pin1, drehung):
    """Kontakt-Nummer -> (x, y) in Platinenkoordinaten."""
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
    x0, y0, x1, y1 = flaeche
    return (round((x0 + x1) / 2.0, 3), round((y0 + y1) / 2.0, 3))


def VERDREHT(flaeche):
    """Dieselbe Flaeche nach 180-Grad-Drehung der Platine."""
    x0, y0, x1, y1 = flaeche
    return (round(BOARD_W - x1, 3), round(BOARD_H - y1, 3),
            round(BOARD_W - x0, 3), round(BOARD_H - y0, 3))


# Stapelreihen: Pin-1-Lage, Drehung so, dass die Pins in die genannte
# Richtung laufen (Footprint-Pins liegen lokal auf +y; 90 Grad ->
# +x, 270 Grad -> -x). "flaeche" ist der Hof, von Tests nachgerechnet.
STECKER_POS = {
    "stapel_unten": {
        "zweck": "Stapelbuchse 1x20, Pico-Pins 1..20, nach +x",
        "stecker": "STECKER_STAPEL",
        "footprints": (FP_STAPEL_20,),
        "pin1": PICO_PIN1,
        "drehung": 90,
        "pico_pins": tuple(range(1, 21)),
        "flaeche": (7.23, 26.01, 59.03, 29.55),
    },
    "stapel_oben": {
        "zweck": "Stapelbuchse 1x20, Pico-Pins 21..40, nach -x",
        "stecker": "STECKER_STAPEL",
        "footprints": (FP_STAPEL_20,),
        "pin1": PICO_PIN21,
        "drehung": 270,
        "pico_pins": tuple(range(21, 41)),
        "flaeche": (7.23, 8.23, 59.03, 11.77),
    },
    "leistung": {
        "zweck": "Stapelbuchse 1x4: VIN, VIN, GND, GND (Durchleitung)",
        "stecker": "STECKER_STAPEL",
        "footprints": (FP_STAPEL_4,),
        "pin1": (26.00, 4.00),
        "drehung": 90,
        "pins": {1: "VIN", 2: "VIN", 3: "GND", 4: "GND"},
        "flaeche": (24.23, 2.23, 35.39, 5.77),
    },
}

STECKER_LEISTUNG = {
    "typ": "Stapelbuchse 1x4 (STECKER_STAPEL, abgelaengt)",
    "pins": STECKER_POS["leistung"]["pins"],
    "strom_pro_kontakt_a": STECKER_STAPEL["strom_pro_kontakt_a"],
    "kontakte_je_ader": 2,
}

# Qwiic und User-Header sind keine Stapelstecker; ihre Lage darf ein
# Modul frei waehlen (Empfehlung: obere Kante). Pinbelegung ist Vertrag.
QWIIC_PINS = {1: "GND", 2: "3V3", 3: "I2C_SDA", 4: "I2C_SCL"}
USER_PINS = {1: "GP0", 2: "GP1", 3: "GP2", 4: "GP3", 5: "3V3", 6: "GND"}


def VERDREHT_STECKT_NIRGENDS(mindestabstand=2.0):
    """Ein um 180 Grad verdreht aufgesetztes Modul darf mit keinem Stift
    einen Buchsenkontakt treffen. Liefert den kleinsten Abstand
    zwischen einem verdrehten Stift und einem Kontakt."""
    kontakte = []
    for e in STECKER_POS.values():
        kontakte += list(PAD_LAGEN(e["footprints"][0], e["pin1"],
                                   e["drehung"]).values())
    d_min = float("inf")
    for x, y in kontakte:
        vx, vy = BOARD_W - x, BOARD_H - y
        for kx, ky in kontakte:
            d_min = min(d_min, math.hypot(vx - kx, vy - ky))
    return round(d_min, 3), d_min >= mindestabstand


# --- Klemmen ------------------------------------------------------------------
FP_KLEMME_35 = ("TerminalBlock_Phoenix:"
                "TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal")
FP_KLEMME_508 = ("TerminalBlock_Phoenix:"
                 "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal")
KLEMME_OEFFNUNG = {
    FP_KLEMME_35.split(":")[1]: (0.0, 1.0),
    FP_KLEMME_508.split(":")[1]: (0.0, 1.0),
}
KLEMME_KANTENABSTAND_MAX = 0.10
KLEMME_UEBERSTAND_MAX = 0.00
# Klemmenreihe: untere Kante, zwischen den M3-Freihaltekreisen.
# Tiefe = Hof der PT-1,5-Klemme (8,60 mm) + Reserve.
KLEMMENZONE = (7.5, 41.0, 66.5, 50.0)


def KLEMME_OEFFNUNG_GLOBAL(footprint, drehung_grad, gespiegelt=False):
    """Oeffnungsrichtung einer Klemme in Platinenkoordinaten."""
    if gespiegelt:
        raise NotImplementedError(
            "Oeffnungsrichtung einer auf der Rueckseite bestueckten "
            "Klemme ist nie nachgemessen worden -- erst messen")
    lx, ly = KLEMME_OEFFNUNG[footprint.split(":")[-1]]
    w = math.radians(drehung_grad)
    c, s = math.cos(w), math.sin(w)
    return (round(lx * c + ly * s, 9), round(-lx * s + ly * c, 9))


# --- Layoutregeln (pruefbar) ------------------------------------------------------
LAYOUT_REGELN = {
    "R1": {"text": "Klemmen kantenbuendig an der unteren Kante, Oeffnung "
                   "nach aussen; kein Klemmen-Hof schneidet PICO_SCHATTEN.",
           "keepout": "PICO_SCHATTEN",
           "beleg": "Hardware design with RP2040 (Raspberry Pi): Bauteile "
                    "unter dem Pico niedriger als der Steckabstand; eine "
                    "Klemme braucht Schraubendreher-Zugriff von oben."},
    "R2": {"text": "Alle Lastklemmen eines Moduls in EINER Reihe in "
                   "Kanalreihenfolge von links, Einspeisung ganz rechts, "
                   "vollstaendig in KLEMMENZONE.",
           "zone": "KLEMMENZONE",
           "beleg": "Pimoroni Automation HAT, Adafruit 5095, Kitronik 5331."},
    "R3": {"text": "Bauteilhoehe unter dem Pico <= 8,0 mm, sonst <= 9,5 mm.",
           "max_bauteilhoehe_mm": BAUTEILHOEHE_PICO_SCHATTEN_MAX,
           "beleg": "Buchsenhoehe 8,5 mm; STAPEL_ABSTAND-Rechnung oben."},
    "R4": {"text": "Luft-/Kriechstrecke zwischen Klemmenkontakten >= 0,8 mm.",
           "mindestabstand_mm": 0.8,
           "beleg": "IEC 60664, 0,8 mm bei 50 V."},
    "R5": {"text": "Kupfer mindestens 0,5 mm von der Platinenkante.",
           "mindestabstand_mm": 0.5,
           "beleg": "JLCPCB-Designregel 0,3 mm plus Reserve."},
    "R6": {"text": "Jedes Bauteil traegt seine Referenz sichtbar auf F.Silkscreen.",
           "layer": "F.Silkscreen", "sichtbar": True,
           "beleg": "Konvention (Audit v2 W1)."},
    "R7": {"text": "Jede Klemme, jeder Stecker und jede Matrix-Spalte traegt "
                   "ihre Funktion im Siebdruck.",
           "layer": "F.Silkscreen",
           "beleg": "Adafruit 5095 / DFRobot 2591: Pinnamen an jeder Klemme."},
    "R9": {"text": "Modulname, Vertragsversion und Bank-Vorgabe stehen "
                   "lesbar im Siebdruck.",
           "layer": "F.Silkscreen",
           "pflichtfelder": ("modulname", "vertrag_version", "bank"),
           "beleg": "Konvention (Audit v2 W7)."},
    # Platzierung nach Stromfluss (Bericht 04, A1-A12): als Zahlen,
    # damit die Beschreibung KiCad-frei geprueft werden kann.
    "P1": {"text": "Abblockkondensator <= 5 mm vom Versorgungspin seines IC, "
                   "gleiche Lage.",
           "max_mm": 5.0, "beleg": "TI SLVA959B 5.3.1 (< 0,5 cm)."},
    "P2": {"text": "Schaltregler: Spule, Freilaufdiode und Eingangs-Keramik "
                   "<= 6 mm vom IC (kleinste Schleife).",
           "max_mm": 6.0, "beleg": "TI SLVS632L Layout-Beispiel; SLVA959B 6.3.2."},
    "P3": {"text": "Schalter (FET/Treiber) <= 15 mm von seiner Lastklemme.",
           "max_mm": 15.0, "beleg": "Adafruit/SparkFun 10-12 mm (Konvention)."},
    "P4": {"text": "Gate-Widerstand <= 5 mm vom Gate.",
           "max_mm": 5.0, "beleg": "Adafruit 2,5 mm, SparkFun 3,8 mm (Konvention)."},
    "P5": {"text": "Keine Schaltregler-Teile und kein Kupfer in ANTENNE_FREI.",
           "zone": "ANTENNE_FREI", "beleg": "Pico-Datenblatt 2.2.1."},
}

LAYOUT_AUFLAGEN = (
    "Jede Platine traegt neben Pin 1 der unteren Stapelreihe eine "
    "Kennzeichnung im Bestueckungsdruck (Dreieck plus \"1\") und an der "
    "Klemmenkante die Marke \"UNTEN\". Das M3-Lochbild ist "
    "punktsymmetrisch; ein verdreht angeschraubtes Modul steckt nirgends "
    "(VERDREHT_STECKT_NIRGENDS), bleibt also tot statt kaputt -- die "
    "Marke macht den Fehler sichtbar.",
    "ERST stecken, DANN auf die Abstandsbolzen schrauben.",
)
MONTAGE_REGEL = LAYOUT_AUFLAGEN[1]

# --- Modultypen -------------------------------------------------------------------
MODULTYPEN = {
    0x01: {"name": "Motor",   "familie": "Motor",  "kanaele": 1, "signale": 4, "adc": True},
    0x10: {"name": "Dimmer1", "familie": "Dimmer", "kanaele": 1, "signale": 1, "adc": False},
    0x11: {"name": "Dimmer3", "familie": "Dimmer", "kanaele": 3, "signale": 3, "adc": False},
    0x12: {"name": "Dimmer4", "familie": "Dimmer", "kanaele": 4, "signale": 4, "adc": False},
}

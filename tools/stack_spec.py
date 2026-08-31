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

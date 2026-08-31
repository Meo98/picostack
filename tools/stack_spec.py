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

M3_DRILL = 3.2
M3_HOLES = [(4.0, 4.0), (4.0, 56.0), (60.0, 4.0), (60.0, 56.0)]

STAPEL_ABSTAND = 15.0     # mm zwischen zwei Platinen
# Belegt gegen den Stapelstecker (siehe unten, STECKER_STAPEL) in
# hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31): Buchse mit
# durchgehendem Stift, Gehaeusehoehe 8,5 mm, Stiftlaenge unterhalb des
# Gehaeuses 12,46 mm (Datenblatt ZHOURI/BOOMELE "PC104-2*NA+1",
# LCSC C35165). Rechnerisch gueltiger Bereich fuer diesen Wert bei
# 1,6 mm Platinendicke: 12,46 mm bis 20,96 mm -- 15,0 mm liegt
# komfortabel darin (~5,96 mm Einstecktiefe), keine Aenderung noetig.
# Fuer den separaten Kettenstecker (STECKER_KETTE) ergibt sich mit
# gewoehnlichen, nicht durchgehenden Steckerteilen dagegen nur eine
# knappe Einstecktiefe von rechnerisch 1,1 mm bei denselben 15,0 mm --
# siehe STECKER_KETTE unten und hardware/bauteile-1b.md.

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
    # 4 (GP2) war SEL, jetzt wieder frei -- SEL laeuft ueber
    # STECKER_KETTE, nicht mehr ueber diesen Stecker.
    5:  "FLASH_MODE",   # GP3
    6:  "I2C_SDA",      # GP4
    7:  "I2C_SCL",      # GP5
    9:  "NOTAUS",       # GP6
    10: "SEL_CLK",      # GP7
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
    "buchse_lcsc": "C541849",      # XFCN PM254V-11-02-H85, 8,5 mm
    "stift_lcsc": "C492401",       # XFCN PZ254V-11-02P, 6,0/3,0 mm
    "pins": {1: "SEL", 2: "GND"},
    "einstecktiefe_mm": 1.1,       # rechnerisch, bei 15,0 mm Stapelabstand
    "quelle": "hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31)",
}

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

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

# --- Steckerbelegung ------------------------------------------------
# Pico-Pins 1..40. Die Nummern folgen dem Pico-Datenblatt, nicht der
# GPIO-Nummer: der Stecker traegt Pins, nicht GPIO.
RESERVIERT = (
    "I2C_SDA", "I2C_SCL",     # Bus zu den Modulen
    "FLASH_TX", "FLASH_RX",   # Bootlader der Modul-MCU
    "SEL",                    # Auswahl-Token, von Modul zu Modul
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
    4:  "SEL",          # GP2
    5:  "FLASH_MODE",   # GP3
    6:  "I2C_SDA",      # GP4
    7:  "I2C_SCL",      # GP5
    9:  "NOTAUS",       # GP6
})

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

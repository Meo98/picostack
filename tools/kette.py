"""Die Logik der Auswahlkette, als Wahrheitstabelle pruefbar.

Jedes Modul leitet aus zwei Eingaengen drei Signale ab:

    FLASH_MODE  global, vom Sockel
    SEL_IN      Token vom Modul darueber (beim obersten: vom Sockel)

    RESET       an den Modul-MCU (1 = im Reset gehalten)
    BOOT0       an den Modul-MCU (1 = Bootlader statt Anwendung)
    SEL_OUT     Token an das Modul darunter

Der Kniff steckt in SEL_OUT: das gewaehlte Modul gibt das Token nicht
weiter. Dadurch wandert es beim naechsten Puls genau eine Position
tiefer, und der Sockel muss nur mitzaehlen, um die Adressen zu kennen.

Ausserhalb des Flash-Modus laufen alle Module. Das ist der
Normalbetrieb und der haeufigste Fall -- er darf nicht vom Token
abhaengen.
"""


def modul_zustand(flash_mode, sel_in):
    if not flash_mode:
        # Normalbetrieb: alle laufen, das Token wird nur durchgereicht
        return 0, 0, sel_in
    if sel_in:
        # dieses Modul ist an der Reihe: wach, im Bootlader, haelt das
        # Token an
        return 0, 1, 0
    # nicht an der Reihe: im Reset, Ausgaenge hochohmig
    return 1, 0, 0

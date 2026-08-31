"""Beschreibt einen Modul-MCU vom Pico aus. Nachweis, kein Produkt.

Reihenfolge: ueber die Kettenlogik in den Bootlader bringen,
synchronisieren, loeschen, blockweise schreiben, ueber dieselbe
Kettenlogik zurueck in die Anwendung.

Auf dem Tischaufbau gibt es weder Flipflop noch Gatter: Pico und MCU
sind ueber vier blanke Draehte verbunden (siehe
docs/nachweis-2026-08.md). Die Pico-UART-Pins entsprechen
FLASH_TX/FLASH_RX aus stack_spec.PIN_ROLLE (Steckerpins 1/2) und
fuehren direkt zum Bootlader-USART der MCU (physisch PA11/PA12, siehe
hardware/bauteile.md). BOOT0 und NRST dagegen liegen hier direkt an
den rohen MCU-Pins (PA14/NRST) an, nicht an SEL/SEL_CLK/FLASH_MODE --
auf der fertigen Platine haelt erst ein D-Flipflop die Auswahl (Q) und
ein Gatter leitet daraus mit FLASH_MODE Reset und Bootlader-Auswahl
ab. Beides existiert auf dem Tisch nicht; das eine Modul am Tisch ist
hier von Hand als "ausgewaehlt" gesetzt (q=1).

EHRLICHKEIT: Dieses Programm ist noch nie auf Hardware gelaufen. Es
ist nicht einmal syntaktisch auf einem Pico geprueft -- MicroPython
mit machine.UART gibt es auf dem Entwicklungsrechner nicht.
"""
from machine import Pin, UART
import time
from an3155 import Bootlader
from kette import modul_zustand

BLOCK = 256
START = 0x08000000

# timeout: MicroPython liefert bei Zeitueberschreitung None zurueck,
# was an3155._quittung() als "keine Antwort" meldet. Ohne timeout=
# blockiert read() je nach Port unbestimmt lange -- ein Modul ohne
# bestueckten MCU laesst den Nachweis dann einfach haengen, statt einen
# Fehler zu melden.
# 2000 ms: Die Quittungen auf SYNC und die Schreibbloecke kommen in
# wenigen Millisekunden; der lange Fall ist die Massenloeschung, deren
# Dauer wir nicht nachgeschlagen haben. Der Wert ist deshalb bewusst
# grosszuegig geschaetzt und nicht aus einem Datenblatt hergeleitet --
# er soll nur verhindern, dass ein toter Chip den Aufbau blockiert.
uart = UART(0, baudrate=115200, bits=8, parity=0, stop=1, tx=0, rx=1,
            timeout=2000)
boot0 = Pin(2, Pin.OUT)
nrst = Pin(3, Pin.OUT)


def reset(flash_mode, q):
    """Reset- und BOOT0-Pegel nicht direkt setzen, sondern ueber
    kette.modul_zustand(flash_mode, q) ableiten -- derselben
    Gatterlogik, die auf der fertigen Platine aus FLASH_MODE und dem
    Flipflop-Ausgang Q gebildet wird. Ein direktes Setzen von
    BOOT0/NRST wuerde eine zweite, womoeglich abweichende Logik neben
    die Kettenlogik stellen, die schon gegen die Wahrheitstabelle
    geprueft ist (tests/test_kette.py). So prueft dieser Nachweis am
    Tisch denselben Weg, den spaeter die Gatter in Kupfer ausfuehren --
    nur eben in Software nachgerechnet, weil sie auf dem Tischaufbau
    (noch) fehlen.

    q ist am Tisch von Hand gesetzt: es gibt nur ein Modul und kein
    Schieberegister, das die Auswahl weiterschieben koennte.

    flash_mode=1, q=1 waehlt dieses (einzige) Modul im Flash-Modus:
    reset=0, boot0=1 -- der Bootlader startet.
    flash_mode=0 ist der Normalbetrieb: reset=0, boot0=0 -- die
    Anwendung startet.
    """
    reset_haltung, boot0_ziel, _sel_out = modul_zustand(flash_mode, q)
    boot0.value(boot0_ziel)
    nrst.value(0)
    time.sleep_ms(10)
    nrst.value(0 if reset_haltung else 1)
    time.sleep_ms(50)


def aufspielen(pfad):
    reset(flash_mode=1, q=1)
    bl = Bootlader(uart)
    if not bl.sync():
        raise RuntimeError("keine Antwort vom Bootlader")
    if not bl.erase_all():
        raise RuntimeError("Loeschen abgelehnt")
    with open(pfad, "rb") as f:
        adresse = START
        while True:
            block = f.read(BLOCK)
            if not block:
                break
            if len(block) % 4:
                block += b"\xff" * (4 - len(block) % 4)
            if not bl.write(adresse, block):
                raise RuntimeError("Schreiben abgelehnt bei 0x%08X" % adresse)
            adresse += len(block)
    reset(flash_mode=0, q=0)
    print("aufgespielt:", pfad)

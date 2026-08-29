"""Beschreibt einen Modul-MCU vom Pico aus. Nachweis, kein Produkt.

Reihenfolge: ueber die Kettenlogik in den Bootlader bringen,
synchronisieren, loeschen, blockweise schreiben, ueber dieselbe
Kettenlogik zurueck in die Anwendung.

Auf dem Tischaufbau gibt es noch kein Gatter: Pico und MCU sind ueber
vier blanke Draehte verbunden (siehe docs/nachweis-2026-08.md). Die
Pico-UART-Pins entsprechen FLASH_TX/FLASH_RX aus stack_spec.PIN_ROLLE
(Steckerpins 1/2) und fuehren direkt zum Bootlader-USART der MCU
(physisch PA11/PA12, siehe hardware/bauteile.md). BOOT0 und NRST
dagegen liegen hier direkt an den rohen MCU-Pins (PA14/NRST) an, nicht
an SEL/FLASH_MODE (Steckerpins 4/5) -- auf der fertigen Platine leitet
erst ein Gatter aus SEL und FLASH_MODE die Reset- und
Bootlader-Auswahl ab, und dieses Gatter existiert auf dem Tisch nicht.
"""
from machine import Pin, UART
import time
from an3155 import Bootlader
from kette import modul_zustand

BLOCK = 256
START = 0x08000000

uart = UART(0, baudrate=115200, bits=8, parity=0, stop=1, tx=0, rx=1)
boot0 = Pin(2, Pin.OUT)
nrst = Pin(3, Pin.OUT)


def reset(flash_mode, sel_in):
    """Reset- und BOOT0-Pegel nicht direkt setzen, sondern ueber
    kette.modul_zustand(flash_mode, sel_in) ableiten -- derselben
    Logik, die auf der fertigen Platine ein Gatter aus den
    Verdrahtungssignalen SEL und FLASH_MODE bildet (Steckerpins 4/5,
    stack_spec.PIN_ROLLE). Ein direktes Setzen von BOOT0/NRST wuerde
    eine zweite, womoeglich abweichende Logik neben die Kettenlogik
    stellen, die schon gegen die Wahrheitstabelle geprueft ist
    (tests/test_kette.py). So prueft dieser Nachweis am Tisch
    denselben Weg, den spaeter das Gatter in Kupfer ausfuehrt --
    nur eben in Software nachgerechnet, weil das Gatter auf dem
    Tischaufbau (noch) fehlt.

    flash_mode=1, sel_in=1 waehlt dieses (einzige) Modul im
    Flash-Modus: reset=0, boot0=1 -- der Bootlader startet.
    flash_mode=0 ist der Normalbetrieb: reset=0, boot0=0 -- die
    Anwendung startet.
    """
    reset_haltung, boot0_ziel, _sel_out = modul_zustand(flash_mode, sel_in)
    boot0.value(boot0_ziel)
    nrst.value(0)
    time.sleep_ms(10)
    nrst.value(0 if reset_haltung else 1)
    time.sleep_ms(50)


def aufspielen(pfad):
    reset(flash_mode=1, sel_in=1)
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
    reset(flash_mode=0, sel_in=0)
    print("aufgespielt:", pfad)

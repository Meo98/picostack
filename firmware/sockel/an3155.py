"""Der USART-Bootlader der STM32, so weit PicoStack ihn braucht.

Laeuft auf dem Pico unter MicroPython und beschreibt darueber die
Modul-MCU. Absichtlich klein gehalten: synchronisieren, loeschen,
schreiben, starten -- mehr braucht das Aufspielen einer Firmware
nicht.

Die Schnittstelle ist 8 Datenbits mit gerader Paritaet und einem
Stoppbit. Jeder Befehl geht mit seinem Einerkomplement hinaus; das ist
die einzige Pruefung, die das Protokoll auf der Befehlsebene hat.

Werte nach ST AN3155 (Rev. 16, Februar 2023):
- ACK/NACK: Abschnitt "Communication safety" (Seite 8/50)
- SYNC und Bootloader-Sequenz: Abschnitt 1 (Seite 5/50)
- Befehlscodes: Table 2 (Seite 7/50)
- Get: Abschnitt 3.1 (Seite 9/50)
- Go: Abschnitt 3.5 (Seite 18/50)
- Write Memory: Abschnitt 3.6 (Seite 20/50)
- Extended Erase Memory: Abschnitt 3.8 (Seite 26/50)
- Prüfsummen-Regel: Abschnitt "Communication safety" (Seite 8/50)
  - XOR für alle Daten-Bytes
  - Befehl + Komplement (XOR = 0xFF)
  - Global erase (0xFFFF) mit Checksum 0x00
"""

ACK = 0x79
NACK = 0x1F

SYNC = 0x7F
CMD_GET = 0x00
CMD_ERASE_EXT = 0x44
CMD_WRITE = 0x31
CMD_GO = 0x21


def _xor(daten, start=0):
    p = start
    for b in daten:
        p ^= b
    return p


class Bootlader:
    def __init__(self, uart):
        self.uart = uart

    # --- unterste Ebene ---
    def _quittung(self):
        a = self.uart.read(1)
        return len(a) == 1 and a[0] == ACK

    def _befehl(self, code):
        """Befehl samt Komplement senden und Quittung abholen."""
        self.uart.write(bytes([code, code ^ 0xFF]))
        return self._quittung()

    # --- Protokoll ---
    def sync(self):
        self.uart.write(bytes([SYNC]))
        return self._quittung()

    def get(self):
        return self._befehl(CMD_GET)

    def erase_all(self):
        if not self._befehl(CMD_ERASE_EXT):
            return False
        # 0xFFFF = Massenloeschung, Pruefsumme ist das XOR darueber
        self.uart.write(b"\xff\xff\x00")
        return self._quittung()

    def write(self, adresse, daten):
        if len(daten) > 256 or len(daten) % 4:
            raise ValueError("Block muss 1..256 Byte und durch 4 teilbar sein")
        if not self._befehl(CMD_WRITE):
            return False
        a = bytes([(adresse >> 24) & 0xFF, (adresse >> 16) & 0xFF,
                   (adresse >> 8) & 0xFF, adresse & 0xFF])
        self.uart.write(a + bytes([_xor(a)]))
        if not self._quittung():
            return False
        n = len(daten) - 1
        self.uart.write(bytes([n]) + daten + bytes([_xor(daten, n)]))
        return self._quittung()

    def go(self, adresse):
        if not self._befehl(CMD_GO):
            return False
        a = bytes([(adresse >> 24) & 0xFF, (adresse >> 16) & 0xFF,
                   (adresse >> 8) & 0xFF, adresse & 0xFF])
        self.uart.write(a + bytes([_xor(a)]))
        return self._quittung()

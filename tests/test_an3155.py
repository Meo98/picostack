"""Prueft die Bootlader-Umsetzung gegen eine nachgebildete Gegenstelle."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "firmware", "sockel"))
from an3155 import Bootlader, ACK, NACK

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


class FakeUart:
    """Nimmt Bytes entgegen und antwortet nach Skript."""

    def __init__(self, antworten):
        self.gesendet = bytearray()
        self.antworten = bytearray(antworten)

    def write(self, b):
        self.gesendet += b

    def read(self, n):
        aus, self.antworten = self.antworten[:n], self.antworten[n:]
        return bytes(aus)


# --- Synchronisieren ---
u = FakeUart([ACK])
b = Bootlader(u)
check("sync meldet Erfolg", b.sync(), True)
check("sync sendet 0x7F", bytes(u.gesendet), b"\x7f")

# --- Jeder Befehl geht mit seinem Komplement raus ---
# Das ist die Pruefsumme des Protokolls: faellt ein Bit, passt das
# Komplement nicht mehr und der Chip antwortet mit NACK.
u = FakeUart([ACK, ACK])
b = Bootlader(u)
b.erase_all()
check("Loeschbefehl mit Komplement", bytes(u.gesendet[:2]), b"\x44\xbb")

# --- Schreiben: Adresse und Daten je mit XOR-Pruefsumme ---
u = FakeUart([ACK, ACK, ACK])
b = Bootlader(u)
b.write(0x08000000, b"\x01\x02\x03\x04")
g = bytes(u.gesendet)
check("Schreibbefehl mit Komplement", g[:2], b"\x31\xce")
check("Adresse gefolgt von XOR", g[2:7], b"\x08\x00\x00\x00\x08")
# Laengenbyte ist N-1, dann die Daten, dann XOR ueber Laenge und Daten
check("Laengenbyte ist N-1", g[7], 3)
check("Datenpruefsumme", g[-1], 3 ^ 1 ^ 2 ^ 3 ^ 4)

# --- NACK wird nicht verschluckt ---
# Ein Bootlader, der Fehler stillschweigend hinnimmt, schreibt halbe
# Firmware auf ein Modul und niemand merkt es.
u = FakeUart([NACK])
b = Bootlader(u)
check("NACK meldet Misserfolg", b.sync(), False)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

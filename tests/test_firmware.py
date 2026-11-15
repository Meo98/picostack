"""firmware/pico/picostack.py gegen den Vertrag (tools/stack_spec.py).

Die Bibliothek laeuft auf dem Pico ohne das Repo; sie TRAEGT deshalb
ihre eigene Kopie der Baenke. Diese Suite haelt beide gleich -- ein
Modul, das an Bank B steckt, muss von der Bibliothek auch an Bank B
angesprochen werden.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "tools"))
sys.path.insert(0, os.path.join(HIER, "..", "firmware", "pico"))

import picostack as F   # noqa: E402  (ohne machine-Modul: Host-Modus)
import stack_spec as S  # noqa: E402

fails = []


def check(label, bedingung, detail=""):
    if not bedingung:
        fails.append("%s%s" % (label, (" -- %s" % (detail,)) if detail else ""))


check("Vertragsversion", F.VERTRAG_VERSION == S.VERTRAG_VERSION)
check("Baenke identisch", F.BAENKE == S.BAENKE, (F.BAENKE, S.BAENKE))
check("ADC-Bank identisch", tuple(F.ADC_BANK) == tuple(S.ADC_BANK))
check("Bank-Vorgaben identisch", F.BANK_VORGABE == S.BANK_VORGABE)
check("ADC-Vorgabe identisch", F.ADC_VORGABE == S.ADC_VORGABE)
check("NOTAUS = GP6", F.NOTAUS_GP == 6 and S.RESERVIERT[6] == "NOTAUS")
check("I2C = GP4/GP5", (F.I2C_SDA, F.I2C_SCL) == (4, 5)
      and S.RESERVIERT[4] == "I2C_SDA" and S.RESERVIERT[5] == "I2C_SCL")

d = F.Dimmer(kanaele=4)
check("Dimmer-Vorgabe Bank B", d.bank == "B" and d.gp == (12, 13, 14, 15), d.gp)
check("Dimmer.set klemmt auf 0..1", d.set(1, 1.7) == 1.0 and d.set(2, -1) == 0.0)
try:
    d.set(5, 0.5)
    check("Dimmer.set Kanal 5 abgelehnt", False)
except ValueError:
    pass
m = F.Motor()
check("Motor-Vorgabe Bank A, ADC 26", m.bank == "A" and (m.gp_en, m.gp_ph, m.gp_fault, m.gp_sleep) == (8, 9, 10, 11) and m.gp_adc == 26)
check("Motor.fahren klemmt auf -1..1", m.fahren(2) == 1.0 and m.fahren(-3) == -1.0)
try:
    F.Dimmer(bank="E")
    check("Bank E abgelehnt", False)
except ValueError:
    pass
check("PWM-Frequenz ueber dem Hoerbereich", F.PWM_HZ >= 20000)
# Rot-Nachweis: eine abweichende Bank-Tabelle faellt auf.
check("Rot-Nachweis Bank-Abweichung", {"A": (1, 2, 3, 4)} != S.BAENKE)

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Firmware-Bibliothek stimmt mit Vertrag v%d ueberein" % S.VERTRAG_VERSION)

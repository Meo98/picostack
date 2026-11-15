"""PicoStack v3 -- MicroPython-Bibliothek fuer den Raspberry Pi Pico.

Der Pico steckt oben auf dem Stapel; jedes Modul belegt eine GPIO-Bank
(A-D) ueber seine Slot-Matrix. Diese Bibliothek kennt nur den Vertrag
(tools/stack_spec.py): Baenke, ADC-Pins, NOTAUS, I2C.

    import picostack
    led = picostack.Dimmer(bank="B", kanaele=4)
    led.set(1, 0.5)          # Kanal 1 auf 50 %
    led.set(3, 1.0)
    led.aus()

    m = picostack.Motor(bank="A")      # kommt mit dem Motormodul v3
    m.fahren(0.8)                      # vorwaerts 80 %
    m.fahren(-0.3)                     # rueckwaerts 30 %
    print(m.strom_a())                 # aus IPROPI (GP26)

    picostack.notaus_aktiv()           # True = Schleife unterbrochen

Zahlen hier MUESSEN mit tools/stack_spec.py uebereinstimmen; tests/
test_firmware.py prueft das (KiCad-frei, ohne Pico).
"""
try:
    from machine import Pin, PWM, ADC, I2C
except ImportError:          # Host-Tests ohne MicroPython
    Pin = PWM = ADC = I2C = None

VERTRAG_VERSION = 4

BAENKE = {
    "A": (8, 9, 10, 11),
    "B": (12, 13, 14, 15),
    "C": (16, 17, 18, 19),
    "D": (20, 21, 22, 7),
}
ADC_BANK = (26, 27, 28)
BANK_VORGABE = {"Motor": "A", "Dimmer": "B"}
ADC_VORGABE = {"Motor": 26}
NOTAUS_GP = 6
I2C_SDA, I2C_SCL = 4, 5
PWM_HZ = 20000               # ueber dem Hoerbereich; 16 getrennte Kanaele


def bank_pins(bank):
    try:
        return BAENKE[bank]
    except KeyError:
        raise ValueError("Bank %r gibt es nicht (A-D)" % (bank,))


class Dimmer:
    """LED-Dimmer-Modul (1, 3 oder 4 Kanaele), Low-Side-PWM."""

    def __init__(self, bank=None, kanaele=4, hz=PWM_HZ):
        bank = BANK_VORGABE["Dimmer"] if bank is None else bank
        if not 1 <= kanaele <= 4:
            raise ValueError("1..4 Kanaele")
        self.bank = bank
        self.gp = bank_pins(bank)[:kanaele]
        self._pwm = []
        if PWM is not None:
            for gp in self.gp:
                p = PWM(Pin(gp))
                p.freq(hz)
                p.duty_u16(0)
                self._pwm.append(p)

    def set(self, kanal, wert):
        """Kanal 1..n auf 0.0..1.0."""
        if not 1 <= kanal <= len(self.gp):
            raise ValueError("Kanal %d gibt es nicht" % kanal)
        wert = min(1.0, max(0.0, float(wert)))
        if self._pwm:
            self._pwm[kanal - 1].duty_u16(int(wert * 65535))
        return wert

    def aus(self):
        for k in range(1, len(self.gp) + 1):
            self.set(k, 0.0)


class Motor:
    """Motormodul (DRV8876, PH/EN): S1 = EN (PWM), S2 = PH (Richtung),
    S3 = nFAULT (Eingang), S4 = nSLEEP (Freigabe), IPROPI an der ADC-Bank.
    Ohne NOTAUS-Freigabe (Hardware-UND auf dem Modul) laeuft nichts."""

    def __init__(self, bank=None, adc=None, hz=PWM_HZ, ipropi_r_ohm=1300.0):
        bank = BANK_VORGABE["Motor"] if bank is None else bank
        adc = ADC_VORGABE["Motor"] if adc is None else adc
        if adc not in ADC_BANK:
            raise ValueError("ADC-Pin %r nicht in %r" % (adc, ADC_BANK))
        self.bank = bank
        self.gp_en, self.gp_ph, self.gp_fault, self.gp_sleep = bank_pins(bank)
        self.gp_adc = adc
        self._r = ipropi_r_ohm          # 1 mA/A x R -> V
        if PWM is not None:
            self._en = PWM(Pin(self.gp_en))
            self._en.freq(hz)
            self._en.duty_u16(0)
            self._ph = Pin(self.gp_ph, Pin.OUT, value=0)
            self._fault = Pin(self.gp_fault, Pin.IN, Pin.PULL_UP)
            self._sleep = Pin(self.gp_sleep, Pin.OUT, value=1)
            self._adc = ADC(Pin(self.gp_adc))

    def fahren(self, wert):
        """-1.0..1.0; Vorzeichen = Richtung."""
        wert = min(1.0, max(-1.0, float(wert)))
        if PWM is not None:
            self._ph.value(1 if wert >= 0 else 0)
            self._en.duty_u16(int(abs(wert) * 65535))
        return wert

    def stopp(self):
        return self.fahren(0.0)

    def fehler(self):
        return (self._fault.value() == 0) if PWM is not None else False

    def strom_a(self):
        """Motorstrom aus IPROPI: V = I x 1 mA/A x R."""
        if PWM is None:
            return 0.0
        v = self._adc.read_u16() * 3.3 / 65535.0
        return v / (self._r * 1e-3)


def notaus_aktiv():
    """True, wenn NOTAUS (GP6, LOW = gesperrt) ausgeloest ist."""
    if Pin is None:
        return False
    return Pin(NOTAUS_GP, Pin.IN, Pin.PULL_UP).value() == 0


def i2c(freq=400000):
    """Der Qwiic-Bus (GP4/GP5, I2C0)."""
    return I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=freq)

"""Die Auswahlkette: ein Schieberegister ueber den ganzen Stapel.

Jedes Modul traegt ein D-Flipflop. Die Flipflops aller Module haengen
in Reihe und an einem gemeinsamen Takt vom Sockel -- zusammen sind sie
ein Schieberegister, das so lang ist wie der Stapel hoch:

    SEL_IN      D des Flipflops: Ausgang des Moduls darueber
                (beim obersten Modul: vom Sockel)
    SEL_CLK     global, vom Sockel -- alle Flipflops takten gemeinsam
    FLASH_MODE  global, vom Sockel

    Q           "ich bin ausgewaehlt"; zugleich SEL_OUT an das Modul
                darunter
    RESET       an den Modul-MCU (1 = im Reset gehalten)
    BOOT0       an den Modul-MCU (1 = Bootlader statt Anwendung)

So waehlt der Sockel aus: Er legt eine 1 an SEL_IN des obersten Moduls
und taktet einmal -- die 1 steht im ersten Flipflop, Modul 1 ist
ausgewaehlt. Dann legt er 0 an und taktet weiter; die 1 wandert bei
jedem Takt genau eine Position tiefer. Der Sockel zaehlt die Takte mit
und weiss damit, das wievielte Modul gerade antwortet. Daher kommt die
Adressvergabe: Modul Nummer drei ist das, das nach dem dritten Takt
ausgewaehlt war.

Genau dieser Speicher fehlte der frueheren, rein kombinatorischen
Fassung: dort war SEL_OUT = ¬FLASH_MODE ∧ SEL_IN, im Flash-Modus also
immer 0. Nur das oberste Modul war je erreichbar.

Ausserhalb des Flash-Modus laufen alle Module. Das ist der
Normalbetrieb und der haeufigste Fall -- er haengt nicht vom Inhalt
des Schieberegisters ab (RESET und BOOT0 sind dann beide 0).

Rollenteilung in diesem Modul:

    modul_zustand()  ist die reine GATTERLOGIK -- genau das, was die
                     Gatter auf dem Modul aus FLASH_MODE und Q machen.
                     Kein Zustand, als Wahrheitstabelle pruefbar.
    Modul            ist das FLIPFLOP plus diese Gatter: es haelt Q
                     und schreibt es bei jedem Takt fort.
"""


def modul_zustand(flash_mode, q):
    """Die Gatterlogik eines Moduls. Zustandslos.

        RESET   = flash_mode ∧ ¬q
        BOOT0   = flash_mode ∧ q
        SEL_OUT = q            (der Flipflop-Ausgang selbst)

    q ist der Ausgang des Flipflops, nicht der Eingang der Kette --
    das Weiterreichen erledigt der Takt, nicht ein Gatter.

    RESET=1 heisst hier "wird im Reset gehalten" -- das ist die logisch
    richtige Aussage ueber das Modul, unabhaengig von der Polung eines
    bestimmten Bauteil-Pins, und bleibt deshalb absichtlich so (Tests
    haengen daran). In der Hardware (tools/sch/modulsockel.py, U100)
    heisst der Reset-Eingang des STM32C011 aber `NRST` und ist AKTIV
    LOW (0 = im Reset). Das Gatter, das RESET bildet, muss die Zeile
    oben deshalb beim Verdrahten invertieren -- ein NAND statt eines
    AND liefert direkt NRST = ¬RESET = ¬(flash_mode ∧ ¬q). Genau an
    dieser Stelle -- Modell sagt "AND", Hardware braucht "NAND" -- ist
    der Verpolungsfehler entstanden, den Aufgabe 3 dieser Etappe
    behoben hat (siehe modulsockel.py, Moduldoku bei U103). Wer hier
    ein AND liest und daraus ein AND-Gatter auf NRST verdrahtet, baut
    denselben Fehler erneut.
    """
    q = 1 if q else 0
    if not flash_mode:
        # Normalbetrieb: alle laufen, unabhaengig vom Schieberegister
        return 0, 0, q
    if q:
        # dieses Modul ist an der Reihe: wach, im Bootlader
        return 0, 1, q
    # nicht an der Reihe: im Reset, Ausgaenge hochohmig
    return 1, 0, q


class Modul:
    """Ein Modul in der Kette: D-Flipflop plus Gatterlogik.

    Der Default q=0 ist eine Annahme dieser Simulation, keine
    Eigenschaft der Hardware: ein reales D-Flipflop hat beim
    Einschalten einen undefinierten Zustand. Deshalb muss der Sockel
    die Kette leertakten, bevor er FLASH_MODE das erste Mal auf 1
    setzt (siehe docs/superpowers/specs/2026-08-28-picostack-design.md,
    Abschnitt "Bus und Adressierung", "Einschaltzustand").
    """

    def __init__(self, q=0):
        self.q = 1 if q else 0

    def takt(self, sel_in, flash_mode):
        """Eine Taktflanke auf SEL_CLK.

        Uebernimmt SEL_IN in das Flipflop und liefert danach
        (reset, boot0, sel_out) aus der Gatterlogik.
        """
        self.q = 1 if sel_in else 0
        return modul_zustand(flash_mode, self.q)

    def zustand(self, flash_mode):
        """(reset, boot0, sel_out) ohne Takt -- was gerade anliegt."""
        return modul_zustand(flash_mode, self.q)


def kette_takten(module, sel_in, flash_mode):
    """Eine Taktflanke fuer den ganzen Stapel.

    Alle Flipflops haengen am selben SEL_CLK und uebernehmen
    gleichzeitig. Deshalb werden erst alle Eingaenge aus den ALTEN
    Ausgaengen gebildet und dann getaktet -- sonst schoebe sich das
    Bit in einem einzigen Takt durch den ganzen Stapel.

    module   Liste von Modul-Objekten, oben zuerst
    sel_in   was der Sockel an das oberste Modul legt
    """
    eingaenge = [sel_in] + [m.q for m in module[:-1]]
    return [m.takt(e, flash_mode) for m, e in zip(module, eingaenge)]

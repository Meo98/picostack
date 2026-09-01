"""Der Modulsockel: gemeinsamer Schaltplanblock fuer jedes PicoStack-Modul.

Sitzt auf jeder Modulplatine (Motormodul, kuenftige Dimmer-Module, ...)
und -- ohne MCU/Flipflop/Gatter -- auch auf der Sockelplatine, die nur
die Steckerteile braucht. Ein Fehler hier ist ein Fehler in jedem
kuenftigen Modul, deshalb wird ausschliesslich aus dem Vertrag
(`tools/stack_spec.py`) und der Auswahlketten-Logik (`tools/kette.py`)
abgeleitet, nichts wird von Hand abgeschrieben.

Inhalt (mit_flipflop=True, der Normalfall fuer ein Modul):

  U100  STM32C011F6P6 (TSSOP-20), Modul-MCU. USART1 auf den physischen
        Pins PA11 (TX)/PA12 (RX) -- siehe hardware/bauteile.md, Beleg 1.
        WICHTIG: PA11 ist der TX-Pin des MCU, landet also auf der
        Leitung, auf der der Pico EMPFAENGT (FLASH_RX) -- nicht auf der
        gleichnamigen Leitung. stack_spec.AUFLAGEN sagt das woertlich:
        "FLASH_RX ist der Empfangspin des Pico und damit die gemeinsame
        Sendeleitung aller Module." PA12 (RX des MCU) liegt entsprechend
        an FLASH_TX (das, was der Pico sendet).
        NRST ist bei diesem Gehaeuse mit PF2 zusammengelegt (PF2-NRST,
        Datenblatt DS13866, TSSOP20-Pinout) -- das ist der einzige Pin
        dieses Bauteils, an dem die Selbstpruefung nicht aus einem
        eigenen Symbolpin "NRST" besteht, sondern aus "PF2".
  U101  SN74LVC1G175 (SOT-363-6), D-Flipflop mit asynchronem Loesch-
        eingang CLR. D = SEL_IN (Kettenstecker oben), CLK = SEL_CLK
        (Stapelstecker), Q = SEL_OUT (an Kettenstecker unten UND an
        die Gatter) -- tools/kette.py: SEL_OUT ist der Flipflop-Ausgang
        selbst, kein eigenes Gatter mehr.
  R102/C101  lokales RC-Glied an CLR (aktiv LOW): loescht die Kette bei
        jedem Einschalten automatisch, ohne eigene Stapelleitung -- die
        Entscheidung des Auftraggebers vom 2026-08-31 (Weg 2 aus
        hardware/bauteile-1b.md, Beleg 2). Zeitkonstante siehe unten
        bei RC_TAU_S.
  U102  SN74LVC2G00DCUR (VSSOP-8, Dual-NAND) -- BEIDE NAND-Funktionen der
        Reset-Kette in einem Bauteil. WARUM NAND UND NICHT AND, obwohl
        tools/kette.py::modul_zustand() die Groesse "RESET" nennt und mit
        UND beschreibt (RESET = flash_mode ∧ ¬q): kette.py modelliert die
        LOGISCHE Aussage "im Reset gehalten" (1 = ja), nicht die
        Hardware-Polung. Der tatsaechliche Reset-Eingang des STM32C011
        heisst NRST und ist aktiv LOW (0 = im Reset) -- ein AND-Gatter
        direkt auf NRST verpolt das Modul (laeuft, wenn es stehen soll,
        und umgekehrt). Ein NAND liefert exakt die fehlende Invertierung
        in derselben Rechnung: NAND(a,b) = ¬(a∧b) = ¬RESET = NRST.
        Einheit 1 (Pins 1,2,7) hat BEIDE Eingaenge an SEL_OUT (Q)
        angeschlossen -- ein NAND mit verbundenen Eingaengen ist ein
        Inverter (NAND(Q,Q) = ¬Q); das ersetzt das fruehere
        Einzel-NOT-Gatter (SN74LVC1G04) und liefert NQ = ¬Q, ohne ein
        eigenes NOT-Bauteil zu brauchen. ABSICHT, KEIN VERSEHEN: die zwei
        kurzgeschlossenen Pins sehen wie ein Fehler aus (ein Eingang
        "unbenutzt") -- sind es nicht, NICHT auf zwei getrennte Eingaenge
        "reparieren". Einheit 2 (Pins 3,5,6) bildet
        NRST = ¬(FLASH_MODE ∧ ¬Q) = ¬(FLASH_MODE ∧ NQ) aus dem Ausgang
        von Einheit 1 und FLASH_MODE, direkt an PF2-NRST des MCU
        (Pin 6). NICHT auf AND zurueckstellen, auch wenn kette.py "AND"
        nahelegt.
  U103  SN74LVC1G08 (SOT-353-5, AND) -- BOOT0 = FLASH_MODE ∧ Q, unveraendert
        eine reine UND-Funktion (der Bootloader-Pin des STM32 ist aktiv
        HIGH, keine Verpolung dort). Kein Gegenstueck in U102: ein
        homogenes Dual-Gatter kann nicht eine NAND- und eine AND-Einheit
        zugleich sein (jede "2G"-Familie ist zwei Gatter DERSELBEN
        Funktion) -- ein gemischtes AND/NAND-Bauteil wurde bei
        LCSC/JLCPCB nicht gefunden. Deshalb ein Einzel-Gatter-IC fuer
        BOOT0, waehrend NOT und NRST sich ein Dual-NAND teilen (U102).
        Physische Gatter-ICs insgesamt: **zwei** (U102, U103) statt der
        drei aus der vorherigen Fassung (NOT/NAND/AND je einzeln) --
        die Gatter-**logik** bleibt bei drei Funktionen: 1x NOT
        (als NAND(Q,Q) in U102, Einheit 1), 1x NAND (U102, Einheit 2),
        1x AND (U103) (tools/kette.py::modul_zustand).
  R104/R100, R105/R101  zwei Kennwiderstand-Spannungsteiler gegen den
        festen Oberwiderstand ID_OBEN (stack_spec.ID_OBEN): R104/R105
        sind der feste Oberwiderstand (immer ID_OBEN), R100/R101 die
        Kennwiderstaende, deren Wert den Modultyp verraet (stack_spec.
        ID_WIDERSTAENDE) -- Wert wird je Modultyp in dessen eigener
        Stueckliste gesetzt, hier nur als Platzhalter eingetragen.
  J100  Stapelstecker 2x20 (STECKER_STAPEL) -- EIN Bauteil, seit der
        Umstellung auf den durchgehenden Stift kein Buchse/Stift-Paar
        mehr. Pin-Rollen kommen ausschliesslich aus stack_spec.PIN_ROLLE.
  J101/J102  Kettenstecker (STECKER_KETTE), Buchse oben / Stift unten --
        dieser EINE Stecker muss die Kette auftrennen koennen und bleibt
        deshalb ein normales, nicht durchgehendes Paar.
  J103/J104  Leistungsstecker, durchgereicht (Buchse oben / Stift unten,
        gleiche Familie wie der urspruengliche Signalstecker).

mit_flipflop=False (die Sockelplatine, Aufgabe 4) laesst U100..U103 und
alle Kennwiderstaende weg -- der Sockel ist kein Modul, hat keinen
eigenen Modultyp und speist die Kette, statt an ihr teilzunehmen. Es
bleiben nur die Steckerteile mit ihren woertlich aus stack_spec
gelesenen Netznamen; die aufrufende Sockelplatine schliesst SEL_IN/
SEL_OUT und die Leistungsleitungen selbst an ihre eigenen Bauteile an.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S  # noqa: E402  (Pfad muss zuerst gesetzt sein)

# -------------------------------------------------------------- Footprints
FP_R0805 = "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
FP_TSSOP20 = "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm"
FP_SOT363 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
FP_SOT353 = "Package_TO_SOT_SMD:SOT-353_SC-70-5"
# SN74LVC2G00DCUR (U102) ist trotz "DCUR"-Namensaehnlichkeit zum
# SOT-363-Flipflop NICHT SOT-363 -- SOT-363/SC-70-6 hat nur 6 Pins,
# ein Dual-2-Input-Gatter braucht mindestens 8 (2x(2 Eingaenge + 1
# Ausgang) + VCC + GND). Verifiziert auf der LCSC-Produktseite
# (lcsc.com/product-detail/C206109.html): Gehaeuse "VSSOP-8-0.5mm".
FP_VSSOP8 = "Package_SO:VSSOP-8_2.3x2mm_P0.5mm"
FP_HDR_2X20 = "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical"
# Ketten- und Leistungsstecker sind seit Aufgabe 5e (2026-08-31)
# SMD-PAARE: Buchse oben, Stiftleiste unten, am selben Ort. Zwei
# bedrahtete Haelften am selben Ort brauchten dieselben Bohrungen und
# waeren damit derselbe Leiter -- fuer die Auswahlkette (SEL_IN oben,
# SEL_OUT unten) genau falsch. Die Herleitung steht vollstaendig im
# Block bei stack_spec.STECKER_KETTE. Deshalb hier vier Footprints
# statt zwei: Buchse (PinSocket) und Stiftleiste (PinHeader) je Groesse.
FP_SKT_1X02 = ("Connector_PinSocket_2.54mm:"
               "PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left")
FP_HDR_1X02 = ("Connector_PinHeader_2.54mm:"
               "PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left")
FP_SKT_2X02 = ("Connector_PinSocket_2.54mm:"
               "PinSocket_2x02_P2.54mm_Vertical_SMD")
FP_HDR_2X02 = ("Connector_PinHeader_2.54mm:"
               "PinHeader_2x02_P2.54mm_Vertical_SMD")
# Alle fuenf Header-Footprints sind Platzhalter aus der KiCad-Standard-
# bibliothek. Die tatsaechlichen Bauteile (STECKER_STAPEL/STECKER_KETTE/
# STECKER_LEISTUNG in stack_spec.py) sind Spezialteile (Buchse mit
# durchgehendem Stift bzw. bestimmte Bauhoehen) und brauchen eigene
# .kicad_mod-Footprints -- das ist Sache der PCB-Layout-Aufgaben
# (Aufgabe 6/7 dieser Etappe), nicht dieses Schaltplan-Blocks. Die
# Bauform (bedrahtet/SMD, Buchse/Stift) stimmt jetzt aber, und
# stack_spec.FOOTPRINT_HOF rechnet mit genau diesen Hoefen.

# ------------------------------------------------------- Netze am Stecker
# Rolle -> Netzname am 2x20-Stapelstecker. Ausschliesslich aus dem
# Vertrag gelesen, nicht abgeschrieben: das ist der Sinn von PIN_ROLLE.
# "SEL_OUT" ist zwar seit Befund 2 (Aufgabe-4-Fix-1) eine echte
# Vertragsrolle (stack_spec.RESERVIERT), aber ausdruecklich KEIN Pin
# DIESES Steckers -- SEL laeuft ueber den eigenen STECKER_KETTE (s.
# stack_spec.py). Sie bleibt deshalb hier aussen vor, genau wie "frei";
# _stapelstecker() behandelt beide gleich als no_connect (Modulseite)
# bzw. Sonderfall (Sockelseite, s. dort).
# Drei Vertragsrollen sind absichtlich KEINE Netze dieses Steckers:
# "SEL_OUT" laeuft ueber den Kettenstecker, "RUN" und "ADC_VREF" sind
# gar keine Busleitungen, sondern Pico-eigene Anschluesse, die kein
# Modul sehen darf (Begruendung bei PIN_GPIO_NAME unten).
NICHT_AM_STAPELSTECKER = ("frei", "SEL_OUT", "RUN", "ADC_VREF")

STECKER_NETZE = {rolle: rolle for rolle in set(S.PIN_ROLLE.values())
                  if rolle not in NICHT_AM_STAPELSTECKER}

# Physische Pico-Pins mit Vertragsrolle "frei" (stack_spec.PIN_ROLLE),
# die tatsaechlich echte GPIO sind -- ihre Bezeichnung aus dem Pico-
# Datenblatt-Pinout (Raspberry Pi Ltd, "Raspberry Pi Pico Datasheet",
# Release 21, Build 03.07.2026, Abschnitt 2.1 "Raspberry Pi Pico
# pinout", S. 6f., Figure 2). Nur diese 18 Pins werden von
# sockelplatine.py tatsaechlich zum Stapel durchgereicht
# (frei_durchreichen=True unten) -- ABSICHTLICH NICHT enthalten sind
# Pin 30 (RUN) und Pin 35 (ADC_VREF): stack_spec.PIN_ROLLE fuehrt auch
# sie generisch als "frei" (die Voreinstellung fuer jeden nicht
# ausdruecklich zugewiesenen Pin, unabhaengig davon, ob er ueberhaupt
# ein GPIO ist), aber keiner der beiden ist ein GPIO. RUN ist der
# aktiv-LOW Reset-Eingang des RP2040 mit eigenem ~50-kOhm-Pullup nach
# 3V3 (Datenblatt, selber Abschnitt, S. 7: "RUN is the RP2040 enable
# pin... To reset RP2040, short this pin low.") -- ihn ungeprueft durch
# den ganzen Stapel zu reichen, gaebe jedem Modul die Moeglichkeit, den
# Pico zurueckzusetzen. ADC_VREF ist die (aus 3V3 gefilterte) Referenz-
# spannung des ADC, kein digitales Signal. Beide bleiben deshalb auf
# J2 no_connect, obwohl PIN_ROLLE sie technisch als "frei" fuehrt --
# eine bewusste Entscheidung dieser Runde (Aufgabe-4-Fix-1), keine
# Erweiterung des Vertrags selbst (stack_spec traegt bewusst nur Pin-
# Nummern, keine GPIO-Namen, s. Kommentar dort).
PIN_GPIO_NAME = {
    11: "GP8", 12: "GP9", 14: "GP10", 15: "GP11", 16: "GP12",
    17: "GP13", 19: "GP14", 20: "GP15", 21: "GP16", 22: "GP17",
    24: "GP18", 25: "GP19", 26: "GP20", 27: "GP21", 29: "GP22",
    31: "GP26", 32: "GP27", 34: "GP28",
}

# Was die Endstufe (z.B. der Motortreiber im Motormodul, Aufgabe 5)
# anschliesst -- lokale Netze am Modul-MCU, keine Stecker-Rollen. NOTAUS
# ist die Ausnahme: die kommt vom Stecker (global, wired-OR).
NETZE_NACH_AUSSEN = {
    "IN1": "IN1",
    "IN2": "IN2",
    "NSLEEP": "NSLEEP",
    "NFAULT": "NFAULT",
    "IPROPI": "IPROPI",
    "NOTAUS": STECKER_NETZE["NOTAUS"],
}

# Zwei Kennwiderstaende, nicht einer -- zwei ADC-Kanaele, 16 Stufen
# (stack_spec.ID_WIDERSTAENDE) macht 256 Modultypen.
ANZAHL_KENNWIDERSTAENDE = 2

# RC-Loeschglied an CLR (SN74LVC1G175, aktiv LOW): 100 kOhm / 1 uF,
# tau = R*C = 100e3 * 1e-6 = 0.1 s. CLR bleibt LOW (Kette geloescht),
# bis die Spannung am Knoten die Schwelle VIH der LVC-Familie erreicht;
# das geschieht bei rund 1.1*tau =~ 110 ms nach Erreichen der
# Versorgungsspannung. Das muss laenger sein als der Spannungsanstieg
# der Versorgung -- ein linearer 5V/3V3-Regler (K7805 + Modul-eigene
# Entkopplung) braucht ueblicherweise deutlich unter 10 ms, damit bleibt
# reichlich Marge. Kein Datenblattwert (kein Bauteil dafuer im Vertrag
# festgelegt), sondern eine bewusst grosszuegige Auslegung.
RC_LOESCH_R_OHM = 100000.0
RC_LOESCH_C_F = 1e-6
RC_TAU_S = RC_LOESCH_R_OHM * RC_LOESCH_C_F


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C", "Device.kicad_sym", "C")
    sch.lib_extends("MCU_ST_STM32C0:STM32C011F6Px", "MCU_ST_STM32C0.kicad_sym",
                     "STM32C011F_4-6_Px", "STM32C011F6Px")
    sch.lib("74xGxx:74LVC1G175", "74xGxx.kicad_sym", "74LVC1G175")
    sch.lib("74xGxx:74LVC2G00", "74xGxx.kicad_sym", "74LVC2G00", multiunit=True)
    sch.lib("74xGxx:74LVC1G08", "74xGxx.kicad_sym", "74LVC1G08")
    sch.lib("Connector_Generic:Conn_02x20_Odd_Even", "Connector_Generic.kicad_sym",
            "Conn_02x20_Odd_Even")
    sch.lib("Connector_Generic:Conn_01x02", "Connector_Generic.kicad_sym", "Conn_01x02")
    sch.lib("Connector_Generic:Conn_02x02_Odd_Even", "Connector_Generic.kicad_sym",
            "Conn_02x02_Odd_Even")


def _stapelstecker(sch, ref, ox, oy, frei_durchreichen=False):
    """J100/J2: der 2x20-Stapelstecker, Pin fuer Pin aus stack_spec.PIN_ROLLE.

    frei_durchreichen=False (Vorgabe, jedes Modul -- J100): freie GPIO
    bleiben no_connect. Ein Modul, das einen freien GPIO tatsaechlich
    braucht, verdrahtet ihn selbst in seinem eigenen Schaltplan -- eine
    stumme Stichleitung mit demselben Label wie auf der Sockelplatine
    waere sonst auf jedem Modul unbenutzter Ballast.

    frei_durchreichen=True (nur die Sockelplatine, J2): dieselben Pins
    werden stattdessen unter ihrem GPIO-Namen (PIN_GPIO_NAME) auf ein
    Label gelegt. Der Sockel ist die einzige Platine, die den Pico
    selbst traegt -- reicht er einen freien GPIO nicht durch, erreicht
    ihn ueberhaupt kein Modul im Stapel (Befund 1, Aufgabe-4-Fix-1:
    der Stapelstecker leitet zwar mechanisch durch, aber ohne einen
    Draht vom Pico dorthin haengt an dem Leiter nichts). Absichtlich
    verschieden von der Modulseite, kein Versehen -- NICHT durch
    Vereinheitlichen "aufraeumen": s. sockelplatine.py fuer die
    Gegenseite dieser Entscheidung.
    """
    sch.bauteil(ref, "Connector_Generic:Conn_02x20_Odd_Even", (ox, oy),
                "Stapelstecker 2x20", FP_HDR_2X20, rot=0,
                roff=(-5.08, 25.4), voff=(-5.08, 27.94))
    for pin in range(1, 41):
        rolle = S.PIN_ROLLE[pin]
        richtung = "L" if pin % 2 else "R"
        if rolle == "SEL_OUT":
            # SEL_OUT ist seit Befund 2 (Aufgabe-4-Fix-1) eine echte
            # Vertragsrolle (stack_spec.RESERVIERT), aber KEIN Pin
            # dieses 2x20-Stapelsteckers -- die Auswahlkette laeuft
            # ueber den eigenen STECKER_KETTE (stack_spec.py). Deshalb
            # ausdruecklich no_connect statt eines STECKER_NETZE[rolle]-
            # Nachschlags: STECKER_NETZE fuehrt "SEL_OUT" absichtlich
            # nicht (s. dort), ein unveraenderter Nachschlag liefe hier
            # in einen KeyError.
            sch.nc(ref, str(pin))
        elif rolle == "frei":
            if frei_durchreichen and pin in PIN_GPIO_NAME:
                sch.netz(ref, str(pin), richtung, PIN_GPIO_NAME[pin])
            else:
                sch.nc(ref, str(pin))
        elif not S.IST_BELEGBAR(pin):
            # Bis 2026-09-01 stand hier die Liste
            # ("3V3_EN", "VSYS", "VBUS", "RUN", "ADC_VREF") als Literal.
            # Fuer RUN und ADC_VREF war sie begruendet, fuer die drei
            # anderen nicht -- und der Vertrag wusste von keiner davon.
            # Jetzt kommt sie aus stack_spec.NICHT_BELEGBAR, samt
            # Begruendung je Pin, und tools/vertrag_doku.py zeigt sie.
            # tests/test_modulsockel.py haelt beide Seiten zusammen.
            sch.nc(ref, str(pin))
        else:
            sch.netz(ref, str(pin), richtung, STECKER_NETZE[rolle])


def _kettenstecker(sch, ref_oben, ref_unten, ox, oy):
    """J101/J102: der zweipolige Kettenstecker (STECKER_KETTE).

    Pin 1 traegt SEL, unterschiedlich benannt je Richtung (SEL_IN von
    oben, SEL_OUT nach unten) -- Pin 2 ist auf beiden Seiten GND.
    """
    assert S.STECKER_KETTE["pins"][1] == "SEL"
    assert S.STECKER_KETTE["pins"][2] == "GND"
    sch.bauteil(ref_oben, "Connector_Generic:Conn_01x02", (ox, oy),
                "Kettenstecker, Buchse oben (SMD)", FP_SKT_1X02, rot=0,
                roff=(-5.08, 3.81), voff=(-5.08, 6.35))
    sch.netz(ref_oben, "1", "L", "SEL_IN")
    sch.netz(ref_oben, "2", "L", "GND")
    sch.bauteil(ref_unten, "Connector_Generic:Conn_01x02", (ox, oy - 10.16),
                "Kettenstecker, Stift unten (SMD)", FP_HDR_1X02, rot=0,
                roff=(-5.08, 3.81), voff=(-5.08, 6.35))
    sch.netz(ref_unten, "1", "L", "SEL_OUT")
    sch.netz(ref_unten, "2", "L", "GND")


def _leistungsstecker(sch, ref_oben, ref_unten, ox, oy):
    """J103/J104: 2x2-Leistungsstecker, durchgereicht (Buchse oben /
    Stift unten, Pin fuer Pin dasselbe Netz -- kein Stapelstecker, siehe
    hardware/bauteile-1b.md, Beleg 4)."""
    netze = {"1": "PWR24V", "2": "GND", "3": "PWR24V", "4": "GND"}
    sch.bauteil(ref_oben, "Connector_Generic:Conn_02x02_Odd_Even", (ox, oy),
                "Leistungsstecker, Buchse oben (SMD)", FP_SKT_2X02, rot=0,
                roff=(-5.08, 3.81), voff=(-5.08, 6.35))
    for pin, name in netze.items():
        sch.netz(ref_oben, pin, "L" if pin in ("1", "3") else "R", name)
    sch.bauteil(ref_unten, "Connector_Generic:Conn_02x02_Odd_Even", (ox, oy - 7.62),
                "Leistungsstecker, Stift unten (SMD)", FP_HDR_2X02, rot=0,
                roff=(-5.08, 3.81), voff=(-5.08, 6.35))
    for pin, name in netze.items():
        sch.netz(ref_unten, pin, "L" if pin in ("1", "3") else "R", name)


def _kennwiderstand(sch, ref_ober, ref_kenn, ox, oy, netz):
    """Ein Kennwiderstand-Spannungsteiler: 3V3 -[Oberwiderstand]- netz
    -[Kennwiderstand]- GND. R_ober ist immer stack_spec.ID_OBEN; der
    Wert von R_kenn haengt vom Modultyp ab (stack_spec.ID_WIDERSTAENDE)
    und wird hier nur als Platzhalter eingetragen -- die konkrete Wahl
    trifft die Stueckliste des jeweiligen Moduls."""
    sch.bauteil(ref_ober, "Device:R", (ox, oy), "%.0f (ID_OBEN)" % S.ID_OBEN,
                FP_R0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz(ref_ober, "1", "U", "3V3")
    sch.netz(ref_ober, "2", "D", netz)
    sch.bauteil(ref_kenn, "Device:R", (ox, oy - 10.16), "Kennwiderstand (Modultyp)",
                FP_R0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz(ref_kenn, "1", "U", netz)
    sch.netz(ref_kenn, "2", "D", "GND")


#: U100 (STM32C011F6P6, TSSOP-20) hat 20 Pins; 15 davon vergibt einbauen()
#: fest (Bus, Versorgung, Kette, Endstufen-Netze, Bootlader). Fuenf bleiben
#: ohne modulspezifische Rolle -- PC14/PC15/PA7/PA8 sind echte, freie GPIO
#: (Pin-Richtung hier vermerkt, aus der Symbolgeometrie ausgemessen:
#: MCU_ST_STM32C0.kicad_sym, STM32C011F_4-6_Px, x=-17.78 -> "L",
#: x=+17.78 -> "R"). PA13 (Pin 18) ist zugleich SWDIO und bleibt deshalb
#: IMMER no_connect -- ein Modul, das den Debug-Pin fuer eigene Zwecke
#: kapert, verliert die Moeglichkeit, es je wieder per SWD anzusprechen,
#: falls die Firmware haengt. Aufgabe 5 (Motormodul) ist die erste
#: Nutzerin: drei der vier Pins tragen dort SENSOR_3V3/SCHLEIFE_1/
#: SCHLEIFE_2 (der Optokoppler-Ausgang und die zwei Schleifenknoten der
#: Notaus-Kanaele muessen an den MCU; SCHLEIFE_1/2 hiessen bis zur
#: Ruhestrom-Umstellung NOTAUS_1/2, s. tools/sch/motormodul.py) -- ohne diese Konstante haette
#: einbauen() sie unbedingt auf nc() gelegt, und ein nachtraeglicher
#: netz()-Aufruf auf demselben Pin waere ein Widerspruch (no_connect UND
#: Draht auf demselben Punkt).
ZUSATZ_PIN_RICHTUNG = {"2": "L", "3": "L", "14": "R", "15": "R"}


def einbauen(sch, ox, oy, mit_flipflop=True, zusatz_pins=None):
    """Baut den Modulsockel-Block bei (ox, oy) in `sch` ein.

    mit_flipflop=True (Vorgabe): voller Modul-Block -- MCU, Flipflop,
    Gatter, Kennwiderstaende, alle Stecker. Fuer jedes Modul.
    mit_flipflop=False: nur die Steckerteile, ohne MCU/Flipflop/Gatter/
    Kennwiderstaende -- fuer die Sockelplatine (Aufgabe 4), die kein
    Modul ist und keinen eigenen Modultyp hat.

    zusatz_pins: optionales dict {Pinnummer(str): Netzname} fuer die vier
    freien U100-Pins aus ZUSATZ_PIN_RICHTUNG (PC14/PC15/PA7/PA8, Pins
    "2"/"3"/"14"/"15"). Ein hier genannter Pin bekommt sch.netz(...) mit
    dem gegebenen Namen statt sch.nc(...); nicht genannte Pins bleiben wie
    bisher no_connect. Pin "18" (PA13/SWDIO) ist nicht waehlbar -- s.
    ZUSATZ_PIN_RICHTUNG-Kommentar.

    Liefert ein dict mit den Netznamen, die die Endstufe braucht
    (== NETZE_NACH_AUSSEN).
    """
    zusatz_pins = zusatz_pins or {}
    unbekannt = set(zusatz_pins) - set(ZUSATZ_PIN_RICHTUNG)
    if unbekannt:
        raise ValueError("zusatz_pins kennt nur %s, nicht %s"
                          % (sorted(ZUSATZ_PIN_RICHTUNG), sorted(unbekannt)))
    _load_libs(sch)

    # PWR_FLAG auf GND und 3V3: ohne einen "power_out"-Pin irgendwo im
    # Netz meldet die ERC "Input Power pin not driven" fuer JEDES
    # power_in-Pin auf GND/3V3 (auch die power:GND/power:+3V3-Symbole
    # selbst sind power_in, kein power_out -- eigene Messung per
    # kicad-cli sch erc gegen ein Minimalbeispiel). Genau dafuer gibt es
    # power:PWR_FLAG; led_dimmer/gen_sch.py nutzt dasselbe Bauteil fuer
    # seine eigenen unversorgten Netze (#FLG1/#FLG2).
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")
    sch.bauteil("#FLG101", "power:PWR_FLAG", (ox - 20.32, oy + 38.1), "PWR_FLAG", "")
    sch.netz("#FLG101", "1", "D", "GND")
    sch.bauteil("#FLG102", "power:PWR_FLAG", (ox - 20.32, oy + 30.48), "PWR_FLAG", "")
    sch.netz("#FLG102", "1", "D", "3V3")

    _stapelstecker(sch, "J100", ox, oy + 38.1)
    _kettenstecker(sch, "J101", "J102", ox, oy - 20.32)
    _leistungsstecker(sch, "J103", "J104", ox + 254.0, oy + 20.32)

    if mit_flipflop:
        # ------------------------------------------------------- U100 MCU
        sch.bauteil("U100", "MCU_ST_STM32C0:STM32C011F6Px", (ox + 88.9, oy),
                    "STM32C011F6P6", FP_TSSOP20, rot=0,
                    roff=(-17.78, 25.4), voff=(-17.78, 27.94))
        sch.netz("U100", "1", "L", "I2C_SDA")     # PB7
        for _p in ("2", "3"):                       # PC14, PC15
            if _p in zusatz_pins:
                sch.netz("U100", _p, ZUSATZ_PIN_RICHTUNG[_p], zusatz_pins[_p])
            else:
                sch.nc("U100", _p)
        sch.netz("U100", "4", "U", "3V3")           # VDD
        sch.netz("U100", "5", "D", "GND")           # VSS
        # PF2-NRST, aktiv LOW. Kommt direkt von U102 Einheit 2 (NAND),
        # das bereits die Invertierung liefert (NRST = ¬(FLASH_MODE ∧ ¬Q)
        # -- siehe Moduldoku oben bei U102, warum NAND und nicht AND).
        sch.netz("U100", "6", "L", "NRST")
        sch.netz("U100", "7", "R", "ID0")           # PA0
        sch.netz("U100", "8", "R", "ID1")           # PA1
        sch.netz("U100", "9", "R", NETZE_NACH_AUSSEN["IN1"])       # PA2
        sch.netz("U100", "10", "R", NETZE_NACH_AUSSEN["IN2"])      # PA3
        sch.netz("U100", "11", "R", NETZE_NACH_AUSSEN["NSLEEP"])   # PA4
        sch.netz("U100", "12", "R", NETZE_NACH_AUSSEN["NFAULT"])   # PA5
        sch.netz("U100", "13", "R", NETZE_NACH_AUSSEN["IPROPI"])   # PA6
        for _p in ("14", "15"):                      # PA7, PA8
            if _p in zusatz_pins:
                sch.netz("U100", _p, ZUSATZ_PIN_RICHTUNG[_p], zusatz_pins[_p])
            else:
                sch.nc("U100", _p)
        sch.netz("U100", "16", "R", "FLASH_RX")     # PA9/PA11 (TX des MCU)
        sch.netz("U100", "17", "R", "FLASH_TX")     # PA10/PA12 (RX des MCU)
        sch.nc("U100", "18")                        # PA13 (SWDIO, unbenutzt)
        sch.netz("U100", "19", "R", "BOOT0")        # PA14
        sch.netz("U100", "20", "L", "I2C_SCL")      # PB6

        # C100: Abblockkondensator an VDD.
        sch.bauteil("C100", "Device:C", (ox + 109.22, oy + 22.86), "100n", FP_C0805,
                    rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
        sch.netz("C100", "1", "U", "3V3")
        sch.netz("C100", "2", "D", "GND")

        # ------------------------------------------------- U101 Flipflop
        sch.bauteil("U101", "74xGxx:74LVC1G175", (ox + 139.7, oy + 20.32),
                    "SN74LVC1G175", FP_SOT363, rot=0,
                    roff=(-12.7, 15.24), voff=(-12.7, 17.78))
        sch.netz("U101", "1", "L", "SEL_CLK")   # CP
        sch.netz("U101", "2", "D", "GND")       # GND
        sch.netz("U101", "3", "L", "SEL_IN")    # D
        sch.netz("U101", "4", "R", "SEL_OUT")   # Q
        sch.netz("U101", "5", "U", "3V3")       # VCC
        sch.netz("U101", "6", "L", "NCLR")      # ~CLR

        # R102/C101: lokales RC-Loeschglied an CLR, siehe RC_TAU_S oben.
        sch.bauteil("R102", "Device:R", (ox + 160.02, oy + 30.48),
                    "%.0fk" % (RC_LOESCH_R_OHM / 1000.0), FP_R0805, rot=0,
                    roff=(2.54, -1.27), voff=(2.54, 1.27))
        sch.netz("R102", "1", "U", "3V3")
        sch.netz("R102", "2", "D", "NCLR")
        sch.bauteil("C101", "Device:C", (ox + 172.72, oy + 30.48),
                    "%.0fn" % (RC_LOESCH_C_F * 1e9), FP_C0805, rot=0,
                    roff=(2.54, -1.27), voff=(2.54, 1.27))
        sch.netz("C101", "1", "U", "NCLR")
        sch.netz("C101", "2", "D", "GND")

        # -------------------------------------------------- U102 Dual-NAND
        # Einheit 1: NQ = NAND(Q,Q) = ¬Q (Pins 1,2,7). Beide Eingaenge
        # ABSICHTLICH auf SEL_OUT (Q) zusammengefuehrt -- ein NAND mit
        # kurzgeschlossenen Eingaengen ist ein Inverter. Das ersetzt das
        # fruehere Einzel-NOT-Gatter (SN74LVC1G04); siehe Moduldoku oben
        # bei U102, warum das kein Verdrahtungsfehler ist.
        sch.bauteil("U102", "74xGxx:74LVC2G00", (ox + 175.26, oy - 5.08),
                    "SN74LVC2G00DCUR", FP_VSSOP8, rot=0, einheit=1,
                    roff=(-15.24, 10.16), voff=(-15.24, 12.7))
        sch.netz("U102", "1", "L", "SEL_OUT")   # A = Q
        sch.netz("U102", "2", "L", "SEL_OUT")   # B = Q (mit A kurzgeschlossen)
        sch.netz("U102", "7", "R", "NQ")        # Y = NAND(Q,Q) = ¬Q
        # Einheit 2: NRST = NAND(FLASH_MODE, NQ) = ¬(FLASH_MODE ∧ ¬Q)
        # (Pins 3,5,6) -- die fehlende Invertierung, direkt an PF2-NRST
        # des MCU (siehe Moduldoku oben bei U102, warum NAND und nicht
        # AND). NICHT auf AND zurueckstellen, auch wenn kette.py "AND"
        # nahelegt.
        sch.bauteil("U102", "74xGxx:74LVC2G00", (ox + 175.26, oy - 20.32),
                    "SN74LVC2G00DCUR", FP_VSSOP8, rot=0, einheit=2,
                    roff=(-15.24, -5.08), voff=(-15.24, -2.54))
        sch.netz("U102", "5", "L", "FLASH_MODE")
        sch.netz("U102", "6", "L", "NQ")
        sch.netz("U102", "3", "R", "NRST")
        # Einheit 3: gemeinsame Versorgung (Pins 4,8)
        sch.bauteil("U102", "74xGxx:74LVC2G00", (ox + 200.66, oy - 12.7),
                    "SN74LVC2G00DCUR", FP_VSSOP8, rot=0, einheit=3,
                    roff=(-5.08, -12.7), voff=(-5.08, -10.16))
        sch.netz("U102", "4", "D", "GND")
        sch.netz("U102", "8", "U", "3V3")

        # --------------------------------------------------------- U103 AND
        # BOOT0 = FLASH_MODE ∧ Q, unveraendert eine reine UND-Funktion
        # (siehe Moduldoku oben bei U103) -- kein Gegenstueck im
        # Dual-NAND U102, weil ein homogenes Dual-Gatter nicht eine
        # NAND- und eine AND-Einheit zugleich sein kann.
        sch.bauteil("U103", "74xGxx:74LVC1G08", (ox + 139.7, oy - 10.16),
                    "SN74LVC1G08", FP_SOT353, rot=0,
                    roff=(-7.62, 12.7), voff=(-7.62, 15.24))
        sch.netz("U103", "1", "L", "FLASH_MODE")  # A
        sch.netz("U103", "2", "L", "SEL_OUT")      # B = Q
        sch.netz("U103", "3", "D", "GND")
        sch.netz("U103", "4", "R", "BOOT0")        # Y = FLASH_MODE ∧ Q
        sch.netz("U103", "5", "U", "3V3")

        # -------------------------------------------- R100/R101/R104/R105
        _kennwiderstand(sch, "R104", "R100", ox + 20.32, oy - 30.48, "ID0")
        _kennwiderstand(sch, "R105", "R101", ox + 35.56, oy - 30.48, "ID1")

    return dict(NETZE_NACH_AUSSEN)


if __name__ == "__main__":
    import gen

    sch = gen.Schaltplan("modulsockel_vorschau", "Modulsockel (Vorschau)",
                          "2026-08-31")
    einbauen(sch, 0.0, 0.0, mit_flipflop=True)
    ziel = os.path.join(HERE, "..", "..", "hardware", "kicad", "_vorschau",
                         "Modulsockel.kicad_sch")
    pfad = sch.schreiben(ziel)
    print("keine unverbundenen Pins -- geschrieben:", pfad)

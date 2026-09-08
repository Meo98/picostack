# -*- coding: utf-8 -*-
"""Schaltplan-Generator der Dimmer-Module (1, 3 und 4 Kanaele).

EIN Generator fuer alle drei Vertragsvarianten (stack_spec.MODULTYPEN:
0x10 Dimmer1, 0x11 Dimmer3, 0x12 Dimmer4) -- die Varianten
unterscheiden sich NUR in der Zahl der bestueckten Kanaele. Aufbau je
Modul:

  * Modulsockel-Block (modulsockel.einbauen): MCU, Flipflop-Kette,
    Gatter, Kennwiderstaende, alle Stecker -- identisch zum Motormodul.
  * Versorgungszelle (tools/sch/versorgung.py, Task 6, ERSETZT den
    vorherigen Q10/R11/R12/D10/C12-Strang): Verpolschutz + TVS +
    Stuetzkondensator + 5-V-Regler + VSYS-Diode, dieselbe Zelle wie im
    Motormodul (Task 5) -- volle Herleitung UND der behobene v1-
    Polungsfehler stehen in versorgung.py bzw. motormodul.py, hier nur
    der Verweis. Q10/R11/R12/D10/C12 sind ERSATZLOS entfallen, s.
    Kommentar vor `_stapel_speist_lokal()` unten.
  * Je Kanal n: Low-Side-N-MOSFET Qn (NCE6020AK, TO-252) mit
    Gate-Vorwiderstand RGn (100 Ohm) und Gate-Pulldown RPn (100 kOhm),
    Freilaufdiode Dn (SS36C, Drain -> +24V) und Schraubklemme Jn
    (Pin 1 = +24V, Pin 2 = geschaltetes Minus der Last).

KANAL->PIN-ZUORDNUNG (hiermit festgelegt, Firmware richtet sich
danach): PWM1 = Pin "15" (PA8), PWM2 = Pin "14" (PA7), PWM3 = Pin "2"
(PC14), PWM4 = Pin "3" (PC15). PA8/PA7 zuerst, weil sie am STM32C011
Timerkanaele tragen (DS13866, Tabelle "Pin assignment": PA8 = TIM1_CH1,
PA7 = TIM1_CH1N/TIM3_CH2); PC14/PC15 sind reine GPIO -- Kanal 3 und 4
dimmen notfalls per Software-PWM. Deshalb hat der Ein-Kanal-Dimmer
IMMER Hardware-PWM.

**Task 6, PWM3/4 NICHT auf PA5/PA6 verlegt -- gepruefte, dokumentierte
Ausnahme (kein Versehen).** Der Auftrag verlangte, Kanal 3/4 von den
OSC32-Pins PC14/PC15 (schwacher Treiber, s. naechster Absatz) auf
"regulaere" Port-A-Pins zu verlegen, mit dem Vorschlag Pin "12"/"13"
(PA5/PA6) -- UNTER DER BEDINGUNG, dass diese Pins im Nest tatsaechlich
frei sind. Beides selbst geprueft, mit gegensaetzlichem Ergebnis:
  * Pin-Namen stimmen: `MCU_ST_STM32C0.kicad_sym`, Symbol
    "STM32C011F_4-6_Px_1_1", eigene Extraktion aller Pin-Name/Nummer-
    Paare -- Pin "12" traegt tatsaechlich den Symbolnamen "PA5", Pin
    "13" "PA6" (und Pin "2"/"3" tatsaechlich "PC14"/"PC15", mit den
    Alternate-Functions "RCC_OSCX_IN"/"RCC_OSCX_OUT"/"RCC_OSC32_EN" --
    das belegt die "schwacher Treiber"-Sorge des Auftrags: das sind die
    externen 32,768-kHz-Quarzpins, keine gewoehnlichen GPIO).
  * Aber "frei im Nest" stimmt NICHT: `tools/sch/modulsockel.py::
    einbauen()` verdrahtet Pin 9/10/11/12/13 (PA2..PA6) UNBEDINGT --
    innerhalb von `if mit_flipflop:`, unabhaengig vom aufrufenden Modul
    -- auf die festen Netznamen IN1/IN2/NSLEEP/NFAULT/IPROPI
    (`modulsockel.NETZE_NACH_AUSSEN`). Das gilt fuer JEDES Modul mit
    `mit_flipflop=True`, auch den Dimmer, der gar keinen DRV8876 hat --
    diese fuenf Pins bleiben dann einfach als unbenutzte
    Ein-Pin-Stichnetze stehen, sind aber elektrisch bereits VERGEBEN.
    Der einzige Weg, ueberhaupt einen zusaetzlichen Netznamen auf einen
    U100-Pin zu legen, ist der `zusatz_pins`-Parameter von einbauen(),
    und der akzeptiert ausschliesslich die vier Pins in
    `modulsockel.ZUSATZ_PIN_RICHTUNG` ("2"/"3"/"14"/"15" == PC14/PC15/
    PA7/PA8) -- ein Aufruf mit "12" oder "13" wirft dort ausdruecklich
    `ValueError` (eigene Pruefung des Codes: `unbekannt = set(zusatz_
    pins) - set(ZUSATZ_PIN_RICHTUNG)`).

  Ausgezaehlt bleibt damit: JEDER Port-A-Pin von U100 traegt bereits
  eine feste Rolle -- PA0/PA1 (ID0/ID1), PA2/PA3 (IN1/IN2), PA4/PA5/PA6
  (NSLEEP/NFAULT/IPROPI), PA7/PA8 (hier: PWM2/PWM1), PA9(11)/PA10(12)
  (FLASH_RX/FLASH_TX), PA13 (SWDIO, dauerhaft no_connect), PA14
  (BOOT0). Es gibt also, ueber die bereits an Kanal 1/2 vergebenen
  PA8/PA7 hinaus, GENAU KEINE freien Port-A-Pins -- nicht "die beiden
  mit der niedrigsten Nummer", sondern keinen einzigen. Frei bleiben
  ausschliesslich PC14/PC15 (Port C, dieselben OSC32-Pins, die der
  Auftrag vermeiden wollte).

  Eine Verlegung waere nur durch eine Aenderung an `modulsockel.py`
  selbst moeglich (z.B. NSLEEP/NFAULT/IPROPI bedingt statt unbedingt
  verdrahten, oder ZUSATZ_PIN_RICHTUNG um Pin "12"/"13" erweitern) --
  das ist eine Aenderung an gemeinsamem Code, der auch das bereits
  fertige Motormodul (Task 5) traegt, und damit ausdruecklich NICHT im
  Auftrag dieser Aufgabe (Modify-Liste: nur `dimmermodul.py`). PWM_PINS
  bleibt deshalb UNVERAENDERT (Kanal 3/4 weiter auf Pin "2"/"3", PC14/
  PC15, mit Software-PWM als Ausweichloesung, s. Absatz oben) -- diese
  Erkenntnis ist der zentrale offene Punkt dieser Aufgabe und steht so
  auch im Aufgabenbericht, nicht nur hier.

GATE DIREKT AM 3,3-V-PIN: Der Kanal-FET ist bei VGS = 3,3 V nicht
vollstaendig durchgesteuert (Datenblatt spezifiziert RDS(on) bei 10 V
und 4,5 V). Das VIERKANALIGE LED-Dimmer-Board des Espace des
Inventions treibt NCE6050KA seit seiner Inbetriebnahme direkt aus
3,3-V-GPIO und bleibt bei 3 A je Kanal handwarm -- fuer LED-Lasten
dieser Groessenordnung reicht die Ansteuerung nachweislich. ERSATZ
2026-09-04: Der NCE6050KA ist bei JLC/LCSC ausverkauft; bestueckt wird
der NCE6020AK (gleiche Familie, gleiches Gehaeuse, gleiches
V_GS(th)-Limit "2.5V" laut LCSC-Rohdaten, RDS(on) 40 mOhm bei 4,5 V
statt 20 mOhm bei 10 V). Die Espace-Felderfahrung gilt woertlich nur
fuer den 6050KA; beim 6020AK ist die Rechnung konservativ dieselbe
(40 mOhm x (3 A)^2 = 0,36 W je Kanal, TO-252 auf Masseflaeche traegt
das), am ersten bestueckten Board aber nachzumessen. Wer mehr Strom
schalten will, braucht einen Gatetreiber (und sollte ein eigenes
Modul vorschlagen).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import modulsockel      # noqa: E402
import stack_spec as S  # noqa: E402
import versorgung        # noqa: E402  (ersetzt den alten Q10-Strang, s. unten)

FP_R0805 = modulsockel.FP_R0805
FP_C0805 = modulsockel.FP_C0805
FP_TO252 = "Package_TO_SOT_SMD:TO-252-3_TabPin2"
# Standard-Padset (nicht die Handloet-Variante des Motormoduls): die
# Dimmer-Dioden werden maschinell bestueckt, und nur so passen vier
# Freilaufdioden aufs Brett (s. spec_dimmer_basis).
FP_TVS_SMC = "Diode_SMD:D_SMC"
# FP_CP_RADIAL (C12) ist mit dem alten Verpolschutz-Strang ENTFALLEN --
# der gleichnamige Kondensator C90 lebt jetzt in tools/sch/versorgung.py,
# s. Kommentar vor `_stapel_speist_lokal()` unten.
# 3,5-mm-Klemme (13,5 A) statt der 5,08er des Motormoduls -- vier
# grosse Klemmen passen nicht an die Klemmenkante (s. spec_dimmer_basis).
FP_KLEMME_2 = ("TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal")

QK_WERT = "NCE6020AK"    # Kanal-FET: 60 V, 20 A, TO-252, LCSC C108639
                         # (Produktseite gesichtet 2026-09-04; Ersatz
                         # fuer den ausverkauften NCE6050KA, s. oben)
DK_WERT = "SS36C"        # Freilauf: Schottky 60 V 3 A, DO-214AB --
                         # das C unterscheidet bei MDD das SMC-Gehaeuse
                         # vom SMA-"SS36" (C16015), s. bauteile-dimmer.md
RG_WERT = "100"
RP_WERT = "100k"
# Gatter-Abblockung (Task 6): C100 (modulsockel.py) blockt nur U100
# (MCU) ab, C101 ist Teil des NCLR-Loeschglieds -- keines von beiden
# deckt U101/U102/U103 (Flipflop/Dual-NAND/AND). Jedes Logik-IC braucht
# einen eigenen 100-nF-Kondensator an seiner VCC/GND-Versorgung (Muster
# wie C14 bei motormodul.U3), s. `_gatter_abblockung()` unten.
C_ABBLOCK_WERT = "100n"
C_ABBLOCK_LCSC = "C49678"   # 100nF/0805, JLCPCB-Basic-Teil

#: Kanalnummer -> Zusatzpin des Modulsockels (s. Docstring).
PWM_PINS = {1: "15", 2: "14", 3: "2", 4: "3"}

#: Variante -> (Typcode, Kanalzahl); direkt am Vertrag verankert.
VARIANTEN = {1: 0x10, 3: 0x11, 4: 0x12}


def _kanal(sch, n, ox, oy):
    """Ein Dimmer-Kanal: Qn, RGn, RPn, Dn, Jn."""
    q, rg, rp, d, j = ("Q%d" % n, "RG%d" % n, "RP%d" % n,
                       "D%d" % n, "J%d" % (4 + n))
    pwm, led = "PWM%d" % n, "LED%d" % n

    sch.bauteil(q, "Transistor_FET:Q_NMOS_GDS", (ox, oy), QK_WERT, FP_TO252,
                rot=0, roff=(2.54, 2.54), voff=(2.54, 5.08))
    sch.netz(q, "1", "L", pwm + "_G")   # G, hinter RGn
    sch.netz(q, "2", "U", led)          # D -> Klemme (Minus der Last)
    sch.netz(q, "3", "D", "GND")        # S

    sch.bauteil(rg, "Device:R", (ox - 17.78, oy + 10.16), RG_WERT, FP_R0805,
                rot=90, roff=(-1.27, -2.54), voff=(1.27, -2.54))
    sch.netz(rg, "1", "L", pwm)
    sch.netz(rg, "2", "R", pwm + "_G")

    sch.bauteil(rp, "Device:R", (ox - 12.7, oy + 12.7), RP_WERT, FP_R0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz(rp, "1", "U", pwm + "_G")
    sch.netz(rp, "2", "D", "GND")

    # Freilauf: Kathode an +24V. LED-Baender sind zwar ueberwiegend
    # ohmsch, aber die Zuleitung ist eine Induktivitaet -- beim
    # Abschalten muss ihr Strom irgendwohin (Muster aus dem
    # LED-Dimmer-Altprojekt, dort D1..D4).
    sch.bauteil(d, "Device:D_Schottky", (ox + 12.7, oy + 10.16), DK_WERT,
                FP_TVS_SMC, rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz(d, "1", "U", "+24V")       # K
    sch.netz(d, "2", "D", led)          # A

    sch.bauteil(j, "Connector:Screw_Terminal_01x02", (ox + 27.94, oy),
                "LED-Kanal %d" % n, FP_KLEMME_2, rot=0,
                roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz(j, "1", "R", "+24V")
    sch.netz(j, "2", "R", led)


# ===================================================================
#  Q10/R11/R12/D10/C12 (v1-Verpolschutz-Strang) ENTFALLEN (Task 6, 2026-09-08)
# ===================================================================
# Frueher stand hier `_leistung()`: ein eigener Verpolschutz (Q10/R11/
# R12) plus TVS (D10) und Stuetzkondensator (C12) zwischen dem
# Stapelnetz "PWR24V" und der lokalen Schiene "+24V" -- wortgleiches
# Muster wie motormodul._endstufe_leistung() (Task 5, vor dessen
# eigenem Fix). Diese Funktion ist ERSATZLOS entfallen -- ersetzt durch
# `versorgung.bauen()` (s. `bauen()` unten), dieselbe Zelle, die Task 5
# fuer das Motormodul einfuehrt: Verpolschutz + TVS + Stuetzkondensator
# + 5-V-Regler + VSYS-Diode, mit einer eigenen Einspeiseklemme J90
# statt "PWR24V" als Eingang, UND -- anders als das alte Muster --
# RICHTIG gepolt (volle Fehleranalyse in tools/sch/versorgung.py, Kopf-
# Docstring, und in motormodul.py vor `_stapel_speist_lokal()`).


def _stapel_speist_lokal(sch, ox, oy):
    """Verbindet "PWR24V" (Stapel, ueber J103/J104 durchgereicht) mit
    "+24V" (lokal, hinter Q90 geschuetzt) zu EINEM elektrischen Knoten.

    Woertlich dasselbe Muster wie motormodul._stapel_speist_lokal() --
    volle Begruendung dort. Kurzfassung: ohne diesen Draht waeren beide
    Netze auf diesem Modul voneinander isoliert, weil modulsockel.
    einbauen() J103/J104 unbedingt auf "PWR24V" legt, aber (seit Q10
    entfallen ist) nichts sonst hier daran haengt. Der Vertrag sieht
    vor, dass EINE Platine im Stapel tatsaechlich extern gespeist wird
    (ihre eigene Klemme J90, s. versorgung.bauen()) und diese Speisung
    ueber den Leistungsstecker an den Rest des Stapels weitergibt. Ist
    das Dimmermodul NICHT die gespeiste Platine (J90 bleibt dann
    unbestueckt/offen), schadet die Verbindung trotzdem nicht: sie
    macht "+24V" und "PWR24V" nur zu Namen fuer denselben Knoten,
    unabhaengig davon, wer ihn tatsaechlich treibt. Verifiziert per
    `kicad-cli sch erc` (0 Fehler, 0 Warnungen)."""
    a = (ox, oy)
    b = (ox + 15.24, oy)
    sch.draht(a, b)
    sch.LABELS.append((a[0], a[1], 0, "+24V"))
    sch.LABELS.append((b[0], b[1], 180, "PWR24V"))


def _gatter_abblockung(sch, ox, oy):
    """Je ein 100-nF-Abblockkondensator fuer U101/U102/U103 (Task 6).

    modulsockel.py deckt bislang nur U100 ab (C100, an dessen VDD/VSS)
    -- C101 ist Teil des NCLR-Loeschglieds, kein Abblockkondensator.
    U101 (SN74LVC1G175, SOT-363), U102 (SN74LVC2G00DCUR, VSSOP-8) und
    U103 (SN74LVC1G08, SOT-353) haengen alle drei mit VCC/GND an
    3V3/GND, aber KEINER hat einen eigenen Kondensator direkt an seiner
    Versorgung -- derselbe Bedarf, den motormodul.py fuer sein eigenes
    Gatter U3 mit C14 deckt (dortiger Kommentar: "Abblockkondensator
    fuer U3, wie ihn jedes Logik-IC braucht"). Referenzen C102/C103/
    C104, direkt im Anschluss an C100/C101 (modulsockel.py) nummeriert.
    Platziert bei y = oy - 45,72 -- knapp 15,24 mm unterhalb der
    Kennwiderstandsreihe (oy - 30,48, s. modulsockel.einbauen()),
    kollidiert also mit keinem Nest-Bauteil; per `kicad-cli sch erc`
    gegen 0 Fehler/0 Warnungen geprueft, nicht nur angenommen.

    Nur fuer DIESES Modul ergaenzt (Aufgabenbrief Task 6) -- dieselbe
    Luecke besteht wahrscheinlich auch im Motormodul (Task 5), das
    modulsockel.py unveraendert uebernimmt; das zu schliessen ist nicht
    Teil dieses Auftrags (Modify-Liste: nur dimmermodul.py) und muesste
    ohnehin in modulsockel.py selbst passieren, um beiden Modulen
    zugutezukommen."""
    for ref, x in (("C102", ox + 152.40), ("C103", ox + 177.80),
                   ("C104", ox + 203.20)):
        sch.bauteil(ref, "Device:C", (x, oy - 45.72), C_ABBLOCK_WERT,
                    FP_C0805, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27),
                    felder={"LCSC": C_ABBLOCK_LCSC})
        sch.netz(ref, "1", "U", "3V3")
        sch.netz(ref, "2", "D", "GND")


def _load_libs(sch):
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C", "Device.kicad_sym", "C")
    sch.lib("Device:D_Schottky", "Device.kicad_sym", "D_Schottky")
    # Generisches FET-Symbol (Pins 1=G, 2=D, 3=S): Typ steht im
    # Wertfeld -- dieselbe Begruendung wie bei motormodul._load_libs().
    # Q_PMOS_GDS wird hier NICHT mehr geladen (Q10 entfallen) --
    # versorgung.bauen() laedt es fuer Q90 selbst.
    sch.lib("Transistor_FET:Q_NMOS_GDS", "Transistor_FET.kicad_sym",
            "Q_NMOS_GDS")
    sch.lib("Connector:Screw_Terminal_01x02", "Connector.kicad_sym",
            "Screw_Terminal_01x02")


def bauen(sch, ox, oy, kanaele):
    _load_libs(sch)
    zusatz = {PWM_PINS[n]: "PWM%d" % n for n in range(1, kanaele + 1)}
    # frei_durchreichen=True (NEU, Task 6): das Dimmermodul ist ein
    # v2-Modul und traegt die Randpads (J95/J96, s. modulsockel.
    # randpads() unten) -- ohne frei_durchreichen=True legte
    # _stapelstecker() die freien GPIO auf no_connect, und die
    # Randpads-Labels haetten kein Gegenstueck (Leerlauf-Loetpad).
    # Dasselbe Muster wie motormodul.bauen() (Task 5).
    modulsockel.einbauen(sch, ox, oy, mit_flipflop=True,
                          frei_durchreichen=True, zusatz_pins=zusatz)
    # J95/J96: die 22 unbestueckten Randpads (stack_spec.RANDPADS, v2) --
    # jedes v2-Modul traegt sie. Unabhaengig von einbauen() (s.
    # modulsockel.randpads()-Docstring); die Netznamen (GP.., 3V3, GND)
    # treffen sich mit den frei_durchreichen=True oben gelegten Labels
    # an J100/J105 ausschliesslich ueber den gemeinsamen Namen, nicht
    # ueber einen gemeinsamen Draht.
    modulsockel.randpads(sch)

    _gatter_abblockung(sch, ox, oy)

    # PWR_FLAG auf +24V: dasselbe ERC-Muster wie im Motormodul
    # (kein power_out-Pin im Netz; der MOSFET-Drain ist "passive").
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")
    sch.bauteil("#FLG201", "power:PWR_FLAG", (ox + 279.4, oy + 83.82),
                "PWR_FLAG", "")
    sch.netz("#FLG201", "1", "D", "+24V")

    # Versorgungszelle (Task 6, ersetzt Q10/R11/R12/D10/C12, s.
    # Kommentar oben): platziert an derselben Stelle, an der vorher
    # `_leistung()` sass -- ausreichend Abstand nach oben zu den
    # Kanaelen (die fruehestens bei oy+78,74 beginnen, versorgung.bauen()
    # reicht hoechstens bis oy+48,26) und nach rechts zu jeder Kanalspalte
    # (Kanal 2 beginnt bei ox+431,8, versorgung.bauen() reicht
    # hoechstens bis ox+472,44 -- beide Bloecke ueberlappen sich in x,
    # aber NICHT in y). Geprueft per kicad-cli sch erc (0 Fehler,
    # 0 Warnungen), nicht bloss angenommen.
    versorgung.bauen(sch, ox + 330.2, oy + 15.24)
    # Bindet die geschuetzte lokale Schiene "+24V" (hinter Q90) an die
    # Stapel-Sammelschiene "PWR24V" (an J103/J104) -- s. Docstring dort.
    # Weit rechts von der Versorgungszelle abgesetzt (ox+502,92), damit
    # die beiden Labels nicht mit D91/U90 kollidieren.
    _stapel_speist_lokal(sch, ox + 502.92, oy + 15.24)

    for n in range(1, kanaele + 1):
        _kanal(sch, n, ox + 330.2 + ((n - 1) % 2) * 101.6,
               oy + 78.74 + ((n - 1) // 2) * 55.88)


# ------------------------------------------------------- Erzeugen
DATUM = "2026-09-04"
_ZIELE = {
    kanaele: os.path.join(HERE, "..", "..", "hardware", "kicad",
                          "dimmer%d" % kanaele,
                          "Dimmer%d.kicad_sch" % kanaele)
    for kanaele in VARIANTEN
}


def erzeugen(ziel=None, kanaele=1):
    """Baut den Schaltplan einer Variante (Vorgabe: Dimmer1)."""
    import gen

    name = S.MODULTYPEN[VARIANTEN[kanaele]]["name"]
    sch = gen.Schaltplan(name, name, DATUM, papier="A2")
    bauen(sch, 60.96, 139.7, kanaele)
    pfad = _ZIELE[kanaele] if ziel is None else ziel
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    return sch.schreiben(pfad)


if __name__ == "__main__":
    for kanaele in sorted(VARIANTEN):
        print("Dimmer%d: keine unverbundenen Pins -- geschrieben: %s"
              % (kanaele, erzeugen(kanaele=kanaele)))

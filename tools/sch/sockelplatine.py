"""Die Sockelplatine: traegt den Pico, speist den Stapel, sitzt zuoberst.

Anders als jedes Modul hat der Sockel KEINEN eigenen Modultyp -- er ist
kein Modul (Aufgabe-4-Brief, "Vier Dinge, die der Brief nicht sagen
kann", Punkt 1). Er bekommt deshalb keinen Kleinst-MCU, kein Flipflop,
keine Gatter und keine Kennwiderstaende. Der Rechner des ganzen Stapels
ist hier der Pico selbst (U1) -- der treibt direkt die globalen Leitungen
(FLASH_TX/FLASH_RX/FLASH_MODE/I2C_SDA/I2C_SCL/NOTAUS/SEL_CLK), die bei
jedem Modul ueber modulsockel.py an einen eigenen Kleinst-MCU gehen.

Von modulsockel.py wird ausschliesslich wiederverwendet:
  - die Footprint-Konstanten (FP_R0805, FP_C0805, FP_HDR_1X02,
    FP_HDR_2X02) fuer Bauteile, die auf beiden Plattenarten gleich
    aussehen
  - _stapelstecker() fuer J2 (mit frei_durchreichen=True, seit Aufgabe-
    4-Fix-1 -- s. Punkt 5 unten) -- Punkt 2 unten erklaert, warum genau
    dasselbe Bauteil wie bei jedem Modul zum Einsatz kommt, obwohl die
    Rollenzuordnung (PIN_ROLLE) dieselbe bleibt

modulsockel.einbauen(..., mit_flipflop=False) wird HIER BEWUSST NICHT
aufgerufen: das wuerde zusaetzlich zum Stapelstecker auch beide Haelften
des Kettensteckers (Buchse oben UND Stift unten) und beide Haelften des
Leistungssteckers anlegen. Der Sockel braucht aber nur je eine Haelfte
(Punkt 3 unten) -- deshalb baut dieses Modul J3/J4 selbst, nach demselben
Muster wie modulsockel._kettenstecker()/_leistungsstecker(), aber nur mit
der unteren (Stift-)Haelfte.

Vier Dinge, die der Aufgabenbrief nicht sagen konnte (vom Auftraggeber
nachgereicht, 2026-08-31):

1. Der Sockel ist kein Modul -- kein MCU, kein Flipflop, keine Gatter,
   keine Kennwiderstaende. Nur die Steckerteile werden von modulsockel.py
   wiederverwendet.

2. J2 ist derselbe Stapelstecker-Typ (STECKER_STAPEL, Buchse mit
   durchgehendem Stift) wie bei jedem Modul, obwohl seine obere
   Buchsenoeffnung nie bestueckt wird (der Sockel sitzt zuoberst im
   Stapel, darueber kommt nichts). Eine gewoehnliche Stiftleiste mit
   6,0 mm Stift gaebe bei STAPEL_ABSTAND=13,5 mm nur 2,6 mm
   Einstecktiefe (6,0 mm Stift + 8,5 mm Buchsenhoehe - 11,9 mm Spalt,
   siehe stack_spec.EINSTECKTIEFE_KETTE()-Rechnung fuer das analoge
   Bauteil); der Stapelstecker gibt an dieser Stelle 7,46 mm
   (stack_spec.EINSTECKTIEFE_STAPEL()) -- UND die Geometrie ist so fuer
   die ganze Platinenfamilie identisch, was Lager und Layout
   vereinfacht. Absicht, kein Versehen: die ungenutzte obere
   Buchsenoeffnung von J2 NICHT durch eine guenstigere Stiftleiste
   "aufraeumen".

3. Beim Kettenstecker (J3) traegt der Sockel NUR die Stiftseite -- er
   empfaengt nichts von oben (es gibt nichts ueber dem Sockel), er
   treibt nur nach unten in das oberste Modul. Deshalb hier keine
   J101-aequivalente Buchse: sie haette keinen Gegenpart und ihr Pin 1
   (SEL_IN) bliebe ein Label ohne zweiten Anschluss -- kein Kurzschluss,
   aber unnoetiger Ballast im Schaltplan fuer ein Bauteil, das nie
   bestueckt wuerde.

4. Die Versorgung des Pico ist die gefaehrlichste Stelle dieses
   Schaltplans: +5V (U2-Ausgang) MUSS an VSYS (Pin 39), NIEMALS an
   3V3_OUT (Pin 36) -- dort liegt 5V direkt am Ausgang des internen
   Schaltreglers des Pico und zerstoert ihn. Pin 36 (3V3_OUT) ist
   umgekehrt die QUELLE der 3V3-Schiene fuer den ganzen Stapel: der
   Pico erzeugt sie selbst aus VSYS und speist sie hier in J2 Pin 36
   ein (stack_spec.PIN_ROLLE[36] == "3V3"). tests/test_sockelplatine.py
   sichert das mit einer eigenen, expliziten Pruefung ab (siehe dort).

Nachtrag 2026-08-31 (Aufgabe-4-Fix-1, zwei zusammenhaengende Befunde der
vorigen Runde uebersehen):

5. Befund 1 -- die volle 2x20-Durchreichung fehlte: freie Pico-GPIO
   waren hier UND auf J2 (modulsockel._stapelstecker()) no_connect. Der
   Stapelstecker leitet zwar mechanisch durch, aber ohne einen Draht vom
   Pico zum jeweiligen J2-Pin haengt an diesem Leiter nichts -- kein
   Modul konnte je einen freien GPIO benutzen, obwohl stack_spec.py
   "freie GPIO" ausdruecklich als eine im ganzen Stapel gleiche Netzart
   nennt. Fix: modulsockel._stapelstecker() bekam einen neuen Parameter
   frei_durchreichen (Vorgabe False, unveraendertes Verhalten fuer jedes
   Modul-J100); J2 wird hier mit frei_durchreichen=True aufgerufen, UND
   U1 verdrahtet dieselben Pins unter demselben Netznamen
   (modulsockel.PIN_GPIO_NAME). RUN (Pin 30) und ADC_VREF (Pin 35)
   bleiben trotzdem no_connect -- s. Kommentar bei ihrer Verdrahtung
   unten, warum sie keine echten GPIO sind.

   Befund 2 -- GP8 als lokaler SEL-Treiber kollidiert seit Befund 1: Pin
   11 (GP8) trieb bisher lokal J3, ausdruecklich als "keine
   Vertragsleitung" kommentiert. Das ging nur gut, solange Pin 11 tot
   war -- nach Befund 1 wird er ein durchgereichter freier GPIO, und ein
   Modul, das ihn beansprucht, triebe gegen den Sockel (zwei Ausgaenge
   auf einem Netz). Fix: SEL_OUT bekommt Pin 4 (GP2) zurueck -- der war
   vor der Steckertrennung schon SEL und traegt jetzt wieder eine echte
   Vertragsrolle (stack_spec.PIN_ROLLE[4] == "SEL_OUT",
   stack_spec.RESERVIERT), aber KEIN Pin von J2 (s. Kommentar bei J3
   unten). Pin 11 (GP8) ist seither ein gewoehnlicher freier GPIO.

   Ausserdem in dieser Runde geklaert: AGND (Pin 33) ist laut
   Pico-Datenblatt keine interne Verbindung zu GND, sondern eine eigene
   analoge Massenflaeche, die der Hersteller optional (nicht
   zwingend) mit digitaler Masse verbinden laesst -- s. Kommentar bei
   ihrer Verdrahtung unten. Vollstaendiger Bericht:
   .superpowers/sdd/2026-08-31-etappe-1b-sockel-und-motormodul/
   aufgabe-4-fix1-report.md.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "..")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S  # noqa: E402
import modulsockel      # noqa: E402  (Footprint-Konstanten + _stapelstecker)

# -------------------------------------------------------------- Footprints
# Die Header-Platzhalter (FP_HDR_1X02/FP_HDR_2X02) und die 0805-Footprints
# kommen unveraendert aus modulsockel.py -- siehe dort, warum es
# Platzhalter sind (die echten Spezialteile brauchen eigene
# .kicad_mod-Footprints, Sache der PCB-Layout-Aufgaben).
FP_R0805 = modulsockel.FP_R0805
FP_C0805 = modulsockel.FP_C0805
FP_HDR_1X02 = modulsockel.FP_HDR_1X02   # SMD-Stiftleiste, s. dort
FP_HDR_2X02 = modulsockel.FP_HDR_2X02   # SMD-Stiftleiste, s. dort

FP_PICO = "Module:RaspberryPi_Pico_Common_THT"      # Aufgabenbrief, woertlich
FP_CP_RADIAL = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"   # Aufgabenbrief, woertlich
FP_TVS_SMC = "Diode_SMD:D_SMC_Handsoldering"               # Aufgabenbrief, woertlich
# K7805-2000R3 (SIP-3) hat in den KiCad-Standardbibliotheken kein eigenes
# Symbol/Footprint. hardware/bauteile-1b.md dokumentiert bereits, dass
# der K7805-2000R3 "Fussabdruck-kompatibel zum Recom R-78B5.0-2.0" gilt
# (Etappe 1a, led_dimmer/hardware/README_4ch.md, Abschnitt "U10
# pruefen") -- dieselbe Simplification wird hier uebernommen: Symbol UND
# Footprint des Recom-Bauteils (identische SIP-3-Pinbelegung IN/GND/OUT,
# siehe unten), der WERT des platzierten Bauteils nennt trotzdem den
# tatsaechlich einzukaufenden Teil (K7805-2000R3, LCSC C2931187), nicht
# den Recom-Platzhalter -- das haelt BOM-Auszuege aus der Netzliste
# korrekt, waehrend Symbol/Footprint wiederverwendet werden.
FP_RECOM = "Converter_DCDC:Converter_DCDC_RECOM_R-78B-2.0_THT"
# Terminalblock-Platzhalter fuer J1 -- exakt dieselbe Simplification wie
# led_dimmer/hardware/generator/gen_sch.py fuer sein eigenes J1 (DB128L,
# dieselbe LCSC-Nummer C395868): Symbol "Connector:Screw_Terminal_01x02",
# Footprint ein genormter 5,08-mm-Terminalblock als Platzhalter, bis die
# PCB-Layout-Aufgabe einen eigenen DB128L-Footprint zeichnet.
FP_KLEMME_2 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal"

# ---------------------------------------------------- Kondensatorwerte U2
# Datenblatt MORNSUN "K78xx-2000R3 Series" (Rev. 2025.09.29-A/9),
# S. 4, Abschnitt "Design Reference / 1. Typical application", Tabelle
# "Sheet 1": fuer K7805-2000R3(L) C1 = 22 uF/50 V (Keramik, Spalte fuer
# die ganze Baureihe gemeinsam), C2 = 22 uF/10 V (Keramik). Dasselbe
# Bauteil (K78xx-2000R3-Familie) wird bei LCSC unter DEXU Electronics
# gefuehrt (C2931187, siehe hardware/bauteile-1b.md) -- die dortige
# Herstellerdatei liess sich nicht als Text extrahieren (die von LCSC
# ausgelieferte PDF-Ressource ist eine serverseitig gerenderte
# Bild-Wiedergabe ohne Textebene); die MORNSUN-Anwendungsschaltung ist
# die einzige tatsaechlich gelesene Quelle fuer diese Baureihe und wird
# deshalb explizit als solche zitiert, nicht als DEXU-Originaldatenblatt
# ausgegeben.
#
# C1 auf 22 uF/50 V zu setzen ist im hier vorgegebenen 0805-Footprint
# (Aufgabenbrief, woertlich) NICHT umsetzbar: 0805-Keramikkondensatoren
# mit X7R-Dielektrikum erreichen bei 50 V ueblicherweise nur einige
# hundert nF bis wenige uF (das Kapazitaets-Spannungs-Produkt einer
# 0805-Bauform reicht dafuer nicht) -- 22 uF/50 V ist in der Praxis eine
# 1210- oder groessere Bauform. C1 wird deshalb als lokale
# HF-Abblockung direkt an den Reglerpins auf 100 nF/50 V X7R (0805, ein
# Standardwert, in jeder Baureihe verfuegbar) gesetzt; C3 (220 uF radial,
# eigens im Aufgabenbrief fuer "Stuetzung am 24-V-Eingang" vorgesehen)
# uebernimmt die Speicherkapazitaet, die das Datenblatt mit 22 uF/50 V
# eigentlich meint. C2 bleibt beim Datenblattwert -- 22 uF bei 10-16 V
# ist in 0805 (X5R) eine Standardgroesse, hier mit 16 V statt der
# minimal geforderten 10 V fuer Spannungsreserve ueber der 5-V-Schiene.
C1_WERT = "100n"     # 0805, X7R, 50V -- lokale HF-Abblockung an U2 Pin 1
C2_WERT = "22u"       # 0805, X5R, 16V -- Ausgangskondensator, Datenblattwert
C3_WERT = "220u"      # radial, 50V   -- Stuetzung am 24-V-Eingang (Aufgabenbrief)

# TVS D1: SMCJ30A, unidirektional (LCSC C340696, YANGJIE-Fassung,
# Produktseite gesichtet: DO-214AB/SMC, Vrwm 30V, Vbr 36.8V min., Vc
# 48.4V max. bei 1.5kW/10x1000us -- lcsc.com/product-detail/C340696.html).
# KiCads generisches "Device:D_TVS" ist laut eigener Beschreibung
# ("Bidirectional transient-voltage-suppression diode") explizit
# BIdirektional -- fuer ein unidirektionales Bauteil wie das SMCJ30A
# irrefuehrend (keine echte Anode/Kathode-Polung im Symbol). Stattdessen
# "Device:D_Zener" (Pin 1 = K, Pin 2 = A): elektrisch verhaelt sich ein
# unidirektionaler TVS im Sperrbereich wie eine Lawinen-/Z-Diode, und
# das Symbol zeigt die tatsaechliche Polung -- Kathode (Pin 1) an
# PWR24V, Anode (Pin 2) an GND, klemmt also die positive Schiene gegen
# Masse, sobald sie ueber die Durchbruchspannung steigt.
D1_WERT = "SMCJ30A"

R_I2C_WERT = "4.7k"   # 0805 -- I2C-Abschluss, siehe Aufgabenbrief


def bauen(sch, ox, oy):
    """Baut die Sockelplatine bei (ox, oy) in `sch` ein."""
    sch.lib("Device:R", "Device.kicad_sym", "R")
    sch.lib("Device:C", "Device.kicad_sym", "C")
    sch.lib("Device:C_Polarized", "Device.kicad_sym", "C_Polarized")
    sch.lib("Device:D_Zener", "Device.kicad_sym", "D_Zener")
    sch.lib("Connector:Screw_Terminal_01x02", "Connector.kicad_sym",
            "Screw_Terminal_01x02")
    sch.lib("Connector_Generic:Conn_02x20_Odd_Even", "Connector_Generic.kicad_sym",
            "Conn_02x20_Odd_Even")
    sch.lib("Connector_Generic:Conn_01x02", "Connector_Generic.kicad_sym", "Conn_01x02")
    sch.lib("Connector_Generic:Conn_02x02_Odd_Even", "Connector_Generic.kicad_sym",
            "Conn_02x02_Odd_Even")
    sch.lib("MCU_Module:RaspberryPi_Pico", "MCU_Module.kicad_sym", "RaspberryPi_Pico")
    sch.lib_extends("Converter_DCDC:R-78B5.0-2.0", "Converter_DCDC.kicad_sym",
                     "R-78B1.2-2.0", "R-78B5.0-2.0")
    sch.lib("power:PWR_FLAG", "power.kicad_sym", "PWR_FLAG")

    # ---------------------------------------------------- 24-V-Eingang
    # J1 (Klemme 2-polig, DB128L-5.08-2P-GN-S, LCSC C395868) -> PWR24V/GND,
    # D1 (TVS) direkt am Eingang, C3 (220uF) stuetzt, C1/U2/C2 folgen.
    j1x, j1y = ox, oy
    sch.bauteil("J1", "Connector:Screw_Terminal_01x02", (j1x, j1y), "24V Eingang",
                FP_KLEMME_2, rot=0, roff=(2.54, -6.35), voff=(2.54, -3.81))
    sch.netz("J1", "1", "R", "PWR24V")
    sch.netz("J1", "2", "R", "GND", laenge=7.62)

    # PWR_FLAG auf PWR24V: J1/D1/C3/C1/U2-Eingang sind alle "passive"
    # bzw. "power_in" -- ohne einen power_out-Pin irgendwo im Netz meldet
    # die ERC "Input Power pin not driven" fuer U2 Pin 1 (power_in).
    # Dasselbe Muster wie modulsockel.py fuer GND/3V3 (dort per
    # power_out-Pin am MCU nicht noetig, hier schon, weil kein Bauteil
    # an PWR24V von sich aus "power_out" ist).
    sch.bauteil("#FLG1", "power:PWR_FLAG", (j1x + 12.7, j1y - 15.24), "PWR_FLAG", "")
    sch.netz("#FLG1", "1", "D", "PWR24V")

    sch.bauteil("D1", "Device:D_Zener", (ox + 25.4, oy + 12.7), D1_WERT, FP_TVS_SMC,
                rot=270, roff=(2.54, -2.54), voff=(2.54, 2.54))
    sch.netz("D1", "1", "U", "PWR24V")   # Kathode -> PWR24V (klemmt gegen GND)
    sch.netz("D1", "2", "D", "GND")      # Anode -> GND

    sch.bauteil("C3", "Device:C_Polarized", (ox + 12.7, oy + 25.4), C3_WERT,
                FP_CP_RADIAL, rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C3", "1", "U", "PWR24V")   # Pin 1 = "+" (Device:C_Polarized)
    sch.netz("C3", "2", "D", "GND")

    # ---------------------------------------------------- U2 5-V-Regler
    sch.bauteil("C1", "Device:C", (ox + 40.64, oy + 12.7), C1_WERT, FP_C0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C1", "1", "U", "PWR24V")
    sch.netz("C1", "2", "D", "GND")

    sch.bauteil("U2", "Converter_DCDC:R-78B5.0-2.0", (ox + 63.5, oy),
                "K7805-2000R3", FP_RECOM, rot=0,
                roff=(-7.62, -13.97), voff=(-7.62, -11.43))
    sch.netz("U2", "1", "L", "PWR24V")   # IN
    sch.netz("U2", "2", "D", "GND")      # GND
    sch.netz("U2", "3", "R", "+5V")      # OUT

    sch.bauteil("C2", "Device:C", (ox + 86.36, oy + 12.7), C2_WERT, FP_C0805,
                rot=0, roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("C2", "1", "U", "+5V")
    sch.netz("C2", "2", "D", "GND")

    # ---------------------------------------------------- J4 Leistung
    # Nur die untere (Stift-)Haelfte -- der Sockel speist den Stapel,
    # empfaengt aber selbst keine 24V von oben (es kommt nichts ueber
    # ihm). Dieselbe Pin-Zuordnung wie modulsockel._leistungsstecker()s
    # ref_unten, hier lokal nachgebaut statt importiert, weil jene
    # Funktion immer BEIDE Haelften gemeinsam anlegt.
    j4x, j4y = ox + 20.32, oy - 33.02
    sch.bauteil("J4", "Connector_Generic:Conn_02x02_Odd_Even", (j4x, j4y),
                "Leistungsstecker, Stift SMD (24V in den Stapel)", FP_HDR_2X02, rot=0,
                roff=(-5.08, 3.81), voff=(-5.08, 6.35))
    for pin, name in {"1": "PWR24V", "2": "GND", "3": "PWR24V", "4": "GND"}.items():
        sch.netz("J4", pin, "L" if pin in ("1", "3") else "R", name)

    # ---------------------------------------------------- J3 Kettenstecker
    # Nur die Stiftseite -- Punkt 3 der Moduldoku oben: der Sockel treibt
    # SEL nur nach unten, empfaengt nichts von oben. Getrieben von Pin 4
    # (GP2, physisch), stack_spec.PIN_ROLLE[4] == "SEL_OUT" -- seit
    # Befund 2 (Aufgabe-4-Fix-1) eine echte Vertragsrolle, KEIN Pin des
    # 2x20-Stapelsteckers J2 (der laeuft ueber den eigenen Kettenstecker,
    # s. stack_spec.py-Kommentar bei STECKER_KETTE). Vorher stand hier
    # lokal, unreserviert GP8 (Pin 11) -- das kollidierte, sobald Befund 1
    # derselben Runde auch Pin 11 als freien GPIO zum Stapel durchreichte
    # (zwei Ausgaenge auf einem Netz, sobald ein Modul GP8 selbst nutzt).
    j3x, j3y = ox + 76.2, oy - 55.88
    sch.bauteil("J3", "Connector_Generic:Conn_01x02", (j3x, j3y),
                "Kettenstecker, Stift SMD (treibt SEL)", FP_HDR_1X02, rot=0,
                roff=(-5.08, 3.81), voff=(-5.08, 6.35))
    sch.netz("J3", "1", "L", "SEL_OUT")
    sch.netz("J3", "2", "L", "GND")

    # ---------------------------------------------------- J2 Stapelstecker
    # modulsockel._stapelstecker() -- Punkt 2 der Moduldoku oben:
    # derselbe Stecker wie bei jedem Modul, auch wenn die obere
    # Buchsenoeffnung hier nie bestueckt wird. frei_durchreichen=True,
    # NUR hier, NICHT bei einem Modul-J100 -- Befund 1 (Aufgabe-4-Fix-1):
    # der Sockel traegt den Pico direkt und muss jeden freien GPIO
    # tatsaechlich zum Stapel durchreichen, sonst erreicht ihn kein
    # Modul (der Stapelstecker leitet zwar mechanisch durch, aber ohne
    # einen Draht vom Pico dorthin haengt an dem Leiter nichts). Ein
    # Modul dagegen verdrahtet einen freien GPIO nur, wenn es ihn
    # tatsaechlich braucht -- s. modulsockel._stapelstecker()-Docstring
    # fuer die Begruendung dieser bewusst unterschiedlichen Behandlung.
    modulsockel._stapelstecker(sch, "J2", ox + 190.5, oy + 76.2,
                                frei_durchreichen=True)

    # ---------------------------------------------------- U1 Pico
    px, py = ox + 292.1, oy + 12.7
    sch.bauteil("U1", "MCU_Module:RaspberryPi_Pico", (px, py), "Raspberry Pi Pico",
                FP_PICO, rot=0, roff=(-22.86, -40.64), voff=(-22.86, -38.1))

    sch.netz("U1", "1", "L", "FLASH_TX")     # GP0
    sch.netz("U1", "2", "L", "FLASH_RX")     # GP1
    # Pin 3 ist die einzige SICHTBARE der acht GND-Pin-Nummern dieses
    # Symbols (3/8/13/18/23/28/38) -- 8/13/18/23/28/38 sind im
    # Symbol als "hidden"-Duplikate an EXAKT derselben Koordinate wie
    # Pin 3 hinterlegt (eigene Pruefung: `symlib.extract` +
    # `(hide yes)` im Rohblock jedes dieser sechs Pins). Ein einziger
    # Draht von Pin 3 aus deckt geometrisch auch die anderen sechs ab --
    # zusaetzliche netz()-Aufrufe fuer sie waeren exakt deckungsgleiche
    # Extra-Draehte, kein zusaetzlicher Anschluss.
    sch.netz("U1", "3", "D", "GND")          # GND (+ sechs versteckte Duplikate)
    # Pin 4 (GP2): SEL_OUT, s. Kommentar bei J3 oben -- treibt den
    # Kettenstecker direkt vom Pico aus, laeuft NICHT ueber J2.
    sch.netz("U1", "4", "L", "SEL_OUT")      # GP2 -- treibt J3
    sch.netz("U1", "5", "L", "FLASH_MODE")   # GP3
    sch.netz("U1", "6", "L", "I2C_SDA")      # GP4
    sch.netz("U1", "7", "L", "I2C_SCL")      # GP5
    sch.netz("U1", "9", "L", "NOTAUS")       # GP6
    sch.netz("U1", "10", "L", "SEL_CLK")     # GP7
    # GP8..GP22, GP26..GP28: alle "frei" (stack_spec.PIN_ROLLE) und seit
    # Befund 1 (Aufgabe-4-Fix-1) tatsaechlich zum Stapel durchgereicht --
    # an J2 unter demselben Netznamen (modulsockel._stapelstecker(...,
    # frei_durchreichen=True) oben). Vorher waren diese Pins hier nc,
    # obwohl stack_spec.py "freie GPIO" ausdruecklich als eine im ganzen
    # Stapel gleiche Netzart nennt (STECKER_STAPEL-Kommentar) -- kein
    # einziger freier GPIO erreichte je ein Modul. modulsockel.
    # PIN_GPIO_NAME ist die gemeinsame Quelle der Netznamen fuer U1 UND
    # J2, damit beide Seiten garantiert denselben Namen tragen. GP8
    # (Pin 11) war bis zu dieser Runde lokal der SEL-Treiber (s. J3-
    # Kommentar oben) -- jetzt wieder ein gewoehnlicher freier GPIO.
    for p in ("11", "12", "14", "15", "16", "17", "19", "20"):
        sch.netz("U1", p, "L", modulsockel.PIN_GPIO_NAME[int(p)])
    for p in ("21", "22", "24", "25", "26", "27", "29", "31", "32", "34"):
        sch.netz("U1", p, "R", modulsockel.PIN_GPIO_NAME[int(p)])
    # RUN (Pin 30) und ADC_VREF (Pin 35) bleiben BEWUSST nc, obwohl
    # stack_spec.PIN_ROLLE auch sie generisch als "frei" fuehrt (die
    # Voreinstellung fuer jeden nicht ausdruecklich zugewiesenen Pin,
    # unabhaengig davon, ob er ein GPIO ist) -- keiner von beiden ist
    # tatsaechlich ein GPIO. RUN ist der aktiv-LOW Reset-Eingang des
    # RP2040 mit eigenem ~50-kOhm-Pullup (Raspberry Pi Pico Datasheet,
    # Release 21, Abschnitt 2.1, S. 7: "To reset RP2040, short this pin
    # low.") -- ihn durch den Stapel zu reichen, gaebe jedem Modul die
    # Moeglichkeit, den Pico zurueckzusetzen. ADC_VREF ist eine aus 3V3
    # gefilterte Referenzspannung, kein digitales Signal. s.
    # modulsockel.PIN_GPIO_NAME-Kommentar fuer dieselbe Begruendung.
    sch.nc("U1", "30")                        # RUN -- Pico-eigener Pullup, unbenutzt
    # AGND (Pin 33) NICHT mit GND verdrahten, obwohl stack_spec.PIN_ROLLE
    # beide als "GND" fuehrt -- eine bewusste, dokumentierte Abweichung
    # vom Vertrag, kein Versehen: das Pico-Symbol markiert AGND ALS
    # EIGENEN "Power output"-Pin (eigene Pruefung: symlib-Pintyp
    # "power_out", eigene, von Pin 3 abweichende Koordinate -- kein
    # verstecktes Duplikat wie 8/13/18/23/28/38). Zwei "Power output"-
    # Pins auf demselben Netz meldet kicad-cli sch erc als FEHLER ("Pins
    # of type Power output and Power output are connected"), nicht nur
    # als Warnung. Laut Datenblatt (Raspberry Pi Pico Datasheet, Release
    # 21, Abschnitt 2.1 "Raspberry Pi Pico pinout", S. 7) ist AGND KEIN
    # interner Kurzschluss zu GND, sondern eine eigene analoge
    # Massenflaeche: "AGND is the ground reference for GPIO26-29, there
    # is a separate analog ground plane running under these signals and
    # terminating at this pin. If the ADC is not used or ADC performance
    # is not critical, this pin can be connected to digital ground."
    # Das Datenblatt nennt das Verbinden also ausdruecklich als Option
    # ("can be"), nicht als Vorgabe -- diese Platine verwendet keinen
    # ADC-Kanal (GP26..28 werden zwar seit Befund 1 zum Stapel
    # durchgereicht, s.o., aber von KEINEM Bauteil dieser Platine als
    # ADC-Eingang benutzt), braucht also keine analoge Masse-Referenz.
    # no_connect ist ehrlich (die Leitung bleibt tatsaechlich unbenutzt)
    # und vermeidet den ERC-Fehler, statt ihn nur zu unterdruecken.
    sch.nc("U1", "33")                        # AGND, unbenutzt (kein ADC-Kanal hier)
    sch.nc("U1", "35")                        # ADC_VREF, unbenutzt (kein ADC-Kanal hier)
    sch.netz("U1", "36", "U", "3V3")         # 3V3_OUT -- QUELLE der Stapel-3V3-Schiene
    sch.nc("U1", "37")                        # 3V3_EN -- Pico-eigener Pullup, unbenutzt
    # Pin 39 = VSYS: die kritischste Leitung dieses Schaltplans. +5V
    # (U2-Ausgang) MUSS hierhin, NIEMALS an Pin 36 (3V3_OUT) -- siehe
    # Moduldoku oben, Punkt 4, und tests/test_sockelplatine.py.
    sch.netz("U1", "39", "U", "+5V")         # VSYS
    sch.nc("U1", "40")                        # VBUS, unbenutzt (kein USB hier)

    # ------------------------------------------------- R1/R2 I2C-Abschluss
    # Nur hier auf dem Sockel, nicht auf Modulen (stack_spec/Aufgabenbrief).
    rx, ry = ox + 241.3, oy + 60.96
    sch.bauteil("R1", "Device:R", (rx, ry), R_I2C_WERT, FP_R0805, rot=0,
                roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R1", "1", "U", "3V3")
    sch.netz("R1", "2", "D", "I2C_SDA")
    sch.bauteil("R2", "Device:R", (rx + 15.24, ry), R_I2C_WERT, FP_R0805, rot=0,
                roff=(2.54, -1.27), voff=(2.54, 1.27))
    sch.netz("R2", "1", "U", "3V3")
    sch.netz("R2", "2", "D", "I2C_SCL")


# ------------------------------------------------------- Erzeugen
# Projektname, Titel, Datum und Zielpfad stehen hier als Konstanten und
# nicht mehr im __main__-Block: tests/test_erzeugte_dateien.py muss den
# Schaltplan mit GENAU denselben Angaben nachbauen koennen, um ihn gegen
# die eingecheckte Datei zu halten. Stuenden sie im __main__, muesste der
# Test sie abschreiben -- und zwei Kopien derselben Angabe laufen
# auseinander, ohne dass es jemand merkt. Genau daran ist die
# eingecheckte Datei schon einmal veraltet (s. Test).
PROJEKT = "Sockelplatine"
TITEL = "Sockelplatine"
DATUM = "2026-08-31"
ZIEL = os.path.join(HERE, "..", "..", "hardware", "kicad", "sockel",
                    "Sockelplatine.kicad_sch")


def erzeugen(ziel=None):
    """Baut den Schaltplan und schreibt ihn nach `ziel` (Vorgabe: ZIEL)."""
    import gen

    sch = gen.Schaltplan(PROJEKT, TITEL, DATUM)
    # Inhalt 343 x 160 mm ab x=-23/y=-56: mittig auf A3 statt an der
    # Blattecke angeschlagen (dort ragten Pico und Einspeisung ueber
    # den Rand). Raster 1,27 mm einhalten.
    bauen(sch, 60.96, 110.49)
    return sch.schreiben(ZIEL if ziel is None else ziel)


if __name__ == "__main__":
    print("keine unverbundenen Pins -- geschrieben:", erzeugen())

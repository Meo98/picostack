"""Der Vertrag von PicoStack: Steckerbelegung, Umriss, Modultypen.

Bewusst ohne KiCad-Abhaengigkeit, damit er ohne KiCad geprueft werden
kann -- und damit fremde Werkzeuge ihn lesen koennen, ohne KiCad zu
installieren.

Was hier steht, ist die Zusage an alle, die eigene Module bauen.
Aendert sich etwas davon, sind fremde Module unbrauchbar. Alles andere
im System darf sich aendern.

Grundlage: docs/superpowers/specs/2026-08-28-picostack-design.md
"""

BOARD_W = 64.0
BOARD_H = 60.0
CORNER_R = 3.0

PLATINE_DICKE = 1.6      # mm, Standard-PCB-Dicke (JLCPCB); auch Grundlage
# der Spaltrechnung unten und der Gehaeuse-Konstruktion (Aufgabe 9).

M3_DRILL = 3.2
M3_HOLES = [(4.0, 4.0), (4.0, 56.0), (60.0, 4.0), (60.0, 56.0)]

STAPEL_ABSTAND = 13.6     # mm zwischen zwei Platinen (Platinenoberkante
# zu Platinenoberkante). Vierte Runde, 2026-08-31 -- ersetzt 13,5 mm,
# das nur Stunden vorher 13,0 mm das seinerseits die urspruenglichen 15,0 mm ersetzt
# hatte. Herleitung, siehe hardware/bauteile-1b.md, Beleg 6 (zweite
# Runde), Beleg 13.5 und Beleg 14:
#
#   Spalt G = STAPEL_ABSTAND - PLATINE_DICKE = 13,6 - 1,6 = 12,00 mm
#   Kettenstecker  : Einstecktiefe = 17,00 - 12,00 = 5,00 mm (EINSTECKTIEFE_KETTE())
#   Leistungsstecker: dieselbe Rechnung             = 5,00 mm (EINSTECKTIEFE_LEISTUNG())
#   Stapelstecker  : Einstecktiefe = 19,36 - 12,00 = 7,36 mm (EINSTECKTIEFE_STAPEL())
#   Luft Stiftkoerper/Buchsenoberkante = 12,00 - 8,50 - 2,50
#                                                   = 1,00 mm (LUFT_STIFTKOERPER())
#
# WARUM AUSGERECHNET 13,6. Der Spalt G IST die Bauhoehe der Abstands-
# bolzen, die den Stapel mechanisch tragen -- und 11,90 mm gibt es
# nicht zu kaufen. Handelsuebliche M3-Bolzen kommen in 10/11/12/15 mm.
# 13,6 mm trifft mit G = 12,00 mm ein Katalogmass genau, bei 1,00 mm
# Luft statt 0,90 und einer Einstecktiefe, die nur 0,10 mm unter der
# von 13,5 liegt. Der Fehler war geerbt: auch 13,0 mm ergab mit
# 11,40 mm kein Katalogmass, es hat nur niemand nachgesehen, weil die
# Bolzen erst im Gehaeuse (Aufgabe 9) vorkommen -- dort waere es als
# Sonderanfertigung oder als Stapel aus Unterlegscheiben aufgefallen,
# lange nachdem die Platinen gefertigt sind.
#
# WARUM 13,5 UND NICHT 13,0. Die 0,40 mm Luft, die 13,0 mm liess, waren
# der engste Punkt des ganzen Stapels: der Isolierkoerper der SMD-
# Stiftleiste kann nicht in die Buchse eintauchen, er muss ueber deren
# Oberkante bleiben. Im unguenstigen Toleranzstapel (+-0,2 mm je
# Bauteil, +-10 % Platinendicke) faellt er auf null, und dann stossen
# die beiden Kunststoffe aneinander, BEVOR die Abstandsbolzen sitzen --
# die Platinen liessen sich nicht mehr flach verschrauben. Bei 13,5 mm
# sind es 0,90 mm; derselbe Toleranzstapel laesst davon noch etwa die
# Haelfte uebrig.
#
# WAS DAS KOSTET, vollstaendig aufgezaehlt (nur zwei Werte sinken,
# beide um genau 0,50 mm, beide bleiben weit ueber ihrer Reissleine):
#   Einstecktiefe SMD-Paar   5,60 -> 5,10 mm  (Reissleine 2,0 mm)
#   Einstecktiefe Stapel     7,96 -> 7,46 mm  (Reissleine 2,0 mm)
# Alles andere waechst:
#   Luft ueber der Buchse    0,40 -> 0,90 mm
#   Luft ueber der Klemme    1,30 -> 1,80 mm  (KLEMME_HOEHE_MM 10,10)
#   Luft ueber dem K7805     1,20 -> 1,70 mm  (K7805_HOEHE_MM 10,2)
#   Rest im Stapelstecker vor dem Anschlagen des Stifts am Buchsengrund
#     (Buchse 8,5 mm tief)   0,54 -> 1,04 mm
#   Rest der Steckstiftlaenge des SMD-Paars (Stift 6,0 mm frei)
#                            0,40 -> 0,90 mm
# In der Ebene aendert sich NICHTS: STECKER_POS, die Hoefe, die freien
# Flaechen und VERDREHT_MINDESTABSTAND_MM haengen nicht am Abstand.
#
# Der gueltige Bereich, in dem STAPEL_ABSTAND ueberhaupt liegen darf:
#   nach UNTEN begrenzt die Luft ueber der Buchse -- G >= 8,5 + 2,5 =
#     11,0 mm, also STAPEL_ABSTAND >= 12,6 mm. Das ist enger als die
#     Klemmen (G >= 10,10 mm, also >= 11,7 mm).
#   nach OBEN begrenzt die Einstecktiefe -- erst ab 16,6 mm faellt sie
#     unter die 2,0-mm-Reissleine des Tests.
# 13,5 mm liegt damit 0,9 mm ueber der unteren und 3,1 mm unter der
# oberen Grenze -- ungefaehr mittig, statt wie 13,0 mm dicht am Rand.
#
# Klemmenhoehe belegt (nicht geschaetzt) gegen genau diesen Spalt:
#   DB128L-5.08-2P/-3P (C395868/C395869): 10,10 mm -- Datenblatt DORABO
#     "DB128L-5.08-XXP-C-S" (Zeichnung datiert 2022.11.25, Bemassung
#     "10.10" in der Seitenansicht; ein Zeichnungssatz fuer alle
#     Polzahlen, Hoehe unabhaengig von XX). -> Rest ueber der Klemme:
#     11,90 - 10,10 = 1,80 mm.
#   K7805-2000R3 (C2931187), SIP-3, als hoechstes denkbares Bauteil
#     falls ein Modul es je verwendet: 10,2 mm -- Datenblatt DEXU
#     Electronics "K78xx-2000R3", Rev. A0-2018.12, S. 2 (Tabelle
#     "外观尺寸" / Aussenmasse), "长*宽*高 11.6*7.5*10.2mm". Rest:
#     11,90 - 10,2 = 1,70 mm.
# Siehe KLEMME_HOEHE_MM / K7805_HOEHE_MM unten fuer die maschinen-
# lesbaren Werte.
#
# ACHTUNG, zwei offene Punkte, die nicht in diesem Modul stehen koennen:
#   1. Das Gehaeuse (Aufgabe 9 dieser Etappe) wurde gegen den alten Wert
#      15,0 mm entworfen und muss auf 13,5 mm nachgezogen werden. Es
#      existiert in diesem Repo noch nicht -- die Aenderung kostet
#      deshalb heute nichts.
#   2. Der Spalt G IST die Bauhoehe der Abstandsbolzen: 11,90 mm ist
#      kein Katalogmass (ueblich sind 10, 11, 12, 15 mm). Das war schon
#      bei 13,0 mm so (11,40 mm) und wird hier nicht schlechter, aber
#      es bleibt zu entscheiden -- s. Bericht zu Aufgabe 5g, Bedenken 1.

# --- Steckerbelegung ------------------------------------------------
# Pico-Pins 1..40. Die Nummern folgen dem Pico-Datenblatt, nicht der
# GPIO-Nummer: der Stecker traegt Pins, nicht GPIO.
#
# Dieser 2x20-Stecker ist seit 2026-08-31 der Stapelstecker (Buchse mit
# durchgehendem Stift, STECKER_STAPEL unten) -- passend fuer alle
# Leitungen, die im ganzen Stapel dasselbe Netz sind (Bus- und
# Global-Signale, Versorgung, freie GPIO). Nur die Auswahlkette (SEL)
# muss von Modul zu Modul aufgetrennt werden (Schieberegister,
# tools/kette.py) und laeuft deshalb NICHT mehr ueber diesen Stecker,
# sondern ueber einen eigenen, zweipoligen STECKER_KETTE mit normaler
# Buchse/Stiftleiste. SEL ist deshalb kein Pin dieses Steckers mehr.
RESERVIERT = (
    "I2C_SDA", "I2C_SCL",     # Bus zu den Modulen
    "FLASH_TX", "FLASH_RX",   # Bootlader der Modul-MCU
    "SEL_CLK",                # global: Takt der Auswahlkette. Jedes
                              # Modul haelt die Auswahl in einem
                              # D-Flipflop; ein Takt schiebt sie eine
                              # Position tiefer (tools/kette.py).
    "FLASH_MODE",             # global: Stapel im Flash-Modus
    "NOTAUS",                 # global, wired-OR, wirkt ohne Software
    "SEL_OUT",                # der Pico-Pin, der die Auswahlkette treibt
                              # (Pin 4 / GP2). KEIN Pin des 2x20-Stapel-
                              # steckers -- laeuft ausserhalb davon auf
                              # STECKER_KETTE (s. Kommentar dort). Bis
                              # 2026-08-31 (Aufgabe-4-Fix-1-Runde) stand
                              # dafuer lokal, unreserviert Pin 11 (GP8)
                              # auf der Sockelplatine; das kollidierte,
                              # sobald Befund 1 derselben Runde jeden
                              # freien GPIO -- auch Pin 11 -- zum Stapel
                              # durchreichte (zwei Ausgaenge auf einem
                              # Netz, sobald ein Modul GP8 selbst nutzt).
                              # Pin 4 (GP2) war vor der Steckertrennung
                              # bereits SEL und bekommt die Rolle jetzt
                              # zurueck, s. Kommentar bei PIN_ROLLE[4]
                              # unten und .superpowers/sdd/
                              # 2026-08-31-etappe-1b-sockel-und-motormodul/
                              # aufgabe-4-fix1-report.md.
)

_GND = {3, 8, 13, 18, 23, 28, 33, 38}
_VERSORGUNG = _GND | {36, 37, 39, 40}    # 3V3_OUT, 3V3_EN, VSYS, VBUS


def IST_VERSORGUNG(pin):
    return pin in _VERSORGUNG


# Pins, die eine Rolle TRAGEN, aber trotzdem nicht benutzbar sind.
#
# Warum es diesen Eintrag gibt (2026-09-01, Aufgabe 6, beim Lesen der
# Netzliste gefunden). PIN_ROLLE gab bis dahin drei Pins einen
# Versorgungsnamen -- 37 "3V3_EN", 39 "VSYS", 40 "VBUS" --, und
# IST_VERSORGUNG() bestaetigte das. Getrieben hat sie NIEMAND: der
# Generator legte sie auf jeder Platine auf no_connect, Sockelseite wie
# Modulseite. Auf dem Sockel gibt es sogar eine 5-V-Schiene (der K7805
# speist damit U1 Pin 39), sie erreicht den Stapelstecker nur nicht.
# Wer sich auf den Vertrag verliess, haelt drei Pins fuer belegt, an
# denen nichts liegt.
#
# Das ist genau die Luecke, die der Vertrag fuer Pin 30 und 35 schon
# selbst benennt ("ein Modulautor, der sich auf PIN_ROLLE verlaesst,
# haelt einen Pin fuer benutzbar, der es nicht ist"). Bei diesen dreien
# stand nirgends etwas; sie sassen bloss im selben elif-Zweig von
# tools/sch/modulsockel.py wie 30 und 35. Die Liste stand damit im
# GENERATOR und nicht im Vertrag -- dieselbe Trennung, die dieses
# Projekt sonst ueberall aufloest.
#
# RULING (2026-09-01): Der Vertrag wird ehrlich gemacht, es wird KEINE
# 5-V-Schiene verteilt.
#   Fuer das Verteilen spraeche: der K7805 kann 2 A, die Schiene
#   existiert auf dem Sockel bereits, eine Bahn zu J2 Pin 39 waere
#   billig.
#   Dagegen spricht dreierlei. (1) Es gibt heute keinen Verbraucher:
#   das Motormodul zieht 24 V aus dem Leistungsstecker und 3V3 aus
#   Pin 36. Eine Schiene ohne Verbraucher ist eine Zusage, die nie
#   erprobt wird. (2) VSYS ist am Pico ein EINGANG. Sobald der Sockel
#   ihn treibt, muss der Vertrag zusaetzlich regeln, dass kein Modul
#   ihn ebenfalls speisen darf -- sonst stehen zwei Quellen auf einem
#   Netz. Diese Regel gaebe es dann nur, weil die Schiene existiert.
#   (3) Die Entscheidung laesst sich spaeter mit einem echten Bedarf
#   im Ruecken treffen; heute waere sie geraten.
# Kosten wenn falsch: eine Bahn auf dem Sockel und eine Vertragszeile,
# solange keine Platine gefertigt ist. Genau deshalb wird sie
# aufgeschoben und nicht vorweggenommen.
NICHT_BELEGBAR = {
    30: "RUN -- Reset des RP2040, aktiv-LOW mit eigenem Pullup "
        "(Pico Datasheet Rel. 21, Abschnitt 2.1). Ein Modul, das ihn "
        "treibt, setzt den Pico zurueck.",
    35: "ADC_VREF -- analoge Referenzspannung des ADC, kein "
        "Digitalanschluss.",
    37: "3V3_EN -- schaltet den internen Regler des Pico ab. Nach "
        "aussen gefuehrt waere das ein Ausschalter fuer den ganzen "
        "Stapel, den jedes Modul versehentlich ziehen koennte.",
    39: "VSYS -- Versorgungs-EINGANG des Pico. Der Sockel treibt ihn "
        "heute nicht (s. Ruling oben); ein Modul darf ihn nicht "
        "speisen, solange das nicht geregelt ist.",
    40: "VBUS -- liegt nur an, wenn am Pico ein USB-Kabel steckt. Eine "
        "Schiene, die von einem Zufall abhaengt, ist keine Zusage.",
}


def IST_BELEGBAR(pin):
    """Darf ein Modul diesen Pin benutzen?

    Die Frage, die ein Modulautor wirklich stellt -- PIN_ROLLE allein
    beantwortet sie nicht, weil dort auch Namen stehen, hinter denen
    nichts liegt.
    """
    return pin not in NICHT_BELEGBAR


PIN_ROLLE = {}
for _p in range(1, 41):
    PIN_ROLLE[_p] = "GND" if _p in _GND else "frei"
PIN_ROLLE.update({
    36: "3V3", 37: "3V3_EN", 39: "VSYS", 40: "VBUS",
    1:  "FLASH_TX",     # GP0
    2:  "FLASH_RX",     # GP1
    # 4 (GP2) war SEL, dann (Etappe 1b, erste Runde) kurz wieder frei --
    # SEL laeuft seit der Steckertrennung ueber STECKER_KETTE, nicht
    # mehr ueber den 2x20-Stapelstecker. "Frei" war dabei nur halb
    # richtig: die vorige Runde liess den Pin zwar ungenutzt am 2x20-
    # Stecker, verdrahtete ihn dann aber lokal auf der Sockelplatine
    # unreserviert an Pin 11 (GP8) als SEL-Treiber -- eine stille
    # Kollision, sobald ein Modul GP8 selbst braucht (Aufgabe-4-Fix-1-
    # Runde, Befund 2). Pin 4 (GP2) traegt die Rolle deshalb jetzt
    # wieder als echte Vertragsrolle SEL_OUT (s. RESERVIERT oben):
    # treibt STECKER_KETTE direkt vom Pico aus, weiterhin KEIN Pin
    # dieses 2x20-Steckers.
    4:  "SEL_OUT",      # GP2
    5:  "FLASH_MODE",   # GP3
    6:  "I2C_SDA",      # GP4
    7:  "I2C_SCL",      # GP5
    9:  "NOTAUS",       # GP6
    10: "SEL_CLK",      # GP7
    # Pin 30 (RUN) und 35 (ADC_VREF) sind KEINE GPIO, obwohl die
    # Voreinstellung oben sie mangels eigener Rolle als "frei" fuehrte.
    # Das ist dieselbe Luecke wie bei Pin 4 (Befund 2 der Aufgabe-4-Fix-1-
    # Runde), nur eine Stufe weiter: ein Modulautor, der sich auf
    # PIN_ROLLE verlaesst, haelt einen Pin fuer benutzbar, der es nicht
    # ist. RUN ist der Reset des RP2040, aktiv-LOW mit eigenem Pullup
    # (Pico Datasheet Release 21, Abschnitt 2.1, S. 7) -- ein Modul, das
    # ihn als GPIO treibt, setzt den Pico zurueck. ADC_VREF ist die
    # analoge Referenz, kein Digitalanschluss. Beide bleiben deshalb vom
    # Stapelstecker getrennt (s. _stapelstecker in tools/sch/modulsockel.py).
    30: "RUN",
    35: "ADC_VREF",
})

# --- Die drei Steckverbinder -----------------------------------------
# Drei Stecker, zwei Bauprinzipien. Der Unterschied ist keine
# Geschmacksfrage, sondern folgt aus genau einer Frage: fuehren die
# Haelfte OBEN und die Haelfte UNTEN dasselbe Netz?
#
#   ja   -> EIN durchgehender Stapelstecker (Buchse oben und langer
#           Stift unten sind derselbe Leiter, ein einziges Bauteil).
#           So der 2x20-Signalstecker: alle 40 Leitungen sind im ganzen
#           Stapel dasselbe Netz.
#   nein -> ZWEI getrennte Haelften, die trotzdem am SELBEN Ort sitzen
#           muessen. So der Kettenstecker: SEL kommt von oben als
#           SEL_IN herein und geht nach unten als SEL_OUT weiter.
#
# WARUM BEIDE HAELFTEN AM SELBEN ORT SITZEN MUESSEN. Alle Platinen des
# Stapels sind gleich. Der Stift an der Unterseite von Modul N trifft
# die Buchse an der Oberseite von Modul N+1 nur, wenn beide dieselbe
# (x|y) haben: zwischen zwei GLEICHEN Platinen hebt sich eine
# Verschiebung nicht auf, sie summiert sich (eine Verschiebung hat
# keinen Fixpunkt). Deshalb steht in STECKER_POS unten je EINE Flaeche
# pro Stecker, nicht zwei.
#
# WARUM DIE KETTE KEIN DURCHGEHENDER STIFT SEIN DARF -- nachgerechnet,
# nicht behauptet: bei durchgehenden Kontakten ist Kontakt k EIN Netz
# ueber den ganzen Stapel. Alle Module sind gleich und verbinden also
# denselben Modulknoten mit demselben Kontakt. Laege SEL_OUT auf
# Kontakt a und SEL_IN auf Kontakt b, verlangte die Kette
# SEL_OUT(n) = SEL_IN(n+1) fuer JEDES n -- das geht nur, wenn Netz(a)
# und Netz(b) dasselbe Netz sind, und dann liegen ALLE SEL_IN und ALLE
# SEL_OUT des Stapels auf einem einzigen Knoten: D und Q jedes
# Flipflops kurzgeschlossen, das Schieberegister aus tools/kette.py
# waere sinnlos. Das gilt unabhaengig von der Kontaktzahl -- auch zwei
# oder zwanzig Kontakte des 2x20-Stapelsteckers koennen die Kette
# nicht tragen. Genau deshalb hat sie einen eigenen Stecker.
#
# ZWEI GETRENNTE HAELFTEN AM SELBEN ORT GEHEN NUR OBERFLAECHENMONTIERT.
# Zwei BEDRAHTETE Bauteile am selben Ort brauchten dieselben
# Bohrungen; dieselbe Bohrung ist aber derselbe Leiter, also wieder ein
# durchgehender Kontakt -- und der ist fuer die Kette gerade verboten.
# Die Mischung geht auch nicht: die Bohrungen der bedrahteten Haelfte
# liegen genau dort, wo die Kontakte der SMD-Haelfte auf der Gegenseite
# liegen muessten. Es bleibt: BEIDE Haelften SMD, Buchse oben,
# Stiftleiste unten, auf demselben Kontaktraster, ohne Durch-
# kontaktierung dazwischen.
#
# Bis zum 2026-08-31 (Aufgabe 5e) trugen Ketten- UND Leistungsstecker
# zwei BEDRAHTETE Haelften am selben Ort -- so nicht baubar. Der Fehler
# ist hier behoben; tests/test_stack_spec.py haelt die Regel seither
# fest ("kein Steckerpaar mit zwei bedrahteten Haelften").
#
# Die Felder "durchgehend", "montage_oben" und "montage_unten" sind
# genau dafuer da: sie machen die Bauart maschinenlesbar, statt sie nur
# in "typ" zu erzaehlen.

STECKER_STAPEL = {
    "typ": "Buchse mit durchgehendem Stift (Stapelstecker), 2x20, 2,54 mm",
    "durchgehend": True,           # EIN Bauteil, Buchse und Stift sind
                                   # derselbe Leiter -> beide Seiten
                                   # zwangslaeufig dasselbe Netz.
    "montage_oben": "THT",
    "montage_unten": "THT",
    "haelften_gleiche_netze": True,
    "buchse_lcsc": "C35165",       # BOOMELE "2.54-2*20PPC104"
    "stift_lcsc": "C35165",        # dasselbe Bauteil
    "buchse_mpn": "BOOMELE 2.54-2*20PPC104",
    "stift_mpn": "BOOMELE 2.54-2*20PPC104",
    "strom_pro_kontakt_a": 3.0,    # LCSC-Produktseite C35165,
                                   # "Current Rating: 3A"
    "gehaeusehoehe_mm": 8.5,       # Datenblatt, Masszeichnung "8.5+-0.2"
    "stiftlaenge_unter_gehaeuse_mm": 12.46,  # Datenblatt, "12.46+-0.2"
    "quelle": "hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31)",
}

# --- Die beiden kleinen Stecker: SMD-Paare ---------------------------
# Beide bestehen aus zwei Bauteilen am SELBEN Ort, beide oberflaechen-
# montiert (Begruendung im Block oben). Die Masse:
#
#   F = Isolationshoehe der Buchse ueber ihrer Platine        = 8,50 mm
#   M = Isolierkoerper des Stifts + freie Steckstiftlaenge
#       = 2,50 + 6,00                                        = 8,50 mm
#     (SMD: nichts geht in der Platine verloren -- anders als beim
#      bedrahteten Stift, dessen Loetschwanz 3,0 mm kostet, und anders
#      als beim Stapelstecker, dessen Stift erst durch die eigene
#      Platine muss.)
#   G = STAPEL_ABSTAND - PLATINE_DICKE                       = 11,90 mm
#
#   Einstecktiefe   = (M + F) - G = 17,00 - 11,90 = 5,10 mm
#   Luft ueber der Buchse (Stift-Isolierkoerper gegen Buchsenoberkante)
#                   = G - F - Isolierkoerper = 11,90 - 8,50 - 2,50
#                   = 0,90 mm
#
# Die 5,10 mm sind immer noch deutlich mehr als die 3,1 mm, die das
# alte bedrahtete Paar hatte -- weil der Loetschwanz wegfaellt. Die
# 0,90 mm sind das Ergebnis der Aufgabe 5g: bei STAPEL_ABSTAND = 13,0 mm
# waren es nur 0,40 mm, und die konnten im unguenstigen Toleranzstapel
# (+-0,2 mm je Bauteil, +-10 % Platinendicke) auf null fallen -- dann
# stossen die beiden Isolierkoerper aneinander, bevor die Abstands-
# bolzen sitzen. Deshalb ist STAPEL_ABSTAND auf 13,5 mm gestiegen
# (Herleitung im Block dort). LUFT_STIFTKOERPER() rechnet den Wert
# nach, der Test haelt ihn > 0.
#
# Bauteilbelege: alle vier Steckerhaelften haben seit Aufgabe 5g
# (2026-08-31) eine LCSC-Nummer von einer tatsaechlich geoeffneten
# Produktseite -- Einzelheiten in hardware/bauteile-1b.md, Beleg 14.
# Damit sind beide Platinen bestueckt bestellbar; alle vier Teile sind
# ausserdem in der JLCPCB-Bestueckungsbibliothek gefuehrt (Abfrage der
# JLCPCB-SMT-Bauteilsuche, componentLibraryType "expand" = Extended
# Part, allowPostFlag true).
#
#   Buchse 1x2 (Kette)    C46635838  hanxia "HX PM2.54-1x2P TP H8.5-YQ"
#     "Mounting Type: Surface Mount, Vertical", "Holes Structure: 1x2P",
#     "Insulation Height: 8.5mm", "Current Rating: 3A", Messing
#     vergoldet, "Packaging: SMD, P=2.54mm (Staggered Pins)".
#   Stift  1x2 (Kette)    C41417359  hanxia "HX PZ2.54-1x2P TP-YQ"
#     "Mounting Type: Surface Mount, Vertical", "Pin Structure: 1x2P",
#     "Insulation Height: 2.5mm", "Length of Mating Pin: 6mm",
#     "Current Rating: 3A", Messing vergoldet.
#   Buchse 2x2 (Leistung) C3975147   HCTL "PM254-2-02-S-8.5"
#     "Mounting Type: Surface Mount, Vertical", "Holes Structure: 2x2P",
#     "Row Spacing: 2.54mm", "Insulation Height: 8.5mm",
#     "Current Rating: 3A", Kupferlegierung.
#   Stift  2x2 (Leistung) C919361    BOOMELE "2.54-2*2P"
#     "Mounting Type: Surface Mount, Vertical", "Pin Structure: 2x2P",
#     "Insulation Height: 2.5mm", "Length of Mating Pin: 6mm",
#     "Current Rating: 3A".
#
# Alle vier bestaetigen genau die drei Masse, mit denen dieser Vertrag
# rechnet (8,50 / 2,50 / 6,00 mm) -- die Geometrie oben ist damit nicht
# mehr nur an einer Bauform belegt, sondern an den wirklich bestellten
# Teilen.
#
# Belegte Ersatztypen, falls einer ausgeht (dieselbe Bauform, dieselben
# Masse, ebenfalls Produktseiten gesehen):
#   Buchse 1x2: C55218893 (SHOU HAN "PM2.54-1x2PLT-H8.5-R", 8,5 mm, 3 A)
#               und C48641753 (hanxia "HX PM2.54-1x2P TP H8.5-ZQ").
#   Buchse 2x2: kein zweiter Typ mit geoeffneter Produktseite. Die
#               JLCPCB-Bauteilsuche zeigt zwar weitere 2x2-Buchsen in
#               "立贴" (SMD senkrecht) mit 8,5 mm, deren Produktseiten
#               sind aber NICHT geoeffnet worden -- sie stehen deshalb
#               hier bewusst nicht mit Nummer.
#   Stift 2x2:  C192300 (BOOMELE 2.54-2*4P, 2x4) belegt dieselbe
#               Bauform in anderer Polzahl.
BUCHSE_SMD_HOEHE_MM = 8.5      # LCSC C46635838/C3975147, "Insulation
                               # Height: 8.5mm"
STIFT_SMD_KOERPER_MM = 2.5     # LCSC C41417359/C919361, "Insulation
                               # Height: 2.5mm"
STIFT_SMD_STECKLAENGE_MM = 6.0  # LCSC C41417359/C919361, "Length of
                               # Mating Pin: 6mm"

STECKER_KETTE = {
    "typ": "SMD-Buchse oben / SMD-Stiftleiste unten (auftrennbar), "
           "1x2, 2,54 mm",
    "zweck": "traegt SEL (Auswahlkette) und eine GND daneben",
    "durchgehend": False,          # zwei Bauteile am selben Ort
    "montage_oben": "SMD",
    "montage_unten": "SMD",
    "haelften_gleiche_netze": False,   # oben SEL_IN, unten SEL_OUT
    "buchse_lcsc": "C46635838",    # hanxia "HX PM2.54-1x2P TP H8.5-YQ",
                                   # SMD senkrecht, 1x2, Isolations-
                                   # hoehe 8,5 mm, 3 A, Messing
                                   # vergoldet -- Produktseite gesehen
                                   # (2026-08-31), s. Block oben
    "buchse_spec": "Buchsenleiste 1x2, 2,54 mm, SMD senkrecht, "
                   "Isolationshoehe 8,5 mm, >= 1 A",
    "stift_lcsc": "C41417359",     # hanxia "HX PZ2.54-1x2P TP-YQ",
                                   # SMD senkrecht, 1x2, Isolier-
                                   # koerper 2,5 mm, Steckstift 6,0 mm,
                                   # 3 A -- Produktseite gesehen
    "stift_spec": "Stiftleiste 1x2, 2,54 mm, SMD senkrecht, "
                  "Isolierkoerper <= 2,5 mm, Steckstift 6,0 mm",
    "buchse_mpn": "hanxia HX PM2.54-1x2P TP H8.5-YQ",
    "stift_mpn": "hanxia HX PZ2.54-1x2P TP-YQ",
    "pins": {1: "SEL", 2: "GND"},
    "buchsenhoehe_mm": BUCHSE_SMD_HOEHE_MM,
    "stiftkoerper_mm": STIFT_SMD_KOERPER_MM,
    "stiftlaenge_mm": STIFT_SMD_STECKLAENGE_MM,
    "quelle": "hardware/bauteile-1b.md, Beleg 13 und 14 (2026-08-31)",
}

# Der Leistungsstecker stand bisher nur in hardware/bauteile-1b.md
# (Beleg 4) und in STECKER_POS -- seine Bauart war damit nirgends
# maschinenlesbar, und genau deshalb ist der Konstruktionsfehler dort
# so lange unbemerkt geblieben. Jetzt steht er im Vertrag.
#
# WARUM ER KEIN 2x2-STAPELSTECKER IST, obwohl seine beiden Haelften
# Pin fuer Pin dasselbe Netz fuehren und ein durchgehender Stift hier
# also erlaubt WAERE: es gibt keinen. Gesucht wurde bei LCSC/JLCPCB
# (Belege in hardware/bauteile-1b.md, Beleg 13); die Stapelstecker-
# Reihe hat dort nur 2x20 (C35165, C5307344) und 2x40 (C5307345). Das
# naechstliegende "langbeinige" Teil, C72555 (BOOMELE 2.54-2*8P3.8,
# "Heightened, Pins are long 3.8mm"), ueberbrueckt den Spalt nicht
# einmal: M = 3,8 - 1,6 = 2,2 mm, M + F = 2,2 + 8,5 = 10,7 mm < G =
# 11,9 mm (und lag auch bei den frueheren 11,4 mm darunter).
#
# Und warum die Leistung nicht ueber Kontakte des vorhandenen
# 2x20-Stapelsteckers laeuft: dort ist kein Kontakt frei. Alle 40
# tragen Pico-Pins (PIN_ROLLE oben), und die Sockelplatine verbindet
# sie mit dem Pico -- 24 V auf einem davon zerstoert ihn. Elektrisch
# tot sind allein die Kontakte 30 (RUN) und 35 (ADC_VREF), die kein
# Modul anfassen darf; das waere EIN Pfad fuer 24 V mit 3 A
# (C35165-Produktseite) direkt neben 3,3-V-GPIO im 2,54-mm-Raster --
# unter dem Bedarf des Motormoduls (DRV8876 ueber 2,5 A) und gegen die
# ausdrueckliche Vorgabe des Design-Dokuments, Motorstroeme vom
# Signalstecker getrennt zu fuehren.
STECKER_LEISTUNG = {
    "typ": "SMD-Buchse oben / SMD-Stiftleiste unten, 2x2, 2,54 mm",
    "zweck": "24 V und GND in den Stapel, je zwei Kontakte parallel",
    "durchgehend": False,          # zwei Bauteile am selben Ort
    "montage_oben": "SMD",
    "montage_unten": "SMD",
    "haelften_gleiche_netze": True,    # oben wie unten PWR24V/GND
    "buchse_lcsc": "C3975147",     # HCTL "PM254-2-02-S-8.5", SMD
                                   # senkrecht, 2x2, Reihenabstand
                                   # 2,54 mm, Isolationshoehe 8,5 mm,
                                   # 3 A, Kupferlegierung --
                                   # Produktseite gesehen (2026-08-31)
    "buchse_spec": "Buchsenleiste 2x2, 2,54 mm, SMD senkrecht, "
                   "Isolationshoehe 8,5 mm, >= 2,5 A je Kontakt",
    "stift_lcsc": "C919361",       # BOOMELE "2.54-2*2P", SMD
                                   # senkrecht, 2,5 mm Isolierkoerper,
                                   # 6,0 mm Steckstift, 3 A, gesehen
                                   # auf der LCSC-Produktseite
    "stift_spec": "Stiftleiste 2x2, 2,54 mm, SMD senkrecht, "
                  "Isolierkoerper <= 2,5 mm, Steckstift 6,0 mm",
    "buchse_mpn": "HCTL PM254-2-02-S-8.5",
    "stift_mpn": "BOOMELE 2.54-2*2P",
    "pins": {1: "PWR24V", 2: "GND", 3: "PWR24V", 4: "GND"},
    "buchsenhoehe_mm": BUCHSE_SMD_HOEHE_MM,
    "stiftkoerper_mm": STIFT_SMD_KOERPER_MM,
    "stiftlaenge_mm": STIFT_SMD_STECKLAENGE_MM,
    # Beide Haelften tragen 3 A je Kontakt: Buchse C3975147 ("Current
    # Rating: 3A") und Stift C919361 ("Current Rating: 3A"). Bis
    # Aufgabe 5g stand hier 2,5 A -- das war der Wert der damals
    # ersatzweise herangezogenen 2x5-Buchse C261072, nicht der eines
    # Teils in der gebrauchten Polzahl. Seit die 2x2-Buchse belegt ist,
    # ist der Engpass verschwunden.
    # Zwei Kontakte je Ader ergeben rechnerisch 6,0 A vor Derating --
    # dieselbe Vorsicht wie in hardware/bauteile-1b.md, Beleg 4: eine
    # Parallel-Summe von Einzelkontakt-Nennwerten, keine Hersteller-
    # aussage ueber den Parallelbetrieb bei ungleichen Kontakt-
    # widerstaenden. Der DRV8876 des Motormoduls zieht ueber 2,5 A; EIN
    # Motormodul passt damit mit Faktor 2,4, mehrere gleichzeitig unter
    # Volllast weiterhin nicht.
    "strom_pro_kontakt_a": 3.0,
    "kontakte_je_ader": 2,
    "quelle": "hardware/bauteile-1b.md, Beleg 4, 13 und 14",
}


def EINSTECKTIEFE_STAPEL():
    """Rechnerische Einstecktiefe des Stapelsteckers bei STAPEL_ABSTAND.

    M+F ueberbruecken den Spalt G = STAPEL_ABSTAND - PLATINE_DICKE; der
    Stift von Modul A fuehrt zuerst durch dessen eigene Platine (M wird
    dadurch um PLATINE_DICKE kuerzer), siehe hardware/bauteile-1b.md,
    Beleg 1, Nachtrag.
    """
    g = STAPEL_ABSTAND - PLATINE_DICKE
    m = STECKER_STAPEL["stiftlaenge_unter_gehaeuse_mm"] - PLATINE_DICKE
    f = STECKER_STAPEL["gehaeusehoehe_mm"]
    return (m + f) - g


def EINSTECKTIEFE_SMD_PAAR(stecker):
    """Einstecktiefe eines SMD-Paars (Buchse oben, Stiftleiste unten).

    Der Stift sitzt AUF der Unterseite, nicht in ihr: seine wirksame
    Laenge unter der Platine ist Isolierkoerper + Steckstift, ohne
    Abzug fuer die Platine und ohne Loetschwanz.
    """
    g = STAPEL_ABSTAND - PLATINE_DICKE
    m = stecker["stiftkoerper_mm"] + stecker["stiftlaenge_mm"]
    f = stecker["buchsenhoehe_mm"]
    return (m + f) - g


def LUFT_STIFTKOERPER(stecker):
    """Luft zwischen Stift-Isolierkoerper und Buchsenoberkante.

    Der Isolierkoerper des Stifts kann nicht in die Buchse eintauchen;
    er muss ueber deren Oberkante bleiben, sonst stossen die beiden
    Kunststoffe aneinander, bevor die Abstandsbolzen die Platinen auf
    Abstand gebracht haben. Muss > 0 sein.
    """
    g = STAPEL_ABSTAND - PLATINE_DICKE
    return g - stecker["buchsenhoehe_mm"] - stecker["stiftkoerper_mm"]


def EINSTECKTIEFE_KETTE():
    """Rechnerische Einstecktiefe des Kettensteckers bei STAPEL_ABSTAND."""
    return EINSTECKTIEFE_SMD_PAAR(STECKER_KETTE)


def EINSTECKTIEFE_LEISTUNG():
    """Rechnerische Einstecktiefe des Leistungssteckers."""
    return EINSTECKTIEFE_SMD_PAAR(STECKER_LEISTUNG)



# --- Wo die Stecker auf der Platine sitzen ---------------------------
# Bis hierher legte der Vertrag fest, WELCHE Rolle auf welchem Pin
# liegt und WIE HOCH die Stecker bauen -- aber nirgends, WO sie sitzen.
# Zwei unabhaengig entstehende Layouts (Sockel, Motormodul) passen
# damit nicht zusammen, ein fremdes Modul erst recht nicht. Deshalb
# gehoert die Lage hierher und nicht in die einzelnen
# Platinenbeschreibungen: es gibt EINE Koordinatenmenge fuer ALLE
# Platinen des Stapels. Der Stapelstecker der Sockelplatine steht
# senkrecht ueber dem jedes Moduls, Ketten- und Leistungsstecker
# ebenso -- sonst steckt der Stapel mechanisch nicht.
#
# Koordinatensystem: mm, Ursprung linke obere Ecke der Platine, x nach
# rechts, y nach unten (KiCad-Konvention). Dasselbe System wie
# M3_HOLES oben.
#
# Nur die Lage des Pico (PICO_POS) gilt ausschliesslich fuer die
# Sockelplatine -- er ist das einzige Bauteil, das genau eine Platine
# im Stapel traegt. Er steht trotzdem hier und nicht in
# tools/pcb/spec_sockel.py, weil sein Antennen-Sperrbereich
# (ANTENNE_SPERRBEREICH) gegen dieselben Stecker geprueft werden muss.

M3_KEEPOUT = 7.0   # mm Durchmesser Freihaltebereich um jede M3-Bohrung.
# Nicht der Bohrdurchmesser (M3_DRILL = 3,2 mm), sondern der Platz fuer
# Schraubenkopf/Unterlegscheibe und den Abstandsbolzen. Uebernommen aus
# der gebauten Platine des Vorlaeuferprojekts
# (PecheAuxCanards/tools/pcb/spec.py, M3_KEEPOUT = 7.0); dort gegen
# echte M3-Bolzen erprobt. tools/pcb/geometry.py liest den Wert ueber
# getattr aus der Platinenbeschreibung und faellt sonst auf dieselbe
# 7,0 zurueck -- hier steht er, damit beide PicoStack-Platinen ihn aus
# EINER Quelle bekommen.

# Hoefe (F.CrtYd) der Footprints, jeweils (x0, y0, x1, y1) relativ zur
# Mitte von KONTAKT 1 -- also zu der Achse, in die der Stift eines
# Nachbarmoduls faehrt, nicht zu einem Loetpad. Bei den bedrahteten
# Footprints ist das dasselbe (Pad 1 sitzt auf der Steckachse); bei den
# SMD-Footprints NICHT: dort liegen die Loetpads seitlich neben den
# Stiften. Der Bezug auf den Kontakt ist der richtige, weil genau er im
# Stapel zusammenpassen muss.
# GEMESSEN, nicht geschaetzt: aus den echten .kicad_mod-Dateien der
# KiCad-Standardbibliothek (kicad-footprints, nixpkgs-Ableitung
# a2d01395d2, gelesen mit KiCad 10.0.5), aufgeloest ueber
# tools/pcb/kicadlibs.py. Als Konstanten hier eingetragen und nicht per
# Aufruf geholt, damit der Vertrag ohne KiCad lesbar bleibt.
#
# Die SMD-Werte sind zusaetzlich SYMMETRIERT: das kleinste Rechteck um
# das Kontaktfeld herum, das den Hof enthaelt. Grund: die Buchse wird
# im Layout gespiegelt platziert (sie sitzt oben und muss zum Stift der
# Platine darueber passen, dessen Footprint auf der Unterseite liegt).
# Ohne Symmetrierung haenge der Vertragswert davon ab, welche
# Spiegelung das Layout waehlt -- das waere genau die Art stiller
# Abhaengigkeit, die dieser Vertrag verhindern soll. Die Symmetrierung
# kostet hoechstens 0,05 mm (KiCad zeichnet den Buchsenhof leicht
# unsymmetrisch: -4,50 gegen +4,55).
#
# ACHTUNG, das bleibt der wunde Punkt dieser Masse: alle fuenf
# Header-Footprints sind PLATZHALTER aus der Standardbibliothek
# (dieselben, die tools/sch/modulsockel.py eintraegt). Die wirklichen
# Bauteile -- der PC104-Stapelstecker C35165 und die SMD-Paare aus
# STECKER_KETTE/STECKER_LEISTUNG -- brauchen eigene .kicad_mod. Deren
# Isolierkoerper und Pads koennen groesser sein.
# tests/test_stack_spec.py prueft deshalb, dass die hier genannten
# Footprint-Namen noch dieselben sind wie in modulsockel.py: wer sie
# gegen die echten austauscht, faellt in den roten Test und muss die
# Lage neu nachrechnen, statt sie stillschweigend zu erben.
FOOTPRINT_HOF = {
    # bedrahtet: Kontakt 1 == Pad 1
    "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical":
        (-1.77, -1.78, 4.32, 50.03),     # 6,09 x 51,81 mm
    # SMD-Paar Kettenstecker (1x2). Kontakt 1 liegt im Footprint bei
    # (0 | -1,27), die Pads bei (-1,655 | -1,27) und (1,655 | 1,27).
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left":
        (-3.41, -1.77, 3.41, 4.31),      # 6,82 x 6,08 mm
    "Connector_PinSocket_2.54mm:PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left":
        (-3.10, -1.88, 3.10, 4.42),      # 6,20 x 6,30 mm
    # SMD-Paar Leistungsstecker (2x2). Kontakt 1 liegt im Footprint bei
    # (-1,27 | -1,27) (Stift) bzw. (1,27 | -1,27) (Buchse, gespiegelt);
    # beide Hoefe sind hier um das Kontaktfeld symmetriert.
    "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD":
        (-4.60, -1.77, 7.14, 4.31),      # 11,74 x 6,08 mm
    "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD":
        (-3.28, -1.78, 5.82, 4.32),      # 9,10 x 6,10 mm
    "Module:RaspberryPi_Pico_Common_THT":
        (-2.65, -3.17, 20.43, 50.68),    # 23,08 x 53,85 mm
}


def LAGE(rechteck, pin1, drehung):
    """Ein footprint-relatives Rechteck in Platinenkoordinaten drehen.

    `drehung` in Grad, KiCad-Konvention (im Bildschirmbild gegen den
    Uhrzeigersinn; die gespeicherte y-Achse zeigt nach unten). Ein
    Punkt (fx, fy) des Footprints landet bei
        0 Grad   -> (px + fx, py + fy)
        90 Grad  -> (px + fy, py - fx)
        180 Grad -> (px - fx, py - fy)
        270 Grad -> (px - fy, py + fx)
    mit (px, py) = Lage von KONTAKT 1 (nicht von Pad 1 -- bei den
    SMD-Footprints sind das verschiedene Punkte, s. FOOTPRINT_HOF).
    Die Formel ist der Grund, warum die
    Eintraege unten sowohl `pin1`/`drehung` als auch `flaeche` tragen:
    der Test rechnet die eingetragene Flaeche aus den ersten beiden
    nach und faengt so einen Zahlendreher ab.
    """
    x0, y0, x1, y1 = rechteck
    px, py = pin1
    ecken = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    aus = []
    for fx, fy in ecken:
        if drehung == 0:
            aus.append((px + fx, py + fy))
        elif drehung == 90:
            aus.append((px + fy, py - fx))
        elif drehung == 180:
            aus.append((px - fx, py - fy))
        elif drehung == 270:
            aus.append((px - fy, py + fx))
        else:
            raise ValueError("nur 0/90/180/270 Grad, nicht %r" % (drehung,))
    xs = [p[0] for p in aus]
    ys = [p[1] for p in aus]
    return (round(min(xs), 3), round(min(ys), 3),
            round(max(xs), 3), round(max(ys), 3))


def HOF(footprint, pin1, drehung):
    """Hof (F.CrtYd) eines Footprints in Platinenkoordinaten."""
    return LAGE(FOOTPRINT_HOF[footprint], pin1, drehung)


def HOEFE(footprints, pin1, drehung):
    """Gemeinsamer Hof mehrerer Footprints am selben Ort.

    Ein Steckerplatz traegt bei den SMD-Paaren ZWEI Bauteile (Buchse
    oben, Stiftleiste unten) auf demselben Kontaktraster. Belegt ist
    dann die Vereinigung beider Hoefe -- die eine Haelfte darf nicht
    stillschweigend hinter der anderen verschwinden.
    """
    kaesten = [HOF(f, pin1, drehung) for f in footprints]
    return (round(min(k[0] for k in kaesten), 3),
            round(min(k[1] for k in kaesten), 3),
            round(max(k[2] for k in kaesten), 3),
            round(max(k[3] for k in kaesten), 3))


RASTER = 2.54      # mm Rastermass aller drei Stecker (2,54 mm / 0,1")

# Footprint -> (Spalten, Reihen). Zusammen mit RASTER ergibt das die
# KONTAKT-Lagen; die Nummerierung ist die von KiCad fuer die
# Conn_0NxNN_Odd_Even-Familie: Kontakt 1 links oben, danach zeilenweise
# (Pin 1 und 2 nebeneinander, Pin 3 und 4 die naechste Reihe). An den
# echten .kicad_mod-Dateien nachgesehen, nicht angenommen -- bei
# PinHeader_2x20 liegt Pad 1 bei (0|0), Pad 2 bei (2,54|0), Pad 3 bei
# (0|2,54). Bei den SMD-Footprints liegen die Loetpads seitlich, die
# KONTAKTE aber weiterhin genau auf diesem Raster -- und nur die
# zaehlen fuer die Frage, ob ein Stift einen Kontakt trifft.
FOOTPRINT_RASTER = {
    "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical": (2, 20),
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left":
        (1, 2),
    "Connector_PinSocket_2.54mm:PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left":
        (1, 2),
    "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD": (2, 2),
    "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD": (2, 2),
}


def PAD_LAGEN(footprint, pin1, drehung):
    """Kontakt-Nummer -> (x, y) in Platinenkoordinaten.

    Gebraucht fuer die Verdreh-Probe: ob ein um 180 Grad verdreht
    aufgesetztes Modul steckt, entscheidet nicht die Flaeche, sondern
    ob ein Stift einen Kontakt trifft.
    """
    spalten, reihen = FOOTPRINT_RASTER[footprint]
    aus = {}
    for reihe in range(reihen):
        for spalte in range(spalten):
            pin = reihe * spalten + spalte + 1
            ecke = LAGE((spalte * RASTER, reihe * RASTER,
                         spalte * RASTER, reihe * RASTER), pin1, drehung)
            aus[pin] = (ecke[0], ecke[1])
    return aus


def MITTE(flaeche):
    """Mittelpunkt einer Flaeche (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = flaeche
    return (round((x0 + x1) / 2.0, 3), round((y0 + y1) / 2.0, 3))


def VERDREHT(flaeche):
    """Dieselbe Flaeche, nachdem die Platine um 180 Grad gedreht wurde.

    Das Lochbild M3_HOLES ist punktsymmetrisch zur Platinenmitte -- ein
    Modul laesst sich also verdreht anschrauben. Diese Funktion sagt,
    wo ein Stecker dann liegt; s. Kommentar bei STECKER_POS.
    """
    x0, y0, x1, y1 = flaeche
    return (round(BOARD_W - x1, 3), round(BOARD_H - y1, 3),
            round(BOARD_W - x0, 3), round(BOARD_H - y0, 3))


# Die drei Vertragsstecker. `mitte`, `drehung` und `flaeche` (der
# belegte Hof) sind das, was jede Platine einhalten muss; `pin1`
# (Kontakt 1) und `footprints` sind die Herleitung dazu.
#
# `footprints` ist eine Liste, weil zwei der drei Plaetze ZWEI Bauteile
# tragen: die SMD-Buchse oben und die SMD-Stiftleiste unten, auf
# demselben Kontaktraster (Begruendung im Block bei STECKER_KETTE).
# `flaeche` ist die Vereinigung beider Hoefe -- HOEFE() rechnet sie
# nach.
#
# Warum genau diese drei Plaetze:
#
# * Der Stapelstecker liegt QUER (Drehung 90 Grad) und oben. Quer, weil
#   er 51,81 mm lang ist: laege er laengs, belegte er fast die ganzen
#   60 mm Hoehe und zerschnitte jede Platine in zwei schmale Spalten.
#   Oben, weil die untere Kante allen Modulen fuer die Schraubklemmen
#   gehoert (12,20 mm tief, Footprint-Hof der DB128L-Klemmen) -- so
#   bleibt unter ihm EINE grosse zusammenhaengende Flaeche statt zweier
#   halber. Sein Hof haelt 1,18 mm Abstand zum Freihaltebereich der
#   oberen M3-Bohrungen.
# * Der Leistungsstecker sitzt unten rechts, so weit vom Signalstecker
#   weg, wie es auf 64 x 60 mm geht (Design-Doc, Abschnitt "Die beiden
#   Stecker": "Getrennt vom Signalstecker gefuehrt, damit Motorstroeme
#   nicht neben empfindlichen Leitungen liegen"). Er liegt zugleich
#   ausserhalb des Antennen-Sperrbereichs des Pico und knapp ueber dem
#   Klemmenstreifen. Kontakt 1 ist am 2026-08-31 (Aufgabe 5e) von
#   x = 57,50 auf x = 54,70 gewandert -- NICHT aus Geschmack: das
#   SMD-Paar baut 11,74 statt 6,09 mm breit (die Loetpads liegen
#   seitlich neben den Stiften), und an der alten Stelle haette sein
#   Hof bei x = 64,64 ueber die Platinenkante gestanden. Von den
#   Stellen, die auf die Platine passen, ist 54,70 die am weitesten
#   rechts liegende, an der die Verdreh-Probe noch ueber der
#   2,5-mm-Reissleine bleibt (2,755 mm; bei x = 56,00 waeren es nur
#   2,460 mm gewesen) -- gescannt in 0,1-mm-Schritten ueber alle
#   zulaessigen Lagen, nicht geraten.
# * Der Kettenstecker sitzt im schmalen Streifen ueber dem Stapel-
#   stecker, links. SEL laeuft von dort auf kurzem Weg zum D-Flipflop
#   des Moduls, das seinerseits neben dem Stapelstecker liegt. Kontakt 1
#   bleibt an seinem Platz; nur sein Hof waechst von 3,54 auf 6,82 mm
#   Breite, und das passt dort ohne Verschiebung.
STECKER_POS = {
    "stapel": {
        "zweck": "2x20-Stapelstecker, Pico-Pinbild (PIN_ROLLE)",
        "stecker": "STECKER_STAPEL",
        "footprints": (
            "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical",
        ),
        "pin1": (8.00, 13.00),
        "drehung": 90,
        "mitte": (32.125, 11.725),
        "flaeche": (6.22, 8.68, 58.03, 14.77),
    },
    "kette": {
        "zweck": "zweipoliger Kettenstecker, SEL + GND (STECKER_KETTE)",
        "stecker": "STECKER_KETTE",
        "footprints": (
            # oben: Buchse, unten: Stiftleiste -- selber Ort
            "Connector_PinSocket_2.54mm:PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left",
            "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left",
        ),
        "pin1": (12.50, 2.75),
        "drehung": 0,
        "mitte": (12.5, 4.02),
        "flaeche": (9.09, 0.87, 15.91, 7.17),
    },
    "leistung": {
        "zweck": "2x2-Leistungsstecker, 24 V und GND je doppelt",
        "stecker": "STECKER_LEISTUNG",
        "footprints": (
            "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD",
            "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD",
        ),
        "pin1": (54.70, 42.00),
        "drehung": 0,
        "mitte": (55.97, 43.27),
        "flaeche": (50.1, 40.22, 61.84, 46.32),
    },
}

# Der Pico -- NUR auf der Sockelplatine.
# Drehung 90 Grad legt seine Laengsachse nach rechts: die USB-Buchse
# zeigt zur linken Platinenkante (ihre Stirnflaeche liegt 1,10 mm
# hinter der Kante, der Stecker erreicht sie also), die Antenne zeigt
# nach rechts. Das ist die Gegenrichtung zur unteren Klemmenkante --
# das USB-Kabel kommt damit nicht dort heraus, wo die Exponat-
# Verkabelung liegt.
PICO_POS = {
    "zweck": "Raspberry Pi Pico, nur auf der Sockelplatine",
    "footprints": ("Module:RaspberryPi_Pico_Common_THT",),
    "pin1": (3.80, 36.00),
    "drehung": 90,
    "mitte": (27.555, 27.11),
    "flaeche": (0.63, 15.57, 54.48, 38.65),
}

# Sperrbereich unter der WLAN-Antenne des Pico: kein Kupfer, keine
# Bauteile. Auf der Sockelplatine wird daraus im Layout entweder eine
# Kupferfreihaltung oder (wie im Vorlaeuferprojekt) ein gefraester
# Schlitz.
#
# Das ist die teuerste Lektion des Vorgaengerprojekts: die Antenne
# sitzt ZWISCHEN den beiden Pin-Reihen, nicht am Rand -- ein Ueberhang,
# der sie ins Freie bringen soll, nimmt zwangslaeufig acht Pins mit
# hinaus (PecheAuxCanards, docs/.../2026-08-27-board-redesign-design.md,
# "Nachtrag 2026-08-28: Schlitz statt Ueberhang").
#
# Masse, belegt statt geschaetzt -- (x0, y0, x1, y1) relativ zu Pad 1
# des Pico-Footprints:
#
# 1. Groesse aus dem Datenblatt: "Raspberry Pi Pico W Datasheet",
#    Raspberry Pi Ltd, Release 7, Build date 03/07/2026, Abschnitt
#    2.2.1 "Keep-out area": "There is a cutout for the antenna
#    (14 mm x 9 mm). If anything is placed close to the antenna (in any
#    dimension) the effectiveness of the antenna is reduced."
#    Wortgleich im "Raspberry Pi Pico 2 W Datasheet", Release 2,
#    Build date 03/07/2026, ebenfalls Abschnitt 2.2.1.
# 2. Lage: Abschnitt 2 "Mechanical specification" desselben
#    Datenblatts -- "a single sided 51 mm x 21 mm x 1 mm PCB with a
#    micro USB port overhanging the top edge ... The onboard wireless
#    antenna is located on the bottom edge." Der Ausschnitt liegt also
#    buendig an der der USB-Buchse gegenueberliegenden Kante und mittig
#    ueber die 21 mm Breite. Im Footprint Module:RaspberryPi_Pico_
#    Common_THT liegt diese Platinenkante bei y = 49,63 und die Mitte
#    der 21 mm bei x = 8,89 (F.Fab-Umriss x -1,61..19,39,
#    y -1,37..49,63, relativ zu Pad 1).
# 3. Breite: die offizielle KiCad-Fassung des Pico W
#    (Module:RaspberryPi_Pico_W_SMD.kicad_mod, kicad-footprints
#    a2d01395d2) traegt eine benannte Sperrzone "Antenna Copper Keep
#    Out"; ihr umschliessendes Rechteck ist 14,2 x 8,0 mm -- 0,2 mm
#    breiter, aber 1,0 mm flacher als die Datenblattangabe. Der Vertrag
#    nimmt die VEREINIGUNG beider Angaben: 14,2 mm breit (KiCad),
#    9,0 mm tief (Datenblatt). Keine der beiden Zahlen ist geraten.
#
#    -> x: 8,89 +- 7,1  = 1,79 .. 15,99
#    -> y: 49,63 - 9,00 = 40,63 .. 49,63
PICO_ANTENNE_HOF = (1.79, 40.63, 15.99, 49.63)

# Derselbe Bereich in Platinenkoordinaten der Sockelplatine, aus
# PICO_POS gedreht (9,00 x 14,20 mm, weil PICO_POS 90 Grad gedreht
# ist). Geprueft in tests/test_stack_spec.py: er ueberschneidet weder
# einen der drei Stecker noch einen Freihaltebereich der M3-Bohrungen.
ANTENNE_SPERRBEREICH = (44.43, 20.01, 53.43, 34.21)

# --- Wieviel Platz bleibt uebrig ------------------------------------
# Ein Vertrag, der die Stecker so hinlegt, dass kein Modul mehr
# hineinpasst, ist wertlos. Untergrenze, hergeleitet statt geraten:
#
# MODUL_HOF_SUMME_MM2 ist die Summe der Bauteil-Hoefe des heute
# anspruchsvollsten Moduls (Motormodul, hardware/kicad/motor/
# Motormodul.kicad_sch, 43 Bauteile) OHNE die drei Vertragsstecker --
# gemessen aus denselben echten Footprints wie FOOTPRINT_HOF oben.
MODUL_HOF_SUMME_MM2 = 956.8
# BELEGUNGSGRAD_ERPROBT ist der Anteil der Platinenflaeche, den die
# Hoefe auf einer WIRKLICH gebauten, verlegten und DRC-sauberen
# 2-Lagen-Platine desselben Umrisses belegen: die Vereinigung aller
# Hoefe in PecheAuxCanards/tools/pcb/spec.py (PLACEMENT) deckt
# 2172,8 mm2 von 64 x 60 = 3840 mm2. Mehr als das passt erfahrungs-
# gemaess nicht mehr, ohne dass die Verdrahtung nicht mehr aufgeht.
BELEGUNGSGRAD_ERPROBT = 0.566
# Daraus die Untergrenze: 956,8 / 0,566 = 1690,5 mm2, aufgerundet.
FREIE_FLAECHE_MINDEST = 1700.0
# Dieselbe Rechnung fuer die Sockelplatine, die zusaetzlich den Pico
# und dessen Antennen-Sperrbereich verliert: ihre eigenen acht Bauteile
# (J1, D1, C3, C1, C2, R1, R2, U2 -- ohne die drei Vertragsstecker und
# ohne den Pico selbst) summieren sich auf 437,8 mm2 Hof, das sind bei
# demselben erprobten Belegungsgrad 773,5 mm2 Bedarf. Sie hat nach
# Abzug von Pico und Sperrbereich noch 1711,5 mm2 am Stueck.
SOCKEL_HOF_SUMME_MM2 = 437.8
# Die hier festgelegte Anordnung laesst einem Modul 3013,0 mm2 am
# Stueck (78,5 % der Platine), groesstes freies Rechteck 1852,2 mm2
# -- Faktor 1,77 ueber der Untergrenze. Bis Aufgabe 5e waren es
# 3077,7 mm2; die 64,7 mm2 Unterschied sind der Preis der breiteren
# SMD-Hoefe. Der Sockelplatine bleiben 1711,5 mm2 (vorher 1776,2),
# gegen 773,5 mm2 Bedarf. Nachgerechnet in tests/test_stack_spec.py
# mit tools/pcb/geometry.freie_flaeche().

# --- Verdreht aufgesteckt --------------------------------------------
# M3_HOLES ist punktsymmetrisch zur Platinenmitte: (4|4) und (60|56)
# tauschen unter einer 180-Grad-Drehung die Plaetze, (4|56) und (60|4)
# ebenso. Ein Modul laesst sich also seitenrichtig, aber um 180 Grad
# verdreht auf die Abstandsbolzen schrauben. Auf dem Stapelstecker
# wuerde das Pin 1 auf Pin 40 legen -- VBUS auf FLASH_TX -- und den
# Stapel zerstoeren. Der Umriss ist Vertrag und laesst sich nicht
# unsymmetrisch machen; die Steckerlage dagegen schon, und genau dafuer
# liegen die drei Stecker oben BEWUSST UNSYMMETRISCH:
#
#   VERDREHT(...) der drei Flaechen ergibt
#     stapel   -> (5.97, 45.23, 57.78, 51.32)
#     kette    -> (48.09, 52.83, 54.91, 59.13)
#     leistung -> (2.16, 13.68, 13.90, 19.78)
#
#   Keine dieser drei Flaechen deckt sich mit der eines Steckers.
#   Entscheidend ist aber nicht die Flaeche, sondern das Raster: der
#   kleinste Abstand zwischen einem verdrehten Kontakt und irgendeinem
#   Kontakt betraegt 2,755 mm (bis Aufgabe 5e: 2,881 mm -- der
#   Leistungsstecker mussten fuer sein breiteres SMD-Paar umziehen).
#   Das ist mehr als das halbe Raster (1,27 mm), das
#   ein Stift braucht, um in einen Buchsenkontakt zu finden -- ein
#   verdreht aufgesetztes Modul steckt NIRGENDS. Es bleibt tot, statt
#   kaputtzugehen. tests/test_stack_spec.py rechnet beides nach, damit
#   eine kuenftige Verschiebung das nicht stillschweigend aufhebt.
#
# Tot ist besser als kaputt, aber nicht gut genug: sichtbar wird der
# Fehler dadurch nicht. Die zugehoerige Layout-Auflage steht in
# AUFLAGEN unten (Pin-1-Kennzeichnung, kein freiliegendes Kupfer in den
# drei verdrehten Flaechen).
VERDREHT_MINDESTABSTAND_MM = 2.755   # gerechnet, s. Test

# --- Belegte Bauhoehen im Stapelspalt (gegen STAPEL_ABSTAND) --------
# Beide Werte aus echten Datenblaettern gelesen, nicht geschaetzt --
# Herleitung siehe Kommentar bei STAPEL_ABSTAND und hardware/bauteile-1b.md,
# Beleg 6, zweite Runde.
KLEMME_HOEHE_MM = 10.10   # DB128L-5.08-2P/-3P (C395868/C395869), Datenblatt
                          # DORABO "DB128L-5.08-XXP-C-S" (2022.11.25),
                          # Seitenansicht, Bemassung "10.10" -- ein
                          # Zeichnungssatz fuer alle Polzahlen, Hoehe
                          # unabhaengig von der Polzahl XX.
K7805_HOEHE_MM = 10.2     # K7805-2000R3 (C2931187), SIP-3, Datenblatt DEXU
                          # Electronics "K78xx-2000R3", Rev. A0-2018.12,
                          # S. 2, Tabelle "外观尺寸": "长*宽*高
                          # 11.6*7.5*10.2mm" (Laenge*Breite*Hoehe).

# --- Auflagen an die Modulfirmware ----------------------------------
# Teil des Vertrags, aber keine Geometrie und keine Pinnummer: Regeln,
# die Modulfirmware einhalten muss, damit ein fremdes Modul den Stapel
# nicht lahmlegt.
AUFLAGEN = (
    "Ausserhalb des Flash-Modus darf ein Modul die Leitung FLASH_RX "
    "nicht treiben. FLASH_RX ist der Empfangspin des Pico und damit "
    "die gemeinsame Sendeleitung aller Module. Im Normalbetrieb sind "
    "alle Module gleichzeitig wach; treibt mehr als eines diese "
    "Leitung, fallen sie einander ins Wort und koennen einander im "
    "Gegentakt beschaedigen. Senden darf ein Modul nur, solange es "
    "ueber die Auswahlkette ausgewaehlt ist (FLASH_MODE = 1 und das "
    "eigene Flipflop Q = 1). Sonst bleibt der Pin hochohmig.",
)

# Auflagen an das LAYOUT eines Moduls -- ebenfalls Vertrag, aber
# Kupfer und Bestueckungsdruck statt Software. Getrennt von
# AUFLAGEN, weil das eine der Firmware gilt und das andere der
# Platine.
LAYOUT_AUFLAGEN = (
    "Jede Platine traegt neben Pin 1 des Stapelsteckers eine "
    "Kennzeichnung im Bestueckungsdruck (Dreieck plus Text \"1\") und "
    "an der Klemmenkante (untere Kante, y = BOARD_H) die "
    "Beschriftung \"KLEMMEN\". Grund: das "
    "M3-Lochbild ist punktsymmetrisch, ein Modul laesst sich also um "
    "180 Grad verdreht anschrauben. Die Steckerlage (STECKER_POS) ist "
    "bewusst so unsymmetrisch, dass dann kein einziger Stift in einen "
    "Buchsenkontakt findet -- das verhindert den Schaden, macht den "
    "Fehler aber nicht sichtbar. Ausserdem darf in den drei Flaechen "
    "VERDREHT(STECKER_POS[...][\"flaeche\"]) kein freiliegendes Kupfer "
    "liegen (keine Testpunkte, keine offenen Pads): dort setzen die "
    "Stifte eines verdreht aufgesteckten Moduls auf.",

    "Ketten- und Leistungsstecker sind SMD-Paare: Buchse auf der "
    "Oberseite, Stiftleiste auf der Unterseite, auf demselben "
    "Kontaktraster und OHNE Durchkontaktierung zwischen den beiden "
    "Kontaktflaechen. Beim Kettenstecker ist die fehlende "
    "Durchkontaktierung die eigentliche Funktion: oben liegt SEL_IN, "
    "unten SEL_OUT: waeren sie verbunden, waere die Auswahlkette "
    "kurzgeschlossen und das Schieberegister (tools/kette.py) "
    "wirkungslos. Beim Leistungsstecker fuehren beide Seiten dasselbe "
    "Netz; dort ist die Verbindung erlaubt, aber sie gehoert dann in "
    "eine eigene Durchkontaktierung neben dem Pad, nicht in das "
    "SMD-Pad selbst.",

    "Beide SMD-Steckerpaare brauchen eine Zugentlastung: die "
    "Steckkraft eines ganzen Stapels darf nicht an den Loetstellen "
    "haengen. Zulaessig sind zwei zusaetzliche, mechanisch "
    "verschraubte oder verklebte Befestigungspunkte je Stecker, oder "
    "ein Fuegeverfahren, bei dem die Platinen ERST gesteckt und DANN "
    "auf die Abstandsbolzen geschraubt werden. Welches von beiden, "
    "entscheidet die Layout-Aufgabe -- aber nicht keines von beiden. "
    "Bedrahtete Stecker haetten das nicht gebraucht; sie sind hier "
    "aber ausgeschlossen (s. Block bei STECKER_KETTE).",
)

# --- Modultypen -----------------------------------------------------
# 0x00 ist ungueltig (ein unbeschriebener Kennwiderstand liest 0).
# 0x80 und darueber bleibt fremden Modulen vorbehalten.
MODULTYPEN = {
    0x01: {"name": "Motor",    "kanaele": 1},
    0x10: {"name": "Dimmer1",  "kanaele": 1},
    0x11: {"name": "Dimmer3",  "kanaele": 3},
    0x12: {"name": "Dimmer4",  "kanaele": 4},
}

# --- Kennwiderstaende -----------------------------------------------
# Zwei Teiler gegen einen festen Oberwiderstand, je 16 Stufen aus der
# E24-Reihe. Die Stufen sind so gewaehlt, dass sich benachbarte
# Spannungsteiler um mehr als 3 % unterscheiden -- weit mehr als die
# Streuung von 1-%-Widerstaenden und die Aufloesung des ADC.
# Die Werte sind nicht die E24-Reihe der Reihe nach, sondern so
# gewaehlt, dass die SPANNUNGSTEILER gleichmaessig liegen. Nimmt man
# stumpf E24, draengen sich die oberen Stufen: zwischen 150 k und 220 k
# liegen nur 1,9 % Spannungsunterschied, weniger als die Streuung von
# 1-%-Widerstaenden zusammen mit dem ADC-Fehler.
ID_OBEN = 10000.0
ID_WIDERSTAENDE = (
    0.0, 680.0, 1500.0, 2200.0, 3300.0, 4700.0, 6200.0, 7500.0,
    10000.0, 13000.0, 16000.0, 22000.0, 30000.0, 43000.0, 68000.0,
    150000.0,
)


def ID_ANTEIL(r):
    """Spannungsanteil am ADC fuer einen Kennwiderstand."""
    return r / (r + ID_OBEN)

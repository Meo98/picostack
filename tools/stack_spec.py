"""Der Vertrag von PicoStack: Steckerbelegung, Umriss, Modultypen.

Bewusst ohne KiCad-Abhaengigkeit, damit er ohne KiCad geprueft werden
kann -- und damit fremde Werkzeuge ihn lesen koennen, ohne KiCad zu
installieren.

Was hier steht, ist die Zusage an alle, die eigene Module bauen.
Aendert sich etwas davon, sind fremde Module unbrauchbar. Alles andere
im System darf sich aendern.

Grundlage: docs/superpowers/specs/2026-08-28-picostack-design.md

--- v2: der Pico ist der Stapel (2026-09-0x, Commit 7daaad3) -----------
v1 hatte eine eigene Sockelplatine, die EINEN Pico trug und seine 40
Pins ueber einen gemeinsamen 2x20-Stapelstecker (STECKER_POS["stapel"],
Bauform "Buchse mit durchgehendem Stift") an den Rest des Stapels
weiterreichte. v2 streicht diese Sonderrolle: JEDES Modul bekommt seine
zwei eigenen 1x20-Buchsenreihen in echter Pico-Geometrie (Reihenabstand
17,78 mm -- das Pico-Datenblattmass, nicht mehr ein beliebiges
2,54-mm-Raster) und damit seinen eigenen, dort eingesteckten Pico.
STECKER_POS["stapel"] gibt es deshalb nicht mehr; an seiner Stelle
stehen STECKER_POS["stapel_links"] und ["stapel_rechts"] (eine Reihe je
Pico-Seite, s. Kommentar dort). VERTRAG_VERSION haelt diesen Bruch
maschinenlesbar fest, damit ein Werkzeug, das noch mit v1 rechnet, sich
selbst erkennt, statt still falsche Koordinaten zu benutzen.

Aus demselben Grund sind PICO_POS, PICO_ANTENNE_HOF und
ANTENNE_SPERRBEREICH in v2 nicht mehr Teil dieses Vertrags: sie
beschrieben die Lage EINES bestimmten, huebsch aufgeloeteten Pico auf
GENAU EINER Platine (der Sockelplatine). Wenn stattdessen jedes Modul
seinen Pico selbst traegt, gibt es keine einzelne, ausgezeichnete
Pico-Position mehr, gegen die sich das pruefen liesse -- die Flaeche,
die der Pico einnimmt, IST jetzt die Flaeche von stapel_links/rechts
zusammen. Was dabei verloren geht: der WLAN-Antennen-Sperrbereich des
Pico ist eine reale Pflicht (Datenblatt, Abschnitt 2.2.1), die v1 hier
maschinenlesbar hielt. Sie ist in v2 NICHT neu hergeleitet -- das
haette eine eigene, nicht in Aufgabe 2 verlangte Entscheidung ueber die
Pico-Orientierung auf dem neuen Umriss gebraucht (liegt die Antenne
ueber freiem Rand oder ueber Kupfer?). Offener Punkt fuer eine
Folgeaufgabe, s. Bericht zu Aufgabe 2.
"""

VERTRAG_VERSION = 2

BOARD_W = 75.0
BOARD_H = 65.0
# Hergeleitet in tools/platzprobe_v2.py (Aufgabe 1): das alte Mass
# (64x60) wurde nie gegen die v2-Zusatzlast gerechnet (zwei
# Pico-Buchsenreihen, eigene 6-30-V-Versorgungszelle, 22 Randpads).
# platzprobe_v2.pruefe() rechnet drei Kandidaten (70x60, 75x65, 80x70)
# durch: 70x60 scheitert an der Geometrie (die Versorgungszelle und die
# Randpad-Kante sind breiter als der Rand neben den M3-Eckloechern
# zulaesst), 75x65 und 80x70 bestehen beide; 75x65 ist der kleinere der
# beiden bestandenen Kandidaten und damit das Ergebnis
# (`python3 tools/platzprobe_v2.py` druckt "EINHEITSMASS: 75x65").
CORNER_R = 3.0

PLATINE_DICKE = 1.6      # mm, Standard-PCB-Dicke (JLCPCB); auch Grundlage
# der Spaltrechnung unten und der Gehaeuse-Konstruktion (Aufgabe 9).

M3_DRILL = 3.2
# Wie v1: 4,0 mm Abstand von jeder Kante (dieselbe Herleitung, nur auf
# das neue Mass angewendet -- v1 rechnete ebenfalls nicht von der Mitte,
# sondern zog 4,0 mm von jeder der vier Kanten ab/dazu). Bei 75x65 also
# (4, 4), (4, 65-4), (75-4, 4), (75-4, 65-4).
M3_HOLES = [(4.0, 4.0), (4.0, 61.0), (71.0, 4.0), (71.0, 61.0)]

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
#
# TEILWEISE AUFGEHOBEN fuer Pin 39 (VSYS), Fix-Runde 1, Task-5-Review,
# 2026-09-08. Das RULING oben stammt aus Aufgabe 6 (v1) und ging davon
# aus, dass niemand VSYS speist -- Grund (1) war "es gibt heute keinen
# Verbraucher". Das stimmt seit der v2-VERSORGUNG-Zusage
# (VERSORGUNG["vsys_diode"] == True) nicht mehr: JEDES Modul bekommt
# ueber tools/sch/versorgung.py eine Schottky-Diode (D91), die genau
# dafuer gebaut ist, VSYS zu speisen -- der Verbraucher, dessen Fehlen
# Grund (1) trug, existiert jetzt in jeder Modul-Stueckliste. Grund (2)
# ("dann muss der Vertrag zusaetzlich regeln, dass kein Modul VSYS
# OHNE Diode speisen darf") ist damit nicht entfallen, sondern GENAU
# das, was diese Runde regelt: erlaubt ist ausschliesslich die
# Einspeisung UEBER die Entkopplungsdiode der Versorgungszelle (s.
# vsys_diode-Kommentar bei VERSORGUNG oben), eine direkte, ungeschuetzte
# Verbindung bleibt verboten. Gefunden wurde die Luecke, weil ein zuerst
# fehlender Verbindungspunkt fuer VSYS in einem generierten Schaltplan
# als `isolated_pin_label`-ERC-Warnung sichtbar wurde (Task 5,
# Motormodul) -- der Vertrag verbot genau das Netz, das die eigene
# VERSORGUNG-Zusage verlangt. RUN/ADC_VREF/3V3_EN/VBUS sind von diesem
# Ruling nicht betroffen und bleiben unveraendert nicht belegbar (keiner
# von ihnen hat ein Gegenstueck in VERSORGUNG).
NICHT_BELEGBAR = {
    30: "RUN -- Reset des RP2040, aktiv-LOW mit eigenem Pullup "
        "(Pico Datasheet Rel. 21, Abschnitt 2.1). Ein Modul, das ihn "
        "treibt, setzt den Pico zurueck.",
    35: "ADC_VREF -- analoge Referenzspannung des ADC, kein "
        "Digitalanschluss.",
    37: "3V3_EN -- schaltet den internen Regler des Pico ab. Nach "
        "aussen gefuehrt waere das ein Ausschalter fuer den ganzen "
        "Stapel, den jedes Modul versehentlich ziehen koennte.",
    40: "VBUS -- liegt nur an, wenn am Pico ein USB-Kabel steckt. Eine "
        "Schiene, die von einem Zufall abhaengt, ist keine Zusage.",
}
# Pin 39 (VSYS) stand hier bis Fix-Runde 1 (Task-5-Review, 2026-09-08)
# ebenfalls drin -- s. Absatz oben. Er ist jetzt belegbar, aber NUR
# ueber die Entkopplungsdiode der Versorgungszelle (VERSORGUNG
# ["vsys_diode"]); eine direkte Verbindung waere trotzdem falsch, das
# regelt IST_BELEGBAR() alleine nicht (s. dortiger Docstring).


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

# --- v2: footprint-lokale Kontakte -> Pico-Pin (stapel_links/rechts) --
# PIN_ROLLE oben ist UNVERAENDERT: sie kennt nur Pico-Pin-Nummern
# (1..40), keine Steckerplaetze. Was sich mit v2 aendert, ist allein,
# WELCHER footprint-lokale Kontakt (PAD_LAGEN(), s. unten) welchen
# Pico-Pin traegt -- in v1 galt Kontakt k == Pico-Pin k fuer den
# gesamten 2x20-Block; in v2 gilt das nur noch INNERHALB je einer
# Reihe, und die Zuordnung ist bewusst so gewaehlt, dass eine einzige
# Formel je Reihe reicht (keine Tabelle, kein Umdrehen von Hand):
#
#   stapel_links,  Drehung 0   : Pico-Pin == footprint-lokaler Kontakt
#                                 (k = 1..20)
#   stapel_rechts, Drehung 180 : Pico-Pin == footprint-lokaler Kontakt
#                                 + 20 (k = 1..20 -> Pico-Pin 21..40)
#
# Das ist keine neue Zusage -- es folgt zwingend aus der Pin-1-Lage,
# die STECKER_POS["stapel_rechts"] bereits eintraegt (Kontakt 1 unten,
# waechst nach oben, s. dortiger Kommentar) und aus der geforderten
# Zaehlrichtung "21-40 rechts unten->oben". Ein Modullayout, das
# PAD_LAGEN(footprint, pin1, drehung) fuer stapel_rechts aufruft, muss
# also 20 zum zurueckgegebenen Kontaktschluessel addieren, um den
# Pico-Pin (und damit die PIN_ROLLE) zu bekommen.

# --- v2: freie GPIO an den Rand -- RANDPADS ---------------------------
# Jeder der 18 Pico-Pins mit PIN_ROLLE == "frei" bekommt ein eigenes,
# beschriftetes Loetpad an der UNTEREN Plattenkante -- damit ein
# Modulautor, der einen freien GPIO braucht, ihn ohne eigene
# Durchkontaktierung von den beiden Pico-Buchsenreihen abgreifen kann,
# genau wie in v1 (dort lagen die freien Pins einfach unbenutzt im
# 2x20-Block, ohne eigenen Zugriffspunkt). Dazu vier Versorgungspads
# (2x 3V3, 2x GND), die die GPIO-Strecke an beiden Enden einrahmen --
# uebliche Header-Praxis, und praktisch fuer ein Multimeter oder einen
# Pull-up/-down-Widerstand in Griffnaehe zum jeweiligen GPIO.
#
# Lage: 2,54-mm-Raster (RAND_RASTER), y nahe der unteren Kante
# (BOARD_H - 2,0 mm, Aufgabenzettel), x beginnend bei 8,0 mm -- knapp
# ausserhalb der M3-Eckloch-Reichweite (M3_KEEPOUT/2 + 4,0 mm
# Lochabstand = 7,5 mm, s. platzprobe_v2.M3_REICHWEITE), damit das
# erste Randpad nicht mit dem Freihaltebereich des linken unteren
# Eckochs kollidiert. 22 Pads x 2,54 mm = 53,34 mm Gesamtbreite, endet
# bei x = 61,34 mm -- bleibt mit 13,66 mm klar innerhalb der
# 75-mm-Breite und weit vor der M3-Eckloch-Reichweite auf der rechten
# Seite (67,5 mm).
RAND_RASTER = 2.54
RAND_X0 = 8.0
RAND_Y = round(BOARD_H - 2.0, 3)

# Pico-Pin -> GPIO-Nummer, NUR fuer die frei bleibenden Pins. Aus dem
# offiziellen Pico-Pinout (Raspberry Pi Pico Datasheet, Release 21,
# Abschnitt 2 "Pinout"): die Pins zaehlen GP0..GP22 lueckenlos durch
# (unterbrochen nur von den acht GND-Pins und Pin 30/RUN), dann folgen
# GP26/ADC0 (Pin 31), GP27/ADC1 (Pin 32), GND/AGND (Pin 33), GP28/ADC2
# (Pin 34), ADC_VREF (Pin 35) -- exakt das Bild, das PIN_ROLLE oben
# schon unveraendert traegt. Diese Tabelle ordnet den 18 frei
# bleibenden Pins nur noch ihre GPIO-Nummer zu, sie vergibt keine neue
# Rolle.
_GP_NUMMER = {
    11: 8, 12: 9, 14: 10, 15: 11, 16: 12, 17: 13,
    19: 14, 20: 15, 21: 16, 22: 17, 24: 18, 25: 19,
    26: 20, 27: 21, 29: 22, 31: 26, 32: 27, 34: 28,
}

# Reihenfolge auf der Kante: GND, 3V3, dann die 18 GPIO aufsteigend
# nach Pico-Pin, dann noch einmal 3V3, GND -- die Versorgung rahmt die
# GPIO-Strecke symmetrisch ein. Pin 3 und Pin 38 sind zwei
# VERSCHIEDENE GND-Pico-Pins (beide ohnehin dasselbe Netz, s.
# IST_VERSORGUNG/_GND oben); Pin 36 (3V3) versorgt beide 3V3-Randpads,
# weil es am Pico nur diesen einen 3V3-Ausgangspin gibt.
_RAND_REIHENFOLGE = (
    [(3, "GND"), (36, "3V3")]
    + [(p, "GP%d" % _GP_NUMMER[p]) for p in sorted(_GP_NUMMER)]
    + [(36, "3V3"), (38, "GND")]
)

RANDPADS = tuple(
    (pin, label, (round(RAND_X0 + i * RAND_RASTER, 2), RAND_Y))
    for i, (pin, label) in enumerate(_RAND_REIHENFOLGE)
)

# --- v2: Verpolschutz-Zusagen an jedes Modul --------------------------
# Jedes Modul hat jetzt seine eigene Einspeisung (6..30 V, ueber
# STECKER_LEISTUNG) UND seinen eigenen Pico -- also auch seinen eigenen
# Verpolschutz, statt dass ihn (wie in v1) nur die Sockelplatine traegt.
# VERSORGUNG haelt fest, WAS jedes Modul an dieser Stelle zusagen muss;
# WIE (welches Bauteil, welcher Footprint) ist Sache der jeweiligen
# spec_*.py und bleibt dort -- dieser Vertrag zwingt nur die Topologie
# fest, nicht die Stueckliste.
#
#   schutz_drain_an = "PWR_IN"    : der P-Kanal-MOSFET (oder aequivalente
#     Schutzschaltung), der Verpolung an der Einspeisung abfaengt, haengt
#     mit seinem Drain-Anschluss AN DER EINSPEISUNG (STECKER_LEISTUNG,
#     vor jeder eigenen Schutz-/Reglerstufe) -- nicht irgendwo dahinter.
#     Nur so schuetzt er auch alles, was danach kommt.
#   gate_teiler_an = "+24V_LOKAL" : der Spannungsteiler, der das Gate
#     dieses MOSFETs ansteuert, haengt an der LOKALEN, bereits
#     verpolungsrichtigen 24-V-Schiene des Moduls (hinter dem Schutz)
#     -- nicht an der rohen Einspeisung. Haenge er dort, koennte eine
#     verpolte Einspeisung das Gate direkt falsch ansteuern und den
#     Schutz umgehen, den er herstellen soll.
#   vsys_diode = True             : zwischen dem lokalen Regler-Ausgang
#     und Pico-VSYS sitzt eine Schottky-Diode (in Sperrichtung fuer den
#     Fall, dass der Pico stattdessen ueber USB versorgt wird) -- ohne
#     sie speisten zwei Quellen (Modul-Regler und USB-VBUS-Pico-
#     Regler) denselben Knoten gegeneinander.
#     ZUSATZ (Fix-Runde 1, Task-5-Review, 2026-09-08): genau DESHALB ist
#     Pin 39 (VSYS) seit dieser Runde belegbar (s. NICHT_BELEGBAR unten)
#     -- aber NUR auf diesem Weg. Die v1-Sperre galt der DIREKTEN,
#     ungeschuetzten Einspeisung (Rueckspeisegefahr in den internen
#     Pico-Regler, kein Verbraucher, keine Diode); diese Zusage erlaubt
#     ausschliesslich die Einspeisung UEBER die Entkopplungsdiode der
#     Versorgungszelle. Ein Modul, das VSYS ohne diese Diode direkt
#     ansteuert, verletzt die Zusage genauso, wie es sie vor dieser
#     Runde verletzt haette -- IST_BELEGBAR(39) prueft nur, ob der Pin
#     ueberhaupt eine Rolle tragen darf, nicht WIE er verdrahtet wird;
#     das bleibt Sache des Generators (s. tools/sch/versorgung.py: D91).
#   eingang_v = (6.0, 30.0)       : das Fenster, in dem die
#     Eingangsspannung liegen darf. Untergrenze 6 V: der lokale
#     Linearregler (K7805-1000R3, s. STAPEL_ABSTAND-Kommentar oben,
#     "K7805_HOEHE_MM") braucht laut Datenblatt mindestens Ausgangs-
#     spannung + 2 V Dropout, hier grosszuegig auf 6 V aufgerundet.
#     Obergrenze 30 V: die K7805-1000R3-Familie ist bis 30 V
#     Eingangsspannung spezifiziert (DEXU Electronics "K78xx-1000R3"
#     Datenblatt, "Absolute Maximum Ratings", "Input Voltage: 30V");
#     mehr wuerde den Regler ausserhalb seines Datenblatts betreiben.
VERSORGUNG = {
    "schutz_drain_an": "PWR_IN",
    "gate_teiler_an": "+24V_LOKAL",
    "vsys_diode": True,
    "eingang_v": (6.0, 30.0),
}

# --- Die vier Steckerplaetze ------------------------------------------
# Vier Steckerplaetze (v2: stapel_links, stapel_rechts, kette,
# leistung), zwei Bauprinzipien. Der Unterschied ist keine
# Geschmacksfrage, sondern folgt aus genau einer Frage: fuehren die
# Haelfte OBEN und die Haelfte UNTEN dasselbe Netz?
#
#   ja   -> EIN durchgehender Stapelstecker (Buchse oben und langer
#           Stift unten sind derselbe Leiter, ein einziges Bauteil).
#           So die beiden 1x20-Signalstecker (stapel_links/rechts, seit
#           v2 zwei Plaetze statt eines 2x20-Platzes, s. STECKER_POS-
#           Kommentar): alle 40 Leitungen sind im ganzen Stapel
#           dasselbe Netz, nur eben auf zwei Reihen verteilt statt auf
#           eine.
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
    "typ": "1x20 (oder 2x 1x10 in Reihe), 2,54 mm, Buchse mit "
           "durchgehendem Stift (PC104/Arduino-Stapelleisten-Prinzip) "
           "-- je EINE Reihe (stapel_links ODER stapel_rechts, s. "
           "STECKER_POS), nicht mehr die ganze 2x20-Pico-Bahn wie in "
           "v1",
    "durchgehend": True,           # EIN Bauteil, Buchse und Stift sind
                                   # derselbe Leiter -> beide Seiten
                                   # zwangslaeufig dasselbe Netz.
    "montage_oben": "THT",
    "montage_unten": "THT",
    "haelften_gleiche_netze": True,
    # RULING (Fix-Runde 1, 2026-09-08): der urspruengliche Vorschlag
    # dieser Aufgabe -- ein fertiges 2x20-PC104-Teil (C35165) nehmen und
    # je Reihenplatz nur EINE seiner beiden Kontaktspalten bestuecken --
    # ist MECHANISCH NICHT BAUBAR. C35165 ist ein einziges, durch-
    # gespritztes Gehaeuse mit ZWEI Pinreihen 2,54 mm auseinander; die
    # zweite (elektrisch unbenutzte) Reihe braucht trotzdem ihre eigenen
    # Bohrungen/ihren eigenen Platz im Lochbild -- ein 1x20-Lochbild
    # (nur EINE Bohrreihe, s. FOOTPRINT_HOF oben) haelt dafuer keinen
    # Platz vor. Das waere kein "eine Spalte bleibt frei", sondern ein
    # Gehaeuse, das gar nicht erst aufsteckbar ist.
    #
    # Der Vertrag geht deshalb auf den Plan-Fallback: eine ECHTE
    # EINREIHIGE Stapelleiste (Buchse oben, langer durchgehender Stift
    # unten), entweder als fertiges 1x20-Teil oder als zwei 1x10-Stuecke
    # stumpf hintereinander (dieselbe Bauform, gaengig als "Arduino-
    # Stapelheader" -- lange Buchsenstifte mit 2,54-mm-Raster, in
    # 1x6/1x8/1x10 verbreitet). Ein solches Teil mit OFFENER
    # Produktseite wurde waehrend dieser Aufgabe NICHT gefunden (LCSC/
    # JLCPCB-Websuche, Fix-Runde 1, 2026-09-08) -- die eingesehene
    # PC104-Reihe fuehrt dort nur die zweireihigen C35165/C5307344
    # (2x20) und C5307345 (2x40), hardware/bauteile-1b.md Beleg 13.
    # buchse_lcsc/stift_lcsc/buchse_mpn/stift_mpn bleiben deshalb LEER,
    # bis die Fertigungs-Sichtung (Aufgabe 9 dieser Etappe) ein
    # tatsaechlich bestellbares 1x20- oder 1x10-Teil gefunden hat --
    # eine erfundene Nummer waere schlimmer als eine ehrliche Luecke.
    #
    # C35165 taucht hier trotzdem noch auf, aber nur noch als BAUFORM-
    # BELEG: es beweist, dass "Buchse mit durchgehendem Stift" (PC104-
    # Prinzip) als Bauform real existiert und mit einer offenen
    # Produktseite bestellbar ist (s. hardware/bauteile-1b.md, Beleg 1)
    # -- NICHT als das hier zu bestueckende Teil. gehaeusehoehe_mm und
    # stiftlaenge_unter_gehaeuse_mm unten sind deshalb ZIELWERTE
    # (von C35165 als bauformaehnlicher Platzhalter uebernommen, weil
    # STAPEL_ABSTAND/EINSTECKTIEFE_STAPEL() ohne irgendeine Zahl gar
    # nicht rechnen koennten), keine Messwerte DIESES Teils -- ein
    # gefundenes 1x20/1x10-Teil muss gegen sie geprueft werden, nicht
    # umgekehrt.
    "buchse_lcsc": None,           # offen bis Fertigungs-Sichtung (T9)
    "stift_lcsc": None,            # offen bis Fertigungs-Sichtung (T9)
    "buchse_mpn": None,            # offen bis Fertigungs-Sichtung (T9)
    "stift_mpn": None,             # offen bis Fertigungs-Sichtung (T9)
    "strom_pro_kontakt_a": 3.0,    # Zielwert, uebernommen von C35165
                                   # (LCSC-Produktseite, "Current
                                   # Rating: 3A") als Bauform-Platzhalter
    "gehaeusehoehe_mm": 8.5,       # Zielwert, uebernommen von C35165
                                   # (Datenblatt, Masszeichnung
                                   # "8.5+-0.2") als Bauform-Platzhalter
    "stiftlaenge_unter_gehaeuse_mm": 12.46,  # Zielwert, uebernommen von
                                   # C35165 (Datenblatt, "12.46+-0.2")
                                   # als Bauform-Platzhalter
    "quelle": "hardware/bauteile-1b.md, Beleg 1 (Fassung 2026-08-31, "
              "C35165 als Bauform-Beleg); Sourcing-Ruling fuer 1x20 s. "
              "Kommentar oben (Aufgabe 2, Fix-Runde 1, 2026-09-08)",
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
    # v2-Stapelbuchse (eine Reihe, 1x20, echte Pico-Geometrie). Kontakt 1
    # == Pad 1 (bedrahtet). Pinspanne 19 x 2,54 = 48,26 mm (Pin 1 bis
    # Pin 20, Mitte-zu-Mitte -- das Pico-Datenblattmass); Hof lt.
    # Aufgabenzettel/tools/platzprobe_v2.py PICO_REIHE_L/B = 50,8 x
    # 5,1 mm, also 1,27 mm Ueberstand an jedem Ende der Pinreihe
    # (50,8 - 48,26 = 2,54, geteilt durch zwei Enden) und 2,55 mm
    # beidseits der Kontaktachse (5,1 / 2). Kein gemessener .kicad_mod
    # (noch kein Bauteil verifiziert bestellt, s. STECKER_STAPEL-
    # Kommentar) -- deshalb aus dem Aufgabenzettelmass abgeleitet statt
    # aus einer echten Footprint-Datei gelesen, wie es bei den anderen
    # Eintraegen hier der Fall ist. Rot-Nachweis wird nachgeholt, sobald
    # das Bauteil feststeht (s. Bericht zu Aufgabe 2, Bedenken).
    "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical":
        (-2.55, -1.27, 2.55, 49.53),     # 5,10 x 50,80 mm
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
        (-3.28, -1.78, 5.77, 4.32),      # 9,05 x 6,10 mm
        # Rechts 5,77 statt 5,82: an der gebauten Platine nachgemessen
        # (steckerprobe meldete am Motormodul 0,05 mm Hof-Abweichung;
        # der reale KiCad-Hof endet strichbereinigt bei +5,77).
    "Module:RaspberryPi_Pico_Common_THT":
        (-2.65, -3.17, 20.43, 50.68),    # 23,08 x 53,85 mm
}


# Loetpad-Schwerpunkt relativ zum Kontaktfeld-Schwerpunkt, je
# Footprint. Die SMD-Buchse 2x02 traegt ASYMMETRISCHE Ausleger (die
# Loetpads ragen links 1,3 und rechts 1,2 mm ueber die Kontakte
# hinaus) -- ihr Pad-Schwerpunkt liegt deshalb 0,05 mm westlich des
# Kontaktrasters, bei exakt vertragskonformer Lage der KONTAKTE.
# steckerprobe.pruefen() rechnet diesen Versatz beim
# Schwerpunktvergleich heraus (gefunden 2026-09-03 am Motormodul:
# die Probe meldete 0,05 mm Versatz, die Kontaktprobe war gruen).
# In FOOTPRINT-Koordinaten (Drehung 0); die Probe dreht mit.
PAD_SCHWERPUNKT_VERSATZ = {
    "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD":
        (-0.05, 0.0),
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
# KONTAKT-Lagen. `pin1` in STECKER_POS ist dabei der RASTER-ANKER: der
# linke obere Punkt des Kontaktgitters -- NICHT zwingend die Lage von
# Kontakt 1 (s. SPALTEN_GESPIEGELT unten). FOOTPRINT_HOF und HOF()
# beziehen sich auf denselben Anker.
FOOTPRINT_RASTER = {
    "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical": (2, 20),
    # Eine Spalte, 20 Reihen -- eine einzelne 1x20-Pinreihe (s.
    # FOOTPRINT_HOF oben).
    "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical": (1, 20),
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left":
        (1, 2),
    "Connector_PinSocket_2.54mm:PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left":
        (1, 2),
    "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD": (2, 2),
    "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD": (2, 2),
}

# Footprints, deren Kontaktnummerierung in Platinenkoordinaten von
# RECHTS nach links laeuft -- Kontakt 1 sitzt in der RECHTEN Spalte des
# Gitters, nicht auf dem Anker.
#
# RULING (2026-09-01, nach Aufgabe 6 an der gebauten Platine gemessen).
# Die alte Fassung dieses Blocks behauptete "Kontakt 1 links oben,
# zeilenweise, an den echten .kicad_mod-Dateien nachgesehen" -- wirklich
# nachgesehen war das nur beim 2x20-THT. Beim 2x02-SMD-Paar ist es
# falsch, und zwar fuer BEIDE Haelften:
#
#   * Die Buchse (PinSocket_2x02_SMD) hat Pad 1 RECHTS (+2,520 im
#     Footprint) -- ihr Kontakt 1 liegt in der rechten Gitterspalte.
#   * Die Stiftleiste (PinHeader_2x02_SMD) hat Pad 1 links (-2,525),
#     aber sie sitzt laut diesem Vertrag GESPIEGELT auf der UNTERSEITE
#     ("Buchse oben, Stiftleiste unten") -- in Platinenkoordinaten
#     landet ihr Kontakt 1 damit ebenfalls rechts. Die Bibliothek
#     zeichnet die Haelften absichtlich gespiegelt zueinander, damit
#     sie am selben Anker zusammenpassen.
#
# An der gebauten Sockelplatine bestaetigt (J4, Stifthaelfte auf B.Cu):
# Pad 1 traegt /PWR24V und sein Kontakt liegt bei x = 57,24 -- die alte
# PAD_LAGEN-Fassung veroeffentlichte fuer Kontakt 1 aber x = 54,70.
# Exakt spiegelverkehrt, und STECKER_LEISTUNG legt auf die Spalten
# VERSCHIEDENE Netze (Kontakt 1/3 = PWR24V, 2/4 = GND): wer nach der
# alten Koordinate einen eigenen Footprint zeichnete, setzte 24 V
# dorthin, wo der Stapel GND fuehrt.
#
# Fuer Platinen, die die KiCad-Standardfootprints benutzen, aendert
# dieses Ruling NICHTS am Kupfer -- nur die veroeffentlichte Zuordnung
# Nummer -> Ort wird der Wirklichkeit angepasst. Die 1x02-Paare sind
# nicht betroffen (eine Spalte, Nummerierung laeuft ueber die Reihen;
# an der gebauten Platine gegengeprueft: J3 Kontakt 1 liegt auf dem
# Anker). Der 2x20-THT ist nicht betroffen (Pad 1 wirklich links oben).
SPALTEN_GESPIEGELT = frozenset((
    "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD",
    "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD",
))


def PAD_LAGEN(footprint, pin1, drehung):
    """Kontakt-Nummer -> (x, y) in Platinenkoordinaten.

    Gebraucht fuer die Verdreh-Probe (ob ein um 180 Grad verdreht
    aufgesetztes Modul steckt, entscheidet nicht die Flaeche, sondern
    ob ein Stift einen Kontakt trifft) und fuer die Steckerprobe an
    der gebauten Platine (liegt Kontakt k wirklich dort, wo dieser
    Vertrag es sagt).

    Die MENGE der Punkte ist bei gespiegelter Nummerierung dieselbe --
    die Verdreh-Probe haengt an dieser Korrektur deshalb nicht. Die
    ZUORDNUNG Nummer -> Ort tut es: s. SPALTEN_GESPIEGELT.
    """
    spalten, reihen = FOOTPRINT_RASTER[footprint]
    gespiegelt = footprint in SPALTEN_GESPIEGELT
    aus = {}
    for reihe in range(reihen):
        for spalte in range(spalten):
            pin = reihe * spalten + spalte + 1
            sp = (spalten - 1 - spalte) if gespiegelt else spalte
            ecke = LAGE((sp * RASTER, reihe * RASTER,
                         sp * RASTER, reihe * RASTER), pin1, drehung)
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


# Die vier Vertragsstecker (v2: aus drei werden vier -- der 2x20-Block
# wird zu zwei 1x20-Reihen, s. Modul-Docstring). `mitte`, `drehung` und
# `flaeche` (der belegte Hof) sind das, was jede Platine einhalten
# muss; `pin1` (Kontakt 1) und `footprints` sind die Herleitung dazu.
#
# `footprints` ist eine Liste, weil zwei der vier Plaetze ZWEI Bauteile
# tragen: die SMD-Buchse oben und die SMD-Stiftleiste unten, auf
# demselben Kontaktraster (Begruendung im Block bei STECKER_KETTE).
# `flaeche` ist die Vereinigung beider Hoefe -- HOEFE() rechnet sie
# nach.
#
# stapel_links/stapel_rechts: ZWEI 1x20-Buchsenreihen in echter
# Pico-Geometrie statt eines 2x20-Blocks in freiem Raster. Die Namen
# folgen der PICO-eigenen Seite, nicht einer Himmelsrichtung auf
# unserer Platine: "links" traegt die Pico-Pins 1..20 (auf dem
# Original-Pico die linke Stiftreihe, USB-Buchse oben gedacht),
# "rechts" die Pins 21..40 (die rechte Reihe). Auf UNSERER Platine
# liegen beide Reihen SENKRECHT (Pins laufen von oben nach unten,
# genau wie auf dem Pico selbst -- keine 90-Grad-Drehung wie beim
# alten 2x20-Block noetig, weil eine einzelne 1x20-Reihe mit 50,8 mm
# Laenge bequem hochkant in die 65 mm Plattenhoehe passt) und stehen
# nebeneinander, Mittenabstand GENAU 17,78 mm (Pico-Datenblatt,
# Reihenabstand) -- das ist der Wert, den
# tests/test_stack_spec.py als "Stapelreihen in Pico-Geometrie" prueft.
# NICHT exakt ueber die Plattenbreite (75 mm) zentriert, sondern um
# 2,0 mm nach rechts verschoben -- und das ist keine Geschmacksfrage,
# sondern dieselbe Verdreh-Probe wie beim v1-Leistungsstecker (s.
# Kommentar dort, "gescannt ... nicht geraten"): stapel_links und
# stapel_rechts sind exakte Spiegelbilder voneinander (Reihenabstand
# 17,78 mm = 7 x RASTER, s.o.), UND beide Reihen liegen auf demselben
# Y-Raster (dieselben 20 Kontakthoehen, nur mit vertauschter
# Zaehlrichtung). Eine exakt MITTIGE Platzierung (Rand links/rechts je
# (75 - 22,88) / 2 = 26,06 mm) macht die 180-Grad-Drehung dadurch zur
# perfekten X-Deckung: ein verdreht aufgestecktes Modul traefe
# stapel_links exakt auf stapel_rechts in X, und der einzige
# verbleibende Schutz waere der Y-Versatz -- der bei diesem Raster nie
# ueber die haelfte des Rastermasses (1,27 mm) hinauskommt, weit unter
# der 2,5-mm-Reissleine, die tests/test_stack_spec.py seit Aufgabe 5e
# fuer jede Steckerlage verlangt (Nachrechnung ergab dort real nur
# 0,50 mm -- ROT). Um 2,0 mm aus der Mitte verschoben ergibt dagegen
# einen X-Versatz von 2 x 2,0 = 4,0 mm (die Verschiebung wirkt doppelt,
# weil sie BEIDE Reihen der gespiegelten Paarung gegeneinander
# versetzt) -- allein das haelt die Verdreh-Probe komfortabel ueber der
# Reissleine, unabhaengig vom Y-Versatz (nachgerechnet: 4,03 mm). Der
# Rand zur linken Kante (28,06 mm, s. "flaeche" von stapel_links unten)
# bleibt dabei weiterhin weit ueber der M3-Eckloch-Reichweite
# (7,5 mm) -- das Reihenpaar kann so oder so nicht in ein Eckloch
# hineinragen.
# Oben angeschlagen (1,0 mm Rand zur Plattenkante, mehr als das
# vertragliche RAND-Minimum von 0,5 mm, damit an der Buchse noch
# Loetstopplack/Silk Platz hat) -- die Reihe reicht dann von y = 1,0 bis
# y = 51,8 mm, deutlich innerhalb der 65 mm Plattenhoehe und mit reichlich
# Abstand zu den unteren M3-Loechern (y = 61).
#
# Zaehlrichtung UND Drehung sind gekoppelt (s. auch den Kommentar
# weiter oben, gleich nach PIN_ROLLE, "v2: footprint-lokale Kontakte ->
# Pico-Pin"): stapel_links
# steht bei Drehung 0, ihr footprint-lokaler Kontakt 1 liegt oben und
# waechst nach unten (Pico-Pin k == Kontakt k, k=1..20, "oben->unten"
# wie im Aufgabenzettel gefordert). stapel_rechts steht bei Drehung
# 180 -- NICHT 0 --, damit ihr footprint-lokaler Kontakt 1 physisch UNTEN
# landet und mit wachsendem Kontakt nach OBEN laeuft: genau das
# "unten->oben" der Pico-Pins 21..40, und zwar OHNE dass irgendein
# Aufrufer footprint-lokale Nummern erst umdrehen muesste (Pico-Pin
# (20+k) == footprint-lokaler Kontakt k, k=1..20 -- dieselbe simple
# Formel wie bei stapel_links, nur mit Offset 20). Die beiden Reihen
# sind dazu exakt end-zu-end ausgerichtet: pin1 von stapel_rechts liegt
# 48,26 mm (= Pinspanne, 19 x 2,54) unterhalb von pin1 von stapel_links,
# sodass beide Hoefe denselben Y-Bereich [1,0 .. 51,8] belegen.
#
# kette und leistung wandern gegenueber v1 nur soweit, wie es die neue
# Lage der Stapelzone erzwingt -- dieselbe Herleitungslogik wie in v1
# (Kettenstecker nah am Stapel/D-Flipflop, links; Leistungsstecker so
# weit wie moeglich vom Signalstecker weg, unten rechts), neu
# angewendet auf den 75x65-Umriss und die jetzt SEITLICH statt oben
# liegende Stapelzone:
#
# * Der Kettenstecker sitzt links NEBEN stapel_links (statt darueber
#   wie in v1, weil "darueber" auf dem neuen Umriss die Plattenkante
#   waere) -- 4,06 mm Luft zu dessen Hof (stapel_links.flaeche[0] -
#   kette.flaeche[2] = 28,06 - 24,0 = 4,06 mm; die S.LUFT-Reissleine der
#   Ueberlapp-Probe ist 0,6 mm), Hoehe unveraendert aus v1 uebernommen
#   (0,87 .. 7,17 relativ zu pin1, s. FOOTPRINT_HOF), weil sich an der
#   SMD-Paar-Geometrie selbst nichts geaendert hat.
# * Der Leistungsstecker sitzt unten rechts, so weit vom naechsten
#   Signalstecker (stapel_rechts) weg wie es der 75x65-Umriss erlaubt,
#   und bleibt dabei mit 5,36 mm Rand zur rechten Kante (75 - 69,64)
#   klar innerhalb des Vertrags-Randmasses (RAND = 0,5 mm) und weit
#   ausserhalb der M3-Eckloch-Reichweite (7,5 mm) an allen vier Ecken
#   -- nachgerechnet in tests/test_stack_spec.py wie in v1.
STECKER_POS = {
    "stapel_links": {
        "zweck": "1x20-Buchsenreihe, Pico-Pins 1..20 (links, oben->unten)",
        "stecker": "STECKER_STAPEL",
        "footprints": (
            "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical",
        ),
        "pin1": (30.61, 2.27),
        "drehung": 0,
        "mitte": (30.61, 26.4),
        "flaeche": (28.06, 1.0, 33.16, 51.8),
    },
    "stapel_rechts": {
        "zweck": "1x20-Buchsenreihe, Pico-Pins 21..40 (rechts, unten->oben)",
        "stecker": "STECKER_STAPEL",
        "footprints": (
            "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical",
        ),
        "pin1": (48.39, 50.53),
        "drehung": 180,
        "mitte": (48.39, 26.4),
        "flaeche": (45.84, 1.0, 50.94, 51.8),
    },
    "kette": {
        "zweck": "zweipoliger Kettenstecker, SEL + GND (STECKER_KETTE)",
        "stecker": "STECKER_KETTE",
        "footprints": (
            # oben: Buchse, unten: Stiftleiste -- selber Ort
            "Connector_PinSocket_2.54mm:PinSocket_1x02_P2.54mm_Vertical_SMD_Pin1Left",
            "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left",
        ),
        "pin1": (20.59, 2.75),
        "drehung": 0,
        "mitte": (20.59, 4.02),
        "flaeche": (17.18, 0.87, 24.0, 7.17),
    },
    "leistung": {
        "zweck": "2x2-Leistungsstecker, 24 V und GND je doppelt",
        "stecker": "STECKER_LEISTUNG",
        "footprints": (
            "Connector_PinSocket_2.54mm:PinSocket_2x02_P2.54mm_Vertical_SMD",
            "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical_SMD",
        ),
        "pin1": (62.50, 45.50),
        "drehung": 0,
        "mitte": (63.77, 46.77),
        "flaeche": (57.9, 43.72, 69.64, 49.82),
    },
}

# PICO_POS gibt es in v2 NICHT mehr: es beschrieb in v1 die Lage EINES
# aufgeloeteten Pico auf GENAU EINER Platine (der Sockelplatine) -- eine
# Sonderrolle, die der Modul-Docstring oben ("v2: der Pico ist der
# Stapel") aufhebt. Jedes Modul bekommt stattdessen seinen eigenen
# Pico, gesteckt in STECKER_POS["stapel_links"]/["stapel_rechts"].
#
# Der WLAN-Antennen-Sperrbereich des Pico ist dagegen KEINE
# v1-Besonderheit, sondern eine reale Pflicht aus dem Datenblatt --
# RULING (Fix-Runde 1, 2026-09-08): er kommt zurueck in den Vertrag,
# jetzt aus stapel_links/stapel_rechts hergeleitet statt aus einem
# eigenen PICO_POS.
#
# PICO_SCHATTEN: der Umriss des STECKENDEN Pico selbst (51 x 21 mm,
# Datenblatt "Raspberry Pi Pico W Datasheet", Raspberry Pi Ltd,
# RP-008312-DS-2, Abschnitt 2 "Mechanical specification": "a single
# sided 51 mm x 21 mm x 1 mm PCB" -- geprueft per Direktzugriff auf
# https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf,
# Fix-Runde 1, 2026-09-08), zentriert auf dieselbe Achse wie die beiden
# Buchsenreihen:
#   Mitte X = Mittelpunkt der beiden Reihen-Mitten
#           = (30,61 + 48,39) / 2 = 39,5
#           -> X-Bereich 39,5 +- 21/2 = 29,0 .. 50,0
#   Mitte Y = gemeinsame Reihenmitte (beide Reihen liegen exakt auf
#             demselben Y-Bereich, s. STECKER_POS-Kommentar) = 26,4
#           -> Y-Bereich 26,4 +- 51/2 = 0,9 .. 51,9
# Nachprobe: weil PICO_SCHATTEN auf der eigenen Mitte des Reihenpaars
# sitzt (39,5), nicht auf der Plattenmitte (37,5, die der 2,0-mm-
# Verdreh-Versatz aus STECKER_POS gerade verlassen hat), liegt jede
# Reihenmitte GENAU 1,61 mm von der ihr zugewandten PICO_SCHATTEN-Kante
# entfernt: stapel_links 30,61 - 29,0 = 1,61 mm, stapel_rechts
# 50,0 - 48,39 = 1,61 mm. Das ist kein Zufall, sondern die
# Datenblattangabe selbst nachgerechnet: Boardbreite 21 mm minus
# Reihenabstand 17,78 mm, halbiert -> (21 - 17,78) / 2 = 1,61 mm Rand
# je Seite zwischen Kontaktachse und Pico-Kante.
PICO_SCHATTEN = (29.0, 0.9, 50.0, 51.9)

# ANTENNE_FREI: Teilstreifen von PICO_SCHATTEN am Pico-Ende der
# Onboard-Antenne. Laut Datenblatt (Abschnitt 2, "Mechanical
# specification"): "a ... PCB with a micro USB port overhanging the
# top edge, and dual castellated/through-hole pins around the two long
# edges. The onboard wireless antenna is located on the bottom edge."
# -- die Antenne sitzt also am ENDE gegenueber der USB-Buchse, entlang
# der Pinreihen. Pico-Pin 1 (stapel_links, s. STECKER_POS) liegt beim
# echten Pico neben der USB-Buchse; das Antennen-Ende ist deshalb das
# GEGENUEBERLIEGENDE Ende der Reihen, in unseren Platinenkoordinaten
# also das obere Ende von PICO_SCHATTEN (y = 51.9), nicht das untere
# (y = 0.9, wo Pin 1 sitzt).
#
# Streifentiefe: Abschnitt 2.2.1 "Keep-out area": "There is a cutout
# for the antenna (14 mm x 9 mm)." -- 9,0 mm ist die Tiefe senkrecht
# zur Kante (die 14 mm sind die Breite ENTLANG der Kante, schmaler als
# die vollen 21 mm PICO_SCHATTEN-Breite; dieser Vertrag rundet
# grosszuegig auf die volle Breite auf statt ein schmaleres
# Teilrechteck zu fuehren -- dieselbe bewusste Uebervorsicht wie beim
# quadratischen statt kreisrunden M3_KEEPOUT oben). Direkt aus der
# offiziellen PDF-Quelle gelesen (nicht aus einer Sekundaerquelle
# zitiert), s. Zeile oben bei PICO_SCHATTEN -- KEIN konservativer
# Default noetig.
ANTENNE_FREI = (29.0, 42.9, 50.0, 51.9)

# Semantik, bindend fuer die Layout-Aufgaben: in ANTENNE_FREI darf auf
# der Seite, auf der der Pico steckt, weder Kupfer noch ein Bauteil
# liegen (keine Leiterbahn, kein Loetpad, kein Footprint-Hof) -- sonst
# verstimmt es die Antenne (Datenblatt: "If anything is placed close
# to the antenna (in any dimension) the effectiveness of the antenna
# is reduced."). Auf der GEGENUEBERLIEGENDEN Seite der Platine gilt die
# Regel nicht (die Antenne sitzt auf dem aufgesteckten Pico selbst,
# nicht auf unserer Platine) -- eine Folgeaufgabe traegt diese
# Unterscheidung in AUFLAGEN/LAYOUT_AUFLAGEN nach, sobald ein
# Modul-Layout sie wirklich braucht.

# --- Wieviel Platz bleibt uebrig ------------------------------------
# Ein Vertrag, der die Stecker so hinlegt, dass kein Modul mehr
# hineinpasst, ist wertlos. Untergrenze, hergeleitet statt geraten:
#
# MODUL_HOF_SUMME_MM2 ist die Summe der Bauteil-Hoefe des heute
# anspruchsvollsten Moduls (Motormodul, hardware/kicad/motor/
# Motormodul.kicad_sch, 43 Bauteile) OHNE die Vertragsstecker (in v1
# drei, in v2 vier -- die Zahl selbst ist unveraendert aus v1
# uebernommen, s. Aufgabe 2, weil ihre Herleitung -- Motormodul minus
# Vertragsstecker -- unabhaengig davon gilt, wie viele Vertragsstecker
# es gerade sind) -- gemessen aus denselben echten Footprints wie
# FOOTPRINT_HOF oben. tools/platzprobe_v2.py rechnet fuer Aufgabe 1
# unabhaengig davon dieselbe Motor-Nutzlast neu nach (935,3 mm2 vor
# Reserve) und bestaetigt damit dieselbe Groessenordnung, statt sie nur
# abzuschreiben.
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
# SOCKEL_HOF_SUMME_MM2 war in v1 dieselbe Rechnung fuer die
# Sockelplatine, die zusaetzlich den Pico und dessen Antennen-
# Sperrbereich verlor: ihre eigenen acht Bauteile (J1, D1, C3, C1, C2,
# R1, R2, U2 -- ohne die drei Vertragsstecker und ohne den Pico selbst)
# summierten sich auf 437,8 mm2 Hof. Der Wert bleibt hier stehen (kein
# Beleg wird geloescht), ist aber in v2 UNBENUTZT: es gibt keine
# Sockelplatine mehr, gegen die er noch etwas pruefen koennte (s.
# Modul-Docstring, "der Pico ist der Stapel") -- die zugehoerige
# Pruefung ("Sockel: ...") ist deshalb aus
# tests/test_stack_spec.py entfernt, nicht abgeschwaecht.
SOCKEL_HOF_SUMME_MM2 = 437.8
# Die hier festgelegte Anordnung laesst einem Modul 3013,0 mm2 am
# Stueck (78,5 % der Platine), groesstes freies Rechteck 1852,2 mm2
# -- Faktor 1,77 ueber der Untergrenze. Bis Aufgabe 5e waren es
# 3077,7 mm2; die 64,7 mm2 Unterschied sind der Preis der breiteren
# SMD-Hoefe. Der Sockelplatine bleiben 1711,5 mm2 (vorher 1776,2),
# gegen 773,5 mm2 Bedarf. Nachgerechnet in tests/test_stack_spec.py
# mit tools/pcb/geometry.freie_flaeche().

# --- Verdreht aufgesteckt --------------------------------------------
# M3_HOLES ist punktsymmetrisch zur Platinenmitte (v2: (4|4) und
# (71|61) tauschen unter einer 180-Grad-Drehung die Plaetze, (4|61) und
# (71|4) ebenso). Ein Modul laesst sich also seitenrichtig, aber um
# 180 Grad verdreht auf die Abstandsbolzen schrauben. Auf den beiden
# Stapelreihen wuerde das Pico-Pin 1 auf Pico-Pin 40 legen -- VBUS auf
# FLASH_TX -- und den Stapel zerstoeren. Der Umriss ist Vertrag und
# laesst sich nicht unsymmetrisch machen; die Steckerlage dagegen
# schon, und genau dafuer liegen die vier Steckerplaetze oben BEWUSST
# UNSYMMETRISCH:
#
#   VERDREHT(...) der vier Flaechen ergibt
#     stapel_links  -> (41.84, 13.2, 46.94, 64.0)
#     stapel_rechts -> (24.06, 13.2, 29.16, 64.0)
#     kette         -> (51.0, 57.83, 57.82, 64.13)
#     leistung      -> (5.36, 15.18, 17.1, 21.28)
#
#   Keine dieser vier Flaechen deckt sich mit der eines Steckers.
#   Entscheidend ist aber nicht die Flaeche, sondern das Raster: der
#   kleinste Abstand zwischen einem verdrehten Kontakt und irgendeinem
#   Kontakt betraegt 4,031 mm (v1, bis Aufgabe 5e: 2,755 mm). Der
#   groesste Teil davon kommt NICHT aus dem Y-Versatz (der ist beim
#   2,54-mm-Raster niemals mehr als die Haelfte, 1,27 mm), sondern aus
#   dem bewussten seitlichen Versatz von stapel_links/rechts um 2,0 mm
#   aus der Plattenmitte (s. Kommentar bei STECKER_POS,
#   "stapel_links"/"stapel_rechts": 2 x 2,0 mm X-Versatz zwischen einer
#   Reihe und dem verdrehten Abbild der jeweils anderen). Das ist mehr
#   als das halbe Raster (1,27 mm), das ein Stift braucht, um in einen
#   Buchsenkontakt zu finden -- ein verdreht aufgesetztes Modul steckt
#   NIRGENDS. Es bleibt tot, statt kaputtzugehen.
#   tests/test_stack_spec.py rechnet beides nach, damit eine kuenftige
#   Verschiebung das nicht stillschweigend aufhebt.
#
# Tot ist besser als kaputt, aber nicht gut genug: sichtbar wird der
# Fehler dadurch nicht. Die zugehoerige Layout-Auflage steht in
# AUFLAGEN unten (Pin-1-Kennzeichnung, kein freiliegendes Kupfer in den
# vier verdrehten Flaechen).
VERDREHT_MINDESTABSTAND_MM = 4.031   # gerechnet, s. Test

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
# --- Wo die Stifte eines verdreht aufgesteckten Aufbaus landen ------
# Praezisierung der Kupferklausel in LAYOUT_AUFLAGEN (RULING 2026-09-01,
# waehrend Aufgabe 7). Die alte Fassung verbot freiliegendes Kupfer in
# den drei GANZEN Flaechen VERDREHT(STECKER_POS[...]["flaeche"]). Das
# war in sich unerfuellbar: die eigenen Loetpads des Stapelsteckers
# ragen 0,17 mm in VERDREHT(leistung) hinein -- der Vertrag verletzte
# seine eigene Auflage auf jeder Platine, gebaut oder nicht.
#
# Physisch drueckt aber keine Flaeche, sondern es druecken STIFTE, und
# die landen an ausrechenbaren PUNKTEN: an VERDREHT() jedes einzelnen
# Kontakts der (v2: vier) Steckerplaetze -- weiterhin 46 Punkte
# (20 + 20 + 2 + 4, s. STECKER_POS). Der bestehende Vertragstest
# sichert bereits, dass jeder Landepunkt mindestens
# VERDREHT_MINDESTABSTAND_MM (v2: 4,031 mm) von jedem Kontakt entfernt
# bleibt; bis zur KUPFERKANTE des naechsten Steckerpads sind es
# mindestens ebenso viel abzueglich des Padradius (v1: 1,90 mm bei
# 0,85 mm Padradius -- fuer v2 nicht neu nachgerechnet, da
# LANDE_SPERRRADIUS unten konservativ unter dem v1-Wert bleibt). Die
# Regel wird
# deshalb: kein freiliegendes Kupfer naeher als LANDE_SPERRRADIUS an
# einem Landepunkt. 1,5 mm lassen dem stumpfen Stiftende (0,64 mm
# Vierkant, halbe Diagonale 0,45 mm) rund 1 mm Montagetoleranz.
# tools/pcb/steckerprobe.py misst das an der gebauten Platine nach.
LANDE_SPERRRADIUS = 1.5    # mm um jeden Landepunkt, bis zur Kupferkante


def LANDEPUNKTE_VERDREHT():
    """Alle 46 Punkte, an denen ein verdreht aufgesteckter Aufbau mit
    seinen Stiften auf der Oberseite dieser Platine aufsetzt."""
    aus = []
    for eintrag in STECKER_POS.values():
        lagen = PAD_LAGEN(eintrag["footprints"][0], eintrag["pin1"],
                          eintrag["drehung"])
        for x, y in lagen.values():
            aus.append((round(BOARD_W - x, 3), round(BOARD_H - y, 3)))
    return tuple(aus)


# RULING (2026-09-01, Aufgabe 7) zur Zugentlastungs-Auflage unten: es
# gilt das FUEGEVERFAHREN -- die Platinen werden ERST gesteckt und DANN
# auf die Abstandsbolzen geschraubt. Begruendung: null Platinenflaeche
# und null Bauteile, und nach dem Verschrauben tragen die M3-Bolzen
# jede Steck- und Zugkraft; die Loetstellen sehen nur den einen
# kontrollierten Fuegevorgang. Zusaetzliche Befestigungspunkte je
# Stecker haetten auf 64 x 60 mm zweimal vier Bohrungen gekostet --
# mitten in den Flaechen, die den Modulen gehoeren. Kosten wenn
# falsch: die Regel steht im Vertragsdokument, eine Montageanweisung,
# kein Kupfer -- jederzeit aenderbar.
MONTAGE_REGEL = (
    "ERST stecken, DANN auf die Abstandsbolzen schrauben. Die "
    "Zugentlastung der SMD-Steckerpaare ist die Verschraubung des "
    "Stapels; ein bereits verschraubter Stapel darf nicht "
    "auseinandergezogen werden, ohne zuerst die Bolzen zu loesen."
)

LAYOUT_AUFLAGEN = (
    "Jede Platine traegt neben Pin 1 des Stapelsteckers eine "
    "Kennzeichnung im Bestueckungsdruck (Dreieck plus Text \"1\") und "
    "an der Klemmenkante (untere Kante, y = BOARD_H) die "
    "Beschriftung \"KLEMMEN\". Grund: das "
    "M3-Lochbild ist punktsymmetrisch, ein Modul laesst sich also um "
    "180 Grad verdreht anschrauben. Die Steckerlage (STECKER_POS) ist "
    "bewusst so unsymmetrisch, dass dann kein einziger Stift in einen "
    "Buchsenkontakt findet -- das verhindert den Schaden, macht den "
    "Fehler aber nicht sichtbar. Ausserdem darf auf der OBERSEITE "
    "eines Moduls im Umkreis von LANDE_SPERRRADIUS um jeden der "
    "Punkte aus LANDEPUNKTE_VERDREHT() kein freiliegendes Kupfer "
    "liegen (keine Testpunkte, keine offenen Pads, keine unbedeckten "
    "Durchkontaktierungen): genau dort setzen die "
    "Stifte eines verdreht aufgesteckten Aufbaus auf. Die "
    "Sockelplatine ist von dieser Kupferregel ausgenommen -- sie "
    "sitzt zuoberst, auf ihre Oberseite drueckt nie ein Stift.",

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


def TYPCODE_WIDERSTAENDE(typcode):
    """(R_ID0, R_ID1) in Ohm fuer einen Modultyp-Code.

    Kodierung, hiermit festgelegt: das NIEDRIGE Nibble waehlt die
    Stufe des ID0-Kennwiderstands (R100), das HOHE Nibble die des
    ID1-Kennwiderstands (R101). Stufe 0 ist 0 Ohm (Bruecke) --
    deshalb ist Typ 0x00 unzulaessig: er ist von einer leeren
    Platine nicht zu unterscheiden (beide Teiler lesen 0).

    Beispiel Motor (0x01): R100 = 680 Ohm, R101 = Bruecke.
    """
    if typcode not in MODULTYPEN:
        raise ValueError("unbekannter Modultyp 0x%02x" % typcode)
    lo, hi = typcode & 0x0F, (typcode >> 4) & 0x0F
    return ID_WIDERSTAENDE[lo], ID_WIDERSTAENDE[hi]

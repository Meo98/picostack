"""Prueft den Vertrag. Ohne KiCad, ohne Hardware."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "pcb"))
import stack_spec as S
import geometry          # nur Geometrie, kein KiCad -- s. dortiger Docstring

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- v2: der Pico ist der Stapel (Aufgabe 2, TDD Schritt 1) ----------
# Fuenf Pruefungen, woertlich aus dem Aufgabenzettel uebernommen, BEVOR
# der Vertrag geaendert wird -- sie muessen zuerst rot sehen (S.
# STECKER_POS["stapel"] existiert noch, S.VERTRAG_VERSION gibt es noch
# nicht), sonst pruefen sie nichts.
# v2.1 (Aufgabe B, 2026-09-10): der Umriss waechst, M3_HOLES werden
# beweglich, RANDPADS wandern auf F.Cu -- STECKER_POS/PIN_ROLLE (der
# eigentliche Stapelvertrag) bleiben unangetastet. Bump auf 3, s.
# stack_spec.py-Moduldocstring, Abschnitt "v2.1: bedienbares Layout".
check("Vertragsversion 3", getattr(S, "VERTRAG_VERSION", 1), 3)
check("Stapelreihen in Pico-Geometrie",
      round(abs(S.STECKER_POS["stapel_links"]["mitte"][0]
                - S.STECKER_POS["stapel_rechts"]["mitte"][0]), 2), 17.78)
check("alter 2x20-Block ist weg", "stapel" in S.STECKER_POS, False)
check("jeder freie Pin hat genau ein Randpad",
      sorted(p for p, _, _ in S.RANDPADS if S.PIN_ROLLE.get(p) == "frei"),
      sorted(p for p, r in S.PIN_ROLLE.items() if r == "frei"))
check("Versorgungszusagen vorhanden",
      S.VERSORGUNG["schutz_drain_an"], "PWR_IN")

# --- Fix-Runde 1 (Task-5-Review, 2026-09-08): VSYS ist v2-belegbar ---
# BEFUND: v1 verbot jede Einspeisung auf VSYS (Pin 39), weil niemand sie
# trieb -- s. NICHT_BELEGBAR[39]-Kommentar (Stand vor dieser Aenderung).
# Die v2-VERSORGUNG-Zusage (VERSORGUNG["vsys_diode"] == True) verlangt
# aber genau das Gegenteil: JEDE Versorgungszelle (tools/sch/
# versorgung.py, D91) speist VSYS ueber eine Entkopplungsdiode. Ohne
# diesen Vertragswechsel haette der generierte Schaltplan (motormodul.py)
# eine Diode auf einen Pin gelegt, den der Vertrag als "nicht belegbar"
# fuehrt -- ein echter Widerspruch, der als isolated_pin_label-ERC-
# Warnung sichtbar wurde (VSYS erreichte nie ein zweites Bauteil).
# Dieser Check war vor der Aenderung an NICHT_BELEGBAR ROT (2026-09-08):
# S.IST_BELEGBAR(39) lieferte False.
check("VSYS ist v2-belegbar (Einspeisung ueber Schottky)",
      S.IST_BELEGBAR(39), True)
# Die direkte, ungeschuetzte Verbindung bleibt trotzdem verboten -- nur
# der Weg UEBER die Entkopplungsdiode der Versorgungszelle ist erlaubt.
# Das steht jetzt als Zusatz-Satz bei der VERSORGUNG-Zusage im
# Vertragstext (s. tools/stack_spec.py, VERSORGUNG-Kommentar).
check("VBUS bleibt nicht belegbar (unveraendert)",
      S.IST_BELEGBAR(40), False)
check("RUN bleibt nicht belegbar (unveraendert)",
      S.IST_BELEGBAR(30), False)
check("3V3_EN bleibt nicht belegbar (unveraendert)",
      S.IST_BELEGBAR(37), False)
check("ADC_VREF bleibt nicht belegbar (unveraendert)",
      S.IST_BELEGBAR(35), False)

# --- Umriss und Lochbild ---
# v2.1 (Aufgabe B): 75x65 -> 82x73, hergeleitet in
# tools/platzprobe_v2_1.py (Rot-Nachweis + Kandidatenrechnung in
# task-v21a-report.md, Abschnitt 9). Das Lochbild folgt derselben
# 4-mm-Randlogik wie v1/v2, jetzt auf das neue Mass angewendet:
# 82-2*4=74, 73-2*4=65.
check("Breite", S.BOARD_W, 82.0)
check("Hoehe", S.BOARD_H, 73.0)
check("vier M3", len(S.M3_HOLES), 4)
check("Lochbild 74 mm", S.M3_HOLES[2][0] - S.M3_HOLES[0][0], 74.0)
check("Lochbild 65 mm", S.M3_HOLES[1][1] - S.M3_HOLES[0][1], 65.0)

# Alle vier Ecken einzeln, nicht nur zwei Differenzen: sonst darf die
# vierte Bohrung irgendwo liegen und der Test merkt es nicht.
check("Lochbild vollstaendig", sorted(S.M3_HOLES),
      [(4.0, 4.0), (4.0, 69.0), (78.0, 4.0), (78.0, 69.0)])

# --- v2.1: M3_HOLES_FUER() ist eine Verallgemeinerung, keine
# Ersetzung der alten Herleitung -----------------------------------
# ROT-NACHWEIS DER DERIVATION (bindend laut Aufgabenzettel): bei den
# ALTEN Massen (75x65) muss die neue Funktion exakt die vier alten,
# vorher fest eingetragenen M3_HOLES reproduzieren. Waere das nicht
# der Fall, haette die "Verallgemeinerung" in Wirklichkeit die
# Herleitung geaendert, nicht nur parametrisiert.
check("M3_HOLES_FUER(75,65) reproduziert das alte v2-Lochbild",
      S.M3_HOLES_FUER(75.0, 65.0),
      [(4.0, 4.0), (4.0, 61.0), (71.0, 4.0), (71.0, 61.0)])
check("M3_HOLES ist M3_HOLES_FUER(BOARD_W, BOARD_H)",
      S.M3_HOLES, S.M3_HOLES_FUER(S.BOARD_W, S.BOARD_H))

# --- v2.1: die beiden neuen Pflichtzonen ----------------------------
# RANDPAD_ZONE: woertlich aus task-v21a-report.md, Abschnitt 9
# uebernommen (die vom Controller korrigierte, massgebliche Fassung mit
# beweglichem Lochbild). KLEMMENZONE: BREITE seit Aufgabe C1 auf
# 46,40 mm korrigiert (x1 = 70,20 statt 58,20) -- die urspruengliche
# 34,40-mm-Herleitung pruefte nie gegen LANDEPUNKTE_VERDREHT() und war
# fuer Dimmer4 (vier Klemmen) arithmetisch unerfuellbar, s. Herleitung
# und Rot-Nachweis bei stack_spec.KLEMMENZONE.
check("KLEMMENZONE", S.KLEMMENZONE, (23.80, 60.80, 70.20, 73.00))
check("RANDPAD_ZONE", S.RANDPAD_ZONE, (75.60, 8.56, 79.60, 64.44))


def _ueberlappt_rechteck(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


# R1: kein Klemmen-Hof schneidet PICO_SCHATTEN -- hier auf Zonenebene
# geprueft (die tatsaechlichen Klemmen-Hoefe kommen erst in Aufgabe C,
# aber wenn schon die ZONE PICO_SCHATTEN schneidet, kann keine
# Platzierung darin die Regel je einhalten).
check("R1: KLEMMENZONE schneidet PICO_SCHATTEN nicht",
      _ueberlappt_rechteck(S.KLEMMENZONE, S.PICO_SCHATTEN), False)

# R5: RANDPAD_ZONE haelt >= 2,0 mm Kupferabstand zur rechten Kante.
check("R5: RANDPAD_ZONE haelt Mindestabstand zur rechten Kante",
      S.BOARD_W - S.RANDPAD_ZONE[2] >= S.LAYOUT_REGELN["R5"]["mindestabstand_mm"],
      True)

# RANDPAD_ZONE darf keines der (jetzt beweglichen) M3-Freihalte-
# quadrate schneiden -- das war der eigentliche Engpass von Aufgabe A
# (die Zone muss zwischen den beiden rechten Loechern hindurchpassen).
_m3_r = S.M3_KEEPOUT / 2.0
for _hx, _hy in S.M3_HOLES:
    _quad = (_hx - _m3_r, _hy - _m3_r, _hx + _m3_r, _hy + _m3_r)
    check("RANDPAD_ZONE frei von M3 (%s|%s)" % (_hx, _hy),
          _ueberlappt_rechteck(S.RANDPAD_ZONE, _quad), False)
    check("KLEMMENZONE frei von M3 (%s|%s)" % (_hx, _hy),
          _ueberlappt_rechteck(S.KLEMMENZONE, _quad), False)

# Masse, die die Spezifikation zusichert und die bisher niemand prueft.
check("Eckenradius", S.CORNER_R, 3.0)
check("M3-Bohrdurchmesser", S.M3_DRILL, 3.2)
check("Stapelabstand", S.STAPEL_ABSTAND, 13.6)

# Der Spalt G zwischen zwei Platinen IST die Bauhoehe der Abstands-
# bolzen, die den Stapel tragen. Er muss deshalb ein handelsuebliches
# Mass sein -- ein rechnerisch schoener Wert wie 11,90 mm ist als
# Bauteil nicht zu kaufen und faellt erst beim Gehaeuse auf, lange
# nachdem die Platinen gefertigt sind. Genau so ist es zweimal
# passiert: 13,0 mm ergab 11,40 mm, 13,5 mm ergab 11,90 mm, beides
# keine Katalogmasse; erst 13,6 mm trifft mit 12,00 mm eines. Diese
# Pruefung haelt den Grund fest, damit die naechste Aenderung von
# STAPEL_ABSTAND nicht wieder daran vorbeigeht.
BOLZEN_KATALOG = (10.0, 11.0, 12.0, 15.0, 16.0, 20.0)  # mm, gaengige
# M3-Distanzbolzen (Sechskant, Messing) -- die Reihe, die jeder
# Haendler fuehrt. Kein Datenblattwert, sondern eine Sortimentsangabe:
# wer einen Bolzen ausserhalb dieser Reihe braucht, soll das bewusst
# entscheiden und die Reihe hier erweitern.
check("Spalt entspricht einem handelsueblichen Abstandsbolzen",
      round(S.STAPEL_ABSTAND - S.PLATINE_DICKE, 2) in BOLZEN_KATALOG, True)

# --- Steckerbelegung ---
check("40 Pins beschrieben", len(S.PIN_ROLLE), 40)

# Jede reservierte Rolle kommt genau einmal vor. Zwei Pins mit
# derselben Aufgabe waeren ein stiller Kurzschluss im Vertrag.
for rolle in S.RESERVIERT:
    n = sum(1 for r in S.PIN_ROLLE.values() if r == rolle)
    check("Rolle %s genau einmal" % rolle, n, 1)

# Reservierte Rollen duerfen nicht auf Versorgungspins liegen.
for pin, rolle in S.PIN_ROLLE.items():
    if rolle in S.RESERVIERT:
        check("Pin %d ist kein Versorgungspin" % pin,
              S.IST_VERSORGUNG(pin), False)

# --- Stapelstecker/Kettenstecker (seit 2026-08-31) -------------------
# SEL laeuft seit der Umstellung auf den Stapelstecker (Buchse mit
# durchgehendem Stift) nicht mehr ueber den 2x20-Stecker, sondern ueber
# einen eigenen Kettenstecker -- die Rolle "SEL" darf in
# RESERVIERT/PIN_ROLLE nicht mehr auftauchen.
check("SEL nicht mehr reserviert", "SEL" in S.RESERVIERT, False)
check("SEL steht in keiner Pin-Rolle mehr",
      "SEL" in S.PIN_ROLLE.values(), False)

# Pin 4 (GP2) war kurz "frei" (erste Runde), ist seit Befund 2
# (Aufgabe-4-Fix-1, 2026-08-31) aber wieder eine echte Vertragsrolle:
# SEL_OUT, der Pico-Pin, der die Auswahlkette treibt. Grund: die lokale,
# unreservierte Verdrahtung auf GP8 (Pin 11) kollidierte, sobald Pin 11
# selbst zu einem durchgereichten freien GPIO wurde (stack_spec selbst
# bleibt unveraendert dafuer verantwortlich, dass GP8 wieder "frei" ist,
# s. Pruefung unten).
check("Pin 4 (GP2) traegt SEL_OUT", S.PIN_ROLLE[4], "SEL_OUT")
check("SEL_OUT reserviert", "SEL_OUT" in S.RESERVIERT, True)
check("SEL_OUT kein Versorgungspin", S.IST_VERSORGUNG(4), False)
check("Pin 11 (GP8) frei (kein lokaler SEL-Treiber mehr)",
      S.PIN_ROLLE[11], "frei")

# Der Kettenstecker traegt genau SEL und eine GND, sonst nichts.
check("Kettenstecker zweipolig", len(S.STECKER_KETTE["pins"]), 2)
check("Kettenstecker traegt SEL",
      "SEL" in S.STECKER_KETTE["pins"].values(), True)
check("Kettenstecker traegt GND",
      "GND" in S.STECKER_KETTE["pins"].values(), True)

# --- Kein Steckerpaar mit zwei bedrahteten Haelften ------------------
# Der Konstruktionsfehler, den Aufgabe 5e behoben hat, und der Grund,
# warum es diese Pruefung gibt:
#
#   Ketten- und Leistungsstecker bestehen aus ZWEI Bauteilen (Buchse
#   oben, Stiftleiste unten). Beide muessen am SELBEN Ort sitzen, sonst
#   trifft der Stift an der Unterseite von Modul N die Buchse an der
#   Oberseite von Modul N+1 nicht -- alle Platinen sind gleich, und
#   eine Verschiebung hebt sich zwischen zwei gleichen Platinen nicht
#   auf. Zwei BEDRAHTETE Bauteile am selben Ort brauchten aber
#   dieselben Bohrungen, und dieselbe Bohrung ist derselbe Leiter.
#   Das ist entweder unbaubar (zwei Bauteile, ein Loch) oder, wenn man
#   es doch verbindet, ein durchgehender Kontakt -- und der macht beim
#   Kettenstecker SEL_IN und SEL_OUT zu einem Netz und das
#   Schieberegister aus tools/kette.py sinnlos.
#
# Bis zum 2026-08-31 stand genau das im Vertrag: beide Stecker
# "Buchse oben / Stiftleiste unten", beide bedrahtet, je eine
# gemeinsame Flaeche. Diese Pruefung haette das rot gemeldet.
for _name, _st in (("Stapelstecker", S.STECKER_STAPEL),
                   ("Kettenstecker", S.STECKER_KETTE),
                   ("Leistungsstecker", S.STECKER_LEISTUNG)):
    # Jeder Stecker sagt maschinenlesbar, was er ist.
    for _feld in ("durchgehend", "montage_oben", "montage_unten",
                  "haelften_gleiche_netze"):
        check("%s: Feld %s vorhanden" % (_name, _feld), _feld in _st, True)
    check("%s: Montage oben ist THT oder SMD" % _name,
          _st["montage_oben"] in ("THT", "SMD"), True)
    check("%s: Montage unten ist THT oder SMD" % _name,
          _st["montage_unten"] in ("THT", "SMD"), True)
    if _st["durchgehend"]:
        # EIN Bauteil, ein Leiter durch beide Ebenen: dann MUESSEN
        # beide Seiten dasselbe Netz fuehren. Sonst waere die
        # Verbindung, die das Bauteil herstellt, ein Kurzschluss.
        check("%s: durchgehend nur bei gleichen Netzen" % _name,
              _st["haelften_gleiche_netze"], True)
    else:
        # Zwei Bauteile am selben Ort -> hoechstens eines darf
        # bedrahtet sein, und weil die Bohrungen des bedrahteten genau
        # dort laegen, wo die Kontakte des anderen liegen muessen:
        # gar keines.
        check("%s: kein Paar mit zwei bedrahteten Haelften" % _name,
              (_st["montage_oben"], _st["montage_unten"]) == ("THT", "THT"),
              False)
        check("%s: beide Haelften oberflaechenmontiert" % _name,
              (_st["montage_oben"], _st["montage_unten"]) == ("SMD", "SMD"),
              True)

# Die Kette darf NIE ein durchgehender Kontakt werden -- das ist die
# inhaltliche Aussage hinter der Bauform, und sie steht hier noch
# einmal fuer sich, damit sie nicht mit der Bauteilwahl verschwindet.
check("Kettenstecker ist nicht durchgehend",
      S.STECKER_KETTE["durchgehend"], False)
check("Kettenstecker fuehrt oben und unten verschiedene Netze",
      S.STECKER_KETTE["haelften_gleiche_netze"], False)

# --- Jede Steckerhaelfte hat eine Bauteilnummer ----------------------
# "Beide Platinen bestueckt bestellbar" ist ein erklaertes Ziel des
# Projekts (docs/superpowers/specs/2026-08-28-picostack-design.md). Es
# scheitert an EINEM leeren Feld: wer eine Haelfte nicht bestellen
# kann, kann die Platine nicht bestueckt bestellen. Bis Aufgabe 5g
# waren drei der sechs Felder leer (Buchse 1x2, Stift 1x2, Buchse 2x2)
# -- diese Pruefung haelt fest, dass sie es nicht wieder werden.
#
# Sie prueft absichtlich NUR "nicht leer" und "sieht aus wie eine
# LCSC-Nummer", nicht die konkrete Nummer: welches Teil es ist, darf
# sich aendern (Abkuendigung, Lagerbestand), dass es EINES gibt, nicht.
#
# Der Stapelstecker (v2) ist davon ausgenommen -- RULING (Fix-Runde 1,
# 2026-09-08): kein 1x20/1x10-Teil mit offener Produktseite gefunden,
# die Felder bleiben deshalb bewusst leer bis zur Fertigungs-Sichtung
# (Aufgabe 9), s. Kommentar bei STECKER_STAPEL. Das ist eine
# dokumentierte Luecke, keine vergessene -- die Pruefung unten haelt
# genau DAS fest (explizit None, nicht irgendein falscher Wert).
for _name, _st in (("Kettenstecker", S.STECKER_KETTE),
                   ("Leistungsstecker", S.STECKER_LEISTUNG)):
    for _seite in ("buchse_lcsc", "stift_lcsc"):
        _nr = _st[_seite]
        check("%s: %s ist belegt" % (_name, _seite), bool(_nr), True)
        check("%s: %s sieht aus wie eine LCSC-Nummer" % (_name, _seite),
              _nr.startswith("C") and _nr[1:].isdigit(), True)

for _seite in ("buchse_lcsc", "stift_lcsc", "buchse_mpn", "stift_mpn"):
    check("Stapelstecker: %s bewusst offen (Sourcing-Ruling, T9)" % _seite,
          S.STECKER_STAPEL[_seite], None)

# Der Leistungsstecker traegt Motorstrom. Sein Nennstrom je Kontakt
# muss mindestens so gross sein wie der der Buchse des Signalsteckers
# -- sonst waere ausgerechnet der Leistungspfad der schwaechere.
check("Leistungsstecker nicht schwaecher als der Signalstecker",
      S.STECKER_LEISTUNG["strom_pro_kontakt_a"]
      >= S.STECKER_STAPEL["strom_pro_kontakt_a"], True)

# Die Einstecktiefe wird aus STAPEL_ABSTAND und den Steckermassen
# nachgerechnet (nicht nur die Zahl 13.0 abgefragt) -- das faengt den
# naechsten Denkfehler ab: wer STAPEL_ABSTAND aendert, ohne die
# Steckermasse mitzudenken, oder umgekehrt.
MINDEST_EINSTECKTIEFE = 2.0  # mm, konservativ unter dem knappsten
# belegten Fall (Ketten- und Leistungsstecker, rechnerisch je 5,00 mm
# bei 13,6 mm, hardware/bauteile-1b.md Beleg 13/14) -- faengt Rechen-
# oder Bauteiländerungen ab, ohne die exakte Zahl selbst zu
# duplizieren. Die Schwelle bleibt bei 2,0 mm, obwohl der Ist-Wert
# sich dreimal geaendert hat (3,1 -> 5,60 -> 5,10 -> 5,00 mm): sie ist die
# Reissleine, nicht die Messlatte.
check("Stapelstecker-Einstecktiefe ueber Mindestschwelle",
      S.EINSTECKTIEFE_STAPEL() > MINDEST_EINSTECKTIEFE, True)
check("Kettenstecker-Einstecktiefe ueber Mindestschwelle",
      S.EINSTECKTIEFE_KETTE() > MINDEST_EINSTECKTIEFE, True)
check("Leistungsstecker-Einstecktiefe ueber Mindestschwelle",
      S.EINSTECKTIEFE_LEISTUNG() > MINDEST_EINSTECKTIEFE, True)

# Ein Stift kann nicht tiefer stecken als er lang ist -- eine
# Einstecktiefe groesser als die freie Steckstiftlaenge waere eine
# Rechnung, die sich selbst nicht mehr glaubt.
for _n, _st in (("Kette", S.STECKER_KETTE), ("Leistung", S.STECKER_LEISTUNG)):
    check("%s: Einstecktiefe nicht groesser als der Stift" % _n,
          S.EINSTECKTIEFE_SMD_PAAR(_st) <= _st["stiftlaenge_mm"], True)
    # Und der Isolierkoerper des Stifts muss ueber der Buchsenoberkante
    # bleiben, sonst stossen die Kunststoffe aneinander, bevor die
    # Abstandsbolzen sitzen -- die Platinen liessen sich dann nicht
    # mehr flach verschrauben. Das ist der engste Punkt des Stapels und
    # der Grund, warum STAPEL_ABSTAND nicht unter 12,6 mm darf. Seit
    # Aufgabe 5g und der Bolzenkorrektur (13,0 -> 13,5 -> 13,6 mm) sind es 1,00 statt
    # 0,40 mm; die Pruefung bleibt trotzdem "> 0" und nicht "> 0,9" --
    # sie soll den Vorzeichenwechsel fangen, nicht den heutigen Wert
    # festschreiben.
    check("%s: Luft zwischen Stiftkoerper und Buchse" % _n,
          S.LUFT_STIFTKOERPER(_st) > 0, True)

# Ueber den Schraubklemmen (urspruenglicher Grund fuer den alten
# 15,0-mm-Wert) und dem K7805 (hoechstes denkbares Bauteil im Spalt,
# falls je ein Modul es nutzt) muss im Spalt noch Luft bleiben.
# Der Stift des Stapelsteckers darf nicht am Grund seiner Buchse
# anschlagen, bevor die Platinen auf Abstand sind: seine Einstecktiefe
# muss kleiner bleiben als die Buchse tief ist. Das ist die Reserve,
# die beim SENKEN von STAPEL_ABSTAND als erste verschwaende (bei
# 13,6 mm: 8,50 - 7,36 = 1,14 mm).
check("Stapelstift schlaegt nicht am Buchsengrund an",
      S.EINSTECKTIEFE_STAPEL() < S.STECKER_STAPEL["gehaeusehoehe_mm"], True)

check("Ueber der Klemme bleibt Luft im Spalt",
      (S.STAPEL_ABSTAND - S.PLATINE_DICKE - S.KLEMME_HOEHE_MM) > 0, True)
check("Ueber dem K7805 bleibt Luft im Spalt",
      (S.STAPEL_ABSTAND - S.PLATINE_DICKE - S.K7805_HOEHE_MM) > 0, True)

# --- Modultypen ---
check("Motor hat Nummer", "Motor" in
      {t["name"] for t in S.MODULTYPEN.values()}, True)
# Nummern ab 0x80 bleiben fremden Modulen vorbehalten; wer sie
# selbst belegt, nimmt der Community den Platz weg.
for nr in S.MODULTYPEN:
    check("Nummer 0x%02X unter 0x80" % nr, nr < 0x80, True)

# --- Kennwiderstaende ---
# Zwei Teiler zu je 16 Stufen ergeben 256 Nummern. Die Stufen muessen
# sich im ADC sicher unterscheiden lassen.
stufen = sorted(S.ID_WIDERSTAENDE)
check("16 Stufen", len(stufen), 16)
verhaeltnisse = [S.ID_ANTEIL(r) for r in stufen]
abstaende = [b - a for a, b in zip(verhaeltnisse, verhaeltnisse[1:])]
check("Stufen mindestens 3 % auseinander", min(abstaende) > 0.03, True)

# --- Steckerkoordinaten (seit 2026-08-31, Aufgabe 5c) ----------------
# Der Vertrag legte bisher Rollen und Bauhoehen fest, aber nicht, WO
# die Stecker sitzen. Zwei unabhaengig entstehende Layouts passen damit
# nicht zusammen. Diese Pruefungen sind die Bremse dagegen: sie
# schlagen an, sobald jemand einen Stecker verschiebt, ohne die Folgen
# nachzurechnen.

# v2: aus drei Steckerplaetzen werden vier -- der 2x20-Block "stapel"
# wird zu zwei 1x20-Reihen "stapel_links"/"stapel_rechts" (s.
# STECKER_POS-Kommentar in stack_spec.py).
STECKER = ["stapel_links", "stapel_rechts", "kette", "leistung"]
check("vier Vertragsstecker", sorted(S.STECKER_POS), sorted(STECKER))

# Jede eingetragene Flaeche wird aus Footprint-Hof, Pin-1-Lage und
# Drehung nachgerechnet -- ein Zahlendreher in "flaeche" faellt damit
# auf, statt still ein Layout zu vergiften.
#
# v2: KEIN "pico"-Eintrag mehr (PICO_POS ist mit der Sockelplatine
# entfallen, s. stack_spec.py-Kommentar bei "PICO_POS / ... gibt es in
# v2 NICHT mehr") -- die vier STECKER_POS-Eintraege sind jetzt alles,
# was hier nachzurechnen ist.
for name in STECKER:
    e = S.STECKER_POS[name]
    check("%s: Flaeche stimmt mit Footprint+Pin1+Drehung" % name,
          e["flaeche"], S.HOEFE(e["footprints"], e["pin1"], e["drehung"]))
    check("%s: Mitte stimmt mit der Flaeche" % name,
          e["mitte"], S.MITTE(e["flaeche"]))
    check("%s: Drehung ist ein rechter Winkel" % name,
          e["drehung"] in (0, 90, 180, 270), True)

# v2 (Fix-Runde 1, RULING): der Antennen-Sperrbereich ist zurueck --
# nicht mehr aus einem eigenen PICO_POS, sondern aus stapel_links/
# stapel_rechts hergeleitet (PICO_SCHATTEN/ANTENNE_FREI, s. dortiger
# Kommentar in stack_spec.py). Zwei Pruefungen dazu:
#
#   1. ANTENNE_FREI muss VOLLSTAENDIG innerhalb PICO_SCHATTEN liegen --
#      sie ist per Definition ein Teilstreifen davon; faellt sie
#      hinaus, ist entweder PICO_SCHATTEN zu klein oder ANTENNE_FREI
#      falsch platziert.
#   2. PICO_SCHATTEN muss BEIDE Buchsenreihen ueberdecken -- geprueft
#      an den tatsaechlichen KONTAKTEN (PAD_LAGEN), nicht am vollen
#      mechanischen Hof: der Hof der beiden Buchsen ist zusammen
#      22,88 mm breit (Gehaeusebreite je Reihe kommt oben drauf),
#      PICO_SCHATTEN aber nur 21 mm -- das ist die reale Pico-
#      Platinenbreite und bewusst schmaler als der Buchsenhof (die
#      Buchsengehaeuse duerfen seitlich etwas ueber den Rand der
#      aufgesteckten Pico-Platine hinausragen, das ist normal bei
#      einer Buchse, die breiter baut als der Steckling). Was
#      PICO_SCHATTEN wirklich abdecken muss, sind die KONTAKTE selbst
#      (dort, wo die Pico-Pins tatsaechlich einstecken) -- und genau
#      das prueft PAD_LAGEN.
_pico_schatten_kontakte = []
for _n in ("stapel_links", "stapel_rechts"):
    _e = S.STECKER_POS[_n]
    _pico_schatten_kontakte.extend(
        S.PAD_LAGEN(_e["footprints"][0], _e["pin1"], _e["drehung"]).values())
check("PICO_SCHATTEN ueberdeckt jeden Kontakt von stapel_links/rechts",
      all(S.PICO_SCHATTEN[0] <= x <= S.PICO_SCHATTEN[2]
          and S.PICO_SCHATTEN[1] <= y <= S.PICO_SCHATTEN[3]
          for x, y in _pico_schatten_kontakte),
      True)
check("ANTENNE_FREI liegt vollstaendig innerhalb PICO_SCHATTEN",
      (S.ANTENNE_FREI[0] >= S.PICO_SCHATTEN[0]
       and S.ANTENNE_FREI[1] >= S.PICO_SCHATTEN[1]
       and S.ANTENNE_FREI[2] <= S.PICO_SCHATTEN[2]
       and S.ANTENNE_FREI[3] <= S.PICO_SCHATTEN[3]),
      True)


def _ueberlappt(a, b, luft=0.0):
    return (a[0] < b[2] + luft and b[0] < a[2] + luft and
            a[1] < b[3] + luft and b[1] < a[3] + luft)


LUFT = 0.6   # COURTYARD_GAP, Vorgabe von tools/pcb/geometry.py

# 1. Die vier Steckerplaetze untereinander (v2: kein Pico mehr dazu,
#    s.o.).
_flaechen = {n: S.STECKER_POS[n]["flaeche"] for n in STECKER}
_namen = sorted(_flaechen)
for i in range(len(_namen)):
    for j in range(i + 1, len(_namen)):
        a, b = _namen[i], _namen[j]
        check("kein Ueberlapp %s / %s" % (a, b),
              _ueberlappt(_flaechen[a], _flaechen[b], LUFT), False)

# 2. Freihaltebereiche der M3-Bohrungen. Das ist der Platz fuer
#    Schraubenkopf und Abstandsbolzen -- ein Stecker darin liesse sich
#    nicht verschrauben.
_r = S.M3_KEEPOUT / 2.0
for n in list(_flaechen):
    q = _flaechen[n]
    for hx, hy in S.M3_HOLES:
        check("%s frei von M3 (%s|%s)" % (n, hx, hy),
              q[0] - _r < hx < q[2] + _r and q[1] - _r < hy < q[3] + _r,
              False)

# 3. Platinenrand. 0,5 mm Randabstand, dieselbe Vorgabe wie in
#    tools/pcb/geometry.py.
RAND = 0.5
for n in list(_flaechen):
    q = _flaechen[n]
    check("%s bleibt auf der Platine" % n,
          (q[0] >= RAND and q[1] >= RAND and
           q[2] <= S.BOARD_W - RAND and q[3] <= S.BOARD_H - RAND), True)

# --- Die Footprints, aus denen die Masse stammen, sind noch dieselben -
# FOOTPRINT_HOF traegt die Hoefe von PLATZHALTER-Footprints (die
# KiCad-Standard-Stiftleisten). Die echten Bauteile -- der
# PC104-Stapelstecker und die XFCN-Paarung -- brauchen eigene
# .kicad_mod und koennen breiter bauen. Wer den Footprint austauscht,
# muss die Lage neu nachrechnen; dieser Test zwingt ihn dazu.
#
# v2: der Kreuz-Check gegen modulsockel.FP_HDR_2X20 (fuer "stapel") und
# gegen sockelplatine.FP_PICO entfaellt hier ERSATZLOS. Beide Module
# sind v1-Erzeuger, die noch den 2x20-Block bzw. eine eigene
# Sockelplatine kennen (Aufgabe 2 darf Erzeuger/Verbraucher-Dateien
# nicht anfassen, s. Aufgabenbrief) -- ihre eigenen Suiten
# (tests/test_modulsockel.py, tests/test_sockelplatine.py) stehen
# deshalb bewusst auf der Rot-Liste dieser Aufgabe, bis eine
# Folgeaufgabe sie auf stapel_links/stapel_rechts umstellt. kette und
# leistung sind von diesem Bruch NICHT betroffen (dieselbe SMD-Paar-
# Geometrie wie in v1), ihr Kreuz-Check bleibt deshalb stehen.
sys.path.insert(0, os.path.join(HERE, "..", "tools", "sch"))
import modulsockel      # zieht kein KiCad nach, nur stack_spec
# Jeder Steckerplatz nennt jetzt ALLE Footprints, die dort sitzen --
# bei den SMD-Paaren zwei (Buchse oben, Stiftleiste unten). Wuerde nur
# einer genannt, verschwaende die andere Haelfte stillschweigend aus
# der Flaechenrechnung; genau so ist der Fehler von Aufgabe 5c
# entstanden.
for name, konstanten in (("kette", ("FP_SKT_1X02", "FP_HDR_1X02")),
                         ("leistung", ("FP_SKT_2X02", "FP_HDR_2X02"))):
    check("%s: Footprints wie in modulsockel.%s"
          % (name, "/".join(konstanten)),
          tuple(S.STECKER_POS[name]["footprints"]),
          tuple(getattr(modulsockel, k) for k in konstanten))
    for fp in S.STECKER_POS[name]["footprints"]:
        check("%s: Hof von %s ist bekannt" % (name, fp.split(":")[-1]),
              fp in S.FOOTPRINT_HOF, True)
# stapel_links/stapel_rechts kennen ihren eigenen Footprint zwar noch
# nicht in modulsockel.py (s.o.), aber wenigstens der Hof muss bekannt
# sein, sonst faellt schon die Flaechenrechnung weiter oben aus.
for name in ("stapel_links", "stapel_rechts"):
    for fp in S.STECKER_POS[name]["footprints"]:
        check("%s: Hof von %s ist bekannt" % (name, fp.split(":")[-1]),
              fp in S.FOOTPRINT_HOF, True)

# --- v2.1: Randpads liegen auf F.Cu, vollstaendig in RANDPAD_ZONE, und
# jedes Pad haelt LANDE_SPERRRADIUS von jedem Landepunkt ein ----------
#
# WARUM DIESE PRUEFUNG JETZT ANDERS AUSSIEHT ALS VORHER (Aufgabe B,
# 2026-09-10). Die v2-Fassung dieser Datei pruefte RAND_X0 gegen die
# M3-Eckloch-Reichweite, weil die Randpad-Reihe HORIZONTAL nahe der
# unteren Kante lief. v2.1 dreht Seite UND Achse (s. stack_spec.py,
# RANDPADS-Kommentar): die Reihe laeuft jetzt VERTIKAL in einer eigenen
# Zone (RANDPAD_ZONE) auf F.Cu. Die alte Pruefung waere hier sinnlos
# (RAND_X0/RAND_Y gibt es nicht mehr); die neue prueft direkt gegen die
# Zone und gegen die Verdreh-Klausel, die durch den Seitenwechsel neu
# gilt (auf B.Cu war sie nie anwendbar, s. alte RULING in stack_spec.py).
check("Randpads liegen auf F.Cu", S.RAND_LAYER, "F.Cu")

_rand_halb_b = S.RAND_PAD_B / 2.0
_rand_halb_raster = S.RAND_RASTER / 2.0
for _pin, _label, (_rx, _ry) in S.RANDPADS:
    check("Randpad %s (%s) liegt in RANDPAD_ZONE (x)" % (_pin, _label),
          (S.RANDPAD_ZONE[0] <= _rx - _rand_halb_b
           and _rx + _rand_halb_b <= S.RANDPAD_ZONE[2]), True)
    check("Randpad %s (%s) liegt in RANDPAD_ZONE (y)" % (_pin, _label),
          (S.RANDPAD_ZONE[1] <= _ry - _rand_halb_raster
           and _ry + _rand_halb_raster <= S.RANDPAD_ZONE[3]), True)

# R1-Verdreh-Klausel (LAYOUT_AUFLAGEN/LANDE_SPERRRADIUS) OHNE Ausnahme --
# der Aufgabenzettel verlangt ausdruecklich, dass sie NICHT aufgeweicht
# wird. Anders als bei den frueheren B.Cu-Randpads (dort strukturell
# unerfuellbar, s. History) muss hier jeder einzelne der 22 Punkte
# einzeln bestehen, denn die Zone wurde extra so gelegt, dass das geht.
_landepunkte = S.LANDEPUNKTE_VERDREHT()
for _pin, _label, (_rx, _ry) in S.RANDPADS:
    _abstand = min(((_rx - _px) ** 2 + (_ry - _py) ** 2) ** 0.5
                   for _px, _py in _landepunkte)
    check("Randpad %s (%s) haelt LANDE_SPERRRADIUS zu jedem Landepunkt "
          "(Kupferkante, Abstand %.2f mm)" % (_pin, _label, _abstand),
          _abstand - _rand_halb_b >= S.LANDE_SPERRRADIUS, True)

# --- Der Hof umschliesst das Kontaktgitter mittig ---------------------
#
# WARUM DIESE PRUEFUNG EXISTIERT (Fix-Runde 1 zu Aufgabe 7).
# Die Pruefungen oberhalb haben einen Zahlenfehler in FOOTPRINT_HOF
# nicht fangen KOENNEN, und der Grund ist lehrreich:
#
#   * `flaeche == HOEFE(footprints, pin1, drehung)` (weiter oben) rechnet
#     die Flaeche aus FOOTPRINT_HOF nach -- steht dort eine falsche Zahl,
#     rechnet die Pruefung sie fehlerfrei nach und bleibt gruen.
#   * die Bloecke direkt darueber pruefen nur, DASS ein Hof zu einem
#     Footprint bekannt ist, nie WELCHER.
#   * `tests/test_spec_motor.py` prueft Hoefe und Ueberlappungen aus
#     derselben PLACEMENT-Tabelle, in der der Fehler steckte -- es kann
#     an dieser Stelle gar nicht rot werden.
#
# Gefunden hat den Fehler erst `steckerprobe.py` an der GEBAUTEN
# Platine: FOOTPRINT_HOF fuehrte fuer die 1x20-Buchse 5,10 x 50,80 mm,
# der Footprint der Bibliothek ist aber 3,54 x 51,80 mm. build.place()
# legt die Hof-ECKE des echten Footprints auf die Ecke des Rechtecks aus
# dieser Tabelle -- die halbe Differenz, (-0,78|+0,50) mm, landete
# damit als Versatz im KUPFER: beide Stapelreihen des Motormoduls sassen
# neben dem Vertrag. Die Zahl stammt sichtbar noch aus v1, wo "stapel"
# EIN 2x20-Block war (+-2,55 ist dessen halbe Breite).
#
# Die Invariante, die das ohne KiCad-Bibliothek faengt: bei den
# bedrahteten 2,54-mm-Stiftleisten/Buchsen legt die KiCad-Bibliothek den
# Hof mit dem GLEICHEN Rand um das Kontaktgitter -- auf allen vier
# Seiten und in der ganzen Familie derselbe Wert. Der falsche Eintrag
# war 2,55 mm breit gerandet und 1,27 mm hoch: in sich symmetrisch,
# aber eben nicht der Familienrand. Genau daran bricht er.
#
# Die SMD-Paare sind ausgenommen: ihr Anker ist der KONTAKT, nicht Pad 1
# (s. LAGE/FOOTPRINT_HOF), ihre Loetpads liegen seitlich daneben, und
# ihr Hof ist deshalb absichtlich unsymmetrisch.
THT_RAND = 1.775      # mm, an PinHeader_2x20 und PinSocket_1x20 gemessen
THT_RAND_LUFT = 0.01  # die Bibliothek rundet auf 1,77 bzw. 1,78

for _fp, (_spalten, _reihen) in sorted(S.FOOTPRINT_RASTER.items()):
    if "_SMD" in _fp:
        continue
    _x0, _y0, _x1, _y1 = S.FOOTPRINT_HOF[_fp]
    # Kontaktgitter im Footprint-Bezug: Anker (0|0) bis
    # ((Spalten-1)*RASTER | (Reihen-1)*RASTER).
    _gx = (_spalten - 1) * S.RASTER
    _gy = (_reihen - 1) * S.RASTER
    _raender = {"links": -_x0, "rechts": _x1 - _gx,
                "oben": -_y0, "unten": _y1 - _gy}
    for _seite, _wert in sorted(_raender.items()):
        check("%s: Hofrand %s ist der Familienrand %.3f mm (ist %.3f)"
              % (_fp.split(":")[-1], _seite, THT_RAND, _wert),
              abs(_wert - THT_RAND) <= THT_RAND_LUFT, True)

# --- Es bleibt noch Platz --------------------------------------------
# Die Untergrenze ist hergeleitet, nicht gesetzt: Hofsumme des
# anspruchsvollsten Moduls geteilt durch den auf einer wirklich
# gebauten Platine gemessenen Belegungsgrad (s. Kommentar im Vertrag).
_bedarf_modul = S.MODUL_HOF_SUMME_MM2 / S.BELEGUNGSGRAD_ERPROBT
check("Untergrenze passt zu ihrer eigenen Herleitung",
      S.FREIE_FLAECHE_MINDEST >= _bedarf_modul, True)

_modul, _modul_rechteck = geometry.freie_flaeche(
    S, [S.STECKER_POS[n]["flaeche"] for n in STECKER])
check("Modul: freie Flaeche am Stueck ueber der Untergrenze",
      _modul > S.FREIE_FLAECHE_MINDEST, True)
# Nicht nur die Summe, sondern auch ein Stueck am Stueck: eine Flaeche,
# die nur ueber einen schmalen Hals zusammenhaengt, ist keine
# Bauflaeche. Das groesste freie Rechteck muss die Hofsumme des
# Motormoduls selbst tragen koennen.
check("Modul: groesstes freies Rechteck traegt die Hofsumme",
      _modul_rechteck > S.MODUL_HOF_SUMME_MM2, True)

# v2: KEIN separater "Sockel"-Check mehr. Er pruefte in v1 die freie
# Flaeche der EINEN Sockelplatine (Stecker + Pico + Antennen-
# Sperrbereich abgezogen) gegen deren eigene, kleinere Bauteilliste
# (SOCKEL_HOF_SUMME_MM2). Diese Sonderrolle gibt es in v2 nicht mehr --
# jede Platine ist jetzt ein "Modul" im obigen Sinn (traegt Pico +
# Vertragsstecker + eigene Bauteile), der "Modul:"-Check oben deckt sie
# also bereits ab. S.SOCKEL_HOF_SUMME_MM2 bleibt in stack_spec.py als
# historischer Messwert stehen (s. dortiger Kommentar), wird hier aber
# nicht mehr abgefragt -- ersatzlos entfernt, nicht abgeschwaecht: eine
# Platine, die es nicht mehr gibt, hat auch keine Flaeche mehr, die man
# gegen ihre alte Bauteilliste pruefen koennte.

# --- Kontaktnummerierung der SMD-Paare -------------------------------
# Kontakt 1 des 2x02-Leistungssteckers liegt in der RECHTEN Spalte des
# Gitters (SPALTEN_GESPIEGELT): die Buchse hat Pad 1 rechts, und die
# Stiftleiste sitzt laut Vertrag gespiegelt auf der Unterseite -- in
# Platinenkoordinaten landet ihr Kontakt 1 damit ebenfalls rechts. Das
# ist eine Eigenschaft der BIBLIOTHEKS-Footprints (Aufgabe 6/Ruling
# 2026-09-01), unabhaengig von pin1 -- v2 verschiebt "leistung" nur
# (neue Plattengroesse, s. STECKER_POS-Kommentar), die absoluten Zahlen
# unten sind deshalb einfach um denselben Versatz mitgewandert
# (pin1 (54.70, 42.00) -> (62.50, 45.50), Versatz (+7.80, +3.50)).
_L = S.STECKER_POS["leistung"]
for _fp in _L["footprints"]:
    _lag = S.PAD_LAGEN(_fp, _L["pin1"], _L["drehung"])
    check("Kontakt 1 (%s) rechte Spalte" % _fp.split(":")[1][:9],
          _lag[1], (65.04, 45.5))
    check("Kontakt 2 (%s) linke Spalte" % _fp.split(":")[1][:9],
          _lag[2], (62.5, 45.5))
    check("Kontakt 3 unter Kontakt 1 (%s)" % _fp.split(":")[1][:9],
          _lag[3], (65.04, 48.04))
# Beide Haelften muessen DIESELBE Zuordnung liefern -- sonst traefe im
# Stapel Kontakt k auf Kontakt j.
check("beide Leistungs-Haelften nummerieren gleich",
      S.PAD_LAGEN(_L["footprints"][0], _L["pin1"], _L["drehung"]),
      S.PAD_LAGEN(_L["footprints"][1], _L["pin1"], _L["drehung"]))
# Der Kettenstecker (eine Spalte) ist NICHT gespiegelt: Kontakt 1 auf
# dem Anker. v2 verschiebt "kette" seitlich (s. STECKER_POS-Kommentar),
# pin1 wandert von (12.50, 2.75) auf (20.59, 2.75) -- Kontakt 1 bleibt
# per Definition auf dem Anker, unabhaengig von dessen Lage.
_K = S.STECKER_POS["kette"]
for _fp in _K["footprints"]:
    check("Kette: Kontakt 1 auf dem Anker (%s)" % _fp.split(":")[1][:9],
          S.PAD_LAGEN(_fp, _K["pin1"], _K["drehung"])[1], (20.59, 2.75))
# stapel_links ist bei Drehung 0 nicht gespiegelt (Kontakt 1 wirklich
# oben, s. STECKER_POS-Kommentar); stapel_rechts steht dagegen absichtlich
# bei Drehung 180 (nicht gespiegelt im SPALTEN_GESPIEGELT-Sinn -- das
# gilt nur fuer die 2x02-SMD-Footprints -- sondern um ihre eigene
# Zaehlrichtung umzukehren, s. Kommentar "v2: footprint-lokale
# Kontakte -> Pico-Pin"). Beide 1x20-Footprints stehen deshalb NICHT
# in SPALTEN_GESPIEGELT.
for _name in ("stapel_links", "stapel_rechts"):
    check("%s nicht in SPALTEN_GESPIEGELT" % _name,
          S.STECKER_POS[_name]["footprints"][0] in S.SPALTEN_GESPIEGELT,
          False)

# --- Verdreht aufgesteckt --------------------------------------------
# Das Lochbild ist punktsymmetrisch, ein Modul laesst sich also um
# 180 Grad verdreht anschrauben. Dann laege Pin 1 auf Pin 40 -- VBUS
# auf FLASH_TX. Verhindert wird das nicht durch die Mechanik, sondern
# durch die bewusst unsymmetrische Steckerlage: kein Stift darf einen
# Buchsenkontakt treffen. Entscheidend ist der Pad-Abstand, nicht die
# Flaeche (die Flaeche des verdrehten Leistungssteckers ueberdeckt
# durchaus die des Stapelsteckers -- nur eben zwischen dessen
# Rasterloechern).
_pads = []
for n in STECKER:
    e = S.STECKER_POS[n]
    _lagen = S.PAD_LAGEN(e["footprints"][0], e["pin1"], e["drehung"])
    _pads.extend(_lagen.values())
_naechster = min(
    ((S.BOARD_W - x - x2) ** 2 + (S.BOARD_H - y - y2) ** 2) ** 0.5
    for x, y in _pads for x2, y2 in _pads)
# Mehr als das halbe Raster (1,27 mm) -- darunter faende ein Stift in
# einen Kontakt. Die 2,5 mm sind die Reissleine, der gerechnete Wert
# liegt bei 2,755 mm (VERDREHT_MINDESTABSTAND_MM).
check("verdreht trifft kein Stift einen Kontakt",
      _naechster > 2.5, True)
check("der eingetragene Mindestabstand stimmt",
      round(_naechster, 3), S.VERDREHT_MINDESTABSTAND_MM)
check("Mindestabstand ueber dem halben Raster",
      S.VERDREHT_MINDESTABSTAND_MM > S.RASTER / 2.0, True)

# Die Layout-Auflage dazu steht im Vertrag und muss dort bleiben.
check("Layout-Auflage zur Verdreh-Kennzeichnung steht im Vertrag",
      any("180 Grad verdreht" in a for a in S.LAYOUT_AUFLAGEN), True)
# Sie gehoert NICHT unter die Firmware-Auflagen -- das eine gilt der
# Software, das andere dem Kupfer.
check("Firmware-Auflagen bleiben Firmware",
      any("Bestueckungsdruck" in a for a in S.AUFLAGEN), False)

# --- v2.1: R1-R9 als pruefbare Zusagen (LAYOUT_REGELN) ---------------
# Der Aufgabenzettel verlangt "die pledge dict present with the
# documented keys" -- alle neun Regeln aus dem Plan muessen als
# eigener Schluessel auftauchen, jede mit Text UND Belegstatus, damit
# spaeter niemand eine Regel nur behauptet, ohne zu sagen, wie hart sie
# belegt ist.
_R = S.LAYOUT_REGELN
check("LAYOUT_REGELN traegt genau R1..R9",
      sorted(_R), ["R%d" % n for n in range(1, 10)])
for _k in _R:
    check("%s hat einen Regeltext" % _k, bool(_R[_k].get("text")), True)
    check("%s hat einen Belegstatus" % _k, bool(_R[_k].get("beleg")), True)

# Wo die Recherche eine Zahl ausdruecklich als Konvention/unbelegt
# markiert hat, darf dieser Vertrag sie nicht als "belegt" ausgeben --
# das waere genau das Dressing, das der Aufgabenzettel verbietet.
for _k in ("R5", "R6", "R8", "R9"):
    check("%s ist ehrlich als Konvention markiert, nicht als Norm"
          % _k,
          _R[_k]["beleg"].startswith("Konvention")
          or _R[_k]["beleg"].startswith("teilweise belegt"), True)

# R1: die Zusage referenziert dieselbe Flaeche, gegen die oben
# tatsaechlich geprueft wurde (kein zweiter, abweichender Name).
check("R1 referenziert PICO_SCHATTEN", _R["R1"]["keepout"], "PICO_SCHATTEN")
check("R2 referenziert KLEMMENZONE", _R["R2"]["zone"], "KLEMMENZONE")

# R3: die Zahl ist keine geratene Konstante, sondern derselbe Wert wie
# im Stapelvertrag selbst (STECKER_STAPEL) -- ein Auseinanderlaufen
# waere ein stiller Widerspruch zwischen zwei Vertragsstellen.
check("R3-Bauteilhoehe == STECKER_STAPEL-Buchsenhoehe",
      _R["R3"]["max_bauteilhoehe_mm"],
      S.STECKER_STAPEL["gehaeusehoehe_mm"])

# R4/R5: die Zahlen, gegen die die Zonen oben tatsaechlich geprueft
# wurden, muessen aus DIESEM Dict kommen, nicht aus einer zweiten,
# unabhaengig gepflegten Kopie.
check("R4-Klemmenabstand ist 0,8 mm (IEC 60664, konservativ)",
      _R["R4"]["mindestabstand_mm"], 0.8)
check("R5-Kantenabstand ist 2,0 mm", _R["R5"]["mindestabstand_mm"], 2.0)

# R6/R7/R8: Silkscreen-seitige Zusagen liegen auf der Vorderseite --
# eine Randpad-Beschriftung auf B.Silkscreen (der alte v2-Stand) waere
# nach dem Seitenwechsel (RAND_LAYER) falsch.
for _k in ("R6", "R7"):
    check("%s liegt auf F.Silkscreen" % _k, _R[_k]["layer"], "F.Silkscreen")
check("R8-Label liegt auf derselben Seite wie das Randpad-Kupfer",
      _R["R8"]["layer"], S.RAND_LABEL_LAYER)
check("R8-Kupferlayer stimmt mit RAND_LAYER ueberein",
      _R["R8"]["kupfer_layer"], S.RAND_LAYER)
check("R8-Label und -Kupfer liegen NICHT auf verschiedenen Seiten "
      "(sonst waere die Beschriftung spiegelverkehrt zum Pad)",
      _R["R8"]["layer"].split(".")[0], _R["R8"]["kupfer_layer"].split(".")[0])


# --- Typcode -> Kennwiderstaende -------------------------------------
# Die Nibble-Kodierung ist eine Zusage an jede Modul-Stueckliste.
# Rot-Nachweis: der ungueltige Code 0x00 (nicht von einer leeren
# Platine unterscheidbar) MUSS abgewiesen werden -- prueft man ihn
# nicht, bestueckt irgendwann jemand ein "Typ-0"-Modul.
check("Motor 0x01: ID0=680, ID1=Bruecke",
      S.TYPCODE_WIDERSTAENDE(0x01), (680.0, 0.0))
check("Dimmer3 0x11: beide 680",
      S.TYPCODE_WIDERSTAENDE(0x11), (680.0, 680.0))
check("Dimmer4 0x12: ID0=1500, ID1=680",
      S.TYPCODE_WIDERSTAENDE(0x12), (1500.0, 680.0))
try:
    S.TYPCODE_WIDERSTAENDE(0x00)
    fails.append("Typcode 0x00 wurde NICHT abgewiesen")
except ValueError:
    pass
try:
    S.TYPCODE_WIDERSTAENDE(0x99)
    fails.append("unbekannter Typcode 0x99 wurde NICHT abgewiesen")
except ValueError:
    pass

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

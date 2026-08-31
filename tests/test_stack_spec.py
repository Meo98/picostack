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


# --- Umriss und Lochbild ---
check("Breite", S.BOARD_W, 64.0)
check("Hoehe", S.BOARD_H, 60.0)
check("vier M3", len(S.M3_HOLES), 4)
check("Lochbild 56 mm", S.M3_HOLES[2][0] - S.M3_HOLES[0][0], 56.0)
check("Lochbild 52 mm", S.M3_HOLES[1][1] - S.M3_HOLES[0][1], 52.0)

# Alle vier Ecken einzeln, nicht nur zwei Differenzen: sonst darf die
# vierte Bohrung irgendwo liegen und der Test merkt es nicht.
check("Lochbild vollstaendig", sorted(S.M3_HOLES),
      [(4.0, 4.0), (4.0, 56.0), (60.0, 4.0), (60.0, 56.0)])

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
for _name, _st in (("Stapelstecker", S.STECKER_STAPEL),
                   ("Kettenstecker", S.STECKER_KETTE),
                   ("Leistungsstecker", S.STECKER_LEISTUNG)):
    for _seite in ("buchse_lcsc", "stift_lcsc"):
        _nr = _st[_seite]
        check("%s: %s ist belegt" % (_name, _seite), bool(_nr), True)
        check("%s: %s sieht aus wie eine LCSC-Nummer" % (_name, _seite),
              _nr.startswith("C") and _nr[1:].isdigit(), True)

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

STECKER = ["stapel", "kette", "leistung"]
check("drei Vertragsstecker", sorted(S.STECKER_POS), sorted(STECKER))

# Jede eingetragene Flaeche wird aus Footprint-Hof, Pin-1-Lage und
# Drehung nachgerechnet -- ein Zahlendreher in "flaeche" faellt damit
# auf, statt still ein Layout zu vergiften.
for name in STECKER + ["pico"]:
    e = S.STECKER_POS[name] if name in S.STECKER_POS else S.PICO_POS
    check("%s: Flaeche stimmt mit Footprint+Pin1+Drehung" % name,
          e["flaeche"], S.HOEFE(e["footprints"], e["pin1"], e["drehung"]))
    check("%s: Mitte stimmt mit der Flaeche" % name,
          e["mitte"], S.MITTE(e["flaeche"]))
    check("%s: Drehung ist ein rechter Winkel" % name,
          e["drehung"] in (0, 90, 180, 270), True)

# Der Antennen-Sperrbereich wird ebenso aus dem Pico-eigenen Mass
# gedreht statt abgeschrieben.
check("Antennen-Sperrbereich aus PICO_POS gerechnet",
      S.ANTENNE_SPERRBEREICH,
      S.LAGE(S.PICO_ANTENNE_HOF, S.PICO_POS["pin1"], S.PICO_POS["drehung"]))
# 14,2 x 9,0 mm, um 90 Grad gedreht also 9,0 x 14,2.
_a = S.ANTENNE_SPERRBEREICH
check("Antennen-Sperrbereich ist 9,0 x 14,2 mm",
      (round(_a[2] - _a[0], 2), round(_a[3] - _a[1], 2)), (9.0, 14.2))


def _ueberlappt(a, b, luft=0.0):
    return (a[0] < b[2] + luft and b[0] < a[2] + luft and
            a[1] < b[3] + luft and b[1] < a[3] + luft)


LUFT = 0.6   # COURTYARD_GAP, Vorgabe von tools/pcb/geometry.py

# 1. Die drei Stecker untereinander -- und gegen den Pico, denn auf der
#    Sockelplatine liegen alle vier auf derselben Platine.
_flaechen = {n: S.STECKER_POS[n]["flaeche"] for n in STECKER}
_flaechen["pico"] = S.PICO_POS["flaeche"]
_namen = sorted(_flaechen)
for i in range(len(_namen)):
    for j in range(i + 1, len(_namen)):
        a, b = _namen[i], _namen[j]
        check("kein Ueberlapp %s / %s" % (a, b),
              _ueberlappt(_flaechen[a], _flaechen[b], LUFT), False)

# 2. Der Antennen-Sperrbereich gegen die drei Stecker. Gegen den Pico
#    NICHT: er liegt naturgemaess innerhalb von dessen Hof.
for n in STECKER:
    check("Antenne kollidiert nicht mit %s" % n,
          _ueberlappt(S.ANTENNE_SPERRBEREICH, _flaechen[n], LUFT), False)
check("Antennen-Sperrbereich liegt im Hof des Pico",
      _ueberlappt(S.ANTENNE_SPERRBEREICH, S.PICO_POS["flaeche"]), True)

# 3. Freihaltebereiche der M3-Bohrungen. Das ist der Platz fuer
#    Schraubenkopf und Abstandsbolzen -- ein Stecker darin liesse sich
#    nicht verschrauben.
_r = S.M3_KEEPOUT / 2.0
for n in list(_flaechen) + ["antenne"]:
    q = S.ANTENNE_SPERRBEREICH if n == "antenne" else _flaechen[n]
    for hx, hy in S.M3_HOLES:
        check("%s frei von M3 (%s|%s)" % (n, hx, hy),
              q[0] - _r < hx < q[2] + _r and q[1] - _r < hy < q[3] + _r,
              False)

# 4. Platinenrand. 0,5 mm Randabstand, dieselbe Vorgabe wie in
#    tools/pcb/geometry.py.
RAND = 0.5
for n in list(_flaechen) + ["antenne"]:
    q = S.ANTENNE_SPERRBEREICH if n == "antenne" else _flaechen[n]
    check("%s bleibt auf der Platine" % n,
          (q[0] >= RAND and q[1] >= RAND and
           q[2] <= S.BOARD_W - RAND and q[3] <= S.BOARD_H - RAND), True)

# --- Die Footprints, aus denen die Masse stammen, sind noch dieselben -
# FOOTPRINT_HOF traegt die Hoefe von PLATZHALTER-Footprints (die
# KiCad-Standard-Stiftleisten). Die echten Bauteile -- der
# PC104-Stapelstecker und die XFCN-Paarung -- brauchen eigene
# .kicad_mod und koennen breiter bauen. Wer den Footprint austauscht,
# muss die Lage neu nachrechnen; dieser Test zwingt ihn dazu.
sys.path.insert(0, os.path.join(HERE, "..", "tools", "sch"))
import modulsockel      # zieht kein KiCad nach, nur stack_spec
import sockelplatine
# Jeder Steckerplatz nennt jetzt ALLE Footprints, die dort sitzen --
# bei den SMD-Paaren zwei (Buchse oben, Stiftleiste unten). Wuerde nur
# einer genannt, verschwaende die andere Haelfte stillschweigend aus
# der Flaechenrechnung; genau so ist der Fehler von Aufgabe 5c
# entstanden.
for name, konstanten in (("stapel", ("FP_HDR_2X20",)),
                         ("kette", ("FP_SKT_1X02", "FP_HDR_1X02")),
                         ("leistung", ("FP_SKT_2X02", "FP_HDR_2X02"))):
    check("%s: Footprints wie in modulsockel.%s"
          % (name, "/".join(konstanten)),
          tuple(S.STECKER_POS[name]["footprints"]),
          tuple(getattr(modulsockel, k) for k in konstanten))
    for fp in S.STECKER_POS[name]["footprints"]:
        check("%s: Hof von %s ist bekannt" % (name, fp.split(":")[-1]),
              fp in S.FOOTPRINT_HOF, True)
check("Pico: Footprint wie in sockelplatine.FP_PICO",
      (sockelplatine.FP_PICO,), tuple(S.PICO_POS["footprints"]))

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

_sockel, _sockel_rechteck = geometry.freie_flaeche(
    S, [S.STECKER_POS[n]["flaeche"] for n in STECKER]
       + [S.PICO_POS["flaeche"], S.ANTENNE_SPERRBEREICH])
check("Sockel: freie Flaeche traegt die eigenen Bauteile",
      _sockel > S.SOCKEL_HOF_SUMME_MM2 / S.BELEGUNGSGRAD_ERPROBT, True)
check("Sockel: groesstes freies Rechteck traegt die eigene Hofsumme",
      _sockel_rechteck > S.SOCKEL_HOF_SUMME_MM2, True)

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


if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

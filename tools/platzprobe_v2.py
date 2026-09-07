"""Platzprobe fuer PicoStack v2: passt ein neues Einheitsmass?

WARUM DIESES SKRIPT. v2 streicht die Sockelplatine (Commit 7daaad3,
"der Pico ist der Stapel"): jedes Modul traegt kuenftig seinen eigenen
Pico (zwei 1x20-Buchsenreihen statt eines gemeinsamen 2x20-
Stapelsteckers), seine eigene 6-30-V-Versorgungszelle und beschriftete
Randpads fuer alle freien GPIO. Das heutige Einheitsmass (64x60 mm,
stack_spec.BOARD_W/H) wurde nie gegen diese Zusatzlast gerechnet -- es
stammt aus einer Zeit, in der die Sockelplatine den Pico und die
Versorgung allein trug. Bevor Aufgabe 2 den Vertrag aendert, muss
feststehen, OB und WELCHES Mass ueberhaupt passt.

WIE GERECHNET WIRD. Jede Pflichtflaeche wird als EIN achsenparalleles
Rechteck modelliert (Design-Vorgabe der Aufgabe) und an einer festen
Kante platziert -- ein simples Regal-Layout, keine Zufallssuche:

    oben     Pico-Zone (zwei Buchsenreihen + Pico-Schatten), zentriert
    darunter Leistungsstecker + zwei Kettenstecker, nebeneinander
    darunter Versorgungszelle, sechs Teile nebeneinander
    unten    Randpad-Kante (22 Loecher + Silk-Beschriftung), zentriert

Die vier M3-Eckloecher sitzen wie in v1 4 mm von der Kante (stack_spec
kennt keinen anderen Wert) und bekommen ihren Freihaltebereich
(M3_KEEPOUT, hier als Quadrat statt Kreis modelliert -- Design-Vorgabe:
"jede Pflichtflaeche als Rechteck") in den seitlichen Raendern von
Pico-Zone und Randpad-Kante. Das ist der einzige Kollisionstest, den
dieses Skript wirklich rechnet: reicht der Rand rechts und links neben
der zentrierten Zone, damit die Eckloecher nicht in ihr Rechteck
hineinragen? Reicht er nicht, ist der Kandidat "GEOMETRIE ROT" --
unabhaengig davon, ob rechnerisch genug Flaeche uebrig bliebe. Ein
Kandidat mit viel freier Flaeche, dessen Eckloch aber im Steckerhof
sitzt, ist trotzdem unbaubar.

NUTZLAST-REFERENZ. Der Bericht zur Aufgabe verlangt "Bauteilhofflaeche
des Motormoduls v1 aus spec_motor.PLACEMENT, minus J100-Block, plus
neue Zelle". Waertlich umgesetzt (PLACEMENT-Summe minus NUR J100, plus
die Zellen-Flaeche oben) wuerde die Versorgungszelle doppelt gezaehlt:
einmal als eigene Pflichtflaeche oben, einmal im Nutzlast-Aufschlag.
Das haette das Ergebnis nicht sicherer gemacht, nur unehrlich verzerrt
(eine Flaeche, die zweimal abgezogen wird, ist keine zusaetzliche
Reserve, sondern ein Rechenfehler, der zufaellig in die sichere
Richtung faellt). Dieses Skript zaehlt jede Flaeche genau einmal:
J100 UND die vier SMD-Haelften der Ketten-/Leistungsstecker
(J101..J104) fallen aus der Motor-PLACEMENT-Summe heraus, weil ihr
Hof bereits oben als eigene Pflichtflaeche steht (aus
stack_spec.STECKER_POS, nicht aus spec_motor -- andere Quelle, damit
ein Aenderung an einer Stelle nicht beide Zahlen still verschiebt).
Die Versorgungszelle bleibt AUSSCHLIESSLICH oben stehen. Die
verbleibende Motor-Nutzlast ist damit alles, was im Motormodul NICHT
schon ein Vertragsstecker ist: DRV8876, MCU-Nest, Kettenflipflop,
Notaus-Band, Klemmen -- also genau das, was ein neues Modul zusaetzlich
zur generischen v2-Infrastruktur braucht.

PACKUNGSRESERVE 1,25: dieselbe Groessenordnung wie
stack_spec.BELEGUNGSGRAD_ERPROBT (0,566 auf einer echten, verlegten
Platine entspricht Faktor 1/0,566 = 1,77 zwischen Bauteilflaeche und
tatsaechlich benoetigter Platinenflaeche). 1,25 ist davon der
konservativere (kleinere) Wert -- absichtlich, weil dieses Skript nur
die grobe Vorauswahl trifft; Aufgabe 2 und die eigentliche Verlegung
duerfen strenger pruefen.

Rein aus Python, ohne KiCad-Import -- lauffaehig als
`python3 tools/platzprobe_v2.py`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (HERE, os.path.join(HERE, "pcb")):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import stack_spec as S          # noqa: E402
import spec_motor as MOTOR      # noqa: E402


def _mass(flaeche):
    """(Laenge, Breite) eines (x0,y0,x1,y1)-Rechtecks aus dem Vertrag."""
    x0, y0, x1, y1 = flaeche
    return (round(x1 - x0, 3), round(y1 - y0, 3))


# --- 1. Pico-Zone: zwei 1x20-Buchsenreihen + Pico-Schatten -----------
# Reihenhof lt. Aufgabenzettel: 50,8 x 5,1 mm (20 Kontakte a 2,54 mm
# lang, 5,1 mm Buchsenbreite). Reihenabstand 17,78 mm (Pico-Datenblatt,
# Abstand der beiden Pinreihen). Die Zone ist die kleinste Flaeche, die
# BEIDE Reihen UND den Pico-Schatten (51 x 21 mm, Hoehen-Keepout: keine
# Bauteile > 3 mm darunter) umschliesst:
#   Laenge: max(Reihenlaenge, Schattenlaenge) -- beide fast gleich lang
#   Breite: max(Schattenbreite, Reihenabstand + eine Reihenbreite) --
#     die Reihen ragen mit ihrem Buchsenkoerper ueber die 21 mm des
#     Pico-Schattens hinaus (die Buchse ist breiter als die Pico-
#     Platine selbst, die auf ihr aufsteckt).
PICO_REIHE_L = 50.8
PICO_REIHE_B = 5.1
PICO_REIHE_ABSTAND = 17.78
PICO_SCHATTEN_L = 51.0
PICO_SCHATTEN_B = 21.0

PICO_ZONE_L = max(PICO_REIHE_L, PICO_SCHATTEN_L)
PICO_ZONE_B = max(PICO_SCHATTEN_B, PICO_REIHE_ABSTAND + PICO_REIHE_B)
PICO_ZONE_FLAECHE = round(PICO_ZONE_L * PICO_ZONE_B, 3)

# --- 2. Leistungsstecker-2x2 + zwei Kettenstecker ---------------------
# Hoefe direkt aus dem Vertrag (stack_spec.STECKER_POS), nicht neu
# geschaetzt -- aendert sich dort ein Mass, wandert es hierher mit.
# Nebeneinander platziert: Breite = Leistungsstecker + 2x Kettenstecker,
# Tiefe = die groessere der beiden Einzeltiefen.
_LEISTUNG_L, _LEISTUNG_B = _mass(S.STECKER_POS["leistung"]["flaeche"])
_KETTE_L, _KETTE_B = _mass(S.STECKER_POS["kette"]["flaeche"])

STECKER_ZONE_L = round(_LEISTUNG_L + 2 * _KETTE_L, 3)
STECKER_ZONE_B = max(_LEISTUNG_B, _KETTE_B)
STECKER_ZONE_FLAECHE = round(STECKER_ZONE_L * STECKER_ZONE_B, 3)

# --- 3. Versorgungszelle ----------------------------------------------
# Sechs Teile aus dem Aufgabenzettel, Masse woertlich uebernommen.
# Nebeneinander platziert (dieselbe Regal-Logik wie bei den Steckern).
ZELLE_TEILE = {
    "Klemme": (8.0, 8.6),
    "Q-Schutz": (11.1, 7.0),
    "TVS": (9.8, 6.7),
    "Regler SIP-3": (10.0, 10.0),
    "Schottky": (9.8, 6.7),
    "Elko": (8.5, 8.5),
}
ZELLE_ZONE_L = round(sum(w for w, h in ZELLE_TEILE.values()), 3)
ZELLE_ZONE_B = max(h for w, h in ZELLE_TEILE.values())
ZELLE_ZONE_FLAECHE = round(ZELLE_ZONE_L * ZELLE_ZONE_B, 3)
ZELLE_TEILE_SUMME = round(sum(w * h for w, h in ZELLE_TEILE.values()), 3)
# ZELLE_ZONE_FLAECHE (das Regal-Rechteck) ist groesser als
# ZELLE_TEILE_SUMME (die reine Bauteilflaeche): die Teile sind
# unterschiedlich hoch, das Regal reserviert trotzdem die volle Tiefe
# des hoechsten Teils ueber die ganze Breite. Fuer die Pflichtflaeche
# zaehlt das Regal-Rechteck (was wirklich blockiert ist); die
# Teile-Summe steht nur zum Nachrechnen daneben.

# --- 4. Randpads: 18 GPIO + 4x (3V3/GND) ------------------------------
RAND_LOECHER = 18 + 4
RAND_RASTER = 2.54
RAND_KANTE = round(RAND_LOECHER * RAND_RASTER, 3)   # 55,88 mm (Aufgabe
                                                     # rundet auf 55,9)
RAND_SILK_TIEFE = 4.0
RAND_ZONE_FLAECHE = round(RAND_KANTE * RAND_SILK_TIEFE, 3)

# --- 5. M3-Eckloecher + Freihaltekreise -------------------------------
# Wie v1 (stack_spec.M3_HOLES): 4 mm Abstand von der Kante. Der
# Freihaltebereich (M3_KEEPOUT, Durchmesser) wird hier als Quadrat
# modelliert -- Design-Vorgabe der Aufgabe, "jede Pflichtflaeche ein
# achsenparalleles Rechteck" --, nicht als Kreis. Das macht die Flaeche
# etwas GROESSER als der echte Kreis (Quadrat = Seite^2 = 49 mm^2,
# Kreis = pi*r^2 = 38,48 mm^2 je Loch) -- eine kleine, bewusste
# Uebervorsicht, kein Fehler.
M3_RAND_ABSTAND = 4.0
M3_KEEPOUT = S.M3_KEEPOUT           # 7,0 mm (Vertrag)
M3_ANZAHL = 4
M3_FLAECHE = round(M3_ANZAHL * M3_KEEPOUT * M3_KEEPOUT, 3)
# Reichweite eines Eckloch-Freihaltequadrats von der Plattenkante aus
# gemessen: Lochmitte (4 mm) plus halbe Quadratseite (M3_KEEPOUT/2).
M3_REICHWEITE = M3_RAND_ABSTAND + M3_KEEPOUT / 2.0

MANDATORY_ZONEN = (
    ("Pico-Reihen + Pico-Schatten", PICO_ZONE_L, PICO_ZONE_B,
     PICO_ZONE_FLAECHE),
    ("Leistungsstecker + 2x Kettenstecker", STECKER_ZONE_L, STECKER_ZONE_B,
     STECKER_ZONE_FLAECHE),
    ("Versorgungszelle (Regal, 6 Teile)", ZELLE_ZONE_L, ZELLE_ZONE_B,
     ZELLE_ZONE_FLAECHE),
    ("Randpad-Kante (22 Loecher + Silk)", RAND_KANTE, RAND_SILK_TIEFE,
     RAND_ZONE_FLAECHE),
)
MANDATORY_SUMME = round(sum(f for _, _, _, f in MANDATORY_ZONEN), 3)
# Hoehe, die das Regal-Layout braucht, wenn alle vier Zonen von oben
# nach unten gestapelt werden (Reihenfolge oben): Pico -> Stecker ->
# Zelle -> Randpad-Kante ganz unten.
H_BENOETIGT = round(PICO_ZONE_B + STECKER_ZONE_B + ZELLE_ZONE_B
                    + RAND_SILK_TIEFE, 3)

# --- 6. Nutzlast-Referenz: Motormodul v1, bereinigt -------------------
# spec_motor.PLACEMENT traegt jedes platzierte Bauteil als Platz(x, y,
# w, h, rot, tht); w/h sind bereits die Hof-Ausdehnung IN
# Platinenkoordinaten (Drehung ist eingerechnet, s. spec_sockel.Platz-
# Docstring) -- w*h ist also direkt die belegte Flaeche, ohne die
# Drehung gesondert beruecksichtigen zu muessen.
_STECKER_REFS = ("J100", "J101", "J102", "J103", "J104")

PLACEMENT_SUMME = round(
    sum(p.w * p.h for p in MOTOR.PLACEMENT.values()), 4)
STECKER_IM_MOTOR = round(
    sum(MOTOR.PLACEMENT[ref].w * MOTOR.PLACEMENT[ref].h
        for ref in _STECKER_REFS), 4)
# J100 (2x20-Stapelstecker) entfaellt komplett -- seine Rolle uebernimmt
# die Pico-Zone oben. J101..J104 (die SMD-Haelften von Ketten- und
# Leistungsstecker) entfallen aus DIESER Summe, weil ihr Hof bereits in
# STECKER_ZONE_FLAECHE oben steht (aus stack_spec.STECKER_POS gerechnet
# -- andere Quelle als PLACEMENT, deshalb kein blosses Weglassen von
# Duplikaten, sondern eine bewusste Trennung: Vertragsflaeche oben,
# Modul-Eigenflaeche hier). Die Versorgungszelle wird HIER NICHT addiert
# (s. Modul-Docstring, Abschnitt "Nutzlast-Referenz") -- sie steht
# bereits einmal in MANDATORY_SUMME.
MOTOR_NUTZLAST = round(PLACEMENT_SUMME - STECKER_IM_MOTOR, 4)

PACKUNGS_RESERVE = 1.25
NUTZLAST_BEDARF = round(MOTOR_NUTZLAST * PACKUNGS_RESERVE, 4)


# --- 7. Kandidaten pruefen --------------------------------------------
KANDIDATEN = ((70.0, 60.0), (75.0, 65.0), (80.0, 70.0))


def pruefe(w, h):
    """Rechnet einen Kandidaten (W, H) durch. Gibt ein Ergebnis-Dict."""
    rand_oben = round((w - PICO_ZONE_L) / 2.0, 3)
    rand_unten = round((w - RAND_KANTE) / 2.0, 3)
    geometrie_oben = rand_oben >= M3_REICHWEITE
    geometrie_unten = rand_unten >= M3_REICHWEITE
    hoehe_ok = h >= H_BENOETIGT
    breite_reicht = (w >= PICO_ZONE_L and w >= STECKER_ZONE_L
                     and w >= ZELLE_ZONE_L and w >= RAND_KANTE)
    kollisionsfrei = (geometrie_oben and geometrie_unten and hoehe_ok
                      and breite_reicht)

    flaeche = w * h
    frei = round(flaeche - MANDATORY_SUMME - M3_FLAECHE, 3)
    flaeche_reicht = frei >= NUTZLAST_BEDARF
    passt = kollisionsfrei and flaeche_reicht

    return {
        "w": w, "h": h, "flaeche": flaeche, "frei": frei,
        "rand_oben": rand_oben, "rand_unten": rand_unten,
        "geometrie_oben": geometrie_oben, "geometrie_unten": geometrie_unten,
        "hoehe_ok": hoehe_ok, "breite_reicht": breite_reicht,
        "kollisionsfrei": kollisionsfrei, "flaeche_reicht": flaeche_reicht,
        "passt": passt,
    }


def main():
    print("=== Flaecheninventar (v2-Pflichtflaechen) ===")
    print("Pico-Zone           : %5.2f x %5.2f mm = %8.2f mm^2  "
          "(Reihe %sx%s mm, Abstand %s mm, Schatten %sx%s mm)"
          % (PICO_ZONE_L, PICO_ZONE_B, PICO_ZONE_FLAECHE,
             PICO_REIHE_L, PICO_REIHE_B, PICO_REIHE_ABSTAND,
             PICO_SCHATTEN_L, PICO_SCHATTEN_B))
    print("Stecker-Zone        : %5.2f x %5.2f mm = %8.2f mm^2  "
          "(Leistung %sx%s + 2x Kette %sx%s, aus STECKER_POS)"
          % (STECKER_ZONE_L, STECKER_ZONE_B, STECKER_ZONE_FLAECHE,
             _LEISTUNG_L, _LEISTUNG_B, _KETTE_L, _KETTE_B))
    print("Versorgungszelle    : %5.2f x %5.2f mm = %8.2f mm^2  "
          "(Teile-Summe %8.2f mm^2)"
          % (ZELLE_ZONE_L, ZELLE_ZONE_B, ZELLE_ZONE_FLAECHE,
             ZELLE_TEILE_SUMME))
    for name, (bw, bh) in ZELLE_TEILE.items():
        print("    - %-14s %4.1f x %4.1f mm = %6.2f mm^2"
              % (name, bw, bh, bw * bh))
    print("Randpad-Kante       : %5.2f x %5.2f mm = %8.2f mm^2  "
          "(%d Loecher a %s mm)"
          % (RAND_KANTE, RAND_SILK_TIEFE, RAND_ZONE_FLAECHE,
             RAND_LOECHER, RAND_RASTER))
    print("M3-Freihaltequadrate: 4 x %4.1f x %4.1f mm  = %8.2f mm^2"
          % (M3_KEEPOUT, M3_KEEPOUT, M3_FLAECHE))
    print("-> Pflichtflaechen-Summe (ohne M3)     = %8.2f mm^2"
          % MANDATORY_SUMME)
    print("-> Pflichtflaechen-Summe (mit M3)      = %8.2f mm^2"
          % (MANDATORY_SUMME + M3_FLAECHE))
    print("-> benoetigte Regal-Hoehe (Stapel oben->unten) = %5.2f mm"
          % H_BENOETIGT)
    print("-> M3-Eckloch-Reichweite von der Kante = %4.2f mm "
          "(Lochabstand %s + halber Keepout %s)"
          % (M3_REICHWEITE, M3_RAND_ABSTAND, M3_KEEPOUT / 2.0))

    print()
    print("=== Nutzlast-Referenz: Motormodul v1 ===")
    print("PLACEMENT-Summe (alle Bauteile)        = %8.2f mm^2"
          % PLACEMENT_SUMME)
    print("davon J100..J104 (Vertragsstecker, "
          "bereits oben gezaehlt) = %8.2f mm^2" % STECKER_IM_MOTOR)
    print("-> Motor-Nutzlast (Rest)                = %8.2f mm^2"
          % MOTOR_NUTZLAST)
    print("-> mit Packungsreserve x%.2f            = %8.2f mm^2"
          % (PACKUNGS_RESERVE, NUTZLAST_BEDARF))

    print()
    print("=== Kandidaten ===")
    ergebnisse = []
    for w, h in KANDIDATEN:
        r = pruefe(w, h)
        ergebnisse.append(r)
        status = "PASST" if r["passt"] else "nicht"
        print("%dx%d mm (%.0f mm^2): frei = %.2f - %.2f - %.2f = %.2f mm^2, "
              "Bedarf %.2f mm^2 -> Flaeche %s"
              % (w, h, r["flaeche"], r["flaeche"], MANDATORY_SUMME,
                 M3_FLAECHE, r["frei"], NUTZLAST_BEDARF,
                 "ok" if r["flaeche_reicht"] else "ZU KNAPP"))
        print("    Rand oben (Pico-Zone %.1f mm breit)  = %.2f mm "
              "(braucht >= %.2f mm) -> %s"
              % (PICO_ZONE_L, r["rand_oben"], M3_REICHWEITE,
                 "ok" if r["geometrie_oben"] else "KOLLISION mit M3-Ecke"))
        print("    Rand unten (Randpad-Kante %.2f mm breit) = %.2f mm "
              "(braucht >= %.2f mm) -> %s"
              % (RAND_KANTE, r["rand_unten"], M3_REICHWEITE,
                 "ok" if r["geometrie_unten"] else "KOLLISION mit M3-Ecke"))
        print("    Hoehe %.0f mm (braucht >= %.2f mm) -> %s"
              % (h, H_BENOETIGT, "ok" if r["hoehe_ok"] else "ZU NIEDRIG"))
        print("    => %s" % status)

    passende = [r for r in ergebnisse if r["passt"]]
    if not passende:
        print()
        print("KEIN Kandidat passt -- weder Flaeche noch Geometrie "
              "reichen bei allen dreien.")
        raise SystemExit(1)

    kleinster = min(passende, key=lambda r: r["flaeche"])
    print()
    print("EINHEITSMASS: %dx%d" % (kleinster["w"], kleinster["h"]))


if __name__ == "__main__":
    main()

"""Fertigungsparameter, die fuer alle PicoStack-Platinen gelten, aber
keine Schnittstelle zwischen Modulen sind.

Herkunft: aus tools/stack_spec.py wieder herausgezogen (Etappe 1b,
Aufgabe 1, Nachbesserung nach Pruefung). TRACK_SIGNAL/TRACK_POWER
standen zunaechst dort, mit der Begruendung, dass netclasses.py (setzt
die Projekt-Netzklasse) und autoroute.py (schreibt dieselbe Breite in
die an freerouting uebergebene DSN) dieselbe Zahl lesen muessen -- zwei
getrennte Kopien waren im Vorlaeuferprojekt genau der Grund fuer den
0,20-statt-1,00-mm-Fehler, der das Muttern-Redesign noetig machte.

Diese Begruendung (eine Quelle statt zwei) war richtig, der Ort war es
nicht: tools/stack_spec.py ist die Zusage an fremde Modulbauer, und
tools/vertrag_doku.py erzeugt daraus docs/vertrag.md aus fast allen
Feldern des Moduls -- nur eben nicht aus Bahnbreiten, die dort nie
gezeigt wurden. Ein Wert, den die "einzige Quelle" traegt, aber das
eigene Vertragsdokument verschweigt, ist dasselbe Auseinanderlaufen wie
zuvor, nur diesmal zwischen Modul und Doku statt zwischen netclasses.py
und autoroute.py.

Eine Bahnbreite ist ausserdem keine Schnittstelle, sondern eine
Fertigungsentscheidung dieser konkreten Platinen: wer ein eigenes Modul
entwirft, waehlt seine Bahnbreiten nach seinen eigenen Stroemen, nicht
nach der hier verlegten Platine. Verbindlich fuer ihn sind Umriss,
Lochbild, Steckerbelegung, Typnummern und die Regel fuer den sicheren
Zustand -- das bleibt in tools/stack_spec.py.

VIA_PAD/VIA_DRILL stehen aus demselben Grund hier statt in
netclasses.py selbst: autoroute.py braucht dieselben Werte fuer die von
freerouting zurueckgelieferten Vias, und zwei Kopien waeren wieder das
Muster, das diese Datei gerade vermeiden soll.
"""

TRACK_SIGNAL = 0.25       # mm, Signalbahnen
TRACK_POWER = 1.00        # mm, Leistungsbahnen (Motorausgang, LED-Kanal)
# v2.1, Aufgabe D3: eine DRITTE Breite fuer den 24-V-Stamm.
#
# WARUM ZWEI LEISTUNGSBREITEN STATT EINER. TRACK_POWER (1,00 mm) wurde
# nach der "Recommended"-Spalte von KiCadRoutingTools docs/power-nets.md
# fuer die 2-5-A-Stufe gewaehlt. Nachgerechnet mit IPC-2221
# (I = 0,048 x dT^0,44 x A^0,725, 1 oz, 20 K) traegt sie 3,25 A -- das
# deckt einen LED-Kanal (3,0 A) und einen Motorausgang (2,538 A), aber
# NICHT den Stamm, durch den beides zusammen plus die Stapel-
# Durchleitung muss: stack_spec.STROMBUDGET["modul_gesamt_a"] = 4,0 A
# verlangt 1,335 mm. Bis v2.1 trugen /PWR_IN und /+24V dieselbe
# 1,00-mm-Klasse wie ein einzelner Kanal -- das war der eigentliche
# Entwurfsfehler, den tools/pcb/strombelastung.py aufgedeckt hat (der
# Router hatte daran keine Schuld).
#
# 1,40 mm traegt bei 20 K 4,14 A, also 3,5 % ueber den zugesagten
# 4,0 A. Nicht mehr, weil jede weitere Zehntelmillimeter-Breite den
# Korridor auf einem 82x73-mm-Zweilagenbrett verengt, auf dem das
# Routing schon bei 1,00 mm gekaempft hat (s. task-v21d2-report.md).
TRACK_STAMM = 1.40        # mm, 24-V-Stamm (/PWR_IN, /+24V)

VIA_PAD = 0.60             # mm
VIA_DRILL = 0.30           # mm

# Kupferdicke im Via-Loch (mm).
#
# Gebraucht von tools/pcb/strombelastung.py: ein Via ist im Strompfad
# kein Punkt, sondern ein Leiter mit dem Querschnitt
# pi x Bohrdurchmesser x dieser Dicke. IPC-6012 Klasse 2 verlangt
# 20 um Durchschnitt und 18 um Minimum je Loch; gerechnet wird mit dem
# MINIMUM, nicht mit dem Durchschnitt -- eine Pruefung soll am
# schlechtesten zulaessigen Los nicht knapp durchfallen, sondern am
# schlechtesten zulaessigen Los bestehen.
VIA_KUPFER = 0.018         # mm

# Enddicke der Aussenlagen (mm) und Leiterplattendicke (mm).
#
# 1 oz (35 um) ist JLCs Vorgabe fuer ein 2-Lagen-Brett ohne
# Sonderwunsch; 1,6 mm ebenso (s. hardware/fertigung/ORDERING.md).
# Die Plattendicke ist die LAENGE eines Vias im Strompfad -- ohne sie
# koennte strombelastung.py ein Via nicht gegen seine eigene
# Kurzhals-Grenze halten.
KUPFER_AUSSEN = 0.035      # mm (1 oz)
PLATINE_DICKE = 1.60       # mm

# Wie stark pcbnew den Hof gegenueber der Datei aufblaeht.
#
# Warum es diese Zahl braucht (2026-09-01, Aufgabe 6). Zwei Stellen
# messen denselben Hof, aber verschieden:
#   * tools/stack_spec.py (FOOTPRINT_HOF, und daraus STECKER_POS) liest
#     die ROHEN Polygonkoordinaten aus der .kicad_mod -- der Vertrag
#     soll ohne KiCad lesbar bleiben.
#   * tools/pcb/build.py platziert nach pcbnew GetCourtyard().BBox().
#     pcbnew liefert den mit der Strichbreite GESTRICHELTEN Umriss und
#     rundet das umschliessende Rechteck nach aussen.
# Gemessen an allen zehn Footprints beider Platinen: die pcbnew-Fassung
# ist auf JEDER Seite um exakt 0,045 mm groesser, bei durchgehend
# 0,05 mm Strichbreite (KLC-Regel F5.3 verlangt genau diese Breite fuer
# F.CrtYd, deshalb ist der Wert nicht footprint-abhaengig).
#
# Ohne die Korrektur laege KONTAKT 1 jedes Steckers 0,045 mm neben
# seiner Vertragskoordinate -- auf allen Platinen gleich, also fuer das
# Stecken folgenlos, aber es waere ein bekannter, nicht korrigierter
# Fehler im einzigen Mass, das der Vertrag ueberhaupt zusichert.
# build.courtyard_bbox() zieht ihn deshalb wieder ab, damit Vertrag und
# Platzierung dasselbe Rechteck meinen. tools/pcb/steckerprobe.py
# misst an der FERTIGEN Platine nach, ob Kontakt 1 wirklich dort sitzt
# -- diese Zahl ist damit nicht geglaubt, sondern gegengeprueft.
HOF_STRICH = 0.045         # mm je Seite

# Mindest-Texthoehe auf dem Bestueckungsdruck.
#
# Die KiCad-Vorgabe der Entwurfsregeln ist 0,8 mm; das uebernommene
# build.tidy_silkscreen() schrieb 0,7 mm und erzeugte damit auf jeder
# Platine so viele DRC-Fehler, wie es bedrahtete Bauteile gibt (auf der
# Sockelplatine fuenf). Im Vorlaeuferprojekt fiel das nicht auf, weil
# dort dieselbe Regel offenbar nicht geprueft wurde.
SILK_TEXT = 0.8            # mm
SILK_DICKE = 0.12          # mm Strichstaerke des Textes

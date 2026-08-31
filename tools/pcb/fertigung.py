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
TRACK_POWER = 1.00        # mm, Leistungsbahnen (Motor- und 24V-Strang)

VIA_PAD = 0.60             # mm
VIA_DRILL = 0.30           # mm

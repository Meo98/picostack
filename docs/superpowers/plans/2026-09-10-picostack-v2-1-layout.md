# PicoStack v2.1 — Bedienbares Layout

**Ziel:** Die vier v2-Boards so umbauen, dass man sie tatsaechlich benutzen
kann: Klemmen an den Kanten statt unter dem Pico, lesbarer Siebdruck,
beschriftete Randpads auf der Oberseite.

**Grundlage:** Audit `.superpowers/sdd/2026-09-07-picostack-v2/audit-layout-v2.md`
(1 Blocker, 7 Wichtig, 5 Kosmetik) und Recherche
`.superpowers/sdd/2026-09-07-picostack-v2/recherche-hat-layout.md`
(belegte Regeln aus RP2040-Designguide, HAT-Spec, drei Referenzboards).

## Entscheidungen des Auftraggebers (2026-09-10)

1. **Pico bleibt mittig, das Board waechst.** Der Stapelvertrag
   (STECKER_POS, PIN_ROLLE) bleibt unangetastet.
2. **Randpads wandern auf die Oberseite**, in eine Kantenzone, die ein
   verdreht gestecktes Modul nicht erreicht -- die 1,5-mm-Klausel wird
   NICHT aufgeweicht.

## Zusatzentscheidung des Controllers

3. **Vertragsgeometrie friert ein, nur der Umriss waechst.** Stecker- und
   M3-Positionen behalten ihre Koordinaten; der Rand wandert nach aussen.
   Folge: v2- und v2.1-Boards bleiben untereinander stapelbar (gleiches
   Lochbild, gleiche Steckerlage), die neue Flaeche ist reiner Gewinn.
   Die M3-Loecher sitzen danach nicht mehr in den Ecken -- das ist der
   Preis und mechanisch unkritisch.

## Bindende Layoutregeln (neu im Vertrag, mit Rot-Nachweis)

Aus der Recherche abgeleitet, jede Regel pruefbar:

- **R1 Klemmen an der Kante:** Klemmenkoerper buendig zur Platinenkante,
  Drahtoeffnung nach aussen; kein Klemmen-Hof schneidet PICO_SCHATTEN.
  [belegt: RP2040-Designguide -- Bauteile unter dem Pico duerfen keinen
  manuellen Zugriff brauchen]
- **R2 Eine Reihe je Funktionsgruppe:** alle Lastklemmen eines Moduls auf
  EINER Kante, in Kanalreihenfolge. [belegt: Automation HAT, Adafruit 5095]
- **R3 Bauteilhoehe unter dem Pico:** nichts im PICO_SCHATTEN hoeher als
  der Steckabstand. [belegt: RP2040-Designguide]
- **R4 Klemmenabstaende:** Luft-/Kriechstrecke zwischen benachbarten
  Klemmenkontakten nach IEC 60664 fuer 30 V. [belegt]
- **R5 Kupferabstand zur Kante** >= 2,0 mm. [teilweise belegt]
- **R6 Sichtbare Referenzen:** jedes bestueckte Bauteil traegt seinen
  Referenzbezeichner sichtbar auf F.Silkscreen (nicht F.Fab).
- **R7 Funktionsbeschriftung:** jede Klemme und jeder Stecker traegt neben
  sich seine Funktion im Siebdruck, in Anschlussreihenfolge.
  [belegt: Adafruit 5095, DFRobot 2591]
- **R8 Randpad-Labels:** jedes Randpad traegt sein GP-/Netzlabel im
  Siebdruck.
- **R9 Board-Identitaet:** Name + Vertragsversion + Modultyp im Siebdruck.

## Aufgaben

### A -- Flaechenprobe v2.1
Neues Aussenmass und Zonenaufteilung herleiten (Muster:
`tools/platzprobe_v2.py`): Vertragsgeometrie fest, Umriss waechst;
Kandidaten pruefen; Zonen festlegen fuer Klemmenreihe(n), Randpadzone
auf der Oberseite ohne Landepunkte, Leistungsteil, Nest. Ergebnis:
BOARD_W/H v2.1 + Zonenrechteck-Tabelle, Arithmetik nachvollziehbar
gedruckt.

### B -- Vertrag v2.1
`VERTRAG_VERSION = 3` (oder 2.1, wie es das Schema hergibt), neues
Aussenmass, `KLEMMENZONE`/`RANDPAD_ZONE`, R1-R9 als pruefbare Zusagen,
RANDPADS auf F.Cu mit neuen Koordinaten. Rot-Nachweise zuerst:
Klemmenhof-vs-PICO_SCHATTEN, Randpad-vs-Landepunkte, Kantenabstand.

### C -- Platzierung + Siebdruck aller vier Boards
spec_motor + spec_dimmer_basis auf die neuen Zonen; Klemmen an die
Kante; Gate-Netzwerke zu ihren Kanaelen (Audit W6); Q90-M3-Abstand
(K1), J8-Leistungsstecker-Abstand (K3). Siebdruck-Erzeugung neu:
Referenzen sichtbar (W1/K2), Klemmen- und Steckerbeschriftung (W2/W5),
Randpad-Labels (W3), Board-Identitaet (W7), "KLEMMEN"-Text an die
richtige Stelle oder weg (W4).

### D -- Routing aller vier Boards
Bekannte Pipeline; Technik aus Aufgabe 7/8 wiederverwenden
(billiges build+DRC-Gate ohne Router VOR jedem Wurf, gestaffelte
Haelse, datengetriebene Vorverdrahtung nach Wurfstatistik).

### E -- Fertigungsdaten, Doku, Release v0.3.0
jlc.py nachziehen, Gerber/BOM/CPL neu, ORDERING.md, Website mit neuen
Renders, Release.

## Was erhalten bleibt

Vertrag (Stecker, PIN_ROLLE, M3-Lochbild, Verdrehtklausel), das
MCU-Nest, die Versorgungszelle, alle Schaltplaene (nur Footprint-/
Silkscreen-Aenderungen), die Werkzeugfixes (Guss-Erreichbarkeit,
Netzlisten-Abbruch, Rotationskorrektur) und die Routing-Techniken.

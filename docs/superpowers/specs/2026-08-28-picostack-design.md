# PicoStack — stapelbare Module für den Raspberry Pi Pico

**Stand:** 2026-08-28 · **Status:** Entwurf, freigegeben zur Planung

## Ziel

Ein Baukasten aus stapelbaren Platinen für die Exponate im Espace des
Inventions und im Technorama: ein Sockel mit dem Pico, darunter beliebig
viele Funktionsmodule (Motortreiber, LED-Dimmer in mehreren Grössen).
Die Module hängen an einem Bus statt an einzelnen GPIO-Leitungen, damit
die Zahl der Pico-Pins nicht mehr die Grenze ist.

Gebaut wird zuerst für die eigenen Exponate. Die Schnittstellen werden
aber von Anfang an so geschnitten und dokumentiert, dass eine spätere
Veröffentlichung kein Umbau ist, sondern nur ein Veröffentlichen.

## Ausgangslage

Heute trägt **jede** Funktionsplatine ihren eigenen Pico: die
Motorsteuerung von Pêche aux Canards ebenso wie der vierkanalige
LED-Dimmer. Jede Funktion kostet damit einen ganzen Rechner, und jede
neue Funktion braucht wieder freie GPIO am selben Pico, wenn sie
mitspielen soll.

Zwei Erfahrungen aus diesen beiden Projekten fliessen direkt ein:

- **Die WLAN-Antenne des Pico sitzt zwischen seinen Pin-Reihen.** Auf
  der Motorplatine musste dafür ein Schlitz in die Leiterplatte
  gefräst werden; ein Überhang hätte acht Pins gekostet, darunter beide
  Notaus-Eingänge. Im Stapel wäre die Antenne zwischen zwei Platinen
  eingeklemmt — und das WLAN ist der Wartungszugang.
- **Leistungsbahnen müssen aus der Netzklasse kommen, nicht aus dem
  Layout.** Auf der Muttern-Platine v1 war jede Bahn 0,20 mm breit,
  auch die zum Motor. Ein Router, dem man die Klassen nicht mitgibt,
  wiederholt diesen Fehler klaglos.

## Entscheidungen

| Frage | Entscheidung | Warum |
|---|---|---|
| Zweck | Exponate zuerst, Veröffentlichung mitgedacht | keine zusätzliche Hardware, nur Sorgfalt an den Schnittstellen |
| Modul-Intelligenz | Kleinst-MCU je Modul, vom Pico beflasht | Modul bleibt bei Busausfall handlungsfähig; ein Firmware-Stand für den ganzen Stapel |
| Signalstecker | volle 2×20-Durchreichung des Pico-Pinbilds | maximale Freiheit für fremde Module |
| Leistung | eigener Stecker im Stapel | eine Zuleitung für den ganzen Stapel |
| Antenne | Pico-Sockel immer zuoberst | kein Ausschnitt in den Modulen nötig |
| MCU-Familie | Typ mit dokumentiertem UART-Bootlader | Bootlader nachschlagen statt nachbauen |

## Systemaufbau

Zwei Sorten Platine, gleicher Umriss:

**Sockel** — trägt den Pico, den 5-V-Regler, den Stromeingang und die
Abschlusswiderstände des Busses. Sitzt **zuoberst**; USB und Antenne
zeigen nach oben ins Freie.

**Modul** — trägt einen Kleinst-MCU und eine Leistungsstufe. Beliebig
viele, unterhalb des Sockels.

Der Stapel wächst nach unten. Die Schraubklemmen aller Module liegen
dadurch übereinander an derselben Kante; die Verkabelung des Exponats
bleibt auf einer Seite.

## Mechanik

- Umriss **64 × 60 mm** für alle Platinen, Ecken 3 mm gerundet
- Vier M3-Bohrungen (3,2 mm) je 4 mm von den Kanten
- **15 mm** Abstand zwischen den Platinen — die Schraubklemmen sind
  rund 10 mm hoch, die üblichen 11 mm eines Stapelsteckers wären zu eng
- Abstandsbolzen tragen die Mechanik; die Stecker haben nur
  elektrische Aufgaben

Der Umriss ist bewusst der der bereits entworfenen Motorplatine: er ist
gegen die echten Footprints geprüft und ein passendes Gehäuse
existiert. Ein Ein-Kanal-Dimmer wird darauf überwiegend leer sein — das
ist der Preis dafür, dass jeder Stapel mechanisch aufgeht.

## Die beiden Stecker

**Signal — 2×20, Pico-Pinbild.** Jedes Modul hat *zwei getrennte
Steckerteile*: eine Buchsenleiste oben, eine Stiftleiste unten, in der
Platine Pin für Pin verbunden. Ein echter Stapelstecker wäre hier
falsch: sein langer Stift bildet oben und unten denselben Kontakt, und
damit liesse sich keine Kette bauen, die von Modul zu Modul
weiterwandert.

Reserviert sind:

| Zweck | Anzahl Leitungen |
|---|---|
| I²C (Daten, Takt) | 2 |
| UART zum Flashen (senden, empfangen) | 2 |
| Auswahlkette, von Modul zu Modul weitergereicht | 1 |
| Takt der Auswahlkette (`SEL_CLK`), global | 1 |
| Flash-Modus, global | 1 |
| Notaus, global, wired-OR | 1 |

Alle übrigen Pico-Pins gehen unverändert durch und stehen fremden
Modulen zur Verfügung.

**Leistung — eigener Stecker, nur 24 V und Masse**, mehrere Kontakte
parallel. Getrennt vom Signalstecker geführt, damit Motorströme nicht
neben empfindlichen Leitungen liegen.

## Bus und Adressierung

I²C auf zwei reservierten Pico-Pins. Die **Abschlusswiderstände sitzen
nur auf dem Sockel**, nicht auf den Modulen — sonst wächst die Buslast
mit jedem Modul, und der Bus wird bei sechs Modulen unbrauchbar.

Die **Auswahlkette** erledigt drei Dinge zugleich, und deshalb ist sie
so billig:

1. sie hält alle unbeteiligten Module im Reset,
2. sie wählt genau ein Modul zum Beschreiben aus,
3. sie liefert die Adresse — der Sockel zählt mit, wie weit die Auswahl
   gewandert ist.

Modul Nummer drei ist schlicht das dritte, das geantwortet hat. Keine
Lötbrücken, keine Schalter, und ein Ersatzmodul erbt die Position
seines Vorgängers.

Technisch ist die Kette ein **Schieberegister** über den ganzen
Stapel. Jedes Modul trägt ein D-Flipflop:

- `D` ist die Auswahlleitung vom Modul darüber (beim obersten vom
  Sockel),
- `Q` heisst „ich bin ausgewählt" und ist zugleich die Auswahlleitung
  an das Modul darunter,
- getaktet wird über eine gemeinsame Leitung `SEL_CLK` vom Sockel.

Der Sockel legt eine 1 an und taktet einmal: Modul 1 ist ausgewählt.
Dann legt er 0 an und taktet weiter; die 1 wandert je Takt genau eine
Position tiefer, bis sie unten aus der Kette fällt. Weil im Register
immer nur diese eine 1 steht, ist immer genau ein Modul ausgewählt —
und weil der Sockel die Takte zählt, kennt er damit die Adressen.

Ein Speicher ist dafür unverzichtbar: ohne Flipflop, also rein
kombinatorisch, kann die Auswahl nicht wandern und nur das oberste
Modul wäre je erreichbar.

Dass die anderen im Reset liegen, löst nebenbei ein Problem, das sonst
still zuschlägt: die Sendeleitung ist gemeinsam, und ein zweiter wacher
MCU würde dazwischenfunken. Im Reset ist sein Ausgang hochohmig. Im
Normalbetrieb, wenn alle Module gleichzeitig laufen, sichert das keine
Hardware mehr ab — dort gilt die Auflage im Vertrag, dass Modulfirmware
diese Leitung nicht treiben darf.

**Einschaltzustand.** Ein reales D-Flipflop hat beim Einschalten einen
undefinierten Zustand — anders als die Simulation, die immer mit
`Q=0` beginnt. Steht `Q` mehrerer Module zufällig auf 1, sind mehrere
Modul-MCU gleichzeitig wach und im Bootlader, sobald `FLASH_MODE` zum
ersten Mal auf 1 geht — noch bevor überhaupt ein Takt gelaufen ist —,
und funken sich über dieselbe Sendeleitung gegenseitig zu. Deshalb die
verbindliche Regel: Der Sockel muss die Kette **leertakten**, bevor er
`FLASH_MODE` das erste Mal auf 1 setzt — mindestens so viele Takte mit
einer 0 an `SEL_IN`, wie Module im Stapel stecken können, solange
`FLASH_MODE` noch 0 ist. Erst danach darf er die 1 einschieben.
Alternativ ein Flipflop mit asynchronem Löscheingang, beim Start
angesteuert — das ist der sauberere Weg und erspart das Leertakten,
kostet aber eine Leitung oder ein RC-Glied.

Auf jedem Modul leitet ein kleines Gatter aus dem Flipflop-Ausgang und
dem Flash-Modus die beiden Signale ab, die der MCU braucht (Reset und
die Bootlader-Auswahl):

    RESET = FLASH_MODE ∧ ¬Q        BOOT0 = FLASH_MODE ∧ Q

Liegt der Flash-Modus nicht an, laufen **alle** Module — unabhängig
davon, was im Schieberegister steht.

## Flashen

Ein leerer MCU kann nicht sagen, welcher Modultyp er ist. Statt dafür
Hardware zu bezahlen, läuft das Beschreiben **zweistufig**:

1. Der Sockel schreibt ein winziges Erkennungsprogramm.
2. Das liest zwei Kennwiderstände auf dem Modul und meldet den Typ.
3. Der Sockel schreibt die passende Firmware.

Zwei Widerstände zu je einem Rappen, sonst nichts. Ein fremdes Modul
braucht nur eine Kennung, um mitzuspielen.

Die Firmware-Vorlagen liegen als Dateien auf dem Pico, eine je
Modultyp. Damit hängt der ganze Stapel an einem einzigen Stand, den man
über WLAN aktualisiert — und ein Ersatzmodul aus der Schublade ist nach
dem Aufstecken automatisch aktuell. Kein Programmiergerät im Museum,
kein Laptop.

## Modulfamilie

Jedes Modul besteht aus zwei Teilen:

**Modulsockel** (auf allen gleich): MCU, die zwei Steckerteile, der
Leistungsstecker, zwei Kennwiderstände, Abblockung, das D-Flipflop der
Auswahlkette und das Gatter für Reset und Bootlader-Auswahl. Dieser Block ist das eigentliche Produkt —
wer ein eigenes Modul baut, kopiert ihn und entwirft nur seine
Endstufe.

**Leistungsstufe** (macht den Typ aus). Erste Familie:

| Typ | Inhalt |
|---|---|
| Motor | DRV8876, ein Motor, Strommessung, Notaus-Eingänge |
| Dimmer 1 / 3 / 4 | Low-Side-MOSFET je Kanal, PWM aus dem Modul-MCU |

## Fehlerverhalten

**Zeitwächter im Modul.** Kommt eine halbe Sekunde lang kein gültiger
Befehl, geht das Modul in seinen sicheren Zustand: Motor aus, Kanäle
dunkel. Das gilt für jeden Modultyp gleich — genau dafür ist der eigene
MCU da.

**Notaus-Leitung** durch den ganzen Stapel, die jeder herunterziehen
kann und die ohne Software wirkt.

Der sichere Zustand ist je Modultyp zu definieren und zu
dokumentieren. „Dieses Modul fährt bei Busausfall herunter, jenes
nicht" ist die Sorte Ausnahme, die in einem offenen System später
übersehen wird — es gibt sie deshalb nicht.

## Was fest bleibt

Der Vertrag für alle, die eigene Module bauen. Fünf Dinge, nicht mehr:

1. Umriss, Lochbild und Steckerpositionen
2. Belegung beider Stecker
3. Nummernvergabe für Modultypen
4. Ein kleiner gemeinsamer Registersatz auf dem Bus (Typ, Version,
   Zustand, sicherer Zustand); typeigene Register dahinter
5. Die Regel für den sicheren Zustand

Alles andere darf sich ändern.

## Kosten

Mehraufwand pro Modul gegenüber einer nackten Endstufe: rund **1,40
Franken** (MCU, zwei Steckerteile, Leistungsstecker, zwei
Kennwiderstände, Gatter). Heute trägt stattdessen jede Funktionsplatine
einen eigenen Pico für rund 5 Franken.

Diese Schätzung stammt aus der Fassung vor dem Schieberegister; seither
kommt je Modul ein weiteres Einzelgatter-Gehäuse (das D-Flipflop) dazu.
Der Betrag ist nicht neu ausgerechnet.

**Stapelbarkeit macht ein Modul also rund 3,60 Franken billiger, nicht
teurer.** Der Sockel bleibt einmalig teurer — aber einmal pro Stapel
statt einmal pro Funktion.

## Umsetzung in Etappen

Dieser Entwurf beschreibt mehr, als ein einzelner Umsetzungsplan tragen
kann. Er zerfällt in drei Etappen, jede mit eigenem Plan:

1. **Der Vertrag und der erste Stapel.** Beim Planen hat sich gezeigt,
   dass auch diese Etappe noch zu gross für einen Plan ist; sie
   zerfällt weiter:
   - **1a — Vertrag und Machbarkeitsnachweis.** Steckerbelegung als
     prüfbares Datenmodul, die Auswahlkette als Wahrheitstabelle, das
     Bootlader-Protokoll auf dem Pico, und der Nachweis auf dem Tisch,
     dass der Pico einen Modul-MCU wirklich beschreiben kann. Diese
     Annahme trägt das ganze System — sie wird belegt, bevor
     Leiterplatten darum herum entstehen.
   - **1b — Hardware.** Modulsockel, Sockelplatine, Motormodul.
     **Auflage an die Leitungsführung der Flash-UART:** kurz und
     sauber, keine unnötigen Umwege oder parallel geführten
     Störquellen. Der ROM-Bootlader misst das Sync-Byte `0x7F` über
     einen Timer, um die Baudrate zu bestimmen — das gelingt nur
     unmittelbar nach dem Reset und ist ein Einmalversuch: Ein
     Störimpuls auf der Leitung während dieses Fensters lässt die
     Erkennung scheitern und verlangt einen erneuten Reset (Beleg und
     Einordnung in `docs/nachweis-2026-08.md`, Abschnitt "Wie riskant
     ist die offene Annahme?"). Eine saubere, kurze Leitungsführung
     ist damit keine Layout-Kosmetik, sondern Bedingung dafür, dass
     das Flashen überhaupt zuverlässig anläuft.
   - **1c — Firmware.** Registersatz, sicherer Zustand, Aufzählung
     des Stapels beim Start.
2. **Die Dimmer-Familie.** 1, 3 und 4 Kanäle auf demselben
   Modulsockel — vor allem eine Übung darin, ob der Sockel wirklich
   wiederverwendbar ist.
3. **Veröffentlichung.** Vertrag dokumentieren, KiCad-Vorlage für den
   Modulsockel, Beispielmodul, Lizenz.

Nur Etappe 1 ist mit diesem Entwurf abgedeckt; ein Plan liegt
bisher fuer 1a vor. Etappe 2 und 3 brauchen
je eine eigene Runde, sobald Etappe 1 am Exponat gelaufen ist.

## Prüfung

Die Werkzeugkette aus dem Muttern-Redesign trägt weiter: Spezifikation
als Python-Modul ohne KiCad-Abhängigkeit, Geometrieprüfungen,
Platinenaufbau aus der Netzliste, Netzklassenprüfung, freerouting über
den selbstgebauten SES-Rückweg, DRC als unabhängige Instanz.

Dazu kommt eine **Selbstprüfung im Sockel**: beim Start zählt er den
Stapel durch und meldet, welche Module er gefunden hat. Das ist
zugleich die Inbetriebnahmeprüfung im Museum.

## Nicht-Ziele

- Kein Hot-Plug. Module werden stromlos gesteckt.
- Keine galvanische Trennung zwischen Modulen.
- Kein Ersatz für den bestehenden vierkanaligen Dimmer, solange der
  läuft.
- Keine Rückwärtskompatibilität zu den heutigen Einzelplatinen.

## Offene Punkte

Diese Angaben stehen noch nicht fest und müssen vor der Umsetzung
nachgeschlagen werden — nicht aus dem Gedächtnis entschieden:

- **Welcher MCU genau.** Er muss bei JLCPCB bestückbar sein und einen
  dokumentierten UART-Bootlader im ROM haben. Kandidaten: STM32C0,
  PY32F0.
- **Verhält sich der Bootlader im Reset hochohmig?** Die gemeinsame
  Sendeleitung setzt das voraus. Datenblatt prüfen.
- **Strombelastbarkeit des Leistungssteckers** und daraus die
  Obergrenze für den ganzen Stapel.
- **3,3-V-Budget des Pico** gegen die Zahl der Module.
- **Verfügbarkeit des DRV8876** bei JLCPCB.

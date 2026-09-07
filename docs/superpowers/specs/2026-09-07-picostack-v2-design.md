# PicoStack v2 — Der Pico ist der Stapel

Stand 2026-09-07. Entscheidungen mit Meo abgestimmt (Chat, Bestellrunde
Dimmer4/Sockel). Status: Spec zur Review.

## Kontext und Ziel

v1 braucht zwei Platinen für das kleinste System: Sockelplatine
(Pico-Sitz, 24-V-Einspeisung, 5-V-Regler) + ein Modul. v2 verlegt die
Sockel-Aufgaben auf jedes Modul: **ein Board + ein Pico = lauffähiges
Gerät**, und der Stapel läuft über die Steckleisten des Picos selbst.

Schlüsselbefund aus dem v1-Vertrag: `PIN_ROLLE` beschreibt den
2×20-Stapelstecker BEREITS im Pico-Pinbild (VSYS, 3V3, 3V3_EN, RUN,
ADC_VREF, VBUS, 8×GND, FLASH_TX/RX, I2C, SEL_OUT/SEL_CLK, FLASH_MODE,
NOTAUS, 18× frei). v2 ändert also keine einzige Pinrolle — nur die
**Geometrie**: statt eines 2×20-Blocks (Reihen 2,54 mm auseinander)
zwei **1×20-Durchsteck-Buchsenreihen in echter Pico-Anordnung**
(Reihenabstand 17,78 mm, Raster 2,54 mm, Spann 48,26 mm), sodass der
Pico oben direkt einsteckt und alle 40 Pins den Stapel durchlaufen.

## Beschlossene Grundsätze

1. **v1 ist eingefroren** (Release v0.1.0 bleibt Archiv). Die offenen
   v1-Blocker werden NICHT in v1 nachgeroutet, sondern in v2 gefixt.
2. **Modul-MCU-Nest bleibt wörtlich**: STM32C011-Nest, Kennwiderstände
   und Typcodes, SEL-/NOTAUS-Ketten über die 1×2-Kettenstecker.
3. **Versorgung je Board, Schottky-OR**: jede Platine hat Klemme
   (6–30 V), Verpolschutz, TVS, K7805-1000R3 und speist VSYS über eine
   Schottky-Diode. Beliebig viele bestückte Regler koexistieren; die
   Diode ist zugleich Raspberrys empfohlene Entkopplung gegen
   USB-Rückspeisung beim Flashen.
4. **Alle freien GPIOs als Randpads**: die 18 freien Pins des
   Pinbilds plus mehrere 3V3-/GND-Pads als beschriftete Lötpads
   (2,54 mm, GP-Nummer im Silk) auf zwei Plattenkanten, Position
   vertraglich fixiert (identisch auf jedem Modul).

## Vertrag v2 (`tools/stack_spec.py`)

- `STECKER_POS["stapel"]` wird durch zwei Einträge ersetzt
  (`stapel_links`/`stapel_rechts`, je 1×20) in Pico-Geometrie; die
  40-Pin-Nummerierung folgt dem Pico (Pin 1–20 links, 21–40 rechts),
  `PIN_ROLLE` bleibt unverändert gültig.
- Leistungsstecker 2×2 (24 V/GND doppelt) und beide Kettenstecker
  bleiben wörtlich wie v1 (Positionen dürfen dem neuen Layout folgen,
  Bauformen und Rollen nicht).
- Neu im Vertrag: `RANDPADS` (Liste aus Pico-Pin → Kantenposition +
  Beschriftung) und `VERSORGUNG` (Zusicherungen: Verpolschutz-Topologie
  „Drain an der Einspeisung", Schottky vor VSYS, Regler-Eingangsfenster
  ⊇ 6–30 V).
- Bauform Stapelreihe: PC104-Prinzip (Buchse oben, durchgehender
  langer Stift unten), 1×20. **Beschaffungsrisiko:** 1×20 ist seltener
  als das geprüfte 2×20 (C35165). Fallback ist beschlossen: **2× 1×10
  in Reihe je Seite** (Arduino-Stapelleisten, überall lieferbar);
  der Vertrag beschreibt die Reihe deshalb als Pinpositionen, nicht
  als ein Bauteil.
- Board-Format: **darf wachsen** (Meo, 2026-09-07: „kann auch grösser
  sein wenn nötig — einfach so, dass alles passt"). Die Platzprobe im
  ersten Umsetzungsschritt legt das neue Einheitsmaß fest; es gilt EIN
  Maß für alle Module (Stapel!), M3-Lochbild und verdrehte Landepunkte
  skalieren mit, MONTAGE_REGEL unverändert.

## Versorgungskette je Board (ersetzt die Sockel-Schaltung)

Klemme 3,5 mm (6–30 V) → P-FET-Verpolschutz **korrigiert**: Drain an
der Einspeisung, Source an der lokalen 24-V-Schiene, Gate-Teiler
R11/R12 zwischen **lokaler Schiene** und GND (v1-Blocker: Source lag an
der Einspeisung und R11 am Eingang — Bodydiode + TVS bildeten bei
Verpolung einen Crowbar) → TVS → K7805-1000R3 (C909765, Datenblatt
gelesen: 6,0–30 V Eingang, 5 V/1 A) → Schottky → VSYS. 3V3 erzeugt der
Pico; die Modul-MCUs hängen wie in v1 an 3V3 über den Stapel
(Budget ~300 mA, Lastschätzung ~150 mA bei 8 Modulen).

Die 24-V-Schiene läuft zusätzlich über den 2×2-Leistungsstecker durch
den Stapel: EIN eingespeistes Board versorgt alle.

Offen für die Umsetzung (mit Datenblatt-Beleg zu entscheiden): TVS-Typ
— SMCJ30A klemmt bei 33–48 V, der Regler verträgt 30 V; geprüft wird,
ob eine niedriger klemmende TVS (z. B. SMCJ28A) das Fenster schließt,
ohne bei 30-V-Dauereingang zu leiden.

## Aus dem v1-Review übernommene Fixes (alle in v2 enthalten)

1. **Notaus-Treiber U6/U7: SN74LVC1G07 (C7830) statt 1G06** —
   nichtinvertierender OD-Buffer, pinidentisch. v1 war fail-unsafe
   (intakte Schleife sperrte den Motor, Drahtbruch gab frei).
2. **Verpolschutz-Topologie** (s. oben) auf Motor UND Dimmern.
3. Schaltplan↔PCB-Wertesync (NCE6020AK/SS36C überall).
4. MPN-/LCSC-Felder als Symbol-Properties in allen Generatoren
   (BOM-Export wird selbsttragend).
5. 100-nF-Abblockung an jedem Einzelgatter; 3V3-Bulkkondensator je
   Board.
6. Dimmer-PWM Kanal 3/4 von PC14/PC15 auf reguläre Port-A-Pins.
7. Dangling-Via-Bereinigung als Pipeline-Schritt.

## Rot-Nachweise (neu in der Testsuite)

- Verpolschutz-Probe: Drain-Pad des Schutz-FETs MUSS am
  Einspeisungsnetz liegen, Gate-Teiler an der lokalen Schiene
  (Netzlisten-Check je Board; wird rot auf jedem v1-Board).
- Notaus-Polaritätsprobe: Schleife-HIGH ⇒ NOTAUS freigegeben
  (Bausteinliste + Netzkette; wird rot mit 1G06).
- Schottky-Probe: zwischen Reglerausgang und VSYS liegt eine Diode.
- Randpad-Probe: jeder als „frei" deklarierte Pin hat genau ein
  beschriftetes Randpad an der Vertragsposition.

## Migration und Versionierung

- Repo: v1-Stände bleiben unter Release v0.1.0; `stack_spec.py`
  bekommt `VERTRAG_VERSION = 2`; Sockelplatine wird als „v1-only"
  markiert (Generator + Fertigungsdaten bleiben im Baum, README-Hinweis).
- Website/README: v2-Story („one board + a Pico"), neue Renders.
- Module v2: Motor, Dimmer1/3/4 (gleiches Typcode-Schema).

## Risiken

1. 1×20-Stapelleisten-Beschaffung → Fallback 2×1×10 (beschlossen).
2. Platz: zwei Stapelreihen + Leistungsteil + Randpads brauchen mehr
   Fläche als v1 hergab — entschärft durch das freigegebene
   Board-Wachstum. Die Platzprobe (erster Umsetzungsschritt) rechnet
   das dichteste Modul (Motor) durch und legt daraus das neue
   Einheitsmaß fest; Randpad-Ausnahmen je Modul gibt es nicht, der
   Vertrag gilt für alle gleich.
3. 1-A-Budget des Reglers: trägt Logik locker; wer 5-V-Lasten will,
   braucht ein eigenes Modul (dokumentierte Grenze).

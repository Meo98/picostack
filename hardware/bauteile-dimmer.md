# Bauteil-Belege Dimmer-Module (1/3/4 Kanäle)

Die Dimmer übernehmen das MCU-Nest wörtlich vom Motormodul; deren
Nummern sind in `bauteile.md` / `bauteile-1b.md` belegt. Hier stehen
nur die Positionen, die es NUR auf den Dimmern gibt bzw. die für die
Bestückungs-Bestellung 2026-09-04 neu gesichtet wurden. Regel wie
immer: eine LCSC-Nummer steht nur hier, wenn die Produktseite selbst
geöffnet und gelesen wurde.

| Position | Bauteil | Gehäuse | LCSC | gesichtet | Beleg |
|---|---|---|---|---|---|
| Freilaufdiode D1–D4 | SS36**C** (MDD/Microdiode) | **SMC (DO-214AB)** | C16237 | ja | LCSC-Produktseite `lcsc.com/product-detail/C16237.html` (Rohdaten: „SMC(DO-214AB)", 60 V, 3 A, „700mV@3A", Lager 102 720). **Falle:** das MDD-Teil mit dem nackten Namen „SS36" (C16015) ist laut seiner Produktseite **SMA (DO-214AC)** — falsches Gehäuse für unsere Pads. Das onsemi-SS36 in SMC (C391251) existiert, hatte am Recherchetag aber nur 847 Stück Lager bei ~0,37 $ |
| Gate-Vorwiderstand RG1–RG4 | 0805W8F1000T5E (UNI-ROYAL), 100 Ω ±1 % | 0805 | C17408 | ja | LCSC-Produktseite `lcsc.com/product-detail/C17408.html` (Rohdaten: „100Ω", „±1%", „125mW", „150V", Lager 8 236 700). Gleiche geprüfte Baureihe wie der 10-kΩ-Beleg C17414 in `bauteile-1b.md` |
| Stütz-Elko C12 (auch C3 Sockel, C12 Motor) | GR227M035F12RR0VL4FP0 (Chengx) | radial D8×L12, RM 3,5 | C45078 | ja | LCSC-Produktseite `lcsc.com/product-detail/…C45078.html` (Rohdaten: „220µF ±20%", „35V", „8mm × 12mm", „Lead Pitch: 3.5mm", „3000hrs@105℃", Lager 123 720) |
| Schraubklemme J5–J8 | KF350-3.5-2P (Cixi Kefa) | THT, RM 3,5, 2P | C474892 | ja | LCSC-Produktseite `lcsc.com/product-detail/C474892.html` (Rohdaten: „3.5mm", „1x2P", „10A", „300V", „18–24 AWG", M2-Schraube, Lager 7 100). **Ehrlich vermerkt:** das ist ein Klon auf dem Raster des Phoenix-PT-1,5/2-3,5-H-Footprints, keine Maßzeichnungs-Gegenprüfung Pad für Pad — Sitz im JLC-Bestückungs-Preview kontrollieren. Der Phoenix-Originaltyp war bei LCSC nicht auffindbar |

Die übrigen Dimmer-BOM-Nummern (STM32C011F6P6 C5456198, 74LVC-Gatter
C202238/C206109/C7832, IRFR5305 C2624, SMCJ30A C340696, NCE6050KA
C96013, 10 kΩ C17414) sind in `bauteile.md` / `bauteile-1b.md` bzw. im
LED-Dimmer-Altprojekt belegt und in `tools/jlc.py` als Konstanten
übernommen.

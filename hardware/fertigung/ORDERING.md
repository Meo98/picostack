# Ordering an assembled PicoStack v3 board at JLCPCB

Applies to `dimmer1`, `dimmer3`, `dimmer4`. **No v3 board has been
manufactured yet** — the first order is the real test of this document.

## Files you need (already in `hardware/fertigung/<board>/`)

| File | What for |
|---|---|
| `<board>-gerber-jlc.zip` | the PCB itself (upload as-is) |
| `jlc-bom.csv` | bill of materials, JLC column layout, LCSC numbers where verified |
| `jlc-cpl.csv` | pick-and-place positions (pad centroids for THT families) |
| `UNBESTUECKT.txt` | every position that is deliberately not assembled, with the reason |

Regenerate them with `tools/fertigung.sh <board>` after any change (it
refuses to run on a board whose DRC is not clean).

## Step by step

1. **jlcpcb.com → "Instant Quote"**, upload `<board>-gerber-jlc.zip`.
   2 layers, 1.6 mm, 74 × 58 mm. Surface finish: HASL is fine; choose
   ENIG if you want the 0603 matrix easier to rework.
2. **PCB Assembly: on**, top side only, 5 boards is the minimum.
3. Upload `jlc-bom.csv` and `jlc-cpl.csv`.
4. **Check the BOM match.** Lines without an LCSC number (currently
   `100uF 16V SMD-Elko 6.3x7.7`, C94) must be matched by hand: pick a
   6.3 × 7.7 mm SMD electrolytic, 100 µF, ≥ 10 V. Lines *with* a number
   should match automatically; if JLC reports a shortfall, pick the same
   value in the same package from the Basic library (0603/0805/1210 passives
   are all generic).
5. **Check the placement preview, part by part.** This is where v1 cost
   money. Known traps:
   - `U90` (TPS5430, SOIC-8-EP): the rotation correction for SOIC-8 in
     `tools/jlc.py` is a guess until the first order confirms it. Pin 1
     (dot) must sit at the top-left of the footprint as drawn in KiCad.
   - `Q1..Q4` (TO-252, tab down) and `Q90` (TO-252, tab down): the tab is the
     wide pad toward the terminals / toward the bottom of the board.
   - `D90`, `D91`, `D93`, `D1..D4` (SMC): cathode band on the side the
     footprint marks.
   - `C90`, `C94` (SMD electrolytic): "+" towards the silk marker.
   - `L90` (6 × 6 inductor): no polarity.
   - `J4` (JST SH Qwiic): opening towards the board edge.
6. Order. Hand-populate after arrival (see below).

## Unpopulated by design (hand-soldered after arrival)

- `J1`, `J2`: Pimoroni Pico Stacking Headers (1×20, socket 8.5 mm, pin 11 mm).
- `J3`: a 1×4 piece cut from the same stacking header.
- `J10`: 1×6 pin header, 2.54 mm.
- `JA*`, `JC*`, `JD*`: the three non-default rows of the bank matrix. To
  move a module to another bank, desolder the four 0603 bridges in the `JB`
  row and place them in the row of the new bank. Column = signal,
  row = bank (silkscreen: C, D, A, B from top).

Solder the stacking headers **in the plugged-together stack**, with the
Pico in place: that is the only way the contacts line up without strain
(`MONTAGE_REGEL`: plug first, then screw the standoffs — 12 mm M3).

## After the boards arrive

1. Before any Pico: 6–30 V on `J90`, check 4.9 V after `D93`/`L90` (on
   `C94`) and ~4.5 V on VSYS (pin 39). The green LED must light.
2. Reverse the supply briefly: nothing must get warm, LED off.
3. Pico on USB only, no terminal supply: `picostack.Dimmer()` must run and
   the FET gates must toggle (scope on `RG` pads).
4. Both supplies at once: no current into the USB host (measure on the
   USB lead), VSYS stays at the higher of the two.
5. Load a channel with 3 A for 10 minutes: FET tab hand-warm, trunk cool.
6. Write what you measured into `docs/` — that is the first time a v3
   board exists outside this repository.

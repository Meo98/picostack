# Ordering an assembled board at JLCPCB

Covers the four **v2** boards: **Motormodul** (motor), and the **Dimmer**
family (dimmer1, dimmer3, dimmer4 — 1/3/4 LED channels). Same steps for
each; screenshots below use Dimmer4, the largest of the four.

The v1 **Sockelplatine** is **not part of the v2 product line** anymore —
its role (Pico carrier + 24 V supply) is now built into every module as
the versorgung cell (J90/Q90/R90/R91/D90/C90/U90/C91/D91). Its files under
`hardware/fertigung/sockel/` are kept for archive purposes only; do not
order it as a v2 deliverable, and do not copy its steps below without
checking against a current v2 board first — some of what changed between
v1 and v2 (see the traps section) started life as a v1 mistake on this
exact board.

## Files you need (already in `hardware/fertigung/<board>/`)

| File | Used for |
|---|---|
| `<board>-gerber-jlc.zip` | the PCB itself (upload as-is) |
| `jlc-bom.csv` | parts list, JLC BOM format |
| `jlc-cpl.csv` | pick-and-place positions, JLC CPL format |
| `UNBESTUECKT.txt` | what you will solder / fit by hand, and why |

## Step by step

1. **jlcpcb.com → "Instant Quote"** and upload `<board>-gerber-jlc.zip`.
   JLC should detect the board outline (64 × 60 mm on all four v2 boards)
   and 2 layers. Keep the defaults (FR-4, 1.6 mm, HASL, any colour,
   qty 5 — that is the minimum).
2. Toggle **"PCB Assembly"** on. Choose *Economic*, *Top side* — every
   populated part on all four boards sits on the top layer; nothing on
   the bottom is machine-placed (see "unpopulated by design" below).
   Assembly quantity 2 is usually enough for prototypes.
3. Upload `jlc-bom.csv` and `jlc-cpl.csv` when asked.
4. **Check the part matching page carefully.** Most BOM lines carry an
   LCSC part number that was verified against the actual LCSC product
   page (see the constants at the top of `tools/jlc.py` and the evidence
   trail in `hardware/bauteile*.md`) — those match automatically. The
   remaining lines (a few small parts with no verified number, e.g. the
   DRV8876 on the Motormodul, the Notaus pin header, the current-limit
   resistor position) are either matched by JLC from their description or
   deliberately left for you to source/solder — check `UNBESTUECKT.txt`
   and the BOM comment text for each blank LCSC field.
5. **Check the placement preview.** JLC's rotation convention differs
   from KiCad's for some packages — this project already applies a
   correction table in `tools/jlc.py` (`ROT_KORREKTUR`: SOT-353/363
   +180°, TSSOP +270°, VSSOP-8 +180°) and pad-centroid positions for the
   THT families (`tools/pcb/zentroide.py`: terminal blocks, the
   electrolytic, the DC/DC converter). Still **verify pin-1 / cathode
   orientation** in the render for U100 (MCU, TSSOP-20), U101–U103 and
   U6/U7 (SC-70/SOT, VSSOP), the diodes (D90 TVS, D91 and D1–D4
   Schottky), and both MOSFET families (Q90 IRFR5305, Q1–Q4 NCE6020AK on
   the dimmers) — this is the step that catches most assembly mistakes,
   and the correction table does not cover every footprint (TO-252 and
   the DO-214AB diodes are deliberately NOT in it, see the comment above
   `ROT_KORREKTUR`).
6. If JLC flags THT parts (C90 electrolytic, J5/J90/J6–J8 terminals) as
   not assemblable in Economic: deselect them and solder them yourself —
   they are the easiest parts on the board.
7. Order. The stack connectors (J100, J105, J101–J104) are **hand-fitted
   on purpose** (see `UNBESTUECKT.txt` and `stack_spec.MONTAGE_REGEL`):
   solder them in the mated stack so the contacts align without strain.
   J95/J96 (the edge-pad rows) are also unpopulated — see below.

## Unpopulated by design

Every v2 board carries two rows of bare solder pads along one edge —
`J95` (18 GPIO) and `J96` (2× 3V3 + 2× GND), `stack_spec.RANDPADS`. They
are **never meant to be assembled**: they exist so a finished module can
be probed or hand-wired to a free GPIO without opening the stack. Both
are SMD pads on the bottom copper layer (`B.Cu`) — this is new in v2 (v1
had no equivalent). Because they are always unpopulated, **the
bottom-layer change has no effect on `jlc-cpl.csv`**: nothing on the
bottom side of any v2 board is ever machine-placed (the only other
bottom-side footprints, J102/J104, were already hand-soldered stack
connectors before this change) — checked board by board against
`pos.csv`/`jlc-cpl.csv` while building this fabrication data, not
assumed.

The stack connectors (J100/J105 left/right Pico rows, J101–J104 chain and
power connectors) are likewise always in `UNBESTUECKT.txt`: they must be
soldered **in the mated stack**, after stacking, so the contacts align
without strain (`MONTAGE_REGEL`). J105 is new in v2 — v1 had a single
2×20 stacking header (`J100`); v2 splits it into two 1×20 sockets
(`J100` pins 1–20, `J105` pins 21–40).

## Traps that already cost real money in v1 — check these every time

- **JLC's placement-preview rotation check is not optional.** The
  correction table in `tools/jlc.py` fixes the *known* package families;
  it does not guarantee every footprint. A wrongly-rotated part that
  slips through the preview is a wrong assembly, not a wrong file.
- **SS36C (SMC / DO-214AB) is not SS36 (SMA).** The free-wheeling and
  VSYS diodes on every v2 board are **SS36C**, LCSC **C16237** — MDD's
  plain "SS36" (**C16015**) is the smaller SMA package and does not fit
  these pads. Confirm the footprint column reads `D_SMC`, not an SMA
  package, before accepting JLC's auto-match.
- **R100/R101 encode the module type — never "optimise" them to a
  common value.** They are read back by the module's own firmware at
  boot (`stack_spec.TYPCODE_WIDERSTAENDE`) to tell modules apart; a well
  -meaning BOM cleanup that merges "two identical-looking resistor rows"
  into one silently bricks the type detection. This is not theoretical:
  on **Dimmer3** (type code 0x11), R100 *and* R101 both resolve to the
  **same value, 680 Ω** (`TYPCODE_WIDERSTAENDE(0x11) == (680, 680)`) —
  two BOM rows, same value, same footprint, and still two electrically
  and semantically distinct designators that must stay on separate rows.
  Do not let anyone "simplify" that away because the values match.

## After the boards arrive

- Populate the connectors and any deselected THT parts.
- Flash the module MCU through the stack (or SWD for the first board).
- Please open an issue with photos — the first real-world build report
  is worth more than any simulation.

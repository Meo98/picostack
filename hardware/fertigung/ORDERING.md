# Ordering an assembled board at JLCPCB

Worked example: **Dimmer4** (the four-channel LED dimmer). The same steps
apply to every board in this directory.

## Files you need (already in `hardware/fertigung/<board>/`)

| File | Used for |
|---|---|
| `dimmer4-gerber-jlc.zip` | the PCB itself (upload as-is) |
| `jlc-bom.csv` | parts list, JLC BOM format |
| `jlc-cpl.csv` | pick-and-place positions, JLC CPL format |
| `UNBESTUECKT.txt` | what you will solder by hand, and why |

## Step by step

1. **jlcpcb.com → "Instant Quote"** and upload `dimmer4-gerber-jlc.zip`.
   JLC should detect 64 × 60 mm, 2 layers. Keep the defaults
   (FR-4, 1.6 mm, HASL, any colour, qty 5 — that is the minimum).
2. Toggle **"PCB Assembly"** on. Choose *Economic*, *Top side*,
   assembly quantity 2 (you rarely need 5 assembled prototypes).
3. Upload `jlc-bom.csv` and `jlc-cpl.csv` when asked.
4. **Check the part matching page carefully.** Most BOM lines now carry
   an LCSC part number that was verified against the actual LCSC
   product page (see the constants at the top of `tools/jlc.py` and the
   evidence trail in `hardware/bauteile*.md`) — those match
   automatically. The remaining lines (small ceramics, a few resistor
   values) are matched by JLC from their description: confirm package +
   value for each, and pick the *Basic* part where offered (Extended
   parts cost a one-time feeder fee each). Two footguns:
   - the free-wheeling diode is **SS36C** (C16237, SMC/DO-214AB) — the
     MDD part named plain "SS36" (C16015) is the smaller SMA package
     and does **not** fit the pads;
   - the two ID resistors R100/R101 encode the module type — do not
     "optimise" them to a common value.
   The screw terminals J5–J8 are matched to the KF350-3.5-2P (C474892),
   a 3.5 mm THT block on the Phoenix-PT footprint pattern — check its
   fit in the placement preview.
5. **Check the placement preview.** JLC's rotation convention differs
   from KiCad's for some packages: verify pin-1 / cathode orientation
   of U100, U101–U103, the diodes and both MOSFET types against the
   board render, and rotate parts in the preview tool if needed. This
   is the step that catches 90 % of assembly mistakes.
6. If JLC flags the THT parts (C12 electrolytic, J5–J8 terminals) as
   not assemblable in Economic: deselect them and solder them yourself —
   they are the easiest parts on the board.
7. Order. The stack connectors are hand-fitted on purpose (see
   `UNBESTUECKT.txt`): solder them in the mated stack so the contacts
   align without strain.

## After the boards arrive

- Populate the connectors and any deselected THT parts.
- Flash the module MCU through the stack (or SWD for the first board).
- Please open an issue with photos — the first real-world build report
  is worth more than any simulation.

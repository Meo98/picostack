# Contributing to PicoStack

Thanks for wanting to build on this! PicoStack is meant to grow into a
family of stackable Pico modules made by many hands — new hats, better
tooling, firmware in whatever language you like. This document explains
how the project works and what a good contribution looks like.

## The one rule that shapes everything: checks must be able to turn red

Every calculated dimension, every generated file and every "this is safe"
claim in this repository is treated as a promise — and a promise needs a
check **plus a demonstration that the check fails when the promise is
broken**. We call this the *red proof*.

The reason is documented all over the code: during development, KiCad's
ERC and DRC caught **none** of the real bugs (mirrored connector contacts,
broken arc geometry, stale generated schematics, a solder-mask margin that
merged neighbouring pad openings, …). Custom gates with red proofs caught
all of them.

Practically:

- If your PR adds a rule, add a test under `tests/` and show in the PR
  description (or a code comment) how you made it fail once.
- If your PR adds a generated artifact, wire it into
  `tests/test_erzeugte_dateien.py` so a stale copy can never sneak in.

Run everything with:

```bash
python3 tests/run_all.py
```

No pytest needed — each suite is a plain script.

## How the toolchain fits together

```
tools/stack_spec.py        the CONTRACT: connector positions, pin roles,
                           keep-outs, landing-point copper rules, mating rule.
                           Machine-readable; docs and tests are derived from it.

tools/sch/gen.py           tiny schematic writer (S-expressions, self-check)
tools/sch/<board>.py       one generator per board -> hardware/kicad/.../<board>.kicad_sch

tools/pcb/spec_<board>.py  placement, pre-routes, stitching vias -- pure Python,
                           importable without KiCad
tools/pcb/build.py         builds a fresh .kicad_pcb from netlist + spec
tools/pcb/verlegen.sh      the whole routing recipe as one command: power
                           nets first on bare copper, widen, then signals
tools/pcb/autoroute.py     freerouting 2.3 headless, DSN repair, SES import
                           -- the v1/v2 path, superseded by verlegen.sh
tools/pcb/masseheiler.py   finds isolated ground-copper clusters after routing
                           and heals them (vias, bridges, or removal)
tools/pcb/steckerprobe.py  measures the BUILT board against the contract
tools/pcb/strombelastung.py  measures the current every routed segment and via
                           must carry (from the per-pad declaration) against
                           its IPC-2221 ampacity -- REQUIRED before fab data
tools/pcb/stammtrennung.py  splits low-current taps off a power net for the
                           two-pass routing recipe (the router's MST is
                           geometric and would otherwise daisy-chain the
                           trunk through milliamp taps)
tools/pcb/strombudget_druck.py  stamps the contract's current budget on the
                           silkscreen
tools/pcb/kipy             launcher that runs a script inside KiCad's Python
```

### Requirements

- **KiCad 10** (with Python bindings; `tools/pcb/kipy` finds them)
- **Python 3.12+** for the plain suites
- **freerouting 2.3.0** as a JAR in `~/.local/share/freerouting/`
  (grab it from the [freerouting releases](https://github.com/freerouting/freerouting/releases))
  and a **Java ≥ 25** runtime. Version 2.2.x hangs on some exported DSNs —
  `tools/pcb/autoroute.py` documents that story; don't downgrade.

### Rebuilding a board end to end

```bash
python3 tools/sch/motormodul.py                       # schematic
tools/pcb/kipy tools/pcb/build.py spec_motor \
    hardware/kicad/motor/Motormodul.kicad_pcb \
    hardware/kicad/motor/Motormodul.kicad_sch          # placement etc.
tools/pcb/kipy tools/pcb/autoroute.py \
    hardware/kicad/motor/Motormodul.kicad_pcb spec_motor
tools/pcb/kipy tools/pcb/masseheiler.py \
    hardware/kicad/motor/Motormodul.kicad_pcb          # ground healing
kicad-cli pcb drc --severity-error \
    hardware/kicad/motor/Motormodul.kicad_pcb          # must be clean
tools/pcb/kipy tools/pcb/steckerprobe.py spec_motor \
    hardware/kicad/motor/Motormodul.kicad_pcb          # contract geometry
tools/pcb/kipy tools/pcb/strombelastung.py \
    hardware/kicad/motor/Motormodul.kicad_pcb spec_motor   # ampacity gate
```

**The ampacity gate is not optional.** `strombelastung.py` needs `pcbnew`,
so it cannot run inside `tests/run_all.py` (that suite is plain Python) --
exactly like `masseheiler.py`, `steckerprobe.py` and `pcb_checks.py`. It is
therefore a required step of this recipe, and `tests/test_strombudget.py`
keeps the KiCad-free half honest: it re-derives the current budget from the
component datasheet figures in the contract, checks that the committed net
classes really carry those currents, and goes red if this file or README.md
stops naming `strombelastung.py`.

Power nets are routed **first, alone, on bare copper** -- three router
runs, not one. Two independent findings forced this:

* The router builds a minimum spanning tree over a net's pad coordinates
  -- geometry only, no current -- and on every one of these boards it
  chained the 24 V trunk straight through the gate divider (1.3 mA) and a
  freewheel diode, where no 1.8 mm corridor exists.
  `tools/pcb/stammtrennung.py --abtrennen` temporarily detaches every pad
  whose declared current fits in the signal width, so the spanning tree
  becomes the trunk by itself; `--anheften` puts them back afterwards.
* Signal nets routed earlier occupy the corridors the trunk needs. Measured
  on Dimmer1: with the previous run's signal copper still in place the
  router delivered a 133 mm trunk with a 0.25 mm bottleneck; on bare copper
  (`stammtrennung.py --kupfer-weg` first) it delivered 71 of 79 mm at the
  full 1.40 mm without a single "wide route blocked". The corridor was
  there all along -- it was occupied.

```bash
S=tools/pcb; B=hardware/kicad/dimmer4/Dimmer4.kicad_pcb; SPEC=spec_dimmer4
python3 $S/netclasses.py hardware/kicad/dimmer4/Dimmer4.kicad_pro $SPEC
$S/kipy $S/stammtrennung.py --kupfer-weg     $B          # bare copper
$S/kipy $S/stammtrennung.py --vorverdrahtung $B $SPEC    # put PRE_TRACKS back
# fine-pitch parts only (Motormodul): escape U1's pins BEFORE the trunk
# claims that corridor -- qfn_fanout.py --component U1 --escape-method stub
$S/kipy $S/stammtrennung.py --abtrennen      $B $SPEC abzweige.json
# run 1: only /PWR_IN /+24V /LEDn, --ordering original, --escalation off,
#        power widths from fertigung.TRACK_STAMM / TRACK_POWER
$S/kipy $S/stammtrennung.py --anheften       <routed> abzweige.json
# run 2: the same power nets again at 0.25 mm -- hangs the taps on while
#        the board is still empty (doing this after the signals fails)
$S/kipy $S/stammverbreiterung.py $B $SPEC   # widen NOW, while it is empty
$S/kipy $S/stammtrennung.py --sperren        <routed> $SPEC
# run 3: --nets '*' -- everything else; the locked power copper survives
$S/kipy $S/stammtrennung.py --entsperren     <routed> $SPEC
$S/kipy $S/masseheiler.py       $B          # heal the ground pour
```

**Widen before the signals, not after.** `stammverbreiterung.py` can only
use space that is still free, so it belongs between run 2 and run 3 --
while the board carries nothing but power copper. Measured on the
Motormodul, same board, same segment: widening after the signal run
reached 0.300 mm, widening before it reached the full 1.335 mm. Locking
the power copper (`--sperren`) then keeps run 3 from undoing it.

`--vorverdrahtung` is not optional. `--kupfer-weg` removes *all* copper,
including the hand pre-routes the board description carries
(`spec_*.PRE_TRACKS`/`PRE_VIAS`) -- and those exist precisely because
"only what the router fundamentally cannot do is pre-wired": same-net
adjacent pads of a VSSOP-8 on a 0.5 mm pitch, the walled-in ground pad of
a SC-70-5. Without them the same four nest nets (`/SEL_OUT`, `/NRST`,
`3V3`, `/NQ`) failed in every single run on every board.

`stammverbreiterung.py` closes the last gap: the router necks a handful
of short stub segments down to 0.25 mm even on a bare board. The tool
widens each of them, step by step, as far as the clearance to foreign
copper allows -- real extra copper, not a loosened tolerance, the same
approach `via_weld.py` takes. Where the centre is wrong rather than the
space missing, it steps the segment sideways first: a KiCad track only
grows around its own centreline, so a trunk running close to a pad row
stops short of its required width even when the other side is empty
(measured: 1.320 mm against 1.335 mm needed, 26 mm long, alongside the
J105 pin row -- 0.05 mm of offset was the whole fix). Neighbouring
segments do not move; they stay connected because their endpoints remain
inside the widened copper, and DRC confirms it afterwards.

Routing is *not deterministic* (net ordering and rip-up decisions vary) —
the committed board file is the artifact of record, and the DRC + probe
suite is what makes it trustworthy, not the ability to regenerate it
bit-identically.

## Proposing a new module (a new "hat")

1. Open an issue with the **New module proposal** template. One paragraph
   on what the module does, which contract pins it uses, and rough BOM.
2. Copy `tools/sch/motormodul.py` and `tools/pcb/spec_motor.py` as
   starting points. Compute every contract-derived position through
   `stack_spec` helpers — never hardcode contract coordinates.
3. The landing-point rule is the one that protects everyone else's
   boards: no exposed copper in the areas where a rotated stack's pins
   would land. `tools/pcb/steckerprobe.py` measures it for you.
4. Add `tests/test_spec_<yourmodule>.py` (mirror an existing one).
5. PR with: green `tests/run_all.py`, clean DRC, and renders of both
   sides (`kicad-cli pcb render`).

Firmware lives per module and can be written in **any language** that
targets the module's MCU — C, MicroPython, Rust, Arduino. Keep it in
`firmware/<module>/` with its own README.

## Language

Public documentation is English. The existing code comments are German —
they encode the full engineering rationale (why a value is what it is,
which bug motivated a check) and are being translated gradually; a
translation PR that *preserves the reasoning* is a very welcome
contribution. New code and comments should be English.

## Style

- Python: stdlib only where possible, no frameworks. Match the existing
  comment style: explain *why*, cite the bug or datasheet section that
  motivated the code, and never write comments that merely restate the
  next line.
- Keep tools KiCad-free unless they must touch a board — everything a
  test imports should run with plain `python3`.

## Licensing of contributions

By contributing you agree that your hardware contributions are licensed
under CERN-OHL-S-2.0 and your code contributions under GPL-3.0-or-later,
the project licenses. Please add SPDX headers to new files.

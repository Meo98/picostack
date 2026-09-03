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
tools/pcb/autoroute.py     freerouting 2.3 headless (see below), DSN repair,
                           SES import with dedup
tools/pcb/masseheiler.py   finds isolated ground-copper clusters after routing
                           and heals them (vias, bridges, or removal)
tools/pcb/steckerprobe.py  measures the BUILT board against the contract
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
```

Routing is *not deterministic* (freerouting single-thread still varies) —
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

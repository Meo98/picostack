# Contributing to PicoStack

Thanks for looking. This file explains how the repository works, how a
board goes from Python to fab files, and what a new module must respect.

## One rule above all: checks must be able to turn red

Every number that was calculated is a promise. A promise gets a test, and
the test gets a *red proof*: a deliberately broken input it must reject.
`tests/run_all.py` runs every suite without KiCad; the suites that need
pcbnew live in `tools/pcb/` and are run by `verlegen_v3.sh`.

ERC and DRC are gates too, but they have caught none of the real bugs in
this project. Nachrechnen hat sie gefunden.

## Toolchain

- KiCad 10 (`kicad-cli` on PATH; `tools/pcb/kipy` runs a script inside
  KiCad's Python so `import pcbnew` works)
- Python 3 for everything else, no third-party packages
- [KiCadRoutingTools](https://github.com/drandyhaas/KiCadRoutingTools)
  cloned to `~/Dokumente/Tools/KiCadRoutingTools` (or set `KRT=`), with
  numpy/scipy/shapely available — `verlegen_v3.sh` opens a nix-shell for it

## From contract to fab files

```text
tools/stack_spec.py          the contract (v4): geometry, pin roles, banks,
                             stack height, supply assertions, layout rules
tools/sch/versorgung.py      the supply cell every module shares
tools/sch/dimmermodul.py     schematic generator (1/3/4 channels)
tools/pcb/spec_dimmer_basis.py  placement, pre-wired trunk, labels
tools/pcb/verlegen_v3.sh <board>   schematic → ERC → build → netclasses →
                             router (power, then signals) → via tenting →
                             ground healing → DRC → probes
tools/fertigung.sh <board>   gerbers, drill, pos, centroids, BOM, CPL
```

Placement is written as numbers (`Platz(ref, x, y, w, h, rot)`), by
current path: switch above its terminal, bypass caps at their pins, the
buck loop tight, the 4 A trunk pre-wired at 1.4 mm. `tests/test_spec_dimmer.py`
checks the numbers against the contract (overlaps, edges, M3 keep-outs,
antenna zone, P1–P4 distances) before any board is built.

The router is only allowed to fill in what placement left open. If it
narrows a power net (`strombelastung.py` goes red) or squeezes a signal
below 0.2 mm (DRC goes red), fix the placement, not the router flags.

## Proposing a new module

1. Open an issue with the idea and the channel count / signals it needs
   (at most four bank signals plus one ADC signal per module).
2. Copy `tools/sch/dimmermodul.py` and `tools/pcb/spec_dimmer_basis.py`.
   Keep: `J1`/`J2`/`J3` on their contract positions, terminals flush with
   the bottom edge inside `KLEMMENZONE`, nothing taller than 8 mm under the
   Pico, nothing in `ANTENNE_FREI`, the supply cell as is, a bank matrix
   with the contract's reference names (`J<Bank><Signal>`).
3. Add the module type to `MODULTYPEN` and its default bank to
   `BANK_VORGABE`; add a `_dimmer`-style entry to `tools/jlc.py`.
4. Write the placement test before the placement.
5. Run `tools/pcb/verlegen_v3.sh <board>` until it ends with
   "fertig", then `tools/fertigung.sh <board>`.
6. Add the Pico-side class to `firmware/pico/picostack.py` and extend
   `tests/test_firmware.py`.

## Language

Public documentation and new code comments: English. Existing comments are
German and carry the engineering rationale; translate when you touch them,
don't paraphrase them away.

## Licenses

Hardware CERN-OHL-S-2.0, code GPL-3.0-or-later, documentation CC-BY-SA 4.0.
By contributing you agree to license your contribution the same way.

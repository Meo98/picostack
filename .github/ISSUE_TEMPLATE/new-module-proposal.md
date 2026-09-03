---
name: New module proposal
about: Propose a new stackable PicoStack module (a new "hat")
title: "[module] "
labels: ["new-module", "discussion"]
---

**What does the module do?**

One or two paragraphs. What problem does it solve on top of the stack?

**Which contract signals does it use?**

Power (24 V / 5 V / 3V3), I²C, e-stop loop, flash chain, extra pins?

**Rough bill of materials**

Main ICs / connectors. No need for a full BOM yet.

**Firmware plans**

Language / framework, and whether the module has its own MCU.

**Anything that might need a contract change?**

The contract (`tools/stack_spec.py`) only changes with very good reason —
flag it early if you think you need one.

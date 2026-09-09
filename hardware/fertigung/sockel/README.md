# Sockelplatine — v1-only, archived

This fabrication data is **frozen at the v1 state**, kept for archive
purposes alongside [release v0.1.0](https://github.com/Meo98/picostack/releases/tag/v0.1.0).
It is **not part of the v2 product line** and was not regenerated for the
v2 contract (`VERTRAG_VERSION = 2` in `tools/stack_spec.py`).

v2 removed the need for this board entirely: every v2 module now carries
its own supply cell (reverse-polarity protection, TVS, K7805-1000R3,
Schottky-OR into VSYS) and a pair of Pico-native 1×20 socket rows, so one
module plus a Pico is a working device without a separate base board. See
[`hardware/fertigung/ORDERING.md`](../ORDERING.md) for the current v2
board family (motor, dimmer1, dimmer3, dimmer4) and
[`tools/sch/sockelplatine.py`](../../../tools/sch/sockelplatine.py) for
why this board's generator is not kept in sync with the v2 contract.

Do not order this as a v2 deliverable.

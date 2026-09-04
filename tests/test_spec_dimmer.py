"""Prueft die gemeinsame Platinenbeschreibung der Dimmer-Module.

Drei Varianten aus EINER Quelle (spec_dimmer_basis.beschreibung):
was hier rot werden kann, ist fuer alle drei rot. Die Nest-Plaetze
und -Vorverdrahtungen kommen woertlich vom Motormodul -- der Test
sichert genau diese Zusage: wandert das Nest im Motormodul, MUSS
diese Pruefung mitwandern (dann bewusst), statt dass die Dimmer
still auf alten Plaetzen bauen.
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "pcb"))

import geometry           # noqa: E402
import spec_dimmer_basis  # noqa: E402
import spec_motor as M    # noqa: E402
import stack_spec as S    # noqa: E402

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


for kanaele in (1, 3, 4):
    b = types.ModuleType("dimmer%d" % kanaele)
    b.__dict__.update(spec_dimmer_basis.beschreibung(kanaele))
    tag = "Dimmer%d" % kanaele

    bad = geometry.check_all(b.PLACEMENT, b)
    fails.extend("%s Geometrie: %s" % (tag, x) for x in bad)

    # Nest woertlich vom Motormodul.
    for ref in ("J100", "J101", "J102", "J103", "J104", "U100", "U101",
                "U102", "U103", "C100", "C101", "R102",
                "R100", "R101", "R104", "R105"):
        p, q = b.PLACEMENT[ref], M.PLACEMENT[ref]
        check("%s %s auf Motormodul-Platz" % (tag, ref),
              (p.x, p.y, p.rot, p.unten), (q.x, q.y, q.rot, q.unten))

    # Kanalzahl schlaegt ueberall durch.
    check("%s Kanal-FETs" % tag,
          sorted(r for r in b.PLACEMENT if r.startswith("Q") and r != "Q10"),
          ["Q%d" % n for n in range(1, kanaele + 1)])
    check("%s Klemmen" % tag,
          sorted(r for r in b.PLACEMENT if r.startswith("J") and r[1] != "1"),
          sorted("J%d" % (4 + n) for n in range(1, kanaele + 1)))
    check("%s Leistungsnetze" % tag,
          sorted(b.POWER_NETS),
          sorted(["/PWR24V", "/+24V"]
                 + ["/LED%d" % n for n in range(1, kanaele + 1)]))

    # Klemmen-Pads suedlich des Verdreht-Landepunktstreifens: Hof-y
    # 50,0 + Pad-Offset 3,605 = 53,6 -- dieselbe Hoehe wie die
    # Motorklemme (dort per steckerprobe am Board verifiziert).
    for r, p in b.PLACEMENT.items():
        if r.startswith("J") and r[1] not in "1":
            check("%s %s Pad-Zeile" % (tag, r), round(p.y + 3.605, 3), 53.605)

    # Beschreibung vollstaendig.
    check("%s jedes Bauteil hat einen Footprint" % tag,
          sorted(set(b.PLACEMENT) - set(b.FOOTPRINTS)), [])
    check("%s jeder Footprint ist platziert" % tag,
          sorted(set(b.FOOTPRINTS) - set(b.PLACEMENT)), [])

    # Naehte frei -- Radius wie beim Sockel: VIA_PAD/2 + Abstand
    # (0,3 + 0,2). Die erste Fassung addierte noch einmal 0,5 und
    # meldete Vias, die 0,75 mm neben dem C12-Hof liegen.
    via_r = 0.3 + 0.2
    for vx, vy in b.STITCH_VIAS:
        for ref, p in b.PLACEMENT.items():
            if (p.x - via_r < vx < p.x + p.w + via_r
                    and p.y - via_r < vy < p.y + p.h + via_r):
                fails.append("%s Naehvia (%.2f|%.2f) im Hof von %s"
                             % (tag, vx, vy, ref))

# Typcode-Bindung: die Kennwiderstaende der Stueckliste MUESSEN aus
# dem Vertrag kommen -- Rot-Nachweis der Nibble-Zusage in
# tests/test_stack_spec.py.
check("Dimmer1-Typcode existiert", 0x10 in S.MODULTYPEN, True)
check("Dimmer3-Typcode existiert", 0x11 in S.MODULTYPEN, True)
check("Dimmer4-Typcode existiert", 0x12 in S.MODULTYPEN, True)

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Dimmerbeschreibungen: 1/3/4 Kanaele -- alle Pruefungen bestanden")

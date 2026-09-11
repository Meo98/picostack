"""Prueft die gemeinsame Platinenbeschreibung der Dimmer-Module (v2).

Drei Varianten aus EINER Quelle (spec_dimmer_basis.beschreibung): was
hier rot werden kann, ist fuer alle drei rot. Nest und alle sechs
Vertragsstecker kommen woertlich vom Motormodul -- der Test sichert
genau diese Zusage: wandert das Nest im Motormodul, MUSS diese Pruefung
mitwandern (dann bewusst), statt dass die Dimmer still auf alten
Plaetzen bauen.

v2-NEUAUFLAGE (Aufgabe 8a). Die alte Fassung pruefte einen 64x60-Umriss
und v1-Referenzen (Q90 fehlte als "Kanal-FET" ausgeschlossen, die
Versorgungszelle J90/Q90/... kam gar nicht vor, KLEMMEN_POS/J-Pad-Zeilen
waren auf den alten Umriss gerechnet). Diese Fassung prueft den echten
75x65-Vertrag: Board-Mass, Vertragssteckerlage gegen
stack_spec.STECKER_POS[...]["pin1"] (nicht nur gegen sich selbst),
ANTENNE_FREI, Randpads auf B.Cu, und zusaetzlich die Verdreht-
Kupferklausel (approximiert ueber Bauteil-Hoefe -- die scharfe Pruefung
gegen echte Pad-Koordinaten macht steckerprobe.py an der gebauten
Platine, s. Bericht zu Aufgabe 8).
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


# -- Vertragsstecker, gegen S.STECKER_POS[...]["pin1"] nachgerechnet,
# nicht nur gegen die eigene Platzierung. Dieselbe Rechnung wie
# steckerprobe.py (S.HOF aus pin1+drehung), hier ohne KiCad, damit sie
# in run_all.py mitlaeuft. --------------------------------------------
_VERTRAGSSTECKER = {
    "J100": "stapel_links", "J105": "stapel_rechts",
    "J101": "kette", "J102": "kette",
    "J103": "leistung", "J104": "leistung",
}

for kanaele in (1, 3, 4):
    b = types.ModuleType("dimmer%d" % kanaele)
    b.__dict__.update(spec_dimmer_basis.beschreibung(kanaele))
    tag = "Dimmer%d" % kanaele

    # -- Board-Mass: der v2-Vertrag, nicht mehr 64x60 --------------------
    check("%s BOARD_W" % tag, b.BOARD_W, S.BOARD_W)
    check("%s BOARD_H" % tag, b.BOARD_H, S.BOARD_H)
    check("%s M3_HOLES" % tag, b.M3_HOLES, S.M3_HOLES)

    # -- Geometrie: keine Ueberlappungen, keine M3-Kollision, kein
    # Ueberstand -- reine Python-Pruefung, kein KiCad noetig. Die
    # Kanal-Klemmen sitzen kantenbuendig (R1); b.EDGE_FLUSH_REFS sagt
    # geometry.check_all() das bereits (s. dort), kein Filter noetig. --
    bad = geometry.check_all(b.PLACEMENT, b)
    fails.extend("%s Geometrie: %s" % (tag, x) for x in bad)

    # -- Vertragsstecker: Hof exakt aus S.HOF(footprint, pin1, drehung),
    # nicht nur "irgendein Platz". VERTRAGSPLATZ muss diese sechs
    # Referenzen den richtigen Plaetzen zuordnen (steckerprobe.py haengt
    # daran, s. spec_motor.VERTRAGSPLATZ-Docstring). -------------------
    check("%s VERTRAGSPLATZ" % tag,
          {r: b.VERTRAGSPLATZ.get(r) for r in _VERTRAGSSTECKER},
          _VERTRAGSSTECKER)
    for ref, slot in _VERTRAGSSTECKER.items():
        e = S.STECKER_POS[slot]
        fp = b.FOOTPRINTS[ref]
        soll = S.HOF(fp, e["pin1"], e["drehung"])
        p = b.PLACEMENT[ref]
        ist = (round(p.x, 3), round(p.y, 3),
              round(p.x + p.w, 3), round(p.y + p.h, 3))
        check("%s %s Hof gegen STECKER_POS[%s]['pin1']" % (tag, ref, slot),
              ist, soll)

    # -- Nest woertlich vom Motormodul: dieselben Koordinaten, dieselbe
    # Drehung, dieselbe Seite -- fuer ALLE 19 uebernommenen Referenzen
    # (die sechs Vertragsstecker eingeschlossen). -----------------------
    for ref in spec_dimmer_basis.NEST_REFS:
        p, q = b.PLACEMENT[ref], M.PLACEMENT[ref]
        check("%s %s auf Motormodul-Platz" % (tag, ref),
              (p.x, p.y, p.rot, p.unten), (q.x, q.y, q.rot, q.unten))
        check("%s %s Footprint wie Motormodul" % (tag, ref),
              b.FOOTPRINTS[ref], M.FOOTPRINTS[ref])

    # -- Randpads (J95/J96) auf F.Cu, an den Vertragskoordinaten (v2.1:
    # SENKRECHT, s. spec_motor.PLACEMENT-Kommentar). Die Nest-Verbatim-
    # Pruefung oben deckt "identisch zum Motormodul" bereits ab; hier
    # zusaetzlich explizit gegen den Vertrag selbst (RANDPADS/RAND_X/
    # RAND_Y0), falls beide je auseinanderlaufen sollten. ------
    for ref in ("J95", "J96"):
        p = b.PLACEMENT[ref]
        check("%s %s auf F.Cu (unten=False)" % (tag, ref), p.unten, False)
        # Alle Pads teilen sich RAND_X (senkrechte Reihe); Platz.x ist
        # der Hof-Rand (RAND_X - 1,3, s. spec_motor.PLACEMENT-Kommentar).
        check("%s %s x auf RAND_X" % (tag, ref),
              round(p.x + 1.3, 3), S.RAND_X)
    # J96 traegt die ersten vier Kontakte (Versorgung), J95 die
    # restlichen 18 (GPIO) -- zusammen die 22 RANDPADS-Koordinaten,
    # Pad-Mitte(y) = Platz.y + 0.45 + i * RAND_RASTER (Herleitung in
    # spec_motor.PLACEMENT).
    rand_y = sorted(round(p[2][1], 2) for p in S.RANDPADS)
    gebaut_y = sorted(
        round(b.PLACEMENT["J96"].y + 0.45 + i * S.RAND_RASTER, 2)
        for i in range(4)) + sorted(
        round(b.PLACEMENT["J95"].y + 0.45 + i * S.RAND_RASTER, 2)
        for i in range(18))
    check("%s Randpad-y-Koordinaten == RANDPADS" % tag,
          sorted(gebaut_y), rand_y)

    # -- ANTENNE_FREI: kein Bauteil-Hof (ausser den Vertragssteckern
    # J100/J105 selbst, die als Anker dort liegen DUERFEN, s.
    # pcb_checks.STECKER_AUSNAHME) darf das Rechteck beruehren. ---------
    ax0, ay0, ax1, ay1 = S.ANTENNE_FREI
    for ref, p in b.PLACEMENT.items():
        if ref in ("J100", "J105"):
            continue
        x0, y0, x1, y1 = p.x, p.y, p.x + p.w, p.y + p.h
        if x0 < ax1 and ax0 < x1 and y0 < ay1 and ay0 < y1:
            fails.append("%s %s liegt im ANTENNE_FREI-Rechteck" % (tag, ref))

    # -- Verdreht-Kupferklausel, approximiert ueber Bauteil-Hoefe (die
    # scharfe Pruefung gegen echte Pads macht steckerprobe.py, s.
    # Bericht -- diese hier ist die BILLIGE Voranzeige ohne KiCad und
    # war der Fund, der drei Bauteilgruppen dieser Beschreibung an ihren
    # jetzigen Platz gebracht hat: Q1 (gedreht), die Nest-Stuetzkonden-
    # satoren C102-104 und die Gatewiderstaende RG/RP). Ausgenommen sind
    # J95/J96 (B.Cu-SMD -- die Klausel gilt nur der Oberseite, s.
    # steckerprobe.verdrehtprobe) und die vier Vertragsstecker (sie SIND
    # der Anker, s.o.). ---------------------------------------------
    punkte = S.LANDEPUNKTE_VERDREHT()

    def _hof_abstand(p, px, py):
        dx = max(abs(px - (p.x + p.w / 2.0)) - p.w / 2.0, 0.0)
        dy = max(abs(py - (p.y + p.h / 2.0)) - p.h / 2.0, 0.0)
        return (dx * dx + dy * dy) ** 0.5

    # Die Kanal-Klemmen (J5..J8, TerminalBlock_Phoenix_PT-1,5-2-3.5-H)
    # bekommen HIER die SCHARFE Pruefung gegen die beiden echten Pads
    # statt der Hof-Naeherung (Aufgabe C1). Grund: ihr Hof (8,00 mm) ist
    # gegenueber ihren beiden Kontakten (3,5 mm Abstand, je 2,25 mm vom
    # Hofrand eingerueckt) so grosszuegig bemessen, dass die Hof-
    # Naeherung hier KEINE billige Voranzeige mehr ist, sondern falsch
    # alarmiert: KLEMMENZONE liegt fuer alle drei Kanalzahlen im
    # Ueberschneidungsbereich der Landepunkt-Spiegelspalten von
    # stapel_links/-rechts (x=33,61 bzw. 51,39, s. stack_spec.
    # KLEMMENZONE-Kommentar fuer die volle Eskalation) -- eine Klemme,
    # die diese Spalten mit ihren PADS (nicht mit ihrem leeren Hof-Rand)
    # meidet, ist verdreht-sicher, auch wenn ihr Hof den Streifen noch
    # ueberlappt. Radius 1,2 mm = halbe Pad-Kantenlaenge (2,4 x 2,4 mm,
    # aus TerminalBlock_Phoenix_PT-1,5-2-3.5-H.kicad_mod gemessen).
    _KLEMMEN_REFS = tuple("J%d" % (4 + n) for n in range(1, 5))

    def _klemme_pad_abstand(p, px, py):
        pin1 = (p.x + 2.25, p.y + 3.6)
        pin2 = (pin1[0] + 3.5, pin1[1])
        beste = 1e9
        for cx, cy in (pin1, pin2):
            dx = max(abs(px - cx) - 1.2, 0.0)
            dy = max(abs(py - cy) - 1.2, 0.0)
            beste = min(beste, (dx * dx + dy * dy) ** 0.5)
        return beste

    for ref, p in b.PLACEMENT.items():
        if ref in ("J95", "J96") or ref in _VERTRAGSSTECKER:
            continue
        pruefen = _klemme_pad_abstand if ref in _KLEMMEN_REFS else _hof_abstand
        for px, py in punkte:
            if pruefen(p, px, py) < S.LANDE_SPERRRADIUS - 1e-6:
                fails.append(
                    "%s %s: %s naeher als %.1f mm am Landepunkt "
                    "(%.2f|%.2f)" % (tag, ref,
                                     "Pad" if ref in _KLEMMEN_REFS else "Hof",
                                     S.LANDE_SPERRRADIUS, px, py))
                break

    # -- Kanalzahl schlaegt ueberall durch -------------------------------
    check("%s Kanal-FETs" % tag,
          sorted(r for r in b.PLACEMENT
                 if r.startswith("Q") and r != "Q90"),
          ["Q%d" % n for n in range(1, kanaele + 1)])
    check("%s Kanal-Dioden" % tag,
          sorted(r for r in b.PLACEMENT
                 if r.startswith("D") and r not in ("D90", "D91")),
          ["D%d" % n for n in range(1, kanaele + 1)])
    check("%s Klemmen" % tag,
          sorted(r for r in b.PLACEMENT
                 if r.startswith("J") and r not in
                 ("J90", "J95", "J96", "J100", "J101", "J102", "J103",
                  "J104", "J105")),
          sorted("J%d" % (4 + n) for n in range(1, kanaele + 1)))
    check("%s Leistungsnetze" % tag,
          sorted(b.POWER_NETS),
          sorted(["/PWR_IN", "/+24V"]
                 + ["/LED%d" % n for n in range(1, kanaele + 1)]))

    # -- Beschreibung vollstaendig: jeder Platz hat einen Footprint und
    # umgekehrt. ---------------------------------------------------------
    check("%s jedes Bauteil hat einen Footprint" % tag,
          sorted(set(b.PLACEMENT) - set(b.FOOTPRINTS)), [])
    check("%s jeder Footprint ist platziert" % tag,
          sorted(set(b.FOOTPRINTS) - set(b.PLACEMENT)), [])

    # -- Naehte frei: kein STITCH_VIA im Hof eines Bauteils --------------
    via_r = 0.5
    for vx, vy in b.STITCH_VIAS:
        for ref, p in b.PLACEMENT.items():
            if (p.x - via_r < vx < p.x + p.w + via_r
                    and p.y - via_r < vy < p.y + p.h + via_r):
                fails.append("%s Naehvia (%.2f|%.2f) im Hof von %s"
                             % (tag, vx, vy, ref))

    # -- Vorverdrahtung darf nur an tatsaechlich vorhandenen Referenzen
    # haengen (Rot-Nachweis der v1-Falle: die alte Fassung filterte nur
    # nach Netznamen und haette U6/U7/R13-Stummel des Motormoduls an
    # nicht existierende Pads gehaengt, s. Moduldocstring). -------------
    for entry in b.PRE_TRACKS:
        for punkt in entry[2]:
            if (isinstance(punkt, tuple) and len(punkt) == 3
                    and punkt[0] == "PAD" and punkt[1] not in b.PLACEMENT):
                fails.append("%s PRE_TRACKS haengt an fehlender Referenz %s"
                             % (tag, punkt[1]))

# -- Typcode-Bindung: die Kennwiderstaende der Stueckliste MUESSEN aus
# dem Vertrag kommen. ---------------------------------------------------
check("Dimmer1-Typcode existiert", 0x10 in S.MODULTYPEN, True)
check("Dimmer3-Typcode existiert", 0x11 in S.MODULTYPEN, True)
check("Dimmer4-Typcode existiert", 0x12 in S.MODULTYPEN, True)

if fails:
    print("FEHLER:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("Dimmerbeschreibungen: 1/3/4 Kanaele -- alle Pruefungen bestanden")

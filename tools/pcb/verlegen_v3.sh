#!/usr/bin/env bash
# verlegen_v3.sh -- baut und verlegt ein v3-Modul von der Netzliste bis zur DRC.
#
#   tools/pcb/verlegen_v3.sh dimmer4          # spec_dimmer4, hardware/kicad/dimmer4/
#
# Schritte (jeder prueft sich selbst, der Lauf bricht beim ersten roten ab):
#   1. Schaltplan erzeugen (tools/sch/dimmermodul.py) + ERC 0/0
#   2. Platine aus Beschreibung + Netzliste bauen (build.py: Umriss,
#      Platzierung, Regelflaechen, Naehvias, Silk)
#   3. Netzklassen ins Projekt (netclasses.py)
#   4. KiCadRoutingTools, Lauf 1: nur Leistungsnetze, breit (1,4 / 1,0 mm)
#   5. KiCadRoutingTools, Lauf 2: alle uebrigen Netze ausser GND, 0,25 mm
#   6. Vias abdecken, Masse heilen (masseheiler.py)
#   7. DRC 0/0, Steckerprobe, Klemmenprobe, Strombelastung
#
# Der Router liegt in ~/Dokumente/Tools/KiCadRoutingTools (KRT=... zum
# Ueberschreiben) und braucht numpy/scipy/shapely -> nix-shell.
set -euo pipefail

NAME="${1:?Modulname fehlt (dimmer1|dimmer3|dimmer4)}"
S="$(cd "$(dirname "$0")" && pwd)"
WURZEL="$(cd "$S/../.." && pwd)"
KRT="${KRT:-$HOME/Dokumente/Tools/KiCadRoutingTools}"
ARBEIT="$(mktemp -d)"
trap 'rm -rf "$ARBEIT"' EXIT

SPEC="spec_$NAME"
KANAELE="${NAME//[^0-9]/}"
PROJ="$WURZEL/hardware/kicad/$NAME"
BASIS="$(python3 -c "print('$NAME'.capitalize())")"
B="$PROJ/$BASIS.kicad_pcb"
SCH="$PROJ/$BASIS.kicad_sch"
PRO="$PROJ/$BASIS.kicad_pro"

router() {
  ( cd "$KRT" && nix-shell -p 'python3.withPackages (ps: [ps.numpy ps.scipy ps.shapely])' \
      --run "python3 py_router/route.py $*" ) 2>&1 \
    | python3 -c '
import sys, json
for line in sys.stdin:
    if line.startswith("JSON_SUMMARY_MIN:"):
        d = json.loads(line.split(":", 1)[1])
        print("  Router:", {k: d[k] for k in ("routed", "failed", "failed_single",
              "min_clearance_used", "vias", "escalations") if k in d})
        # "escalations" zaehlt auch Halsverengungen an Pads (gewollt);
        # ob eine Bahn zu schmal ist, entscheidet strombelastung.py.
        if d.get("failed"):
            sys.exit(1)
'
}

echo "== 1. Schaltplan + ERC"
( cd "$WURZEL" && python3 tools/sch/dimmermodul.py >/dev/null )
kicad-cli sch erc --severity-all --exit-code-violations -o "$ARBEIT/erc.rpt" "$SCH" >/dev/null

echo "== 2. Platine bauen"
( cd "$WURZEL" && tools/pcb/kipy tools/pcb/build.py "$SPEC" "$B" "$SCH" | tail -3 )

echo "== 3. Netzklassen"
( cd "$WURZEL" && python3 tools/pcb/netclasses.py "$PRO" "$SPEC" | tail -1 )

echo "== 4. Router, Lauf 1 (Leistung)"
router "'$B' '$ARBEIT/r1.kicad_pcb' --nets '/PWR_IN' '/VIN' '/LED*' '/+5V_LOKAL' '/VSW' \
  --power-nets '/PWR_IN' '/VIN' '/LED*' '/+5V_LOKAL' '/VSW' --power-nets-widths 1.4 1.4 1.0 1.0 1.0 \
  --via-size 0.6 --via-drill 0.3 --clearance 0.2 --keepout --layers F.Cu B.Cu"

echo "== 5. Router, Lauf 2 (Signale)"
router "'$ARBEIT/r1.kicad_pcb' '$ARBEIT/r2.kicad_pcb' --nets '*' '!GND' --track-width 0.25 \
  --via-size 0.5 --via-drill 0.3 --clearance 0.2 --keepout --layers F.Cu B.Cu"
cp "$ARBEIT/r2.kicad_pcb" "$B"

echo "== 6. Vias abdecken, Masse heilen"
( cd "$WURZEL" && tools/pcb/kipy tools/pcb/stamp_via_tenting.py "$B" | tail -1 \
  && tools/pcb/kipy tools/pcb/masseheiler.py "$B" | tail -1 )

echo "== 7. DRC + Proben"
kicad-cli pcb drc --severity-error --exit-code-violations --format json -o "$ARBEIT/drc.json" "$B" >/dev/null \
  || { python3 -c "
import json; d = json.load(open('$ARBEIT/drc.json'))
for v in d.get('violations', []): print('  DRC', v['type'], v.get('description','')[:100])
for u in d.get('unconnected_items', []): print('  OFFEN', [i.get('description','')[:60] for i in u.get('items', [])])
"; exit 1; }
echo "  DRC 0 Verletzungen, 0 offen"
( cd "$WURZEL" \
  && tools/pcb/kipy tools/pcb/steckerprobe.py "$SPEC" "$B" | tail -1 \
  && tools/pcb/kipy tools/pcb/klemmenprobe.py "$B" | tail -1 \
  && tools/pcb/kipy tools/pcb/strombelastung.py "$B" "$SPEC" | tail -3 )
echo "== $NAME fertig: $B"

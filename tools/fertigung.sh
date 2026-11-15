#!/usr/bin/env bash
# fertigung.sh -- Fertigungsdaten fuer JLCPCB aus einer verlegten Platine.
#
#   tools/fertigung.sh dimmer4
#
# Schreibt nach hardware/fertigung/<board>/:
#   gerber/                 Kupfer, Paste, Silk, Mask, Umriss, Bohrdateien
#   <board>-gerber-jlc.zip  dasselbe als Upload-Archiv
#   pos.csv                 kicad-cli-Positionsexport (Anker, beide Seiten)
#   zentroide.csv           Pad-Zentroiden (tools/pcb/zentroide.py)
#   jlc-bom.csv, jlc-cpl.csv, UNBESTUECKT.txt   (tools/jlc.py)
# Laeuft nur gegen eine Platine mit DRC 0/0 (verlegen_v3.sh vorher).
set -euo pipefail

NAME="${1:?Modulname fehlt (dimmer1|dimmer3|dimmer4)}"
S="$(cd "$(dirname "$0")" && pwd)"
WURZEL="$(cd "$S/.." && pwd)"
BASIS="$(python3 -c "print('$NAME'.capitalize())")"
B="$WURZEL/hardware/kicad/$NAME/$BASIS.kicad_pcb"
ZIEL="$WURZEL/hardware/fertigung/$NAME"

kicad-cli pcb drc --severity-error --exit-code-violations -o "$(mktemp)" "$B" >/dev/null \
  || { echo "DRC nicht sauber -- erst tools/pcb/verlegen_v3.sh $NAME"; exit 1; }

rm -rf "$ZIEL/gerber" "$ZIEL/$NAME-gerber-jlc.zip"
mkdir -p "$ZIEL/gerber"
kicad-cli pcb export gerbers -o "$ZIEL/gerber/" \
  --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts" \
  --subtract-soldermask --no-x2 --no-netlist "$B" >/dev/null
kicad-cli pcb export drill -o "$ZIEL/gerber/" --format excellon --excellon-units mm \
  --excellon-zeros-format decimal --drill-origin absolute --generate-map --map-format gerberx2 "$B" >/dev/null
# zipfile aus der Python-Standardbibliothek: kein zip-Binary auf dem System
( cd "$ZIEL/gerber" && python3 -m zipfile -c "../$NAME-gerber-jlc.zip" . )
kicad-cli pcb export pos -o "$ZIEL/pos.csv" --format csv --units mm --side both "$B" >/dev/null
( cd "$WURZEL" && tools/pcb/kipy tools/pcb/zentroide.py "$B" "$ZIEL/zentroide.csv" >/dev/null \
  && python3 tools/jlc.py "$NAME" )
echo "$NAME: $(ls "$ZIEL/gerber" | wc -l) Gerber-/Bohrdateien, $(du -h "$ZIEL/$NAME-gerber-jlc.zip" | cut -f1) Archiv"

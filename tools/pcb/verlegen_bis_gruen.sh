#!/usr/bin/env bash
# verlegen_bis_gruen.sh -- verlegt ein Brett, bis es ALLE Tore besteht.
#
#   tools/pcb/verlegen_bis_gruen.sh <spec> <board> <projekt> [versuche] [feinraster]
#
# Warum das kein Wuerfeln ist. Die Verlegung ist nicht deterministisch
# (Netzreihenfolge und Aufreiss-Entscheidungen variieren), und
# CONTRIBUTING.md haelt seit v2 fest, was daraus folgt: "the committed
# board file is the artifact of record, and the DRC + probe suite is
# what makes it trustworthy, not the ability to regenerate it
# bit-identically". Der Unterschied zwischen Wuerfeln und diesem Skript
# ist das ANNAHMEKRITERIUM: hier steht es hin, wird bei JEDEM Versuch
# vollstaendig gefahren, und nur ein Brett, das alle vier Tore besteht,
# wird behalten. Ein Versuch, der "fast" durchkommt, wird verworfen.
#
# GEMESSEN am Motormodul (Aufgabe D5): bei identischer Platzierung und
# identischen Parametern lieferten aufeinanderfolgende Laeufe einmal
# DRC 0/0 + Strom gruen + 2 offene Signale, einmal DRC 0/0 + Strom gruen
# + 4 offene, einmal Strom rot. Die Platzierung war in allen drei
# Faellen dieselbe -- die Streuung kommt vom Router, nicht vom Layout.
set -uo pipefail

SPEC="${1:?spec fehlt}"; B="${2:?board fehlt}"; PRO="${3:?projekt fehlt}"
VERSUCHE="${4:-6}"; FEIN="${5:-}"
S="$(cd "$(dirname "$0")" && pwd)"
W="$(cd "$S/../.." && pwd)"
SCH="${B%.kicad_pcb}.kicad_sch"
ABL="$(mktemp -d)"
BESTE=""; BESTE_PUNKTE=-1

cd "$W"
for i in $(seq 1 "$VERSUCHE"); do
  echo "=== Versuch $i von $VERSUCHE ==="
  "$S/kipy" "$S/build.py" "$SPEC" "$B" "$SCH" >/dev/null 2>&1 || { echo "  Bau fehlgeschlagen"; continue; }
  "$S/verlegen.sh" "$SPEC" "$B" "$PRO" $FEIN > "$ABL/lauf$i.log" 2>&1 \
    || { echo "  Verlegen fehlgeschlagen, s. $ABL/lauf$i.log"; continue; }

  # Tor 1+2: DRC (Verletzungen UND offene Verbindungen)
  AUS=$(kicad-cli pcb drc --severity-error --refill-zones -o "$ABL/drc$i.rpt" "$B" 2>/dev/null)
  V=$(echo "$AUS" | grep -oP '\d+(?= violations)' || echo 99)
  O=$(echo "$AUS" | grep -oP '\d+(?= unconnected)' || echo 99)
  # Tor 3: Strombelastbarkeit
  "$S/kipy" "$S/strombelastung.py" "$B" "$SPEC" > "$ABL/strom$i.txt" 2>&1; ST=$?
  # Tor 4+5: Stecker- und Klemmenlage
  "$S/kipy" "$S/steckerprobe.py" "$SPEC" "$B" > "$ABL/stecker$i.txt" 2>&1; SP=$?
  "$S/kipy" "$S/klemmenprobe.py" "$B" > "$ABL/klemme$i.txt" 2>&1; KL=$?

  echo "  DRC $V Verletzungen / $O offen | Strom $([ $ST -eq 0 ] && echo gruen || echo ROT)" \
       "| Stecker $([ $SP -eq 0 ] && echo gruen || echo ROT)" \
       "| Klemmen $([ $KL -eq 0 ] && echo gruen || echo ROT)"

  if [ "$V" -eq 0 ] && [ "$O" -eq 0 ] && [ $ST -eq 0 ] && [ $SP -eq 0 ] && [ $KL -eq 0 ]; then
    echo "  ALLE TORE GRUEN -- behalten."
    exit 0
  fi
  # Sonst: den am wenigsten schlechten Versuch aufheben, damit ein
  # Abbruch nicht mit leeren Haenden endet.
  P=$(( (V==0?4:0) + (10-O>0?10-O:0) + (ST==0?20:0) + (SP==0?3:0) + (KL==0?3:0) ))
  if [ "$P" -gt "$BESTE_PUNKTE" ]; then BESTE_PUNKTE=$P; BESTE="$ABL/beste.kicad_pcb"; cp "$B" "$BESTE"; cp "$PRO" "$ABL/beste.kicad_pro"; fi
done

if [ -n "$BESTE" ]; then
  cp "$BESTE" "$B"; cp "$ABL/beste.kicad_pro" "$PRO"
  echo "Kein Versuch bestand alle Tore. Bester Stand zurueckgelegt ($BESTE_PUNKTE Punkte);"
  echo "Protokolle in $ABL"
fi
exit 1

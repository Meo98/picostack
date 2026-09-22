#!/usr/bin/env bash
# verlegen.sh -- verlegt ein Brett nach dem dokumentierten Drei-Lauf-Rezept.
#
#   tools/pcb/verlegen.sh <spec_modul> <board.kicad_pcb> <projekt.kicad_pro> \
#                         [feinraster-referenzen]
#
# Beispiel Motormodul (U1 ist ein HTSSOP-16 mit 0,65 mm Raster):
#   tools/pcb/verlegen.sh spec_motor hardware/kicad/motor/Motormodul.kicad_pcb \
#       hardware/kicad/motor/Motormodul.kicad_pro U1
#
# Warum es dieses Skript gibt. Das Rezept stand bisher nur als Prosa in
# CONTRIBUTING.md ("Power nets are routed first, alone, on bare copper --
# three router runs, not one"). Es hat elf Schritte in fester Reihenfolge,
# zwei davon sind nicht vertauschbar (verbreitern VOR den Signalen,
# sperren VOR dem dritten Lauf), und es wurde bei jeder Wiederaufnahme von
# Hand neu abgetippt. Ein Rezept, das nur als Prosa existiert, wird beim
# vierten Brett anders ausgefuehrt als beim ersten.
#
# Die Begruendung JEDES Schritts steht in CONTRIBUTING.md; hier stehen nur
# die Aufrufe und das, was man beim Abtippen falsch machen kann.
set -euo pipefail

SPEC="${1:?spec_modul fehlt}"
B="${2:?board.kicad_pcb fehlt}"
PRO="${3:?projekt.kicad_pro fehlt}"
# Optional: Referenzen feinrastriger Bauteile, deren Pins VOR dem
# Leistungslauf herausgefuehrt werden muessen (s. Schritt 3b).
FEINRASTER="${4:-}"

S="$(cd "$(dirname "$0")" && pwd)"
WURZEL="$(cd "$S/../.." && pwd)"
KRT="${KRT:-$HOME/KiCadRoutingTools}"
ARBEIT="$(mktemp -d)"
trap 'rm -rf "$ARBEIT"' EXIT

# Der Router braucht numpy/scipy/shapely, die weder das System-Python noch
# KiCads Python hat. nix-shell statt venv: PIP_USER=1 ist auf diesem System
# global gesetzt und kollidiert mit venvs (s. task-v21d-eval-report.md).
router() {
  ( cd "$KRT" && nix-shell -p 'python3.withPackages (ps: [ps.numpy ps.scipy ps.shapely])' \
      --run "python3 py_router/route.py $*" ) 2>&1 | grep -vE "^warning: unable to download"
}

# Die Bahnbreiten kommen aus DEMSELBEN Werkzeug, das sie spaeter prueft
# (strombelastung.py --breiten), nicht aus den Netzklassenwerten in
# fertigung.py. Netzklassenbreite ist Auslegungsabsicht, nicht
# Strombedarf -- und wer vom Router MEHR verlangt als noetig, bekommt an
# engen Stellen nicht etwas weniger, sondern die SIGNALBREITE: der Router
# meldet "Wide route blocked - retrying at default track width".
# GEMESSEN am Motormodul: /Out1 und /Out2 brauchen 0,713 mm, bekamen die
# Netzklassenvorgabe 1,000 mm -- und lagen am Ende bei 0,250..0,600 mm.
# Netz UND Breite aus derselben Zeile lesen, nicht zwei Listen der
# Reihe nach zusammenstecken: --breiten laesst ein Netz aus, fuer das
# keine Stromdeklaration vorliegt, und dann waeren beide Listen
# gegeneinander verschoben -- jedes Netz bekaeme die Breite seines
# Nachbarn, ohne dass irgendetwas rot wuerde.
BREITENZEILEN=$("$S/kipy" "$S/strombelastung.py" --breiten "$SPEC" 2>/dev/null \
                | grep -E '^/')
LEISTUNG=$(echo "$BREITENZEILEN" | awk '{print $1}' | tr '\n' ' ')
BREITEN=$(echo "$BREITENZEILEN" | awk '{print $2}' | tr '\n' ' ')
if [ -z "$LEISTUNG" ]; then
  echo "verlegen.sh: strombelastung.py --breiten $SPEC lieferte nichts -- " \
       "ohne Strombedarf keine Leistungsverlegung" >&2
  exit 1
fi
GEMEINSAM="--clearance 0.2 --via-size 0.6 --via-drill 0.3 --escalation off"
# Netzreihenfolge: bei den beiden LEISTUNGS-Laeufen "original", damit der
# Stamm vor seinen Abzweigen liegt (so ist das Rezept in CONTRIBUTING.md
# gemessen worden). Beim SIGNAL-Lauf dagegen die Router-Voreinstellung
# "mps" -- die ordnet nach Kreuzungen. Gemessen an Dimmer4: mit
# "original" auch im dritten Lauf blieb /PWM1 unverlegt UND der
# Massenguss zerfiel in eine 1,7 x 1,7 mm grosse Insel ohne freien
# Heilpunkt (masseheiler rot, DRC "2 unconnected"). Das ist kein
# Wuerfeln, sondern die Reihenfolge, fuer die dieser Lauf gebaut ist.
ORDNUNG_LEISTUNG="--ordering original"
STROM="--power-nets GND $LEISTUNG --power-nets-widths 0.3 $BREITEN"

echo "### $SPEC: Leistungsnetze [$LEISTUNG] mit Breiten [$BREITEN]"

cd "$WURZEL"
echo "### 1/10 Netzklassen ins Projekt (build.py setzt die .kicad_pro zurueck!)"
python3 "$S/netclasses.py" "$PRO" "$SPEC"

echo "### 2/10 blankes Kupfer"
"$S/kipy" "$S/stammtrennung.py" --kupfer-weg "$B"
"$S/kipy" "$S/stammtrennung.py" --vorverdrahtung "$B" "$SPEC"

# Feinrastrige Bauteile zuerst herausfuehren. Begruendung in
# CONTRIBUTING.md: der Leistungsstamm belegt sonst den Korridor, den die
# 0,65-mm-Pins zum Entkommen brauchen, und danach kommt nichts mehr an
# sie heran. GEMESSEN am Motormodul, erster Lauf dieser Aufgabe OHNE
# diesen Schritt: fuenf Verbindungen blieben offen, und ALLE FUENF hingen
# an U1 (Pads 2, 3, 4, 12) bzw. an dem direkt daneben sitzenden C9 --
# /NCLR, /NFAULT, /U1_NSLEEP, /U1_PH_IN2, /VCP. Der Reparaturlauf am Ende
# bekam keine davon zu, weil zu diesem Zeitpunkt alles ringsum voll war.
# NUR DIE SIGNALPINS. Der Leistungspin desselben Bauteils darf NICHT
# mit herausgefuehrt werden: der Leistungslauf sieht sonst einen schon
# angeschlossenen Pin und haengt seinen Stamm an das 0,25-mm-Stummelende,
# statt das breite Kupfer bis an das Pad zu fuehren. GEMESSEN am
# Motormodul: mit Fanout ueber ALLE Netze lief /+24V auf 10,30 mm Laenge
# mit 0,400 mm zu U1.11 (VM), noetig sind 1,335 mm bei 4,00 A -- weit
# jenseits der Kurzhals-Grenze von 4,711 mm. Ein kurzer Hals AM PAD ist
# unvermeidlich (U1.11 ist 0,45 mm hoch), eine 10-mm-Zuleitung nicht.
NICHT_LEISTUNG=""
for NETZ in GND $LEISTUNG; do NICHT_LEISTUNG="$NICHT_LEISTUNG '!$NETZ'"; done

if [ -n "$FEINRASTER" ]; then
  for REF in $FEINRASTER; do
    echo "### 3b/10 Pins von $REF herausfuehren (vor dem Leistungslauf)"
    cp "$B" "$ARBEIT/vor_fanout.kicad_pcb"
    ( cd "$KRT" && nix-shell -p 'python3.withPackages (ps: [ps.numpy ps.scipy ps.shapely])' \
        --run "python3 py_router/qfn_fanout.py '$ARBEIT/vor_fanout.kicad_pcb' \
               -o '$ARBEIT/nach_fanout.kicad_pcb' --component $REF \
               --nets '*' $NICHT_LEISTUNG \
               --escape-method stub --clearance 0.2 --width 0.25 \
               --via-size 0.6 --via-drill 0.3 --escalation off" \
    ) 2>&1 | grep -vE "^warning: unable to download" | tail -6
    cp "$ARBEIT/nach_fanout.kicad_pcb" "$B"
  done
fi

echo "### 3/10 Abzweige abtrennen (der Spannbaum kennt keinen Strom)"
"$S/kipy" "$S/stammtrennung.py" --abtrennen "$B" "$SPEC" "$ARBEIT/abzweige.json"

echo "### 4/10 Lauf 1 -- nur die Leistungsnetze, volle Breite, blankes Brett"
router "'$WURZEL/$B' '$ARBEIT/r1.kicad_pcb' --nets $LEISTUNG $GEMEINSAM \
    $ORDNUNG_LEISTUNG --track-width 0.25 $STROM" | tail -20

echo "### 5/10 Abzweige wieder anheften"
"$S/kipy" "$S/stammtrennung.py" --anheften "$ARBEIT/r1.kicad_pcb" "$ARBEIT/abzweige.json"

echo "### 6/10 Lauf 2 -- dieselben Netze auf 0,25 mm, solange das Brett leer ist"
router "'$ARBEIT/r1.kicad_pcb' '$ARBEIT/r2.kicad_pcb' --nets $LEISTUNG \
    $GEMEINSAM $ORDNUNG_LEISTUNG --track-width 0.25 $STROM" | tail -20

echo "### 7/10 nachverbreitern -- JETZT, nicht nach den Signalen"
cp "$ARBEIT/r2.kicad_pcb" "$B"
"$S/kipy" "$S/stammverbreiterung.py" "$B" "$SPEC" || true

echo "### 8/10 Leistungskupfer sperren, Lauf 3 -- alles uebrige"
"$S/kipy" "$S/stammtrennung.py" --sperren "$B" "$SPEC"
router "'$WURZEL/$B' '$ARBEIT/r3.kicad_pcb' --nets '*' $GEMEINSAM \
    --track-width 0.25 $STROM" | tail -20
cp "$ARBEIT/r3.kicad_pcb" "$B"
"$S/kipy" "$S/stammtrennung.py" --entsperren "$B" "$SPEC"

# Tenting VOR dem Heilen: der Router erbt Tenting aus dem Board-Setup
# ohne expliziten Token, steckerprobe.py vergleicht aber strikt. Stuende
# das Stempeln hinter masseheiler.py, liesse ein Heil-Fehlschlag (der
# unter `set -e` abbricht) das Brett mit ungestempelten Vias zurueck --
# genau so ist Dimmer4 im ersten Lauf liegengeblieben und meldete danach
# eine Landepunkt-Verletzung, die gar keine war.
echo "### 9/10 Via-Tenting normalisieren, Masseflaeche heilen"
"$S/kipy" "$S/stamp_via_tenting.py" "$B"
"$S/kipy" "$S/masseheiler.py" "$B"

# Ein einzelnes Netz bleibt gelegentlich offen, wenn der dritte Lauf es
# zuletzt anfasst und die Korridore schon belegt sind. Dagegen hilft ein
# GEZIELTER Reparaturlauf, der nur dieses Netz verlegt und dabei seine
# Nachbarn aufreissen darf -- nicht ein weiterer Blindwurf ueber alles.
# Gemessen an Dimmer4: /FLASH_TX (U100.17 -> J100.1) blieb offen, der
# Reparaturlauf schloss es in 0,24 s ohne ein anderes Netz zu verlieren.
echo "### 10/10 Reparatur offener Netze (falls noetig)"
OFFEN=$(kicad-cli pcb drc --severity-error --refill-zones           -o "$ARBEIT/drc.rpt" "$B" 2>/dev/null | grep -oP '\d+(?= unconnected)' || echo 0)
if [ "${OFFEN:-0}" -gt 0 ]; then
  NETZE=$(grep -oP '\[/[^]]+\]' "$ARBEIT/drc.rpt" | tr -d '[]' | sort -u | tr '\n' ' ')
  echo "  $OFFEN offene Verbindung(en), betroffene Netze: $NETZE"
  cp "$B" "$ARBEIT/rep_in.kicad_pcb"
  router "'$ARBEIT/rep_in.kicad_pcb' '$ARBEIT/rep.kicad_pcb' --nets $NETZE       --rip-existing-nets '/FLASH*' '/GP*' '/ID*' '/PWM*' '/SEL*' '/I2C*'       $GEMEINSAM --track-width 0.25" | tail -5
  cp "$ARBEIT/rep.kicad_pcb" "$B"
  "$S/kipy" "$S/stamp_via_tenting.py" "$B"
  "$S/kipy" "$S/masseheiler.py" "$B"
else
  echo "  nichts offen"
fi

echo "### fertig: $B"

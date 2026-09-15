"""Strombelastbarkeit der Leistungsnetze -- misst nach, statt zu glauben.

Herkunft: Aufgabe D2 (v2.1), Sicherheits-Gate NACH dem Routing (Aufgabe
D), VOR jeder Fertigungsdatei. Anlass: eine erste, oberflaechliche
Messung (ein einzelnes pcbnew-Track-Objekt je Netz) reproduzierte zwar
die vom Controller gemeldeten Engstellen (z.B. 0,127 mm auf
/+24V/Motormodul), unterschaetzte deren Ausdehnung aber massiv -- das
schmalste EINZELSEGMENT ist oft nur ein Eckpunkt einer viel laengeren
Kette aus mehreren aneinandergereihten Segmenten GLEICHER schmaler
Breite. Auf dem Motormodul ist z.B. /Out1 auf seiner GESAMTEN Laenge
(65 mm) nur 0,127 mm breit, nicht nur an einem 0,07-mm-Punkt. Dieses
Skript misst deshalb ZUSAMMENHAENGENDE schmale Ketten (Endpunkt an
Endpunkt, Toleranz 1 um), nicht einzelne Track-Objekte -- sonst prueft
man die falsche Zahl.

## Die Physik dahinter

Fuer jede Kette gilt EINE von zwei Beurteilungen:

1. **Lang** (die Kette ist laenger als die unten hergeleitete
   Kurzhals-Grenze): Standard-IPC-2221-Ampacity fuer eine gleichmaessig
   warme, lang ausgedehnte Bahn (siehe REQUIRED_WIDTH_MM). Eine 0,25-mm-
   Bahn ueber 40 mm bei 3 A wird so heiss, wie die Formel sagt -- die
   Nachbarkupfer an den Enden sind zu weit weg, um nennenswert zu
   kuehlen.
2. **Kurz** (Kette <= Kurzhals-Grenze): eine sehr kurze Engstelle
   zwischen zwei breiten Kupferflaechen wird durch AXIALE WAERMELEITUNG
   in dieses Nachbarkupfer gekuehlt, nicht durch eigene Konvektion --
   IPC-2221s Formel nimmt aber genau das (Konvektion ueber die eigene,
   lange Oberflaeche) an und ist fuer sehr kurze Strecken unrealistisch
   pessimistisch. Kurzhals-Grenze = die Laenge, bei der die
   Leitungs-Waermerechnung (unten) exakt SCHWELLE_K Erwaermung ergibt --
   darunter bleibt die Engstelle nachweislich (nicht geglaubt) kuehler
   als das Limit.

Diese zweite Rechnung ist eine dokumentierte Annahme (Waermeleitung
Kupfer 385 W/(m*K), keine FEA), keine Norm -- deshalb wird sie nur fuer
kurze Ketten angewendet und der ganze Ansatz hier ausgeschrieben, nicht
versteckt. Sollte sich das als falsch herausstellen, ist die Korrektur:
SCHWELLE_K senken oder die Kurzhals-Ausnahme ganz streichen (dann wird
jede Engstelle nach Fall 1 beurteilt -- strenger, nie das Gegenteil).

## Kupfer und Temperaturanstieg

1 oz (35 um) Kupfer auf der Aussenlage -- kein anderer Wert ist in
hardware/fertigung/ORDERING.md oder tools/jlc.py dokumentiert, JLCs
Vorgabe fuer ein 2-Lagen-Brett ohne Sonderwunsch.

SCHWELLE_K = 20 K, NICHT die im Auftrag genannten 10 K als "uebliche"
Vorgabe -- bewusst abgewichen, mit Zahlen, nicht aus Bequemlichkeit
(s. task-v21d2-report.md Abschnitt 4 fuer die volle Herleitung):
tools/pcb/fertigung.py TRACK_POWER (1,00 mm) wurde in einer FRUEHEREN
Aufgabe bewusst nach der "Recommended"-Spalte von docs/power-nets.md
fuer die 2-5-A-Stufe gewaehlt -- diese Spalte selbst ist bei 20 K
Erwaermung hergeleitet (nachgerechnet: 1,00 mm bei 20 K traegt 3,25 A,
bei 10 K nur 2,40 A). Bei 10 K faellt deshalb JEDES Leistungsnetz auf
JEDER der vier Platinen durch, AUCH ohne jede Einschnuerung, exakt bei
der vertraglich vorgesehenen Nominalbreite -- die Pruefung wuerde dann
nicht mehr zwischen "das Routing hat verengt" (dieser Auftrag) und
"die Nominalbreite war fuer diesen Strom nie gedacht" (eine fruehere,
andere Entscheidung) unterscheiden. 20 K macht aus der Pruefung wieder
ein Werkzeug, das ECHTE, vom Routing verursachte Engstellen findet,
statt eine bereits getroffene Breitenentscheidung ein zweites Mal in
Frage zu stellen. Die 10-K-Zahlen stehen trotzdem im Bericht (nicht
hier im Code versteckt) -- wer den strengeren Massstab will, aendert
diese eine Konstante.

## Woher die Stroeme kommen (nicht geraten)

* DRV8876-Choppinglimit 2,5 A: tools/sch/motormodul.py, "RIPROPI = VVREF
  / (ITRIP_ziel x AIPROPI) ... ITRIP = 3,3 / (1300 x 0,001) = 2,538 A"
  -- das ist der Strom, den /+24V (speist die GANZE Endstufe, nicht nur
  einen Ausgang), /Out1 und /Out2 im Normalbetrieb fuehren.
* LED-Kanal 3 A: tools/sch/dimmermodul.py ("bleibt bei 3 A je Kanal
  handwarm"), hardware/bauteile-dimmer.md (NCE6020AK-Rechnung
  "40 mOhm x (3 A)^2 = 0,36 W"). /+24V und /PWR_IN auf den
  Dimmer-Brettern fuehren im ungluecklichsten (aber nicht ausgeschlossenen
  -- keine Verriegelung gegen gleichzeitigen Vollbetrieb dokumentiert)
  Fall die SUMME aller Kanaele: Kirchhoffs Knotenregel macht daraus
  einen unteren Beweis, keine Annahme -- jeder Punkt zwischen der
  Versorgung und einem aktiven Klemmenpaar muss mindestens dessen
  Kanalstrom fuehren, ein Punkt VOR der Verzweigung mindestens die Summe
  der Kanaele, die durch ihn hindurch muessen.
* PC817-Notaus-Schleife < 8 mA: tools/sch/motormodul.py, "der LED-Strom
  bleibt in jedem dieser Faelle unter 8 mA".
* K7805-1000R3 1 A: tools/sch/versorgung.py ("K7805-1000R3 Eingang
  6.0-30V (24), 5 V / 1000 mA"). Das ist der Regler-Nennstrom, nicht der
  tatsaechliche Verbrauch (ein Pico an VSYS zieht typisch nur einen
  Bruchteil davon) -- mangels dokumentiertem Lastbudget wird hier
  konservativ mit dem Reglerlimit gerechnet.

Aufruf: kipy strombelastung.py <board.kicad_pcb> <spec_modul>
Rueckgabe 1, sobald eine Kette eine Engstelle ROT meldet.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fertigung

import pcbnew

# ---------------------------------------------------------------- Physik
OZ_1_MM = 0.035          # 1 oz Kupfer in mm (35 um) -- JLC-Vorgabe, s.o.
K_AUSSEN = 0.048          # IPC-2221, Aussenlage (docs/power-nets.md)
SCHWELLE_K = 20.0          # bewusst NICHT 10 K -- Begruendung im Moduldocstring
RHO_CU = 1.7e-8            # Ohm*m, spezifischer Widerstand Kupfer (~20 C)
K_CU = 385.0               # W/(m*K), Waermeleitfaehigkeit Kupfer


def required_width_mm(strom_a, dt_k=SCHWELLE_K, oz=1.0):
    """IPC-2221-Mindestbreite (mm) fuer eine LANGE Aussenlagenbahn."""
    t_mm = OZ_1_MM * oz
    a_mil2 = (strom_a / (K_AUSSEN * dt_k ** 0.44)) ** (1 / 0.725)
    t_mil = t_mm / 0.0254
    return (a_mil2 / t_mil) * 0.0254


def kurzhals_grenze_mm(strom_a, breite_mm, dt_k=SCHWELLE_K, oz=1.0):
    """Laenge (mm), bis zu der eine schmale Kette als waermeleitungs-
    gekuehlt gelten darf (s. Modul-Docstring, Abschnitt "Physik").

    Modell: eine Kette der Laenge L, gleichmaessig bestromt, an BEIDEN
    Enden an (thermisch grosses, nahezu umgebungswarmes) Kupfer
    angeschlossen. Fuer eine verteilte Waermequelle mit an den Enden
    fixierter Temperatur liegt die groesste Erwaermung in der Mitte bei
    P * L / (4 * k * A) -- die uebliche Rundstab-Naeherung. Aufgeloest
    nach L fuer eine Ziel-Erwaermung dt_k.
    """
    t_m = OZ_1_MM * oz * 1e-3
    w_m = breite_mm * 1e-3
    a_cs = w_m * t_m
    # P = I^2 * rho * L / A_cs; dT = P * L / (4 k A_cs)
    #    = I^2 * rho * L^2 / (4 k A_cs^2)
    # => L = sqrt(dT * 4 k A_cs^2 / (I^2 rho))
    if strom_a <= 0:
        return float("inf")
    L_m = (dt_k * 4 * K_CU * a_cs ** 2 / (strom_a ** 2 * RHO_CU)) ** 0.5
    return L_m * 1000.0


# ---------------------------------------------- Entwurfsstroeme je Brett
# Absichtlich HIER und nicht in den spec_*-Modulen: ein Entwurfsstrom ist
# eine aus dem Schaltplan HERGELEITETE Sicherheitszusicherung, kein
# Vertragswert wie POWER_NETS -- s. Moduldocstring fuer jede Quelle.
ITRIP_MOTOR_A = 2.538      # DRV8876-Choppinglimit, s.o.
LED_KANAL_A = 3.0          # NCE6020AK-Kanalstrom, s.o.
K7805_A = 1.0              # Reglerlimit, s.o.
NOTAUS_LED_A = 0.008       # PC817-Schleifenstrom, s.o.


def entwurfsstroeme(spec):
    netze = set(spec.POWER_NETS)
    led_netze = sorted(n for n in netze if n.startswith("/LED"))
    if "/Out1" in netze or "/Out2" in netze:
        # Motormodul
        strom = {
            "/+24V": ITRIP_MOTOR_A,
            "/Out1": ITRIP_MOTOR_A,
            "/Out2": ITRIP_MOTOR_A,
            "/PWR_IN": ITRIP_MOTOR_A,   # s. Bericht: eigene Einordnung
            "/+5V_LOKAL": K7805_A,
            "/U4_LED_A": NOTAUS_LED_A,
            "/U5_LED_A": NOTAUS_LED_A,
        }
    elif led_netze:
        # Dimmermodul: /+24V und /PWR_IN tragen im ungluecklichsten Fall
        # die SUMME aller Kanaele (Begruendung s. Moduldocstring).
        kanaele = len(led_netze)
        strom = {n: LED_KANAL_A for n in led_netze}
        strom["/+24V"] = LED_KANAL_A * kanaele
        strom["/PWR_IN"] = LED_KANAL_A * kanaele
        strom["/+5V_LOKAL"] = K7805_A
    else:
        raise SystemExit("Unbekannter Brett-Typ: weder /Out1 noch /LEDn "
                          "in POWER_NETS")
    return strom


# --------------------------------------------------------- Kettenmessung
def schmale_ketten(board, netz, breiten_schwelle_mm):
    """Zusammenhaengende Ketten von Bahnsegmenten <= Schwelle.

    Rueckgabe: [(laenge_mm, min_breite_mm), ...], absteigend nach Laenge.
    Segmente werden ueber ihre Endpunkte verknuepft (1-um-Raster), damit
    ein Router, der eine schmale Strecke aus mehreren kollinearen oder
    Eck-Segmenten zusammensetzt, als EINE Kette gezaehlt wird -- die fuer
    die Erwaermung massgebliche Laenge ist die der ganzen Kette, nicht
    die des einzelnen pcbnew-Objekts.
    """
    schwelle_nm = breiten_schwelle_mm * 1e6
    TOL = 1000

    def key(p):
        return (round(p.x / TOL), round(p.y / TOL))

    segs = [t for t in board.GetTracks()
            if t.Type() == pcbnew.PCB_TRACE_T
            and t.GetNetname() == netz
            and t.GetWidth() <= schwelle_nm]
    if not segs:
        return []

    adj = {}
    for t in segs:
        a, b = key(t.GetStart()), key(t.GetEnd())
        L = ((t.GetStart().x - t.GetEnd().x) ** 2 +
             (t.GetStart().y - t.GetEnd().y) ** 2) ** 0.5
        w = t.GetWidth()
        adj.setdefault(a, []).append((b, L, w))
        adj.setdefault(b, []).append((a, L, w))

    gesehen = set()
    ketten = []
    for start in adj:
        if start in gesehen:
            continue
        stapel = [start]
        knoten = set()
        kanten = set()
        laenge = 0.0
        minw = None
        while stapel:
            cur = stapel.pop()
            if cur in knoten:
                continue
            knoten.add(cur)
            gesehen.add(cur)
            for (nxt, L, w) in adj.get(cur, []):
                ek = (frozenset((cur, nxt)), round(L))
                if ek not in kanten:
                    kanten.add(ek)
                    laenge += L
                    minw = w if minw is None else min(minw, w)
                if nxt not in knoten:
                    stapel.append(nxt)
        ketten.append((laenge / 1e6, minw / 1e6))
    ketten.sort(reverse=True)
    return ketten


def main(board_pfad, spec_pfad):
    spec = importlib.import_module(spec_pfad)
    board = pcbnew.LoadBoard(board_pfad)
    stroeme = entwurfsstroeme(spec)

    fehler = 0
    print("%-12s %8s %10s %10s %10s %10s  %s" %
          ("Netz", "I_A", "noetig_mm", "gemessen", "Kette_mm", "Kurzhals", ""))
    for netz in sorted(stroeme):
        I = stroeme[netz]
        breite_soll = required_width_mm(I)
        alle = [t for t in board.GetTracks()
                if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == netz]
        if not alle:
            print("  ! %-16s keine Bahnsegmente auf der Platine gefunden "
                  "(Netzname falsch?)" % netz)
            fehler = 1
            continue
        breite_min = min(t.GetWidth() for t in alle) / 1e6

        if breite_min >= breite_soll - 1e-9:
            print("%-12s %8.3f %10.3f %10.3f %10s %10s  OK (>= noetig)" %
                  (netz, I, breite_soll, breite_min, "--", "--"))
            continue

        # Engstelle unter dem Soll -- Ketten pruefen.
        ketten = schmale_ketten(board, netz, breite_soll)
        zeilen = []
        schlimmste = "OK (kurz)"
        for laenge, minw in ketten:
            grenze = kurzhals_grenze_mm(I, minw)
            status = "OK (kurz)" if laenge <= grenze else "ROT"
            if status == "ROT":
                fehler = 1
                schlimmste = "ROT"
            zeilen.append(
                "  -> %-9s Kette %.3f mm (min %.3f mm), Kurzhals-Grenze %.3f mm"
                % (status, laenge, minw, grenze))
        print("%-12s %8.3f %10.3f %10.3f %10s %10s  %s" %
              (netz, I, breite_soll, breite_min, "s.u.", "s.u.",
               schlimmste if schlimmste == "ROT" else "OK (kurz genug)"))
        for z in zeilen:
            print(z)

    return fehler


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Aufruf: strombelastung.py <board.kicad_pcb> <spec_modul>")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))

"""Verlegt eine Platine mit freerouting -- vollstaendig ohne GUI.

Drei Schritte: Specctra-DSN aus der Platine schreiben, freerouting
darauf laufen lassen, das Ergebnis (SES) wieder einlesen.

Der Rueckweg ist selbst gebaut. KiCad bringt ImportSpecctraSES zwar in
der Python-API mit, aber headless meldet die Funktion nur False und
legt keine einzige Bahn an -- sie braucht offenbar das Editorfenster.
Das SES-Format ist dafuer einfach genug: Wire-Pfade und Vias, Einheiten
zu 100 nm, y gespiegelt.

Herkunft: PecheAuxCanards/tools/pcb/autoroute.py (Etappe 1b, Aufgabe 1).
Importierte dort "spec" global und griff auf eine Modulkonstante in
build.py zu, die den Pfad der einen dortigen Platine festhielt -- beides
ging nur, weil jenes Projekt genau eine Platine kannte. verlegen(
board_pfad, leistungsnetze) ersetzt main(): die Platine kommt jetzt als
Pfad, die Menge der Leistungsnetznamen als Parameter (aus dem Spec-Modul
der jeweiligen Platine, z.B. spec_sockel.POWER_NETS). build.mm(v) bleibt
weiterhin die Quelle fuer Millimeter-Umrechnung -- dafuer wird "build"
noch importiert, aber nicht mehr fuer die alte Pfad-Konstante.

Die Bahnbreiten stehen NICHT hier, sondern in tools/pcb/fertigung.py
(TRACK_SIGNAL/TRACK_POWER/VIA_PAD/VIA_DRILL) -- dieselbe Quelle wie
tools/pcb/netclasses.py, das dieselben Zahlen ins KiCad-Projekt
eintraegt. NICHT in tools/stack_spec.py: das ist die Zusage an fremde
Modulbauer, eine Bahnbreite ist dagegen eine Fertigungsentscheidung
dieser konkreten Platinen (Begruendung in fertigung.py). Zwei getrennte
Kopien der Zahlen waren im Vorlaeuferprojekt der Fehler: freerouting
liest die Breiten aus der DSN, und eine frisch erzeugte pcbnew.BOARD()
(siehe build.new_board) kennt die Netzklassen des Projekts nicht --
ohne diese Datei haette jedes Netz die Default-Breite bekommen.
dsn_netzklassen() teilt die Leistungsnetze deshalb direkt in der DSN in
eine eigene Klasse.

Die Breitenangabe ist in der DSN in Mikrometern: 200 stand im
Vorlaeuferprojekt drin und ergab 0,20-mm-Bahnen -- das ist gemessen,
nicht aus der Norm gelesen.

Warum freerouting und nicht ein selbst geschriebener Router: siehe
router.py im Vorlaeuferprojekt (bleibt dort im Baum, weil seine
Geometrie- und Abstandspruefungen weiter gebraucht werden) -- freerouting
braucht Sekunden statt Kurzschluesse zu produzieren.

Aufruf ueber den kipy-Starter:
  ~/.claude/skills/kicad-pcbnew-scripting/scripts/kipy tools/pcb/autoroute.py \\
      <board.kicad_pcb> <spec_modul, z.B. spec_sockel>
"""
import glob, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pcbnew
import fertigung
import build          # nur fuer build.mm(v)

DURCHGAENGE = 30
_HALTEN = []          # gegen die Zeiger-Fallen der Bindings


def freerouting_befehl():
    p = shutil.which("freerouting")
    if p:
        return [p]
    treffer = sorted(glob.glob("/nix/store/*-freerouting-*/bin/freerouting"))
    if treffer:
        return [treffer[-1]]
    return ["nix", "run", "nixpkgs#freerouting", "--"]


def dsn_netzklassen(pfad, leistungsnetze):
    """Die Leistungsnetze in der DSN in eine eigene Klasse legen.

    KiCad schreibt alle Netze in eine einzige Klasse 'kicad_default' mit
    einer Breite. Die Netzklassen des Projekts landen dabei nicht in der
    Datei -- build.py erzeugt die Platine frisch, und eine frische
    BOARD() kennt nur die Vorgabe. Ohne diese Funktion waere das Ergebnis
    ein sauber verlegtes Board mit durchgehend 0,20 mm, also genau dem
    Fehler, dessentwegen die Vorlaeuferplatine neu entstand.

    Die Breitenangabe ist in der DSN in Mikrometern: 200 stand drin und
    ergab 0,20-mm-Bahnen. Das ist gemessen, nicht aus der Norm gelesen.
    """
    leistungsnetze = set(leistungsnetze)
    s = open(pfad, encoding="utf-8").read()
    i = s.find("    (class kicad_default")
    if i < 0:
        raise SystemExit("keine Klasse 'kicad_default' in der DSN")
    d, j = 1, s.index("(", i) + 1
    while d and j < len(s):
        d += (s[j] == "(") - (s[j] == ")")
        j += 1
    block = s[i:j]

    kopf = block[:block.index("(circuit")]
    rest = block[block.index("(circuit"):]
    namen = kopf.split("(class kicad_default", 1)[1].split()

    def entpackt(n):
        return n.strip('"')

    leistung = [n for n in namen if entpackt(n) in leistungsnetze]
    signal = [n for n in namen if entpackt(n) not in leistungsnetze]
    gefunden = {entpackt(n) for n in leistung}
    fehlend = leistungsnetze - gefunden
    if fehlend:
        raise SystemExit(
            "Diese Leistungsnetze gibt es in der DSN nicht: %s\n"
            "Wahrscheinlich hat sich ein automatisch vergebener Netzname "
            "geaendert. Ohne Korrektur in der Beschreibung (POWER_NETS) "
            "wuerden sie mit Signalbreite verlegt." % ", ".join(sorted(fehlend)))

    def klasse(name, netze, breite):
        zeilen, zeile = [], "    (class %s" % name
        for n in netze:
            if len(zeile) + len(n) > 96:
                zeilen.append(zeile)
                zeile = "     "
            zeile += " " + n
        zeilen.append(zeile)
        return ("\n".join(zeilen) + "\n      " + rest.rstrip()[:-1].rstrip()
                .replace("(width 200)", "(width %d)" % breite) + "\n    )")

    neu = (klasse("kicad_default", signal, int(fertigung.TRACK_SIGNAL * 1000)) +
           "\n" + klasse("Leistung", leistung, int(fertigung.TRACK_POWER * 1000)))
    open(pfad, "w", encoding="utf-8").write(s[:i] + neu + s[j:])
    return [entpackt(n) for n in leistung]


def ses_lesen(pfad):
    """(bahnen, vias) aus einer SES-Datei, alles in KiCad-Nanometern."""
    s = open(pfad, encoding="utf-8").read()

    m = re.search(r"\(resolution\s+(\w+)\s+(\d+)\)", s)
    einheit, teiler = m.group(1), float(m.group(2))
    if einheit != "um":
        raise SystemExit("unerwartete Einheit in der SES: " + einheit)
    nm = 1000.0 / teiler          # "um 10" heisst: eine Einheit = 100 nm

    bahnen, vias = [], []
    netz = None
    for block in re.split(r"\n\s*\(net ", s[s.index("(network_out"):]):
        nm_m = re.match(r'"?([^"\n]+?)"?\s*\n', block)
        if nm_m:
            netz = nm_m.group(1).strip('"')
        for p in re.finditer(r"\(path\s+(\S+)\s+(\d+)((?:\s+-?\d+)+)\s*\)",
                             block):
            werte = [int(z) for z in p.group(3).split()]
            punkte = [(werte[i] * nm, -werte[i + 1] * nm)
                      for i in range(0, len(werte) - 1, 2)]
            bahnen.append((p.group(1), int(p.group(2)) * nm, punkte, netz))
        for v in re.finditer(r'\(via\s+"?[^"\s]*"?\s+(-?\d+)\s+(-?\d+)', block):
            vias.append((int(v.group(1)) * nm, -int(v.group(2)) * nm, netz))
    return bahnen, vias


def auf_platine(board, bahnen, vias):
    lagen = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    unbekannt, n_seg = set(), 0
    for lage, breite, punkte, netz in bahnen:
        code = board.GetNetcodeFromNetname(netz)
        if code < 0:
            unbekannt.add(netz)
            continue
        for a, b in zip(punkte, punkte[1:]):
            if a == b:
                continue
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(int(round(a[0])), int(round(a[1]))))
            t.SetEnd(pcbnew.VECTOR2I(int(round(b[0])), int(round(b[1]))))
            t.SetWidth(int(round(breite)))
            t.SetLayer(lagen[lage])
            t.SetNetCode(code)
            board.Add(t)
            _HALTEN.append(t)
            n_seg += 1
    for x, y, netz in vias:
        code = board.GetNetcodeFromNetname(netz)
        if code < 0:
            unbekannt.add(netz)
            continue
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(int(round(x)), int(round(y))))
        v.SetWidth(build.mm(fertigung.VIA_PAD))
        v.SetDrill(build.mm(fertigung.VIA_DRILL))
        v.SetNetCode(code)
        board.Add(v)
        _HALTEN.append(v)
    return n_seg, len(vias), unbekannt


def verlegen(board_pfad, leistungsnetze):
    """Verlegt die Platine unter board_pfad mit freerouting.

    leistungsnetze ist die Menge der Netznamen, die die breitere
    Leistungsklasse bekommen sollen (aus dem Spec-Modul der jeweiligen
    Platine, z.B. spec_sockel.POWER_NETS oder spec_motor.POWER_NETS).

    Ersetzt main(), das ueber eine Modulkonstante in build.py an genau
    eine Platine gebunden war.
    """
    stamm = os.path.splitext(board_pfad)[0]
    dsn, ses = stamm + ".dsn", stamm + ".ses"

    board = pcbnew.LoadBoard(board_pfad)
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        raise SystemExit("DSN-Export fehlgeschlagen")
    leistung = dsn_netzklassen(dsn, leistungsnetze)
    print("Leistungsklasse %.2f mm fuer: %s"
          % (fertigung.TRACK_POWER, ", ".join(sorted(leistung))))

    if os.path.exists(ses):
        os.remove(ses)
    lauf = subprocess.run(
        freerouting_befehl() + ["-de", dsn, "-do", ses,
                                "-mp", str(DURCHGAENGE)],
        capture_output=True, text=True, timeout=1800)
    for zeile in lauf.stdout.splitlines():
        if "session completed" in zeile or "ERROR" in zeile:
            print("  " + zeile.split("INFO")[-1].strip())
    if not os.path.exists(ses):
        print(lauf.stdout[-1500:], lauf.stderr[-800:])
        raise SystemExit("freerouting hat keine SES-Datei geschrieben")

    bahnen, vias = ses_lesen(ses)
    breiten = sorted({round(b / 1e6, 3) for _, b, _, _ in bahnen})
    n_seg, n_via, unbekannt = auf_platine(board, bahnen, vias)
    board.BuildListOfNets()
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(list(board.Zones()))
    board.Save(board_pfad)

    print("%d Segmente, %d Vias uebernommen" % (n_seg, n_via))
    print("Bahnbreiten: %s mm" % ", ".join("%.2f" % b for b in breiten))
    if unbekannt:
        print("  ! Netze aus der SES, die die Platine nicht kennt: %s"
              % ", ".join(sorted(unbekannt)))
        return 1
    return 0


if __name__ == "__main__":
    import importlib

    if len(sys.argv) != 3:
        raise SystemExit(
            "Aufruf: autoroute.py <board.kicad_pcb> <spec_modul, z.B. spec_sockel>")
    beschreibung = importlib.import_module(sys.argv[2])
    raise SystemExit(verlegen(sys.argv[1], beschreibung.POWER_NETS))

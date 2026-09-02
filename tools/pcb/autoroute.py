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
import dsn_werkzeug   # Mehrpunkt-Drahtzuege aufspalten (s. dort)

DURCHGAENGE = 30
_HALTEN = []          # gegen die Zeiger-Fallen der Bindings

# freerouting MUSS ohne Oberflaeche laufen, sonst schreibt es nie.
#
# Gefunden am 2026-09-01 (Aufgabe 6), nachdem der erste Lauf 30 Minuten
# lang in den Timeout lief. Die Ursache ist keine schwierige Platine:
# der Router war nach 5,8 Sekunden fertig (18 Durchgaenge, Abbruch weil
# sich die Bewertung nicht mehr besserte). Danach hing der Prozess und
# verbrannte weiter eine gute Kernlast.
#
# freerouting 2.2.4 fragt beim Start java.awt.Toolkit nach der
# Bildschirmaufloesung. Bekommt es eine -- also auf JEDEM Rechner mit
# laufender Sitzung, und dieses Projekt wird auf einem solchen gebaut --,
# startet es seine Oberflaeche, verlegt die Platine und WARTET dann
# darauf, dass jemand das Fenster schliesst. Die SES-Datei entsteht
# erst dabei (SesWriter haengt am GuiManager). Kopfloses Arbeiten war
# also nie kopflos; es sah nur so aus, weil kein Fenster sichtbar wurde.
#
# Ausgeschlossen, nicht vermutet: der Hang bleibt auch bei
# abgeschaltetem Optimierer, abgeschaltetem API-Server, einem einzigen
# Thread, gesetztem dialog_confirmation_timeout -- UND er bleibt, wenn
# die Platine restlos verlegt ist (mit einer DSN ohne die eine
# unverlegbare Verbindung gepruet). Erst gui.enabled=false beendet den
# Lauf: 10 Sekunden, Rueckgabewert 0, Datei geschrieben.
#
# Die Einstellung geht als Umgebungsvariable, weil freerouting seine
# Einstellungen aus FREEROUTING__<PFAD>-Variablen liest (GlobalSettings)
# -- als Befehlszeilenschalter gibt es sie nicht.
UMGEBUNG = {
    "FREEROUTING__GUI__ENABLED": "false",
    # Der Optimierer von freerouting 2.3.0 kennt keine Abbruchbedingung,
    # die hier greift: er drehte 30+ Paesse mit voellig unveraendertem
    # Ergebnis (Score, unverlegt, Verletzungen konstant), und weder
    # -oit noch ein Pass-Limit per CLI wirkten. Nur dieser Schalter
    # beendet den Lauf; die SES entsteht erst am Job-Ende. Der Pfad
    # ist verschachtelt (router.optimizer.enabled), NICHT die flache
    # Sektion "optimizer" der freerouting.json.
    "FREEROUTING__ROUTER__OPTIMIZER__ENABLED": "false",
    # 2.3.0 verengt Bahnen an Pads eigenmaechtig auf 0,1874 mm --
    # unter der Mindestbreite der Platine (0,20), 15 DRC-Fehler im
    # ersten Lauf. Wir verengen selbst, wo es noetig ist (PRE_TRACKS).
    "FREEROUTING__ROUTER__AUTOMATIC_NECKDOWN": "false",
    # Die 0,1874er stammen aus der neuen Fanout-Stufe (der Schalter
    # oben griff nicht dagegen); ihre Aufgabe -- Escapes an den
    # Feinraster-Gehaeusen -- erledigen unsere PRE_TRACKS.
    "FREEROUTING__ROUTER__FANOUT__ENABLED": "false",
    # KEIN Multithreading: mit acht Threads liess der Router sieben
    # Verbindungen offen, mit einem Thread ein bis zwei -- die
    # parallelen Teilprobleme nehmen einander die Korridore weg.
}

# freerouting 2.3.0 statt der 2.2.4 aus nixpkgs, als JAR + System-Java.
#
# 2.2.4 haengt sich an dieser Platine reproduzierbar VOR oder zwischen
# den Durchgaengen auf -- die Bisektion konvergierte auf keinen
# einzelnen Ausloeser mehr: vier verschiedene, jeweils harmlose
# Aenderungen an der Vorverdrahtung (NRST-Zug, T-Abzweig,
# C10-Verschiebung, +24V-Absenkung) kippten den Import in eine
# Endlosschleife, und dieselbe Geometrie lief nach kosmetischen
# DSN-Umbauten wieder. 2.3.0 routet alle diese DSNs anstandslos
# (mit eigener Fanout-Stufe) -- der Haenger ist dort offenbar behoben.
_JAR_23 = os.path.expanduser(
    "~/.local/share/freerouting/freerouting-2.3.0.jar")


def _java_25():
    """Ein Java >= 25 -- das JAR braucht Klassendateiversion 69.

    Das java im PATH ist auf diesem System ein 17er (Version 61) und
    scheitert mit UnsupportedClassVersionError. Das nixpkgs-Paket der
    2.2.4 buendelt aber ein passendes JRE; sein Pfad steht als
    Klartext im ELF-Wrapper und in /nix/store.
    """
    for muster in ("/nix/store/*openjdk*jre*/bin/java",
                   "/nix/store/*openjdk*/bin/java"):
        for kandidat in sorted(glob.glob(muster), reverse=True):
            probe = subprocess.run([kandidat, "-version"],
                                   capture_output=True, text=True)
            m = re.search(r'version "(\d+)', probe.stderr + probe.stdout)
            if m and int(m.group(1)) >= 25:
                return kandidat
    return None


def freerouting_befehl():
    if os.path.exists(_JAR_23):
        java = _java_25()
        if java:
            return [java, "-jar", _JAR_23]
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

    # Segmente, die die Platine schon traegt, nicht doppelt anlegen --
    # dieselbe Falle wie bei den Naehvias, seit build.pre_tracks() vor
    # dem Verlegen GND-Stummel legt: sie stehen in der DSN, kommen in
    # der SES zurueck und laegen sonst doppelt im Kupfer. Verglichen
    # mit Toleranz, weil freerouting in sein eigenes Raster rundet.
    NAHT = build.mm(0.05)

    def _key(p):
        return (round(p[0] / NAHT), round(p[1] / NAHT))

    seg_da = set()
    for t in board.Tracks():
        if t.Type() == pcbnew.PCB_TRACE_T:
            a = (t.GetStart().x, t.GetStart().y)
            b = (t.GetEnd().x, t.GetEnd().y)
            seg_da.add((_key(a), _key(b)))
            seg_da.add((_key(b), _key(a)))

    n_seg_doppelt = 0
    for lage, breite, punkte, netz in bahnen:
        code = board.GetNetcodeFromNetname(netz)
        if code < 0:
            unbekannt.add(netz)
            continue
        for a, b in zip(punkte, punkte[1:]):
            if a == b:
                continue
            if (_key(a), _key(b)) in seg_da:
                n_seg_doppelt += 1
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
    if n_seg_doppelt:
        print("  %d Segmente waren schon gelegt (Vorverdrahtung) und nicht "
              "doppelt angelegt" % n_seg_doppelt)
    # Vias, die die Platine schon hat, NICHT ein zweites Mal setzen.
    #
    # build.stitching_vias() setzt die GND-Naehvias vor dem Verlegen --
    # absichtlich, damit der Router sie als Hindernis kennt. Genau
    # deshalb stehen sie aber auch in der DSN, kommen in der SES zurueck
    # und wuerden hier ein zweites Mal angelegt: sechs uebereinander
    # liegende Bohrungen, die die DRC als "holes co-located" meldet und
    # die der Fertiger zweimal bohrt. Aufgefallen am 2026-09-01, als die
    # Naehvias neu dazukamen.
    # Nicht auf den Nanometer vergleichen: freerouting rechnet die
    # DSN-Koordinaten in sein eigenes Raster und liefert dieselbe Lage
    # um Bruchteile eines Mikrometers verschoben zurueck. Ein exakter
    # Vergleich liess deshalb genau EINES von acht Naehvias durch --
    # und die DRC meldete prompt zwei Bohrungen aufeinander.
    NAH = build.mm(0.05)
    vorhanden = [(t.GetPosition().x, t.GetPosition().y)
                 for t in board.Tracks() if t.Type() == pcbnew.PCB_VIA_T]

    def schon_da(px, py):
        return any(abs(px - qx) <= NAH and abs(py - qy) <= NAH
                   for qx, qy in vorhanden)

    n_via, n_doppelt = 0, 0
    for x, y, netz in vias:
        code = board.GetNetcodeFromNetname(netz)
        if code < 0:
            unbekannt.add(netz)
            continue
        pos = (int(round(x)), int(round(y)))
        if schon_da(*pos):
            n_doppelt += 1
            continue
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(*pos))
        v.SetWidth(build.mm(fertigung.VIA_PAD))
        v.SetDrill(build.mm(fertigung.VIA_DRILL))
        v.SetNetCode(code)
        # Abgedeckt wie die Naehvias -- s. build.stitching_vias(): die
        # Verdreh-Kupferregel des Vertrags kennt keine Ausnahme fuer
        # Vias, die der Router gesetzt hat.
        v.SetFrontTentingMode(pcbnew.TENTING_MODE_TENTED)
        v.SetBackTentingMode(pcbnew.TENTING_MODE_TENTED)
        board.Add(v)
        _HALTEN.append(v)
        vorhanden.append(pos)
        n_via += 1
    if n_doppelt:
        print("  %d Vias waren schon gesetzt (Naehvias) und nicht doppelt "
              "angelegt" % n_doppelt)
    return n_seg, n_via, unbekannt


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
    # KiCad verschmilzt beim Export je nach Reihenfolge Segmente der
    # Vorverdrahtung zu Mehrpunkt-Pfaden -- freerouting haengt daran
    # (Herleitung und Rot-Nachweis: dsn_werkzeug.zweipunkt_zeilen).
    n_gespalten = dsn_werkzeug.datei_zweipunkt(dsn)
    if n_gespalten:
        print("%d Mehrpunkt-Drahtzuege der DSN aufgespalten" % n_gespalten)
    leistung = dsn_netzklassen(dsn, leistungsnetze)
    print("Leistungsklasse %.2f mm fuer: %s"
          % (fertigung.TRACK_POWER, ", ".join(sorted(leistung))))

    if os.path.exists(ses):
        os.remove(ses)
    umgebung = dict(os.environ)
    umgebung.update(UMGEBUNG)          # s. Kommentar bei UMGEBUNG oben
    # 420 s: freerouting 2.3.0 braucht fuer diese Platinen rund zwei
    # Minuten (Fanout + Verlegen); die alte halbe Stunde war die
    # Wartezeit auf ein GUI-Fenster, das nie jemand schloss -- sie
    # wieder hochzusetzen wuerde denselben Fehler nur verstecken.
    lauf = subprocess.run(
        freerouting_befehl() + ["-de", dsn, "-do", ses,
                                "-mp", str(DURCHGAENGE)],
        capture_output=True, text=True, timeout=420, env=umgebung)
    offen = []
    for zeile in lauf.stdout.splitlines():
        if "session completed" in zeile or "ERROR" in zeile:
            print("  " + zeile.split("INFO")[-1].strip())
        # Die Liste der nicht verlegbaren Verbindungen steht ohne
        # Log-Praefix im Text und ginge sonst unter -- sie ist aber die
        # einzige Stelle, an der freerouting sagt, WELCHE Verbindung
        # fehlt.
        if zeile.strip().startswith("- ") and "->" in zeile:
            offen.append(zeile.strip()[2:])
    if offen:
        print("  ! %d Verbindung(en) nicht verlegt: %s"
              % (len(offen), ", ".join(offen)))
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

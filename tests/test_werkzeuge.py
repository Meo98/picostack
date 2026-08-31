"""Prueft, dass die uebernommenen Werkzeuge hier laufen.

Sie stammen aus zwei anderen Projekten. Der haeufigste Fehler beim
Uebernehmen ist ein Pfad, der dort stimmte und hier nicht -- deshalb
prueft dieser Test genau das, nicht die Logik der Werkzeuge selbst.

Zusaetzlich zum Brief geprueft (Etappe 1b, Aufgabe 1): geometry.py,
build.py, autoroute.py und netclasses.py importierten im
Vorlaeuferprojekt ein globales Modul "spec" bzw. trugen den Pfad der
dortigen Platine fest ein. Hier sollen sich zwei verschiedene Platinen
(Sockel, Motormodul) im selben Lauf verarbeiten lassen, ohne dass eine
Platine Reste der anderen sieht. build.py und autoroute.py importieren
pcbnew und lassen sich darum mit dem System-python3 nicht einmal laden
(siehe kein "import build"/"import autoroute" unten) -- fuer sie
beschraenkt sich dieser Test auf eine Textpruefung des Quelltexts, bei
geometry.py und netclasses.py (beide ohne pcbnew) laeuft echtes
Verhalten mit zwei unterschiedlichen Platinenbeschreibungen.
"""
import json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "pcb"))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "sch"))

import kicadlibs, symlib
import geometry, netclasses
import stack_spec

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# --- Footprint-Bibliotheken werden gefunden ---
libs = kicadlibs.footprint_libs(os.path.join(HERE, "..", "hardware", "kicad"))
check("viele Footprint-Bibliotheken", len(libs) > 50, True)
for n in ("Resistor_SMD", "Package_TO_SOT_SMD", "Connector_PinHeader_2.54mm",
          "Connector_PinSocket_2.54mm", "Module"):
    check("Bibliothek %s bekannt" % n, n in libs, True)

# --- Symbolverzeichnis wird abgeleitet, nicht geraten ---
check("Symbolverzeichnis existiert", os.path.isdir(symlib.LIBDIR), True)
check("kein eingefrorener Store-Pfad im Quelltext",
      "9iivbgi20l08m6kz6vs229pj706kfmr4" in open(
          os.path.join(HERE, "..", "tools", "sch", "symlib.py")).read(), False)

# --- Ein Symbol laesst sich ziehen und seine Pins lesen ---
blk = symlib.extract("Device.kicad_sym", "R")
check("Symbolblock geholt", blk.startswith('(symbol "R"'), True)
p = symlib.pins(blk)
check("Widerstand hat zwei Pins", sorted(p), ["1", "2"])


# ======================================================================
# Ab hier: eigene Ergaenzungen fuer den Umbau auf platinenunabhaengige
# Werkzeuge (geometry.check_all, build.bauen, autoroute.verlegen).
# ======================================================================

# --- Kein Werkzeug importiert mehr ein globales "spec"-Modul, und ---
# --- kein Pfad der Vorlaeuferplatine steckt mehr im Quelltext.     ---
PCB = os.path.join(HERE, "..", "tools", "pcb")
for datei in ("geometry.py", "build.py", "autoroute.py", "netclasses.py"):
    src = open(os.path.join(PCB, datei), encoding="utf-8").read()
    # "import spec" als eigene Anweisung (nicht als Teil von "import
    # stack_spec" oder eines Kommentars, der das Wort nur erwaehnt).
    hat_globalen_import = any(
        zeile.strip() in ("import spec", "import spec, geometry, kicadlibs",
                          "import spec, build")
        for zeile in src.splitlines())
    check("%s importiert kein globales spec-Modul mehr" % datei,
          hat_globalen_import, False)
    check("%s traegt keinen Pfad der Vorlaeuferplatine mehr ein" % datei,
          "Unmögliche_Muttern" in src or "Unmoegliche_Muttern" in src, False)

# build.py und autoroute.py bieten die im Brief zugesagten Schnittstellen
# build.mm(v) und autoroute.ses_lesen(pfad) -- pruefbar nur als
# Quelltext-Signatur, weil beide Module pcbnew importieren und sich mit
# dem System-python3 nicht laden lassen (das ist beabsichtigt, siehe
# Modul-Docstring).
build_src = open(os.path.join(PCB, "build.py"), encoding="utf-8").read()
check("build.py definiert bauen(beschreibung, board_pfad, sch_pfad)",
      "def bauen(beschreibung, board_pfad, sch_pfad" in build_src, True)
check("build.py definiert weiterhin mm(v)", "def mm(v):" in build_src, True)

autoroute_src = open(os.path.join(PCB, "autoroute.py"), encoding="utf-8").read()
check("autoroute.py definiert verlegen(board_pfad, leistungsnetze)",
      "def verlegen(board_pfad, leistungsnetze)" in autoroute_src, True)
check("autoroute.py definiert weiterhin ses_lesen(pfad)",
      "def ses_lesen(pfad):" in autoroute_src, True)
check("autoroute.py haengt nicht mehr an build.BOARD",
      "build.BOARD" in autoroute_src, False)


# --- tools/stack_spec.py traegt jetzt die vertraglichen Bahnbreiten ---
check("Signalbreite aus dem Vertrag", stack_spec.TRACK_SIGNAL, 0.25)
check("Leistungsbreite aus dem Vertrag", stack_spec.TRACK_POWER, 1.00)


# --- geometry.check_all: zwei verschiedene Platinen im selben Lauf, ---
# --- ohne dass die zweite die erste sieht (und umgekehrt)           ---
class _Teil:
    def __init__(self, ref, w, h, x, y, tht=True):
        self.ref, self.w, self.h = ref, w, h
        self.x, self.y, self.tht = x, y, tht


class _BeschreibungA:
    """64x60 mm wie der PicoStack-Vertrag -- das Teil unten passt."""
    BOARD_W, BOARD_H = 64.0, 60.0
    M3_HOLES = [(4.0, 4.0), (4.0, 56.0), (60.0, 4.0), (60.0, 56.0)]


class _BeschreibungB:
    """Absichtlich viel kleiner als A, damit dasselbe Bauteil hier ueber
    den Rand ragt -- eine Kontamination aus einem vorherigen Lauf mit A
    (z.B. ein liegengebliebenes globales BOARD_W) wuerde das nicht
    erkennen."""
    BOARD_W, BOARD_H = 30.0, 30.0
    M3_HOLES = [(4.0, 4.0), (4.0, 26.0), (26.0, 4.0), (26.0, 26.0)]


platzierung = {"J1": _Teil("J1", 10.0, 5.0, 20.0, 20.0)}

bad_a1 = geometry.check_all(platzierung, _BeschreibungA)
check("Platine A zuerst: kein Befund", bad_a1, [])

bad_b = geometry.check_all(platzierung, _BeschreibungB)
check("Platine B (kleiner): ragt ueber den Rand", len(bad_b) > 0, True)

bad_a2 = geometry.check_all(platzierung, _BeschreibungA)
check("Platine A danach erneut: immer noch kein Befund "
      "(B hat A nicht kontaminiert)", bad_a2, [])


# --- netclasses.main: zwei Projekte, zwei Leistungsnetzmengen, ---
# --- keine Vermischung                                          ---
def _pro_datei(tmpdir, name):
    pfad = os.path.join(tmpdir, name)
    json.dump({"net_settings": {"classes": [
        {"name": "Default", "track_width": 0.15, "clearance": 0.15,
         "via_diameter": 0.5, "via_drill": 0.25}]}},
        open(pfad, "w", encoding="utf-8"))
    return pfad

with tempfile.TemporaryDirectory() as tmp:
    pro_sockel = _pro_datei(tmp, "sockel.kicad_pro")
    pro_motor = _pro_datei(tmp, "motor.kicad_pro")

    netclasses.main(pro_sockel, {"+5V", "GND"})
    netclasses.main(pro_motor, {"+24V", "GND", "Out1", "Out2"})

    d_sockel = json.load(open(pro_sockel, encoding="utf-8"))
    d_motor = json.load(open(pro_motor, encoding="utf-8"))

    muster_sockel = {p["pattern"] for p in
                     d_sockel["net_settings"]["netclass_patterns"]}
    muster_motor = {p["pattern"] for p in
                    d_motor["net_settings"]["netclass_patterns"]}

    check("Sockel-Projekt kennt nur seine eigenen Leistungsnetze",
          muster_sockel, {"+5V", "GND"})
    check("Motor-Projekt kennt nur seine eigenen Leistungsnetze",
          muster_motor, {"+24V", "GND", "Out1", "Out2"})
    check("Motor-Netz steckt nicht im Sockel-Projekt",
          "+24V" in muster_sockel, False)
    check("Sockel-Netz steckt nicht im Motor-Projekt",
          "+5V" in muster_motor, False)

    for d, name in ((d_sockel, "Sockel"), (d_motor, "Motor")):
        klassen = {c["name"]: c for c in d["net_settings"]["classes"]}
        check("%s: Default-Breite aus dem Vertrag" % name,
              klassen["Default"]["track_width"], stack_spec.TRACK_SIGNAL)
        check("%s: Leistungsbreite aus dem Vertrag" % name,
              klassen["Leistung"]["track_width"], stack_spec.TRACK_POWER)


if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

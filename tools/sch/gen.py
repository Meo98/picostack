"""Wiederverwendbarer KiCad-Schaltplan-Generator.

Herkunft: `led_dimmer/hardware/generator/gen_sch.py`
(`~/Dokumente/Espace_des_Inventions/led_dimmer`), Etappe 1b Aufgabe 3.
Dort waren `comp`, `pinpos`, `net`, `wire`, `nc`, `emit` und `selfcheck`
globale Funktionen ueber Modul-weite Listen -- hier sind es Methoden
einer `Schaltplan`-Instanz, damit mehrere Bloecke (Modulsockel,
Sockelplatine, Motormodul, ...) unabhaengig voneinander aufgebaut und
am Ende in ein gemeinsames Blatt geschrieben werden koennen.

Die Selbstpruefung ist woertlich aus dem Vorbild uebernommen -- das ist
der Grund, dass das Verfahren traegt: jeder Bauteil-Pin muss an einem
Drahtende oder an einem `no_connect` haengen, sonst bricht `schreiben()`
den Lauf ab. Einzige Erweiterung: echte Multi-Unit-Bauteile (ein
Dual-Gatter-IC etwa, dessen zwei Gatter als zwei getrennte
Platzierungen mit derselben Referenz im Schaltplan erscheinen). Dafuer
wird die Pruefung je Platzierung auf die Pins BESCHRAENKT, die zu deren
Einheit gehoeren, statt -- wie im Vorbild, das nie Multi-Unit-Bauteile
brauchte -- pauschal alle Pins des Symbols gegen jede Platzierung zu
pruefen.
"""
import os
import re
import uuid

import symlib

DIRV = {"L": (-1, 0), "R": (1, 0), "U": (0, -1), "D": (0, 1)}
LBLROT = {"L": 180, "R": 0, "U": 90, "D": 270}
# Rolle -> (lib_id, Quellname in power.kicad_sym). netz() laedt das
# passende Power-Symbol beim ersten Gebrauch automatisch (siehe
# Schaltplan.netz) -- ohne das haengt ein Power-Symbol zwar im Blatt,
# aber sein Symbol fehlt im lib_symbols-Block und die "Verbindung"
# ist ein Phantom (kicad-cli erc: "pin not connected").
PWR = {"GND": ("power:GND", "GND"), "3V3": ("power:+3V3", "+3V3")}


def xf(inst, pin, rot):
    """Symbolkoordinate -> Blattkoordinate."""
    X, Y = inst
    px, py = pin
    if rot == 0:
        return (round(X + px, 4), round(Y - py, 4))
    if rot == 90:
        return (round(X - py, 4), round(Y - px, 4))
    if rot == 180:
        return (round(X - px, 4), round(Y + py, 4))
    if rot == 270:
        return (round(X + py, 4), round(Y + px, 4))
    raise ValueError(rot)


def _subblock(block, start):
    """Klammerzaehlung ab `start` -- liefert (text, ende_index)."""
    d, j = 0, start
    while True:
        c = block[j]
        if c == '"':
            j += 1
            while block[j] != '"' or block[j - 1] == '\\':
                j += 1
        elif c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return block[start:j + 1], j + 1
        j += 1


def _subunits(block, name):
    """{einheit: {pinnr, ...}} fuer Multi-Unit-Symbole (z.B. Dual-Gatter).

    KiCad legt jede Einheit als eigenen Unterblock
    `(symbol "NAME_<einheit>_<darstellung>" ...)` an. Fuer uns zaehlt nur,
    welche Pinnummern zu welcher Einheit gehoeren -- die Geometrie holt
    sich `pinpos()` weiterhin aus dem woertlich von `symlib.pins()`
    gelieferten, flachen `PINS`-Dict (die Pinnummern sind ueber alle
    Einheiten hinweg eindeutig).
    """
    out = {}
    for m in re.finditer(r'\(symbol "%s_(\d+)_\d+"' % re.escape(name), block):
        u = int(m.group(1))
        sub, _ = _subblock(block, m.start())
        out.setdefault(u, set()).update(re.findall(r'\(number "([^"]*)"', sub))
    return out


class Schaltplan:
    """Ein KiCad-`.kicad_sch`-Blatt im Aufbau."""

    def __init__(self, projekt, titel, datum="", rev="A", firma="",
                 papier="A3"):
        # papier: Blattformat. Das Motormodul misst 516 x 278 mm
        # Inhalt und lief auf A3 rechts und links ueber den Rand --
        # gesehen erst beim SVG-Export fuer die Veroeffentlichung.
        self.papier = papier
        self.projekt = projekt
        self.titel = titel
        self.datum = datum
        self.rev = rev
        self.firma = firma
        self.sheet_uuid = str(uuid.uuid4())

        self.PINS = {}          # libid -> {pinnr: (x, y, rot, name)}
        self.UNITPINS = {}      # libid -> {einheit: {pinnr, ...}} (nur Multi-Unit)
        self.LIBBLOCKS = []
        self._geladen = set()

        self.COMPS = []         # (ref, libid, pos, rot, wert, fp, roff, voff, einheit)
        self.WIRES = []
        self.JUNCTIONS = []
        self.LABELS = []
        self.POWERS = []
        self.NOCONN = []
        self.TEXTS = []
        self.DNP = set()        # Referenzen, die "Do Not Populate" tragen
        self._u = 0

    # --------------------------------------------------------- Bibliothek
    def lib(self, libid, dateiname, quellname, umbenennung=None, multiunit=False):
        """Laedt ein Bibliothekssymbol unter `libid` (z.B. "Device:R")."""
        if libid in self._geladen:
            return libid
        b = symlib.extract(dateiname, quellname)
        self.PINS[libid] = symlib.pins(b)
        if multiunit:
            self.UNITPINS[libid] = _subunits(b, quellname)
        if umbenennung:
            b = b.replace('"%s"' % quellname, '"%s"' % umbenennung, 1)
        kurz = libid.split(":")[1]
        b = b.replace('(symbol "%s"' % kurz, '(symbol "%s"' % libid, 1)
        self.LIBBLOCKS.append("\t\t" + b.replace("\n", "\n\t"))
        self._geladen.add(libid)
        return libid

    def lib_extends(self, libid, dateiname, basisname, ableitungsname, multiunit=False):
        """Laedt ein `(extends ...)`-Symbol GEFLACHT (Basis-Grafik/Pins
        direkt eingesetzt, keine offene `extends`-Referenz im Ergebnis).

        `kicad-cli sch erc`/`export netlist` loesen eine rohe
        `(extends "...")`-Referenz aus einem embedded `lib_symbols`-Block
        NICHT auf (eigene Messung: ein so eingebettetes Symbol landet in
        der Netzliste komplett ohne Pins, obwohl die eigene
        Selbstpruefung -- die nur die woertlich aus symlib gelesene
        Pin-Geometrie kennt, nicht KiCads Symbolaufloesung -- nichts
        auffaellig fand). Deshalb wird hier genau das nachgebildet, was
        KiCad selbst beim Speichern eines platzierten `extends`-Symbols
        in `lib_symbols` ablegt: ein vollstaendiges, in sich
        geschlossenes Symbol mit den eigenen Eigenschaften der
        Ableitung, aber der Grafik/den Pins der Basis.
        """
        basis_block = symlib.extract(dateiname, basisname)
        self.PINS[libid] = symlib.pins(basis_block)
        if multiunit:
            self.UNITPINS[libid] = _subunits(basis_block, basisname)

        kurz = libid.split(":")[1]
        einheiten = []
        for m in re.finditer(r'\(symbol "%s(_\d+_\d+)"' % re.escape(basisname), basis_block):
            sub, _ = _subblock(basis_block, m.start())
            einheiten.append(sub.replace('"%s%s"' % (basisname, m.group(1)),
                                          '"%s%s"' % (kurz, m.group(1)), 1))

        b = symlib.extract(dateiname, ableitungsname)
        b = re.sub(r'\n\t*\(extends "[^"]*"\)', '', b, count=1)
        b = b.replace('(symbol "%s"' % ableitungsname, '(symbol "%s"' % libid, 1)
        i = b.rindex("(embedded_fonts")
        b = b[:i] + "\n".join(einheiten) + "\n" + b[i:]
        self.LIBBLOCKS.append("\t\t" + b.replace("\n", "\n\t"))
        self._geladen.add(libid)
        return libid

    # ---------------------------------------------------------- Bauteile
    def bauteil(self, ref, libid, pos, wert, footprint, rot=0, einheit=1,
                roff=(0, 0), voff=(0, 0), dnp=False):
        """Platziert ein Bauteil. `einheit` waehlt bei Multi-Unit-Symbolen
        (siehe `lib(..., multiunit=True)`) die gezeichnete Teil-Einheit --
        fuer alle anderen Bauteile bleibt sie bei ihrem Vorgabewert 1.

        `dnp=True` markiert das Bauteil als "Do Not Populate" (Aufgabe 5:
        R10, die unbestueckte Stromgrenzen-Alternative zu R5). Bewusst ein
        SEPARATES Set (`self.DNP`), nicht ein zehntes Feld im COMPS-Tupel
        -- mehrere Stellen (gen.py selbst, UND die _netz_pins()-Helfer in
        tests/test_sockelplatine.py und tests/test_modulsockel.py)
        entpacken COMPS-Eintraege wortwoertlich als 9-Tupel; ein zehntes
        Feld haette diese bereits abgenommenen Tests zerbrochen, ohne dass
        diese Aufgabe sie anfassen sollte. Elektrisch bleibt ein
        DNP-Bauteil normal verdrahtet (nur die Bestueckung entfaellt) --
        das entspricht dem, was das Altprojekt fuer sein eigenes R10
        tatsaechlich in der .kicad_sch stehen hat (eigene Pruefung:
        `(dnp yes)` bei sonst unveraenderter Verdrahtung)."""
        if dnp:
            self.DNP.add(ref)
        self.COMPS.append((ref, libid, pos, rot, wert, footprint,
                            (pos[0] + roff[0], pos[1] + roff[1]),
                            (pos[0] + voff[0], pos[1] + voff[1]), einheit))
        return pos

    def _finde(self, ref, num=None):
        cands = [c for c in self.COMPS if c[0] == ref]
        if not cands:
            raise KeyError(ref)
        if len(cands) == 1 or num is None:
            return cands[0]
        # Multi-Unit-Bauteil: die Platzierung waehlen, deren Einheit
        # diese Pinnummer tatsaechlich traegt.
        einheiten = self.UNITPINS.get(cands[0][1])
        if einheiten:
            for c in cands:
                if num in einheiten.get(c[8], ()):
                    return c
        return cands[0]

    def pinpos(self, ref, num):
        c = self._finde(ref, num)
        p = self.PINS[c[1]][num]
        return xf(c[2], (p[0], p[1]), c[3])

    def netz(self, ref, num, richtung, name, laenge=5.08):
        """Stichleitung vom Pin in Richtung(en) `richtung`, am Ende Label
        oder Power-Symbol `name`. Zwei Aufrufe mit demselben `name`
        verbinden sich elektrisch, auch ohne gemeinsamen Draht --
        genau wie im Vorbild."""
        p = self.pinpos(ref, num)
        cur = p
        for d in richtung:
            dx, dy = DIRV[d]
            nxt = (round(cur[0] + dx * laenge, 4), round(cur[1] + dy * laenge, 4))
            self.WIRES.append((cur, nxt))
            cur = nxt
        letzte = richtung[-1]
        if name in PWR:
            libid, quellname = PWR[name]
            self.lib(libid, "power.kicad_sym", quellname)
            rot = 0 if letzte == "D" else (180 if letzte == "U" else (270 if letzte == "L" else 90))
            self.POWERS.append((libid, cur, rot, name))
        else:
            self.LABELS.append((cur[0], cur[1], LBLROT[letzte], name))
        return cur

    def draht(self, a, b):
        self.WIRES.append((a, b))

    def junction(self, xy):
        self.JUNCTIONS.append(xy)

    def nc(self, ref, num):
        self.NOCONN.append(self.pinpos(ref, num))

    def text(self, x, y, txt, size=1.4, bold=False):
        self.TEXTS.append((x, y, txt, size, bold))

    def _uuid(self):
        self._u += 1
        return str(uuid.uuid5(uuid.NAMESPACE_OID, "%s-%d" % (self.projekt, self._u)))

    # ------------------------------------------------------ Selbstpruefung
    def selbstpruefung(self):
        """Woertlich aus led_dimmer/gen_sch.py::selfcheck uebernommen (nur
        um Multi-Unit-Bauteile erweitert, s. Moduldoku oben): jeder
        Bauteil-Pin muss an einem Drahtende oder an einem no_connect
        haengen, jedes Label auf einem Drahtende sitzen, jedes
        Power-Symbol auf einem Drahtende sitzen, und keine Referenz
        doppelt vergeben sein."""
        ends = set()
        for w in self.WIRES:
            ends.add(w[0])
            ends.add(w[1])
        ncs = set(self.NOCONN)

        def auf_draht(xy):
            if xy in ends or xy in ncs:
                return True
            return any(
                min(w[0][0], w[1][0]) - 1e-6 <= xy[0] <= max(w[0][0], w[1][0]) + 1e-6 and
                min(w[0][1], w[1][1]) - 1e-6 <= xy[1] <= max(w[0][1], w[1][1]) + 1e-6 and
                (abs(w[0][0] - w[1][0]) < 1e-6 or abs(w[0][1] - w[1][1]) < 1e-6)
                for w in self.WIRES)

        bad = []
        for ref, libid, pos, rot, value, fp, _, _, einheit in self.COMPS:
            einheiten = self.UNITPINS.get(libid)
            nums = einheiten[einheit] if einheiten else self.PINS[libid].keys()
            for num in nums:
                p = self.PINS[libid][num]
                xy = xf(pos, (p[0], p[1]), rot)
                if not auf_draht(xy):
                    bad.append("%s Pin %s (%s) bei %s haengt in der Luft"
                               % (ref, num, p[3], xy))
        for x, y, rot, txt in self.LABELS:
            if (x, y) not in ends:
                bad.append("Label %s bei (%g,%g) sitzt auf keinem Drahtende" % (txt, x, y))
        for libid, pos, rot, value in self.POWERS:
            if pos not in ends:
                bad.append("Power-Symbol %s bei %s sitzt auf keinem Drahtende" % (value, pos))
        belegt = {}
        for ref, libid, pos, rot, value, fp, _, _, einheit in self.COMPS:
            belegt.setdefault(ref, []).append(einheit)
        for ref, einheiten in belegt.items():
            if len(einheiten) != len(set(einheiten)):
                bad.append("Referenz %s mehrfach fuer dieselbe Einheit vergeben" % ref)
        return bad

    # ------------------------------------------------------------- Ausgabe
    def _emit(self):
        o = []
        a = o.append
        a('(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")')
        a('\t(uuid "%s")\n\t(paper "%s")' % (self.sheet_uuid, self.papier))
        a('\t(title_block\n\t\t(title "%s")\n\t\t(date "%s")\n\t\t(rev "%s")\n'
          '\t\t(company "%s")\n\t)' % (self.titel, self.datum, self.rev, self.firma))
        a("\t(lib_symbols")
        for b in self.LIBBLOCKS:
            a(b.rstrip())
        a("\t)")

        for j in self.JUNCTIONS:
            a('\t(junction\n\t\t(at %g %g)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n'
              '\t\t(uuid "%s")\n\t)' % (j[0], j[1], self._uuid()))
        for p in self.NOCONN:
            a('\t(no_connect\n\t\t(at %g %g)\n\t\t(uuid "%s")\n\t)' % (p[0], p[1], self._uuid()))
        for w in self.WIRES:
            a('\t(wire\n\t\t(pts\n\t\t\t(xy %g %g) (xy %g %g)\n\t\t)\n'
              '\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "%s")\n\t)'
              % (w[0][0], w[0][1], w[1][0], w[1][1], self._uuid()))
        for x, y, rot, txt in self.LABELS:
            just = "right bottom" if rot in (180, 270) else "left bottom"
            a('\t(label "%s"\n\t\t(at %g %g %d)\n\t\t(fields_autoplaced yes)\n'
              '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
              '\t\t\t(justify %s)\n\t\t)\n\t\t(uuid "%s")\n\t)'
              % (txt, x, y, rot, just, self._uuid()))
        for x, y, txt, size, bold in self.TEXTS:
            a('\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %g %g 0)\n'
              '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %g %g)\n%s\t\t\t)\n'
              '\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "%s")\n\t)'
              % (txt, x, y, size, size, "\t\t\t\t(bold yes)\n" if bold else "", self._uuid()))

        def sym(ref, libid, pos, rot, value, fp, rpos, vpos, einheit):
            dnp_flag = "yes" if ref in self.DNP else "no"
            s = ['\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %g %g %d)\n\t\t(unit %d)'
                 % (libid, pos[0], pos[1], rot, einheit),
                 '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp %s)'
                 % dnp_flag,
                 '\t\t(uuid "%s")' % self._uuid()]
            hidden = ref.startswith("#")
            for pname, pval, ppos, hide in (
                    ("Reference", ref, rpos, hidden),
                    ("Value", value, vpos, hidden),
                    ("Footprint", fp, pos, True),
                    ("Datasheet", "", pos, True)):
                s.append('\t\t(property "%s" "%s"\n\t\t\t(at %g %g %d)\n\t\t\t(show_name no)\n'
                         '\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n'
                         '\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left)\n%s\t\t\t)\n\t\t)'
                         % (pname, pval, ppos[0], ppos[1], (360 - rot) % 360,
                            "\t\t\t\t(hide yes)\n" if hide else ""))
            s.append('\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n'
                     '\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit %d)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'
                     % (self.projekt, self.sheet_uuid, ref, einheit))
            return "\n".join(s)

        for c in self.COMPS:
            a(sym(*c))
        for libid, pos, rot, value in self.POWERS:
            self._u += 1
            ref = "#PWR%03d" % self._u
            a(sym(ref, libid, pos, rot, value, "", (pos[0], pos[1] - 2.54),
                  (pos[0], pos[1] + 2.54), 1))
        a('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)')
        return "\n".join(o) + "\n"

    def schreiben(self, pfad):
        """Prueft (`selbstpruefung`) und schreibt, wenn sauber. Bricht wie
        das Vorbild mit einer Fehlerliste ab, wenn ein Pin in der Luft
        haengt -- das ist die eigentliche Absicherung dieses Moduls."""
        bad = self.selbstpruefung()
        if bad:
            for b in bad:
                print("  *** " + b)
            raise SystemExit("%d Problem(e) in der Selbstpruefung von %s"
                              % (len(bad), pfad))
        d = os.path.dirname(os.path.abspath(pfad))
        if d:
            os.makedirs(d, exist_ok=True)
        with open(pfad, "w", encoding="utf-8") as f:
            f.write(self._emit())
        return pfad

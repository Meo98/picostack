"""Zieht Symbol-Bloecke aus den KiCad-Bibliotheken und liest ihre Pin-Geometrie.

Herkunft: led_dimmer/hardware/generator/symlib.py (Etappe 1b, Aufgabe 1).
LIBDIR war dort ein fest in den Quelltext eingetragener Nix-Store-Pfad
mitsamt Store-Hash -- der ueberlebt keinen nixos-rebuild, weil sich der
Hash mit jedem Paket-Update aendert. tools/pcb/kicadlibs.py loest
dasselbe Problem fuer Footprints schon richtig, indem es die
Verzeichnisse aus dem kicad-cli-Wrapper ausliest statt sie zu raten.
_libdir() macht dasselbe fuer Symbole.
"""
import os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "pcb"))
import kicadlibs


def _libdir():
    """Symbolverzeichnis aus der installierten KiCad-Version ableiten.

    Ein fest eingetragener Store-Pfad ueberlebt kein nixos-rebuild. Die
    Variable heisst KICAD<major>_SYMBOL_DIR und steht im kicad-cli-Wrapper.
    """
    d = kicadlibs.kicad_dirs()
    for k, v in d.items():
        if k.endswith("_SYMBOL_DIR"):
            return v.rstrip("/") + "/"
    raise SystemExit("kein KICAD*_SYMBOL_DIR im kicad-cli-Wrapper gefunden")


LIBDIR = _libdir()


def extract(libfile, name):
    """Liefert den kompletten (symbol "name" ...)-Block per Klammerzaehlung.

    `libfile` ist normalerweise ein Dateiname relativ zu LIBDIR (der
    System-Bibliothek). Aufgabe 5 (Motormodul) braucht zusaetzlich ein
    projekteigenes Symbol (DRV8876PWPR, ein Snapeda-Export ohne
    Gegenstueck in der System-Bibliothek) -- dafuer akzeptiert diese
    Funktion auch einen absoluten Pfad und liest dann direkt von dort,
    ohne LIBDIR voranzustellen."""
    pfad = libfile if os.path.isabs(libfile) else LIBDIR + libfile
    txt = open(pfad, encoding="utf-8").read()
    key = '(symbol "%s"' % name
    i = txt.find(key)
    if i < 0:
        raise KeyError("%s nicht in %s" % (name, libfile))
    d, j = 0, i
    while True:
        c = txt[j]
        if c == '"':                       # Strings ueberspringen
            j += 1
            while txt[j] != '"' or txt[j - 1] == '\\':
                j += 1
        elif c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return txt[i:j + 1]
        j += 1


def pins(block):
    """{Pinnummer: (x, y, rotation, name)} aus einem Symbolblock.

    Die Rotation steht im Rasterformat normalerweise als blanke Ganzzahl
    ("180"), im DRV8876PWPR-Symbol (Aufgabe 5, ein Snapeda-Export, kein
    KiCad-eigenes Symbol) aber als Fliesskommazahl ("180.0") -- deshalb
    `[-\\d.]+` statt `\\d+` und `int(float(...))` statt `int(...)`. Eigene
    Pruefung: ohne diese Aenderung liess die Regex jeden Pin mit
    "180.0" aus (7 von 16 Pins des DRV8876PWPR fehlten im Ergebnis)."""
    out = {}
    for m in re.finditer(
            r'\(pin\s+\S+\s+\S+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)'
            r'.*?\(name "([^"]*)".*?\(number "([^"]*)"',
            block, re.S):
        x, y, rot, nm, num = m.groups()
        out[num] = (float(x), float(y), int(float(rot)), nm)
    return out

"""Loest KiCad-Footprint-Bibliotheken zu Dateipfaden auf.

pcbnew.FootprintLoad() will einen Pfad, die Netzliste nennt aber nur
Spitznamen ("Capacitor_SMD:C_1206_3216Metric"). Die Zuordnung steht in
zwei fp-lib-tables: der globalen unter ~/.config/kicad und der
projekteigenen. Unter NixOS ist die globale nur ein Verweis auf eine
weitere Tabelle im Template-Verzeichnis -- die wird mit aufgeloest.

Die Verzeichnisse kommen aus dem kicad-cli-Wrapper statt aus einem fest
eingetragenen Store-Pfad, damit das nach einem nixos-rebuild weiter
stimmt.
"""
import os, re, shutil, subprocess

_VAR = re.compile(r'\$\{([A-Za-z0-9_]+)\}|\$\(([A-Za-z0-9_]+)\)')


def kicad_dirs():
    """KICAD*_DIR-Vorgaben aus dem kicad-cli-Wrapper lesen."""
    exe = shutil.which("kicad-cli")
    if not exe:
        return {}
    exe = os.path.realpath(exe)
    try:
        blob = open(exe, "rb").read().decode("utf-8", "replace")
    except OSError:
        return {}
    out = {}
    for m in re.finditer(r"(KICAD\d*_[A-Z_]+_DIR)=\$\{\1-'([^']+)'\}", blob):
        out[m.group(1)] = m.group(2)
    return out


def kicad_version():
    return subprocess.run(["kicad-cli", "version"], capture_output=True,
                          text=True).stdout.strip()


def _expand(uri, subst):
    def rep(m):
        k = m.group(1) or m.group(2)
        return subst.get(k, m.group(0))
    return _VAR.sub(rep, uri)


def _read_table(path, subst, seen):
    """fp-lib-table lesen; Eintraege vom Typ 'Table' rekursiv aufloesen."""
    path = os.path.realpath(path)
    if path in seen or not os.path.exists(path):
        return {}
    seen.add(path)
    s = open(path, encoding="utf-8").read()
    libs = {}
    for m in re.finditer(r'\(lib\s+\(name\s+"([^"]+)"\)\s*'
                         r'\(type\s+"([^"]+)"\)\s*\(uri\s+"([^"]+)"\)', s):
        name, typ, uri = m.group(1), m.group(2), _expand(m.group(3), subst)
        if typ.lower() == "table":
            libs.update(_read_table(uri, subst, seen))
        else:
            libs[name] = uri
    return libs


def footprint_libs(project_dir):
    """Spitzname -> Verzeichnispfad, Projekttabelle schlaegt die globale."""
    subst = dict(kicad_dirs())
    subst["KIPRJMOD"] = os.path.realpath(project_dir)
    ver = kicad_version()
    major = ver.split(".")[0] if ver else "10"
    seen = set()
    libs = _read_table(os.path.expanduser(
        "~/.config/kicad/%s.0/fp-lib-table" % major), subst, seen)
    libs.update(_read_table(os.path.join(project_dir, "fp-lib-table"),
                            subst, set()))
    return libs


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    libs = footprint_libs(d)
    print("KiCad %s, %d Bibliotheken" % (kicad_version(), len(libs)))
    for k in sorted(libs)[:5]:
        print("  %-28s %s" % (k, libs[k]))

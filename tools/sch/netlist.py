"""Liest die von kicad-cli exportierte Netzliste."""
import re, os
NET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.net")


def _parse(t):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', t)
    def rd(i):
        out = []
        while i < len(tok):
            k = tok[i]
            if k == "(":
                sub, i = rd(i + 1); out.append(sub)
            elif k == ")":
                return out, i + 1
            else:
                out.append(k[1:-1] if k.startswith('"') else k); i += 1
        return out, i
    return rd(1)[0]


def load(path=NET):
    root = _parse(open(path).read())
    kid = lambda n, t: [c for c in n if isinstance(c, list) and c and c[0] == t]
    val = lambda n, t: ([c[1] for c in n if isinstance(c, list) and c[0] == t] or [""])[0]

    comps = {}                                  # ref -> (footprint, value)
    for c in kid(kid(root, "components")[0], "comp"):
        comps[val(c, "ref")] = (val(c, "footprint"), val(c, "value"))

    padnet = {}                                 # ref -> {pad: netname}
    for n in kid(kid(root, "nets")[0], "net"):
        name = val(n, "name")
        for nd in kid(n, "node"):
            d = {c[0]: c[1] for c in nd if isinstance(c, list)}
            padnet.setdefault(d["ref"], {})[d["pin"]] = name
    return comps, padnet


if __name__ == "__main__":
    c, p = load()
    print("%d Bauteile, %d mit Netzen" % (len(c), len(p)))
    miss = [r for r, (f, v) in c.items() if not f]
    print("ohne Footprint:", miss or "keine")
    for r in sorted(c)[:6]:
        print("  %-5s %-55s %s" % (r, c[r][0], c[r][1]))

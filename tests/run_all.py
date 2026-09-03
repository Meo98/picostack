"""Runs every test suite in this directory, in plain Python.

No pytest, no fixtures: each tests/test_*.py is an executable script that
prints what it checked and exits non-zero on failure. This runner exists
so that `python3 tests/run_all.py` is the one command a contributor (or a
CI job) needs.
"""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fehl = []
for pfad in sorted(glob.glob(os.path.join(HERE, "test_*.py"))):
    name = os.path.basename(pfad)
    lauf = subprocess.run([sys.executable, pfad], capture_output=True,
                          text=True)
    status = "ok " if lauf.returncode == 0 else "ROT"
    letzte = (lauf.stdout.strip().splitlines() or ["(keine Ausgabe)"])[-1]
    print("%s %-28s %s" % (status, name, letzte[:80]))
    if lauf.returncode != 0:
        fehl.append(name)
        print(lauf.stdout[-2000:])
        print(lauf.stderr[-1000:])

if fehl:
    raise SystemExit("ROT: " + ", ".join(fehl))
print("alle %d Suiten gruen" % len(glob.glob(os.path.join(HERE, "test_*.py"))))

"""Dimmer1: duenner Traeger der gemeinsamen Beschreibung.

Alle Inhalte kommen aus spec_dimmer_basis.beschreibung(1) --
build.py/geometry.py erwarten ein MODUL mit Attributen, deshalb der
globals()-Hub statt einer Klasse.
"""
from spec_dimmer_basis import beschreibung

globals().update(beschreibung(1))

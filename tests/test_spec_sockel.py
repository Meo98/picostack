"""spec_sockel (v1): RETIRED fuer v2, nicht ersatzlos geloescht.

Stand vor dieser Aenderung: `import spec_sockel` brach beim Laden mit
`KeyError: 'stapel'` ab -- `spec_sockel.py` liest
`stack_spec.STECKER_POS["stapel"]`, und dieser Schluessel existiert im
v2-Vertrag nicht mehr (ersetzt durch "stapel_links"/"stapel_rechts", zwei
1x20-Buchsenreihen in Pico-Geometrie statt eines 2x20-Blocks).

Grund, warum das NICHT nachgezogen wird: die Sockelplatine ist seit
`stack_spec.VERTRAG_VERSION = 2` v1-only und eingefroren (Release v0.1.0
bleibt ihr Archiv, s. tools/sch/sockelplatine.py- und
tools/pcb/spec_sockel.py-Docstrings sowie
hardware/fertigung/sockel/README.md). `spec_sockel.py` auf den neuen
Vertrag umzustellen hiesse, eine Platine zu aendern, die per Beschluss
genau NICHT weiterentwickelt wird.

Diese Suite laeuft deshalb ab jetzt absichtlich gruen durch, ohne
`spec_sockel` zu importieren oder gegen irgendeinen Vertrag zu pruefen --
sie ist ein Platzhalter, kein Nachweis. Der vollstaendige alte
Testinhalt (Vertragsteile J2/J3/J4/U1 nachgerechnet, Naehvia-Freiheit,
Vollstaendigkeit der Bauteilbeschreibung) bleibt in der Git-Historie
dieser Datei einsehbar, falls die Sockelplatine je wieder aktiv gepflegt
werden sollte.
"""
print("uebersprungen: spec_sockel ist v1-only/eingefroren (s. Docstring)")

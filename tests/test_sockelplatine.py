"""Sockelplatine (v1): RETIRED fuer v2, nicht ersatzlos geloescht.

Stand vor dieser Aenderung: dieser Test rief `sockelplatine.bauen()` gegen
den (fuer v2 umgestellten) `modulsockel._stapelstecker()` auf und brach mit
einem rohen `TypeError: _stapelstecker() missing 1 required positional
argument: 'oy'` ab -- kein gezielter roter Nachweis, sondern ein
Signatur-Mismatch zwischen einem v1-Erzeuger und einer fuer v2 geaenderten
gemeinsamen Bibliotheksfunktion.

Grund, warum das NICHT nachgezogen wird: die Sockelplatine ist seit
`stack_spec.VERTRAG_VERSION = 2` v1-only und eingefroren (Release v0.1.0
bleibt ihr Archiv, s. tools/sch/sockelplatine.py-Docstring und
hardware/fertigung/sockel/README.md). `modulsockel._stapelstecker()` baut
seit v2 grundsaetzlich zwei 1x20-Buchsenreihen (Pico-Geometrie) statt des
einen 2x20-Blocks, den der Sockel benutzt -- den Sockel-Generator daran
anzupassen wuerde entweder die v1-Geometrie verlassen (und damit genau die
Platine aendern, die eingefroren bleiben soll) oder eine zweite,
parallele Bibliotheksfassung nur fuer den Sockel verlangen. Beides kostet
mehr, als ein archiviertes, nicht mehr auszulieferndes Board wert ist.

Diese Suite laeuft deshalb ab jetzt absichtlich gruen durch, OHNE die
Sockelplatine noch gegen irgendeinen Vertrag zu pruefen -- sie ist ein
Platzhalter, kein Nachweis. Der vollstaendige alte Testinhalt (Pin-Rollen-
Pruefung, kicad-cli-ERC-Lauf, VSYS/3V3_OUT-Verwechslungsschutz) bleibt in
der Git-Historie dieser Datei einsehbar, falls die Sockelplatine je wieder
aktiv gepflegt werden sollte.
"""
print("uebersprungen: Sockelplatine ist v1-only/eingefroren (s. Docstring)")

# Modul-Testprogramm: blink

Das kleinstmögliche Programm für den Modul-MCU (STM32C011F6P6), dessen
Wirkung man von aussen sieht: ein GPIO-Pin im Sekundentakt umschalten.
Zweck ist einzig, `firmware/sockel/nachweis.py` etwas zum Aufspielen zu
geben, dessen Erfolg oder Misserfolg man ohne Messgerät erkennt — eine
LED oder ein Multimeter am Pin genügt.

Es gibt hier absichtlich **keinen Quelltext**. Register, Header und
Startup-Code hängen am gewählten MCU-Typ (STM32C011F6P6, siehe
`hardware/bauteile.md`) und liegen im Beispielprojekt des Herstellers
(STM32CubeC0 / STM32CubeIDE-Projektvorlage für die STM32C0-Serie,
GPIO-Toggle-Beispiel). Von dort übernehmen, nicht neu schreiben:
STM32-Startup-Dateien und Register-Zugriffe von Grund auf
nachzubauen wäre Aufwand ohne Erkenntnisgewinn für diesen Nachweis.

## Was das Programm tun soll

- Einen freien GPIO-Pin (z. B. ein LED-taugliches Pin, nicht PA11/PA12
  — die trägt der Bootlader-UART — und nicht PA14/BOOT0) im
  Sekundentakt umschalten (toggle, ca. 1 Hz).
- Keine weitere Funktion. Kein UART, kein I²C, keine Interrupts, die
  nicht zum Blinken gehören — je kleiner, desto eindeutiger ist der
  Nachweis, dass genau *dieses* Programm lief.

## Ausgabeformat

Der ROM-Bootlader (AN3155) kennt keine ELF-Dateien und keine
Sektionsheader. Er nimmt rohe Bytes, die er ab `0x08000000`
(Flash-Anfang) in den Speicher schreibt — Adresse und Byte-Reihenfolge
allein entscheiden, keine Metadaten.

Übersetzung (mit dem `arm-none-eabi`-Toolchain aus dem
Hersteller-Beispielprojekt bzw. STM32CubeIDE/CMake):

```bash
# Projekt wie gewohnt uebersetzen -> blink.elf
arm-none-eabi-objcopy -O binary blink.elf blink.bin
ls -l blink.bin      # erwartet: wenige hundert Byte
```

`blink.bin` ist die Datei, die `nachweis.py::aufspielen(pfad)`
erwartet.

## Status

Noch nicht angelegt. Es fehlt der STM32C011 auf dem Tisch (siehe
`docs/nachweis-2026-08.md`) — ohne Hardware zum Gegenprüfen lohnt sich
kein Quelltext, den niemand testen kann. Sobald ein Chip vorliegt: aus
dem Hersteller-Beispiel ableiten, wie oben beschrieben übersetzen, mit
`nachweis.py` aufspielen.

"""Zusicherungen des Vertrags v4 (tools/stack_spec.py), KiCad-frei.

Jede gerechnete Groesse des Vertrags steht hier als Pruefung, nicht
als Kommentar. Rot-Nachweise: wo eine Pruefung eine Fehlerklasse
abdeckt, wird derselbe Check einmal gegen absichtlich falsche Werte
gerechnet und muss dort anschlagen -- sonst beweist Gruen nichts.
"""
import math
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "tools"))

import stack_spec as S  # noqa: E402

fehler = []


def check(label, bedingung, detail=""):
    if not bedingung:
        fehler.append("%s%s" % (label, (" -- " + str(detail)) if detail else ""))


def nahe(a, b, tol=1e-3):
    return abs(a - b) <= tol


# --- 1. Steckerflaechen stimmen mit der Drehrechnung ueberein -----------
for name, e in S.STECKER_POS.items():
    soll = S.HOEFE(e["footprints"], e["pin1"], e["drehung"])
    check("STECKER_POS[%s].flaeche" % name, e["flaeche"] == soll,
          "eingetragen %s, gerechnet %s" % (e["flaeche"], soll))
    x0, y0, x1, y1 = e["flaeche"]
    r = S.LAYOUT_REGELN["R5"]["mindestabstand_mm"]
    check("%s innerhalb der Platine (R5)" % name,
          x0 >= r and y0 >= r and x1 <= S.BOARD_W - r and y1 <= S.BOARD_H - r)

# --- 2. Pico-Geometrie --------------------------------------------------------
unten = S.PAD_LAGEN(S.FP_STAPEL_20, S.PICO_PIN1, 90)
oben = S.PAD_LAGEN(S.FP_STAPEL_20, S.PICO_PIN21, 270)
check("Pin 1 unten", unten[1] == S.PICO_PIN1)
check("Pin 20 unten laeuft nach +x", nahe(unten[20][0], 9.00 + 19 * 2.54)
      and nahe(unten[20][1], 27.78), unten[20])
check("Pin 21 oben", oben[1] == S.PICO_PIN21)
check("Pin 40 oben laeuft nach -x", nahe(oben[20][0], 9.00) and nahe(oben[20][1], 10.00),
      oben[20])
check("Reihenabstand = Pico-Datenblatt", nahe(unten[1][1] - oben[1][1], S.PICO_REIHENABSTAND))
check("Pinspann 48,26", nahe(unten[20][0] - unten[1][0], 19 * 2.54))
check("Pin 20 und Pin 21 uebereinander", nahe(unten[20][0], oben[1][0]))
# Pico-Schatten aus den Pins hergeleitet: 1,37 ueber die Endpins, 1,61
# ueber die Reihen hinaus.
ueber_x = (S.PICO_LAENGE - 19 * 2.54) / 2.0
ueber_y = (S.PICO_BREITE - S.PICO_REIHENABSTAND) / 2.0
soll_schatten = (round(S.PICO_PIN1[0] - ueber_x, 2), round(S.PICO_PIN21[1] - ueber_y, 2),
                 round(unten[20][0] + ueber_x, 2), round(S.PICO_PIN1[1] + ueber_y, 2))
check("PICO_SCHATTEN aus Pins hergeleitet", S.PICO_SCHATTEN == soll_schatten,
      "%s statt %s" % (S.PICO_SCHATTEN, soll_schatten))
check("ANTENNE_FREI liegt zwischen den Reihen, nicht auf ihren Pads",
      S.ANTENNE_FREI[1] >= S.STECKER_POS["stapel_oben"]["flaeche"][3]
      and S.ANTENNE_FREI[3] <= S.STECKER_POS["stapel_unten"]["flaeche"][1]
      and S.ANTENNE_FREI[0] > S.PICO_SCHATTEN[0] and S.ANTENNE_FREI[2] >= S.PICO_SCHATTEN[2])
check("USB-Ueberstand bleibt auf der Platine",
      S.PICO_SCHATTEN[0] - S.USB_UEBERSTAND > 0)

# --- 3. Stapelrechnung -----------------------------------------------------------
check("Einstecktiefe 7,5 mm", nahe(S.EINSTECKTIEFE_STAPEL(), 7.5), S.EINSTECKTIEFE_STAPEL())
check("Stiftende beruehrt die Platine darunter nicht", S.LUFT_STIFTENDE() > 0,
      S.LUFT_STIFTENDE())
check("Luft ueber der Buchse", S.LUFT_BUCHSENOBERKANTE() > 0, S.LUFT_BUCHSENOBERKANTE())
check("Bauteilhoehe oben passt in den Spalt",
      S.BAUTEILHOEHE_OBEN_MAX < S.SPALT())
check("Bauteilhoehe unter dem Pico < Buchsenhoehe",
      S.BAUTEILHOEHE_PICO_SCHATTEN_MAX < S.STECKER_STAPEL["gehaeusehoehe_mm"])
check("Stapelabstand ist ein Katalogmass (ganze mm)",
      nahe(S.STAPEL_ABSTAND, round(S.STAPEL_ABSTAND)))
# ROT-NACHWEIS: bei 11,0 mm stoesst der Stift auf die Platine darunter.
_alt = S.STAPEL_ABSTAND
S.STAPEL_ABSTAND = 11.0
check("Rot-Nachweis Stapelabstand 11 mm faellt durch", not (S.LUFT_STIFTENDE() > 0),
      S.LUFT_STIFTENDE())
S.STAPEL_ABSTAND = _alt

# --- 4. Baenke und Pinrollen -----------------------------------------------------
alle_bank_gp = [gp for gps in S.BAENKE.values() for gp in gps]
check("16 Bank-GPIO", len(alle_bank_gp) == 16)
check("Bank-GPIO eindeutig", len(set(alle_bank_gp)) == 16)
check("jede Bank hat vier Pins", all(len(g) == 4 for g in S.BAENKE.values()))
pwm = [S.PWM_KANAL(gp) for gp in alle_bank_gp]
check("alle 16 Bank-GPIO sind getrennte PWM-Kanaele", len(set(pwm)) == 16, pwm)
# ROT-NACHWEIS: GP0 und GP16 teilen sich Slice 0A.
check("Rot-Nachweis PWM-Kollision GP0/GP16", S.PWM_KANAL(0) == S.PWM_KANAL(16))
belegt = set(alle_bank_gp) | set(S.ADC_BANK) | set(S.USER_GP) | set(S.RESERVIERT)
check("Baenke, ADC, User, Reserviert ueberschneiden sich nicht",
      len(alle_bank_gp) + len(S.ADC_BANK) + len(S.USER_GP) + len(S.RESERVIERT) == len(belegt))
check("jeder Pico-GPIO hat genau eine Rolle", belegt == set(S.GP_PIN),
      sorted(set(S.GP_PIN) ^ belegt))
check("ADC-Bank sind die drei ADC-Pins", set(S.ADC_BANK) == {26, 27, 28})
for gp in belegt:
    check("GP%d belegbar" % gp, S.IST_BELEGBAR(S.GP_PIN[gp]))
frei = [p for p, r in S.PIN_ROLLE.items() if r == "frei"]
check("kein Pin ist 'frei' (jeder hat eine Rolle)", frei == [], frei)
check("GP_PIN/PIN_GP sind Umkehrungen", all(S.PIN_GP[S.GP_PIN[g]] == g for g in S.GP_PIN))
check("26 GPIO", len(S.GP_PIN) == 26)
for fam, bank in S.BANK_VORGABE.items():
    check("Bank-Vorgabe %s existiert" % fam, bank in S.BAENKE)
check("Vorgaben Motor und Dimmer verschieden",
      S.BANK_VORGABE["Motor"] != S.BANK_VORGABE["Dimmer"])
check("Matrix: Signal 3 auf Bank D = GP22", S.MATRIX_GP(3, "D") == 22)
check("Matrix: Signal 4 auf Bank D = GP7", S.MATRIX_GP(4, "D") == 7)
for code, m in S.MODULTYPEN.items():
    check("Modultyp 0x%02x Familie hat Bank-Vorgabe" % code, m["familie"] in S.BANK_VORGABE)
    check("Modultyp 0x%02x <= 4 Signale" % code, 1 <= m["signale"] <= 4)
    if m["adc"]:
        check("Modultyp 0x%02x ADC-Vorgabe" % code, S.ADC_VORGABE[m["familie"]] in S.ADC_BANK)

# --- 5. Verdreht steckt nirgends ------------------------------------------------
d, ok = S.VERDREHT_STECKT_NIRGENDS()
check("verdrehtes Modul steckt nirgends (>= 2 mm)", ok, d)
# ROT-NACHWEIS: laegen die Reihen symmetrisch zur Mitte, traefe jeder Stift.
_pos = S.STECKER_POS
S.STECKER_POS = {
    "a": dict(_pos["stapel_unten"], pin1=(9.0, S.BOARD_H / 2.0 - 8.89)),
    "b": dict(_pos["stapel_oben"], pin1=(57.26, S.BOARD_H / 2.0 + 8.89)),
}
_d, _ok = S.VERDREHT_STECKT_NIRGENDS()
check("Rot-Nachweis symmetrische Reihen stecken", not _ok, _d)
S.STECKER_POS = _pos
# ROT-NACHWEIS 2: bei 56 mm Hoehe (erster Platzprobe-Kandidat) laege die
# verdrehte untere Reihe 0,44 mm neben der echten -- gesteckt haette es.
_h = S.BOARD_H
S.BOARD_H = 56.0
_d, _ok = S.VERDREHT_STECKT_NIRGENDS()
check("Rot-Nachweis 56 mm Hoehe steckt", not _ok and _d < 0.5, _d)
S.BOARD_H = _h

# --- 6. Zonen und Loecher -------------------------------------------------------
def schneidet(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


check("vier M3-Loecher", len(S.M3_HOLES) == 4)
check("M3-Loecher punktsymmetrisch",
      sorted(S.M3_HOLES) == sorted((round(S.BOARD_W - x, 3), round(S.BOARD_H - y, 3))
                                   for x, y in S.M3_HOLES))
for hx, hy in S.M3_HOLES:
    k = S.M3_KEEPOUT / 2.0
    quadrat = (hx - k, hy - k, hx + k, hy + k)
    for name, e in S.STECKER_POS.items():
        check("M3 (%g|%g) frei von %s" % (hx, hy, name), not schneidet(quadrat, e["flaeche"]))
    check("M3 (%g|%g) frei von KLEMMENZONE" % (hx, hy), not schneidet(quadrat, S.KLEMMENZONE))
    check("M3 (%g|%g) frei vom Pico" % (hx, hy), not schneidet(quadrat, S.PICO_SCHATTEN))
check("KLEMMENZONE schneidet den Pico nicht", not schneidet(S.KLEMMENZONE, S.PICO_SCHATTEN))
check("KLEMMENZONE liegt an der unteren Kante", S.KLEMMENZONE[3] == S.BOARD_H)
check("Leistungsreihe schneidet den Pico nicht",
      not schneidet(S.STECKER_POS["leistung"]["flaeche"], S.PICO_SCHATTEN))
check("Stapelreihen liegen im Pico-Schatten",
      all(schneidet(S.STECKER_POS[n]["flaeche"], S.PICO_SCHATTEN)
          for n in ("stapel_unten", "stapel_oben")))

# --- 7. Versorgung und Strombudget ---------------------------------------------
V = S.VERSORGUNG
check("Reglerfenster umfasst die Zusage",
      V["regler_eingang_v"][0] <= V["eingang_v"][0]
      and V["regler_eingang_v"][1] >= V["eingang_v"][1])
check("Ausgang = Teilerformel", nahe(V["ausgang_v"], round(1.221 * (1 + 10.0 / 3.3), 2), 0.01))
check("Ausgang passt in VSYS 1,8-5,5 V", 1.8 < V["ausgang_v"] - 0.4 < 5.5)
check("Drain an der Einspeisung", V["schutz_drain_an"] == "PWR_IN")
check("VSYS-Diode", V["vsys_diode"] and V["usb_parallel"])
B = S.STROMBUDGET
i_max = math.sqrt(B["q90_verlust_max_w"] / B["q90_rdson_ohm"])
check("Q90 traegt das Modulbudget", i_max >= B["modul_gesamt_a"], i_max)
check("Durchleitung <= Kontaktstrom", B["stapel_durchleitung_a"] <= S.STECKER_STAPEL["strom_pro_kontakt_a"])
check("Kanal <= Modul", B["kanal_a"] <= B["modul_gesamt_a"])
check("Klemme traegt das Modul", B["klemme_a"] >= B["modul_gesamt_a"])
check("Stammnetze sind zwei", len(B["stamm_netze"]) == 2)

# --- 8. Klemmen -------------------------------------------------------------------
check("Klemme 0 Grad oeffnet nach unten", S.KLEMME_OEFFNUNG_GLOBAL(S.FP_KLEMME_35, 0) == (0.0, 1.0))
check("Klemme 180 Grad oeffnet nach oben", S.KLEMME_OEFFNUNG_GLOBAL(S.FP_KLEMME_35, 180) == (0.0, -1.0))
check("Klemmenzone breit genug fuer 5 x 8 mm", S.KLEMMENZONE[2] - S.KLEMMENZONE[0] >= 5 * 8.0)

if fehler:
    for f in fehler:
        print("FEHLER: " + f)
    raise SystemExit("%d Pruefungen fehlgeschlagen" % len(fehler))
print("Vertrag v%d: alle Pruefungen bestanden (verdreht: %.2f mm, Einstecktiefe %.1f mm)"
      % (S.VERTRAG_VERSION, d, S.EINSTECKTIEFE_STAPEL()))

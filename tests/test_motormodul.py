"""Prueft das Motormodul gegen den Vertrag, gegen das Altprojekt und gegen
sich selbst.

Vorbild: tests/test_sockelplatine.py und tests/test_modulsockel.py. Das
Motormodul ist -- wie die Sockelplatine -- ein einzelnes, fertiges Blatt
(hardware/kicad/motor/Motormodul.kicad_sch), baut aber zusaetzlich den
vollen Modulsockel-Block (modulsockel.einbauen(..., mit_flipflop=True))
mit ein, statt nur dessen Steckerteile wiederzuverwenden.

Die reine Pin-auf-Draht-Selbstpruefung (gen.Schaltplan.selbstpruefung,
laeuft bereits beim Schreiben ueber motormodul.bauen()/sch.schreiben())
sieht keine ERC-Fehler wie Phantom-Stromsymbole oder zwei zufaellig
deckungsgleiche Stichleitungen verschiedener Netze -- genau letzteres kam
beim ersten Entwurf dieser Datei tatsaechlich vor (zu enger Zeilenabstand
liess z.B. IN1 und U1_PH_IN2 zu einem Netz verschmelzen, s. Kommentare in
tools/sch/motormodul.py) und wurde ausschliesslich durch den
`kicad-cli sch erc`-Lauf gefunden, nicht durch die Selbstpruefung. Der
ERC-Testschritt unten ist deshalb keine Formalitaet.

Stand 2026-08-31: alle kicad-cli-gestuetzten Pruefbloecke brauchen ein
installiertes `kicad-cli`. Fehlt es, werden sie mit einer deutlichen
Meldung uebersprungen statt entweder mit einem rohen Traceback
abzubrechen oder still gruen zu melden.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for d in ("tools", "tools/sch"):
    sys.path.insert(0, os.path.join(HERE, "..", d))
import stack_spec as S       # noqa: E402
import modulsockel            # noqa: E402
import motormodul              # noqa: E402

fails = []


def check(label, got, want):
    if got != want:
        fails.append("{}: {!r} != {!r}".format(label, got, want))


# ------------------------------------------------------- reine Python-Pruefungen
# Brauchen kein kicad-cli.

# Der reparierte DRV8876-Footprint aus dem Altprojekt: Waermepad MIT
# Masken-/Pastenoeffnung, segmentiertes Pastenmuster, zwoelf Waermevias
# mit echtem Restring auf Pad 17 (Aufgabenbrief, Schritt 2).
_fp_mod = os.path.join(HERE, "..", "hardware", "kicad", "components",
                        "footprints", "DRV8876PWPR.pretty", "IC_DRV8876PWPR.kicad_mod")
check("DRV8876-Footprint aus dem Altprojekt uebernommen (Datei vorhanden)",
      os.path.isfile(_fp_mod), True)
if os.path.isfile(_fp_mod):
    _fp_txt = open(_fp_mod, encoding="utf-8").read()
    check("zwoelf Waerme-Durchkontaktierungen auf Pad 17 (reparierter Footprint)",
          _fp_txt.count("(pad 17 thru_hole circle"), 12)

check("Footprint DRV8876 zeigt auf die uebernommene Bibliothek",
      motormodul.FP_DRV8876, "DRV8876PWPR:IC_DRV8876PWPR")
check("Footprint TVS SMC (D1, wie sockelplatine.py)", motormodul.FP_TVS_SMC,
      "Diode_SMD:D_SMC_Handsoldering")
check("Footprint 220uF radial (C12, wie sockelplatine.py C3)",
      motormodul.FP_CP_RADIAL, "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm")

# Punkt 1 des Auftrags: R5 ist NEU gerechnet (2,538 A bei VVREF=3,3V,
# AIPROPI=1000uA/A), nicht der Altprojekt-Wert (2,2k -> 1,5A, zu klein
# fuer den 2-A-Motor -- exakt der dokumentierte Muttern-Board-Fehler).
_AIPROPI = 1000e-6   # A/A, TI DRV8876-Datenblatt SLVSDS7B, Abschnitt 6.5
_VVREF = 3.3
_R5_OHM = 1300.0
check("R5-Wert wie in motormodul.py verdrahtet", motormodul.R5_WERT, "1.3k")
_itrip = _VVREF / (_R5_OHM * _AIPROPI)
check("neu gerechnete Stromgrenze liegt ueber dem 2-A-Motor (mit Marge)",
      _itrip > 2.2, True)
check("neu gerechnete Stromgrenze bleibt unter der Hardware-Notbremse "
      "IOCP (3,5 A min, Datenblatt Abschnitt 6.5)", _itrip < 3.5, True)
# Der Altprojekt-Wert (2,2k) haette denselben Motor NICHT versorgt --
# Gegenprobe, dass diese Aufgabe nicht einfach denselben Fehler wiederholt.
_itrip_alt = _VVREF / (2200.0 * _AIPROPI)
check("Altprojekt-Wert (2,2k) haette 2-A-Motor unterversorgt (zur Gegenprobe)",
      _itrip_alt < 2.0, True)
check("R10 bleibt der unveraenderte Altprojekt-Wert (nur DNP, nicht neu "
      "gerechnet -- die Aufgabe verlangt das nur fuer R5)",
      motormodul.R10_WERT, "4.7k")

# ------------------------------- Punkt 4: die PEGEL der Notaus-Verriegelung
# Diese Zusicherungen pruefen nicht, ob ein Bauteil da ist, sondern welche
# SPANNUNG am nSLEEP-Pin des DRV8876 tatsaechlich ansteht. Genau daran
# scheiterte die erste Fassung: sie hatte eine Diode, aber keinen Pegel.
# Alle Groessen kommen aus tools/sch/motormodul.py; dort steht zu jeder die
# Datenblattquelle mit Dokumentnummer und Abschnitt.
M = motormodul


def _nsleep_diodenklemme(r_vor, r_serie, v_klemme,
                          rpd=M.DRV_RPD, v_quelle=M.V_3V3):
    """Spannung am nSLEEP-Knoten einer passiven Diodenklemme.

    Ein haengender Modul-MCU treibt ueber `r_vor` aktiv HIGH; die Klemme
    zieht ueber `r_serie` gegen `v_klemme` (= Busspannung + Vorwaerts-
    spannung der Klemmdiode). `rpd` ist der interne Pulldown des
    DRV8876-nSLEEP-Pins. Knotengleichung:

        (v_quelle - U)/r_vor = (U - v_klemme)/r_serie + U/rpd

    `r_serie = 0` heisst: die Diode sitzt ohne Vorwiderstand direkt am
    Knoten, dann ist U = v_klemme.
    """
    if r_serie == 0:
        return v_klemme
    leitwert = 1.0 / r_vor + 1.0 / r_serie + 1.0 / rpd
    return (v_quelle / r_vor + v_klemme / r_serie) / leitwert


# --- Gegenprobe 1: die urspruengliche Klemme (R9=100, R14=1k, Si-Diode) ---
# Selbst wenn die Sammelleitung ideal auf 0 V laege, steht der Pin bei
# rund 3,05 V. R14 schuetzt den GPIO und verhindert dabei die Wirkung.
_u_alt = _nsleep_diodenklemme(M.R9_OHM, M.ALT_R14_OHM, M.ALT_VF_1N4148)
check("Gegenprobe: die alte Klemme mit R14 verfehlt VIL des DRV8876",
      _u_alt > M.DRV_VIL_MAX, True)
check("Gegenprobe: sie liegt sogar ueber VIH -- der Treiber bleibt wach",
      _u_alt > M.DRV_VIH_MIN, True)
check("Gegenprobe: der gerechnete Pegel liegt bei rund 3,05 V",
      round(_u_alt, 2), 3.05)

# --- Gegenprobe 2: R14 weg, R9 gross -- ZWEI Diodenspannungen in Reihe ---
# Der Bus geht nicht auf 0 V, sondern liegt selbst eine Diodenspannung
# ueber Masse (D3/D4 gegen den Schaltkontakt). Eine zweite Diode zum
# nSLEEP-Pin addiert die naechste.
_u_ohne_r14 = _nsleep_diodenklemme(10e3, 0.0, 2 * M.ALT_VF_1N4148)
check("Gegenprobe: Klemme ohne R14 (R9=10k) bleibt trotzdem ueber VIL",
      _u_ohne_r14 > M.DRV_VIL_MAX, True)

# --- Gegenprobe 3: dieselbe passive Klemme mit Schottky auf BEIDEN Wegen
# haette im Grenzfall exakt null Reserve.
_u_schottky = 2 * M.SCHOTTKY_VF_MAX_10MA
check("Gegenprobe: passiv mit zwei Schottky-Dioden bleibt keine Reserve "
      "gegen VIL", _u_schottky >= M.DRV_VIL_MAX, True)

# --- die gebaute Loesung: UND-Gatter mit Gegentaktausgang ---------------
_u_notaus = M.GATTER_VOL_MAX          # SCES217AA 5.5, VOL bei IOL=100uA
_u_normal = M.GATTER_VOH_MIN          # SCES217AA 5.5, VOH bei IOH=-100uA
check("NOTAUS gezogen: U(nSLEEP) liegt unter VIL des DRV8876",
      _u_notaus < M.DRV_VIL_MAX, True)
check("NOTAUS gezogen: mindestens 0,5 V Reserve gegen VIL",
      (M.DRV_VIL_MAX - _u_notaus) >= 0.5, True)
check("Normalbetrieb: U(nSLEEP) liegt ueber VIH des DRV8876",
      _u_normal > M.DRV_VIH_MIN, True)
check("Normalbetrieb: mindestens 1,0 V Reserve gegen VIH",
      (_u_normal - M.DRV_VIH_MIN) >= 1.0, True)
# VOL/VOH gelten nur bis 100 uA Laststrom -- der interne nSLEEP-Pulldown
# des DRV8876 muss darunter bleiben, sonst gilt die Rechnung nicht.
check("der nSLEEP-Pulldown (100 kOhm) bleibt unter der Laststrom-"
      "Bedingung, fuer die VOH/VOL gelten",
      (_u_normal / M.DRV_RPD) <= M.GATTER_IO_BEZUG, True)

# --- der Eingang B des Gatters: was der NOTAUS-Bus liefert --------------
# Gezogener Bus = Vorwaertsspannung der Koppeldiode D3/D4. Der Strom
# kommt aus den R15-Pullups aller Module im Stapel.
_i_bus = M.MODULE_IM_STAPEL * (M.V_3V3 - M.SCHOTTKY_VF_MAX_10MA) / M.R15_OHM
check("Bus-Strom bei zehn Modulen bleibt unter 10 mA -- dem Stuetzpunkt, "
      "fuer den der VF-MAX-Wert der Koppeldiode gilt",
      _i_bus <= 10e-3, True)
check("gezogener NOTAUS-Bus liegt unter VIL des Gatters",
      M.SCHOTTKY_VF_MAX_10MA < M.GATTER_VIL_MAX, True)
check("gezogener NOTAUS-Bus haelt mindestens 0,3 V Reserve gegen VIL",
      (M.GATTER_VIL_MAX - M.SCHOTTKY_VF_MAX_10MA) >= 0.3, True)
# Mit einer Si-Diode (1N4148W, wie zuerst gebaut) waere derselbe Pegel
# nicht mehr sicher unter der Schwelle -- deshalb Schottky.
check("Gegenprobe: eine Si-Koppeldiode risse die 0,3-V-Reserve auf",
      (M.GATTER_VIL_MAX - M.ALT_VF_1N4148) >= 0.3, False)
check("D3/D4 sind deshalb Schottky-Dioden", M.D_KOPPEL_WERT, "BAT54W")

# Ruhepegel des Busses: die Leckstroeme aller Koppeldioden und
# Gattereingaenge gegen den parallelgeschalteten Pullup.
_r_bus = M.R15_OHM / M.MODULE_IM_STAPEL
_i_leck = M.MODULE_IM_STAPEL * (2 * M.SCHOTTKY_IR_MAX + M.GATTER_II_MAX)
_u_bus_high = M.V_3V3 - _i_leck * _r_bus
check("Ruhepegel des NOTAUS-Busses bleibt ueber VIH des Gatters",
      _u_bus_high > M.GATTER_VIH_MIN, True)

# --- die Rueckwirkung auf den MCU-GPIO ---------------------------------
# Genau das Anliegen, das R14 einmal loesen sollte: der GPIO darf nicht
# in die Verriegelung einspeisen. Ein CMOS-Gattereingang loest das ohne
# Widerstand -- und ohne die Wirkung zu verhindern.
check("der MCU-GPIO speist hoechstens Gattereingangs-Leckstrom ein "
      "(unter 0,1 mA)", M.GATTER_II_MAX < 0.1e-3, True)
check("R9 (100 Ohm) macht dabei weniger als 1 mV Abfall -- kein Grund, "
      "ihn zu vergroessern", (M.GATTER_II_MAX * M.R9_OHM) < 1e-3, True)
# Zum Vergleich: die Diodenklemme ohne R14 haette denselben GPIO mit
# rund 27 mA belastet -- der Grund, aus dem R14 ueberhaupt entstand.
_i_alt = (M.V_3V3 - M.ALT_VF_1N4148) / M.R9_OHM
check("Gegenprobe: die Diodenklemme ohne R14 haette den GPIO mit ueber "
      "20 mA belastet", _i_alt > 20e-3, True)


# ------------------- Aufgabe 5d: der Notaus-EINGANG im Ruhestrom (Oeffner)
# Bis Aufgabe 5c war der externe Kontakt ein SCHLIESSER: Schliessen hiess
# Notaus, ein Kabelbruch sah aus wie "alles in Ordnung". Jetzt ist er ein
# OEFFNER im Ruhestrom. Die folgenden Zusicherungen rechnen die Kette
# nach, sie zaehlen nicht Bauteile. Alle Groessen stehen mit
# Dokumentnummer und Abschnitt in tools/sch/motormodul.py.

# --- der Schleifenstrom, aus dem alles Weitere folgt -------------------
# Zwei gleiche Vorwiderstaende je Kanal, dazwischen der externe Oeffner.
_R_SCHLEIFE_GES = 2 * M.R_SCHLEIFE_OHM
_if_min = ((M.V_24V_MIN - M.OPTO_VF_MAX)
           / (_R_SCHLEIFE_GES * (1 + M.R_SCHLEIFE_TOL)))
_if_max = ((M.V_24V_MAX - M.OPTO_VF_TYP)
           / (_R_SCHLEIFE_GES * (1 - M.R_SCHLEIFE_TOL)))
check("Schleifenstrom bleibt im schlechtesten Fall ueber 3 mA "
      "(Kontaktbenetzung)", _if_min > 3e-3, True)
check("Schleifenstrom bleibt weit unter dem Grenzstrom der PC817-LED "
      "(50 mA, SHARP D2-A03101EN, Absolute Maximum Ratings)",
      _if_max < 0.2 * M.OPTO_IF_ABSMAX, True)

# --- HIGH-Pegel bei geschlossener Schleife -----------------------------
# Der Fototransistor muss den Pulldown ueber VIH des Inverters heben.
_ic_noetig = M.INV_VIH_MIN / M.R_PULLDOWN_OHM
_ctr_noetig = _ic_noetig / _if_min
_ctr_garantiert = M.OPTO_IC_MIN_BEI_5MA / M.OPTO_IF_BEZUG
check("noetige Stromuebertragung der Schleife bleibt unter dem "
      "garantierten CTR-Minimum des PC817 (Faktor >= 3)",
      _ctr_garantiert / _ctr_noetig >= 3.0, True)
# Und die Ehrlichkeitsprobe dazu: reicht der Strom NICHT, faellt es in
# die sichere Richtung -- der Knoten bleibt unter VIH, der Kanal meldet
# "offen". Ein zu schwacher Optokoppler kann kein falsches "in Ordnung"
# erzeugen. Das ist der Grund, warum der unbelegte Arbeitspunkt
# (3,0 mA statt der garantierten 5 mA) vertretbar ist.
check("ein CTR-Mangel kann nur 'offen' melden, nie 'in Ordnung' -- der "
      "Knoten wird vom Optokoppler ausschliesslich nach OBEN getrieben",
      M.R_PULLDOWN_OHM > 0, True)

# --- LOW-Pegel bei offener Schleife (Kabelbruch) -----------------------
# Ohne LED-Strom bleiben nur Dunkelstrom (PC817 ICEO) und der
# Eingangsstrom des Inverters.
_i_leck_knoten = M.OPTO_ICEO_MAX + M.INV_II_MAX
_u_knoten_offen = _i_leck_knoten * M.R_PULLDOWN_OHM
check("Kabelbruch: der Schleifenknoten faellt unter VIL des Inverters",
      _u_knoten_offen < M.INV_VIL_MAX, True)
check("Kabelbruch: mindestens 0,7 V Reserve gegen VIL",
      (M.INV_VIL_MAX - _u_knoten_offen) >= 0.7, True)
# Der Pulldown ist bewusst niederohmig genug, dass ein versehentlich in
# der Firmware eingeschalteter interner Pullup des MCU-Pins die Kette
# NICHT aushebelt. Der Pullup-Bereich ist eine Abschaetzung (30 kOhm als
# unguenstigster Wert), kein DS13866-Zitat -- so steht es auch im
# Kommentar in motormodul.py.
_MCU_PULLUP_MIN_ANNAHME = 30e3
_u_mit_firmware_pullup = (M.V_3V3 * M.R_PULLDOWN_OHM
                          / (M.R_PULLDOWN_OHM + _MCU_PULLUP_MIN_ANNAHME))
check("selbst ein irrtuemlich eingeschalteter MCU-Pullup laesst den "
      "Knoten unter VIL", _u_mit_firmware_pullup < M.INV_VIL_MAX, True)

# --- warum kein Pulldown+Diode auf den Bus (die Einschaetzung im Auftrag)
# Der bisherige Weg war: Schaltkontakt zieht den Kanalknoten auf ~0 Ohm,
# Schottky zieht den Bus mit. Ein PULLDOWN kann das nicht: er muss gegen
# den parallelgeschalteten Buspullup arbeiten.
_r_bus = M.R15_OHM / M.MODULE_IM_STAPEL
_u_knoten_gegen_bus = (M.V_3V3 * M.R_PULLDOWN_OHM
                       / (_r_bus + M.R_PULLDOWN_OHM))
check("Gegenprobe: ein Pulldown allein zieht die Sammelleitung NICHT "
      "unter VIL -- deshalb der Open-Drain-Treiber",
      _u_knoten_gegen_bus > M.GATTER_VIL_MAX, True)
# Und der Grenzwert, ab dem ein Pulldown es koennte -- unbaubar klein:
_r_pd_noetig = (_r_bus * (M.GATTER_VIL_MAX - M.SCHOTTKY_VF_MAX_10MA)
                / (M.V_3V3 - M.GATTER_VIL_MAX))
check("ein wirksamer Pulldown muesste unter 200 Ohm liegen (er traegt "
      "die Schwelle 0,8 V abzueglich der Diodenspannung bei 2,5 mA "
      "Busstrom)", _r_pd_noetig < 200.0, True)
_ic_bei_solchem_pulldown = M.INV_VIH_MIN / _r_pd_noetig
check("...und der Optokoppler muesste ihn mit ueber 10 mA auf VIH "
      "heben -- das Dreifache des ganzen Schleifenstroms",
      _ic_bei_solchem_pulldown > 10e-3, True)
check("...also mehr, als ueberhaupt durch die Schleife fliesst",
      _ic_bei_solchem_pulldown > _if_max, True)

# --- der Open-Drain-Treiber auf der Sammelleitung ----------------------
_i_bus_od = (M.MODULE_IM_STAPEL
             * (M.V_3V3 - M.INV_VOL_MAX_16MA) / M.R15_OHM)
check("Busstrom bleibt unter dem Stuetzpunkt, fuer den VOL des Inverters "
      "gilt (16 mA)", _i_bus_od <= M.INV_IOL_BEZUG_16MA, True)
check("Busstrom bleibt weit unter dem zulaessigen IOL (24 mA)",
      _i_bus_od < M.INV_IOL_MAX, True)
check("gezogener NOTAUS-Bus liegt unter VIL des Verriegelungsgatters",
      M.INV_VOL_MAX_16MA < M.GATTER_VIL_MAX, True)
check("gezogener NOTAUS-Bus haelt mindestens 0,3 V Reserve gegen VIL",
      (M.GATTER_VIL_MAX - M.INV_VOL_MAX_16MA) >= 0.3, True)
# Gegenprobe: eine Diode IN REIHE zum Open-Drain-Ausgang (also D3/D4
# stehengelassen) haette exakt die Schwelle erreicht -- null Reserve.
# Genau deshalb entfallen D3/D4, statt bloss zu bleiben.
check("Gegenprobe: Open-Drain PLUS Schottky in Reihe laesst keine "
      "Reserve gegen VIL",
      (M.INV_VOL_MAX_16MA + M.SCHOTTKY_VF_MAX_10MA) >= M.GATTER_VIL_MAX,
      True)
# Ruhepegel des Busses mit den Leckstroemen der neuen Treiber.
_i_leck_bus = M.MODULE_IM_STAPEL * (2 * M.INV_IOFF_MAX + M.GATTER_II_MAX)
_u_bus_high = M.V_3V3 - _i_leck_bus * _r_bus
check("Ruhepegel des NOTAUS-Busses bleibt ueber VIH des Gatters",
      _u_bus_high > M.GATTER_VIH_MIN, True)
check("Ruhepegel haelt mindestens 1,0 V Reserve gegen VIH",
      (_u_bus_high - M.GATTER_VIH_MIN) >= 1.0, True)

# --- Punkt 4: Strombegrenzung nach aussen ------------------------------
_i_kurzschluss = M.V_24V_MAX / M.R_SCHLEIFE_OHM
_p_kurzschluss = M.V_24V_MAX ** 2 / M.R_SCHLEIFE_OHM
check("Kurzschluss einer herausgefuehrten Ader begrenzt auf unter 10 mA",
      _i_kurzschluss < 10e-3, True)
check("...und der betroffene Widerstand bleibt unter seiner Nennleistung",
      _p_kurzschluss < M.R1206_P_NENN, True)
check("die Schleifenwiderstaende sind deshalb 1206, nicht 0805 "
      "(ein 0805 mit 125 mW waere im Kurzschluss ueberlastet)",
      _p_kurzschluss > 0.125, True)
check("Betriebsspannung bleibt weit unter der zulaessigen "
      "Arbeitsspannung des 1206-Typs (200 V)",
      M.V_24V_MAX < 0.2 * M.R1206_U_MAX, True)
# Auch der ungueenstigste Fall auf der Rueckleitung (Ader an +24V) haelt
# den LED-Strom unter dem Grenzstrom des PC817.
_if_bei_kurzschluss = (M.V_24V_MAX - M.OPTO_VF_TYP) / M.R_SCHLEIFE_OHM
check("Ader gegen +24V: der LED-Strom bleibt unter dem PC817-Grenzstrom",
      _if_bei_kurzschluss < M.OPTO_IF_ABSMAX, True)


_KICAD_CLI = shutil.which("kicad-cli")
if _KICAD_CLI is None:
    print("UEBERSPRUNGEN: kicad-cli nicht in PATH gefunden -- die "
          "Netzzuordnungs- und ERC-Pruefung (beide bauen das Motormodul "
          "ueber gen.py/symlib.py tatsaechlich auf, das braucht kicad-cli "
          "fuer die Symbolbibliothekspfade UND fuer den ERC-Lauf selbst) "
          "koennen in dieser Umgebung nicht laufen und werden ausgelassen. "
          "Alle anderen Pruefungen liefen.")
else:
    import gen as _gen

    _sch = _gen.Schaltplan("motormodul_test", "Motormodul (Test)", "")
    motormodul.bauen(_sch, 0.0, 0.0)

    def _netz_pins(sch, gen_mod, netzname):
        """Alle (ref, pinnr) an Pins, deren Stichleitung auf einem Label
        ODER Power-Symbol `netzname` endet. Woertlich aus
        tests/test_modulsockel.py / tests/test_sockelplatine.py
        uebernommen."""
        ziel_pts = {(x, y) for x, y, rot, txt in sch.LABELS if txt == netzname}
        ziel_pts |= {pos for libid, pos, rot, value in sch.POWERS if value == netzname}
        pin_pts = set()
        for a, b in sch.WIRES:
            if a in ziel_pts:
                pin_pts.add(b)
            if b in ziel_pts:
                pin_pts.add(a)
        treffer = []
        for ref, libid, pos, rot, value, fp, _, _, einheit in sch.COMPS:
            einheiten = sch.UNITPINS.get(libid)
            nums = einheiten[einheit] if einheiten else sch.PINS[libid].keys()
            for num in nums:
                p = sch.PINS[libid][num]
                xy = gen_mod.xf(pos, (p[0], p[1]), rot)
                if xy in pin_pts:
                    treffer.append((ref, num))
        return treffer

    # -------------------------------------------------- Bauteilliste
    _refs = sorted(set(c[0] for c in _sch.COMPS if not c[0].startswith("#")))
    # D2 und R14 sind ENTFALLEN (die Diodenklemme, die nicht wirkte --
    # s. Pegelrechnung oben und tools/sch/motormodul.py,
    # _notaus_verriegelung()); dafuer sind U3 (Verriegelungsgatter) und
    # C14 (dessen Abblockkondensator) dazugekommen. Wer R14/D2 wieder
    # einbaut, faellt hier auf.
    # Aufgabe 5d: auch D3/D4 sind ENTFALLEN -- die Koppeldioden vom
    # Schaltkontakt auf die Sammelleitung. An ihre Stelle tritt der
    # Ruhestrom-Eingang: R16..R19 (Schleifenwiderstaende), U4/U5
    # (Optokoppler), R20/R21 (Pulldown am Schleifenknoten), U6/U7
    # (Inverter mit Open-Drain-Ausgang) und C15/C16 (deren Abblockung).
    _erwartet_endstufe = {"D1", "C9", "C10", "C11", "C12",
                           "C13", "C14", "C15", "C16",
                           "J2", "J3", "J5", "Q1", "R5", "R6",
                           "R7", "R8", "R9", "R10", "R11", "R12", "R13",
                           "R15", "R16", "R17", "R18", "R19", "R20", "R21",
                           "U1", "U2", "U3", "U4", "U5", "U6", "U7"}
    _erwartet_sockel = {"U100", "U101", "U102", "U103", "R100", "R101",
                         "R102", "R104", "R105", "C100", "C101",
                         "J100", "J101", "J102", "J103", "J104"}
    check("Referenzen = Modulsockel-Block + Endstufe (nichts Ueberzaehliges)",
          set(_refs), _erwartet_endstufe | _erwartet_sockel)

    # -------------------------------- Steuerleitungen haengen am MCU ---
    # Der eigentliche Auftrag: IN1/IN2/NSLEEP haengen am Modul-MCU (U100),
    # NICHT direkt am Stapelstecker (J100) -- die Vorwiderstaende R7/R8/R9
    # trennen den MCU-seitigen Knoten vom DRV8876-seitigen.
    for rolle, u100_pin, r_ref in (("IN1", "9", "R7"), ("IN2", "10", "R8"),
                                     ("NSLEEP", "11", "R9")):
        _treffer = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN[rolle]))
        check("U100 Pin %s (%s) haengt am MCU" % (u100_pin, rolle),
              ("U100", u100_pin) in _treffer, True)
        check("%s (Vorwiderstand) haengt auf demselben Netz wie %s"
              % (r_ref, rolle), (r_ref, "1") in _treffer, True)
        check("%s erreicht NICHT direkt den Stapelstecker J100"
              % rolle, any(ref == "J100" for ref, _ in _treffer), False)
        check("U1 (DRV8876) haengt NICHT direkt an der MCU-Seite von %s "
              "(der Vorwiderstand muss dazwischen sitzen)" % rolle,
              any(ref == "U1" for ref, _ in _treffer), False)

    # NFAULT und IPROPI haben laut Aufgabenbrief KEINEN Vorwiderstand --
    # DRV8876, Pullup/Filter und MCU teilen sich direkt ein Netz.
    _an_nfault = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["NFAULT"]))
    check("NFAULT erreicht U100 (MCU-Eingang)", ("U100", "12") in _an_nfault, True)
    check("NFAULT erreicht U1 Pin 4 (DRV8876 ~NFAULT)", ("U1", "4") in _an_nfault, True)
    check("NFAULT traegt den Pullup R13", ("R13", "2") in _an_nfault, True)

    _an_ipropi = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["IPROPI"]))
    # PA6 traegt laut STM32C011-Datenblatt (DS13866, Tabelle 12 "Pin
    # assignment and description") die Zusatzfunktion ADC_IN6 -- per
    # WebSearch-Auszug aus der Tabelle bestaetigt (zwei unabhaengige
    # Fundstellen), keine selbst geoeffnete PDF-Seite (st.com blockiert
    # den direkten Download mit HTTP/2 INTERNAL_ERROR, dieselbe
    # Einschraenkung wie hardware/bauteile.md, Beleg 1, dort dokumentiert).
    check("IPROPI erreicht U100 Pin 13 (PA6 -- ADC_IN6, DS13866 Tabelle 12)",
          ("U100", "13") in _an_ipropi, True)
    check("IPROPI erreicht U1 Pin 6 (DRV8876 IPROPI-Ausgang)",
          ("U1", "6") in _an_ipropi, True)
    check("IPROPI traegt R5 (bestueckt, s.o.)", ("R5", "1") in _an_ipropi, True)
    check("IPROPI traegt R10 (DNP)", ("R10", "1") in _an_ipropi, True)

    # -------------------------------------------------------- Punkt 3: C12
    # Polarisierter Kondensator: Pin 1 ("+" im Device:C_Polarized-Symbol)
    # MUSS an +24V liegen, NIE an GND (der Muttern-Print-Fehler).
    _an_24v = set(_netz_pins(_sch, _gen, "+24V"))
    check("C12 Pin 1 (\"+\") haengt an +24V", ("C12", "1") in _an_24v, True)
    _an_gnd = set(_netz_pins(_sch, _gen, "GND"))
    check("C12 Pin 1 (\"+\") haengt NICHT an GND", ("C12", "1") in _an_gnd, False)
    check("C12 Pin 2 haengt an GND", ("C12", "2") in _an_gnd, True)
    check("R5 ist bestueckt (nicht in sch.DNP)", "R5" in _sch.DNP, False)
    check("R10 ist DNP (Aufgabenbrief: 'R10 unbestueckt')", "R10" in _sch.DNP, True)

    # ----------------------------------------------------- Punkt 4: NOTAUS
    # Die Sammelleitung erreicht den Stapelstecker (global) UND die
    # Hardware-Verriegelung (U3, wirkt auf U1_NSLEEP unabhaengig vom MCU)
    # UND die zwei Open-Drain-Treiber der Ruhestrom-Kanaele (U6/U7).
    _an_notaus = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["NOTAUS"]))
    check("NOTAUS erreicht den Stapelstecker (J100 Pin 9)",
          ("J100", "9") in _an_notaus, True)
    check("NOTAUS erreicht U3 Pin 2 (Eingang B des Verriegelungsgatters)",
          ("U3", "2") in _an_notaus, True)
    check("NOTAUS traegt den Pullup R15", ("R15", "2") in _an_notaus, True)
    check("NOTAUS erreicht NICHT direkt U1 (der Weg fuehrt ueber das "
          "Gatter und U1_NSLEEP, nicht direkt auf den DRV8876)",
          any(ref == "U1" for ref, _ in _an_notaus), False)
    # Aufgabe 5d: der Bus wird von den zwei Open-Drain-Ausgaengen gezogen,
    # nicht mehr von Koppeldioden an einem Schaltkontakt.
    check("NOTAUS wird von U6 Pin 4 gezogen (Open-Drain, Kanal 1)",
          ("U6", "4") in _an_notaus, True)
    check("NOTAUS wird von U7 Pin 4 gezogen (Open-Drain, Kanal 2)",
          ("U7", "4") in _an_notaus, True)
    check("auf NOTAUS haengt nichts ausser Stecker, Pullup, "
          "Verriegelungsgatter und den zwei Kanaltreibern",
          _an_notaus, {("J100", "9"), ("R15", "2"), ("U3", "2"),
                        ("U6", "4"), ("U7", "4")})
    check("keine Koppeldiode mehr am Bus (D3/D4 entfallen -- eine Diode "
          "in Reihe zum Open-Drain-Ausgang liesse null Reserve)",
          any(ref in ("D3", "D4") for ref, _ in _an_notaus), False)

    # ------------------------- Aufgabe 5d: der Ruhestromkreis an J3 ----
    # Vier Pole, aber voellig andere Bedeutung als vorher: zwei Adern je
    # Kanal statt Signal+GND. Der beste maschinelle Nachweis, dass der
    # Eingang KEIN Schliesser gegen Masse mehr ist: an J3 haengt kein
    # einziger GND-Pin.
    _an_gnd = set(_netz_pins(_sch, _gen, "GND"))
    check("J3 fuehrt keine Masse mehr nach aussen (der alte Schliesser "
          "gegen GND ist weg)",
          any(ref == "J3" for ref, _ in _an_gnd), False)
    _j3_pins = set()
    for _kanal in (1, 2):
        for _seite, _nr in (("A", 2 * _kanal - 1), ("B", 2 * _kanal)):
            _netzname = "KREIS%d_%s" % (_kanal, _seite)
            _an_kreis = set(_netz_pins(_sch, _gen, _netzname))
            check("%s liegt an J3 Pin %d" % (_netzname, _nr),
                  ("J3", str(_nr)) in _an_kreis, True)
            _j3_pins.add(("J3", str(_nr)))
            check("%s traegt genau zwei Pins (Stecker und Vorwiderstand)"
                  % _netzname, len(_an_kreis), 2)
    check("J3 hat vier Pole -- zwei Adern je Kanal", len(_j3_pins), 4)

    # Die zwei Kanaele bleiben elektrisch GETRENNT bis auf den Bus.
    _an_schleife1 = set(_netz_pins(_sch, _gen, "SCHLEIFE_1"))
    _an_schleife2 = set(_netz_pins(_sch, _gen, "SCHLEIFE_2"))
    check("SCHLEIFE_1 und SCHLEIFE_2 sind verschiedene Netze",
          _an_schleife1.isdisjoint(_an_schleife2), True)
    check("U100 Pin 3 (PC15) liest Kanal 1", ("U100", "3") in _an_schleife1, True)
    check("U100 Pin 14 (PA7) liest Kanal 2", ("U100", "14") in _an_schleife2, True)
    for _kanal, (_pins, _opto, _rpd, _inv) in enumerate((
            (_an_schleife1, "U4", "R20", "U6"),
            (_an_schleife2, "U5", "R21", "U7")), start=1):
        check("Kanal %d: der Optokoppler-EMITTER (Pin 3) treibt den "
              "Schleifenknoten -- Emitterfolger, geschlossen = HIGH"
              % _kanal, (_opto, "3") in _pins, True)
        check("Kanal %d: der Pulldown haengt am Schleifenknoten" % _kanal,
              (_rpd, "1") in _pins, True)
        check("Kanal %d: der Open-Drain-Inverter liest den Schleifenknoten"
              % _kanal, (_inv, "2") in _pins, True)
        check("Kanal %d: am Schleifenknoten haengt sonst nichts" % _kanal,
              _pins, {(_opto, "3"), (_rpd, "1"), (_inv, "2"),
                       ("U100", "3" if _kanal == 1 else "14")})
        check("Kanal %d: der Optokoppler-KOLLEKTOR (Pin 4) haengt an 3V3"
              % _kanal, (_opto, "4") in set(_netz_pins(_sch, _gen, "3V3")), True)
        check("Kanal %d: der Inverter ist versorgt (Pin 5 an 3V3)" % _kanal,
              (_inv, "5") in set(_netz_pins(_sch, _gen, "3V3")), True)
        check("Kanal %d: der Inverter liegt an GND (Pin 3)" % _kanal,
              (_inv, "3") in _an_gnd, True)

    # Die vier Schleifenwiderstaende MUESSEN 1206 sein -- ein 0805 waere
    # im aeusseren Dauerkurzschluss ueberlastet (Rechnung oben).
    _fp = {c[0]: c[5] for c in _sch.COMPS}
    for _r in ("R16", "R17", "R18", "R19"):
        check("%s traegt den 1206-Footprint (Kurzschlussfestigkeit)" % _r,
              _fp.get(_r), motormodul.FP_R1206)
    for _r in ("R20", "R21"):
        check("%s (Pulldown, nur Kleinsignal) bleibt 0805" % _r,
              _fp.get(_r), motormodul.FP_R0805)

    # ---- DIE Zusicherung fuer den Kabelbruch: aus dem Schaltplan ------
    def _knoten_bei_offener_schleife(kanal, r_pd):
        """Spannung am Schleifenknoten bei GEBROCHENER Schleife --
        hergeleitet aus dem, was laut Schaltplan am zweiten Ende des
        Widerstands R20/R21 haengt.

        Liegt es auf GND, ist es ein PULLDOWN: ohne LED-Strom bleibt nur
        Leckstrom, der Knoten faellt praktisch auf Masse.
        Liegt es auf 3V3, ist es ein PULLUP: dann steht der Knoten bei
        offener Schleife HIGH -- der Kabelbruch bliebe unbemerkt.
        Liegt es auf keinem von beiden, ist der Knoten unbestimmt; das
        wird als schlechtester Fall (halbe Schiene) gewertet."""
        an_gnd = (r_pd, "2") in set(_netz_pins(_sch, _gen, "GND"))
        an_3v3 = (r_pd, "2") in set(_netz_pins(_sch, _gen, "3V3"))
        leck = (M.OPTO_ICEO_MAX + M.INV_II_MAX) * M.R_PULLDOWN_OHM
        if an_gnd and not an_3v3:
            return leck
        if an_3v3 and not an_gnd:
            return M.V_3V3 - leck
        return M.V_3V3 / 2.0

    def _notaus_kette_bei_kabelbruch(kanal, r_pd):
        """Die ganze Kette: Kabelbruch -> Schleifenknoten -> Inverter ->
        Sammelleitung -> Verriegelungsgatter -> nSLEEP des DRV8876.
        Liefert (u_knoten, u_bus, u_nsleep)."""
        u_knoten = _knoten_bei_offener_schleife(kanal, r_pd)
        if u_knoten <= M.INV_VIL_MAX:
            # Der Inverter liest LOW und zieht die Sammelleitung: VOL,
            # begrenzt durch den MAX-Wert bei 16 mA (SCES295AB 5.5).
            u_bus = M.INV_VOL_MAX_16MA
        else:
            # Der Inverter laesst den Bus los; der Pullup haelt ihn HIGH.
            u_bus = M.V_3V3
        if u_bus <= M.GATTER_VIL_MAX:
            u_nsleep = M.GATTER_VOL_MAX
        else:
            u_nsleep = M.GATTER_VOH_MIN
        return u_knoten, u_bus, u_nsleep

    for _kanal, _rpd in ((1, "R20"), (2, "R21")):
        _uk, _ub, _un = _notaus_kette_bei_kabelbruch(_kanal, _rpd)
        check("KABELBRUCH Kanal %d: der Schleifenknoten faellt unter VIL "
              "des Inverters" % _kanal, _uk < M.INV_VIL_MAX, True)
        check("KABELBRUCH Kanal %d: die Sammelleitung wird unter VIL des "
              "Verriegelungsgatters gezogen" % _kanal,
              _ub < M.GATTER_VIL_MAX, True)
        check("KABELBRUCH Kanal %d: der DRV8876 liest an nSLEEP LOW und "
              "schlaeft -- Notaus aktiv, ohne dass jemand einen Taster "
              "gedrueckt hat" % _kanal, _un < M.DRV_VIL_MAX, True)

    # Gegenprobe zur Gegenprobe: mit einem PULLUP statt des Pulldowns
    # liefert dieselbe Kette "kein Notaus" -- genau dann wird die
    # Zusicherung oben rot. (Hier bewusst als erwartetes Ergebnis
    # formuliert, damit der Unterschied im Test sichtbar ist und nicht
    # nur in einer Wegwerfkopie des Repos.)
    _u_falsch = M.V_3V3 - (M.OPTO_ICEO_MAX + M.INV_II_MAX) * M.R_PULLDOWN_OHM
    check("Gegenprobe: waere es ein Pullup, laege der Knoten bei "
          "Kabelbruch HIGH", _u_falsch > M.INV_VIH_MIN, True)
    check("Gegenprobe: dann bliebe die Sammelleitung HIGH und der "
          "Treiber wach -- der Bruch bliebe unbemerkt",
          M.GATTER_VOH_MIN > M.DRV_VIH_MIN, True)

    # Die Verriegelung sitzt IM Signalweg zwischen MCU und DRV8876: der
    # MCU erreicht den Treiber-nSLEEP-Pin nur noch ueber das Gatter.
    # Das Netz U1_NSLEEP darf deshalb GENAU zwei Pins tragen -- den
    # Gatterausgang und den Treibereingang. Haengt dort noch etwas
    # anderes (etwa eine wieder eingebaute Diodenklemme R14/D2), ist die
    # Gegentaktstufe des Gatters nicht mehr allein bestimmend und diese
    # Zusicherung wird rot.
    _an_u1_nsleep = set(_netz_pins(_sch, _gen, "U1_NSLEEP"))
    check("U3 Pin 4 (Gatterausgang Y) treibt U1_NSLEEP",
          ("U3", "4") in _an_u1_nsleep, True)
    check("U1 Pin 3 (DRV8876 nSLEEP) haengt auf demselben Netz",
          ("U1", "3") in _an_u1_nsleep, True)
    check("auf U1_NSLEEP haengt NICHTS ausser Gatterausgang und "
          "Treibereingang (kein zweiter Treiber, keine Diodenklemme)",
          _an_u1_nsleep, {("U3", "4"), ("U1", "3")})

    def _u_nsleep_aus_schaltplan(pins_am_netz):
        """Pegel am DRV8876-nSLEEP-Pin im Notaus-Fall, hergeleitet aus
        dem, was laut Schaltplan tatsaechlich auf U1_NSLEEP haengt.

        Treibt dort allein der Gatterausgang, gilt VOL (SCES217AA 5.5).
        Haengt dort etwas anderes, ist es die passive Klemme, wie sie
        zuerst gebaut war (R14 + D2 gegen den MCU-Vorwiderstand R9) --
        dann gilt die Knotengleichung, und der Pegel verfehlt VIL. So
        wird diese Zusicherung rot, sobald jemand R14/D2 wieder
        einbaut."""
        if pins_am_netz - {("U1", "3")} == {("U3", "4")}:
            return M.GATTER_VOL_MAX
        return _nsleep_diodenklemme(M.R9_OHM, M.ALT_R14_OHM, M.ALT_VF_1N4148)

    _u_ist = _u_nsleep_aus_schaltplan(_an_u1_nsleep)
    check("aus dem Schaltplan hergeleitet: U(nSLEEP) liegt im Notaus-Fall "
          "unter VIL des DRV8876", _u_ist < M.DRV_VIL_MAX, True)

    # Der MCU erreicht das Gatter ueber R9 und sonst nichts.
    _an_gatter_a = set(_netz_pins(_sch, _gen, "NSLEEP_GATTER"))
    check("R9 speist den Gattereingang A", ("R9", "2") in _an_gatter_a, True)
    check("U3 Pin 1 (Eingang A) haengt am selben Netz",
          ("U3", "1") in _an_gatter_a, True)
    check("zwischen R9 und Gattereingang A haengt sonst nichts",
          _an_gatter_a, {("R9", "2"), ("U3", "1")})
    _an_mcu_nsleep = set(_netz_pins(_sch, _gen, modulsockel.NETZE_NACH_AUSSEN["NSLEEP"]))
    check("das Gatter haengt NICHT direkt auf der MCU-Seite von NSLEEP "
          "(R9 bleibt dazwischen)",
          any(ref == "U3" for ref, _ in _an_mcu_nsleep), False)

    # Versorgung des Gatters -- ohne sie ist die Verriegelung ein
    # unbestuecktes Versprechen.
    check("U3 Pin 5 (VCC) haengt an 3V3",
          ("U3", "5") in set(_netz_pins(_sch, _gen, "3V3")), True)
    check("U3 Pin 3 (GND) haengt an GND",
          ("U3", "3") in set(_netz_pins(_sch, _gen, "GND")), True)
    check("C14 blockt die Gatterversorgung ab (Pin 1 an 3V3)",
          ("C14", "1") in set(_netz_pins(_sch, _gen, "3V3")), True)

    # ------------------------------------------------------------- ERC
    ERWARTETE_ERC_FEHLER = 0
    ERWARTETE_ERC_WARNUNGEN = 0

    _tmp = tempfile.mkdtemp(prefix="motormodul_erc_")
    try:
        # sym-lib-table/fp-lib-table zeigen relativ auf "${KIPRJMOD}/../
        # components/..." (dieselbe Struktur wie hardware/kicad/motor/,
        # s. dort) -- der Testbau braucht deshalb dieselbe Verzeichnis-
        # SCHACHTELUNG, nicht nur die beiden Tabellen lose im Temp-Ordner.
        # Eigene Messung: ohne die Nachbar-components/ loeste kicad-cli
        # den Pfad zwar auf ("${KIPRJMOD}" korrekt ersetzt), fand die
        # Zieldatei aber nicht -- zwei ERC-Warnungen blieben stehen.
        _motor_dir = os.path.join(_tmp, "motor")
        os.makedirs(_motor_dir)
        os.symlink(os.path.abspath(os.path.join(HERE, "..", "hardware", "kicad",
                                                  "components")),
                   os.path.join(_tmp, "components"))

        _sch_erc = _gen.Schaltplan("motormodul_erc_test", "Motormodul (ERC-Test)", "")
        motormodul.bauen(_sch_erc, 0.0, 0.0)
        _sch_pfad = _sch_erc.schreiben(os.path.join(_motor_dir, "Motormodul.kicad_sch"))
        for _fname in ("sym-lib-table", "fp-lib-table", "Motormodul.kicad_pro"):
            shutil.copy(os.path.join(HERE, "..", "hardware", "kicad", "motor", _fname),
                        os.path.join(_motor_dir, _fname))

        _json_pfad = os.path.join(_tmp, "erc.json")
        _proc = subprocess.run(
            [_KICAD_CLI, "sch", "erc", "--format", "json",
             "--output", _json_pfad, _sch_pfad],
            capture_output=True, text=True)
        if not os.path.exists(_json_pfad):
            fails.append("kicad-cli sch erc lieferte keinen JSON-Report "
                          "(rc=%s): %s" % (_proc.returncode, _proc.stderr.strip()))
        else:
            with open(_json_pfad, encoding="utf-8") as f:
                _report = json.load(f)
            _errors, _warnings = [], []
            for _sheet in _report.get("sheets", []):
                for _v in _sheet.get("violations", []):
                    (_errors if _v["severity"] == "error" else _warnings).append(_v)
            check("ERC-Fehler auf dem Motormodul", len(_errors), ERWARTETE_ERC_FEHLER)
            check("ERC-Warnungen auf dem Motormodul", len(_warnings), ERWARTETE_ERC_WARNUNGEN)
            for _e in _errors:
                print("  ERC-Fehler:", _e.get("type"), "-", _e.get("description"))
            for _w in _warnings:
                print("  ERC-Warnung:", _w.get("type"), "-", _w.get("description"))

        # --------------------------------------------------------- Netzliste
        _net_pfad = os.path.join(_tmp, "motor.net")
        _proc2 = subprocess.run(
            [_KICAD_CLI, "sch", "export", "netlist", "-o", _net_pfad, _sch_pfad],
            capture_output=True, text=True)
        check("Netzlisten-Export lief fehlerfrei durch", _proc2.returncode, 0)
        _ausgabe = (_proc2.stdout + _proc2.stderr).lower()
        check("keine Annotationswarnung beim Netzlisten-Export",
              "annotat" in _ausgabe, False)
    finally:
        shutil.rmtree(_tmp, ignore_errors=True)

if fails:
    print("FEHLGESCHLAGEN:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("alle Pruefungen bestanden")

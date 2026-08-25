"""
================================================================================
AUDIT D'INTÉGRITÉ — chaque chiffre affiché vient-il bien des fichiers sources ?
================================================================================
Ce script recalcule les chiffres clés **directement depuis data/raw/**, avec un
code volontairement écrit à part de celui du pipeline (lectures brutes, pas de
fonction partagée), puis les compare à ce que contient data/gold/.

Objectif : prouver qu'aucune valeur n'a été saisie à la main, arrondie à
l'avantage du récit, ou inventée.

    python src/verify.py

Sortie : une ligne par chiffre, avec la valeur brute, la valeur publiée,
et le verdict. Code de sortie 1 si un seul écart est détecté.
================================================================================
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
GOLD = ROOT / "data" / "gold"

resultats = []


def verifie(libelle, attendu, obtenu, tol=0.01, unite=""):
    ok = attendu is not None and obtenu is not None and abs(attendu - obtenu) <= tol
    resultats.append((ok, libelle, attendu, obtenu, unite))
    return ok


# =============================================================================
# Lecture BRUTE du fichier Banque Mondiale — csv standard, aucune dépendance
# =============================================================================
wb = defaultdict(dict)          # {code: {annee: valeur}}
with open(RAW / "indicators-tgo.csv", encoding="utf-8-sig", newline="") as f:
    for ligne in csv.DictReader(f):
        if ligne["Country ISO3"] != "TGO":
            continue            # écarte la ligne de tags HXL
        try:
            an = int(ligne["Year"])
            val = float(ligne["Value"])
        except (ValueError, TypeError):
            continue
        code = ligne["Indicator Code"]
        # dédoublonnage : on garde la 1re occurrence, comme le pipeline
        if an not in wb[code]:
            wb[code][an] = val


def der(code):
    """(année, valeur) du dernier point non vide d'un indicateur."""
    s = wb.get(code, {})
    if not s:
        return None, None
    a = max(s)
    return a, s[a]


def prem(code):
    s = wb.get(code, {})
    if not s:
        return None, None
    a = min(s)
    return a, s[a]


gold = json.load(open(GOLD / "diagnostic_national.json", encoding="utf-8"))
R = gold["reperes"]

print("=" * 78)
print("AUDIT D'INTÉGRITÉ — recalcul indépendant depuis data/raw/")
print("=" * 78)
print()

# ------------------------------------------------------------------- 1. accès
a_r, v_r = der("EG.ELC.ACCS.RU.ZS")
a_u, v_u = der("EG.ELC.ACCS.UR.ZS")
a0_r, v0_r = prem("EG.ELC.ACCS.RU.ZS")
verifie("Accès rural à l'électricité (dernier point)", v_r,
        R["elec_rural"]["valeur"], unite="%")
verifie("Accès urbain à l'électricité", v_u, R["ecart_urbain_rural"]["urbain"],
        unite="%")
verifie("Écart ville / campagne", v_u - v_r, R["ecart_urbain_rural"]["valeur"],
        unite="points")
verifie("Accès rural au point de départ", v0_r, R["elec_rural"]["valeur_depart"],
        unite="%")

rythme = (v_r - v0_r) / (a_r - a0_r)
verifie("Rythme observé d'électrification rurale", rythme,
        R["elec_rural"]["rythme_observe"], tol=0.001, unite="pt/an")
verifie("Rythme requis pour 2030", (100 - v_r) / (2030 - a_r),
        R["elec_rural"]["rythme_requis_2030"], tol=0.001, unite="pt/an")
verifie("Facteur d'accélération", ((100 - v_r) / (2030 - a_r)) / rythme,
        R["elec_rural"]["facteur_acceleration"], tol=0.01, unite="×")

# ------------------------------------------------------------- 2. population
a_p, v_p = None, None
pr = wb.get("SP.RUR.TOTL", {})
an_pop = max(a for a in pr if a <= a_r)
verifie("Population rurale", pr[an_pop], R["ruraux_sans_elec"]["pop_rurale"],
        tol=1, unite="hab.")
verifie("Ruraux sans électricité", pr[an_pop] * (1 - v_r / 100),
        R["ruraux_sans_elec"]["personnes"], tol=1, unite="pers.")

# ------------------------------------------------------------- 3. combustibles
for code, cle, idx in [("SG.COK.WOOD.ZS", "bois", None),
                       ("SG.COK.CHCO.ZS", "charbon", None),
                       ("SG.COK.LPGN.ZS", "gpl", None)]:
    s = wb[code]
    a_min, a_max = min(s), max(s)
    verifie(f"Combustible « {cle} » en {a_min}", s[a_min],
            R["combustibles"][cle][0], unite="%")
    verifie(f"Combustible « {cle} » en {a_max}", s[a_max],
            R["combustibles"][cle][1], unite="%")

b, c = wb["SG.COK.WOOD.ZS"], wb["SG.COK.CHCO.ZS"]
verifie("Total biomasse (dernière enquête)", b[max(b)] + c[max(c)],
        R["combustibles"]["biomasse"][1], unite="%")

# ------------------------------------------------------------- 4. cuisson propre
a_c, v_c = der("EG.CFT.ACCS.RU.ZS")
verifie("Cuisson propre en milieu rural", v_c, R["cuisson_rurale"]["valeur"],
        unite="%")
a_ct, v_ct = der("EG.CFT.ACCS.ZS")
verifie("Cuisson propre (ensemble du pays)", v_ct,
        R["renouvelable_piege"]["part_cuisson_propre"], unite="%")

# ---------------------------------------------------------------- 5. renouvelable
a_rn, v_rn = der("EG.FEC.RNEW.ZS")
verifie("Part « renouvelable » de l'énergie finale", v_rn,
        R["renouvelable_piege"]["part_renouvelable"], unite="%")

# --------------------------------------------------------------- 6. déforestation
fk = wb["AG.LND.FRST.K2"]
f0, f1 = min(fk), max(fk)
verifie(f"Couvert forestier en {f0}", fk[f0], R["deforestation"]["km2_debut"],
        tol=0.1, unite="km²")
verifie(f"Couvert forestier en {f1}", fk[f1], R["deforestation"]["km2_fin"],
        tol=0.1, unite="km²")
verifie("Perte forestière annuelle", (fk[f0] - fk[f1]) * 100 / (f1 - f0),
        R["deforestation"]["perte_ha_par_an"], tol=0.1, unite="ha/an")
verifie("Perte forestière relative", 100 * (fk[f0] - fk[f1]) / fk[f0],
        R["deforestation"]["perte_pct_relative"], tol=0.01, unite="%")

# ------------------------------------------------------------------ 7. fiabilité
co = wb["IC.ELC.OUTG"]
pt = wb["IC.ELC.OUTG.ZS"]
verifie(f"Coupures/mois en {max(co)}", co[max(co)],
        R["fiabilite"]["coupures_mois"], unite="/mois")
verifie(f"Coupures/mois en {min(co)}", co[min(co)],
        R["fiabilite"]["coupures_mois_ref"], unite="/mois")
verifie(f"Entreprises touchées en {max(pt)}", pt[max(pt)],
        R["fiabilite"]["part_entreprises"], unite="%")
verifie(f"Entreprises touchées en {min(pt)}", pt[min(pt)],
        R["fiabilite"]["part_entreprises_ref"], unite="%")

# --------------------------------------------------------------------- 8. santé
a_pm, v_pm = der("EN.ATM.PM25.MC.M3")
verifie("Exposition aux PM2,5", v_pm, R["sante"]["pm25"], unite="µg/m³")
a_mo, v_mo = der("SH.STA.AIRP.P5")
verifie("Mortalité attribuée à la pollution de l'air", v_mo,
        R["sante"]["mortalite"], unite="/100 000")

# ==================================================================== 9. GES
ges = defaultdict(dict)
with open(RAW / "observationdata-xorttne.csv", encoding="utf-8-sig", newline="") as f:
    for ligne in csv.DictReader(f):
        sect = ligne["secteur"].strip().strip('"')
        typ = ligne["type"].strip().strip('"')
        ges[sect][typ] = float(ligne["Value"])

total_nat = ges["Total"]["Total"]
verifie("Total national GES 2018", total_nat, R["ges"]["total_gg"], tol=0.01,
        unite="Gg")
verifie("Part du secteur énergie", 100 * ges["Energie"]["Total"] / total_nat,
        R["ges"]["part_energie"], unite="%")
afat = [k for k in ges if k.startswith("Agriculture")][0]
verifie("Part agriculture & forêts", 100 * ges[afat]["Total"] / total_nat,
        R["ges"]["part_afat"], unite="%")

gaz_ch4 = [k for k in ges["Total"] if "thane" in k][0]
gaz_n2o = [k for k in ges["Total"] if "azote" in k][0]
verifie("Part de l'énergie dans le méthane national",
        100 * ges["Energie"][gaz_ch4] / ges["Total"][gaz_ch4],
        R["ges"]["energie_dans_ch4"], tol=0.06, unite="%")
verifie("Part de l'énergie dans le N2O national",
        100 * ges["Energie"][gaz_n2o] / ges["Total"][gaz_n2o],
        R["ges"]["energie_dans_n2o"], tol=0.06, unite="%")

# =============================================================== 10. températures
tmax = defaultdict(list)
mois_max = defaultdict(list)
with open(RAW / "observationdata-yvlucze.csv", encoding="utf-8-sig", newline="") as f:
    for ligne in csv.DictReader(f):
        lib = ligne["libellés"].strip().strip('"')
        if "maximal" not in lib:
            continue
        ville = ligne["villes"].strip().strip('"')
        val = float(ligne["Value"])
        tmax[ville].append(val)
        mois = int(ligne["Date"].split("M")[1])
        mois_max[mois].append(val)

moy = {v: sum(x) / len(x) for v, x in tmax.items()}
verifie("Amplitude thermique entre stations",
        max(moy.values()) - min(moy.values()), R["climat"]["gradient"],
        tol=0.001, unite="°C")
verifie("Station la plus chaude (valeur)", max(moy.values()),
        R["climat"]["t_chaude"], tol=0.001, unite="°C")
verifie("Station la plus fraîche (valeur)", min(moy.values()),
        R["climat"]["t_froide"], tol=0.001, unite="°C")

moy_mois = {m: sum(x) / len(x) for m, x in mois_max.items()}
pic = max(moy_mois, key=moy_mois.get)
verifie("Mois le plus chaud (numéro)", float(pic),
        float(R["climat"]["mois_chaud"]), tol=0, unite="")
verifie("Température du mois le plus chaud", moy_mois[pic],
        R["climat"]["t_mois_chaud"], tol=0.01, unite="°C")

# =============================================================== 11. les forêts
with open(RAW / "file-zones-protegees-forets-classees-23-12-2024-09-53-17.csv",
          encoding="utf-8-sig", newline="") as f:
    lignes_forets = [l for l in csv.DictReader(f) if l.get("geometry", "").strip()]
verifie("Nombre de forêts classées analysées", float(len(lignes_forets)),
        float(R["forets"]["nb"]), tol=0, unite="")

# =============================================================== 12. cohérence
# les deux villes citées comme extrêmes doivent être celles des données
ville_chaude = max(moy, key=moy.get)
ville_froide = min(moy, key=moy.get)
coherence = [
    ("Station la plus chaude (nom)", ville_chaude, R["climat"]["ville_chaude"]),
    ("Station la plus fraîche (nom)", ville_froide, R["climat"]["ville_froide"]),
]

# =============================================================== affichage
largeur = max(len(l) for _, l, _, _, _ in resultats)
n_ok = 0
for ok, lib, attendu, obtenu, unite in resultats:
    marque = "OK  " if ok else "ECART"
    n_ok += ok
    print(f"  [{marque}] {lib:<{largeur}}  brut = {attendu:>14,.4f} {unite:<9}"
          f" publie = {obtenu:>14,.4f}")

print()
for lib, brut, publie in coherence:
    ok = brut == publie
    n_ok += ok
    resultats.append((ok, lib, None, None, ""))
    print(f"  [{'OK  ' if ok else 'ECART'}] {lib:<{largeur}}  brut = {brut:>14}"
          f"            publie = {publie:>14}")

echecs = [r for r in resultats if not r[0]]
print()
print("=" * 78)
print(f"  {n_ok}/{len(resultats)} chiffres vérifiés conformes aux fichiers sources.")
if echecs:
    print(f"  {len(echecs)} ECART(S) :")
    for _, lib, *_ in echecs:
        print(f"     - {lib}")
print("=" * 78)
sys.exit(1 if echecs else 0)

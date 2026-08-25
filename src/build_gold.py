"""
================================================================================
Défi 2 — Énergie, Climat & Forêts au Togo
Pipeline unique bronze (data/raw) -> gold (data/gold)
================================================================================
Lancement (depuis la racine du projet) :
    python src/build_gold.py

Principes :
- chemins relatifs au dépôt (reproductible sous Windows / Linux / macOS)
- aucun chiffre inventé : toute valeur vient des 6 jeux de données du défi,
  à la seule exception des coordonnées des 10 stations météo (apport externe
  documenté dans docs/sources.md)
- les correctifs qualité sont explicites et tracés dans le journal de sortie
================================================================================
"""
from pathlib import Path
import json
import unicodedata

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
GOLD = ROOT / "data" / "gold"
GOLD.mkdir(parents=True, exist_ok=True)

LOG = []


def log(msg=""):
    print(msg)
    LOG.append(str(msg))


def find(pattern):
    """Retrouve un fichier brut par motif (les noms sont longs et datés)."""
    hits = sorted(RAW.glob(pattern))
    if not hits:
        raise FileNotFoundError(f"Aucun fichier {pattern} dans {RAW}")
    return hits[0]


# =============================================================================
# 1. BANQUE MONDIALE — séries nationales
# =============================================================================
log("=" * 78)
log("1. INDICATEURS BANQUE MONDIALE")
log("=" * 78)

wb = pd.read_csv(find("indicators-tgo.csv"), encoding="utf-8-sig")
wb = wb[wb["Country ISO3"] == "TGO"].copy()          # retire la ligne de tags HXL
wb["Year"] = pd.to_numeric(wb["Year"], errors="coerce")
wb["Value"] = pd.to_numeric(wb["Value"], errors="coerce")
wb = wb.dropna(subset=["Year"])
avant = len(wb)
wb = wb.drop_duplicates(subset=["Indicator Code", "Year"])
log(f"   dédoublonnage (Indicator Code, Year) : {avant} -> {len(wb)} lignes "
    f"({100*(avant-len(wb))/avant:.0f} % de doublons stricts supprimés)")


def serie(code):
    d = wb[wb["Indicator Code"] == code].dropna(subset=["Value"]).sort_values("Year")
    return {int(y): float(v) for y, v in zip(d["Year"], d["Value"])}


INDICS = {
    # accès
    "elec_total":     "EG.ELC.ACCS.ZS",
    "elec_rural":     "EG.ELC.ACCS.RU.ZS",
    "elec_urbain":    "EG.ELC.ACCS.UR.ZS",
    "cuisson_total":  "EG.CFT.ACCS.ZS",
    "cuisson_rural":  "EG.CFT.ACCS.RU.ZS",
    "cuisson_urbain": "EG.CFT.ACCS.UR.ZS",
    # combustibles de cuisson (enquêtes ménages 2014 & 2017)
    "bois":           "SG.COK.WOOD.ZS",
    "charbon":        "SG.COK.CHCO.ZS",
    "gpl":            "SG.COK.LPGN.ZS",
    "elec_cuisson":   "SG.COK.ELEC.ZS",
    # forêt
    "foret_pct":      "AG.LND.FRST.ZS",
    "foret_km2":      "AG.LND.FRST.K2",
    # mix énergétique
    "renouv":         "EG.FEC.RNEW.ZS",
    # population
    "pop_totale":     "SP.POP.TOTL",
    "pop_rurale":     "SP.RUR.TOTL",
    "pop_urbaine":    "SP.URB.TOTL",
    "pop_rurale_pct": "SP.RUR.TOTL.ZS",
    # santé / pollution de l'air (impact de la cuisson au bois)
    "pm25":           "EN.ATM.PM25.MC.M3",
    "mortalite_air":  "SH.STA.AIRP.P5",
    # contexte
    "pib_hab":        "NY.GDP.PCAP.CD",
}
series = {k: serie(c) for k, c in INDICS.items()}
for k, s in series.items():
    if not s:
        log(f"   [!] série vide : {k} ({INDICS[k]})")

# ---------------------------------------------------------------- fiabilité
# Objectif « mesurer la fiabilité du réseau (coupures) ».
# Source : Enterprise Surveys Banque Mondiale, deux vagues (2009, 2016).
FIAB = {
    "coupures_mois":   ("IC.ELC.OUTG",     "Coupures par mois (entreprises)",        "coupures/mois"),
    "part_touchees":   ("IC.ELC.OUTG.ZS",  "Entreprises subissant des coupures",     "% des entreprises"),
    "pertes_ca":       ("IC.FRM.OUTG.ZS",  "Chiffre d'affaires perdu (touchées)",    "% du CA"),
    "delai_raccord":   ("IC.ELC.DURS",     "Délai d'obtention d'un raccordement",    "jours"),
    "demarches_jours": ("IC.ELC.TIME",     "Temps réglementaire de raccordement",    "jours"),
}
fiabilite = {}
for k, (code, lib, unite) in FIAB.items():
    s = serie(code)
    fiabilite[k] = {"code": code, "libelle": lib, "unite": unite,
                    "valeurs": {str(y): v for y, v in s.items()}}
    if s:
        log(f"   fiabilité {k:16s} {sorted(s.items())}")

# =============================================================================
# 2. GES 2018 — secteur x gaz
# =============================================================================
log("")
log("=" * 78)
log("2. INVENTAIRE GES 2018 (secteur x gaz)")
log("=" * 78)

ges = pd.read_csv(find("observationdata-xorttne.csv"))
ges.columns = [c.strip().strip('"') for c in ges.columns]
for c in ("secteur", "type"):
    ges[c] = ges[c].astype(str).str.strip().str.strip('"')
ges["Value"] = pd.to_numeric(ges["Value"], errors="coerce")

# libellés courts (le fichier source contient une coquille : "mnooxydes d'azote")
GAZ = {
    "Dioxyde de carbone (CO2)": "CO2",
    "Méthane(CH4)": "CH4",
    "mnooxydes d’azote (N2O)": "N2O",
    "mnooxydes d'azote (N2O)": "N2O",
}
SECT = {
    "Energie": "Énergie",
    "Procédés Industriels et Utilisation des Produits (PIUP)": "Industrie (PIUP)",
    "Agriculture, Foresterie et autres Affectations des Terres (AFAT)": "Agriculture & forêts (AFAT)",
    "Déchets": "Déchets",
    "Total": "Total",
}
ges["gaz"] = ges["type"].map(GAZ).fillna(ges["type"])
ges["secteur_court"] = ges["secteur"].map(SECT).fillna(ges["secteur"])

tot_national = float(ges[(ges["secteur"] == "Total") & (ges["type"] == "Total")]["Value"].iloc[0])

# --- totaux par secteur
ges_sect = ges[(ges["type"] == "Total") & (ges["secteur"] != "Total")][
    ["secteur", "secteur_court", "Value"]].copy()
ges_sect["part_%"] = 100 * ges_sect["Value"] / tot_national
ges_sect = ges_sect.sort_values("Value", ascending=False)
log(f"   total national 2018 : {tot_national:,.0f} Gg")
for _, r in ges_sect.iterrows():
    log(f"   {r['secteur_court']:28s} {r['Value']:10,.1f} Gg  ({r['part_%']:5.1f} %)")

# --- matrice secteur x gaz + part de chaque secteur DANS chaque gaz
ges_gaz = ges[(ges["type"] != "Total") & (ges["secteur"] != "Total")][
    ["secteur_court", "gaz", "Value"]].copy()
tot_gaz = ges[(ges["secteur"] == "Total") & (ges["type"] != "Total")].set_index("gaz")["Value"]
ges_gaz["part_du_gaz_%"] = ges_gaz.apply(
    lambda r: 100 * r["Value"] / tot_gaz[r["gaz"]] if tot_gaz.get(r["gaz"], 0) else np.nan, axis=1)
ges_gaz["part_du_secteur_%"] = ges_gaz.groupby("secteur_court")["Value"].transform(
    lambda s: 100 * s / s.sum())

log("")
log("   Lecture croisée — part de chaque secteur DANS chaque gaz :")
piv = ges_gaz.pivot(index="secteur_court", columns="gaz", values="part_du_gaz_%").round(1)
log(piv.to_string())
log("   -> l'Énergie ne pèse que "
    f"{ges_sect.set_index('secteur_court').loc['Énergie','part_%']:.1f} % du total, mais "
    f"{piv.loc['Énergie','CH4']:.0f} % du méthane et {piv.loc['Énergie','N2O']:.0f} % du N2O "
    "(combustion de biomasse domestique).")

# =============================================================================
# 3. CO2 du secteur énergie — série longue
# =============================================================================
co2 = pd.read_csv(find("emissions-*co2*.csv"), encoding="utf-8-sig")
co2 = co2.dropna(subset=["value"])[["date", "value"]].sort_values("date")
co2_energie = {int(d): float(v) for d, v in zip(co2["date"], co2["value"])}

# =============================================================================
# 4. TEMPÉRATURES — 10 stations, mensuel 2013-2019
# =============================================================================
log("")
log("=" * 78)
log("4. TEMPÉRATURES (10 stations, mensuel 2013-2019)")
log("=" * 78)

tp = pd.read_csv(find("observationdata-yvlucze.csv"))
tp.columns = [c.strip().strip('"') for c in tp.columns]
for c in ("libellés", "villes", "Date"):
    tp[c] = tp[c].astype(str).str.strip().str.strip('"')
tp["Value"] = pd.to_numeric(tp["Value"], errors="coerce")
tp["annee"] = tp["Date"].str.slice(0, 4).astype(int)
tp["mois"] = tp["Date"].str.split("M").str[1].astype(int)
tp["mesure"] = np.where(tp["libellés"].str.contains("maximal"), "t_max", "t_min")

mensuel = (tp.pivot_table(index=["villes", "annee", "mois"], columns="mesure",
                          values="Value", aggfunc="mean")
             .reset_index().rename(columns={"villes": "ville"}))
mensuel["amplitude"] = mensuel["t_max"] - mensuel["t_min"]
log(f"   {len(mensuel)} observations ville x mois, "
    f"{mensuel['annee'].min()}-{mensuel['annee'].max()}, "
    f"{mensuel['ville'].nunique()} stations")

# profil moyen par ville
prof = mensuel.groupby("ville")[["t_max", "t_min"]].mean()
prof["amplitude"] = prof["t_max"] - prof["t_min"]

# saisonnalité nationale : mois le plus chaud
sais = mensuel.groupby("mois")[["t_max", "t_min"]].mean().round(2)
mois_chaud = int(sais["t_max"].idxmax())
MOIS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
           "juil.", "août", "sept.", "oct.", "nov.", "déc."]
log(f"   pic thermique national : {MOIS_FR[mois_chaud-1]} "
    f"({sais['t_max'].max():.1f} °C de max moyen) ; "
    f"creux : {MOIS_FR[int(sais['t_max'].idxmin())-1]} ({sais['t_max'].min():.1f} °C)")

# =============================================================================
# 5. COORDONNÉES DES 10 STATIONS (apport externe documenté)
# =============================================================================
VILLES = {
    "Lomé":        (6.1725,  1.2314, "Maritime", "Golfe"),
    "Tabligbo":    (6.5836,  1.5019, "Maritime", "Yoto"),
    "Kouma konda": (6.9500,  0.5833, "Plateaux", "Kloto"),
    "Atakpamé":    (7.5333,  1.1333, "Plateaux", "Ogou"),
    "Sotouboua":   (8.5667,  0.9833, "Centrale", "Sotouboua"),
    "Sokodé":      (8.9833,  1.1333, "Centrale", "Tchaoudjo"),
    "Niamtougou":  (9.7667,  1.1000, "Kara",     "Doufelgou"),
    "Kara":        (9.5511,  1.1861, "Kara",     "Kozah"),
    "Mango":       (10.3592, 0.4711, "Savanes",  "Oti"),
    "Dapaong":     (10.8622, 0.2072, "Savanes",  "Tône"),
}
villes = pd.DataFrame([(v, la, lo, rg, pf) for v, (la, lo, rg, pf) in VILLES.items()],
                      columns=["ville", "lat", "lon", "region", "prefecture"])
villes = villes.merge(prof.reset_index(), on="ville", how="left")
assert villes["t_max"].notna().all(), "station météo non appariée aux coordonnées"
villes["stress_thermique"] = ((villes["t_max"] - villes["t_max"].min()) /
                              (villes["t_max"].max() - villes["t_max"].min()))
villes = villes.sort_values("lat")
villes.to_csv(GOLD / "villes_meteo.csv", index=False)
mensuel.to_csv(GOLD / "temperatures_mensuelles.csv", index=False)

grad = villes["t_max"].max() - villes["t_max"].min()
_f, _c = villes["t_max"].idxmin(), villes["t_max"].idxmax()
log(f"   amplitude thermique entre stations : {grad:.1f} °C "
    f"({villes.loc[_f,'ville']} {villes.loc[_f,'t_max']:.1f} °C -> "
    f"{villes.loc[_c,'ville']} {villes.loc[_c,'t_max']:.1f} °C)")
log(f"   gradient latitudinal Sud->Nord : {villes.iloc[0]['ville']} "
    f"{villes.iloc[0]['t_max']:.1f} °C -> {villes.iloc[-1]['ville']} "
    f"{villes.iloc[-1]['t_max']:.1f} °C")

# =============================================================================
# 6. LES 53 FORÊTS CLASSÉES — indice de vulnérabilité
# =============================================================================
log("")
log("=" * 78)
log("6. FORÊTS CLASSÉES — indice de vulnérabilité")
log("=" * 78)

fg = pd.read_csv(find("file-zones-protegees-forets-classees-*.csv"), encoding="utf-8-sig")
fg["geometry"] = fg["geometry"].apply(
    lambda g: wkt.loads(g) if isinstance(g, str) and g.strip() else None)
gdf = gpd.GeoDataFrame(fg, geometry="geometry", crs="EPSG:4326")
gdf = gdf[gdf.geometry.notna()].copy()
log(f"   {len(gdf)} polygones valides")

gdf_m = gdf.to_crs(32631)                      # UTM 31N — surfaces et distances en mètres
gdf["surface_ha"] = gdf_m.geometry.area / 10_000
cent_m = gdf_m.geometry.centroid
cent_wgs = cent_m.to_crs(4326)
gdf["clon"] = cent_wgs.x.values
gdf["clat"] = cent_wgs.y.values

# --- distance au pôle urbain le plus proche (enclavement)
vg = gpd.GeoDataFrame(villes, geometry=gpd.points_from_xy(villes["lon"], villes["lat"]),
                      crs="EPSG:4326").to_crs(32631).reset_index(drop=True)
dists, near = [], []
for pt in cent_m:
    d = vg.geometry.distance(pt) / 1000
    dists.append(float(d.min()))
    near.append(vg.loc[d.idxmin(), "ville"])
gdf["dist_km"] = dists
gdf["ville_proche"] = near
gdf = gdf.merge(villes[["ville", "t_max", "stress_thermique"]].rename(
    columns={"ville": "ville_proche", "t_max": "t_max_ville"}), on="ville_proche", how="left")

# --- surfaces douteuses : polygones < 10 ha (numérisation partielle)
gdf["surface_incertaine"] = gdf["surface_ha"] < 10
log(f"   surfaces incertaines (<10 ha) : {int(gdf['surface_incertaine'].sum())}/53 "
    f"-> flag + valeur neutre dans l'indice (ni pénalisées, ni survalorisées)")

# --- ancienneté : conservée en descriptif, hors score (16 valeurs manquantes)
def parse_year(x):
    try:
        y = int(str(x).strip())
        return y if 1800 < y < 2030 else np.nan
    except Exception:
        return np.nan


gdf["annee_creation"] = gdf["etab_creation_date"].apply(parse_year)
log(f"   année de classement inconnue (Nsp/Nps/Jadis) : "
    f"{int(gdf['annee_creation'].isna().sum())}/53 -> hors score, aucune imputation")


def nrm(s):
    return (s - s.min()) / (s.max() - s.min())


gdf["enclavement_norm"] = nrm(gdf["dist_km"])
s_ok = gdf.loc[~gdf["surface_incertaine"], "surface_ha"]
lo, hi = np.log1p(s_ok.min()), np.log1p(s_ok.max())
gdf["surface_norm"] = gdf.apply(
    lambda r: 0.5 if r["surface_incertaine"] else (np.log1p(r["surface_ha"]) - lo) / (hi - lo),
    axis=1)
gdf["stress_norm"] = nrm(gdf["t_max_ville"])

POIDS = {"enclavement_norm": 0.40, "surface_norm": 0.35, "stress_norm": 0.25}
gdf["score"] = sum(gdf[c] * w for c, w in POIDS.items()) * 100
gdf = gdf.sort_values("score", ascending=False).reset_index(drop=True)
gdf["rang"] = range(1, len(gdf) + 1)

log("")
log("   TOP 10 (pondération de référence 0.40 / 0.35 / 0.25) :")
for _, r in gdf.head(10).iterrows():
    log(f"   {r['rang']:2d}. {r['etab_nom'][:38]:38s} {r['region_nom_bdd']:9s} "
        f"{r['surface_ha']:9,.0f} ha  {r['dist_km']:5.1f} km  score {r['score']:.1f}")

# --- analyse de sensibilité : le classement de tête tient-il ?
grilles = [(.30, .40, .30), (.35, .35, .30), (.40, .35, .25), (.45, .30, .25), (.50, .30, .20)]
rangs = {}
for e, s, t in grilles:
    sc = (gdf["enclavement_norm"] * e + gdf["surface_norm"] * s + gdf["stress_norm"] * t) * 100
    rk = sc.rank(ascending=False, method="min")
    for i, nm in enumerate(gdf["etab_nom"]):
        rangs.setdefault(nm, []).append(int(rk.iloc[i]))
rob = pd.DataFrame([{"foret": k, "rang_min": min(v), "rang_max": max(v),
                     "toujours_top10": max(v) <= 10, "jamais_top10": min(v) > 10}
                    for k, v in rangs.items()])
nb_rob = int(rob["toujours_top10"].sum())
log(f"\n   robustesse : {nb_rob} forêts restent dans le top 10 sur les "
    f"{len(grilles)} pondérations testées")

gdf.drop(columns=["centroid"], errors="ignore").to_csv(
    GOLD / "forets_vulnerabilite.csv", index=False)
rob.to_csv(GOLD / "forets_robustesse.csv", index=False)

# =============================================================================
# 7. REPÈRES CALCULÉS — les chiffres qui portent la décision
# =============================================================================
log("")
log("=" * 78)
log("7. REPÈRES DÉCISIONNELS (calculés, pas saisis)")
log("=" * 78)


def dernier(k):
    s = series[k]
    y = max(s)
    return y, s[y]


CIBLE = 2030
reperes = {}

# --- trajectoire électrification rurale
er = series["elec_rural"]
y0, y1 = min(er), max(er)
rythme_obs = (er[y1] - er[y0]) / (y1 - y0)
rythme_req = (100 - er[y1]) / (CIBLE - y1)
reperes["elec_rural"] = {
    "annee": y1, "valeur": er[y1],
    "annee_depart": y0, "valeur_depart": er[y0],
    "rythme_observe": rythme_obs, "rythme_requis_2030": rythme_req,
    "facteur_acceleration": rythme_req / rythme_obs,
    "annee_atteinte_tendanciel": y1 + (100 - er[y1]) / rythme_obs,
}
log(f"   Électrification rurale : {er[y1]:.1f} % en {y1} "
    f"(+{rythme_obs:.2f} pt/an depuis {y0})")
log(f"     -> il faudrait +{rythme_req:.1f} pt/an pour 2030 = "
    f"x{rythme_req/rythme_obs:.0f} le rythme actuel")
log(f"     -> au rythme observé, l'accès universel rural tomberait en "
    f"{reperes['elec_rural']['annee_atteinte_tendanciel']:.0f}")

# --- écart ville / campagne
eu = series["elec_urbain"]
reperes["ecart_urbain_rural"] = {"annee": y1, "valeur": eu[y1] - er[y1],
                                 "urbain": eu[y1], "rural": er[y1]}
log(f"   Écart ville/campagne : {eu[y1]-er[y1]:.0f} points ({eu[y1]:.0f} % vs {er[y1]:.0f} %)")

# --- population rurale privée d'électricité
pr = series["pop_rurale"]
an_pop = max(a for a in pr if a <= y1)
sans_elec = pr[an_pop] * (1 - er[y1] / 100)
reperes["ruraux_sans_elec"] = {"annee": y1, "personnes": sans_elec,
                               "pop_rurale": pr[an_pop], "annee_pop": an_pop}
log(f"   Ruraux sans électricité : {sans_elec/1e6:.2f} million de personnes "
    f"({pr[an_pop]/1e6:.2f} M de ruraux x {100-er[y1]:.0f} %)")

# --- cuisson propre : le vrai point noir
cr = series["cuisson_rural"]
cy0, cy1 = min(cr), max(cr)
c_rythme = (cr[cy1] - cr[cy0]) / (cy1 - cy0)
reperes["cuisson_rurale"] = {
    "annee": cy1, "valeur": cr[cy1], "rythme_observe": c_rythme,
    "rythme_requis_2030": (100 - cr[cy1]) / (CIBLE - cy1),
}
log(f"   Cuisson propre rurale : {cr[cy1]:.1f} % en {cy1} "
    f"(+{c_rythme:.2f} pt/an — quasi nul)")

# --- combustibles : le bois PROGRESSE entre les deux enquêtes
bois, charbon, gpl = series["bois"], series["charbon"], series["gpl"]
a, b = sorted(bois)[0], sorted(bois)[-1]
reperes["combustibles"] = {
    "annees": [a, b],
    "bois": [bois[a], bois[b]], "charbon": [charbon[a], charbon[b]], "gpl": [gpl[a], gpl[b]],
    "biomasse": [bois[a] + charbon[a], bois[b] + charbon[b]],
}
log(f"   Combustibles ménages {a} -> {b} : bois {bois[a]:.1f} -> {bois[b]:.1f} %, "
    f"charbon {charbon[a]:.1f} -> {charbon[b]:.1f} %, GPL {gpl[a]:.1f} -> {gpl[b]:.1f} %")
log(f"     -> biomasse totale {bois[a]+charbon[a]:.1f} -> {bois[b]+charbon[b]:.1f} % : "
    "la dépendance ne recule pas")

# --- le piège du « renouvelable »
rn = series["renouv"]
ry = max(rn)
reperes["renouvelable_piege"] = {
    "annee": ry, "part_renouvelable": rn[ry],
    "part_cuisson_propre": series["cuisson_total"][max(series["cuisson_total"])],
    "annee_cuisson": max(series["cuisson_total"]),
}
log(f"   « Renouvelable » {rn[ry]:.1f} % de l'énergie finale en {ry}, "
    f"mais seulement {reperes['renouvelable_piege']['part_cuisson_propre']:.1f} % "
    "des ménages cuisinent proprement -> ce renouvelable EST le bois de feu")

# --- déforestation
fk = series["foret_km2"]
fy0, fy1 = min(fk), max(fk)
perte_km2 = fk[fy0] - fk[fy1]
reperes["deforestation"] = {
    "annee_debut": fy0, "annee_fin": fy1,
    "km2_debut": fk[fy0], "km2_fin": fk[fy1],
    "perte_km2": perte_km2, "perte_ha": perte_km2 * 100,
    "perte_ha_par_an": perte_km2 * 100 / (fy1 - fy0),
    "perte_pct_relative": 100 * perte_km2 / fk[fy0],
    "pct_debut": series["foret_pct"][fy0], "pct_fin": series["foret_pct"][fy1],
}
log(f"   Déforestation {fy0}-{fy1} : {fk[fy0]:,.0f} -> {fk[fy1]:,.0f} km² "
    f"= -{perte_km2:,.0f} km² (-{100*perte_km2/fk[fy0]:.1f} %)")
log(f"     -> {perte_km2*100/(fy1-fy0):,.0f} hectares perdus par an, en moyenne")

# --- fiabilité : synthèse
co = {int(y): v for y, v in serie("IC.ELC.OUTG").items()}
pt_ = {int(y): v for y, v in serie("IC.ELC.OUTG.ZS").items()}
if co and pt_:
    ay = max(co)
    reperes["fiabilite"] = {
        "annee": ay, "coupures_mois": co[ay], "part_entreprises": pt_[max(pt_)],
        "annee_ref": min(co), "coupures_mois_ref": co[min(co)],
        "part_entreprises_ref": pt_[min(pt_)],
    }
    log(f"   Fiabilité : {co[ay]:.1f} coupures/mois en {ay} "
        f"(vs {co[min(co)]:.1f} en {min(co)}), "
        f"{pt_[max(pt_)]:.1f} % des entreprises touchées")

# --- santé : coût humain de la cuisson au bois
pm = series["pm25"]
reperes["sante"] = {
    "pm25": pm[max(pm)], "annee_pm25": max(pm), "seuil_oms": 5.0,
    "ratio_oms": pm[max(pm)] / 5.0,
    "mortalite": series["mortalite_air"][max(series["mortalite_air"])],
    "annee_mortalite": max(series["mortalite_air"]),
}
log(f"   Air : PM2,5 = {pm[max(pm)]:.1f} µg/m³ ({max(pm)}), "
    f"soit {pm[max(pm)]/5:.0f} x la ligne directrice OMS (5 µg/m³)")
log(f"   Mortalité attribuée à la pollution de l'air : "
    f"{reperes['sante']['mortalite']:.0f} pour 100 000 hab. "
    f"({reperes['sante']['annee_mortalite']})")

# --- climat / énergie
i_froid = villes["t_max"].idxmin()
i_chaud = villes["t_max"].idxmax()
reperes["climat"] = {
    "gradient": float(grad),
    "ville_froide": villes.loc[i_froid, "ville"], "t_froide": float(villes.loc[i_froid, "t_max"]),
    "ville_chaude": villes.loc[i_chaud, "ville"], "t_chaude": float(villes.loc[i_chaud, "t_max"]),
    "t_sud": float(villes.iloc[0]["t_max"]), "ville_sud": villes.iloc[0]["ville"],
    "t_nord": float(villes.iloc[-1]["t_max"]), "ville_nord": villes.iloc[-1]["ville"],
    "mois_froid": int(sais["t_max"].idxmin()),
    "mois_froid_nom": MOIS_FR[int(sais["t_max"].idxmin()) - 1],
    "t_mois_froid": float(sais["t_max"].min()),
    "mois_chaud": mois_chaud, "mois_chaud_nom": MOIS_FR[mois_chaud - 1],
    "t_mois_chaud": float(sais["t_max"].max()),
    "amplitude_max_ville": villes.loc[villes["amplitude"].idxmax(), "ville"],
    "amplitude_max": float(villes["amplitude"].max()),
}

reperes["ges"] = {
    "total_gg": tot_national,
    "part_energie": float(ges_sect.set_index("secteur_court").loc["Énergie", "part_%"]),
    "part_afat": float(ges_sect.set_index("secteur_court").loc["Agriculture & forêts (AFAT)", "part_%"]),
    "energie_dans_ch4": float(piv.loc["Énergie", "CH4"]),
    "energie_dans_n2o": float(piv.loc["Énergie", "N2O"]),
}

reperes["forets"] = {
    "nb": int(len(gdf)),
    "surface_totale_ha": float(gdf.loc[~gdf["surface_incertaine"], "surface_ha"].sum()),
    "nb_incertaines": int(gdf["surface_incertaine"].sum()),
    "nb_robustes": nb_rob,
    "top1": gdf.iloc[0]["etab_nom"], "top1_score": float(gdf.iloc[0]["score"]),
    "dist_mediane": float(gdf["dist_km"].median()),
}

# =============================================================================
# 8. ÉCRITURE
# =============================================================================
payload = {
    "series": {k: {str(y): v for y, v in s.items()} for k, s in series.items()},
    "co2_energie": {str(y): v for y, v in co2_energie.items()},
    "ges_secteur": ges_sect.to_dict("records"),
    "ges_gaz": ges_gaz.to_dict("records"),
    "ges_total_national": tot_national,
    "fiabilite": fiabilite,
    "saisonnalite": sais.reset_index().to_dict("records"),
    "reperes": reperes,
}
with open(GOLD / "diagnostic_national.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

with open(GOLD / "journal_construction.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))

log("")
log("=" * 78)
log(f"[OK] gold écrit dans {GOLD}")
for p in sorted(GOLD.glob("*")):
    log(f"   {p.name:34s} {p.stat().st_size/1024:8.1f} Ko")

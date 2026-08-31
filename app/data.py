"""Chargement des données gold (mises en cache) et petits helpers d'accès."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

GOLD = Path(__file__).resolve().parent.parent / "data" / "gold"


@st.cache_data(show_spinner=False)
def national():
    with open(GOLD / "diagnostic_national.json", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def verification():
    """Résultat de `src/verify.py` — l'audit qui recalcule tout depuis data/raw/.

    Le fichier est écrit par le script d'audit lui-même : si l'audit n'a jamais
    tourné, la page le dit au lieu d'afficher un chiffre rassurant sans preuve.
    """
    p = GOLD / "verification.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def forets():
    return pd.read_csv(GOLD / "forets_vulnerabilite.csv")


@st.cache_data(show_spinner=False)
def geojson_forets():
    """Polygones WKT -> FeatureCollection GeoJSON (parsé une seule fois)."""
    from shapely import wkt
    df = forets()
    feats = []
    for _, r in df.iterrows():
        try:
            geom = wkt.loads(r["geometry"])
        except Exception:
            continue
        feats.append({"type": "Feature", "id": str(r["FID"]),
                      "properties": {"nom": r["etab_nom"]},
                      "geometry": geom.__geo_interface__})
    return {"type": "FeatureCollection", "features": feats}


@st.cache_data(show_spinner=False)
def robustesse():
    return pd.read_csv(GOLD / "forets_robustesse.csv")


@st.cache_data(show_spinner=False)
def villes():
    return pd.read_csv(GOLD / "villes_meteo.csv")


@st.cache_data(show_spinner=False)
def temperatures():
    return pd.read_csv(GOLD / "temperatures_mensuelles.csv")


# ------------------------------------------------------------------ accès série
def serie(nat, cle, an_min=None, an_max=None):
    """Série {année: valeur} -> DataFrame trié, filtrable sur une période."""
    s = nat["series"].get(cle, {})
    df = pd.DataFrame([(int(a), v) for a, v in s.items()], columns=["annee", "valeur"])
    df = df.sort_values("annee")
    if an_min is not None:
        df = df[df["annee"] >= an_min]
    if an_max is not None:
        df = df[df["annee"] <= an_max]
    return df.reset_index(drop=True)


def dernier(nat, cle):
    """(année, valeur) du dernier point disponible."""
    df = serie(nat, cle)
    return int(df["annee"].iloc[-1]), float(df["valeur"].iloc[-1])


def fiab(nat, cle):
    """Série d'un indicateur de fiabilité -> DataFrame (annee, valeur) + métadonnées."""
    bloc = nat["fiabilite"][cle]
    df = pd.DataFrame([(int(a), v) for a, v in bloc["valeurs"].items()],
                      columns=["annee", "valeur"]).sort_values("annee").reset_index(drop=True)
    return df, bloc["libelle"], bloc["unite"], bloc["code"]

"""Chargement des données gold (mises en cache) et petits helpers d'accès."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

GOLD = Path(__file__).resolve().parent.parent / "data" / "gold"


def _empreinte(nom):
    """Date de dernière écriture d'un fichier gold, en nanosecondes.

    Elle sert de clé de cache. Sans elle, régénérer `data/gold/` pendant que
    l'application tourne ne change rien à l'écran : Streamlit continue de
    servir le contenu mémorisé, et une clé ajoutée par le pipeline provoque un
    KeyError sur un fichier qui, sur le disque, la contient bel et bien.
    """
    p = GOLD / nom
    return p.stat().st_mtime_ns if p.exists() else 0


@st.cache_data(show_spinner=False)
def _lire_national(_empreinte_fichier):
    with open(GOLD / "diagnostic_national.json", encoding="utf-8") as f:
        return json.load(f)


def national():
    return _lire_national(_empreinte("diagnostic_national.json"))


@st.cache_data(show_spinner=False)
def _lire_forets(_empreinte_fichier):
    return pd.read_csv(GOLD / "forets_vulnerabilite.csv")


def forets():
    return _lire_forets(_empreinte("forets_vulnerabilite.csv"))


@st.cache_data(show_spinner=False)
def _lire_geojson(_empreinte_fichier):
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


def geojson_forets():
    return _lire_geojson(_empreinte("forets_vulnerabilite.csv"))


@st.cache_data(show_spinner=False)
def _lire_robustesse(_empreinte_fichier):
    return pd.read_csv(GOLD / "forets_robustesse.csv")


def robustesse():
    return _lire_robustesse(_empreinte("forets_robustesse.csv"))


@st.cache_data(show_spinner=False)
def _lire_villes(_empreinte_fichier):
    return pd.read_csv(GOLD / "villes_meteo.csv")


def villes():
    return _lire_villes(_empreinte("villes_meteo.csv"))


@st.cache_data(show_spinner=False)
def _lire_temperatures(_empreinte_fichier):
    return pd.read_csv(GOLD / "temperatures_mensuelles.csv")


def temperatures():
    return _lire_temperatures(_empreinte("temperatures_mensuelles.csv"))


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

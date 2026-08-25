"""
Tableau de bord — Énergie, Climat & Forêts au Togo (Défi 2).
Point d'entrée : configuration, navigation et filtres globaux.

    streamlit run app/Accueil.py
"""
from pathlib import Path

import streamlit as st

ARMOIRIES = Path(__file__).resolve().parent / "assets" / "armoiries_togo.svg"

st.set_page_config(page_title="Togo · Énergie, Climat & Forêts",
                   page_icon=str(ARMOIRIES), layout="wide",
                   initial_sidebar_state="expanded")

from theme import inject_css, tricolore, armoiries_uri   # noqa: E402

inject_css()

# Icônes Material Symbols plutôt qu'émojis : monochromes, alignées sur la
# typographie, elles se fondent dans l'interface au lieu de la ponctuer.
PAGES = [
    st.Page("views/synthese.py",     title="Synthèse",
            icon=":material/dashboard:", default=True),
    st.Page("views/acces.py",        title="Accès & fiabilité",
            icon=":material/bolt:"),
    st.Page("views/cuisson.py",      title="Cuisson & forêts",
            icon=":material/local_fire_department:"),
    st.Page("views/emissions.py",    title="Émissions & climat",
            icon=":material/thermostat:"),
    st.Page("views/priorisation.py", title="Où agir",
            icon=":material/map:"),
    st.Page("views/plan.py",         title="Plan d'action",
            icon=":material/checklist:"),
]
nav = st.navigation(PAGES, position="sidebar")

# ---------------------------------------------------------------- barre latérale
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:13px;padding:2px 0 4px">'
        f'<img src="{armoiries_uri()}" alt="Armoiries de la République togolaise" '
        f'style="height:52px;width:auto;flex:0 0 auto;'
        f'filter:drop-shadow(0 1px 3px rgba(0,0,0,.28))">'
        f'<div><div style="font-size:15.5px;font-weight:800;color:#fff;'
        f'line-height:1.22;letter-spacing:-.2px">Énergie, Climat<br>'
        f'&amp; Forêts au Togo</div>'
        f'<div style="font-size:11px;color:#A9D3BC;margin-top:4px;'
        f'letter-spacing:.3px">Défi 2 · datalab.gouv.tg</div></div></div>'
        f'{tricolore(".85")}', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10.5px;font-weight:800;letter-spacing:1.2px;'
                'color:#A9D3BC;text-transform:uppercase;margin:16px 0 2px">'
                'Filtre global</div>', unsafe_allow_html=True)
    periode = st.slider("Période des séries temporelles", 1990, 2023, (1998, 2023),
                        help="S'applique à toutes les courbes historiques du tableau de bord.")
    st.session_state["an_min"], st.session_state["an_max"] = periode

    st.caption("Les filtres propres à chaque analyse se trouvent en haut de page.")

    st.markdown(
        f'{tricolore(".5")}<div style="font-size:10.5px;color:#8FC0A6;line-height:1.55">'
        f'6 jeux de données du Défi 2.<br>Pipeline reproductible :<br>'
        f'<code style="color:#CFE8DA;background:transparent;padding:0">'
        f'python src/build_gold.py</code><br>'
        f'<span style="color:#7FB396">Audit des chiffres :</span><br>'
        f'<code style="color:#CFE8DA;background:transparent;padding:0">'
        f'python src/verify.py</code></div>',
        unsafe_allow_html=True)

nav.run()

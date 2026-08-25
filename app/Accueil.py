"""
Tableau de bord — Énergie, Climat & Forêts au Togo.
Point d'entrée : configuration, navigation et filtre global.

    streamlit run app/Accueil.py
"""
from pathlib import Path

import streamlit as st

ARMOIRIES = Path(__file__).resolve().parent / "assets" / "armoiries_togo.svg"

st.set_page_config(page_title="Togo · Énergie, Climat & Forêts",
                   page_icon=str(ARMOIRIES), layout="wide",
                   initial_sidebar_state="expanded")

from theme import inject_css, logo_menu   # noqa: E402

inject_css()
# `st.logo` est le seul emplacement qui se rend au-dessus des liens de
# navigation : les armoiries et l'intitulé y tiennent en une seule image.
st.logo(logo_menu(), size="large")

# Les intitulés de pages annoncent une trouvaille, pas un thème : un décideur
# clique sur « La marmite et la forêt », pas sur « Objectif 2 ».
PAGES = [
    st.Page("views/synthese.py",     title="Vue d'ensemble",
            icon=":material/dashboard:", default=True),
    st.Page("views/acces.py",        title="La fracture électrique",
            icon=":material/bolt:"),
    st.Page("views/cuisson.py",      title="La marmite et la forêt",
            icon=":material/local_fire_department:"),
    st.Page("views/emissions.py",    title="Ce que le CO₂ cache",
            icon=":material/co2:"),
    st.Page("views/priorisation.py", title="Les forêts à sauver",
            icon=":material/forest:"),
    st.Page("views/plan.py",         title="Que faire d'ici 2030",
            icon=":material/target:"),
]
nav = st.navigation(PAGES, position="sidebar")

with st.sidebar:
    periode = st.slider("Période affichée", 1990, 2023, (1998, 2023),
                        help="S'applique à toutes les courbes historiques "
                             "du tableau de bord.")
    st.session_state["an_min"], st.session_state["an_max"] = periode
    st.caption("Chaque page a ses propres filtres, en haut de page.")

nav.run()

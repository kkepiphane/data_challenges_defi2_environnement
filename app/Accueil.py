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

# Un nom nu par entrée : dans un menu on cherche, on ne se laisse pas
# séduire. Chaque libellé nomme la pièce du dossier — le diagnostic,
# l'électrification, la cuisson, l'inventaire, les forêts, les
# recommandations — et c'est le titre de la page qui livre la trouvaille.
# Ni thème abstrait (« Objectif 2 »), ni format (« Vue d'ensemble »).
PAGES = [
    st.Page("views/synthese.py",     title="Diagnostic",
            icon=":material/dashboard:", default=True),
    st.Page("views/acces.py",        title="Électrification",
            icon=":material/bolt:"),
    st.Page("views/cuisson.py",      title="Cuisson",
            icon=":material/local_fire_department:"),
    st.Page("views/emissions.py",    title="Inventaire",
            icon=":material/co2:"),
    st.Page("views/priorisation.py", title="Forêts",
            icon=":material/forest:"),
    st.Page("views/plan.py",         title="Recommandations",
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

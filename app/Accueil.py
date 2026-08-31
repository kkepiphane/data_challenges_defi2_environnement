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
# Pas d'`icon_image` : Streamlit l'affiche aussi dans le volet déplié, où
# l'emblème seul, mis à la largeur du menu, écrase la navigation. Le cas du
# volet replié est traité dans la feuille de style.
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
    st.Page("views/donnees.py",      title="Données",
            icon=":material/rule:"),
]
nav = st.navigation(PAGES, position="sidebar")

DEFAUT_PERIODE = (1998, 2023)

with st.sidebar:
    st.markdown('<div class="repere-volet">Réglage commun à toutes les pages</div>',
                unsafe_allow_html=True)
    periode = st.slider("Période affichée", 1990, 2023, DEFAUT_PERIODE,
                        key="periode_globale",
                        help="S'applique à toutes les courbes historiques "
                             "du tableau de bord. Les réglages propres à chaque "
                             "page sont dans son bandeau « Réglages ».")
    st.session_state["an_min"], st.session_state["an_max"] = periode
    if periode != DEFAUT_PERIODE:
        st.caption(f"Période restreinte à {periode[0]}–{periode[1]} — "
                   "certaines séries peuvent être tronquées.")

    # Un tableau de bord qu'on explore accumule des réglages. Sans retour en
    # arrière, on finit par lire un écran dont on ne sait plus ce qui l'a
    # produit : le bouton rend l'état de départ à portée de main.
    if st.button("Réinitialiser tous les réglages", width="stretch",
                 help="Curseurs, filtres et sélections de toutes les pages "
                      "reviennent à leur valeur par défaut."):
        for cle in list(st.session_state.keys()):
            del st.session_state[cle]
        st.rerun()

nav.run()

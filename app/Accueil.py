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
]
nav = st.navigation(PAGES, position="sidebar")

# Les cinq régions administratives du Togo, du Sud au Nord. Elles ne
# s'appliquent qu'aux données réellement géolocalisées — les 53 forêts
# classées et les 10 stations météorologiques. L'électrification, la cuisson
# et les émissions n'existent qu'au niveau national dans les six jeux de
# données : le filtre le dit au lieu de faire semblant de les découper.
REGIONS = ["Tout le pays", "Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]
DEFAUT_PERIODE = (1998, 2023)

with st.sidebar:
    st.markdown('<div class="repere-volet">Filtres communs à toutes les pages</div>',
                unsafe_allow_html=True)
    # Un clic sur la carte ne peut pas écrire directement dans la clé du
    # sélecteur : Streamlit refuse qu'on modifie un widget déjà rendu. La page
    # dépose donc sa demande dans une clé neutre, que l'on consomme ici, avant
    # que le sélecteur n'existe.
    if "region_demandee" in st.session_state:
        st.session_state["region_globale"] = st.session_state.pop("region_demandee")

    region = st.selectbox(
        "Région", REGIONS, key="region_globale",
        help="Agit sur la carte des forêts, leur classement et les stations "
             "climatiques. Les séries nationales (accès, cuisson, émissions) "
             "n'existent pas à cette maille dans les données du défi.")
    st.session_state["region"] = region

    periode = st.slider("Période affichée", 1990, 2023, DEFAUT_PERIODE,
                        key="periode_globale",
                        help="S'applique à toutes les courbes historiques "
                             "du tableau de bord.")
    st.session_state["an_min"], st.session_state["an_max"] = periode

    if region != "Tout le pays":
        st.caption(f"**{region}** — forêts, classement et stations filtrés. "
                   "Les chiffres nationaux restent nationaux, et le signalent.")
    if st.button("Réinitialiser les filtres", width="stretch"):
        for cle in list(st.session_state.keys()):
            del st.session_state[cle]
        st.rerun()

nav.run()

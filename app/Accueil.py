"""
Tableau de bord — Énergie, Climat & Forêts au Togo (Défi 2).
Point d'entrée : configuration, navigation et filtres globaux.

    streamlit run app/Accueil.py
"""
import streamlit as st

st.set_page_config(page_title="Togo · Énergie, Climat & Forêts",
                   page_icon="🌳", layout="wide",
                   initial_sidebar_state="expanded")

from theme import inject_css, C, tricolore   # noqa: E402

inject_css()

PAGES = [
    st.Page("views/synthese.py",     title="Synthèse",             icon="🧭", default=True),
    st.Page("views/acces.py",        title="Accès & fiabilité",    icon="⚡"),
    st.Page("views/cuisson.py",      title="Cuisson & forêts",     icon="🔥"),
    st.Page("views/emissions.py",    title="Émissions & climat",   icon="🌍"),
    st.Page("views/priorisation.py", title="Où agir",              icon="🗺️"),
    st.Page("views/plan.py",         title="Plan d'action",        icon="✅"),
]
nav = st.navigation(PAGES, position="sidebar")

# ---------------------------------------------------------------- barre latérale
with st.sidebar:
    st.markdown(
        f'<div style="padding:2px 0 10px"><div style="font-size:17px;font-weight:800;'
        f'color:#fff;line-height:1.25">Énergie, Climat<br>& Forêts au Togo</div>'
        f'<div style="font-size:11.5px;color:#A9D3BC;margin-top:5px">'
        f'Défi 2 · datalab.gouv.tg</div>{tricolore(".85")}</div>',
        unsafe_allow_html=True)

    st.markdown('<div style="font-size:10.5px;font-weight:800;letter-spacing:1.2px;'
                'color:#A9D3BC;text-transform:uppercase;margin:14px 0 2px">'
                'Filtre global</div>', unsafe_allow_html=True)
    periode = st.slider("Période des séries temporelles", 1990, 2023, (1998, 2023),
                        help="S'applique à toutes les courbes historiques du tableau de bord.")
    st.session_state["an_min"], st.session_state["an_max"] = periode

    st.caption("Les filtres propres à chaque analyse se trouvent en haut de page.")

    st.markdown('<div style="margin-top:auto"></div>', unsafe_allow_html=True)
    st.markdown(
        f'{tricolore(".5")}<div style="font-size:10.5px;color:#8FC0A6;line-height:1.5">'
        f'6 jeux de données du Défi 2.<br>Pipeline reproductible :<br>'
        f'<code style="color:#CFE8DA;background:transparent;padding:0">'
        f'python src/build_gold.py</code></div>',
        unsafe_allow_html=True)

nav.run()

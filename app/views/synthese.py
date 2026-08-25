"""Synthèse — la page que lit un décideur pressé : diagnostic, preuve, décision."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   titre_carte, pied, fr)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

er, ec, rs = R["elec_rural"], R["ecart_urbain_rural"], R["ruraux_sans_elec"]
cb, df_, fi = R["combustibles"], R["deforestation"], R["fiabilite"]

banniere(
    "Synthèse décisionnelle",
    "Électrifier les campagnes sans brûler les forêts",
    "Le Togo vise l'accès universel à l'électricité en 2030. Les données du défi montrent "
    "que l'objectif ne se joue pas seulement sur le réseau : il se joue sur la cuisson des "
    "ménages, qui consomme la forêt. Diagnostic en cinq chiffres, preuve, et lieu d'action.",
    reperes=[("Accès rural", f"{er['valeur']:.0f} %"),
             ("Ménages au bois", f"{cb['biomasse'][1]:.0f} %"),
             ("Forêt / an", f"−{fr(df_['perte_ha_par_an'])} ha")])

# ------------------------------------------------------------------ chiffres clés
s_elec = list(D.serie(nat, "elec_rural")["valeur"])
s_foret = list(D.serie(nat, "foret_pct")["valeur"])
s_cuis = list(D.serie(nat, "cuisson_rural")["valeur"])
s_pop = list(D.serie(nat, "pop_rurale")["valeur"])

kpi_row([
    ("Accès rural à l'électricité", f"{er['valeur']:.0f} %",
     f"contre {ec['urbain']:.0f} % en ville en {ec['annee']} — un écart de "
     f"{ec['valeur']:.0f} points", C["energie"],
     f"+{er['rythme_observe']:.1f} pt/an", s_elec),
    ("Ruraux sans électricité", f"{rs['personnes']/1e6:.1f} M",
     f"personnes, soit {100-er['valeur']:.0f} % de la population rurale "
     f"({er['annee']})", C["risque"], None, s_pop),
    ("Ménages au bois ou au charbon", f"{cb['biomasse'][1]:.0f} %",
     f"en {cb['annees'][1]} — la dépendance n'a pas reculé depuis "
     f"{cb['annees'][0]} ({cb['biomasse'][0]:.0f} %)", C["risque"], "stable",
     cb["biomasse"]),
    ("Forêt perdue chaque année", f"{fr(df_['perte_ha_par_an'])} ha",
     f"soit −{df_['perte_pct_relative']:.0f} % du couvert entre "
     f"{df_['annee_debut']} et {df_['annee_fin']}", C["foret"], None, s_foret),
    ("Accélération requise", f"× {er['facteur_acceleration']:.0f}",
     f"pour l'accès universel rural en 2030 : +{er['rythme_requis_2030']:.1f} pt/an "
     f"au lieu de +{er['rythme_observe']:.1f}", C["risque"], "hors trajectoire",
     s_cuis),
])

st.write("")
encart("alerte",
       f"<b>Le rythme actuel ne mène pas à 2030, il mène à "
       f"{er['annee_atteinte_tendanciel']:.0f}.</b> L'électrification rurale progresse de "
       f"+{er['rythme_observe']:.2f} point par an depuis {er['annee_depart']}. Pour atteindre "
       f"100 % en 2030, il faudrait +{er['rythme_requis_2030']:.1f} points par an, soit "
       f"{er['facteur_acceleration']:.0f} fois plus vite. L'extension du réseau seule ne peut "
       f"pas produire cette accélération : c'est l'argument central en faveur du "
       f"<b>solaire décentralisé</b>.",
       titre="Le constat qui commande tout le reste")

# ------------------------------------------------- la preuve : électrifier ≠ sauver la forêt
section("La preuve en un graphique",
        "Électrifier ne suffit pas : l'accès progresse depuis vingt-cinq ans, "
        "le couvert forestier recule sans discontinuer sur la même période.")

elec = D.serie(nat, "elec_rural", an_min, an_max)
foret = D.serie(nat, "foret_pct", an_min, an_max)
cuis = D.serie(nat, "cuisson_rural", an_min, an_max)

with st.container(border=True):
    titre_carte("Accès à l'énergie et couvert forestier, sur la même période",
                "Deux échelles distinctes : accès à gauche, couvert forestier à droite.",
                C["foret"])
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=elec["annee"], y=elec["valeur"], name="Accès rural à l'électricité",
        line=dict(color=C["energie"], width=3.4), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Accès rural</extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=cuis["annee"], y=cuis["valeur"], name="Accès rural à une cuisson propre",
        line=dict(color=C["risque"], width=2.6, dash="dot"), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Cuisson propre rurale</extra>"),
        secondary_y=False)
    fig.add_trace(go.Scatter(
        x=foret["annee"], y=foret["valeur"], name="Couvert forestier (% du territoire)",
        line=dict(color=C["foret"], width=3.4), mode="lines", fill="tozeroy",
        fillcolor="rgba(15,122,74,.10)",
        hovertemplate="%{x} · %{y:.1f} %<extra>Couvert forestier</extra>"),
        secondary_y=True)

    style_fig(fig, hauteur=390)
    fig.update_yaxes(title="Accès (% de la population rurale)", ticksuffix=" %",
                     range=[0, 40], secondary_y=False)
    fig.update_yaxes(title="Couvert forestier (% du territoire)", ticksuffix=" %",
                     range=[21, 26], secondary_y=True, showgrid=False)
    if len(elec):
        annote(fig, int(elec["annee"].iloc[-1]), float(elec["valeur"].iloc[-1]),
               f"{elec['valeur'].iloc[-1]:.0f} %", C["energie"], ax=-30, ay=-26)
    if len(cuis):
        annote(fig, int(cuis["annee"].iloc[-1]), float(cuis["valeur"].iloc[-1]),
               f"{cuis['valeur'].iloc[-1]:.1f} % — quasi nul", C["risque"], ax=-58, ay=26)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

encart("constat",
       f"Entre {int(elec['annee'].iloc[0]) if len(elec) else an_min} et {er['annee']}, l'accès "
       f"rural à l'électricité a été multiplié par "
       f"{er['valeur']/er['valeur_depart']:.0f}. Le couvert forestier, lui, n'a jamais cessé de "
       f"reculer. La raison tient dans la troisième courbe : la <b>cuisson</b> propre rurale "
       f"reste à {R['cuisson_rurale']['valeur']:.1f} %. L'électricité éclaire les foyers, elle "
       f"ne remplace pas le bois dans les marmites — et c'est la marmite, pas l'ampoule, qui "
       f"consomme la forêt.")

# ------------------------------------------------------------------ quatre constats
section("Quatre constats, quatre pages",
        "Chaque constat est démontré, chiffré et sourcé dans la page correspondante.")

CARTES = [
    ("Objectif 1", C["energie"], "La fracture ne se referme pas assez vite",
     f"{ec['valeur']:.0f} points d'écart ville/campagne. Et le réseau lui-même est fragile : "
     f"{fi['coupures_mois']:.1f} coupures par mois, {fi['part_entreprises']:.0f} % des "
     f"entreprises touchées en {fi['annee']}.", "Accès & fiabilité", "views/acces.py"),
    ("Objectif 2", C["risque"], "Le « renouvelable » togolais, c'est du bois de feu",
     f"{R['renouvelable_piege']['part_renouvelable']:.0f} % de l'énergie finale est classée "
     f"renouvelable, mais seulement "
     f"{R['renouvelable_piege']['part_cuisson_propre']:.0f} % des ménages cuisinent proprement. "
     f"Renouvelable ne veut pas dire propre.", "Cuisson & forêts", "views/cuisson.py"),
    ("Objectifs 3 & 4", C["urbain"], "L'énergie est marginale… seulement en CO₂",
     f"Le secteur énergie ne pèse que {R['ges']['part_energie']:.0f} % des émissions totales, "
     f"mais {R['ges']['energie_dans_n2o']:.0f} % du protoxyde d'azote et "
     f"{R['ges']['energie_dans_ch4']:.0f} % du méthane.", "Émissions & climat",
     "views/emissions.py"),
    ("Objectif 5", C["foret"], "Neuf forêts concentrent la priorité",
     f"Sur les {R['forets']['nb']} forêts classées, {R['forets']['nb_robustes']} restent dans le "
     f"top 10 quelle que soit la pondération testée. La cible d'investissement est identifiée.",
     "Où agir", "views/priorisation.py"),
]
cols = st.columns(4, gap="small")
for col, (objectif, coul, titre, txt, lien, cible) in zip(cols, CARTES):
    with col:
        st.markdown(
            f'<div style="background:{C["surface"]};border:1px solid {C["bord"]};'
            f'border-top:3px solid {coul};border-radius:4px 4px 12px 12px;'
            f'padding:14px 16px 15px;height:184px;'
            f'box-shadow:0 1px 2px rgba(7,42,32,.05)">'
            f'<div style="font-size:9.5px;font-weight:900;letter-spacing:1.2px;'
            f'text-transform:uppercase;color:{coul}">{objectif}</div>'
            f'<div style="font-size:14.4px;font-weight:800;color:{C["encre"]};'
            f'margin-top:9px;line-height:1.3;letter-spacing:-.2px">{titre}</div>'
            f'<div style="font-size:12px;color:{C["sourdine"]};margin-top:8px;'
            f'line-height:1.5">{txt}</div></div>', unsafe_allow_html=True)
        st.page_link(cible, label=lien, icon=":material/arrow_forward:")

# ------------------------------------------------------------------------ décision
st.write("")
encart("action",
       f"Trois leviers sortent des données, dans cet ordre de priorité : "
       f"<b>(1)</b> la cuisson propre, parce qu'elle touche {cb['biomasse'][1]:.0f} % des "
       f"ménages, cause {fr(df_['perte_ha_par_an'])} ha de perte forestière par an et "
       f"{R['sante']['mortalite']:.0f} décès pour 100 000 habitants via la pollution de l'air ; "
       f"<b>(2)</b> le solaire décentralisé, seul capable de multiplier par "
       f"{er['facteur_acceleration']:.0f} le rythme d'électrification là où le réseau n'ira pas ; "
       f"<b>(3)</b> la protection ciblée des {R['forets']['nb_robustes']} forêts prioritaires "
       f"identifiées par l'indice de vulnérabilité.")
st.write("")
st.page_link("views/plan.py",
             label="Voir le plan d'action chiffré et le simulateur 2030",
             icon=":material/checklist:")

pied()

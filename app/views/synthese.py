"""Synthèse — la page que lit un décideur pressé : diagnostic, preuve, décision."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data as D
from theme import (C, hero, section, kpi_row, encart, style_fig, annote,
                   legende, pied, fr)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

hero("Défi 2 · synthèse décisionnelle",
     "Électrifier les campagnes sans brûler les forêts",
     "Le Togo vise l'accès universel en 2030. Les données du défi montrent que l'objectif "
     "ne se joue pas seulement sur le réseau électrique : il se joue sur la cuisson des "
     "ménages, qui consomme la forêt. Voici le diagnostic en cinq chiffres, la preuve, "
     "et l'endroit où agir.")

# ------------------------------------------------------------------ chiffres clés
er, ec, rs = R["elec_rural"], R["ecart_urbain_rural"], R["ruraux_sans_elec"]
cb, df_, fi = R["combustibles"], R["deforestation"], R["fiabilite"]

kpi_row([
    ("Accès rural à l'électricité", f"{er['valeur']:.0f} %",
     f"contre {ec['urbain']:.0f} % en ville en {ec['annee']} — un écart de "
     f"{ec['valeur']:.0f} points", C["energie"], f"+{er['rythme_observe']:.1f} pt/an"),
    ("Ruraux sans électricité", f"{rs['personnes']/1e6:.1f} M",
     f"personnes, soit {100-er['valeur']:.0f} % de la population rurale "
     f"({er['annee']})", C["risque"]),
    ("Ménages au bois ou au charbon", f"{cb['biomasse'][1]:.0f} %",
     f"en {cb['annees'][1]} — la dépendance n'a pas reculé depuis "
     f"{cb['annees'][0]} ({cb['biomasse'][0]:.0f} %)", C["risque"], "stable"),
    ("Forêt perdue chaque année", f"{fr(df_['perte_ha_par_an'])} ha",
     f"soit −{df_['perte_pct_relative']:.0f} % du couvert entre "
     f"{df_['annee_debut']} et {df_['annee_fin']}", C["foret"]),
    ("Accélération requise", f"× {er['facteur_acceleration']:.0f}",
     f"pour tenir l'accès universel rural en 2030 "
     f"(+{er['rythme_requis_2030']:.1f} pt/an au lieu de "
     f"+{er['rythme_observe']:.1f})", C["risque"]),
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
        "Électrifier ne suffit pas : l'accès progresse depuis 25 ans, "
        "le couvert forestier recule sans discontinuer sur la même période.")

elec = D.serie(nat, "elec_rural", an_min, an_max)
foret = D.serie(nat, "foret_pct", an_min, an_max)
cuis = D.serie(nat, "cuisson_rural", an_min, an_max)

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(
    x=elec["annee"], y=elec["valeur"], name="Accès rural à l'électricité",
    line=dict(color=C["energie"], width=3.2), mode="lines",
    hovertemplate="%{x} · %{y:.1f} %<extra>Accès rural</extra>"), secondary_y=False)
fig.add_trace(go.Scatter(
    x=cuis["annee"], y=cuis["valeur"], name="Accès rural à une cuisson propre",
    line=dict(color=C["risque"], width=2.6, dash="dot"), mode="lines",
    hovertemplate="%{x} · %{y:.1f} %<extra>Cuisson propre rurale</extra>"), secondary_y=False)
fig.add_trace(go.Scatter(
    x=foret["annee"], y=foret["valeur"], name="Couvert forestier (% du territoire)",
    line=dict(color=C["foret"], width=3.2), mode="lines", fill="tozeroy",
    fillcolor="rgba(27,122,67,.08)",
    hovertemplate="%{x} · %{y:.1f} %<extra>Couvert forestier</extra>"), secondary_y=True)

style_fig(fig, hauteur=400)
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
        "Chaque constat est démontré dans la page correspondante.")

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
cols = st.columns(4)
for col, (objectif, coul, titre, txt, lien, cible) in zip(cols, CARTES):
    with col:
        st.markdown(
            f'<div style="background:#fff;border:1px solid {C["line"]};'
            f'border-top:3px solid {coul};border-radius:3px 3px 11px 11px;'
            f'padding:14px 16px 15px;height:186px;'
            f'box-shadow:0 1px 2px rgba(21,34,56,.05)">'
            f'<div style="font-size:10px;font-weight:800;letter-spacing:1.1px;'
            f'text-transform:uppercase;color:{coul}">{objectif}</div>'
            f'<div style="font-size:14.2px;font-weight:700;color:{C["ink"]};'
            f'margin-top:9px;line-height:1.32">{titre}</div>'
            f'<div style="font-size:12.2px;color:{C["muted"]};margin-top:7px;'
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

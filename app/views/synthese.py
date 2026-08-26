"""Vue d'ensemble — ce que lit un décideur pressé : diagnostic, preuve, décision."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   titre_carte, pied, fr, rgba, FONT_T)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

er, ec, rs = R["elec_rural"], R["ecart_urbain_rural"], R["ruraux_sans_elec"]
cb, df_, fi = R["combustibles"], R["deforestation"], R["fiabilite"]

banniere(
    "Diagnostic national · vue d'ensemble",
    "Électrifier les campagnes sans brûler les forêts",
    "Le Togo vise l'accès universel à l'électricité en 2030. Les données du défi montrent "
    "que l'objectif ne se joue pas seulement sur le réseau : il se joue sur la cuisson des "
    "ménages, qui consomme la forêt. Diagnostic en cinq chiffres, preuve, et lieu d'action.",
    reperes=[("Accès rural", f"{er['valeur']:.0f} %"),
             ("Ménages au bois", f"{cb['biomasse'][1]:.0f} %"),
             ("Forêt / an", f"−{fr(df_['perte_ha_par_an'])} ha")])

# ------------------------------------------------------------------ chiffres clés
# Chaque micro-courbe doit tracer LA grandeur de sa tuile, pas une grandeur
# voisine : une courbe qui ne correspond pas à son chiffre induit en erreur.
_elec = D.serie(nat, "elec_rural")
_pop_r = D.serie(nat, "pop_rurale").set_index("annee")["valeur"]
_foret_km2 = D.serie(nat, "foret_km2")

# ruraux privés d'électricité, année par année
_prives = [(a, _pop_r[a] * (1 - v / 100))
           for a, v in zip(_elec["annee"], _elec["valeur"]) if a in _pop_r.index]
# perte forestière annuelle : dérivée du stock de couvert, en hectares
_perte = [(int(_foret_km2["annee"].iloc[i]),
           (_foret_km2["valeur"].iloc[i - 1] - _foret_km2["valeur"].iloc[i]) * 100)
          for i in range(1, len(_foret_km2))]


def _bornes(paires):
    return (str(paires[0][0]), str(paires[-1][0]))


kpi_row([
    ("Accès rural à l'électricité", f"{er['valeur']:.0f} %",
     f"contre {ec['urbain']:.0f} % en ville en {ec['annee']} — un écart de "
     f"{ec['valeur']:.0f} points", C["energie"],
     f"+{fr(er['rythme_observe'], 1)} pt/an", list(_elec["valeur"]),
     (str(er["annee_depart"]), str(er["annee"]))),
    ("Ruraux sans électricité", f"{fr(rs['personnes']/1e6, 1)} M",
     f"personnes, soit {100-er['valeur']:.0f} % de la population rurale "
     f"en {er['annee']}", C["risque"], None,
     [v for _, v in _prives], _bornes(_prives)),
    ("Ménages au bois ou au charbon", f"{cb['biomasse'][1]:.0f} %",
     f"en {cb['annees'][1]} — la dépendance n'a pas reculé depuis "
     f"{cb['annees'][0]}, où elle était de {cb['biomasse'][0]:.0f} %",
     C["risque"], "stable"),
    ("Forêt perdue chaque année", f"{fr(df_['perte_ha_par_an'])} ha",
     f"en moyenne, soit −{df_['perte_pct_relative']:.0f} % du couvert entre "
     f"{df_['annee_debut']} et {df_['annee_fin']}", C["risque"], None,
     [v for _, v in _perte], _bornes(_perte)),
    ("Accélération requise", f"× {er['facteur_acceleration']:.0f}",
     f"pour l'accès universel rural en 2030 : il faudrait "
     f"+{fr(er['rythme_requis_2030'], 1)} pt/an au lieu de "
     f"+{fr(er['rythme_observe'], 1)}", C["risque"], "hors trajectoire"),
])

st.write("")
encart("alerte",
       f"<b>Le rythme actuel ne mène pas à 2030, il mène à "
       f"{er['annee_atteinte_tendanciel']:.0f}.</b> L'électrification rurale progresse de "
       f"+{fr(er['rythme_observe'], 2)} point par an depuis {er['annee_depart']}. Pour atteindre "
       f"100 % en 2030, il faudrait +{fr(er['rythme_requis_2030'], 1)} points par an, soit "
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
    # Deux panneaux superposés plutôt qu'un double axe : l'axe secondaire
    # obligeait à resserrer l'échelle du couvert forestier pour rendre son
    # recul visible, et une échelle resserrée face à une autre courbe est
    # toujours attaquable. Ici chaque série garde son échelle, l'axe du
    # temps est partagé, et la divergence se lit sans qu'aucune courbe
    # n'ait été redressée. Les valeurs de début et de fin sont écrites en
    # clair sur le panneau du bas : l'échelle ne cache rien.
    titre_carte("Accès à l'énergie et couvert forestier, sur la même période",
                "Deux panneaux, un seul axe du temps : chaque série garde son "
                "échelle propre.", C["foret"])
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=.09, row_heights=[.58, .42])
    fig.add_trace(go.Scatter(
        x=elec["annee"], y=elec["valeur"], name="Accès rural à l'électricité",
        line=dict(color=C["energie"], width=3.4), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Accès rural</extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=cuis["annee"], y=cuis["valeur"], name="Accès rural à une cuisson propre",
        line=dict(color=C["risque"], width=2.6, dash="dot"), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Cuisson propre rurale</extra>"),
        row=1, col=1)
    fig.add_trace(go.Scatter(
        x=foret["annee"], y=foret["valeur"], name="Couvert forestier (% du territoire)",
        line=dict(color=C["foret"], width=3.4), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Couvert forestier</extra>"),
        row=2, col=1)

    style_fig(fig, hauteur=440)
    fig.update_yaxes(title="Accès (% de la population rurale)", ticksuffix=" %",
                     range=[0, 40], row=1, col=1)
    fig.update_yaxes(title="Couvert forestier (% du territoire)", ticksuffix=" %",
                     row=2, col=1)
    fig.update_xaxes(title=None)
    if len(elec):
        annote(fig, int(elec["annee"].iloc[-1]), float(elec["valeur"].iloc[-1]),
               f"{elec['valeur'].iloc[-1]:.0f} %", C["energie"], ax=-30, ay=-26,
               row=1, col=1)
    if len(cuis):
        annote(fig, int(cuis["annee"].iloc[-1]), float(cuis["valeur"].iloc[-1]),
               f"{fr(cuis['valeur'].iloc[-1], 1)} % — quasi nul", C["risque"],
               ax=-58, ay=26, row=1, col=1)
    if len(foret) > 1:
        annote(fig, int(foret["annee"].iloc[-1]), float(foret["valeur"].iloc[-1]),
               f"{fr(foret['valeur'].iloc[0], 1)} % → {fr(foret['valeur'].iloc[-1], 1)} % "
               f"du territoire", C["foret"], ax=-96, ay=-20, row=2, col=1)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

encart("constat",
       f"Entre {int(elec['annee'].iloc[0]) if len(elec) else an_min} et {er['annee']}, l'accès "
       f"rural à l'électricité a été multiplié par "
       f"{er['valeur']/er['valeur_depart']:.0f}. Le couvert forestier, lui, n'a jamais cessé de "
       f"reculer. La raison tient dans la troisième courbe : la <b>cuisson</b> propre rurale "
       f"reste à {fr(R['cuisson_rurale']['valeur'], 1)} %. L'électricité éclaire les foyers, elle "
       f"ne remplace pas le bois dans les marmites — et c'est la marmite, pas l'ampoule, qui "
       f"consomme la forêt.")

# ------------------------------------------------------------------ quatre constats
section("Quatre constats, quatre pages",
        "Chaque constat est démontré, chiffré et sourcé dans la page correspondante.")

CARTES = [
    ("Électrification", C["energie"],
     "Le retard rural ne se comble pas assez vite",
     f"{ec['valeur']:.0f} points d'écart ville/campagne. Et le réseau lui-même est fragile : "
     f"{fr(fi['coupures_mois'], 1)} coupures par mois, {fi['part_entreprises']:.0f} % des "
     f"entreprises touchées en {fi['annee']}.", "Voir la page", "views/acces.py"),
    ("Cuisson", C["risque"],
     "Le « renouvelable » togolais, c'est du bois de feu",
     f"{R['renouvelable_piege']['part_renouvelable']:.0f} % de l'énergie finale est classée "
     f"renouvelable, mais seulement "
     f"{R['renouvelable_piege']['part_cuisson_propre']:.0f} % des ménages cuisinent proprement. "
     f"Renouvelable ne veut pas dire propre.", "Voir la page", "views/cuisson.py"),
    ("Inventaire", C["urbain"],
     "L'énergie n'est marginale qu'en dioxyde de carbone",
     f"Le secteur énergie ne pèse que {R['ges']['part_energie']:.0f} % des émissions totales, "
     f"mais {R['ges']['energie_dans_n2o']:.0f} % du protoxyde d'azote et "
     f"{R['ges']['energie_dans_ch4']:.0f} % du méthane.", "Voir la page",
     "views/emissions.py"),
    ("Forêts", C["foret"],
     "Neuf massifs concentrent toute la priorité",
     f"Sur les {R['forets']['nb']} forêts classées, {R['forets']['nb_robustes']} restent dans le "
     f"top 10 quelle que soit la pondération testée. La cible d'investissement est identifiée.",
     "Voir la page", "views/priorisation.py"),
]
cols = st.columns(4, gap="small")
for col, (objectif, coul, titre, txt, lien, cible) in zip(cols, CARTES):
    with col:
        st.markdown(
            f'<div class="carte-relais" style="background:{C["surface"]};'
            f'border:1px solid {C["bord"]};border-radius:10px;'
            f'padding:15px 17px 16px">'
            f'<div style="font-size:10.5px;font-weight:700;letter-spacing:.55px;'
            f'text-transform:uppercase;color:{coul}">{objectif}</div>'
            f'<div style="font-family:{FONT_T};font-size:16.5px;font-weight:600;'
            f'color:{C["encre"]};margin-top:10px;line-height:1.28">{titre}</div>'
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

"""Objectif 6 — recommandations pratiques et simulateur de trajectoire 2030."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, banniere, section, kpi_row, kpi, encart, style_fig,
                   legende, pied, fr, titre_carte)

nat = D.national()
R = nat["reperes"]
forets = D.forets()
robust = D.robustesse()

er, cb, dfr, sa, fi = (R["elec_rural"], R["combustibles"], R["deforestation"],
                       R["sante"], R["fiabilite"])
pop = D.serie(nat, "pop_totale")["valeur"].iloc[-1]
an_pop = int(D.serie(nat, "pop_totale")["annee"].iloc[-1])

banniere("Objectif 6 · Recommandations",
     "Trois leviers, dans cet ordre, et une manière de vérifier qu'ils marchent",
     "Les cinq pages précédentes convergent vers une hiérarchie que les données "
     "imposent : la cuisson propre avant le raccordement, le solaire décentralisé "
     "avant l'extension du réseau, et une protection ciblée plutôt qu'un discours "
     "général sur la forêt.",
     reperes=[("Levier n°1", "Cuisson propre"),
              ("Population visée", f"{fr(pop*cb['biomasse'][1]/100/1e6, 1)} M"),
              ("Massifs prioritaires", f"{R['forets']['nb_robustes']}")])

# ================================================== la portée comparée des leviers
section("Pourquoi cet ordre : la portée comparée des trois leviers",
        "Combien de Togolais chaque levier concerne-t-il directement ?")

pers_biomasse = pop * cb["biomasse"][1] / 100
pers_sans_elec = R["ruraux_sans_elec"]["personnes"]

g1, g2 = st.columns([1.25, 1])
with g1:
    # Seuls les deux premiers leviers se comptent en personnes : le troisième
    # n'a pas d'échelle comparable, on ne lui invente donc pas de barre.
    fig = go.Figure(go.Bar(
        y=["Électrification rurale décentralisée", "Cuisson propre"],
        x=[pers_sans_elec, pers_biomasse], orientation="h",
        marker_color=[C["energie"], C["risque"]],
        text=[f"{fr(pers_sans_elec/1e6, 2)} M de personnes",
              f"{fr(pers_biomasse/1e6, 2)} M de personnes"],
        textposition="outside", textfont=dict(size=12.5),
        hovertemplate="%{y} · %{x:,.0f} personnes<extra></extra>"))
    style_fig(fig, "Population directement concernée par chaque levier", hauteur=280,
              marge_g=0)
    fig.add_annotation(
        x=0, y=-0.62, xanchor="left", showarrow=False,
        text=f"<b>Protection ciblée des forêts</b> — {R['forets']['nb_robustes']} massifs "
             f"prioritaires, {fr(R['forets']['surface_totale_ha'])} ha : "
             "ne se compte pas en personnes",
        font=dict(size=12, color=C["foret"]), align="left",
        bgcolor="rgba(27,122,67,.08)", borderpad=8)
    fig.update_xaxes(range=[0, pers_biomasse * 1.5], title="personnes",
                     tickvals=[0, 2e6, 4e6, 6e6, 8e6],
                     ticktext=["0", "2 M", "4 M", "6 M", "8 M"])
    fig.update_yaxes(title=None, range=[-1.1, 1.6])
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with g2:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    encart("constat",
           f"La cuisson propre concerne <b>{fr(pers_biomasse/1e6, 1)} millions</b> de "
           f"Togolais, soit {pers_biomasse/pers_sans_elec:.1f} fois plus que "
           f"l'électrification rurale ({fr(pers_sans_elec/1e6, 1)} M). C'est aussi le "
           f"seul levier qui agisse simultanément sur la <b>forêt</b> "
           f"({fr(dfr['perte_ha_par_an'])} ha/an), sur la <b>santé</b> "
           f"({sa['mortalite']:.0f} décès pour 100 000 hab.) et sur le <b>climat</b> "
           f"(méthane et N₂O de combustion). D'où sa place en tête.")

# =========================================================== les trois leviers
section("Les trois leviers")

LEVIERS = [
    {
        "n": "1", "coul": C["risque"], "titre": "Cuisson propre",
        "quoi": "GPL subventionné en zone périurbaine et foyers améliorés certifiés "
                "en zone rurale enclavée, distribués via les réseaux existants "
                "(coopératives, marchés hebdomadaires, centres de santé).",
        "pourquoi": f"{cb['biomasse'][1]:.0f} % des ménages dépendent du bois ou du "
                    f"charbon, et cette part n'a pas bougé entre {cb['annees'][0]} et "
                    f"{cb['annees'][1]} — le bois brut a même gagné "
                    f"{cb['bois'][1]-cb['bois'][0]:.1f} points.",
        "ou": "Priorité aux cantons riverains des forêts classées du top 10 "
              "(voir page « Où agir »), puis aux préfectures rurales des Plateaux "
              "et de la Centrale, les plus peuplées parmi les zones enclavées.",
        "cible": "Passer de 0,9 % à 15 % d'accès rural à une cuisson propre en 2030.",
        "suivi": "`EG.CFT.ACCS.RU.ZS` (accès rural à une cuisson propre) — "
                 "et surtout **pas** le taux d'énergie renouvelable, qui baissera "
                 "quand la situation s'améliorera.",
    },
    {
        "n": "2", "coul": C["energie"],
        "titre": "Solaire villageois décentralisé",
        "quoi": "Mini-réseaux solaires avec stockage pour les gros bourgs, kits "
                "domestiques pour l'habitat dispersé, dimensionnés sur les usages "
                "productifs (mouture, froid, pompage) et non sur le seul éclairage.",
        "pourquoi": f"Atteindre l'accès universel rural en 2030 exige de multiplier par "
                    f"{er['facteur_acceleration']:.0f} le rythme actuel "
                    f"(+{er['rythme_observe']:.2f} pt/an). Et le réseau lui-même reste "
                    f"instable : {fi['coupures_mois']:.1f} coupures par mois, "
                    f"{fi['part_entreprises']:.0f} % des entreprises touchées.",
        "ou": "Zones à plus de 40 km d'un pôle urbain raccordé — celles-là mêmes qui "
              "ressortent en tête de l'indice d'enclavement. Priorité au Nord, où le "
              "pic thermique de "
              f"{R['climat']['mois_chaud_nom']} coïncide avec le maximum "
              "d'ensoleillement : la pointe de demande et la pointe de production "
              "solaire tombent au même moment.",
        "cible": f"Raccorder de l'ordre de "
                 f"{fr(R['ruraux_sans_elec']['pop_rurale']*(100-er['valeur'])/100/8/1000)} 000 "
                 "ruraux par an jusqu'en 2030.",
        "suivi": "`EG.ELC.ACCS.RU.ZS`, complété par un indicateur de **disponibilité "
                 "horaire** du service, absent des données actuelles.",
    },
    {
        "n": "3", "coul": C["foret"],
        "titre": "Protection ciblée des massifs prioritaires",
        "quoi": "Concentrer surveillance, régénération assistée et plantations "
                "d'agroforesterie sur un nombre restreint de massifs, plutôt que "
                "de saupoudrer sur les 53 forêts classées.",
        "pourquoi": f"Le couvert forestier a perdu {dfr['perte_pct_relative']:.0f} % "
                    f"entre {dfr['annee_debut']} et {dfr['annee_fin']}, soit "
                    f"{fr(dfr['perte_ha_par_an'])} ha par an, sans une seule année "
                    f"de reprise.",
        "ou": None,      # rempli dynamiquement ci-dessous
        "cible": "Stopper la perte nette sur les massifs prioritaires d'ici 2030.",
        "suivi": "`AG.LND.FRST.K2` au niveau national, et un suivi surfacique par "
                 "massif à mettre en place — il n'existe pas aujourd'hui.",
    },
]

# où agir pour le levier 3 : les forêts robustes, avec leurs préfectures
rb = robust[robust["toujours_top10"]].merge(
    forets[["etab_nom", "region_nom_bdd", "prefecture_nom_bdd", "surface_ha", "dist_km"]],
    left_on="foret", right_on="etab_nom", how="left").sort_values("rang_max")
prefs = rb["prefecture_nom_bdd"].dropna().unique()[:6]
LEVIERS[2]["ou"] = (
    f"Les {len(rb)} forêts qui restent dans le top 10 quelle que soit la pondération, "
    f"situées principalement dans les préfectures de "
    f"{', '.join(str(p) for p in prefs)}.")

for lv in LEVIERS:
    st.markdown(
        f'<div style="background:#fff;border:1px solid {C["bord"]};'
        f'border-left:5px solid {lv["coul"]};border-radius:11px;padding:17px 21px;'
        f'margin-bottom:13px;box-shadow:0 1px 2px rgba(21,34,56,.05)">'
        f'<div style="display:flex;align-items:baseline;gap:12px">'
        f'<span style="font-size:10.5px;font-weight:800;color:#fff;'
        f'background:{lv["coul"]};letter-spacing:1.2px;padding:3px 9px;'
        f'border-radius:4px;position:relative;top:-2px">LEVIER {lv["n"]}</span>'
        f'<span style="font-size:19px;font-weight:800;color:{C["foret_d"]}">'
        f'{lv["titre"]}</span></div>'
        f'<div style="font-size:14px;color:{C["encre"]};margin-top:9px;line-height:1.6">'
        f'{lv["quoi"]}</div></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, (etiq, txt) in zip(
            [c1, c2, c3, c4],
            [("Ce qui le justifie", lv["pourquoi"]), ("Où agir en priorité", lv["ou"]),
             ("Cible 2030", lv["cible"]), ("Indicateur de suivi", lv["suivi"])]):
        with col:
            st.markdown(
                f'<div style="font-size:10px;font-weight:800;letter-spacing:.9px;'
                f'text-transform:uppercase;color:{lv["coul"]};margin-bottom:4px">'
                f'{etiq}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:12.5px;color:{C["sourdine"]};'
                        f'line-height:1.55">{txt}</div>', unsafe_allow_html=True)
    st.write("")

# ====================================================== simulateur de trajectoire
section("Simulateur de trajectoire 2030",
        "Réglez l'ambition de chaque levier et lisez immédiatement où le Togo "
        "atterrit en 2030.")

s1, s2, s3 = st.columns(3)
with s1:
    v_elec = st.slider("Rythme d'électrification rurale (points/an)",
                       0.5, 12.0, float(round(er["rythme_observe"], 1)), 0.5,
                       help=f"Rythme observé {er['annee_depart']}–{er['annee']} : "
                            f"+{er['rythme_observe']:.2f} pt/an. "
                            f"Rythme requis pour 2030 : "
                            f"+{er['rythme_requis_2030']:.1f} pt/an.")
with s2:
    v_cuis = st.slider("Population sortie de la biomasse d'ici 2030 (%)",
                       0, 60, 25, 5)
with s3:
    v_attr = st.slider("Recul forestier imputable au bois-énergie (%)",
                       0, 100, 50, 5,
                       help="Hypothèse explicite ; aucune source du défi ne tranche "
                            "cette répartition.")

annees = 2030 - er["annee"]
acces_2030 = min(100, er["valeur"] + v_elec * annees)
raccordes = R["ruraux_sans_elec"]["pop_rurale"] * (acces_2030 - er["valeur"]) / 100
cuis_2030 = R["cuisson_rurale"]["valeur"] + v_cuis
perte_2030 = dfr["perte_ha_par_an"] * (1 - (v_attr / 100) * (v_cuis / 100))
ha_sauves = (dfr["perte_ha_par_an"] - perte_2030) * 5

st.write("")
kpi_row([
    ("Accès rural en 2030", f"{acces_2030:.0f} %",
     f"contre {er['valeur']:.0f} % en {er['annee']} · "
     f"{'objectif atteint' if acces_2030 >= 99.5 else f'il manque {100-acces_2030:.0f} points'}",
     C["foret"] if acces_2030 >= 99.5 else C["risque"]),
    ("Ruraux raccordés", f"{fr(raccordes/1e6, 2)} M",
     f"sur {fr(pers_sans_elec/1e6, 2)} M actuellement privés d'électricité",
     C["energie"]),
    ("Cuisson propre rurale", f"{cuis_2030:.1f} %",
     f"contre {R['cuisson_rurale']['valeur']:.1f} % en "
     f"{R['cuisson_rurale']['annee']}", C["foret"] if cuis_2030 >= 15 else C["risque"]),
    ("Perte forestière en 2030", f"{fr(perte_2030)} ha/an",
     f"contre {fr(dfr['perte_ha_par_an'])} ha/an aujourd'hui", C["foret"]),
    ("Forêt préservée", f"{fr(ha_sauves)} ha",
     "cumulés sur cinq ans grâce au levier cuisson", C["foret"]),
])

st.write("")
# graphique « où l'on atterrit » : trois jauges alignées sur leurs cibles
JAUGES = [
    ("Accès rural à l'électricité", er["valeur"], acces_2030, 100, "%", C["energie"]),
    ("Cuisson propre rurale", R["cuisson_rurale"]["valeur"], cuis_2030, 15, "%",
     C["risque"]),
    ("Réduction de la perte forestière", 0,
     100 * (dfr["perte_ha_par_an"] - perte_2030) / dfr["perte_ha_par_an"], 50, "%",
     C["foret"]),
]
fig2 = go.Figure()
noms = [j[0] for j in JAUGES]
fig2.add_trace(go.Bar(y=noms, x=[100 for _ in JAUGES], orientation="h",
                      marker_color=C["neutre_l"], showlegend=False, hoverinfo="skip",
                      width=.52))
fig2.add_trace(go.Bar(y=noms, x=[j[1] for j in JAUGES], orientation="h",
                      marker_color=C["neutre"], name="Aujourd'hui", width=.52,
                      hovertemplate="%{y} · aujourd'hui : %{x:.1f} %<extra></extra>"))
fig2.add_trace(go.Bar(y=noms, x=[j[2] - j[1] for j in JAUGES], orientation="h",
                      marker_color=[j[5] for j in JAUGES], name="Gain simulé d'ici 2030",
                      width=.52,
                      hovertemplate="%{y} · gain : +%{x:.1f} pts<extra></extra>"))
for i, j in enumerate(JAUGES):
    fig2.add_shape(type="line", x0=j[3], x1=j[3], y0=i - .34, y1=i + .34,
                   line=dict(color=C["encre"], width=2.6))
fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines",
                          line=dict(color=C["encre"], width=2.6), name="Cible 2030"))
style_fig(fig2, "Où atterrit le Togo en 2030 avec ces réglages", hauteur=280, marge_g=0)
fig2.update_layout(barmode="overlay")
fig2.update_traces(selector=dict(type="bar"), offsetgroup=None)
fig2.update_layout(barmode="stack")
fig2.update_xaxes(range=[0, 106], ticksuffix=" %", title=None)
fig2.update_yaxes(title=None, autorange="reversed")
st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

if acces_2030 >= 99.5 and cuis_2030 >= 15:
    encart("action",
           f"Avec ces réglages, les deux cibles majeures sont tenues. Le prix à payer est "
           f"explicite : un rythme d'électrification de +{v_elec:.1f} points par an, soit "
           f"{v_elec/er['rythme_observe']:.0f} fois le rythme historique, et une politique "
           f"de cuisson propre touchant {v_cuis} % de la population. "
           f"C'est un choix d'investissement, pas une projection.")
else:
    manque = []
    if acces_2030 < 99.5:
        manque.append(f"il manque {100-acces_2030:.0f} points d'accès rural")
    if cuis_2030 < 15:
        manque.append(f"la cuisson propre rurale reste à {cuis_2030:.1f} %")
    encart("alerte",
           f"Avec ces réglages, l'objectif 2030 n'est pas tenu : {' et '.join(manque)}. "
           f"Faites glisser les curseurs vers +{er['rythme_requis_2030']:.1f} pt/an "
           f"d'électrification pour voir l'effort réellement nécessaire.")

# ============================================================ tableau récapitulatif
section("Récapitulatif décisionnel",
        "Une ligne par action, avec la donnée qui la justifie et l'indicateur qui la suit.")

recap = pd.DataFrame([
    {"Priorité": "1", "Action": "GPL + foyers améliorés certifiés",
     "Où": "Cantons riverains du top 10, Plateaux et Centrale",
     "Cible 2030": "15 % d'accès rural à la cuisson propre",
     "Donnée qui la justifie": f"{cb['biomasse'][1]:.0f} % des ménages sur biomasse ; "
                              f"bois +{cb['bois'][1]-cb['bois'][0]:.1f} pt en 3 ans",
     "Indicateur de suivi": "EG.CFT.ACCS.RU.ZS"},
    {"Priorité": "2", "Action": "Mini-réseaux solaires + kits domestiques",
     "Où": "Zones à plus de 40 km d'un pôle raccordé, priorité Nord",
     "Cible 2030": "Accès universel rural",
     "Donnée qui la justifie": f"× {er['facteur_acceleration']:.0f} de rythme requis ; "
                              f"{fi['part_entreprises']:.0f} % d'entreprises subissant "
                              f"des coupures",
     "Indicateur de suivi": "EG.ELC.ACCS.RU.ZS + disponibilité horaire (à créer)"},
    {"Priorité": "3", "Action": "Protection et régénération ciblées",
     "Où": f"Les {len(rb)} massifs robustes du classement",
     "Cible 2030": "Perte nette nulle sur les massifs prioritaires",
     "Donnée qui la justifie": f"−{dfr['perte_pct_relative']:.0f} % de couvert en "
                              f"{dfr['annee_fin']-dfr['annee_debut']} ans",
     "Indicateur de suivi": "AG.LND.FRST.K2 + suivi surfacique par massif (à créer)"},
    {"Priorité": "4", "Action": "Corriger le tableau de bord public de la transition",
     "Où": "Pilotage national",
     "Cible 2030": "Abandonner EG.FEC.RNEW.ZS comme indicateur de progrès",
     "Donnée qui la justifie": f"{R['renouvelable_piege']['part_renouvelable']:.0f} % "
                              f"d'énergie « renouvelable » pour "
                              f"{R['renouvelable_piege']['part_cuisson_propre']:.0f} % "
                              f"de cuisson propre",
     "Indicateur de suivi": "Part des ménages sortis de la biomasse"},
])
st.dataframe(recap, width="stretch", hide_index=True,
             column_config={
                 "Priorité": st.column_config.TextColumn(width="small"),
                 "Action": st.column_config.TextColumn(width="medium"),
                 "Donnée qui la justifie": st.column_config.TextColumn(width="large"),
             })

# ==================================================== honnêteté méthodologique
section("Ce que ces données ne permettent pas de dire",
        "Le périmètre des recommandations s'arrête là où s'arrêtent les preuves.")

st.markdown(f"""
- **Aucun coût, aucun budget.** Les six jeux de données ne contiennent ni prix des
  équipements, ni coût de raccordement, ni budget public. Les recommandations
  décrivent donc un **ordre de priorité et des cibles physiques**, pas un plan de
  financement. Toute affirmation chiffrée sur le coût aurait été inventée.
- **Aucune maille infranationale pour l'énergie.** L'électrification, la cuisson et
  les émissions ne sont disponibles qu'au niveau national. Le seul croisement
  spatial rigoureux possible est celui construit ici : forêts × stations météo ×
  éloignement urbain. Les recommandations géographiques reposent sur cette
  construction, pas sur des taux d'accès locaux qui n'existent pas.
- **Le lien cuisson → déforestation est corrélatif.** Aucun fichier ne mesure les
  prélèvements de bois-énergie. C'est pourquoi le simulateur rend l'attribution
  **paramétrable** au lieu de la fixer.
- **La fiabilité est mesurée sur les entreprises**, pas sur les ménages, et sur deux
  vagues d'enquête seulement ({fi['annee_ref']}, {fi['annee']}).
- **Les températures sont au degré entier**, sur 7 ans : le gradient spatial est
  exploitable, la tendance temporelle ne l'est pas.
- **Trois indicateurs manquent** pour piloter correctement cette politique et
  devraient être créés : la disponibilité horaire du service électrique, un suivi
  surfacique par massif forestier, et une enquête ménages sur les combustibles plus
  fréquente que tous les trois ans.
""")

pied()

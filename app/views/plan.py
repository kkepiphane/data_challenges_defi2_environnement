"""Recommandations pratiques et simulateur de trajectoire 2030."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig,
                   legende, pied, fr, titre_carte, rgba, telecharger,
                   reglages, jetons, FONT_T)

nat = D.national()
R = nat["reperes"]
forets = D.forets()
robust = D.robustesse()

er, cb, dfr, sa, fi = (R["elec_rural"], R["combustibles"], R["deforestation"],
                       R["sante"], R["fiabilite"])
tr, us, rg = R["tapis_roulant"], R["usage_sols"], R["regimes_foret"]
PERTE = dfr["perte_actuelle_ha_an"]      # régime en cours, pas la moyenne longue
pop = D.serie(nat, "pop_totale")["valeur"].iloc[-1]
an_pop = int(D.serie(nat, "pop_totale")["annee"].iloc[-1])

banniere("Recommandations et trajectoire 2030",
         "Quatre leviers, dans cet ordre, et une manière de vérifier qu'ils marchent",
         "Les cinq pages d'analyse convergent vers une hiérarchie que les données "
         "imposent : la cuisson propre avant le raccordement, le solaire décentralisé "
         "avant l'extension du réseau, une protection forestière ciblée plutôt qu'un "
         "discours général — et, derrière elle, l'intensification agricole, parce que "
         "le défrichement de terres cultivables avance plus vite que la forêt ne recule.")

# ================================================== la portée comparée des leviers
section("Pourquoi cet ordre : la portée comparée des leviers",
        "Combien de Togolais chaque levier concerne-t-il directement, et sur quelle "
        "surface agit-il ?")

pers_biomasse = pop * cb["biomasse"][1] / 100
pers_sans_elec = tr["sans_elec_fin"]

g1, g2 = st.columns([1.25, 1])
with g1:
    with st.container(border=True):
        # Seuls les deux premiers leviers se comptent en personnes : les deux
        # autres se comptent en hectares, on ne leur invente donc pas de barre
        # sur la même échelle.
        titre_carte("Population directement concernée par chaque levier",
                    "Les deux leviers énergétiques se comptent en personnes ; les "
                    "deux leviers fonciers se comptent en hectares, et figurent "
                    "sous le graphique.", C["risque"])
        fig = go.Figure(go.Bar(
            y=["Électrification rurale décentralisée", "Cuisson propre"],
            x=[pers_sans_elec, pers_biomasse], orientation="h",
            marker_color=[C["energie"], C["risque"]],
            text=[f"{fr(pers_sans_elec/1e6, 2)} M de personnes",
                  f"{fr(pers_biomasse/1e6, 2)} M de personnes"],
            textposition="outside", textfont=dict(size=12.5),
            hovertemplate="%{y} · %{x:,.0f} personnes<extra></extra>"))
        style_fig(fig, hauteur=300, marge_g=0)
        fig.add_annotation(
            x=0, y=-0.72, xanchor="left", showarrow=False,
            text=f"<b>Protection ciblée des forêts</b> — "
                 f"{R['forets']['nb_robustes']} massifs prioritaires, "
                 f"{fr(R['forets']['surface_totale_ha'])} ha<br>"
                 f"<b>Intensification agricole</b> — "
                 f"{fr(us['expansion_cerealiere_ha_an'])} ha défrichés chaque année, "
                 f"soit {us['ratio_defrichement_deforestation']:.1f} fois la perte "
                 f"forestière",
            font=dict(size=12, color=C["foret"]), align="left",
            bgcolor=rgba("foret", .08), borderpad=8)
        fig.update_xaxes(range=[0, pers_biomasse * 1.5], title="personnes",
                         tickvals=[0, 2e6, 4e6, 6e6, 8e6],
                         ticktext=["0", "2 M", "4 M", "6 M", "8 M"])
        fig.update_yaxes(title=None, range=[-1.3, 1.6])
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with g2:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    encart("constat",
           f"La cuisson propre concerne <b>{fr(pers_biomasse/1e6, 1)} millions</b> de "
           f"Togolais, soit {fr(pers_biomasse/pers_sans_elec, 1)} fois plus que "
           f"l'électrification rurale ({fr(pers_sans_elec/1e6, 1)} M). C'est aussi le "
           f"seul levier qui agisse simultanément sur la <b>santé</b> "
           f"({sa['mortalite']:.0f} décès pour 100 000 hab.), sur le <b>climat</b> "
           f"(méthane et N₂O de combustion incomplète) et sur la <b>forêt</b>. "
           f"D'où sa place en tête.")
    encart("methode",
           f"L'ordre n'est pas un classement d'importance mais un ordre "
           f"d'<b>efficacité par unité d'effort</b>, établi sur trois critères "
           f"mesurés : le nombre de personnes touchées, le nombre de problèmes "
           f"traités simultanément, et la <b>certitude du lien de causalité</b>. "
           f"Le levier 4 vient en dernier non parce qu'il pèse peu — il pèse "
           f"{us['ratio_defrichement_deforestation']:.1f} fois la perte forestière — "
           f"mais parce qu'il relève de la politique agricole, hors du périmètre "
           f"énergie du défi.")

# =========================================================== les quatre leviers
section("Les quatre leviers")

LEVIERS = [
    {
        "n": "1", "coul": C["risque"], "titre": "Cuisson propre",
        "quoi": "GPL subventionné en zone périurbaine et foyers améliorés certifiés "
                "en zone rurale enclavée, distribués via les réseaux existants "
                "(coopératives, marchés hebdomadaires, centres de santé).",
        "pourquoi": f"{cb['biomasse'][1]:.0f} % des ménages dépendent du bois ou du "
                    f"charbon, et cette part n'a pas bougé entre {cb['annees'][0]} et "
                    f"{cb['annees'][1]} — le bois brut a même gagné "
                    f"{fr(cb['bois'][1]-cb['bois'][0], 1)} points.",
        "ou": "Priorité aux cantons riverains des forêts classées du top 10 "
              "(voir la page « Forêts »), puis aux préfectures rurales des Plateaux "
              "et de la Centrale, les plus peuplées parmi les zones enclavées.",
        "cible": f"Passer de {fr(R['cuisson_rurale']['valeur'], 1)} % à 15 % d'accès "
                 f"rural à une cuisson propre en 2030.",
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
        "pourquoi": f"Le nombre de ruraux privés d'électricité a <b>augmenté de "
                    f"{tr['variation_pct']:.0f} %</b> depuis {tr['annee_debut']} "
                    f"malgré la hausse du taux d'accès : il faut franchir "
                    f"{fr(tr['seuil_stagnation']/1000)} 000 raccordements par an "
                    f"rien que pour stabiliser ce stock. Et le réseau lui-même reste "
                    f"instable : {fr(fi['coupures_mois'], 1)} coupures par mois, "
                    f"{fi['part_entreprises']:.0f} % des entreprises touchées.",
        "ou": "Zones à plus de 40 km d'un pôle urbain raccordé — celles-là mêmes qui "
              "ressortent en tête de l'indice d'enclavement. Priorité au Nord, où le "
              f"pic thermique de {R['climat']['mois_chaud_nom']} coïncide avec le "
              "maximum d'ensoleillement : la pointe de demande et la pointe de "
              "production solaire tombent au même moment.",
        "cible": f"Dépasser durablement {fr(tr['seuil_stagnation']/1000)} 000 "
                 f"raccordements ruraux par an — le seuil au-dessous duquel le "
                 f"nombre de personnes privées d'électricité continue de croître.",
        "suivi": "`EG.ELC.ACCS.RU.ZS` **converti en volume annuel de raccordements**, "
                 "complété par un indicateur de **disponibilité horaire** du service, "
                 "absent des données actuelles.",
    },
    {
        "n": "3", "coul": C["foret"],
        "titre": "Protection ciblée des massifs prioritaires",
        "quoi": "Concentrer surveillance, régénération assistée et plantations "
                "d'agroforesterie sur un nombre restreint de massifs, plutôt que "
                "de saupoudrer sur les 53 forêts classées.",
        "pourquoi": f"Le couvert forestier recule de {fr(PERTE)} ha par an depuis "
                    f"{dfr['regime_depuis']}, sans une seule année de reprise. Le "
                    f"rythme a été divisé par {rg['ralentissement']:.1f} après 2000, "
                    f"mais la série étant interpolée, elle serait <b>incapable de "
                    f"détecter un retournement récent</b>.",
        "ou": None,      # rempli dynamiquement ci-dessous
        "cible": "Stopper la perte nette sur les massifs prioritaires d'ici 2030.",
        "suivi": "`AG.LND.FRST.K2` au niveau national — mais cette série ne contient "
                 f"que {rg['n_mesures_independantes']} mesures indépendantes. Un "
                 "**suivi surfacique annuel par massif** est indispensable et "
                 "n'existe pas aujourd'hui.",
    },
    {
        "n": "4", "coul": C["charbon"],
        "titre": "Intensification agricole",
        "quoi": "Semences améliorées, restauration de la fertilité des sols et "
                "conseil agricole sur les bassins céréaliers riverains des massifs "
                "prioritaires, pour que produire plus cesse de signifier "
                "défricher plus.",
        "pourquoi": f"Le rendement céréalier togolais est de "
                    f"{fr(us['rendement_fin'], 2)} t/ha, et "
                    f"{us['part_surface_dans_production']:.0f} % de la hausse de "
                    f"production depuis {us['cereales_annee_debut']} vient de "
                    f"l'extension des surfaces. Le pays met en culture "
                    f"{fr(us['expansion_cerealiere_ha_an'])} ha de terres nouvelles "
                    f"par an, soit {us['ratio_defrichement_deforestation']:.1f} fois "
                    f"ce qu'il perd de forêt.",
        "ou": "Les bassins céréaliers des Plateaux, de la Centrale et de la Kara, "
              "qui jouxtent les massifs prioritaires du classement.",
        "cible": f"Ramener l'expansion des surfaces céréalières "
                 f"(+{fr(us['expansion_cerealiere_ha_an'])} ha/an) vers zéro en "
                 f"faisant porter la hausse de production par le seul rendement.",
        "suivi": "`AG.LND.CREL.HA` et `AG.PRD.CREL.MT`, lus ensemble comme un "
                 "rendement en t/ha — et la **surface** comme indicateur de "
                 "pression foncière.",
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
        f'<div style="background:{C["surface"]};border:1px solid {C["bord"]};'
        f'border-radius:10px;padding:18px 22px 19px;margin-bottom:13px">'
        f'<div style="display:flex;align-items:baseline;gap:14px">'
        f'<span style="font-family:{FONT_T};font-size:29px;font-weight:600;'
        f'color:{lv["coul"]};line-height:1">{lv["n"]}</span>'
        f'<span style="font-family:{FONT_T};font-size:21px;font-weight:600;'
        f'color:{C["encre"]}">{lv["titre"]}</span></div>'
        f'<div style="font-size:14px;color:{C["encre_2"]};margin-top:12px;'
        f'line-height:1.65">{lv["quoi"]}</div></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, (etiq, txt) in zip(
            [c1, c2, c3, c4],
            [("Ce qui le justifie", lv["pourquoi"]), ("Où agir en priorité", lv["ou"]),
             ("Cible 2030", lv["cible"]), ("Indicateur de suivi", lv["suivi"])]):
        with col:
            st.markdown(
                f'<div style="font-size:10.5px;font-weight:600;letter-spacing:.4px;'
                f'text-transform:uppercase;color:{C["sourdine"]};'
                f'margin-bottom:5px">{etiq}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:12.5px;color:{C["sourdine"]};'
                        f'line-height:1.55">{txt}</div>', unsafe_allow_html=True)
    st.write("")

# ====================================================== simulateur de trajectoire
section("Simulateur de trajectoire 2030",
        "Réglez l'ambition de chaque levier et lisez immédiatement où le Togo "
        "atterrit en 2030. Les trois scénarios pré-réglés donnent les points de "
        "repère : ce qui se passe sans rien changer, ce qu'exige l'objectif "
        "officiel, et ce que produit une politique centrée sur la cuisson.")

SCENARIOS = {
    "Tendanciel — sans rien changer": (round(er["rythme_observe"], 1), 0, 30),
    "Objectif officiel 2030": (min(12.0, round(er["rythme_requis_2030"], 1)), 25, 30),
    "Priorité à la cuisson": (round(er["rythme_observe"] * 2, 1), 50, 30),
}

with reglages("Hypothèses de la trajectoire",
              "Ces curseurs produisent une projection, jamais une donnée. "
              f"La perte forestière de référence est celle du régime en cours "
              f"({fr(PERTE)} ha/an depuis {dfr['regime_depuis']})."):
    cols_s = st.columns(len(SCENARIOS))
    for col, (nom_s, vals) in zip(cols_s, SCENARIOS.items()):
        with col:
            if st.button(nom_s, width="stretch", key=f"plan_scen_{nom_s}"):
                (st.session_state["plan_elec"], st.session_state["plan_cuis"],
                 st.session_state["plan_attr"]) = vals
                st.rerun()

    s1, s2, s3 = st.columns(3)
    with s1:
        v_elec = st.slider("Rythme d'électrification rurale (points/an)",
                           0.5, 12.0, float(round(er["rythme_observe"], 1)), 0.5,
                           key="plan_elec",
                           help=f"Rythme observé {er['annee_depart']}–{er['annee']} : "
                                f"+{fr(er['rythme_observe'], 2)} pt/an. "
                                f"Rythme requis pour 2030 : "
                                f"+{fr(er['rythme_requis_2030'], 1)} pt/an.")
    with s2:
        v_cuis = st.slider("Population sortie de la biomasse d'ici 2030 (%)",
                           0, 60, 25, 5, key="plan_cuis")
    with s3:
        v_attr = st.slider("Recul forestier imputable au bois-énergie (%)",
                           0, 100, 30, 5, key="plan_attr",
                           help="Hypothèse explicite. La page « Cuisson » montre que "
                                "l'expansion agricole suffit à elle seule à absorber "
                                "tout le recul forestier : une attribution majoritaire "
                                "au bois-énergie serait peu vraisemblable.")

annees = 2030 - er["annee"]
acces_2030 = min(100, er["valeur"] + v_elec * annees)
raccordes = R["ruraux_sans_elec"]["pop_rurale"] * (acces_2030 - er["valeur"]) / 100
raccordes_an = raccordes / annees
cuis_2030 = R["cuisson_rurale"]["valeur"] + v_cuis
perte_2030 = PERTE * (1 - (v_attr / 100) * (v_cuis / 100))
ha_sauves = (PERTE - perte_2030) * 5
# Le complément de l'attribution revient au foncier agricole : c'est la part
# que le levier 4 doit traiter, et elle se lit sur le même curseur.
perte_agricole = PERTE * (100 - v_attr) / 100

jetons(("Électrification", f"+{fr(v_elec, 1)} pt/an"),
       ("Sortie de la biomasse", f"{v_cuis} %"),
       ("Attribution bois-énergie", f"{v_attr} %"),
       ("Seuil de stagnation", f"{fr(tr['seuil_stagnation']/1000)} 000/an"),
       ("Nature du résultat", "projection"))

st.write("")
kpi_row([
    ("Accès rural en 2030", f"{acces_2030:.0f} %",
     f"contre {er['valeur']:.0f} % en {er['annee']} · "
     f"{'objectif atteint' if acces_2030 >= 99.5 else f'il manque {100-acces_2030:.0f} points'}",
     C["foret"] if acces_2030 >= 99.5 else C["risque"]),
    ("Raccordements annuels", f"{fr(raccordes_an/1000)} k/an",
     f"contre un seuil de stagnation à {fr(tr['seuil_stagnation']/1000)} 000/an — "
     f"{'au-dessus' if raccordes_an >= tr['seuil_stagnation'] else 'en dessous'}",
     C["foret"] if raccordes_an >= tr["seuil_stagnation"] else C["risque"]),
    ("Cuisson propre rurale", f"{fr(cuis_2030, 1)} %",
     f"contre {fr(R['cuisson_rurale']['valeur'], 1)} % en "
     f"{R['cuisson_rurale']['annee']}",
     C["foret"] if cuis_2030 >= 15 else C["risque"]),
    ("Perte forestière en 2030", f"{fr(perte_2030)} ha/an",
     f"contre {fr(PERTE)} ha/an aujourd'hui", C["risque"]),
    ("Reste au levier foncier", f"{fr(perte_agricole)} ha/an",
     f"la part du recul non imputée au bois-énergie, que seule "
     f"l'intensification agricole peut traiter", C["charbon"]),
])

st.write("")
# graphique « où l'on atterrit » : trois jauges alignées sur leurs cibles
JAUGES = [
    ("Accès rural à l'électricité", er["valeur"], acces_2030, 100, C["energie"]),
    ("Cuisson propre rurale", R["cuisson_rurale"]["valeur"], cuis_2030, 15,
     C["risque"]),
    ("Réduction de la perte forestière", 0,
     100 * (PERTE - perte_2030) / PERTE, 50, C["foret"]),
]
with st.container(border=True):
    titre_carte("Où atterrit le Togo en 2030 avec ces réglages",
                "Gris : situation observée aujourd'hui. Couleur : gain simulé. "
                "Trait noir : cible.", C["encre"])
    fig2 = go.Figure()
    noms = [j[0] for j in JAUGES]
    fig2.add_trace(go.Bar(y=noms, x=[100 for _ in JAUGES], orientation="h",
                          marker_color=C["neutre_l"], showlegend=False,
                          hoverinfo="skip", width=.52))
    fig2.add_trace(go.Bar(y=noms, x=[j[1] for j in JAUGES], orientation="h",
                          marker_color=C["neutre"], name="Aujourd'hui", width=.52,
                          hovertemplate="%{y} · aujourd'hui : %{x:.1f} %<extra></extra>"))
    fig2.add_trace(go.Bar(y=noms, x=[j[2] - j[1] for j in JAUGES], orientation="h",
                          marker_color=[j[4] for j in JAUGES],
                          name="Gain simulé d'ici 2030", width=.52,
                          hovertemplate="%{y} · gain : +%{x:.1f} pts<extra></extra>"))
    for i, j in enumerate(JAUGES):
        fig2.add_shape(type="line", x0=j[3], x1=j[3], y0=i - .34, y1=i + .34,
                       line=dict(color=C["encre"], width=2.6))
    fig2.add_trace(go.Scatter(x=[None], y=[None], mode="lines",
                              line=dict(color=C["encre"], width=2.6),
                              name="Cible 2030"))
    style_fig(fig2, hauteur=280, marge_g=0)
    fig2.update_layout(barmode="stack")
    fig2.update_xaxes(range=[0, 106], ticksuffix=" %", title=None)
    fig2.update_yaxes(title=None, autorange="reversed")
    st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})
    telecharger(pd.DataFrame([
        {"indicateur": j[0], "aujourdhui_pct": round(j[1], 2),
         "simule_2030_pct": round(j[2], 2), "cible_pct": j[3]} for j in JAUGES]
        + [{"indicateur": "hypothèse — rythme électrification (pt/an)",
            "aujourdhui_pct": round(er["rythme_observe"], 2),
            "simule_2030_pct": v_elec, "cible_pct": round(er["rythme_requis_2030"], 2)},
           {"indicateur": "hypothèse — sortie de la biomasse (%)",
            "aujourdhui_pct": 0, "simule_2030_pct": v_cuis, "cible_pct": None},
           {"indicateur": "hypothèse — attribution bois-énergie (%)",
            "aujourdhui_pct": None, "simule_2030_pct": v_attr, "cible_pct": None}]),
        "trajectoire_2030")

if acces_2030 >= 99.5 and cuis_2030 >= 15:
    encart("action",
           f"Avec ces réglages, les deux cibles majeures sont tenues. Le prix à payer "
           f"est explicite : un rythme d'électrification de +{fr(v_elec, 1)} points par "
           f"an, soit {v_elec/er['rythme_observe']:.0f} fois le rythme historique et "
           f"{fr(raccordes_an/1000)} 000 raccordements ruraux par an, et une politique "
           f"de cuisson propre touchant {v_cuis} % de la population. "
           f"C'est un choix d'investissement, pas une projection tendancielle.")
else:
    manque = []
    if acces_2030 < 99.5:
        manque.append(f"il manque {100-acces_2030:.0f} points d'accès rural")
    if cuis_2030 < 15:
        manque.append(f"la cuisson propre rurale reste à {fr(cuis_2030, 1)} %")
    encart("alerte",
           f"Avec ces réglages, l'objectif 2030 n'est pas tenu : {' et '.join(manque)}. "
           f"Faites glisser le curseur d'électrification vers "
           f"+{fr(er['rythme_requis_2030'], 1)} pt/an, ou cliquez sur « Objectif "
           f"officiel 2030 », pour voir l'effort réellement nécessaire.")

if raccordes_an < tr["seuil_stagnation"]:
    encart("alerte",
           f"<b>Attention au piège du taux.</b> Avec ce rythme, le Togo raccorderait "
           f"{fr(raccordes_an/1000)} 000 ruraux par an, soit moins que les "
           f"{fr(tr['seuil_stagnation']/1000)} 000 nécessaires pour compenser la seule "
           f"croissance de la population rurale. Le taux d'accès progresserait, et le "
           f"<b>nombre</b> de personnes privées d'électricité continuerait d'augmenter.",
           titre="Le taux progresse, le problème aussi")

# ============================================================ tableau récapitulatif
section("Récapitulatif décisionnel",
        "Une ligne par action, avec la donnée qui la justifie et l'indicateur qui "
        "la suit. C'est le tableau à emporter en réunion d'arbitrage.")

recap = pd.DataFrame([
    {"Priorité": "1", "Action": "GPL + foyers améliorés certifiés",
     "Où": "Cantons riverains du top 10, Plateaux et Centrale",
     "Cible 2030": "15 % d'accès rural à la cuisson propre",
     "Donnée qui la justifie": f"{cb['biomasse'][1]:.0f} % des ménages sur biomasse ; "
                              f"bois +{fr(cb['bois'][1]-cb['bois'][0], 1)} pt en 3 ans",
     "Indicateur de suivi": "EG.CFT.ACCS.RU.ZS"},
    {"Priorité": "2", "Action": "Mini-réseaux solaires + kits domestiques",
     "Où": "Zones à plus de 40 km d'un pôle raccordé, priorité Nord",
     "Cible 2030": f"Plus de {fr(tr['seuil_stagnation']/1000)} 000 raccordements "
                   f"ruraux par an",
     "Donnée qui la justifie": f"{tr['variation_pct']:+.0f} % de ruraux sans "
                              f"électricité depuis {tr['annee_debut']} ; "
                              f"{fi['part_entreprises']:.0f} % d'entreprises "
                              f"subissant des coupures",
     "Indicateur de suivi": "Volume annuel de raccordements + disponibilité "
                            "horaire (à créer)"},
    {"Priorité": "3", "Action": "Protection et régénération ciblées",
     "Où": f"Les {len(rb)} massifs robustes du classement",
     "Cible 2030": "Perte nette nulle sur les massifs prioritaires",
     "Donnée qui la justifie": f"{fr(PERTE)} ha/an perdus depuis "
                              f"{dfr['regime_depuis']}, sans année de reprise",
     "Indicateur de suivi": "Suivi surfacique annuel par massif (à créer) — "
                            "AG.LND.FRST.K2 est interpolé"},
    {"Priorité": "4", "Action": "Intensification agricole",
     "Où": "Bassins céréaliers riverains des massifs prioritaires",
     "Cible 2030": "Expansion des surfaces céréalières ramenée vers zéro",
     "Donnée qui la justifie": f"{fr(us['expansion_cerealiere_ha_an'])} ha défrichés/an "
                              f"= {us['ratio_defrichement_deforestation']:.1f} × la "
                              f"perte forestière ; rendement "
                              f"{fr(us['rendement_fin'], 2)} t/ha",
     "Indicateur de suivi": "AG.PRD.CREL.MT / AG.LND.CREL.HA (rendement t/ha)"},
    {"Priorité": "5", "Action": "Corriger le tableau de bord public de la transition",
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
telecharger(recap, "recapitulatif_decisionnel",
            "Récapitulatif décisionnel (CSV)")

# ==================================================== honnêteté méthodologique
section("Ce que ces données ne permettent pas de dire",
        "Le périmètre des recommandations s'arrête là où s'arrêtent les preuves. "
        "L'audit complet des séries et de leurs défauts est dans la page « Données ».")

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
- **Le lien cuisson → déforestation n'est pas mesuré.** Aucun fichier ne quantifie
  les prélèvements de bois-énergie. Ce que les données permettent, c'est de mesurer
  le moteur concurrent : l'expansion agricole gagne {us['ratio_agri_foret']:.1f} fois
  ce que la forêt perd. C'est pourquoi l'attribution reste un curseur, et pourquoi
  le levier 4 existe.
- **La série forestière ne contient que {rg['n_mesures_independantes']} mesures
  indépendantes** sur trente-deux points annuels : elle ne peut ni confirmer ni
  infirmer un retournement récent. C'est l'argument central en faveur d'un suivi
  surfacique par massif.
- **La fiabilité est mesurée sur les entreprises**, pas sur les ménages, et sur deux
  vagues d'enquête seulement ({fi['annee_ref']}, {fi['annee']}).
- **Les températures sont au degré entier**, sur sept ans : le gradient spatial est
  exploitable, la tendance temporelle ne l'est pas.
- **Trois indicateurs manquent** pour piloter correctement cette politique et
  devraient être créés : la disponibilité horaire du service électrique, un suivi
  surfacique par massif forestier, et une enquête ménages sur les combustibles plus
  fréquente que tous les trois ans.
""")

st.write("")
st.page_link("views/donnees.py",
             label="Voir l'audit complet de qualité des données et la méthode",
             icon=":material/rule:")

pied()

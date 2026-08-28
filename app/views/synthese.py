"""Vue d'ensemble — ce que lit un décideur pressé : diagnostic, preuve, décision."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   titre_carte, pied, fr, rgba, telecharger, jetons, FONT_T)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

er, ec, rs = R["elec_rural"], R["ecart_urbain_rural"], R["ruraux_sans_elec"]
cb, df_, fi = R["combustibles"], R["deforestation"], R["fiabilite"]
tr, rg = R["tapis_roulant"], R["regimes_foret"]

banniere(
    "Diagnostic national · vue d'ensemble",
    "Le taux d'électrification monte, le nombre de Togolais sans électricité aussi",
    "Le Togo vise l'accès universel à l'électricité en 2030. Confrontées les unes aux "
    "autres, les données du défi disent trois choses que chaque indicateur pris seul "
    "dissimule : le rattrapage rural est une illusion d'optique statistique, la forêt "
    "recule trois fois moins vite qu'on ne le dit mais sans jamais s'arrêter, et le vrai "
    "front énergétique est la marmite des ménages, pas l'ampoule.")

# ------------------------------------------------------------------ chiffres clés
# Chaque micro-courbe doit tracer LA grandeur de sa tuile, pas une grandeur
# voisine : une courbe qui ne correspond pas à son chiffre induit en erreur.
_elec = D.serie(nat, "elec_rural")
_prives = D.serie(nat, "ruraux_sans_elec")
_foret_km2 = D.serie(nat, "foret_km2")

kpi_row([
    ("Accès rural à l'électricité", f"{er['valeur']:.0f} %",
     f"contre {ec['urbain']:.0f} % en ville en {ec['annee']} — un écart de "
     f"{ec['valeur']:.0f} points", C["energie"],
     f"+{fr(er['rythme_observe'], 1)} pt/an", list(_elec["valeur"]),
     (str(er["annee_depart"]), str(er["annee"]))),
    ("Ruraux privés d'électricité", f"{fr(tr['sans_elec_fin']/1e6, 2)} M",
     f"de personnes — soit {fr(tr['variation']/1000)} 000 de <b>plus</b> qu'en "
     f"{tr['annee_debut']}, alors que le taux d'accès a été multiplié par "
     f"{er['valeur']/er['valeur_depart']:.0f}",
     C["risque"], f"+{tr['variation_pct']:.0f} %",
     list(_prives["valeur"]),
     (str(tr["annee_debut"]), str(tr["annee_fin"]))),
    ("Ménages au bois ou au charbon", f"{cb['biomasse'][1]:.0f} %",
     f"en {cb['annees'][1]} — la dépendance n'a pas reculé depuis "
     f"{cb['annees'][0]}, où elle était de {cb['biomasse'][0]:.0f} %",
     C["risque"], "stable"),
    ("Forêt perdue chaque année", f"{fr(df_['perte_actuelle_ha_an'])} ha/an",
     f"dans le régime en cours depuis {df_['regime_depuis']} — trois fois moins "
     f"que dans les années 1990, mais sans une seule année de reprise",
     C["risque"], f"÷ {rg['ralentissement']:.1f} après 2000"),
    ("Accélération requise", f"× {er['facteur_acceleration']:.0f}",
     f"pour l'accès universel rural en 2030 : il faudrait "
     f"+{fr(er['rythme_requis_2030'], 1)} pt/an au lieu de "
     f"+{fr(er['rythme_observe'], 1)}", C["risque"], "hors trajectoire"),
])

st.write("")
encart("alerte",
       f"<b>Le taux d'accès rural a été multiplié par "
       f"{er['valeur']/er['valeur_depart']:.0f} depuis {tr['annee_debut']}. Le nombre "
       f"de ruraux privés d'électricité, lui, a augmenté de "
       f"{tr['variation_pct']:.0f} %.</b> Les deux affirmations sont vraies en même "
       f"temps, et c'est le résultat central de ce tableau de bord : un taux est un "
       f"rapport, et son dénominateur — la population rurale — a gagné "
       f"{fr((tr['pop_rurale_fin']-tr['pop_rurale_debut'])/1e6, 1)} million de personnes "
       f"sur la même période. Piloter la politique d'électrification sur le taux, c'est "
       f"piloter sur l'indicateur qui progresse pendant que le problème grandit.",
       titre="Le résultat qui commande tout le reste")

# ------------------------------------------------- le tapis roulant démographique
section("Le tapis roulant démographique",
        "À gauche, les deux courbes qui montent ensemble. À droite, la décomposition "
        f"exacte de la variation du stock entre {tr['annee_debut']} et "
        f"{tr['annee_fin']} — elle ne fait appel à aucune hypothèse.")
jetons(("Source", "Banque Mondiale, 2 séries"),
       ("Méthode", "identité comptable, sans hypothèse"),
       ("Période", f"{tr['annee_debut']}–{tr['annee_fin']}"))

g1, g2 = st.columns([1.25, 1])

with g1:
    with st.container(border=True):
        titre_carte("Le taux progresse, le nombre de personnes aussi",
                    "Deux panneaux, un seul axe du temps. En haut le taux d'accès, "
                    "en bas les personnes qu'il laisse de côté.", C["risque"])
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=.10, row_heights=[.44, .56])
        fig.add_trace(go.Scatter(
            x=_elec["annee"], y=_elec["valeur"], name="Taux d'accès rural",
            line=dict(color=C["energie"], width=3.2), mode="lines",
            hovertemplate="%{x} · %{y:.1f} % de la population rurale"
                          "<extra>Taux d'accès</extra>"), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=_prives["annee"], y=_prives["valeur"] / 1e6,
            name="Ruraux privés d'électricité",
            line=dict(color=C["risque"], width=3.2), mode="lines",
            fill="tozeroy", fillcolor=rgba("risque", .10),
            hovertemplate="%{x} · %{y:.2f} million de personnes"
                          "<extra>Sans électricité</extra>"), row=2, col=1)
        style_fig(fig, hauteur=392)
        fig.update_yaxes(title=None, ticksuffix=" %", range=[0, 30], row=1, col=1)
        fig.update_yaxes(title=None, ticksuffix=" M", range=[0, 4.4], row=2, col=1)
        fig.update_xaxes(title=None)
        annote(fig, int(_elec["annee"].iloc[-1]), float(_elec["valeur"].iloc[-1]),
               f"{_elec['valeur'].iloc[-1]:.0f} %", C["energie"], ax=-28, ay=-24,
               row=1, col=1)
        annote(fig, int(_prives["annee"].iloc[-1]),
               float(_prives["valeur"].iloc[-1]) / 1e6,
               f"{fr(tr['sans_elec_fin']/1e6, 2)} M — <b>+{tr['variation_pct']:.0f} %</b> "
               f"depuis {tr['annee_debut']}", C["risque"], ax=-104, ay=-26, row=2, col=1)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        telecharger(pd.DataFrame({
            "annee": _prives["annee"],
            "acces_rural_pct": _elec.set_index("annee")["valeur"].reindex(
                _prives["annee"]).values,
            "ruraux_sans_electricite": _prives["valeur"].round(0)}),
            "tapis_roulant_electrification")

with g2:
    with st.container(border=True):
        titre_carte("D'où vient la hausse du stock",
                    "Identité comptable exacte : la somme des deux effets "
                    "reconstitue la variation observée, au chiffre près.", C["risque"])
        fig2 = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=[f"{tr['annee_debut']}", "Croissance de la<br>population rurale",
               "Effet de<br>l'électrification", f"{tr['annee_fin']}"],
            y=[tr["sans_elec_debut"], tr["effet_demographie"],
               tr["effet_acces"], 0],
            text=[f"{fr(tr['sans_elec_debut']/1e6, 2)} M",
                  f"+{fr(tr['effet_demographie']/1e6, 2)} M",
                  f"−{fr(abs(tr['effet_acces'])/1e6, 2)} M",
                  f"{fr(tr['sans_elec_fin']/1e6, 2)} M"],
            textposition="outside", textfont=dict(size=11.5),
            connector=dict(line=dict(color=C["bord_fort"], width=1)),
            increasing=dict(marker=dict(color=C["risque"])),
            decreasing=dict(marker=dict(color=C["foret"])),
            totals=dict(marker=dict(color=C["encre_2"])),
            hovertemplate="%{x}<br>%{y:,.0f} personnes<extra></extra>"))
        style_fig(fig2, hauteur=392, marge_g=0)
        fig2.update_yaxes(title="personnes privées d'électricité",
                          range=[0, 5.4e6],
                          tickvals=[0, 1e6, 2e6, 3e6, 4e6, 5e6],
                          ticktext=["0", "1 M", "2 M", "3 M", "4 M", "5 M"])
        fig2.update_xaxes(title=None, tickfont=dict(size=10.5))
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})
        telecharger(pd.DataFrame([
            {"poste": f"stock {tr['annee_debut']}", "personnes": tr["sans_elec_debut"]},
            {"poste": "effet démographie", "personnes": tr["effet_demographie"]},
            {"poste": "effet électrification", "personnes": tr["effet_acces"]},
            {"poste": f"stock {tr['annee_fin']}", "personnes": tr["sans_elec_fin"]},
        ]), "decomposition_stock_sans_electricite")

encart("constat",
       f"L'électrification a bien sorti <b>{fr(abs(tr['effet_acces'])/1e6, 2)} million</b> "
       f"de ruraux de l'obscurité en {tr['annee_fin']-tr['annee_debut']} ans. Mais la "
       f"population rurale en a ajouté <b>{fr(tr['effet_demographie']/1e6, 2)} million</b> "
       f"qui n'y avaient pas accès. Le raccordement n'annule que "
       f"<b>{tr['taux_compensation']:.0f} %</b> de la poussée démographique : le reste "
       f"s'accumule. Conséquence opérationnelle immédiate — il faut raccorder "
       f"<b>{fr(tr['seuil_stagnation']/1000)} 000 ruraux par an</b> rien que pour que le "
       f"nombre de personnes privées d'électricité cesse d'augmenter, avant même de "
       f"commencer à le réduire — c'est très exactement la croissance annuelle de la "
       f"population rurale. Sur {tr['annee_debut_decennie']}–{tr['annee_fin']}, "
       f"{fr(tr['raccordements_moyens_10ans'])} raccordements par an ont été réalisés "
       f"pour un seuil moyen de {fr(tr['seuil_moyen_10ans'])} : le déficit de "
       f"<b>{fr(tr['seuil_moyen_10ans']-tr['raccordements_moyens_10ans'])} personnes "
       f"par an</b> explique, au chiffre près, les "
       f"{fr(tr['variation_decennie'])} personnes supplémentaires sans électricité "
       f"sur la décennie.")

# ------------------------------------------------- la preuve : électrifier ≠ sauver la forêt
section("Électrifier ne suffit pas à sauver la forêt",
        "L'accès progresse depuis vingt-cinq ans ; le couvert forestier recule sans "
        "discontinuer sur la même période. La troisième courbe dit pourquoi.")

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
    fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         vertical_spacing=.09, row_heights=[.58, .42])
    fig3.add_trace(go.Scatter(
        x=elec["annee"], y=elec["valeur"], name="Accès rural à l'électricité",
        line=dict(color=C["energie"], width=3.4), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Accès rural</extra>"), row=1, col=1)
    fig3.add_trace(go.Scatter(
        x=cuis["annee"], y=cuis["valeur"], name="Accès rural à une cuisson propre",
        line=dict(color=C["risque"], width=2.6, dash="dot"), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Cuisson propre rurale</extra>"),
        row=1, col=1)
    fig3.add_trace(go.Scatter(
        x=foret["annee"], y=foret["valeur"], name="Couvert forestier (% du territoire)",
        line=dict(color=C["foret"], width=3.4), mode="lines",
        hovertemplate="%{x} · %{y:.1f} %<extra>Couvert forestier</extra>"),
        row=2, col=1)

    style_fig(fig3, hauteur=420)
    # Pas de titre d'axe : la légende nomme déjà chaque série avec son unité,
    # et deux titres verticaux sur deux panneaux se chevauchaient.
    fig3.update_yaxes(title=None, ticksuffix=" %", range=[0, 40], row=1, col=1)
    fig3.update_yaxes(title=None, ticksuffix=" %", row=2, col=1)
    fig3.update_xaxes(title=None)
    if len(elec):
        annote(fig3, int(elec["annee"].iloc[-1]), float(elec["valeur"].iloc[-1]),
               f"{elec['valeur'].iloc[-1]:.0f} %", C["energie"], ax=-30, ay=-26,
               row=1, col=1)
    if len(cuis):
        annote(fig3, int(cuis["annee"].iloc[-1]), float(cuis["valeur"].iloc[-1]),
               f"{fr(cuis['valeur'].iloc[-1], 1)} % — quasi nul", C["risque"],
               ax=-58, ay=26, row=1, col=1)
    if len(foret) > 1:
        annote(fig3, int(foret["annee"].iloc[-1]), float(foret["valeur"].iloc[-1]),
               f"{fr(foret['valeur'].iloc[0], 1)} % → {fr(foret['valeur'].iloc[-1], 1)} % "
               f"du territoire", C["foret"], ax=-96, ay=-20, row=2, col=1)
    st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})
    telecharger(pd.DataFrame({"annee": elec["annee"],
                              "acces_elec_rural_pct": elec["valeur"]}).merge(
        pd.DataFrame({"annee": cuis["annee"], "cuisson_propre_rurale_pct": cuis["valeur"]}),
        on="annee", how="outer").merge(
        pd.DataFrame({"annee": foret["annee"], "couvert_forestier_pct": foret["valeur"]}),
        on="annee", how="outer").sort_values("annee"), "acces_energie_et_foret")

encart("constat",
       f"Entre {int(elec['annee'].iloc[0]) if len(elec) else an_min} et {er['annee']}, "
       f"l'accès rural à l'électricité a été multiplié par "
       f"{er['valeur']/er['valeur_depart']:.0f}. Le couvert forestier, lui, n'a jamais "
       f"cessé de reculer. La raison tient dans la troisième courbe : la <b>cuisson</b> "
       f"propre rurale reste à {fr(R['cuisson_rurale']['valeur'], 1)} %. L'électricité "
       f"éclaire les foyers, elle ne remplace pas le bois dans les marmites — et c'est "
       f"la marmite, pas l'ampoule, qui consomme la forêt.")

# ------------------------------------------------------------------ quatre constats
section("Quatre constats, quatre pages",
        "Chaque constat est démontré, chiffré et sourcé dans la page correspondante.")

CARTES = [
    ("Électrification", C["energie"],
     "Le retard rural ne se comble pas assez vite",
     f"{ec['valeur']:.0f} points d'écart ville/campagne, et un réseau fragile : "
     f"{fr(fi['coupures_mois'], 1)} coupures par mois, {fi['part_entreprises']:.0f} % des "
     f"entreprises touchées en {fi['annee']}.", "Voir la page", "views/acces.py"),
    ("Cuisson", C["risque"],
     "Le « renouvelable » togolais, c'est du bois de feu",
     f"{R['renouvelable_piege']['part_renouvelable']:.0f} % de l'énergie finale est classée "
     f"renouvelable, mais seulement "
     f"{R['renouvelable_piege']['part_cuisson_propre']:.0f} % des ménages cuisinent "
     f"proprement. Renouvelable ne veut pas dire propre.", "Voir la page",
     "views/cuisson.py"),
    ("Inventaire", C["urbain"],
     "L'énergie n'est marginale qu'en dioxyde de carbone",
     f"Le secteur énergie ne pèse que {R['ges']['part_energie']:.0f} % des émissions "
     f"totales, mais {R['ges']['energie_dans_n2o']:.0f} % du protoxyde d'azote et "
     f"{R['ges']['energie_dans_ch4']:.0f} % du méthane.", "Voir la page",
     "views/emissions.py"),
    ("Forêts", C["foret"],
     "Neuf massifs concentrent toute la priorité",
     f"Sur les {R['forets']['nb']} forêts classées, {R['forets']['nb_robustes']} restent "
     f"dans le top 10 quelle que soit la pondération testée. La cible d'investissement "
     f"est identifiée.", "Voir la page", "views/priorisation.py"),
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
       f"Quatre leviers sortent des données, dans cet ordre de priorité : "
       f"<b>(1)</b> la cuisson propre, parce qu'elle touche {cb['biomasse'][1]:.0f} % des "
       f"ménages et {R['sante']['mortalite']:.0f} décès pour 100 000 habitants via la "
       f"pollution de l'air ; <b>(2)</b> le solaire décentralisé, seul capable de "
       f"combler le déficit de "
       f"{fr(tr['seuil_moyen_10ans']-tr['raccordements_moyens_10ans'])} raccordements "
       f"annuels en dessous duquel le nombre de ruraux sans électricité continue "
       f"d'augmenter ; "
       f"<b>(3)</b> la protection ciblée des {R['forets']['nb_robustes']} forêts "
       f"prioritaires ; et <b>(4)</b> l'intensification agricole, car l'expansion des "
       f"cultures avance "
       f"{R['usage_sols']['ratio_defrichement_deforestation']:.0f} fois plus vite que "
       f"la forêt ne recule.")
st.write("")
liens = st.columns(2)
with liens[0]:
    st.page_link("views/plan.py",
                 label="Voir le plan d'action chiffré et le simulateur 2030",
                 icon=":material/checklist:")
with liens[1]:
    st.page_link("views/donnees.py",
                 label="Voir l'audit de qualité des données et la méthode",
                 icon=":material/rule:")

pied()

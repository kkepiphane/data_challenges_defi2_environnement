"""Accès à l'électricité (ville / campagne), rythme réel et fiabilité du réseau."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   pied, fr, titre_carte, rgba, telecharger, reglages, jetons)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

er, ec, rs, fi = (R["elec_rural"], R["ecart_urbain_rural"],
                  R["ruraux_sans_elec"], R["fiabilite"])
tr, te = R["tapis_roulant"], R["tendance_elec"]

banniere("Accès à l'électricité et qualité du réseau",
         f"Il manque {fr(tr['seuil_moyen_10ans']-tr['raccordements_moyens_10ans'])} "
         f"raccordements par an rien que pour ne pas reculer",
         "Trois questions commandent la stratégie d'électrification : à quelle vitesse "
         "l'écart ville / campagne se referme-t-il, ce rythme suffit-il seulement à "
         "compenser la croissance de la population rurale, et le courant, une fois "
         "arrivé, est-il fiable ? Les trois réponses pointent vers la même solution.")

# séries complètes pour les micro-courbes des tuiles
_r = D.serie(nat, "elec_rural")
_u = D.serie(nat, "elec_urbain")
_ecart = list((_u.set_index("annee")["valeur"] - _r.set_index("annee")["valeur"]).dropna())
_racc = D.serie(nat, "raccordes_par_an")

kpi_row([
    ("Accès rural", f"{er['valeur']:.0f} %",
     f"de la population rurale en {er['annee']}, contre "
     f"{fr(er['valeur_depart'], 1)} % en {er['annee_depart']}", C["energie"],
     f"× {er['valeur']/er['valeur_depart']:.0f} en {er['annee']-er['annee_depart']} ans",
     list(_r["valeur"])),
    ("Écart ville / campagne", f"{ec['valeur']:.0f} pts",
     f"{ec['urbain']:.0f} % en ville contre {ec['rural']:.0f} % en campagne — "
     f"l'ampleur de la fracture à combler d'ici 2030", C["risque"],
     "au plus haut", _ecart),
    ("Déficit de raccordement", f"{fr(tr['seuil_moyen_10ans']-tr['raccordements_moyens_10ans'])} /an",
     f"personnes de retard chaque année sur la seule croissance démographique, "
     f"en moyenne {tr['annee_debut_decennie']}–{tr['annee_fin']}", C["risque"],
     f"{fr(tr['variation_decennie']/1000)} 000 cumulés",
     list(_racc["valeur"])),
    ("Coupures subies", f"{fr(fi['coupures_mois'], 1)} /mois",
     f"par les entreprises raccordées en {fi['annee']} "
     f"(enquête Banque Mondiale)", C["risque"],
     f"{fi['part_entreprises']:.0f} % touchées",
     [fi["coupures_mois_ref"], fi["coupures_mois"]]),
])

# =============================================================================
onglet1, onglet2, onglet3 = st.tabs([" La fracture et sa trajectoire ",
                                     " Le rythme réel des raccordements ",
                                     " La fiabilité du réseau "])

# -------------------------------------------------------------- 1. LA FRACTURE
with onglet1:
    section("Trajectoire de l'accès, et ce qu'il faudrait pour 2030",
            "Réglez la cible : le tableau de bord recalcule l'effort annuel "
            "correspondant, en points de pourcentage et en personnes.")

    with reglages("Réglages de la trajectoire",
                  "Le scénario tendanciel prolonge le rythme moyen observé depuis "
                  f"{er['annee_depart']} ; le scénario cible relie la valeur "
                  "actuelle à l'objectif choisi."):
        f1, f2, f3 = st.columns([1.2, 1, 1])
        with f1:
            cible = st.slider("Cible d'accès rural en 2030 (%)", 40, 100, 100, 5,
                              key="acces_cible",
                              help="Objectif national officiel : accès universel "
                                   "en 2030.")
        with f2:
            montrer_proj = st.toggle("Afficher les trajectoires", value=True,
                                     key="acces_proj")
        with f3:
            montrer_ic = st.toggle("Afficher l'incertitude", value=True,
                                   key="acces_ic",
                                   help="Intervalle de confiance à 95 % de la pente "
                                        "estimée par moindres carrés sur les "
                                        f"{te['periode'][1]-te['periode'][0]+1} "
                                        "points observés.")

    rural = D.serie(nat, "elec_rural", an_min, an_max)
    urbain = D.serie(nat, "elec_urbain", an_min, an_max)
    total = D.serie(nat, "elec_total", an_min, an_max)

    jetons(("Cible 2030", f"{cible} %"),
           ("Période affichée", f"{an_min}–{an_max}"),
           ("Incertitude", "affichée" if montrer_ic else "masquée"))

    with st.container(border=True):
        titre_carte("Accès à l'électricité, ville contre campagne",
                    "La zone rouge mesure la fracture. Réglez la cible pour voir "
                    "l'effort requis.", C["energie"])
        fig = go.Figure()
        # bande d'écart ville/campagne : la fracture devient une surface, pas deux courbes
        fig.add_trace(go.Scatter(x=urbain["annee"], y=urbain["valeur"], name="Urbain",
                                 line=dict(color=C["urbain"], width=3), mode="lines",
                                 hovertemplate="%{x} · %{y:.1f} %<extra>Urbain</extra>"))
        fig.add_trace(go.Scatter(x=rural["annee"], y=rural["valeur"], name="Rural",
                                 line=dict(color=C["energie"], width=3), mode="lines",
                                 fill="tonexty", fillcolor=rgba("risque", .10),
                                 hovertemplate="%{x} · %{y:.1f} %<extra>Rural</extra>"))
        fig.add_trace(go.Scatter(x=total["annee"], y=total["valeur"],
                                 name="Ensemble du pays",
                                 line=dict(color=C["sourdine"], width=1.8, dash="dot"),
                                 mode="lines",
                                 hovertemplate="%{x} · %{y:.1f} %<extra>Ensemble</extra>"))

        a0, v0 = er["annee"], er["valeur"]
        if montrer_proj:
            ans = np.arange(a0, 2031)
            tend = np.clip(v0 + er["rythme_observe"] * (ans - a0), 0, 100)
            vers = v0 + (cible - v0) * (ans - a0) / (2030 - a0)
            if montrer_ic:
                # L'enveloppe n'est pas décorative : elle montre que la conclusion
                # « hors trajectoire » ne dépend pas de la pente retenue. Même la
                # borne haute de l'intervalle laisse le Togo très loin de 2030.
                haut = np.clip(v0 + te["pente_haute"] * (ans - a0), 0, 100)
                bas = np.clip(v0 + te["pente_basse"] * (ans - a0), 0, 100)
                fig.add_trace(go.Scatter(
                    x=np.concatenate([ans, ans[::-1]]),
                    y=np.concatenate([haut, bas[::-1]]),
                    fill="toself", fillcolor=rgba("risque", .12),
                    line=dict(width=0), hoverinfo="skip",
                    name="Incertitude à 95 % de la pente"))
            fig.add_trace(go.Scatter(x=ans, y=tend, name="Tendanciel (rythme actuel)",
                                     line=dict(color=C["risque"], width=2, dash="dash"),
                                     mode="lines",
                                     hovertemplate="%{x} · %{y:.1f} %"
                                                   "<extra>Tendanciel</extra>"))
            fig.add_trace(go.Scatter(x=ans, y=vers, name=f"Trajectoire vers {cible} %",
                                     line=dict(color=C["foret"], width=2.4), mode="lines",
                                     hovertemplate="%{x} · %{y:.1f} %<extra>Cible</extra>"))
            fig.add_vrect(x0=a0, x1=2030, fillcolor=C["neutre"], opacity=.06, line_width=0)
            annote(fig, 2030, cible, f"Cible {cible} %", C["foret"], ax=-42, ay=-24)
            annote(fig, 2030, float(tend[-1]), f"Tendanciel {tend[-1]:.0f} %",
                   C["risque"], ax=-52, ay=30)

        style_fig(fig, hauteur=430)
        fig.update_yaxes(title="% de la population", ticksuffix=" %", range=[0, 105])
        fig.update_xaxes(title=None)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        telecharger(pd.DataFrame({"annee": rural["annee"],
                                  "rural_pct": rural["valeur"]}).merge(
            pd.DataFrame({"annee": urbain["annee"], "urbain_pct": urbain["valeur"]}),
            on="annee", how="outer").merge(
            pd.DataFrame({"annee": total["annee"], "ensemble_pct": total["valeur"]}),
            on="annee", how="outer").sort_values("annee"), "acces_electricite")

    # ---- l'effort traduit en personnes, pas en points de pourcentage
    pop_rur = rs["pop_rurale"]
    annees_restantes = 2030 - er["annee"]
    pts_requis = (cible - er["valeur"]) / annees_restantes
    pers_total = pop_rur * (cible - er["valeur"]) / 100
    pers_an = pers_total / annees_restantes
    pers_tend_an = pop_rur * er["rythme_observe"] / 100

    st.write("")
    kpi_row([
        ("Rythme requis", f"+{fr(pts_requis, 1)} pt/an",
         f"pour atteindre {cible} % en 2030", C["foret"]),
        ("Rythme observé", f"+{fr(er['rythme_observe'], 2)} pt/an",
         f"moyenne {er['annee_depart']}–{er['annee']}", C["risque"],
         f"× {pts_requis/er['rythme_observe']:.0f} à trouver"
         if er["rythme_observe"] else None),
        ("Personnes à raccorder", f"{fr(pers_an/1000)} k/an",
         f"soit {fr(pers_total/1e6, 1)} millions de ruraux d'ici 2030",
         C["energie"]),
        ("Au rythme actuel", f"{fr(pers_tend_an/1000)} k/an",
         f"l'accès universel rural serait atteint vers "
         f"{er['annee_atteinte_tendanciel']:.0f}", C["neutre"]),
    ])

    st.write("")
    encart("constat",
           f"L'écart ville / campagne est de <b>{ec['valeur']:.0f} points</b> "
           f"({ec['urbain']:.0f} % contre {ec['rural']:.0f} %). Il ne s'agit pas d'un "
           f"retard qui se comble : sur {er['annee']-er['annee_depart']} ans, le rural "
           f"a gagné {er['valeur']-er['valeur_depart']:.0f} points quand l'urbain "
           f"saturait. Atteindre {cible} % en 2030 suppose de raccorder "
           f"<b>{fr(pers_an/1000)} 000 ruraux par an</b>, contre environ "
           f"{fr(pers_tend_an/1000)} 000 aujourd'hui.")

    encart("methode",
           f"<b>La conclusion ne dépend pas de la méthode d'estimation.</b> Le rythme "
           f"affiché ci-dessus est celui du premier au dernier point "
           f"(+{fr(er['rythme_observe'], 2)} pt/an). Une régression par moindres carrés "
           f"sur les {te['periode'][1]-te['periode'][0]+1} points de la série donne "
           f"+{fr(te['pente'], 2)} pt/an (r² = {fr(te['r2'], 3)}), avec un intervalle de "
           f"confiance à 95 % de {fr(te['pente_basse'], 2)} à {fr(te['pente_haute'], 2)} "
           f"pt/an — soit un accès universel rural entre "
           f"<b>{te['annee_atteinte_optimiste']:.0f} et "
           f"{te['annee_atteinte_pessimiste']:.0f}</b>. Et la seule dernière décennie "
           f"({te['periode_recente'][0]}–{te['periode_recente'][1]}) progresse à "
           f"+{fr(te['pente_recente'], 2)} pt/an, c'est-à-dire "
           f"{'moins' if te['pente_recente'] < te['pente'] else 'pas plus'} vite que la "
           f"moyenne longue : le retard n'est pas en train de se résorber. "
           f"Quelle que soit l'estimation retenue, 2030 est hors d'atteinte par "
           f"prolongement de la tendance.",
           titre="Robustesse de la projection")

    encart("action",
           "Un facteur d'accélération de cet ordre ne s'obtient pas en prolongeant le "
           "réseau national, dont le coût au raccordement croît avec la distance et la "
           "dispersion de l'habitat. Il s'obtient par des solutions décentralisées — "
           "mini-réseaux solaires et kits domestiques — déployables sans attendre la "
           "ligne moyenne tension. Les deux onglets suivants ajoutent chacun une raison "
           "de le faire.")

# ------------------------------------------------- 2. LE RYTHME DES RACCORDEMENTS
with onglet2:
    section("Combien de personnes sont réellement raccordées chaque année",
            "Le taux d'accès masque le volume. Ce graphique compare ce qui est fait "
            "à deux seuils calculés : celui qui empêche le stock de croître, et "
            "celui qui mène à la cible.")

    with reglages("Réglages de la comparaison",
                  "Les deux seuils sont recalculés à partir des séries observées, "
                  "sans hypothèse de croissance future."):
        h1, h2 = st.columns([1.2, 1])
        with h1:
            cible2 = st.slider("Cible d'accès rural en 2030 (%)", 40, 100, 100, 5,
                               key="acces_cible2",
                               help="Le seuil « cible » se recalcule en direct.")
        with h2:
            lissage = st.toggle("Lisser sur trois ans", value=True,
                                key="acces_lissage",
                                help="Les enquêtes d'accès sont bruitées d'une année "
                                     "à l'autre : la moyenne mobile montre le rythme "
                                     "de fond plutôt que les à-coups de mesure.")

    seuil_s = D.serie(nat, "seuil_stagnation")
    racc = _racc.merge(seuil_s.rename(columns={"valeur": "seuil"}), on="annee")
    racc = racc[(racc["annee"] >= an_min) & (racc["annee"] <= an_max)]
    serie_aff = (racc["valeur"].rolling(3, center=True, min_periods=1).mean()
                 if lissage else racc["valeur"])

    besoin_cible = (rs["pop_rurale"] * (cible2 - er["valeur"]) / 100
                    / (2030 - er["annee"]))
    deficit = tr["seuil_moyen_10ans"] - tr["raccordements_moyens_10ans"]
    jetons(("Cible 2030", f"{cible2} %"),
           ("Seuil en " + str(tr["annee_fin"]), f"{fr(tr['seuil_stagnation'])}/an"),
           ("Besoin pour la cible", f"{fr(besoin_cible/1000)} 000/an"),
           ("Lissage", "3 ans" if lissage else "aucun"))

    with st.container(border=True):
        titre_carte("Raccordements ruraux annuels, face à deux seuils",
                    "Barres : personnes nouvellement raccordées, calculées comme la "
                    "variation d'une année à l'autre du produit population × taux "
                    "d'accès. La ligne rouge est la croissance de la population "
                    "rurale — le seuil exact au-dessous duquel le stock augmente.",
                    C["energie"])
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=racc["annee"], y=serie_aff,
            marker_color=[C["foret"] if v >= s else C["energie"]
                          for v, s in zip(serie_aff, racc["seuil"])],
            name="Raccordements réalisés",
            hovertemplate="%{x} · %{y:,.0f} personnes raccordées<extra></extra>"))
        fig2.add_trace(go.Scatter(
            x=racc["annee"], y=racc["seuil"], mode="lines",
            line=dict(color=C["risque"], width=2.4, dash="dash"),
            name="Seuil : croissance de la population rurale",
            hovertemplate="%{x} · seuil %{y:,.0f} personnes<extra></extra>"))
        fig2.add_hline(y=besoin_cible, line=dict(color=C["encre"], width=2))
        style_fig(fig2, hauteur=400)
        fig2.update_yaxes(title="personnes par an",
                          range=[min(0, float(serie_aff.min()) * 1.15),
                                 max(float(besoin_cible),
                                     float(serie_aff.max()),
                                     float(racc["seuil"].max())) * 1.24])
        fig2.update_xaxes(title=None, dtick=3)
        fig2.add_annotation(
            x=racc["annee"].iloc[0], y=besoin_cible, xanchor="left", yanchor="bottom",
            text=f"<b>{fr(besoin_cible/1000)} 000/an</b> — rythme nécessaire pour "
                 f"atteindre {cible2} % en 2030",
            showarrow=False, font=dict(size=11, color=C["encre"]),
            bgcolor="rgba(255,255,255,.92)", borderpad=3)
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})
        telecharger(pd.DataFrame({
            "annee": racc["annee"],
            "raccordements_annuels": racc["valeur"].round(0),
            "affiche_lisse": serie_aff.round(0),
            "seuil_stagnation": racc["seuil"].round(0),
            "besoin_cible_2030": besoin_cible}), "raccordements_annuels")

    st.write("")
    au_dessus = int((racc["valeur"] >= racc["seuil"]).sum())
    kpi_row([
        ("Rythme moyen récent", f"{fr(tr['raccordements_moyens_10ans']/1000)} k/an",
         f"raccordements réalisés en moyenne sur "
         f"{tr['annee_debut_decennie']}–{tr['annee_fin']}", C["energie"]),
        ("Seuil moyen sur la même décennie",
         f"{fr(tr['seuil_moyen_10ans']/1000)} k/an",
         "la croissance de la population rurale, qu'il faut d'abord absorber",
         C["risque"]),
        ("Déficit annuel", f"{fr(deficit/1000)} k/an",
         f"l'écart entre les deux — soit {fr(tr['variation_decennie']/1000)} 000 "
         f"personnes de plus sans électricité en dix ans", C["risque"]),
        ("Années au-dessus du seuil", f"{au_dessus} ans",
         f"sur les {len(racc)} années de la période affichée",
         C["foret"] if au_dessus > len(racc) / 2 else C["risque"]),
        ("Besoin pour la cible", f"{fr(besoin_cible/1000)} k/an",
         f"soit {besoin_cible/max(tr['raccordements_moyens_10ans'], 1):.1f} fois le "
         f"rythme moyen récent", C["risque"]),
    ])

    st.write("")
    encart("alerte",
           f"<b>Le stock de ruraux privés d'électricité est passé de "
           f"{fr(tr['sans_elec_debut']/1e6, 2)} à {fr(tr['sans_elec_fin']/1e6, 2)} "
           f"millions entre {tr['annee_debut']} et {tr['annee_fin']}</b> — soit "
           f"{tr['variation_pct']:+.0f} % — alors même que le taux d'accès passait de "
           f"{fr(er['valeur_depart'], 1)} % à {er['valeur']:.0f} %. La décomposition est "
           f"exacte et sans hypothèse : la croissance de la population rurale a ajouté "
           f"{fr(tr['effet_demographie']/1e6, 2)} million de personnes non raccordées, "
           f"l'électrification en a retiré {fr(abs(tr['effet_acces'])/1e6, 2)} million. "
           f"Le solde reste positif.")
    encart("action",
           f"<b>Conséquence pour le pilotage.</b> Un objectif exprimé en taux "
           f"(« 100 % en 2030 ») ne dit rien de l'effort réel et peut être atteint sur "
           f"le papier pendant que le nombre de personnes concernées augmente. "
           f"L'indicateur à suivre est le <b>volume annuel de raccordements</b>, avec "
           f"deux repères chiffrés : <b>{fr(tr['seuil_stagnation'])} par an</b> pour "
           f"stabiliser le stock — c'est exactement la croissance de la population "
           f"rurale en {tr['annee_fin']} — et <b>{fr(besoin_cible/1000)} 000 par an</b> "
           f"pour tenir la cible. Ce sont deux ordres de grandeur qui départagent "
           f"immédiatement une extension de réseau d'un programme décentralisé.")

# ------------------------------------------------------------- 3. LA FIABILITÉ
with onglet3:
    section("Ce que vaut un raccordement",
            "Objectif du défi : « mesurer la fiabilité du réseau (coupures) ». "
            "Les enquêtes entreprises de la Banque Mondiale fournissent quatre "
            "mesures, sur deux vagues comparables.")

    CARTES = [
        ("coupures_mois",   "Coupures par mois",        "{:.1f}",   "moins de coupures"),
        ("part_touchees",   "Entreprises touchées",     "{:.1f} %", "moins d'entreprises"),
        ("pertes_ca",       "Chiffre d'affaires perdu", "{:.1f} %", "moins de pertes"),
        ("delai_raccord",   "Délai de raccordement",    "{:.0f} j", "délai plus court"),
    ]
    tuiles, lignes_pente = [], []
    for cle, label, fmt, mieux in CARTES:
        df, lib, unite, code = D.fiab(nat, cle)
        df = df.drop_duplicates(subset="annee")
        if len(df) < 2:
            continue
        a0_, v0_ = int(df["annee"].iloc[0]), float(df["valeur"].iloc[0])
        a1_, v1_ = int(df["annee"].iloc[-1]), float(df["valeur"].iloc[-1])
        ameliore = v1_ < v0_
        coul = C["foret"] if ameliore else C["risque"]
        fleche = "▼" if ameliore else "▲"
        tuiles.append((label, fmt.format(v1_),
                       f"en {a1_} · était de {fmt.format(v0_)} en {a0_}",
                       coul, f"{fleche} {fr(abs(v1_-v0_), 1)}"))
        lignes_pente.append((label, a0_, v0_, a1_, v1_, coul, unite))
    if tuiles:
        kpi_row(tuiles)

    st.write("")
    g1, g2 = st.columns([1.15, 1])

    with g1:
        with st.container(border=True):
            # graphique de pente : deux vagues d'enquête, quatre indicateurs, une lecture
            titre_carte("Les quatre mesures de fiabilité, entre deux enquêtes",
                        "Base 100 = la pire des deux valeurs, pour comparer des "
                        "unités différentes.", C["risque"])
            fig3 = go.Figure()
            for label, a0_, v0_, a1_, v1_, coul, unite in lignes_pente:
                base = max(v0_, v1_)
                n0, n1 = 100 * v0_ / base, 100 * v1_ / base
                fig3.add_trace(go.Scatter(
                    x=[a0_, a1_], y=[n0, n1], mode="lines+markers+text",
                    line=dict(color=coul, width=2.6), marker=dict(size=9, color=coul),
                    text=[f"{fr(v0_, 1)}", f"{fr(v1_, 1)}"],
                    textposition=["middle left", "middle right"],
                    textfont=dict(size=11.5, color=coul), name=label,
                    customdata=[[v0_, unite], [v1_, unite]],
                    hovertemplate=f"{label}<br>%{{x}} : %{{customdata[0]:.1f}} "
                                  f"%{{customdata[1]}}<extra></extra>",
                    showlegend=True))
            style_fig(fig3, hauteur=344)
            fig3.update_xaxes(tickvals=[2009, 2016], range=[2006, 2019], title=None)
            fig3.update_yaxes(title="Niveau relatif", range=[0, 118],
                              showticklabels=False)
            st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})
            telecharger(pd.DataFrame(
                [{"indicateur": l, "annee_debut": a0_, "valeur_debut": v0_,
                  "annee_fin": a1_, "valeur_fin": v1_, "unite": u}
                 for l, a0_, v0_, a1_, v1_, _, u in lignes_pente]),
                "fiabilite_reseau")

    with g2:
        with st.container(border=True):
            dj, *_ = D.fiab(nat, "demarches_jours")
            dj = dj.drop_duplicates(subset="annee")
            titre_carte("Délai réglementaire de raccordement",
                        "Seule série annuelle disponible sur la qualité de service.",
                        C["energie"])
            fig4 = go.Figure(go.Scatter(
                x=dj["annee"], y=dj["valeur"], mode="lines+markers",
                line=dict(color=C["energie"], width=3, shape="hv"),
                marker=dict(size=7, color=C["energie"]), fill="tozeroy",
                fillcolor=rgba("energie", .10),
                hovertemplate="%{x} · %{y:.0f} jours<extra></extra>"))
            style_fig(fig4, hauteur=344)
            fig4.update_yaxes(title="jours", range=[0, 100])
            fig4.update_xaxes(title=None, dtick=2)
            if len(dj):
                annote(fig4, int(dj["annee"].iloc[-1]), float(dj["valeur"].iloc[-1]),
                       f"{dj['valeur'].iloc[-1]:.0f} j", C["energie"], ax=-34, ay=-26)
            st.plotly_chart(fig4, width="stretch", config={"displayModeBar": False})
            telecharger(dj.rename(columns={"valeur": "delai_jours"}),
                        "delai_raccordement")

    encart("alerte",
           f"<b>Les coupures se raréfient, mais elles se généralisent.</b> Entre "
           f"{fi['annee_ref']} et {fi['annee']}, la fréquence baisse "
           f"({fr(fi['coupures_mois_ref'], 1)} → {fr(fi['coupures_mois'], 1)} coupures "
           f"par mois), mais la part d'entreprises qui en subissent <b>augmente de "
           f"{fi['part_entreprises_ref']:.0f} % à {fi['part_entreprises']:.0f} %</b>. "
           f"Autrement dit : le réseau s'est étendu plus vite qu'il ne s'est consolidé. "
           f"Le raccordement au réseau national ne garantit donc pas un service continu.")
    encart("action",
           "Cette conclusion se combine aux précédentes. Pour un village éloigné, la "
           "question n'est pas « réseau ou solaire ? » mais « service fiable ou service "
           "intermittent ? ». Un mini-réseau solaire avec stockage offre une "
           "disponibilité prévisible, immédiate, et dimensionnable au besoin réel — là "
           "où l'extension du réseau apporterait, plus tard, un courant lui-même "
           "instable.")

with st.expander("Méthode, données et limites de cette page"):
    st.markdown(f"""
**Accès à l'électricité** — Banque Mondiale, `EG.ELC.ACCS.RU.ZS` (rural),
`EG.ELC.ACCS.UR.ZS` (urbain), `EG.ELC.ACCS.ZS` (ensemble), séries annuelles
{er['annee_depart']}–{er['annee']}.

**Décomposition du stock de ruraux sans électricité** — croisement de
`EG.ELC.ACCS.RU.ZS` et `SP.RUR.TOTL`. La variation du produit
population × (1 − taux d'accès) se décompose exactement en un effet
démographique, (P₁ − P₀) × (1 − a₀), et un effet d'électrification,
− P₁ × (a₁ − a₀). C'est une **identité comptable** : elle ne fait appel à aucune
hypothèse, et la somme des deux effets reconstitue la variation observée au
chiffre près. L'audit d'intégrité la recalcule indépendamment.

**Raccordements annuels** — variation d'une année à l'autre du produit
population rurale × taux d'accès. Ces séries proviennent d'enquêtes : les
à-coups d'une année sur l'autre sont largement de la variabilité de mesure,
d'où l'option de lissage sur trois ans.

**Seuil de stagnation** — le nombre de personnes privées d'électricité vaut
P − raccordés ; sa variation vaut donc ΔP − (nouveaux raccordés). Il est stable
exactement quand les raccordements annuels égalent la **croissance de la
population rurale** — ni plus, ni moins. Ce seuil n'est donc pas une constante :
il suit la démographie, et il décroît à mesure que la croissance rurale
ralentit ({fr(tr['seuil_moyen_10ans'])} par an en moyenne sur
{tr['annee_debut_decennie']}–{tr['annee_fin']},
{fr(tr['seuil_stagnation'])} en {tr['annee_fin']}). Sur cette décennie,
{fr(tr['raccordements_moyens_10ans'])} raccordements par an ont été réalisés
pour un seuil moyen de {fr(tr['seuil_moyen_10ans'])} : le déficit de
{fr(tr['seuil_moyen_10ans']-tr['raccordements_moyens_10ans'])} par an
reconstitue exactement la hausse observée du stock
({fr(tr['variation_decennie'])} personnes). L'audit d'intégrité vérifie cette
identité.

**Fiabilité** — Enterprise Surveys : `IC.ELC.OUTG` (coupures/mois),
`IC.ELC.OUTG.ZS` (% d'entreprises touchées), `IC.FRM.OUTG.ZS` (CA perdu),
`IC.ELC.DURS` (délai de raccordement), `IC.ELC.TIME` (temps réglementaire).

**Limites à connaître.**
1. Les indicateurs de coupures portent sur les **entreprises**, pas sur les
   ménages : aucune source du défi ne mesure la fiabilité vécue par les foyers
   ruraux. Ils constituent la meilleure approximation disponible de la qualité
   du réseau, et sont plutôt un **minorant** de ce que subissent les zones
   rurales.
2. Deux vagues d'enquête seulement ({fi['annee_ref']} et {fi['annee']}) : la
   comparaison est un contraste, pas une tendance.
3. **Aucune donnée infranationale d'électrification** n'existe dans les six jeux
   fournis. Le clivage analysable est donc rural / urbain, pas région par région.
4. Les projections en personnes retiennent la population rurale de
   {rs['annee_pop']} ({fr(rs['pop_rurale']/1e6, 2)} M), **maintenue constante**.
   C'est une hypothèse conservatrice : la page « Le rythme réel des
   raccordements » montre que la population rurale croît encore, donc l'effort
   réel sera supérieur à celui affiché ici.
""")

pied()

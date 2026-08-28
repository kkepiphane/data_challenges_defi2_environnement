"""Consommation d'énergie des ménages, dépendance à la biomasse, et ce qui
prend réellement la place de la forêt."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   pied, fr, titre_carte, rgba, telecharger, reglages, jetons)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

cb, rp, dfr, sa = (R["combustibles"], R["renouvelable_piege"],
                   R["deforestation"], R["sante"])
us, rg = R["usage_sols"], R["regimes_foret"]
PERTE = dfr["perte_actuelle_ha_an"]      # régime en cours, pas la moyenne longue

banniere("Consommation des ménages et couvert forestier",
         "Le bois de feu n'est pas une énergie du passé : sa part augmente",
         "Neuf ménages togolais sur dix cuisinent au bois ou au charbon. Cette page "
         "montre que la dépendance ne recule pas, qu'elle est masquée par une "
         "statistique flatteuse — le « taux d'énergie renouvelable » — et qu'elle se "
         "paie en fumées respirées. Elle mesure aussi, données à l'appui, ce qui prend "
         "réellement la place de la forêt : l'expansion agricole, cinq fois plus vaste "
         "que le recul forestier lui-même.")

kpi_row([
    ("Bois + charbon de bois", f"{cb['biomasse'][1]:.0f} %",
     f"des ménages en {cb['annees'][1]}, contre {cb['biomasse'][0]:.0f} % en "
     f"{cb['annees'][0]}", C["risque"], "aucun recul", cb["biomasse"]),
    ("Cuisson propre en milieu rural", f"{fr(R['cuisson_rurale']['valeur'], 1)} %",
     f"en {R['cuisson_rurale']['annee']} — progression de "
     f"+{fr(R['cuisson_rurale']['rythme_observe'], 2)} pt/an", C["risque"], None,
     list(D.serie(nat, "cuisson_rural")["valeur"])),
    ("Forêt perdue", f"{fr(PERTE)} ha/an",
     f"dans le régime en cours depuis {dfr['regime_depuis']} — "
     f"{rg['ralentissement']:.1f} fois moins que dans les années 1990, "
     f"mais sans reprise", C["risque"], f"depuis {dfr['regime_depuis']}",
     list(D.serie(nat, "foret_km2")["valeur"])),
    ("Expansion agricole", f"× {us['ratio_agri_foret']:.1f}",
     f"la surface agricole a gagné {fr(us['delta_agri_km2'])} km² quand la forêt "
     f"en perdait {fr(abs(us['delta_foret_km2']))}, entre {us['annee_debut']} et "
     f"{us['annee_fin']}", C["energie"], "moteur concurrent"),
    ("Pollution de l'air", f"× {sa['ratio_oms']:.0f}",
     f"la ligne directrice OMS · {sa['pm25']:.0f} µg/m³ de PM2,5 en "
     f"{sa['annee_pm25']}", C["risque"], None,
     list(D.serie(nat, "pm25")["valeur"])),
])

# =============================================================================
o1, o2, o3, o4 = st.tabs([" Ce que brûlent les ménages ",
                          " Le piège du « renouvelable » ",
                          " Qui prend la place de la forêt ? ",
                          " Simulateur de sortie de la biomasse "])

# ------------------------------------------------------- 1. LE MIX DE CUISSON
with o1:
    section("Le combustible principal de cuisson, entre deux enquêtes",
            f"Enquêtes ménages {cb['annees'][0]} et {cb['annees'][1]} — "
            "les seules mesures directes disponibles dans les données du défi. "
            "Deux points de mesure se lisent comme un contraste, jamais comme "
            "une tendance.")

    labels = ["Bois de chauffe", "Charbon de bois", "GPL / gaz", "Électricité"]
    v0 = [cb["bois"][0], cb["charbon"][0], cb["gpl"][0],
          D.serie(nat, "elec_cuisson")["valeur"].iloc[0]]
    v1 = [cb["bois"][1], cb["charbon"][1], cb["gpl"][1],
          D.serie(nat, "elec_cuisson")["valeur"].iloc[-1]]

    g1, g2 = st.columns([1.25, 1])
    with g1:
        with st.container(border=True):
            titre_carte("Le combustible de cuisson, entre les deux enquêtes",
                        "Le total biomasse ne bouge pas ; sa composition se dégrade.",
                        C["risque"])
            fig = go.Figure()
            fig.add_trace(go.Bar(y=labels, x=v0, name=str(cb["annees"][0]),
                                 orientation="h", marker_color=C["neutre"],
                                 text=[f"{fr(v, 1)} %" for v in v0],
                                 textposition="outside", textfont=dict(size=11.5),
                                 hovertemplate="%{y} · %{x:.1f} %<extra>"
                                               f"{cb['annees'][0]}</extra>"))
            fig.add_trace(go.Bar(y=labels, x=v1, name=str(cb["annees"][1]),
                                 orientation="h",
                                 marker_color=[C["risque"], C["charbon"],
                                               C["foret"], C["energie"]],
                                 text=[f"{fr(v, 1)} %" for v in v1],
                                 textposition="outside",
                                 textfont=dict(size=11.5, color=C["encre"]),
                                 hovertemplate="%{y} · %{x:.1f} %<extra>"
                                               f"{cb['annees'][1]}</extra>"))
            style_fig(fig, hauteur=360, marge_g=0)
            fig.update_xaxes(range=[0, 66], ticksuffix=" %", title=None)
            fig.update_yaxes(title=None, autorange="reversed")
            fig.update_layout(barmode="group", bargap=.28, bargroupgap=.06)
            annote(fig, cb["bois"][1], "Bois de chauffe",
                   f"+{fr(cb['bois'][1]-cb['bois'][0], 1)} pt", C["risque"],
                   ax=46, ay=-22)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            telecharger(pd.DataFrame({
                "combustible": labels,
                f"part_{cb['annees'][0]}_pct": v0,
                f"part_{cb['annees'][1]}_pct": v1}), "combustibles_cuisson")

    with g2:
        with st.container(border=True):
            # accès à une cuisson propre : rural vs urbain, dans le temps
            cr = D.serie(nat, "cuisson_rural", an_min, an_max)
            cu = D.serie(nat, "cuisson_urbain", an_min, an_max)
            titre_carte("Accès à une cuisson propre, ville contre campagne",
                        "La courbe rurale est le point noir du dossier énergétique "
                        "togolais.", C["risque"])
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=cu["annee"], y=cu["valeur"], name="Urbain",
                                      line=dict(color=C["urbain"], width=3),
                                      mode="lines",
                                      hovertemplate="%{x} · %{y:.1f} %"
                                                    "<extra>Urbain</extra>"))
            fig2.add_trace(go.Scatter(x=cr["annee"], y=cr["valeur"], name="Rural",
                                      line=dict(color=C["risque"], width=3),
                                      mode="lines", fill="tozeroy",
                                      fillcolor=rgba("risque", .10),
                                      hovertemplate="%{x} · %{y:.1f} %"
                                                    "<extra>Rural</extra>"))
            style_fig(fig2, hauteur=360)
            fig2.update_yaxes(ticksuffix=" %", range=[0, 32], title=None)
            fig2.update_xaxes(title=None)
            if len(cr):
                annote(fig2, int(cr["annee"].iloc[-1]), float(cr["valeur"].iloc[-1]),
                       f"{fr(cr['valeur'].iloc[-1], 1)} % en zone rurale", C["risque"],
                       ax=-70, ay=-30)
            st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})
            telecharger(pd.DataFrame({"annee": cr["annee"],
                                      "rural_pct": cr["valeur"]}).merge(
                pd.DataFrame({"annee": cu["annee"], "urbain_pct": cu["valeur"]}),
                on="annee", how="outer"), "cuisson_propre")

    encart("alerte",
           f"<b>La transition n'a pas commencé, elle a reculé.</b> Entre "
           f"{cb['annees'][0]} et {cb['annees'][1]}, le bois de chauffe gagne "
           f"{fr(cb['bois'][1]-cb['bois'][0], 1)} points ({fr(cb['bois'][0], 1)} % → "
           f"{fr(cb['bois'][1], 1)} %). Le charbon recule de "
           f"{fr(cb['charbon'][0]-cb['charbon'][1], 1)} points et le GPL progresse de "
           f"{fr(cb['gpl'][1]-cb['gpl'][0], 1)} points, mais le total biomasse reste à "
           f"<b>{cb['biomasse'][1]:.0f} %</b>. Le mouvement observé est un glissement "
           f"du charbon vers le bois brut — soit l'inverse de la transition recherchée, "
           f"puisque le bois brut est le combustible le plus émetteur de particules à "
           f"l'intérieur des habitations.")

# ------------------------------------------------- 2. LE PIÈGE DU RENOUVELABLE
with o2:
    section("Une statistique flatteuse qui masque le problème",
            "Le jeu de données « énergies renouvelables, combustibles et déchets » "
            "place le Togo parmi les pays les plus « renouvelables » du monde. "
            "Confronté à la cuisson propre, ce chiffre change de sens.")

    ren = D.serie(nat, "renouv", an_min, an_max)
    ct = D.serie(nat, "cuisson_total", an_min, an_max)

    with st.container(border=True):
        titre_carte("Deux mesures du même système énergétique",
                    "L'écart entre les deux courbes, c'est la biomasse brûlée dans "
                    "les foyers.", C["foret"])
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ren["annee"], y=ren["valeur"],
                                  name="Part « renouvelable » de l'énergie finale",
                                  line=dict(color=C["foret"], width=3.2), mode="lines",
                                  hovertemplate="%{x} · %{y:.1f} %"
                                                "<extra>Renouvelable</extra>"))
        fig3.add_trace(go.Scatter(x=ct["annee"], y=ct["valeur"],
                                  name="Ménages ayant accès à une cuisson propre",
                                  line=dict(color=C["risque"], width=3.2), mode="lines",
                                  fill="tonexty", fillcolor=rgba("risque", .09),
                                  hovertemplate="%{x} · %{y:.1f} %"
                                                "<extra>Cuisson propre</extra>"))
        style_fig(fig3, hauteur=384)
        fig3.update_yaxes(ticksuffix=" %", range=[0, 92], title=None)
        fig3.update_xaxes(title=None)
        milieu = int((ren["annee"].iloc[len(ren)//2])) if len(ren) else 2005
        annote(fig3, milieu, 45,
               "Cet écart, c'est la biomasse<br>brûlée dans les foyers", C["risque"],
               ax=0, ay=0, fleche=False)
        if len(ren):
            annote(fig3, int(ren["annee"].iloc[-1]), float(ren["valeur"].iloc[-1]),
                   f"{ren['valeur'].iloc[-1]:.0f} %", C["foret"], ax=-32, ay=-24)
        st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})
        telecharger(pd.DataFrame({"annee": ren["annee"],
                                  "renouvelable_pct": ren["valeur"]}).merge(
            pd.DataFrame({"annee": ct["annee"], "cuisson_propre_pct": ct["valeur"]}),
            on="annee", how="outer"), "renouvelable_vs_cuisson_propre")

    encart("constat",
           f"<b>« Renouvelable » ne veut pas dire « propre ».</b> En {rp['annee']}, "
           f"{fr(rp['part_renouvelable'], 1)} % de l'énergie finale consommée au Togo "
           f"est comptabilisée comme renouvelable — un taux que peu de pays affichent. "
           f"Au même moment, seuls {fr(rp['part_cuisson_propre'], 1)} % des ménages ont "
           f"accès à une cuisson propre. Les deux chiffres décrivent la même réalité "
           f"vue de deux côtés : ce « renouvelable » est très majoritairement du "
           f"<b>bois de feu et du charbon de bois</b>, une biomasse brûlée sans "
           f"évacuation des fumées.")
    encart("action",
           "Conséquence directe pour le pilotage : le taux d'énergie renouvelable est "
           "un mauvais indicateur de suivi pour la transition énergétique togolaise. "
           "Il baissera mécaniquement à mesure que les ménages passeront au GPL ou à "
           "l'électricité — c'est-à-dire précisément quand la situation s'améliorera. "
           "Les indicateurs à suivre sont l'<b>accès à la cuisson propre</b> et la "
           "<b>part des ménages sortis de la biomasse</b>.")

# --------------------------------------------- 3. QUI PREND LA PLACE DE LA FORÊT
with o3:
    section("Ce que les données permettent réellement d'attribuer",
            "Aucun fichier du défi ne mesure les prélèvements de bois-énergie : le "
            "lien cuisson → déforestation ne peut pas être établi directement. En "
            "revanche, le moteur concurrent est mesuré, lui — et il est bien plus "
            "vaste que le recul forestier lui-même.")

    ag = D.serie(nat, "agri_km2")
    fo_k = D.serie(nat, "foret_km2")
    ch = D.serie(nat, "cereales_ha")
    ctn = D.serie(nat, "cereales_t")

    jetons(("Fenêtre de comparaison", f"{us['annee_debut']}–{us['annee_fin']}"),
           ("Raison de l'arrêt",
            f"surface agricole gelée depuis {us['agri_derniere_maj']}"),
           ("Source", "Banque Mondiale, 4 séries"))

    kpi_row([
        ("Expansion agricole", f"{fr(us['delta_agri_km2'])} km²",
         f"gagnés par la surface agricole entre {us['annee_debut']} et "
         f"{us['annee_fin']}", C["energie"]),
        ("Recul forestier", f"{fr(abs(us['delta_foret_km2']))} km²",
         "perdus par la forêt sur exactement la même fenêtre", C["risque"]),
        ("Rapport des deux", f"× {us['ratio_agri_foret']:.1f}",
         f"l'agricole gagne {us['ratio_agri_foret']:.1f} fois ce que la forêt perd : "
         f"la forêt ne peut fournir que {us['part_foret_dans_expansion']:.0f} % de "
         f"cette expansion", C["encre_2"]),
        ("Rendement céréalier", f"{fr(us['rendement_fin'], 2)} t/ha",
         f"en {us['cereales_annee_fin']}, contre "
         f"{fr(us['rendement_debut'], 2)} t/ha en {us['cereales_annee_debut']}",
         C["energie"]),
        ("Défrichement céréalier", f"{fr(us['expansion_cerealiere_ha_an'])} ha/an",
         f"de terres nouvelles mises en culture, soit "
         f"{us['ratio_defrichement_deforestation']:.1f} fois la perte forestière "
         f"annuelle actuelle", C["risque"]),
    ])

    st.write("")
    g1, g2 = st.columns([1, 1])

    with g1:
        with st.container(border=True):
            titre_carte("Surface agricole et couvert forestier, en km²",
                        "Deux panneaux, un seul axe du temps. Les échelles diffèrent "
                        "d'un facteur trois : les superposer aurait faussé la lecture.",
                        C["energie"])
            fig4 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                 vertical_spacing=.09, row_heights=[.5, .5])
            agv = ag[(ag["annee"] >= us["annee_debut"])
                     & (ag["annee"] <= us["annee_fin"])]
            fov = fo_k[(fo_k["annee"] >= us["annee_debut"])
                       & (fo_k["annee"] <= us["annee_fin"])]
            fig4.add_trace(go.Scatter(
                x=agv["annee"], y=agv["valeur"], name="Surface agricole",
                line=dict(color=C["energie"], width=3.2), mode="lines",
                hovertemplate="%{x} · %{y:,.0f} km²<extra>Surface agricole</extra>"),
                row=1, col=1)
            fig4.add_trace(go.Scatter(
                x=fov["annee"], y=fov["valeur"], name="Couvert forestier",
                line=dict(color=C["foret"], width=3.2), mode="lines",
                hovertemplate="%{x} · %{y:,.0f} km²<extra>Couvert forestier</extra>"),
                row=2, col=1)
            style_fig(fig4, hauteur=386)
            fig4.update_yaxes(title=None, range=[30000, 39500], row=1, col=1)
            fig4.update_yaxes(title=None, range=[11800, 14000], row=2, col=1)
            fig4.update_xaxes(title=None)
            annote(fig4, us["annee_fin"], us["agri_fin_km2"],
                   f"+{fr(us['delta_agri_km2'])} km²", C["energie"],
                   ax=-58, ay=26, row=1, col=1)
            annote(fig4, us["annee_fin"], us["foret_fin_km2"],
                   f"−{fr(abs(us['delta_foret_km2']))} km²", C["risque"],
                   ax=-58, ay=26, row=2, col=1)
            st.plotly_chart(fig4, width="stretch", config={"displayModeBar": False})
            telecharger(agv.rename(columns={"valeur": "agricole_km2"}).merge(
                fov.rename(columns={"valeur": "foret_km2"}), on="annee", how="outer"),
                "usage_des_sols")

    with g2:
        with st.container(border=True):
            titre_carte("D'où vient la hausse de la production céréalière",
                        f"Entre {us['cereales_annee_debut']} et "
                        f"{us['cereales_annee_fin']}. La production a triplé — mais "
                        "surtout parce que les surfaces ont doublé.", C["risque"])
            parts = [us["part_surface_dans_production"],
                     us["part_rendement_dans_production"], us["part_croisee"]]
            noms = ["Extension<br>des surfaces", "Hausse des<br>rendements",
                    "Effet croisé<br>des deux"]
            fig5 = go.Figure(go.Bar(
                x=noms, y=parts,
                marker_color=[C["risque"], C["foret"], C["neutre"]],
                text=[f"{p:.0f} %" for p in parts], textposition="outside",
                textfont=dict(size=13, color=C["encre"]),
                hovertemplate="%{x} · %{y:.1f} % de la hausse<extra></extra>"))
            style_fig(fig5, hauteur=386, marge_g=0)
            fig5.update_yaxes(title="part de la hausse de production",
                              ticksuffix=" %", range=[0, 60])
            fig5.update_xaxes(title=None, tickfont=dict(size=11))
            st.plotly_chart(fig5, width="stretch", config={"displayModeBar": False})
            telecharger(pd.DataFrame({
                "annee": ch["annee"],
                "surface_cerealiere_ha": ch["valeur"],
                "production_t": ctn.set_index("annee")["valeur"].reindex(
                    ch["annee"]).values}), "cereales_surface_et_production")

    encart("methode",
           f"<b>Ce que la comparaison établit, et ce qu'elle n'établit pas.</b> Entre "
           f"{us['annee_debut']} et {us['annee_fin']}, la surface agricole togolaise a "
           f"gagné {fr(us['delta_agri_km2'])} km² pendant que la forêt en perdait "
           f"{fr(abs(us['delta_foret_km2']))}. Deux conséquences, dans les deux sens : "
           f"la forêt ne peut avoir fourni que <b>{us['part_foret_dans_expansion']:.0f} %</b> "
           f"de l'expansion agricole — le reste vient des savanes et des jachères ; mais "
           f"l'expansion agricole est, à elle seule, <b>largement suffisante</b> pour "
           f"absorber la totalité du recul forestier. Ces données ne permettent donc "
           f"pas d'attribuer la déforestation au bois-énergie, et elles rendent peu "
           f"vraisemblable qu'il en soit le facteur majoritaire. C'est la raison pour "
           f"laquelle l'attribution reste, dans le simulateur, un curseur explicite — "
           f"et non un chiffre posé d'autorité.",
           titre="Portée exacte de ce croisement")

    encart("action",
           f"<b>Un quatrième levier sort de ces données : l'intensification agricole.</b> "
           f"Le rendement céréalier togolais est de {fr(us['rendement_fin'], 2)} t/ha, "
           f"et {us['part_surface_dans_production']:.0f} % de la hausse de production "
           f"depuis {us['cereales_annee_debut']} vient de l'extension des surfaces, "
           f"non du progrès des rendements. Le pays met en culture "
           f"{fr(us['expansion_cerealiere_ha_an'])} hectares de terres nouvelles par an "
           f"— soit {us['ratio_defrichement_deforestation']:.1f} fois ce qu'il perd de "
           f"forêt. Tant que produire plus signifie défricher plus, la protection "
           f"forestière restera un combat d'arrière-garde : faire monter les rendements "
           f"est une politique forestière autant qu'une politique agricole.")

# ---------------------------------------------- 4. SIMULATEUR
with o4:
    section("Que gagne-t-on à sortir les ménages de la biomasse ?",
            "Deux curseurs, deux hypothèses assumées et affichées. Le résultat "
            "n'est pas une prévision : c'est un ordre de grandeur pour arbitrer.")

    with reglages("Hypothèses du simulateur",
                  "La perte forestière de référence est celle du régime en cours "
                  f"({fr(PERTE)} ha/an depuis {dfr['regime_depuis']}), et non la "
                  "moyenne 1990-2021 qui mélange deux rythmes."):
        s1, s2, s3 = st.columns([1, 1, 1])
        with s1:
            bascule = st.slider("Ménages sortis de la biomasse d'ici 2030 (%)",
                                0, 60, 25, 5, key="cuisson_bascule",
                                help="Part de la population qui passerait du "
                                     "bois/charbon au GPL, à l'électricité ou à un "
                                     "foyer amélioré performant.")
        with s2:
            attribution = st.slider(
                "Part du recul forestier imputable au bois-énergie (%)",
                0, 100, 30, 5, key="cuisson_attribution",
                help="Hypothèse explicite. L'onglet « Qui prend la place de la "
                     "forêt ? » montre que l'expansion agricole suffit à elle seule "
                     "à absorber tout le recul forestier : une attribution "
                     "majoritaire au bois-énergie serait peu vraisemblable.")
        with s3:
            unite = st.radio("Unité du couvert forestier",
                             ["% du territoire", "km²"], horizontal=False,
                             key="cuisson_unite")

    cle = "foret_pct" if unite.startswith("%") else "foret_km2"
    fo = D.serie(nat, cle, an_min, an_max)
    suffixe = " %" if cle == "foret_pct" else " km²"

    pop = D.serie(nat, "pop_totale")["valeur"].iloc[-1]
    an_pop = int(D.serie(nat, "pop_totale")["annee"].iloc[-1])
    personnes = pop * bascule / 100
    perte_bois = PERTE * attribution / 100
    evite = perte_bois * bascule / 100
    perte_apres = PERTE - evite
    cumul_2030 = evite * 5     # 2026 -> 2030

    jetons(("Sortie de la biomasse", f"{bascule} %"),
           ("Attribution bois-énergie", f"{attribution} %"),
           ("Perte de référence", f"{fr(PERTE)} ha/an"),
           ("Nature du résultat", "projection, pas donnée"))

    kpi_row([
        ("Personnes concernées", f"{fr(personnes/1e6, 2)} M",
         f"{bascule} % de la population ({fr(pop/1e6, 1)} M en {an_pop})",
         C["energie"]),
        ("Perte forestière évitée", f"{fr(evite)} ha/an",
         f"sur les {fr(perte_bois)} ha/an imputés au bois-énergie", C["foret"]),
        ("Perte annuelle résiduelle", f"{fr(perte_apres)} ha/an",
         f"contre {fr(PERTE)} ha/an aujourd'hui",
         C["risque"] if perte_apres > PERTE * .7 else C["energie"]),
        ("Cumul 2026-2030", f"{fr(cumul_2030)} ha",
         "de forêt préservée sur cinq ans", C["foret"]),
    ])

    st.write("")
    g1, g2 = st.columns([1, 1.1])

    with g1:
        with st.container(border=True):
            titre_carte("Perte forestière annuelle, avant et après",
                        "Le trait noir marque le régime observé aujourd'hui.",
                        C["foret"])
            fig6 = go.Figure()
            fig6.add_trace(go.Bar(
                y=["Aujourd'hui", "Avec la politique simulée"],
                x=[PERTE, perte_apres], orientation="h",
                marker_color=[C["risque"], C["foret"]],
                text=[f"{fr(PERTE)} ha/an", f"{fr(perte_apres)} ha/an"],
                textposition="outside", textfont=dict(size=12.5),
                hovertemplate="%{y} · %{x:,.0f} ha/an<extra></extra>"))
            style_fig(fig6, hauteur=250, marge_g=0)
            fig6.update_xaxes(range=[0, PERTE * 1.36], title="hectares par an")
            fig6.update_yaxes(title=None)
            st.plotly_chart(fig6, width="stretch", config={"displayModeBar": False})
            telecharger(pd.DataFrame([
                {"scenario": "régime observé", "perte_ha_an": PERTE},
                {"scenario": f"sortie biomasse {bascule} %, "
                             f"attribution {attribution} %",
                 "perte_ha_an": perte_apres}]), "simulateur_perte_forestiere")

    with g2:
        with st.container(border=True):
            titre_carte(f"Couvert forestier observé ({unite})",
                        "La série est interpolée par la FAO entre trois points de "
                        "référence : les ruptures de pente sont les seules mesures.",
                        C["foret"])
            fig7 = go.Figure(go.Scatter(
                x=fo["annee"], y=fo["valeur"], mode="lines",
                line=dict(color=C["foret"], width=3.4), fill="tozeroy",
                fillcolor=rgba("foret", .10),
                hovertemplate="%{x} · %{y:,.0f}" + suffixe + "<extra></extra>"))
            style_fig(fig7, hauteur=250)
            fig7.update_xaxes(title=None)
            if cle == "foret_pct":
                fig7.update_yaxes(range=[21, 26], ticksuffix=" %", title=None)
            else:
                fig7.update_yaxes(range=[11500, 14000], title="km²")
            if len(fo) > 1:
                annote(fig7, int(fo["annee"].iloc[-1]), float(fo["valeur"].iloc[-1]),
                       f"−{dfr['perte_pct_relative']:.0f} % depuis "
                       f"{dfr['annee_debut']}", C["risque"], ax=-58, ay=28)
            st.plotly_chart(fig7, width="stretch", config={"displayModeBar": False})
            telecharger(fo.rename(columns={"valeur": cle}), f"couvert_{cle}")

    st.write("")
    encart("action",
           f"Avec {bascule} % de la population sortie de la biomasse et une attribution "
           f"de {attribution} % du recul forestier au bois-énergie, le Togo préserverait "
           f"<b>{fr(cumul_2030)} hectares</b> de forêt sur cinq ans — l'équivalent de "
           f"{fr(cumul_2030/R['forets']['surface_totale_ha']*100, 1)} % de la surface "
           f"totale des forêts classées analysées dans la page « Forêts ». Et "
           f"{fr(personnes/1e6, 2)} millions de personnes cesseraient de respirer des "
           f"fumées de combustion domestique, dans un pays où l'exposition moyenne aux "
           f"PM2,5 vaut {sa['ratio_oms']:.0f} fois la ligne directrice de l'OMS. "
           f"<b>Le gain sanitaire, lui, ne dépend d'aucune hypothèse d'attribution :</b> "
           f"il est proportionnel au seul curseur de sortie de la biomasse.")

with st.expander("Méthode, données et limites de cette page"):
    st.markdown(f"""
**Combustibles de cuisson** — `SG.COK.WOOD.ZS`, `SG.COK.CHCO.ZS`, `SG.COK.LPGN.ZS`,
`SG.COK.ELEC.ZS` (enquêtes ménages {cb['annees'][0]} et {cb['annees'][1]}).
Deux points de mesure : on lit un **contraste**, pas une tendance.

**Accès à une cuisson propre** — `EG.CFT.ACCS.ZS` / `.RU.ZS` / `.UR.ZS`
(série annuelle, {R['cuisson_rurale']['annee']} en dernier point).

**Part renouvelable** — `EG.FEC.RNEW.ZS`, croisée avec le fichier
« énergies renouvelables, combustibles et déchets » du défi.

**Couvert forestier** — `AG.LND.FRST.ZS` et `AG.LND.FRST.K2`,
{dfr['annee_debut']}–{dfr['annee_fin']}. L'audit automatique des séries
(page « Données ») établit que cette série ne contient que
**{rg['n_mesures_independantes']} mesures indépendantes** : elle est interpolée
linéairement entre points de référence FAO. Le chiffre retenu partout dans cette
page est donc celui du **régime en cours** ({fr(PERTE)} ha/an depuis
{dfr['regime_depuis']}), et non la moyenne 1990-2021
({fr(dfr['perte_ha_par_an'])} ha/an), qui mélange deux rythmes et ne correspond
à aucune année réelle.

**Usage des sols** — `AG.LND.AGRI.K2` (surface agricole), `AG.LND.ARBL.ZS`,
`AG.LND.CREL.HA` et `AG.PRD.CREL.MT` (surfaces et production céréalières).
La comparaison forêt / agriculture s'arrête à **{us['annee_fin']}** parce que la
surface agricole est gelée à la même valeur depuis {us['agri_derniere_maj']}
({us['agri_ans_geles']} années de valeur répétée) — la prolonger aurait produit
une fausse stabilisation.

**Décomposition de la production céréalière** — production = surface × rendement,
donc ΔP = ΔS·R₀ + S₀·ΔR + ΔS·ΔR. Les trois termes sont affichés séparément, le
troisième étant l'effet croisé, qui n'est imputable ni à l'un ni à l'autre.

**Air et santé** — `EN.ATM.PM25.MC.M3` (exposition moyenne aux PM2,5) et
`SH.STA.AIRP.P5` (mortalité attribuée à la pollution de l'air,
{sa['annee_mortalite']} — **un seul point de mesure**).

**Limites assumées.**
1. Le lien cuisson → déforestation est **non mesuré** dans les données du défi :
   aucune source ne quantifie les prélèvements de bois-énergie. Le simulateur
   rend donc l'attribution **paramétrable**, et l'onglet « Qui prend la place de
   la forêt ? » montre pourquoi une attribution majoritaire serait peu
   vraisemblable.
2. L'indicateur PM2,5 mesure l'exposition **ambiante**, pas la pollution
   intérieure des habitations, qui est la voie d'exposition dominante pour la
   cuisson au bois : le chiffre affiché sous-estime l'exposition réelle des
   ménages concernés.
3. La mortalité `SH.STA.AIRP.P5` agrège pollution intérieure et extérieure ;
   elle n'est pas imputable à la seule cuisson, et ne compte qu'un seul point.
4. La population est supposée constante sur l'horizon du simulateur.
""")

pied()

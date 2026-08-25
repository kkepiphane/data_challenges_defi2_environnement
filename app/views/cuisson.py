"""Objectif 2 — consommation d'énergie des ménages, dépendance à la biomasse
et impact sur le recul des forêts."""
import numpy as np
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, hero, section, kpi_row, kpi, encart, style_fig, annote,
                   pied, fr)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

cb, rp, dfr, sa = (R["combustibles"], R["renouvelable_piege"],
                   R["deforestation"], R["sante"])

hero("Objectif 2 · Consommation des ménages",
     "Le bois de feu n'est pas une énergie du passé : sa part augmente",
     "Neuf ménages togolais sur dix cuisinent au bois ou au charbon. Cette page montre "
     "que la dépendance ne recule pas, qu'elle est masquée par une statistique "
     "flatteuse — le « taux d'énergie renouvelable » — et qu'elle se paie en hectares "
     "de forêt et en vies humaines.")

kpi_row([
    ("Bois + charbon de bois", f"{cb['biomasse'][1]:.0f} %",
     f"des ménages en {cb['annees'][1]}, contre {cb['biomasse'][0]:.0f} % en "
     f"{cb['annees'][0]}", C["risque"], "aucun recul"),
    ("Cuisson propre en milieu rural", f"{R['cuisson_rurale']['valeur']:.1f} %",
     f"en {R['cuisson_rurale']['annee']} — progression de "
     f"+{R['cuisson_rurale']['rythme_observe']:.2f} pt/an", C["risque"]),
    ("Forêt perdue", f"{fr(dfr['perte_ha_par_an'])} ha/an",
     f"soit {fr(dfr['perte_km2'])} km² disparus entre {dfr['annee_debut']} "
     f"et {dfr['annee_fin']}", C["foret"]),
    ("Pollution de l'air", f"× {sa['ratio_oms']:.0f}",
     f"la ligne directrice OMS · {sa['pm25']:.0f} µg/m³ de PM2,5 en "
     f"{sa['annee_pm25']}", C["risque"]),
    ("Mortalité attribuée", f"{sa['mortalite']:.0f}",
     f"décès pour 100 000 habitants liés à la pollution de l'air "
     f"({sa['annee_mortalite']})", C["risque"]),
])

# =============================================================================
o1, o2, o3 = st.tabs(["  🍲  Ce que brûlent les ménages  ",
                      "  🌿  Le piège du « renouvelable »  ",
                      "  🌳  Impact sur la forêt & simulateur  "])

# ------------------------------------------------------- 1. LE MIX DE CUISSON
with o1:
    section("Le combustible principal de cuisson, entre deux enquêtes",
            f"Enquêtes ménages {cb['annees'][0]} et {cb['annees'][1]} — "
            "les seules mesures directes disponibles dans les données du défi.")

    labels = ["Bois de chauffe", "Charbon de bois", "GPL / gaz", "Électricité"]
    v0 = [cb["bois"][0], cb["charbon"][0], cb["gpl"][0],
          D.serie(nat, "elec_cuisson")["valeur"].iloc[0]]
    v1 = [cb["bois"][1], cb["charbon"][1], cb["gpl"][1],
          D.serie(nat, "elec_cuisson")["valeur"].iloc[-1]]

    g1, g2 = st.columns([1.25, 1])
    with g1:
        fig = go.Figure()
        fig.add_trace(go.Bar(y=labels, x=v0, name=str(cb["annees"][0]), orientation="h",
                             marker_color=C["neutre"],
                             text=[f"{v:.1f} %" for v in v0], textposition="outside",
                             textfont=dict(size=11.5),
                             hovertemplate="%{y} · %{x:.1f} %<extra>"
                                           f"{cb['annees'][0]}</extra>"))
        fig.add_trace(go.Bar(y=labels, x=v1, name=str(cb["annees"][1]), orientation="h",
                             marker_color=[C["risque"], "#8C4A2F", C["foret"], C["energie"]],
                             text=[f"{v:.1f} %" for v in v1], textposition="outside",
                             textfont=dict(size=11.5, color=C["ink"]),
                             hovertemplate="%{y} · %{x:.1f} %<extra>"
                                           f"{cb['annees'][1]}</extra>"))
        style_fig(fig, "Combustible principal de cuisson (% des ménages)", hauteur=380,
                  marge_g=0)
        fig.update_xaxes(range=[0, 66], ticksuffix=" %", title=None)
        fig.update_yaxes(title=None, autorange="reversed")
        fig.update_layout(barmode="group", bargap=.28, bargroupgap=.06)
        annote(fig, cb["bois"][1], "Bois de chauffe",
               f"+{cb['bois'][1]-cb['bois'][0]:.1f} pt", C["risque"], ax=46, ay=-22)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with g2:
        # accès à une cuisson propre : rural vs urbain, dans le temps
        cr = D.serie(nat, "cuisson_rural", an_min, an_max)
        cu = D.serie(nat, "cuisson_urbain", an_min, an_max)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=cu["annee"], y=cu["valeur"], name="Urbain",
                                  line=dict(color=C["urbain"], width=3), mode="lines",
                                  hovertemplate="%{x} · %{y:.1f} %<extra>Urbain</extra>"))
        fig2.add_trace(go.Scatter(x=cr["annee"], y=cr["valeur"], name="Rural",
                                  line=dict(color=C["risque"], width=3), mode="lines",
                                  fill="tozeroy", fillcolor="rgba(192,57,43,.10)",
                                  hovertemplate="%{x} · %{y:.1f} %<extra>Rural</extra>"))
        style_fig(fig2, "Accès à une cuisson propre (% de la population)", hauteur=380)
        fig2.update_yaxes(ticksuffix=" %", range=[0, 32], title=None)
        fig2.update_xaxes(title=None)
        if len(cr):
            annote(fig2, int(cr["annee"].iloc[-1]), float(cr["valeur"].iloc[-1]),
                   f"{cr['valeur'].iloc[-1]:.1f} % en zone rurale", C["risque"],
                   ax=-70, ay=-30)
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

    encart("alerte",
           f"<b>La transition n'a pas commencé, elle a reculé.</b> Entre "
           f"{cb['annees'][0]} et {cb['annees'][1]}, le bois de chauffe gagne "
           f"{cb['bois'][1]-cb['bois'][0]:.1f} points ({cb['bois'][0]:.1f} % → "
           f"{cb['bois'][1]:.1f} %). Le charbon recule de "
           f"{cb['charbon'][0]-cb['charbon'][1]:.1f} points et le GPL progresse de "
           f"{cb['gpl'][1]-cb['gpl'][0]:.1f} points, mais le total biomasse reste à "
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

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=ren["annee"], y=ren["valeur"],
                              name="Part « renouvelable » de l'énergie finale",
                              line=dict(color=C["foret"], width=3.2), mode="lines",
                              hovertemplate="%{x} · %{y:.1f} %<extra>Renouvelable</extra>"))
    fig3.add_trace(go.Scatter(x=ct["annee"], y=ct["valeur"],
                              name="Ménages ayant accès à une cuisson propre",
                              line=dict(color=C["risque"], width=3.2), mode="lines",
                              fill="tonexty", fillcolor="rgba(192,57,43,.09)",
                              hovertemplate="%{x} · %{y:.1f} %<extra>Cuisson propre</extra>"))
    style_fig(fig3, "Deux mesures du même système énergétique (%)", hauteur=400)
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

    encart("constat",
           f"<b>« Renouvelable » ne veut pas dire « propre ».</b> En {rp['annee']}, "
           f"{rp['part_renouvelable']:.1f} % de l'énergie finale consommée au Togo est "
           f"comptabilisée comme renouvelable — un taux que peu de pays affichent. "
           f"Au même moment, seuls {rp['part_cuisson_propre']:.1f} % des ménages ont accès "
           f"à une cuisson propre. Les deux chiffres décrivent la même réalité vue de deux "
           f"côtés : ce « renouvelable » est très majoritairement du <b>bois de feu et du "
           f"charbon de bois</b>, une biomasse prélevée plus vite qu'elle ne se régénère, "
           f"brûlée sans évacuation des fumées.")
    encart("action",
           "Conséquence directe pour le pilotage : le taux d'énergie renouvelable est un "
           "mauvais indicateur de suivi pour la transition énergétique togolaise. Il "
           "baissera mécaniquement à mesure que les ménages passeront au GPL ou à "
           "l'électricité — c'est-à-dire précisément quand la situation s'améliorera. "
           "Les indicateurs à suivre sont l'<b>accès à la cuisson propre</b> et la "
           "<b>part des ménages sortis de la biomasse</b>.")

# ------------------------------------------------ 3. FORÊT + SIMULATEUR
with o3:
    section("Ce que la cuisson coûte à la forêt",
            "Et ce qu'une politique de cuisson propre permettrait d'éviter.")

    ctrl1, ctrl2 = st.columns([1, 2.4])
    with ctrl1:
        unite = st.radio("Unité du couvert forestier", ["% du territoire", "km²"],
                         horizontal=False)
    with ctrl2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.caption("Le couvert forestier togolais est mesuré par la Banque Mondiale "
                   f"(`AG.LND.FRST.ZS` / `AG.LND.FRST.K2`) sur {dfr['annee_debut']}–"
                   f"{dfr['annee_fin']}. La perte est continue sur toute la période, "
                   "sans aucune année de reprise.")

    cle = "foret_pct" if unite.startswith("%") else "foret_km2"
    fo = D.serie(nat, cle, an_min, an_max)
    suffixe = " %" if cle == "foret_pct" else " km²"

    fig4 = go.Figure(go.Scatter(
        x=fo["annee"], y=fo["valeur"], mode="lines",
        line=dict(color=C["foret"], width=3.4), fill="tozeroy",
        fillcolor="rgba(27,122,67,.10)",
        hovertemplate="%{x} · %{y:,.0f}" + suffixe + "<extra></extra>"))
    style_fig(fig4, f"Couvert forestier ({unite})", hauteur=360)
    fig4.update_xaxes(title=None)
    if cle == "foret_pct":
        fig4.update_yaxes(range=[21, 26], ticksuffix=" %", title=None)
    else:
        fig4.update_yaxes(range=[11500, 14000], title="km²")
    if len(fo) > 1:
        annote(fig4, int(fo["annee"].iloc[0]), float(fo["valeur"].iloc[0]),
               f"{fo['valeur'].iloc[0]:,.0f}".replace(",", " ") + suffixe,
               C["foret"], ax=44, ay=-24)
        annote(fig4, int(fo["annee"].iloc[-1]), float(fo["valeur"].iloc[-1]),
               f"−{dfr['perte_pct_relative']:.0f} % en "
               f"{dfr['annee_fin']-dfr['annee_debut']} ans", C["risque"], ax=-56, ay=32)
    st.plotly_chart(fig4, width="stretch", config={"displayModeBar": False})

    # ------------------------------------------------------------- simulateur
    section("Simulateur — que gagne-t-on à sortir les ménages de la biomasse ?",
            "Deux curseurs, deux hypothèses assumées et affichées. "
            "Le résultat n'est pas une prévision : c'est un ordre de grandeur pour arbitrer.")

    s1, s2, s3 = st.columns([1, 1, 1.3])
    with s1:
        bascule = st.slider("Ménages sortis de la biomasse d'ici 2030 (%)",
                            0, 60, 25, 5,
                            help="Part de la population qui passerait du bois/charbon "
                                 "au GPL, à l'électricité ou à un foyer amélioré performant.")
    with s2:
        attribution = st.slider("Part du recul forestier imputable au bois-énergie (%)",
                                0, 100, 50, 5,
                                help="Hypothèse explicite : le reste du recul est imputé "
                                     "à l'agriculture et à l'urbanisation. Aucune source "
                                     "du défi ne tranche cette répartition — d'où le curseur.")
    with s3:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.caption("Hypothèse de proportionnalité : la pression bois-énergie sur la forêt "
                   "décroît proportionnellement à la part de ménages qui en sortent.")

    pop = D.serie(nat, "pop_totale")["valeur"].iloc[-1]
    an_pop = int(D.serie(nat, "pop_totale")["annee"].iloc[-1])
    personnes = pop * bascule / 100
    perte_bois = dfr["perte_ha_par_an"] * attribution / 100
    evite = perte_bois * bascule / 100
    perte_apres = dfr["perte_ha_par_an"] - evite
    cumul_2030 = evite * 5     # 2026 -> 2030

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(kpi("Personnes concernées", f"{fr(personnes/1e6, 2)} M",
                        f"{bascule} % de la population ({fr(pop/1e6, 1)} M en {an_pop})",
                        C["energie"]), unsafe_allow_html=True)
    with r2:
        st.markdown(kpi("Perte forestière évitée", f"{fr(evite)} ha/an",
                        f"sur les {fr(perte_bois)} ha/an imputés au bois-énergie",
                        C["foret"]), unsafe_allow_html=True)
    with r3:
        st.markdown(kpi("Perte annuelle résiduelle", f"{fr(perte_apres)} ha/an",
                        f"contre {fr(dfr['perte_ha_par_an'])} ha/an aujourd'hui",
                        C["risque"] if perte_apres > 3000 else C["energie"]),
                    unsafe_allow_html=True)
    with r4:
        st.markdown(kpi("Cumul 2026-2030", f"{fr(cumul_2030)} ha",
                        "de forêt préservée sur cinq ans", C["foret"]),
                    unsafe_allow_html=True)

    # visualisation de l'effet
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        y=["Aujourd'hui", "Avec la politique simulée"],
        x=[dfr["perte_ha_par_an"], perte_apres], orientation="h",
        marker_color=[C["risque"], C["foret"]],
        text=[f"{fr(dfr['perte_ha_par_an'])} ha/an", f"{fr(perte_apres)} ha/an"],
        textposition="outside", textfont=dict(size=12.5),
        hovertemplate="%{y} · %{x:,.0f} ha/an<extra></extra>"))
    style_fig(fig5, "Perte forestière annuelle, avant / après", hauteur=210, marge_g=0)
    fig5.update_xaxes(range=[0, dfr["perte_ha_par_an"] * 1.32], title="hectares par an")
    fig5.update_yaxes(title=None)
    st.plotly_chart(fig5, width="stretch", config={"displayModeBar": False})

    encart("action",
           f"Avec {bascule} % de la population sortie de la biomasse et une attribution de "
           f"{attribution} % du recul forestier au bois-énergie, le Togo préserverait "
           f"<b>{fr(cumul_2030)} hectares</b> de forêt sur cinq ans — l'équivalent de "
           f"{cumul_2030/R['forets']['surface_totale_ha']*100:.1f} % de la surface totale "
           f"des forêts classées analysées dans la page « Où agir ». "
           f"Et {fr(personnes/1e6, 2)} millions de personnes cesseraient de respirer des "
           f"fumées de combustion domestique, dans un pays où la pollution de l'air est "
           f"associée à {sa['mortalite']:.0f} décès pour 100 000 habitants.")

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
{dfr['annee_debut']}–{dfr['annee_fin']}.

**Air et santé** — `EN.ATM.PM25.MC.M3` (exposition moyenne aux PM2,5) et
`SH.STA.AIRP.P5` (mortalité attribuée à la pollution de l'air, {sa['annee_mortalite']}).

**Limites assumées.**
1. Le lien cuisson → déforestation est **corrélatif** dans les données du défi :
   aucune source ne mesure directement les prélèvements de bois-énergie. Le simulateur
   rend donc l'attribution **paramétrable** plutôt que de la fixer arbitrairement.
2. L'indicateur PM2,5 mesure l'exposition **ambiante**, pas la pollution intérieure
   des habitations, qui est la voie d'exposition dominante pour la cuisson au bois :
   le chiffre affiché sous-estime l'exposition réelle des ménages concernés.
3. La mortalité `SH.STA.AIRP.P5` agrège pollution intérieure et extérieure ;
   elle n'est pas imputable à la seule cuisson.
4. La population est supposée constante sur l'horizon du simulateur.
""")

pied()

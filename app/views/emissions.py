"""Objectifs 3 & 4 — bilan des émissions par secteur et par gaz,
et variations du climat du Sud au Nord."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, MOIS, RAMPE, hero, section, kpi_row, kpi, encart,
                   style_fig, annote, pied, fr)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

hero("Objectifs 3 & 4 · Émissions et climat",
     "Le secteur énergie n'est marginal que si l'on ne regarde que le CO₂",
     "Le bilan 2018 place l'agriculture et l'usage des terres très loin devant. "
     "Mais un inventaire ne se lit pas seulement en totaux : gaz par gaz, et surtout "
     "en équivalent CO₂, la hiérarchie des secteurs change complètement. "
     "La seconde partie relie le climat observé aux besoins énergétiques.")

COUL_SECT = {
    "Agriculture & forêts (AFAT)": C["foret"],
    "Énergie": C["energie"],
    "Industrie (PIUP)": C["urbain"],
    "Déchets": C["neutre"],
}
COUL_GAZ = {"CO2": "#4A5568", "CH4": C["energie"], "N2O": C["risque"]}
PRG = {"CO2": 1, "CH4": 28, "N2O": 265}       # PRG 100 ans, GIEC AR5

gaz_df = pd.DataFrame(nat["ges_gaz"])
sect_df = pd.DataFrame(nat["ges_secteur"])

o1, o2 = st.tabs(["  🏭  Bilan des émissions  ", "  🌡️  Climat et besoins en énergie  "])

# ============================================================ 1. LES ÉMISSIONS
with o1:
    kpi_row([
        ("Total national 2018", f"{fr(R['ges']['total_gg'])} Gg",
         "tous secteurs, tous gaz directs, tel que publié dans l'inventaire",
         C["ink_soft"]),
        ("Agriculture & forêts", f"{R['ges']['part_afat']:.0f} %",
         "du total en masse brute — de loin le premier poste", C["foret"]),
        ("Secteur énergie", f"{R['ges']['part_energie']:.0f} %",
         "du total en masse brute — un contributeur apparemment mineur",
         C["energie"]),
        ("Part de l'énergie dans le N₂O", f"{R['ges']['energie_dans_n2o']:.0f} %",
         f"et {R['ges']['energie_dans_ch4']:.0f} % du méthane : l'énergie domine "
         "les gaz les plus réchauffants", C["risque"]),
    ])

    section("Le classement des secteurs dépend de ce qu'on mesure",
            "Changez le gaz observé, ou passez en équivalent CO₂ : "
            "le podium ne tient pas en place.")

    f1, f2 = st.columns([1.5, 1])
    with f1:
        choix_gaz = st.radio("Gaz observé",
                             ["Tous les gaz", "CO₂", "CH₄ (méthane)", "N₂O (protoxyde d'azote)"],
                             horizontal=True)
    with f2:
        base = st.radio("Unité de lecture",
                        ["Masse brute (Gg, source)", "Équivalent CO₂ (PRG 100 ans)"],
                        horizontal=False)

    cle_gaz = {"Tous les gaz": None, "CO₂": "CO2",
               "CH₄ (méthane)": "CH4", "N₂O (protoxyde d'azote)": "N2O"}[choix_gaz]
    en_co2e = base.startswith("Équivalent")

    d = gaz_df.copy()
    d["poids"] = d["gaz"].map(PRG) if en_co2e else 1
    d["val"] = d["Value"] * d["poids"]
    if cle_gaz:
        d = d[d["gaz"] == cle_gaz]
    agg = d.groupby("secteur_court", as_index=False)["val"].sum()
    agg["part"] = 100 * agg["val"] / agg["val"].sum()
    agg = agg.sort_values("val")

    g1, g2 = st.columns([1.25, 1])
    with g1:
        unite = "Gg CO₂e" if en_co2e else "Gg"
        fig = go.Figure(go.Bar(
            y=agg["secteur_court"], x=agg["val"], orientation="h",
            marker_color=[COUL_SECT.get(s, C["neutre"]) for s in agg["secteur_court"]],
            text=[f"{p:.1f} %" for p in agg["part"]], textposition="outside",
            textfont=dict(size=12.5),
            hovertemplate="%{y}<br>%{x:,.0f} " + unite + " · %{text}<extra></extra>"))
        titre = (f"Émissions par secteur — {choix_gaz.lower()}, "
                 f"{'équivalent CO₂' if en_co2e else 'masse brute'}")
        style_fig(fig, titre, hauteur=340, marge_g=0)
        fig.update_xaxes(title=unite, range=[0, agg["val"].max() * 1.22])
        fig.update_yaxes(title=None)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with g2:
        # composition interne de chaque secteur : quel gaz le compose
        comp = gaz_df.copy()
        comp["poids"] = comp["gaz"].map(PRG) if en_co2e else 1
        comp["val"] = comp["Value"] * comp["poids"]
        comp["part"] = comp.groupby("secteur_court")["val"].transform(
            lambda s: 100 * s / s.sum())
        ordre = list(agg["secteur_court"])
        fig2 = go.Figure()
        for g in ["CO2", "CH4", "N2O"]:
            sub = comp[comp["gaz"] == g].set_index("secteur_court").reindex(ordre)
            fig2.add_trace(go.Bar(
                y=ordre, x=sub["part"], orientation="h", name=g,
                marker_color=COUL_GAZ[g],
                hovertemplate="%{y} · " + g + " : %{x:.1f} % du secteur<extra></extra>"))
        style_fig(fig2, "Composition de chaque secteur, gaz par gaz (%)", hauteur=340,
                  marge_g=0)
        fig2.update_layout(barmode="stack")
        fig2.update_xaxes(range=[0, 100], ticksuffix=" %", title=None)
        fig2.update_yaxes(title=None, showticklabels=False)
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

    if en_co2e:
        e_part = float(agg.loc[agg["secteur_court"] == "Énergie", "part"].iloc[0])
        encart("alerte",
               f"<b>En équivalent CO₂, le secteur énergie passe de "
               f"{R['ges']['part_energie']:.0f} % à {e_part:.0f} % des émissions "
               f"nationales.</b> La raison : l'inventaire publie des masses brutes, où une "
               f"tonne de méthane pèse autant qu'une tonne de CO₂. Or le méthane réchauffe "
               f"{PRG['CH4']} fois plus, et le protoxyde d'azote {PRG['N2O']} fois plus. "
               f"L'énergie concentre {R['ges']['energie_dans_ch4']:.0f} % du méthane et "
               f"{R['ges']['energie_dans_n2o']:.0f} % du N₂O du pays — deux gaz typiques "
               f"de la <b>combustion incomplète de biomasse</b>, c'est-à-dire des foyers "
               f"de cuisson. Conclusion : « l'énergie ne pèse que 6 % » est une lecture "
               f"comptable, pas une lecture climatique.")
    else:
        encart("constat",
               f"En masse brute — la lecture publiée par l'inventaire — l'agriculture et "
               f"l'usage des terres représentent {R['ges']['part_afat']:.0f} % des émissions, "
               f"contre {R['ges']['part_energie']:.0f} % pour l'énergie. Cette prépondérance "
               f"inclut le <b>changement d'affectation des sols et la déforestation</b> : "
               f"elle ne contredit pas l'enjeu forestier, elle le confirme. "
               f"Mais basculez l'unité de lecture en équivalent CO₂ : le classement change "
               f"radicalement.")

    section("Le CO₂ du secteur énergie sur longue période",
            "Le fichier dédié du défi couvre plus de cinquante ans.")
    co2 = pd.DataFrame([(int(a), v) for a, v in nat["co2_energie"].items()],
                       columns=["annee", "valeur"]).sort_values("annee")
    co2 = co2[(co2["annee"] >= an_min) & (co2["annee"] <= an_max)]
    fig3 = go.Figure(go.Scatter(
        x=co2["annee"], y=co2["valeur"], mode="lines",
        line=dict(color=C["energie"], width=3), fill="tozeroy",
        fillcolor="rgba(226,144,20,.10)",
        hovertemplate="%{x} · %{y:.3f} Mt CO₂e<extra></extra>"))
    style_fig(fig3, "Émissions de CO₂ du secteur énergie (Mt CO₂e)", hauteur=300)
    fig3.update_yaxes(title="Mt CO₂e")
    fig3.update_xaxes(title=None)
    st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})
    if len(co2) > 1:
        encart("constat",
               f"Les émissions de CO₂ du secteur énergie sont passées de "
               f"{co2['valeur'].iloc[0]:.3f} à {co2['valeur'].iloc[-1]:.3f} Mt CO₂e entre "
               f"{int(co2['annee'].iloc[0])} et {int(co2['annee'].iloc[-1])}. Le niveau "
               f"absolu reste faible : l'électricité togolaise n'est pas le problème "
               f"climatique du pays. Le problème est la <b>biomasse brûlée dans les "
               f"foyers</b>, qui est comptabilisée ailleurs — en usage des terres et en "
               f"méthane.")

# ================================================================== 2. CLIMAT
with o2:
    villes = D.villes()
    temp = D.temperatures()
    cl = R["climat"]

    kpi_row([
        ("Amplitude entre stations", f"{cl['gradient']:.1f} °C",
         f"de {cl['ville_froide']} ({cl['t_froide']:.1f} °C) à "
         f"{cl['ville_chaude']} ({cl['t_chaude']:.1f} °C)", C["risque"]),
        ("Pic thermique national", f"{cl['t_mois_chaud']:.1f} °C",
         f"en {cl['mois_chaud_nom']}, en pleine saison sèche", C["risque"]),
        ("Creux thermique", f"{cl['t_mois_froid']:.1f} °C",
         f"en {cl['mois_froid_nom']}, au cœur de la saison des pluies", C["urbain"]),
        ("Amplitude jour / nuit maximale", f"{cl['amplitude_max']:.1f} °C",
         f"à {cl['amplitude_max_ville']} — le contraste croît vers le Nord",
         C["energie"]),
    ])

    section("Le gradient Sud → Nord, mois par mois",
            "10 stations, 2013-2019. Sélectionnez les villes à comparer.")

    f1, f2 = st.columns([2.4, 1])
    with f1:
        ordre_sud_nord = list(villes.sort_values("lat")["ville"])
        choix = st.multiselect("Stations affichées", ordre_sud_nord,
                               default=ordre_sud_nord,
                               help="Les stations sont listées du Sud vers le Nord.")
    with f2:
        mesure = st.selectbox("Mesure",
                              ["Température maximale", "Température minimale",
                               "Amplitude jour / nuit"])
    col_mes = {"Température maximale": "t_max", "Température minimale": "t_min",
               "Amplitude jour / nuit": "amplitude"}[mesure]

    t = temp[(temp["annee"] >= an_min) & (temp["annee"] <= an_max)]
    t = t[t["ville"].isin(choix)]

    g1, g2 = st.columns([1.35, 1])
    with g1:
        prof_mois = t.groupby(["ville", "mois"], as_index=False)[col_mes].mean()
        lat = villes.set_index("ville")["lat"]
        villes_tri = sorted(choix, key=lambda v: lat.get(v, 0))
        fig4 = go.Figure()
        for i, v in enumerate(villes_tri):
            sub = prof_mois[prof_mois["ville"] == v].sort_values("mois")
            coul = RAMPE[min(len(RAMPE) - 1, int(i / max(1, len(villes_tri) - 1) * 5))]
            coul = ["#2E6F9E", "#5A8FB5", "#E8B85C", "#E29014",
                    "#D2691E", "#C0392B"][min(5, int(i / max(1, len(villes_tri)-1) * 5))]
            fig4.add_trace(go.Scatter(
                x=[MOIS[m - 1] for m in sub["mois"]], y=sub[col_mes], name=v,
                mode="lines", line=dict(color=coul, width=2.4),
                hovertemplate=f"{v} · %{{x}} : %{{y:.1f}} °C<extra></extra>"))
        style_fig(fig4, f"{mesure} moyenne par mois (°C)", hauteur=400)
        fig4.update_yaxes(title="°C")
        fig4.update_xaxes(title=None)
        fig4.update_layout(legend=dict(orientation="v", x=1.01, y=1, xanchor="left",
                                       font=dict(size=10.5)))
        if col_mes == "t_max":
            fig4.add_vrect(x0=1.5, x1=3.5, fillcolor=C["risque"], opacity=.06, line_width=0,
                           annotation_text="pic thermique", annotation_position="top left",
                           annotation_font=dict(size=11, color=C["risque"]))
        st.plotly_chart(fig4, width="stretch", config={"displayModeBar": False})

    with g2:
        # profil latitudinal : la température suit-elle vraiment la latitude ?
        vv = villes[villes["ville"].isin(choix)]
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=vv["lat"], y=vv[col_mes if col_mes in vv.columns else "t_max"],
            mode="markers+text", text=vv["ville"], textposition="top center",
            textfont=dict(size=10, color=C["muted"]),
            marker=dict(size=13, color=vv[col_mes if col_mes in vv.columns else "t_max"],
                        colorscale=[[0, "#2E6F9E"], [.5, C["energie"]], [1, C["risque"]]],
                        line=dict(color="white", width=1.5)),
            hovertemplate="%{text}<br>latitude %{x:.2f}° · %{y:.1f} °C<extra></extra>"))
        if len(vv) > 2:
            yv = vv[col_mes if col_mes in vv.columns else "t_max"]
            a, b = np.polyfit(vv["lat"], yv, 1)
            xs = np.linspace(vv["lat"].min(), vv["lat"].max(), 20)
            fig5.add_trace(go.Scatter(x=xs, y=a * xs + b, mode="lines", showlegend=False,
                                      line=dict(color=C["neutre"], width=1.6, dash="dash"),
                                      hoverinfo="skip"))
            r = np.corrcoef(vv["lat"], yv)[0, 1]
            annote(fig5, float(xs[len(xs)//2]), float(a * xs[len(xs)//2] + b),
                   f"+{a:.2f} °C par degré<br>de latitude (r = {r:.2f})",
                   C["muted"], ax=0, ay=-46)
        style_fig(fig5, f"{mesure} selon la latitude", hauteur=400)
        fig5.update_xaxes(title="latitude Nord (°)")
        fig5.update_yaxes(title="°C")
        st.plotly_chart(fig5, width="stretch", config={"displayModeBar": False})

    encart("constat",
           f"Le Togo s'étire sur près de 700 km du Sud au Nord et cela se lit dans les "
           f"températures : {cl['gradient']:.1f} °C séparent la station la plus fraîche "
           f"({cl['ville_froide']}, sur les hauteurs des Plateaux) de la plus chaude "
           f"({cl['ville_chaude']}, dans les Savanes). Le pic national tombe en "
           f"<b>{cl['mois_chaud_nom']}</b> ({cl['t_mois_chaud']:.1f} °C de maximum moyen) — "
           f"c'est-à-dire en fin de saison sèche, avant les pluies. "
           f"L'amplitude jour/nuit croît elle aussi vers le Nord, jusqu'à "
           f"{cl['amplitude_max']:.1f} °C à {cl['amplitude_max_ville']}.")
    encart("action",
           f"<b>Le lien avec l'énergie est un argument, pas une illustration.</b> "
           f"Le maximum de besoin — ventilation, conservation des aliments, pompage d'eau, "
           f"santé des personnes fragiles — tombe en {cl['mois_chaud_nom']}, au cœur de la "
           f"saison sèche, c'est-à-dire au moment où l'ensoleillement est maximal et la "
           f"couverture nuageuse minimale. <b>La pointe de demande et la pointe de "
           f"production solaire coïncident.</b> C'est exactement la configuration où le "
           f"photovoltaïque décentralisé est le plus efficace, et elle est la plus marquée "
           f"dans les régions du Nord — celles où l'accès est le plus faible et où se "
           f"trouvent les forêts sèches les plus exposées.")

with st.expander("Méthode, données et limites de cette page"):
    st.markdown(f"""
**Inventaire GES 2018** — fichier `observationdata-xorttne.csv` du défi :
4 secteurs × 3 gaz (CO₂, CH₄, N₂O), en **Gg**.

*Point de méthode important.* Le total publié ({fr(R['ges']['total_gg'])} Gg) est la
**somme arithmétique des masses** de gaz : CO₂ + CH₄ + N₂O additionnés à poids égal.
Ce n'est donc pas un total en équivalent CO₂. Le tableau de bord propose les deux
lectures, et la seconde applique les PRG à 100 ans du GIEC (AR5) :
CH₄ × {PRG['CH4']}, N₂O × {PRG['N2O']}. **À manier avec prudence** : la valeur de N₂O
du secteur énergie ({gaz_df[(gaz_df.secteur_court == 'Énergie') & (gaz_df.gaz == 'N2O')]['Value'].iloc[0]:.0f} Gg)
est anormalement élevée au regard du total du secteur, ce qui suggère une possible
hétérogénéité d'unités dans la source. La conversion est proposée comme **test de
sensibilité** — elle montre à quel point la conclusion « l'énergie est marginale »
dépend d'une convention de mesure — et non comme un inventaire alternatif validé.

**CO₂ du secteur énergie** — fichier dédié
`emissions-de-dioxyde-de-carbone-co2-du-secteur-de-lenergie-mt-co2e-.csv`, en Mt CO₂e.

**Températures** — `observationdata-yvlucze.csv` : 10 stations, relevés mensuels
2013-2019, maximales et minimales, **au degré entier**. Conséquence directe :
le **gradient spatial** Sud → Nord est parfaitement exploitable (les écarts entre
stations dépassent largement la précision de mesure), mais la **tendance sur 7 ans**
ne l'est pas — elle n'est donc pas présentée ici comme une preuve de réchauffement.

**Les précipitations** (`AG.LND.PRCP.MM`) présentes dans le fichier Banque Mondiale
sont une **valeur constante répétée** sur toutes les années : elles ont été écartées
plutôt que tracées en fausse tendance plate.
""")

pied()

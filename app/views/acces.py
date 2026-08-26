"""Accès à l'électricité (ville / campagne) et fiabilité du réseau."""
import numpy as np
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   pied, fr, titre_carte, rgba)

nat = D.national()
R = nat["reperes"]
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

er, ec, rs, fi = R["elec_rural"], R["ecart_urbain_rural"], R["ruraux_sans_elec"], R["fiabilite"]

banniere("Accès à l'électricité et qualité du réseau",
     "Le réseau progresse, mais ni assez vite ni assez sûrement",
     "Deux questions commandent la stratégie d'électrification : à quelle vitesse l'écart "
     "ville / campagne se referme-t-il, et le courant, une fois arrivé, est-il fiable ? "
     "Les deux réponses pointent vers la même solution.",
     reperes=[("Accès rural", f"{er['valeur']:.0f} %"),
              ("Écart ville/campagne", f"{ec['valeur']:.0f} pts"),
              ("Coupures/mois", f"{fr(fi['coupures_mois'], 1)}")])

# séries complètes pour les micro-courbes des tuiles
_r = D.serie(nat, "elec_rural"); _u = D.serie(nat, "elec_urbain")
_ecart = list((_u.set_index("annee")["valeur"] - _r.set_index("annee")["valeur"]).dropna())

kpi_row([
    ("Accès rural", f"{er['valeur']:.0f} %",
     f"de la population rurale en {er['annee']}, contre "
     f"{fr(er['valeur_depart'], 1)} % en {er['annee_depart']}", C["energie"],
     f"× {er['valeur']/er['valeur_depart']:.0f} en {er['annee']-er['annee_depart']} ans",
     list(_r["valeur"])),
    ("Accès urbain", f"{ec['urbain']:.0f} %",
     "les villes sont proches de l'accès universel", C["urbain"], None,
     list(_u["valeur"])),
    ("Écart ville / campagne", f"{ec['valeur']:.0f} pts",
     "l'ampleur de la fracture à combler d'ici 2030", C["risque"],
     "au plus haut", _ecart),
    ("Coupures subies", f"{fr(fi['coupures_mois'], 1)} /mois",
     f"par les entreprises raccordées en {fi['annee']} "
     f"(enquête Banque Mondiale)", C["risque"],
     f"{fi['part_entreprises']:.0f} % touchées",
     [fi["coupures_mois_ref"], fi["coupures_mois"]]),
])

# =============================================================================
onglet1, onglet2 = st.tabs([" La fracture et sa trajectoire ",
                            " La fiabilité du réseau "])

# -------------------------------------------------------------- 1. LA FRACTURE
with onglet1:
    section("Trajectoire de l'accès, et ce qu'il faudrait pour 2030",
            "Réglez la cible : le tableau de bord recalcule l'effort annuel correspondant.")

    f1, f2, f3 = st.columns([1.1, 1, 1.4])
    with f1:
        cible = st.slider("Cible d'accès rural en 2030 (%)", 40, 100, 100, 5,
                          help="Objectif national officiel : accès universel en 2030.")
    with f2:
        montrer_proj = st.toggle("Afficher les trajectoires", value=True)
    with f3:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        st.caption("Le scénario tendanciel prolonge le rythme moyen observé depuis "
                   f"{er['annee_depart']} ; le scénario cible relie la valeur actuelle "
                   "à l'objectif choisi.")

    rural = D.serie(nat, "elec_rural", an_min, an_max)
    urbain = D.serie(nat, "elec_urbain", an_min, an_max)
    total = D.serie(nat, "elec_total", an_min, an_max)

    titre_carte("Accès à l'électricité, ville contre campagne",
                "La zone rouge mesure la fracture. Réglez la cible pour voir l'effort requis.", C["energie"])
    fig = go.Figure()
    # bande d'écart ville/campagne : la fracture devient une surface, pas deux courbes
    fig.add_trace(go.Scatter(x=urbain["annee"], y=urbain["valeur"], name="Urbain",
                             line=dict(color=C["urbain"], width=3), mode="lines",
                             hovertemplate="%{x} · %{y:.1f} %<extra>Urbain</extra>"))
    fig.add_trace(go.Scatter(x=rural["annee"], y=rural["valeur"], name="Rural",
                             line=dict(color=C["energie"], width=3), mode="lines",
                             fill="tonexty", fillcolor=rgba("risque", .10),
                             hovertemplate="%{x} · %{y:.1f} %<extra>Rural</extra>"))
    fig.add_trace(go.Scatter(x=total["annee"], y=total["valeur"], name="Ensemble du pays",
                             line=dict(color=C["sourdine"], width=1.8, dash="dot"), mode="lines",
                             hovertemplate="%{x} · %{y:.1f} %<extra>Ensemble</extra>"))

    a0, v0 = er["annee"], er["valeur"]
    if montrer_proj:
        ans = np.arange(a0, 2031)
        tend = np.clip(v0 + er["rythme_observe"] * (ans - a0), 0, 100)
        vers = v0 + (cible - v0) * (ans - a0) / (2030 - a0)
        fig.add_trace(go.Scatter(x=ans, y=tend, name="Tendanciel (rythme actuel)",
                                 line=dict(color=C["risque"], width=2, dash="dash"),
                                 mode="lines",
                                 hovertemplate="%{x} · %{y:.1f} %<extra>Tendanciel</extra>"))
        fig.add_trace(go.Scatter(x=ans, y=vers, name=f"Trajectoire vers {cible} %",
                                 line=dict(color=C["foret"], width=2.4), mode="lines",
                                 hovertemplate="%{x} · %{y:.1f} %<extra>Cible</extra>"))
        fig.add_vrect(x0=a0, x1=2030, fillcolor=C["neutre"], opacity=.06, line_width=0)
        annote(fig, 2030, cible, f"Cible {cible} %", C["foret"], ax=-42, ay=-24)
        annote(fig, 2030, float(tend[-1]), f"Tendanciel {tend[-1]:.0f} %", C["risque"],
               ax=-52, ay=30)

    style_fig(fig, hauteur=430)
    fig.update_yaxes(title="% de la population", ticksuffix=" %", range=[0, 105])
    fig.update_xaxes(title=None)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    # ---- l'effort traduit en personnes, pas en points de pourcentage
    pop_rur = rs["pop_rurale"]
    annees_restantes = 2030 - a0
    pts_requis = (cible - v0) / annees_restantes
    pers_total = pop_rur * (cible - v0) / 100
    pers_an = pers_total / annees_restantes
    pers_tend_an = pop_rur * er["rythme_observe"] / 100

    st.write("")
    kpi_row([
        ("Rythme requis", f"+{fr(pts_requis, 1)} pt/an",
         f"pour atteindre {cible} % en 2030", C["foret"]),
        ("Rythme observé", f"+{fr(er['rythme_observe'], 2)} pt/an",
         f"moyenne {er['annee_depart']}–{er['annee']}", C["risque"],
         f"× {pts_requis/er['rythme_observe']:.0f} à trouver"),
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
           f"({ec['urbain']:.0f} % contre {ec['rural']:.0f} %). Il ne s'agit pas d'un retard "
           f"qui se comble : sur {er['annee']-er['annee_depart']} ans, le rural a gagné "
           f"{er['valeur']-er['valeur_depart']:.0f} points quand l'urbain saturait. "
           f"Atteindre {cible} % en 2030 suppose de raccorder "
           f"<b>{fr(pers_an/1000)}000 ruraux par an</b>, contre environ "
           f"{fr(pers_tend_an/1000)} 000 aujourd'hui.")
    encart("action",
           "Un facteur d'accélération de cet ordre ne s'obtient pas en prolongeant le réseau "
           "national, dont le coût au raccordement croît avec la distance et la dispersion de "
           "l'habitat. Il s'obtient par des solutions décentralisées — mini-réseaux solaires "
           "et kits domestiques — déployables sans attendre la ligne moyenne tension. "
           "L'onglet suivant ajoute une seconde raison de le faire.")

# ------------------------------------------------------------- 2. LA FIABILITÉ
with onglet2:
    section("Ce que vaut un raccordement",
            "Objectif du défi : « mesurer la fiabilité du réseau (coupures) ». "
            "Les enquêtes entreprises de la Banque Mondiale fournissent quatre mesures, "
            "sur deux vagues comparables.")

    CARTES = [
        ("coupures_mois",   "Coupures par mois",              "{:.1f}", "moins de coupures"),
        ("part_touchees",   "Entreprises touchées",           "{:.1f} %", "moins d'entreprises"),
        ("pertes_ca",       "Chiffre d'affaires perdu",       "{:.1f} %", "moins de pertes"),
        ("delai_raccord",   "Délai de raccordement",          "{:.0f} j", "délai plus court"),
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
        # graphique de pente : deux vagues d'enquête, quatre indicateurs, une lecture
        titre_carte("Les quatre mesures de fiabilité, entre deux enquêtes",
                    "Base 100 = la pire des deux valeurs, pour comparer des unités différentes.", C["risque"])
        fig2 = go.Figure()
        for i, (label, a0_, v0_, a1_, v1_, coul, unite) in enumerate(lignes_pente):
            base = max(v0_, v1_)
            n0, n1 = 100 * v0_ / base, 100 * v1_ / base
            fig2.add_trace(go.Scatter(
                x=[a0_, a1_], y=[n0, n1], mode="lines+markers+text",
                line=dict(color=coul, width=2.6), marker=dict(size=9, color=coul),
                text=[f"{fr(v0_, 1)}", f"{fr(v1_, 1)}"],
                textposition=["middle left", "middle right"],
                textfont=dict(size=11.5, color=coul), name=label,
                hovertemplate=f"{label}<br>%{{x}} : %{{fr(customdata, 1)}} {unite}<extra></extra>",
                customdata=[v0_, v1_], showlegend=True))
        style_fig(fig2, hauteur=344)
        fig2.update_xaxes(tickvals=[2009, 2016], range=[2006, 2019], title=None)
        fig2.update_yaxes(title="Niveau relatif", range=[0, 118], showticklabels=False)
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

    with g2:
        dj, *_ = D.fiab(nat, "demarches_jours")
        dj = dj.drop_duplicates(subset="annee")
        titre_carte("Délai réglementaire de raccordement",
                    "Seule série annuelle disponible sur la qualité de service.", C["energie"])
        fig3 = go.Figure(go.Scatter(
            x=dj["annee"], y=dj["valeur"], mode="lines+markers",
            line=dict(color=C["energie"], width=3, shape="hv"),
            marker=dict(size=7, color=C["energie"]), fill="tozeroy",
            fillcolor=rgba("energie", .10),
            hovertemplate="%{x} · %{y:.0f} jours<extra></extra>"))
        style_fig(fig3, hauteur=344)
        fig3.update_yaxes(title="jours", range=[0, 100])
        fig3.update_xaxes(title=None, dtick=2)
        if len(dj):
            annote(fig3, int(dj["annee"].iloc[-1]), float(dj["valeur"].iloc[-1]),
                   f"{dj['valeur'].iloc[-1]:.0f} j", C["energie"], ax=-34, ay=-26)
        st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})

    encart("alerte",
           f"<b>Les coupures se raréfient, mais elles se généralisent.</b> Entre "
           f"{fi['annee_ref']} et {fi['annee']}, la fréquence baisse "
           f"({fr(fi['coupures_mois_ref'], 1)} → {fr(fi['coupures_mois'], 1)} coupures par mois), "
           f"mais la part d'entreprises qui en subissent <b>augmente de "
           f"{fi['part_entreprises_ref']:.0f} % à {fi['part_entreprises']:.0f} %</b>. "
           f"Autrement dit : le réseau s'est étendu plus vite qu'il ne s'est consolidé. "
           f"Le raccordement au réseau national ne garantit donc pas un service continu.")
    encart("action",
           "Cette conclusion se combine à la précédente. Pour un village éloigné, la question "
           "n'est pas « réseau ou solaire ? » mais « service fiable ou service intermittent ? ». "
           "Un mini-réseau solaire avec stockage offre une disponibilité prévisible, immédiate, "
           "et dimensionnable au besoin réel — là où l'extension du réseau apporterait, plus "
           "tard, un courant lui-même instable.")

with st.expander("Méthode, données et limites de cette page"):
    st.markdown(f"""
**Accès à l'électricité** — Banque Mondiale, `EG.ELC.ACCS.RU.ZS` (rural),
`EG.ELC.ACCS.UR.ZS` (urbain), `EG.ELC.ACCS.ZS` (ensemble), séries annuelles
{er['annee_depart']}–{er['annee']}.

**Fiabilité** — Enterprise Surveys : `IC.ELC.OUTG` (coupures/mois),
`IC.ELC.OUTG.ZS` (% d'entreprises touchées), `IC.FRM.OUTG.ZS` (CA perdu),
`IC.ELC.DURS` (délai de raccordement), `IC.ELC.TIME` (temps réglementaire).

**Limites à connaître.**
1. Les indicateurs de coupures portent sur les **entreprises**, pas sur les ménages :
   aucune source du défi ne mesure la fiabilité vécue par les foyers ruraux.
   Ils constituent la meilleure approximation disponible de la qualité du réseau,
   et sont plutôt un **minorant** de ce que subissent les zones rurales.
2. Deux vagues d'enquête seulement ({fi['annee_ref']} et {fi['annee']}) : la comparaison
   est un contraste, pas une tendance.
3. **Aucune donnée infranationale d'électrification** n'existe dans les 6 jeux fournis.
   Le clivage analysable est donc rural / urbain, pas région par région.
4. La projection de population retient la population rurale de
   {rs['annee_pop']} ({fr(rs['pop_rurale']/1e6, 2)} M), maintenue constante : l'effort réel
   sera supérieur si la population rurale croît.
""")

pied()

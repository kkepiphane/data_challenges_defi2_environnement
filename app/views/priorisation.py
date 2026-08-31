"""Cartographie des 53 forêts classées et désignation des priorités."""
import numpy as np
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig,
                   barres_donnees, legende, pied, fr, titre_carte, rgba, RAMPE,
                   region_active, rappel_filtre)

nat = D.national()
R = nat["reperes"]
forets = D.forets()
robust = D.robustesse()
villes = D.villes()

banniere("Les 53 forêts classées du territoire",
     "Cinquante-trois forêts classées, neuf priorités qui ne bougent pas",
     "Protéger « les forêts » n'est pas une décision opérationnelle : protéger "
     "Assoukoko l'est. Cette page construit un indice de vulnérabilité à trois "
     "composantes, le rend entièrement réglable, et vérifie quelles priorités "
     "résistent au changement de pondération.")

# Les chiffres-clés suivent le filtre régional : afficher « 53 forêts » à côté
# d'une carte qui n'en montre que douze serait un mensonge par juxtaposition.
_reg = region_active()
_f = forets[forets["region_nom_bdd"] == _reg] if _reg else forets
_fiables = _f[~_f["surface_incertaine"]]
_robustes = set(robust.loc[robust["toujours_top10"], "foret"])
_nb_rob = int(_f["etab_nom"].isin(_robustes).sum())
_ou = f"dans la région {_reg}" if _reg else "sur l'ensemble du territoire"

rappel_filtre("carte, classement et chiffres-clés de cette page")
kpi_row([
    ("Forêts classées analysées", f"{len(_f)}",
     f"{_ou}, pour {fr(_fiables['surface_ha'].sum())} ha de surface fiable "
     f"cumulée", C["foret"]),
    ("Priorités robustes", f"{_nb_rob} forêts",
     f"restent dans le top 10 national quelle que soit la pondération testée"
     + (f" — sur les {R['forets']['nb_robustes']} du pays" if _reg else ""),
     C["foret"]),
    ("Éloignement médian", f"{_f['dist_km'].median():.0f} km",
     "du pôle urbain le plus proche — proxy de la pression bois-énergie",
     C["energie"]),
    ("Surfaces à vérifier", f"{int(_f['surface_incertaine'].sum())} / {len(_f)}",
     "polygones < 10 ha, signalés et neutralisés dans l'indice", C["neutre"]),
])

# ------------------------------------------------------------------- réglages
section("Réglez l'indice, le classement et la carte suivent",
        "Les trois curseurs sont normalisés automatiquement : ce qui compte est "
        "leur poids relatif. Vous testez ainsi votre propre doctrine de priorisation.")

p1, p2, p3, p4 = st.columns(4)
with p1:
    w_enc = st.slider("Enclavement", 0, 100, 40, 5,
                      help="Distance au pôle urbain le plus proche. Plus une forêt est "
                           "loin d'une ville raccordée, plus la pression bois-énergie "
                           "sur elle est forte.")
with p2:
    w_sur = st.slider("Enjeu / surface", 0, 100, 35, 5,
                      help="Superficie du massif, en échelle logarithmique. "
                           "Protéger un grand massif a plus d'effet.")
with p3:
    w_str = st.slider("Stress thermique", 0, 100, 25, 5,
                      help="Température maximale de la zone de rattachement. "
                           "Les forêts sèches du Nord sont plus exposées.")
with p4:
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    if w_enc + w_sur + w_str == 0:      # dégénéré : on revient à la référence
        w_enc, w_sur, w_str = 40, 35, 25
        st.caption("Les trois poids sont nuls : la pondération de référence "
                   "**40 / 35 / 25** est appliquée.")
    else:
        tot_w = w_enc + w_sur + w_str
        st.caption(f"Pondération effective : **{100*w_enc/tot_w:.0f} % / "
                   f"{100*w_sur/tot_w:.0f} % / {100*w_str/tot_w:.0f} %**  \n"
                   "Pondération de référence : 40 / 35 / 25.")
tot_w = w_enc + w_sur + w_str

# La région n'est plus choisie ici : elle vient du volet et vaut pour toute
# l'application. Un filtre qui commande la carte, le classement et les stations
# climatiques n'a pas sa place au milieu d'une seule page.
reg = region_active() or "Toutes les régions"

f2, f3 = st.columns([1.2, 2])
with f2:
    nb_aff = st.slider("Forêts au classement", 5, 53, 15, 1, key="prio_nb")
with f3:
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    incl = st.checkbox("Inclure les forêts à surface incertaine", value=True,
                       key="prio_incertaines",
                       help="16 polygones font moins de 10 ha, ce qui est incompatible "
                            "avec le statut de forêt classée : leur numérisation est "
                            "probablement partielle.")

# ---------------------------------------------------- recalcul en direct du score
d = forets.copy()
d["score_live"] = 100 * (w_enc * d["enclavement_norm"]
                         + w_sur * d["surface_norm"]
                         + w_str * d["stress_norm"]) / tot_w

vue = d.copy()
if reg != "Toutes les régions":
    vue = vue[vue["region_nom_bdd"] == reg]
if not incl:
    vue = vue[~vue["surface_incertaine"]]
vue = vue.sort_values("score_live", ascending=False).reset_index(drop=True)
vue["rang_live"] = np.arange(1, len(vue) + 1)

# écart au classement de référence : le réglage change-t-il la décision ?
ref_top = list(d.sort_values("score", ascending=False).head(10)["etab_nom"])
live_top = list(d.sort_values("score_live", ascending=False).head(10)["etab_nom"])
stables = len(set(ref_top) & set(live_top))

# ------------------------------------------------------------------- carte + table
gauche, droite = st.columns([1.05, 1])

with gauche:
    fond = st.selectbox("Fond de carte", ["Clair (Carto)", "OpenStreetMap",
                                          "Aucun — mode hors ligne"],
                        label_visibility="collapsed")
    style_map = {"Clair (Carto)": "carto-positron", "OpenStreetMap": "open-street-map",
                 "Aucun — mode hors ligne": "white-bg"}[fond]

    gj = D.geojson_forets()
    ids_vue = set(vue["FID"].astype(str))
    gj_vue = {"type": "FeatureCollection",
              "features": [f for f in gj["features"] if f["id"] in ids_vue]}

    fig = go.Figure(go.Choroplethmap(
        geojson=gj_vue, locations=vue["FID"].astype(str), z=vue["score_live"],
        colorscale=[[0, RAMPE[0]], [.4, RAMPE[2]], [.72, RAMPE[4]], [1, RAMPE[5]]],
        zmin=float(d["score_live"].min()),
        zmax=float(max(d["score_live"].max(), d["score_live"].min() + 1e-6)),
        marker=dict(line=dict(color=C["foret_d"], width=.7), opacity=.9),
        colorbar=dict(title=dict(text="Indice", side="right", font=dict(size=11)),
                      thickness=11, len=.62, x=.99, tickfont=dict(size=10)),
        customdata=np.stack([vue["etab_nom"], vue["region_nom_bdd"], vue["surface_ha"],
                             vue["dist_km"], vue["rang_live"]], axis=-1),
        hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                       "Rang %{customdata[4]} · indice %{z:.0f}<br>"
                       "%{customdata[2]:,.0f} ha · %{customdata[3]:.0f} km "
                       "du pôle urbain<extra></extra>")))

    fig.add_trace(go.Scattermap(
        lat=villes["lat"], lon=villes["lon"], mode="markers+text",
        marker=dict(size=9, color=C["energie"]),
        text=villes["ville"], textposition="top right",
        textfont=dict(size=10.5, color=C["encre"]),
        hovertemplate="<b>%{text}</b><br>station de rattachement<extra></extra>",
        showlegend=False))

    fig.update_layout(
        map=dict(style=style_map, center=dict(lat=8.6, lon=1.0), zoom=5.45),
        margin=dict(l=0, r=0, t=6, b=0), height=560,
        paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False,
                                                  "scrollZoom": True})
    legende((C["foret_d"], "vert foncé = plus vulnérable"),
            (RAMPE[0], "vert clair = moins vulnérable"),
            (C["energie"], "stations de rattachement"))

with droite:
    st.markdown(
        f'<div style="font-weight:700;color:{C["foret_d"]};font-size:15px;'
        f'margin-bottom:9px">Classement · {len(vue)} forêt'
        f'{"s" if len(vue) > 1 else ""} retenue{"s" if len(vue) > 1 else ""}</div>',
        unsafe_allow_html=True)
    aff = vue.head(nb_aff)
    lignes = []
    for _, r in aff.iterrows():
        nom = str(r["etab_nom"]).replace("Forêt classée de ", "").replace(
            "Forêt classée des ", "").replace("Forêt classée ", "").replace(
            "Forêt ", "")[:28]
        lignes.append((
            [int(r["rang_live"]), nom, r["region_nom_bdd"],
             f"{r['surface_ha']:,.0f}".replace(",", " "), f"{r['dist_km']:.0f}"],
            float(r["score_live"]),
            "surface à vérifier" if r["surface_incertaine"] else None))
    st.markdown(barres_donnees(lignes, ["#", "Forêt", "Région", "ha", "km"],
                               score_max=float(d["score_live"].max())),
                unsafe_allow_html=True)

st.write("")
if reg == "Toutes les régions" and incl:
    encart("constat",
           f"Avec votre pondération ({100*w_enc/tot_w:.0f} / {100*w_sur/tot_w:.0f} / "
           f"{100*w_str/tot_w:.0f}), <b>{stables} des 10 forêts prioritaires</b> sont les "
           f"mêmes qu'avec la pondération de référence. La tête de classement — "
           f"{', '.join(n.replace('Forêt classée ', '') for n in live_top[:3])} — "
           f"ne dépend donc pas d'un arbitrage subjectif : ce sont de <b>grands massifs "
           f"enclavés</b>, éloignés de tout pôle raccordé, donc soumis à la pression "
           f"bois-énergie la plus forte, et situés dans des zones au stress thermique élevé.")

# ---------------------------------------------------------------- robustesse
section("Test de robustesse : la priorité tient-elle si l'on change d'avis ?",
        "Cinq pondérations différentes ont été appliquées lors de la construction "
        "des données. Voici l'intervalle de rang obtenu par chaque forêt.")

rb = robust.merge(d[["etab_nom", "region_nom_bdd", "score"]],
                  left_on="foret", right_on="etab_nom", how="left")
rb = rb.sort_values("rang_min").head(16)

fig2 = go.Figure()
for _, r in rb.iterrows():
    nom = str(r["foret"]).replace("Forêt classée de ", "").replace(
        "Forêt classée des ", "").replace("Forêt classée ", "")[:26]
    coul = C["foret"] if r["toujours_top10"] else C["neutre"]
    fig2.add_trace(go.Scatter(
        x=[r["rang_min"], r["rang_max"]], y=[nom, nom], mode="lines",
        line=dict(color=coul, width=6), showlegend=False, hoverinfo="skip"))
    fig2.add_trace(go.Scatter(
        x=[r["rang_min"], r["rang_max"]], y=[nom, nom], mode="markers",
        marker=dict(size=10, color=coul, line=dict(color="white", width=1.6)),
        showlegend=False,
        hovertemplate=f"{nom}<br>rang entre %{{x}}<extra></extra>"))
fig2.add_vline(x=10.5, line=dict(color=C["risque"], width=1.4, dash="dash"))
style_fig(fig2, "Intervalle de rang sur les 5 pondérations testées", hauteur=440,
          marge_g=0)
fig2.update_xaxes(title="rang (1 = plus vulnérable)", range=[0, 30], dtick=5)
fig2.update_yaxes(title=None, autorange="reversed", tickfont=dict(size=11))
fig2.add_annotation(x=10.5, y=-0.6, text="seuil du top 10", showarrow=False,
                    font=dict(size=11, color=C["risque"]), xanchor="left")
st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})
legende((C["foret"], "toujours dans le top 10 — priorité robuste"),
        (C["neutre"], "rang dépendant de la pondération"))

encart("action",
       f"<b>{R['forets']['nb_robustes']} forêts ne quittent jamais le top 10.</b> Ce sont "
       f"elles qui doivent recevoir le premier budget : le classement de tête est un "
       f"résultat des données, pas un choix d'analyste. Les forêts dont l'intervalle de "
       f"rang est large méritent une instruction complémentaire avant tout engagement — "
       f"leur position dépend de la doctrine retenue.")

with st.expander("Méthode de l'indice de vulnérabilité, données et limites"):
    st.markdown(f"""
**Construction géographique.** Les {R['forets']['nb']} polygones du fichier
`file-zones-protegees-forets-classees-*.csv` (WKT, EPSG:4326) sont reprojetés en
**UTM 31N (EPSG:32631)** pour calculer surfaces et distances en mètres — une mesure
faite directement en degrés décimaux serait fausse.

**Les trois composantes, normalisées entre 0 et 1 :**

| Composante | Ce qu'elle mesure | Pourquoi elle compte |
|---|---|---|
| **Enclavement** | distance du centroïde au pôle urbain le plus proche | proxy de la dépendance locale au bois-énergie : plus une zone est loin d'une ville raccordée, moins elle a d'alternative à la biomasse |
| **Enjeu / surface** | superficie du massif, en échelle logarithmique | l'effet d'une protection est proportionnel à ce qu'elle couvre ; l'échelle log évite qu'un seul très grand massif écrase le classement |
| **Stress thermique** | température maximale moyenne de la station de rattachement | les forêts sèches du Nord sont plus exposées au stress hydrique et au feu |

**Traitement de la qualité des données.**
- **{R['forets']['nb_incertaines']} forêts sur {R['forets']['nb']}** ont un polygone de
  moins de 10 ha, incompatible avec le statut de forêt classée : numérisation
  probablement partielle. Elles reçoivent un **flag visible** et une valeur **neutre
  (0,5)** sur la composante surface — ni pénalisées, ni survalorisées — et restent
  filtrables via la case à cocher ci-dessus.
- L'**année de classement** est absente pour 17 forêts (« Nsp », « Nps », « Jadis »).
  Aucune imputation n'a été faite : la variable est écartée du score et conservée
  en descriptif.

**Limites à connaître.**
1. L'indice mesure une **exposition au risque**, pas un état constaté de dégradation :
   le champ « état de la zone » du dictionnaire de données n'est pas exporté dans le
   fichier fourni.
2. Le rattachement climatique passe par la **station météo la plus proche** parmi 10 :
   c'est une approximation grossière pour les massifs situés à mi-chemin entre deux
   stations.
3. Les coordonnées des 10 stations ne figurent dans aucun fichier du défi ; elles ont
   été ajoutées depuis des sources géographiques publiques. C'est **le seul apport
   externe** de tout le travail (cf. `docs/sources.md`).
""")

pied()

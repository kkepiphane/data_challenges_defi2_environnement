"""Vue d'ensemble — ce que lit un décideur pressé : diagnostic, preuve, décision."""
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   titre_carte, pied, fr, rgba, RAMPE, FONT_T,
                   region_active, rappel_filtre)

nat = D.national()
R = nat["reperes"]
forets = D.forets()
robust = D.robustesse()
villes = D.villes()
an_min = st.session_state.get("an_min", 1998)
an_max = st.session_state.get("an_max", 2023)

er, ec, rs = R["elec_rural"], R["ecart_urbain_rural"], R["ruraux_sans_elec"]
cb, df_, fi = R["combustibles"], R["deforestation"], R["fiabilite"]
tr, rg = R["tapis_roulant"], R["regimes_foret"]

banniere(
    "Diagnostic national · vue d'ensemble",
    "Électrifier les campagnes sans brûler les forêts",
    "Le Togo vise l'accès universel à l'électricité en 2030. Les données du défi montrent "
    "que l'objectif ne se joue pas seulement sur le réseau : il se joue sur la cuisson des "
    "ménages, qui consomme la forêt. Diagnostic en cinq chiffres, preuve, et lieu d'action.")

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
    ("Ruraux privés d'électricité", f"{fr(tr['sans_elec_fin']/1e6, 2)} M",
     f"de personnes, soit {fr(tr['variation']/1000)} 000 de <b>plus</b> "
     f"qu'en {tr['annee_debut']}", C["risque"],
     f"+{tr['variation_pct']:.0f} %",
     [v for _, v in _prives], _bornes(_prives)),
    ("Ménages au bois ou au charbon", f"{cb['biomasse'][1]:.0f} %",
     f"en {cb['annees'][1]} — la dépendance n'a pas reculé depuis "
     f"{cb['annees'][0]}, où elle était de {cb['biomasse'][0]:.0f} %",
     C["risque"], "stable"),
    ("Forêt perdue chaque année", f"{fr(df_['perte_actuelle_ha_an'])} ha",
     f"dans le régime en cours depuis {df_['regime_depuis']}, sans une seule "
     f"année de reprise", C["risque"],
     f"÷ {rg['ralentissement']:.1f} après {rg['regimes'][0]['fin']}",
     [v for _, v in _perte], _bornes(_perte)),
    ("Accélération requise", f"× {er['facteur_acceleration']:.0f}",
     f"pour l'accès universel rural en 2030 : il faudrait "
     f"+{fr(er['rythme_requis_2030'], 1)} pt/an au lieu de "
     f"+{fr(er['rythme_observe'], 1)}", C["risque"], "hors trajectoire"),
])

st.write("")
encart("alerte",
       f"Le taux d'accès rural a été multiplié par "
       f"{er['valeur']/er['valeur_depart']:.0f} depuis {tr['annee_debut']} ; le "
       f"<b>nombre</b> de ruraux privés d'électricité a augmenté de "
       f"{tr['variation_pct']:.0f} %. Les deux sont vrais : la population rurale "
       f"a gagné {fr((tr['pop_rurale_fin']-tr['pop_rurale_debut'])/1e6, 1)} million "
       f"d'habitants sur la même période. Il faut raccorder "
       f"{fr(tr['seuil_stagnation'])} personnes par an — la seule croissance "
       f"rurale — avant même de commencer à réduire ce nombre.",
       titre="Le résultat qui commande tout le reste")

# ------------------------------------------------------ où se joue le problème
section("Où se joue le problème",
        "Les 53 forêts classées, teintées par leur indice de vulnérabilité. "
        "Cliquez un massif pour l'examiner, ou choisissez une région dans le "
        "volet.")
rappel_filtre("carte et classement ci-dessous")

_reg = region_active()
_f = forets[forets["region_nom_bdd"] == _reg] if _reg else forets
_f = _f.sort_values("score", ascending=False).reset_index(drop=True)

carte, panneau = st.columns([1.75, 1])

with carte:
    with st.container(border=True):
        titre_carte(
            f"{len(_f)} forêts classées"
            + (f" · région {_reg}" if _reg else " · ensemble du territoire"),
            "Vert foncé = plus vulnérable. Les points ambrés sont les dix "
            "stations climatiques.", C["foret"])
        gj = D.geojson_forets()
        ids = set(_f["FID"].astype(str))
        gj_vue = {"type": "FeatureCollection",
                  "features": [g for g in gj["features"] if g["id"] in ids]}
        fig_c = go.Figure(go.Choroplethmap(
            geojson=gj_vue, locations=_f["FID"].astype(str), z=_f["score"],
            colorscale=[[0, RAMPE[0]], [.4, RAMPE[2]], [.72, RAMPE[4]],
                        [1, RAMPE[5]]],
            zmin=float(forets["score"].min()), zmax=float(forets["score"].max()),
            marker=dict(line=dict(color=C["foret_d"], width=.7), opacity=.9),
            showscale=False,
            customdata=np.stack([_f["etab_nom"], _f["region_nom_bdd"],
                                 _f["surface_ha"], _f["dist_km"]], axis=-1),
            hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                           "%{customdata[2]:,.0f} ha · %{customdata[3]:.0f} km "
                           "du pôle urbain<br><i>cliquez pour "
                           "examiner</i><extra></extra>")))
        fig_c.add_trace(go.Scattermap(
            lat=villes["lat"], lon=villes["lon"], mode="markers",
            marker=dict(size=8, color=C["energie"]),
            text=villes["ville"], hoverinfo="skip", showlegend=False))
        # Le cadrage suit ce qui est affiché : filtrer sur une région et
        # rester braqué sur le pays entier laisserait douze polygones perdus
        # au milieu du Ghana et du Bénin. On calcule donc le centre et le
        # niveau de zoom depuis l'emprise réelle des massifs retenus.
        HAUTEUR_CARTE = 560
        lat0, lat1 = float(_f["clat"].min()), float(_f["clat"].max())
        lon0, lon1 = float(_f["clon"].min()), float(_f["clon"].max())
        # Étendue à couvrir, en degrés de latitude, avec une marge d'un tiers.
        # La largeur est ramenée à une hauteur équivalente par le rapport de
        # la colonne, pour qu'un massif large ne déborde pas latéralement.
        etendue = max(lat1 - lat0, (lon1 - lon0) * .72, .25) * 1.35
        # En projection de Mercator, la hauteur visible vaut environ
        # 170° x hauteur_px / (256 x 2^zoom). On inverse.
        zoom = float(np.clip(np.log2(170 * HAUTEUR_CARTE / (256 * etendue)),
                             5.6, 8.5))
        fig_c.update_layout(
            map=dict(style="carto-positron",
                     center=dict(lat=(lat0 + lat1) / 2 + .12,
                                 lon=(lon0 + lon1) / 2),
                     zoom=zoom),
            margin=dict(l=0, r=0, t=4, b=0), height=HAUTEUR_CARTE,
            paper_bgcolor="rgba(0,0,0,0)")
        # `on_select` fait de la carte un filtre, pas une illustration : le clic
        # renvoie l'indice du polygone, que l'on relit dans le tableau trié.
        clic = st.plotly_chart(fig_c, width="stretch", on_select="rerun",
                               selection_mode="points", key="carte_diagnostic",
                               config={"displayModeBar": False,
                                       "scrollZoom": True})

def _massif_clique(evenement, table):
    """Massif désigné par un clic sur la carte, ou None.

    L'état de sélection est un dictionnaire — on le lit donc par clés, seul
    accès garanti. Plotly renvoie l'indice du point dans la trace ; si un jour
    il ne renvoyait que l'identifiant du polygone, la seconde branche prend le
    relais plutôt que de laisser le panneau vide sans explication.
    """
    points = (evenement or {}).get("selection", {}).get("points", [])
    if not points:
        return None
    p0 = points[0]
    i = p0.get("point_index")
    if i is not None and 0 <= i < len(table):
        return table.iloc[i]
    fid = p0.get("location")
    if fid is not None:
        ligne = table[table["FID"].astype(str) == str(fid)]
        if len(ligne):
            return ligne.iloc[0]
    return None


with panneau:
    choisie = _massif_clique(clic, _f)

    if choisie is not None:
        rang_nat = int(forets.sort_values("score", ascending=False)
                       .reset_index(drop=True)
                       .index[forets.sort_values("score", ascending=False)
                              .reset_index(drop=True)["etab_nom"]
                              == choisie["etab_nom"]][0]) + 1
        robuste = choisie["etab_nom"] in set(
            robust.loc[robust["toujours_top10"], "foret"])
        with st.container(border=True):
            titre_carte(str(choisie["etab_nom"]),
                        f"{choisie['region_nom_bdd']} · "
                        f"{choisie['prefecture_nom_bdd']}", C["foret_d"])
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr;'
                f'gap:14px 18px;padding:0 4px 8px">'
                + "".join(
                    f'<div><div style="font-size:10.5px;font-weight:700;'
                    f'letter-spacing:.4px;text-transform:uppercase;'
                    f'color:{C["sourdine"]}">{k}</div>'
                    f'<div style="font-size:17px;font-weight:700;color:{c};'
                    f'margin-top:2px">{v}</div></div>'
                    for k, v, c in [
                        ("Rang national", f"{rang_nat} / {len(forets)}",
                         C["risque"] if rang_nat <= 10 else C["encre"]),
                        ("Indice", f"{choisie['score']:.0f} / 100", C["foret_d"]),
                        ("Surface", f"{fr(choisie['surface_ha'])} ha",
                         C["encre"]),
                        ("Pôle urbain le plus proche",
                         f"{choisie['dist_km']:.0f} km", C["energie"]),
                    ])
                + '</div>', unsafe_allow_html=True)
            if choisie["surface_incertaine"]:
                st.caption("⚠ Polygone de moins de 10 ha : numérisation "
                           "probablement partielle. La surface est neutralisée "
                           "dans l'indice.")
            elif robuste:
                st.caption("✓ Reste dans le top 10 quelle que soit la "
                           "pondération testée — priorité robuste.")
            if _reg != choisie["region_nom_bdd"]:
                if st.button(f"Filtrer sur la région {choisie['region_nom_bdd']}",
                             width="stretch"):
                    st.session_state["region_demandee"] = str(
                        choisie["region_nom_bdd"])
                    st.rerun()
    else:
        with st.container(border=True):
            titre_carte("Les massifs les plus vulnérables",
                        "Cliquez un polygone sur la carte pour le détail.",
                        C["foret"])
            lignes = "".join(
                f'<tr style="border-top:1px solid {C["bord"]}">'
                f'<td style="padding:7px 10px;font-size:12.5px;text-align:right;'
                f'color:{C["sourdine"]};font-variant-numeric:tabular-nums">'
                f'{i + 1}</td>'
                f'<td style="padding:7px 10px;font-size:12.8px;font-weight:600;'
                f'color:{C["encre"]}">{str(r["etab_nom"]).replace("Forêt classée de ", "").replace("Forêt classée des ", "").replace("Forêt classée ", "")[:26]}</td>'
                f'<td style="padding:7px 10px;font-size:12.2px;'
                f'color:{C["encre_2"]}">{r["region_nom_bdd"]}</td>'
                f'<td style="padding:7px 10px;font-size:12.2px;text-align:right;'
                f'font-variant-numeric:tabular-nums;color:{C["encre_2"]}">'
                f'{fr(r["surface_ha"])} ha</td></tr>'
                for i, r in _f.head(8).iterrows())
            st.markdown(
                f'<div style="overflow:auto;border:1px solid {C["bord"]};'
                f'border-radius:8px;margin:0 2px">'
                f'<table style="width:100%;border-collapse:collapse">'
                f'<tbody>{lignes}</tbody></table></div>',
                unsafe_allow_html=True)
            st.page_link("views/priorisation.py",
                         label="Le classement complet et ses trois curseurs",
                         icon=":material/arrow_forward:")

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
    # Pas de titre d'axe : la légende nomme déjà chaque série avec son unité,
    # et deux titres verticaux sur deux panneaux se chevauchaient.
    fig.update_yaxes(title=None, ticksuffix=" %", range=[0, 40], row=1, col=1)
    fig.update_yaxes(title=None, ticksuffix=" %", row=2, col=1)
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

# ------------------------------------------------------------ quatre constats
section("Quatre constats, quatre pages",
        "Chaque constat est démontré, chiffré et sourcé dans sa page.")
CARTES = [
    ("Électrification", C["energie"],
     f"{ec['valeur']:.0f} points d'écart ville / campagne, et "
     f"{fi['part_entreprises']:.0f} % des entreprises subissent des coupures",
     "views/acces.py"),
    ("Cuisson", C["risque"],
     f"{R['renouvelable_piege']['part_renouvelable']:.0f} % d'énergie "
     f"« renouvelable » pour "
     f"{R['renouvelable_piege']['part_cuisson_propre']:.0f} % de cuisson propre",
     "views/cuisson.py"),
    ("Inventaire", C["urbain"],
     f"{R['ges']['part_energie']:.0f} % des émissions totales, mais "
     f"{R['ges']['energie_dans_n2o']:.0f} % du protoxyde d'azote",
     "views/emissions.py"),
    ("Forêts", C["foret"],
     f"{R['forets']['nb_robustes']} massifs sur {R['forets']['nb']} restent "
     f"prioritaires quelle que soit la pondération", "views/priorisation.py"),
]
cols = st.columns(4, gap="small")
for col, (objectif, coul, txt, cible) in zip(cols, CARTES):
    with col:
        st.markdown(
            f'<div style="font-size:10.5px;font-weight:700;letter-spacing:.55px;'
            f'text-transform:uppercase;color:{coul};margin-bottom:5px">'
            f'{objectif}</div>'
            f'<div style="font-size:12.5px;color:{C["encre_2"]};'
            f'line-height:1.5;min-height:54px">{txt}</div>',
            unsafe_allow_html=True)
        st.page_link(cible, label="Voir la page",
                     icon=":material/arrow_forward:")

# ------------------------------------------------------------------------ décision
st.write("")
encart("action",
       f"Trois leviers sortent des données, dans cet ordre de priorité : "
       f"<b>(1)</b> la cuisson propre, parce qu'elle touche {cb['biomasse'][1]:.0f} % des "
       f"ménages, cause {fr(df_['perte_actuelle_ha_an'])} ha de perte forestière par an et "
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

"""Ce que valent les données avant ce qu'elles disent : audit, méthode, limites."""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import data as D
from theme import (C, banniere, section, kpi_row, encart, style_fig, annote,
                   titre_carte, pied, fr, rgba, telecharger, reglages, jetons)

nat = D.national()
R = nat["reperes"]
qual = pd.DataFrame(nat["qualite"])
verif = D.verification()
rg, us = R["regimes_foret"], R["usage_sols"]

banniere(
    "Qualité des données, méthode et limites",
    "Six jeux de données, trente-deux séries auditées, six défauts qui changent la lecture",
    "Un tableau de bord qui ne dit pas ce que valent ses données demande qu'on lui fasse "
    "confiance. Celui-ci mesure la qualité de chaque série par un test automatique, "
    "publie les défauts trouvés, et fait recalculer tous ses chiffres clés par un second "
    "programme écrit indépendamment du premier. Cette page est le résultat de ces deux "
    "contrôles.")

n_sr = int((qual["gravite"] == 0).sum())
n_struct = int((qual["gravite"] >= 2).sum())

kpi_row([
    ("Séries auditées", f"{len(qual)} séries",
     f"toutes celles qui alimentent une page du tableau de bord, testées par la "
     f"même procédure", C["encre_2"]),
    ("Sans réserve", f"{n_sr} / {len(qual)}",
     "exploitables telles quelles, sans précaution de lecture particulière",
     C["foret"]),
    ("Défauts structurels", f"{n_struct} séries",
     "série interpolée, gelée ou constante : le défaut change la conclusion, "
     "pas seulement la précision", C["risque"]),
    ("Chiffres recontrôlés",
     f"{verif['n_conformes']} / {verif['n_controles']}" if verif else "audit non lancé",
     (f"recalculés depuis <code>data/raw/</code> par un second programme, "
      f"le {verif['date']} — {verif['n_ecarts']} écart") if verif else
     "lancer <code>python src/verify.py</code>",
     C["foret"] if verif and not verif["n_ecarts"] else C["neutre"]),
])

# =============================================================================
o1, o2, o3 = st.tabs([" Audit automatique des séries ",
                      " Le cas de la série forestière ",
                      " Sources, chaîne de traitement et limites "])

# ---------------------------------------------------------------- 1. L'AUDIT
with o1:
    section("Un même test appliqué à toutes les séries",
            "Trois questions, posées automatiquement : combien de valeurs "
            "distinctes ? combien de pentes distinctes ? les dernières années "
            "sont-elles identiques ? Une série qui échoue à l'une des trois "
            "n'est pas fausse — elle ne dit simplement pas ce qu'elle a l'air "
            "de dire.")

    VERDICTS = {
        0: ("Exploitable", C["foret"],
            "aucune anomalie de structure détectée"),
        1: ("À lire comme un contraste", C["energie"],
            "trop peu de points pour parler de tendance"),
        2: ("Défaut structurel", C["risque"],
            "interpolée, gelée : la lecture annuelle est trompeuse"),
        3: ("Inutilisable", C["risque"],
            "une seule valeur répétée sur toute la période"),
    }

    with reglages("Filtrer l'audit",
                  "L'export reprend exactement la sélection affichée."):
        c1, c2 = st.columns([1.6, 1])
        with c1:
            choix = st.multiselect(
                "Verdicts affichés",
                [VERDICTS[g][0] for g in sorted(VERDICTS)],
                default=[VERDICTS[g][0] for g in sorted(VERDICTS)],
                key="donnees_verdicts",
                help="Décochez « Exploitable » pour ne garder que les séries "
                     "qui demandent une précaution de lecture.")
        with c2:
            tri = st.radio("Trier par", ["Gravité", "Nom de la série",
                                         "Nombre de points"],
                           horizontal=False, key="donnees_tri")

    gravites = [g for g, (lib, *_) in VERDICTS.items() if lib in choix]
    vue = qual[qual["gravite"].isin(gravites)].copy()
    vue = vue.sort_values({"Gravité": ["gravite", "nom"],
                           "Nom de la série": ["nom"],
                           "Nombre de points": ["n"]}[tri],
                          ascending=(tri != "Gravité"))
    jetons(("Séries affichées", f"{len(vue)} / {len(qual)}"),
           ("Tri", tri.lower()))

    if vue.empty:
        st.info("Aucune série ne correspond à ce filtre.")
    else:
        lignes = ""
        for _, r in vue.iterrows():
            lib, coul, _ = VERDICTS[r["gravite"]]
            lignes += (
                f'<tr style="border-top:1px solid {C["bord"]}">'
                f'<td style="padding:8px 12px;font-size:12.6px;font-weight:600;'
                f'color:{C["encre"]}">{r["nom"]}</td>'
                f'<td style="padding:8px 12px;font-size:11.5px;'
                f'font-family:ui-monospace,monospace;color:{C["sourdine"]}">'
                f'{r["code"]}</td>'
                f'<td style="padding:8px 12px;font-size:12.4px;text-align:right;'
                f'font-variant-numeric:tabular-nums;color:{C["encre_2"]}">'
                f'{r["n"]}</td>'
                f'<td style="padding:8px 12px;font-size:12.4px;'
                f'color:{C["encre_2"]};white-space:nowrap">'
                f'{r["debut"]}–{r["fin"]}</td>'
                f'<td style="padding:8px 12px;font-size:12.4px;text-align:right;'
                f'font-variant-numeric:tabular-nums;color:{C["encre_2"]}">'
                f'{r["valeurs_distinctes"]}</td>'
                f'<td style="padding:8px 12px"><span style="font-size:10.5px;'
                f'font-weight:700;color:{coul};text-transform:uppercase;'
                f'letter-spacing:.4px">{lib}</span>'
                f'<div style="font-size:12px;color:{C["sourdine"]};'
                f'margin-top:2px;line-height:1.4">{r["verdict"]}</div></td></tr>')
        entetes = ["Série", "Code source", "Points", "Période",
                   "Valeurs distinctes", "Verdict de l'audit"]
        head = "".join(
            f'<th style="text-align:{"right" if h in ("Points", "Valeurs distinctes") else "left"};'
            f'padding:9px 12px;color:{C["sur_nuit"]};font-weight:600;font-size:10.5px;'
            f'text-transform:uppercase;letter-spacing:.5px">{h}</th>' for h in entetes)
        st.markdown(
            f'<div style="overflow:auto;border:1px solid {C["bord"]};'
            f'border-radius:10px;background:{C["surface"]}">'
            f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr style="background:{C["nuit"]}">{head}</tr></thead>'
            f'<tbody>{lignes}</tbody></table></div>', unsafe_allow_html=True)
        st.write("")
        telecharger(vue, "audit_qualite_series", "Audit filtré (CSV)")

    st.write("")
    encart("methode",
           "<b>Comment le test fonctionne.</b> Pour chaque série, on calcule les "
           "écarts d'une année à la suivante. Si tous ces écarts sont égaux sur de "
           "longues plages, la série n'a pas été mesurée chaque année : elle a été "
           "<b>interpolée linéairement</b> entre quelques points de référence, et le "
           "nombre de ruptures de pente donne le nombre de mesures réellement "
           "indépendantes. Si les dernières années répètent la même valeur, la série "
           "a une <b>queue gelée</b> : la source a cessé de la mettre à jour sans le "
           "signaler. Si une seule valeur revient partout, la série ne porte aucune "
           "information temporelle. Le test est dans "
           "<code>src/build_gold.py</code>, section 8.5 ; son résultat est écrit "
           "dans le fichier gold et relu ici, jamais saisi à la main.",
           titre="Le test, en clair")

    encart("action",
           "<b>Ce que l'audit a changé dans ce tableau de bord.</b> Les "
           "<b>précipitations</b> ont été retirées de toutes les pages : une valeur "
           "unique répétée sur 61 ans aurait produit une fausse tendance plate. La "
           "comparaison <b>forêt / surface agricole</b> s'arrête à "
           f"{us['agri_derniere_maj']} et non à {us['agri_derniere_maj'] + us['agri_ans_geles']}, "
           f"parce que la surface agricole est gelée depuis {us['agri_ans_geles']} ans. "
           "La <b>perte forestière annuelle</b> est présentée par régime et non en "
           "moyenne, parce que la série n'en contient que deux. Et les "
           "<b>combustibles de cuisson</b> sont lus comme un contraste entre deux "
           "enquêtes, jamais comme une tendance.")

# ------------------------------------------------- 2. LA SÉRIE FORESTIÈRE
with o2:
    section("Trente-deux points annuels, trois mesures",
            "C'est le défaut le plus lourd de conséquences du dossier : il change "
            "à la fois le chiffre de la déforestation et ce qu'on peut en conclure.")

    fo = D.serie(nat, "foret_km2")
    ans = list(fo["annee"])
    val = list(fo["valeur"])
    pentes = [round(b - a, 1) for a, b in zip(val, val[1:])]
    ruptures = [ans[i + 1] for i in range(1, len(pentes))
                if pentes[i] != pentes[i - 1]]
    ancres = [ans[0]] + ruptures + [ans[-1]]

    g1, g2 = st.columns([1.35, 1])
    with g1:
        with st.container(border=True):
            titre_carte("La série forestière et ses points d'ancrage",
                        "Les points pleins sont les seules mesures indépendantes. "
                        "Entre eux, la courbe est une droite : chaque écart annuel "
                        "y est rigoureusement identique.", C["foret"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=ans, y=val, mode="lines", name="Série publiée (annuelle)",
                line=dict(color=C["foret"], width=2.6),
                fill="tozeroy", fillcolor=rgba("foret", .08),
                hovertemplate="%{x} · %{y:,.0f} km²<extra>Valeur publiée</extra>"))
            fig.add_trace(go.Scatter(
                x=ancres, y=[val[ans.index(a)] for a in ancres],
                mode="markers", name="Mesures indépendantes",
                marker=dict(size=13, color=C["risque"],
                            line=dict(color="white", width=2)),
                hovertemplate="%{x} · %{y:,.0f} km²"
                              "<extra>Point de référence</extra>"))
            style_fig(fig, hauteur=380)
            fig.update_yaxes(title="km² de couvert forestier", range=[11500, 14200])
            fig.update_xaxes(title=None)
            for r_ in rg["regimes"]:
                milieu = (r_["debut"] + r_["fin"]) // 2
                y_mil = float(np.interp(milieu, ans, val))
                annote(fig, milieu, y_mil,
                       f"−{fr(r_['perte_ha_an'])} ha/an", C["risque"],
                       ax=0, ay=42, fleche=False)
            st.plotly_chart(fig, width="stretch",
                            config={"displayModeBar": False})
            telecharger(pd.DataFrame({"annee": ans, "foret_km2": val}),
                        "serie_forestiere_annuelle")

    with g2:
        with st.container(border=True):
            titre_carte("Les écarts d'une année à la suivante",
                        "Une série mesurée chaque année produirait un nuage. "
                        "Celle-ci ne prend que deux valeurs.", C["risque"])
            fig2 = go.Figure(go.Bar(
                x=ans[1:], y=[-p * 100 for p in pentes],
                marker_color=[C["risque"] if p < -50 else C["energie"]
                              for p in pentes],
                hovertemplate="%{x} · %{y:,.0f} ha perdus<extra></extra>"))
            style_fig(fig2, hauteur=380, marge_g=0)
            fig2.update_yaxes(title="hectares perdus dans l'année",
                              range=[0, 10600])
            fig2.update_xaxes(title=None, dtick=5)
            st.plotly_chart(fig2, width="stretch",
                            config={"displayModeBar": False})
            telecharger(pd.DataFrame({
                "annee": ans[1:],
                "perte_ha": [-p * 100 for p in pentes]}),
                "ecarts_annuels_foret")

    reg = pd.DataFrame(rg["regimes"])
    kpi_row([
        ("Points annuels publiés", f"{len(ans)} mesures",
         f"de {ans[0]} à {ans[-1]}, un par an en apparence", C["neutre"]),
        ("Mesures indépendantes", f"{rg['n_mesures_independantes']} mesures",
         "les extrémités des segments linéaires — tout le reste est calculé",
         C["risque"]),
        ("Régime des années 1990", f"{fr(rg['perte_ancienne_ha_an'])} ha/an",
         f"entre {reg.iloc[0]['debut']} et {reg.iloc[0]['fin']}", C["risque"]),
        ("Régime en cours", f"{fr(rg['perte_recente_ha_an'])} ha/an",
         f"depuis {reg.iloc[-1]['debut']} — soit "
         f"{rg['ralentissement']:.1f} fois moins", C["energie"]),
    ])

    st.write("")
    encart("alerte",
           f"<b>Le chiffre de {fr(rg['moyenne_toutes_periodes'])} hectares perdus "
           f"par an, obtenu en divisant la perte totale par le nombre d'années, "
           f"ne correspond à aucune année réelle.</b> Il mélange un régime à "
           f"{fr(rg['perte_ancienne_ha_an'])} ha/an, valable jusqu'en "
           f"{reg.iloc[0]['fin']}, et un régime à {fr(rg['perte_recente_ha_an'])} ha/an "
           f"qui court depuis. Toute projection à 2030 doit partir du second : c'est "
           f"celui qui décrit la situation d'aujourd'hui. C'est le chiffre retenu "
           f"dans les simulateurs de ce tableau de bord.")
    encart("constat",
           f"<b>Ce défaut a aussi une bonne nouvelle à livrer.</b> La déforestation "
           f"togolaise a été divisée par {rg['ralentissement']:.1f} après "
           f"{reg.iloc[0]['fin']} — un résultat que la moyenne sur trente ans efface "
           f"complètement. Elle n'a en revanche jamais cessé : le régime en cours est "
           f"stable à {fr(rg['perte_recente_ha_an'])} ha/an, sans une seule année de "
           f"reprise du couvert. Et la série, étant interpolée, est <b>incapable de "
           f"détecter un retournement récent</b> : elle ne le montrerait qu'au "
           f"prochain inventaire de référence. C'est précisément l'argument pour "
           f"créer un suivi surfacique par massif, recommandé dans la page "
           f"« Recommandations ».")

# --------------------------------------------- 3. SOURCES ET CHAÎNE
with o3:
    section("Les six jeux de données du défi",
            "Aucun autre fichier n'a été utilisé. L'unique apport externe est "
            "signalé en clair.")

    JEUX = [
        ("Indicateurs Banque Mondiale", "indicators-tgo.csv",
         "3 440 indicateurs, 1960-2023",
         "Accès à l'électricité et à la cuisson propre, combustibles des ménages, "
         "couvert forestier, usage des sols, population, air et santé, fiabilité "
         "du réseau.",
         "22 % de doublons stricts supprimés ; précipitations écartées "
         "(valeur constante) ; séries forestières signalées comme interpolées."),
        ("Inventaire national des GES 2018", "observationdata-xorttne.csv",
         "4 secteurs × 3 gaz",
         "Bilan des émissions par secteur et par gaz, en masse brute (Gg).",
         "Coquille corrigée dans le libellé du N₂O ; total publié identifié comme "
         "une somme de masses, pas un équivalent CO₂."),
        ("Relevés météorologiques", "observationdata-yvlucze.csv",
         "10 stations, mensuel 2013-2019",
         "Températures maximales et minimales, gradient Sud → Nord, "
         "rattachement climatique des forêts.",
         "Valeurs au degré entier : gradient spatial exploité, tendance sur "
         "7 ans écartée."),
        ("Zones protégées et forêts classées", "file-zones-protegees-*.csv",
         "53 polygones WKT",
         "Cartographie, surfaces, distances aux pôles urbains, indice de "
         "vulnérabilité.",
         "Reprojection UTM 31N avant tout calcul ; 16 polygones < 10 ha "
         "signalés et neutralisés ; 17 années de classement absentes, "
         "aucune imputation."),
        ("CO₂ du secteur énergie", "emissions-de-dioxyde-de-carbone-*.csv",
         "série longue, Mt CO₂e",
         "Trajectoire des émissions énergétiques sur plus de cinquante ans.",
         "Aucun correctif nécessaire."),
        ("Énergies renouvelables et déchets", "energies-renouvelables-*.csv",
         "part de l'énergie finale",
         "Confrontation du taux « renouvelable » à l'accès à une cuisson propre.",
         "Aucun correctif nécessaire ; c'est l'interprétation du chiffre qui "
         "est en cause, pas sa valeur."),
    ]
    for nom, fichier, taille, usage, correctif in JEUX:
        with st.container(border=True):
            st.markdown(
                f'<div style="padding:4px 8px 8px">'
                f'<div style="display:flex;align-items:baseline;gap:12px;'
                f'flex-wrap:wrap">'
                f'<span style="font-size:15px;font-weight:700;color:{C["encre"]}">'
                f'{nom}</span>'
                f'<span style="font-size:11.5px;font-family:ui-monospace,monospace;'
                f'color:{C["sourdine"]}">{fichier}</span>'
                f'<span style="font-size:11px;color:{C["sourdine"]};'
                f'margin-left:auto">{taille}</span></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;'
                f'margin-top:11px">'
                f'<div><div style="font-size:10.5px;font-weight:700;'
                f'letter-spacing:.4px;text-transform:uppercase;color:{C["sourdine"]};'
                f'margin-bottom:4px">Ce qu\'il sert à établir</div>'
                f'<div style="font-size:12.6px;color:{C["encre_2"]};'
                f'line-height:1.55">{usage}</div></div>'
                f'<div><div style="font-size:10.5px;font-weight:700;'
                f'letter-spacing:.4px;text-transform:uppercase;color:{C["sourdine"]};'
                f'margin-bottom:4px">Correctif qualité appliqué</div>'
                f'<div style="font-size:12.6px;color:{C["encre_2"]};'
                f'line-height:1.55">{correctif}</div></div></div></div>',
                unsafe_allow_html=True)

    section("La chaîne de traitement",
            "Quatre étapes, toutes rejouables depuis les fichiers bruts. "
            "Aucun chiffre du tableau de bord ni du rapport n'est saisi à la main.")

    ETAPES = [
        ("1", "build_gold.py", "Bronze → gold",
         "Lit les six fichiers bruts, applique les correctifs qualité, calcule "
         "les repères décisionnels, les analyses croisées et l'audit des séries. "
         "Écrit un journal détaillant chaque traitement.", C["urbain"]),
        ("2", "verify.py", "Audit d'intégrité",
         f"Recalcule {verif['n_controles'] if verif else '59'} chiffres clés "
         "directement depuis les fichiers bruts, avec un code écrit sans "
         "réutiliser une ligne du pipeline, et sort en erreur au moindre écart.",
         C["foret"]),
        ("3", "make_figures.py", "Figures du rapport",
         "Génère les figures du rapport depuis les mêmes données gold et la "
         "même palette que le tableau de bord — écran et papier ne peuvent pas "
         "diverger.", C["energie"]),
        ("4", "make_report.py / make_pptx.py", "Rapport et présentation",
         "Assemblent le rapport HTML imprimable et la présentation, en "
         "réinjectant les chiffres du fichier gold.", C["risque"]),
    ]
    cols = st.columns(4, gap="small")
    for col, (n, fichier, titre, txt, coul) in zip(cols, ETAPES):
        with col:
            st.markdown(
                f'<div class="carte-relais" style="background:{C["surface"]};'
                f'border:1px solid {C["bord"]};border-radius:10px;'
                f'padding:15px 17px 16px">'
                f'<div style="display:flex;align-items:baseline;gap:9px">'
                f'<span style="font-size:20px;font-weight:800;color:{coul};'
                f'line-height:1">{n}</span>'
                f'<span style="font-size:14.5px;font-weight:700;'
                f'color:{C["encre"]}">{titre}</span></div>'
                f'<div style="font-size:11px;font-family:ui-monospace,monospace;'
                f'color:{C["sourdine"]};margin-top:6px">{fichier}</div>'
                f'<div style="font-size:12px;color:{C["sourdine"]};margin-top:8px;'
                f'line-height:1.5">{txt}</div></div>', unsafe_allow_html=True)

    if verif:
        st.write("")
        section("Le détail de l'audit d'intégrité",
                f"{verif['n_conformes']} contrôles sur {verif['n_controles']} "
                f"conformes au {verif['date']}. Chaque ligne compare une valeur "
                f"recalculée depuis les fichiers bruts à la valeur publiée.")
        ctrl = pd.DataFrame(verif["controles"])
        ctrl["Verdict"] = np.where(ctrl["conforme"], "conforme", "ÉCART")
        ctrl = ctrl.rename(columns={"libelle": "Chiffre contrôlé",
                                    "valeur_brute": "Recalculé depuis data/raw",
                                    "valeur_publiee": "Publié",
                                    "unite": "Unité"})
        st.dataframe(ctrl[["Chiffre contrôlé", "Recalculé depuis data/raw",
                           "Publié", "Unité", "Verdict"]],
                     width="stretch", hide_index=True, height=330,
                     column_config={
                         "Recalculé depuis data/raw":
                             st.column_config.NumberColumn(format="%.4f"),
                         "Publié": st.column_config.NumberColumn(format="%.4f"),
                     })
        telecharger(ctrl, "audit_integrite", "Audit d'intégrité (CSV)")

    section("Ce que ces données ne permettent pas de dire",
            "Le périmètre des conclusions s'arrête là où s'arrêtent les preuves.")
    st.markdown(f"""
- **Aucun coût, aucun budget.** Les six jeux de données ne contiennent ni prix
  d'équipement, ni coût de raccordement, ni budget public. Les recommandations
  portent donc sur un **ordre de priorité et des cibles physiques**, jamais sur
  un plan de financement.
- **Aucune maille infranationale pour l'énergie.** L'électrification, la cuisson
  et les émissions ne sont disponibles qu'au niveau national. Le seul croisement
  spatial rigoureux possible est celui construit ici : forêts × stations météo ×
  éloignement urbain.
- **Le lien cuisson → déforestation reste corrélatif.** Aucun fichier ne mesure
  les prélèvements de bois-énergie. Ce que les données permettent, en revanche,
  c'est de **mesurer le moteur concurrent** : l'expansion agricole, qui gagne
  {us['ratio_agri_foret']:.1f} fois ce que la forêt perd. C'est pourquoi
  l'attribution reste un curseur explicite dans les simulateurs, borné par cette
  mesure et non fixé arbitrairement.
- **La fiabilité est mesurée sur les entreprises**, pas sur les ménages, et sur
  deux vagues d'enquête seulement ({R['fiabilite']['annee_ref']} et
  {R['fiabilite']['annee']}).
- **Les températures sont au degré entier**, sur sept ans : le gradient spatial
  est exploitable, la tendance temporelle ne l'est pas.
- **Trois indicateurs manquent** pour piloter cette politique et devraient être
  créés : la disponibilité horaire du service électrique, un suivi surfacique
  par massif forestier, et une enquête ménages sur les combustibles plus
  fréquente que tous les trois ans.
""")

    encart("methode",
           "<b>Le seul apport extérieur aux six fichiers du défi</b> est constitué "
           "des <b>coordonnées géographiques des dix stations météorologiques</b>, "
           "absentes de toutes les sources fournies et sans lesquelles aucun "
           "croisement climat × forêt n'est possible. Elles figurent en clair dans "
           "<code>src/build_gold.py</code>. S'y ajoutent deux constantes "
           "scientifiques utilisées pour la lecture en équivalent CO₂ — les "
           "pouvoirs de réchauffement global du GIEC (CH₄ × 28, N₂O × 265) — et "
           "les valeurs des curseurs, qui sont des hypothèses réglées par "
           "l'utilisateur et étiquetées comme telles.")

pied()

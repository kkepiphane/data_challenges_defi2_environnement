"""
Système visuel du tableau de bord — Défi 2 (Togo).

Une seule règle de couleur, appliquée partout :
    ambre  = énergie / électricité      vert  = forêt / solution propre
    rouge  = biomasse / risque / émission   bleu = urbain / contexte
    gris   = donnée incertaine ou absente

Tout ce qui est visuel passe par ce module : aucune couleur en dur ailleurs.
"""
import streamlit as st

# --------------------------------------------------------------------- couleurs
C = {
    "energie":       "#E29014",   # ambre — énergie, électricité
    "energie_l":     "#FDF0DA",
    "foret":         "#1B7A43",   # vert — forêt, propre, solution
    "foret_d":       "#0C4F2B",
    "foret_l":       "#E3F1E8",
    "risque":        "#C0392B",   # rouge — biomasse, émissions, alerte
    "risque_l":      "#FBE4E1",
    "urbain":        "#2E6F9E",   # bleu — urbain, contexte
    "urbain_l":      "#E2EDF5",
    "neutre":        "#94A3B8",   # gris — incertain / absent
    "neutre_l":      "#F1F5F9",
    "ink":           "#152238",
    "ink_soft":      "#3D4A5C",
    "muted":         "#6B7A8D",
    "line":          "#E4E9EF",
    "canvas":        "#FAFBFC",
    "white":         "#FFFFFF",
}
# rampe séquentielle « pression » (bas -> haut), lisible en niveaux de gris
RAMPE = ["#E3F1E8", "#B7DCC4", "#7FC095", "#41A067", "#1B7A43", "#0C4F2B"]
DRAPEAU = ("#006A4E", "#FFCE00", "#D21034")   # filet tricolore togolais

FONT = "Inter, 'Segoe UI', system-ui, sans-serif"
MOIS = ["Janv", "Févr", "Mars", "Avr", "Mai", "Juin",
        "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]

SOURCES = ("Sources : datalab.gouv.tg — 6 jeux de données du Défi 2 (Banque Mondiale, "
           "inventaire GES 2018, stations météo, forêts classées). "
           "Seul apport externe : les coordonnées des 10 stations (cf. docs/sources.md).")


# ------------------------------------------------------------------------ CSS
def inject_css():
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, .stMetric { font-family: Inter, 'Segoe UI', system-ui, sans-serif; }
#MainMenu, footer, header [data-testid="stStatusWidget"] { visibility: hidden; }
.block-container { padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1260px; }
section[data-testid="stSidebar"] { background: #0C4F2B; }
section[data-testid="stSidebar"] * { color: #E8F3EC !important; }
section[data-testid="stSidebar"] .stSlider label { font-size: 12.5px; font-weight: 600; }
/* navigation : l'item actif doit se voir sans effort */
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
  border-radius: 8px; padding-top: 5px; padding-bottom: 5px; }
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {
  background: rgba(255,255,255,.07); }
section[data-testid="stSidebar"] li[aria-current="page"] a,
section[data-testid="stSidebar"] a[aria-current="page"] {
  background: rgba(255,255,255,.14); font-weight: 600; }
/* le vert du thème est illisible sur le vert du volet : on éclaircit le curseur */
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
  background: #FFCE00 !important; border-color: #FFCE00 !important; }
section[data-testid="stSidebar"] [data-baseweb="slider"] div[data-testid="stTickBar"] {
  color: #A9D3BC !important; }
div[data-testid="stExpander"] { border: 1px solid #E4E9EF; border-radius: 12px; background: #fff; }
div[data-testid="stExpander"] summary { font-size: 13.5px; font-weight: 600; }
div[data-testid="stTabs"] button { font-size: 14px; font-weight: 600; }
hr { margin: 1.2rem 0; border-color: #E4E9EF; }
.stSlider [data-baseweb="slider"] { padding-top: 4px; }
</style>""", unsafe_allow_html=True)


# ------------------------------------------------------------------ composants
def tricolore(op=".6"):
    a, b, c = DRAPEAU
    return (f'<div style="height:3px;border-radius:2px;margin:14px 0 6px;opacity:{op};'
            f'background:linear-gradient(to right,{a} 0 33%,{b} 33% 66%,{c} 66% 100%)"></div>')


def hero(eyebrow, titre, lede):
    """En-tête de page : objectif traité, conclusion en titre, précision en dessous."""
    st.markdown(
        f'<div style="font-size:11px;font-weight:700;letter-spacing:1.4px;'
        f'text-transform:uppercase;color:{C["energie"]}">{eyebrow}</div>'
        f'<div style="font-size:29px;font-weight:800;color:{C["foret_d"]};'
        f'line-height:1.2;margin-top:6px">{titre}</div>'
        f'<div style="font-size:15.5px;color:{C["ink_soft"]};margin-top:8px;'
        f'max-width:860px;line-height:1.55">{lede}</div>'
        + tricolore(), unsafe_allow_html=True)


def section(titre, sous=None):
    st.markdown(
        f'<div style="margin:26px 0 10px"><div style="font-size:19px;font-weight:700;'
        f'color:{C["foret_d"]}">{titre}</div>'
        + (f'<div style="font-size:13.5px;color:{C["muted"]};margin-top:3px">{sous}</div>'
           if sous else '') + '</div>', unsafe_allow_html=True)


def kpi(label, valeur, sous="", couleur=None, note=None):
    """Carte chiffre-clé : liseré coloré = famille sémantique, note = tendance."""
    col = couleur or C["foret"]
    n = len(str(valeur))
    taille = 30 if n <= 7 else (24 if n <= 11 else 19)
    note_html = (f'<span style="font-size:11px;font-weight:700;color:{col};'
                 f'background:{col}1A;border-radius:20px;padding:2px 8px;'
                 f'margin-left:7px;white-space:nowrap">{note}</span>') if note else ""
    return (f'<div style="background:#fff;border:1px solid {C["line"]};border-left:4px solid {col};'
            f'border-radius:10px;padding:14px 16px;height:100%;'
            f'box-shadow:0 1px 2px rgba(21,34,56,.05)">'
            f'<div style="font-size:10.5px;text-transform:uppercase;letter-spacing:.7px;'
            f'color:{C["muted"]};font-weight:700">{label}</div>'
            f'<div style="margin-top:7px;display:flex;align-items:baseline;flex-wrap:wrap">'
            f'<span style="font-size:{taille}px;font-weight:800;color:{col};'
            f'font-variant-numeric:tabular-nums;line-height:1.1">{valeur}</span>{note_html}</div>'
            f'<div style="font-size:11.8px;color:{C["muted"]};margin-top:6px;'
            f'line-height:1.4">{sous}</div></div>')


def kpi_row(cartes):
    cols = st.columns(len(cartes))
    for col, args in zip(cols, cartes):
        with col:
            st.markdown(kpi(*args), unsafe_allow_html=True)


_ENCARTS = {
    "constat": (C["foret"],   C["foret_l"],   "Constat"),
    "alerte":  (C["risque"],  C["risque_l"],  "Alerte"),
    "action":  (C["energie"], C["energie_l"], "Ce qu'il faut en faire"),
    "methode": (C["urbain"],  C["urbain_l"],  "Méthode"),
}


def encart(kind, texte, titre=None):
    col, bg, defaut = _ENCARTS[kind]
    st.markdown(
        f'<div style="background:{bg};border-left:4px solid {col};border-radius:0 10px 10px 0;'
        f'padding:13px 17px;margin:6px 0 2px">'
        f'<div style="font-size:10.5px;font-weight:800;letter-spacing:1px;'
        f'text-transform:uppercase;color:{col};margin-bottom:5px">{titre or defaut}</div>'
        f'<div style="font-size:14px;color:{C["ink"]};line-height:1.6">{texte}</div></div>',
        unsafe_allow_html=True)


def puce(couleur, texte):
    return (f'<span style="display:inline-flex;align-items:center;gap:6px;margin-right:16px;'
            f'font-size:11.5px;color:{C["muted"]}">'
            f'<span style="width:10px;height:10px;border-radius:3px;'
            f'background:{couleur};display:inline-block"></span>{texte}</span>')


def legende(*items):
    st.markdown('<div style="margin-top:-6px">' + "".join(puce(c, t) for c, t in items)
                + '</div>', unsafe_allow_html=True)


def pied():
    st.markdown(tricolore(".45"), unsafe_allow_html=True)
    st.caption(SOURCES)


# --------------------------------------------------------------------- plotly
def style_fig(fig, titre=None, hauteur=None, legende_h=True, marge_g=10):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=13, color=C["ink_soft"]),
        title=(dict(text=titre, font=dict(size=15.5, color=C["foret_d"], family=FONT),
                    x=0, xanchor="left", y=.97, yanchor="top") if titre else None),
        margin=dict(l=marge_g, r=14, t=54 if titre else 18, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=hauteur,
        hoverlabel=dict(font=dict(family=FONT, size=12.5), bgcolor="white",
                        bordercolor=C["line"]),
        legend=(dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                     font=dict(size=12), bgcolor="rgba(0,0,0,0)")
                if legende_h else dict(font=dict(size=12))),
    )
    fig.update_xaxes(gridcolor=C["line"], zeroline=False, linecolor=C["line"],
                     title_font=dict(size=12, color=C["muted"]), tickfont=dict(size=11.5))
    fig.update_yaxes(gridcolor=C["line"], zeroline=False, linecolor=C["line"],
                     title_font=dict(size=12, color=C["muted"]), tickfont=dict(size=11.5))
    return fig


def annote(fig, x, y, texte, couleur, ax=0, ay=-34, fleche=True):
    """Annotation directe sur le graphe : un décideur lit le graphe, pas la légende."""
    fig.add_annotation(x=x, y=y, text=texte, showarrow=fleche, arrowhead=0, arrowwidth=1.3,
                       arrowcolor=couleur, ax=ax, ay=ay,
                       font=dict(size=12, color=couleur, family=FONT),
                       bgcolor="rgba(255,255,255,.88)", borderpad=4)
    return fig


def barres_donnees(lignes, entetes, score_max=100, couleur=None):
    """Tableau HTML avec barres de données : classement lisible d'un coup d'œil."""
    col = couleur or C["foret"]
    score_max = score_max if score_max else 1
    head = "".join(
        f'<th style="text-align:{"right" if i == 0 else "left"};padding:9px 12px;'
        f'color:#EAF4EE;font-weight:600;font-size:11.5px;text-transform:uppercase;'
        f'letter-spacing:.5px">{h}</th>' for i, h in enumerate(entetes))
    corps = ""
    for i, (cellules, score, badge) in enumerate(lignes):
        bg = "#F6FAF7" if i % 2 else "#fff"
        tds = "".join(
            f'<td style="padding:8px 12px;font-size:12.8px;color:{C["ink"]};'
            f'text-align:{"right" if j == 0 else "left"};'
            f'font-variant-numeric:tabular-nums;'
            f'{"font-weight:700" if j == 1 else ""}">{v}</td>'
            for j, v in enumerate(cellules))
        if badge:
            tds = tds[:-5] + (
                f'<span style="font-size:9.5px;color:{C["neutre"]};border:1px solid '
                f'{C["neutre"]};border-radius:8px;padding:0 5px;margin-left:6px;'
                f'white-space:nowrap">{badge}</span></td>')
        pct = max(0, min(100, 100 * score / score_max))
        tds += (f'<td style="padding:8px 12px;min-width:140px">'
                f'<div style="display:flex;align-items:center;gap:9px">'
                f'<div style="flex:1;height:14px;background:{C["neutre_l"]};border-radius:3px;'
                f'overflow:hidden"><div style="width:{pct:.0f}%;height:100%;background:{col}">'
                f'</div></div><span style="font-variant-numeric:tabular-nums;font-size:12.3px;'
                f'font-weight:600;min-width:32px;text-align:right">{score:.0f}</span>'
                f'</div></td>')
        corps += f'<tr style="background:{bg};border-top:1px solid {C["line"]}">{tds}</tr>'
    return (f'<div style="overflow:auto;border:1px solid {C["line"]};border-radius:10px">'
            f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr style="background:{C["foret_d"]}">{head}'
            f'<th style="text-align:left;padding:9px 12px;color:#EAF4EE;font-weight:600;'
            f'font-size:11.5px;text-transform:uppercase;letter-spacing:.5px">Score</th></tr>'
            f'</thead><tbody>{corps}</tbody></table></div>')


def fr(x, dec=0):
    """Nombre au format français : 3 720 000 plutôt que 3,720,000."""
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")

"""
Système visuel du tableau de bord — Défi Énergie / Climat / Forêts (Togo).

Parti pris : un tableau de bord de décision, pas un document.
- bandeaux haut et bas en vert nuit, contenu sur canvas clair : le regard
  est cadré, l'identité institutionnelle est portée par les armoiries ;
- palette dérivée du drapeau togolais (vert, or, rouge), une couleur =
  une signification, appliquée partout sans exception ;
- tuiles de chiffres avec courbe de tendance intégrée : un décideur voit
  le niveau ET le mouvement d'un seul regard ;
- chaque graphique vit dans une carte titrée, jamais nu sur la page.

Aucune couleur en dur ailleurs que dans ce fichier.
"""
import base64
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent / "assets"
ARMOIRIES = ASSETS / "armoiries_togo.svg"


@st.cache_data(show_spinner=False)
def armoiries_uri():
    """Armoiries du Togo en data-URI : aucun fichier à servir, aucun appel réseau."""
    return ("data:image/svg+xml;base64,"
            + base64.b64encode(ARMOIRIES.read_bytes()).decode("ascii"))


# ============================================================== palette
C = {
    # chrome — bandeaux et navigation
    "nuit":      "#072A20",
    "nuit_2":    "#0C3A2B",
    "nuit_3":    "#12503A",
    "sur_nuit":  "#E8F3EC",
    "sur_nuit_2": "#9FCBB2",

    # canvas et surfaces
    "canvas":    "#EDF1EF",
    "surface":   "#FFFFFF",
    "sunk":      "#F4F7F5",
    "bord":      "#D9E2DC",

    # familles sémantiques — une couleur, une signification
    "foret":     "#0F7A4A",   # forêt · propre · solution
    "foret_l":   "#DCEFE4",
    "foret_d":   "#0A5533",
    "energie":   "#D9930A",   # énergie · électricité
    "energie_l": "#FBEBCB",
    "energie_d": "#9A6704",
    "risque":    "#C2261C",   # biomasse · risque · émissions
    "risque_l":  "#FADEDB",
    "risque_d":  "#8E1A12",
    "urbain":    "#14707E",   # urbain · contexte
    "urbain_l":  "#D6EBEF",
    "charbon":   "#8A4B2A",   # charbon de bois
    "neutre":    "#8B9AA3",   # incertain · absent
    "neutre_l":  "#EBEFED",

    # texte
    "encre":     "#0D1B16",
    "encre_2":   "#35463E",
    "sourdine":  "#61736A",
}
# rampe séquentielle « pression » — lisible aussi en niveaux de gris
RAMPE = ["#DCEFE4", "#A8D8BF", "#6CBE93", "#2E9B65", "#0F7A4A", "#0A5533"]
# rampe froid -> chaud pour les températures
RAMPE_T = ["#14707E", "#4E9AA2", "#C9A65A", "#D9930A", "#C2261C"]
DRAPEAU = ("#006A4E", "#FFCE00", "#D21034")

FONT = "Inter, 'Segoe UI', system-ui, sans-serif"
MOIS = ["Janv", "Févr", "Mars", "Avr", "Mai", "Juin",
        "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]

SOURCES = ("6 jeux de données du Défi · datalab.gouv.tg — indicateurs Banque Mondiale, "
           "inventaire GES 2018, stations météo 2013-2019, forêts classées. "
           "Seul apport externe : les coordonnées des 10 stations.")


# ================================================================== CSS
def inject_css():
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"], .stMarkdown {{ font-family:{FONT}; }}
#MainMenu, footer, header [data-testid="stStatusWidget"] {{ visibility:hidden; }}
[data-testid="stHeader"] {{ background:transparent; height:0; }}

.stApp {{ background:{C['canvas']}; }}
.block-container {{ padding-top:1.1rem; padding-bottom:1.2rem; max-width:1340px; }}

/* ---- cartes : tout graphique vit dans un conteneur titré ----
   Deux chemins : les conteneurs bordés explicites, et toute colonne qui
   contient un en-tête de carte (:has). Si un navigateur ancien ignore
   :has, la page reste lisible — elle perd seulement le fond blanc. */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stColumn"]:has(> div > div > .carte-tete),
div[data-testid="stColumn"]:has(.carte-tete) {{
  background:{C['surface']}; border:1px solid {C['bord']} !important;
  border-radius:12px;
  box-shadow:0 1px 2px rgba(7,42,32,.05), 0 4px 14px -8px rgba(7,42,32,.10);
  overflow:hidden;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{ padding:2px 4px; }}
div[data-testid="stColumn"]:has(.carte-tete) {{ padding:0 12px 10px; }}
/* une colonne-carte ne doit pas contenir une tuile KPI (double bordure) */
div[data-testid="stColumn"]:has(.tuile-kpi) {{
  background:transparent; border:none !important; box-shadow:none;
  padding:0; overflow:visible;
}}

/* ---- volet latéral ---- */
section[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,{C['nuit']} 0%,{C['nuit_2']} 100%);
  border-right:1px solid rgba(255,255,255,.08);
}}
section[data-testid="stSidebar"] * {{ color:{C['sur_nuit']} !important; }}
section[data-testid="stSidebar"] .stSlider label {{ font-size:12.5px; font-weight:600; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{
  border-radius:8px; padding-top:6px; padding-bottom:6px; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{
  background:rgba(255,255,255,.08); }}
section[data-testid="stSidebar"] li[aria-current="page"] a,
section[data-testid="stSidebar"] a[aria-current="page"] {{
  background:rgba(255,206,0,.16); font-weight:600;
  box-shadow:inset 3px 0 0 {DRAPEAU[1]}; }}
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
  background:{DRAPEAU[1]} !important; border-color:{DRAPEAU[1]} !important; }}

/* ---- contrôles : lisibles, compacts, jamais bavards ---- */
div[data-testid="stExpander"] {{
  border:1px solid {C['bord']}; border-radius:12px; background:{C['surface']}; }}
div[data-testid="stExpander"] summary {{ font-size:13.5px; font-weight:600; }}
div[data-testid="stTabs"] {{ margin-top:2px; }}
div[data-testid="stTabs"] button {{ font-size:14px; font-weight:600;
  color:{C['sourdine']}; }}
div[data-testid="stTabs"] button[aria-selected="true"] {{ color:{C['foret_d']}; }}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background:{C['foret']}; }}
.stSlider [data-baseweb="slider"] {{ padding-top:4px; }}
label[data-testid="stWidgetLabel"] p {{ font-size:12.5px; font-weight:600;
  color:{C['encre_2']}; }}
hr {{ margin:.9rem 0; border-color:{C['bord']}; }}
</style>""", unsafe_allow_html=True)


# =========================================================== composants
def _filet(op=".75", h=3):
    a, b, c = DRAPEAU
    return (f'<div style="height:{h}px;border-radius:2px;opacity:{op};'
            f'background:linear-gradient(to right,{a} 0 33.3%,{b} 33.3% 66.6%,'
            f'{c} 66.6% 100%)"></div>')


def tricolore(op=".75"):
    return f'<div style="margin:12px 0 6px">{_filet(op)}</div>'


def banniere(objectif, titre, accroche, reperes=None):
    """Bandeau de tête : armoiries, objectif traité, conclusion en titre.

    `reperes` : liste de (libellé, valeur) affichée à droite — le décideur a
    les ordres de grandeur avant même de lire le corps de la page.
    """
    blocs = ""
    if reperes:
        cellules = "".join(
            f'<div style="padding:0 20px;border-left:1px solid rgba(255,255,255,.16)">'
            f'<div style="font-size:9.5px;font-weight:700;letter-spacing:1.1px;'
            f'text-transform:uppercase;color:{C["sur_nuit_2"]}">{lab}</div>'
            f'<div style="font-size:21px;font-weight:800;color:#fff;margin-top:3px;'
            f'font-variant-numeric:tabular-nums;line-height:1.1">{val}</div></div>'
            for lab, val in reperes)
        blocs = (f'<div style="display:flex;align-items:center;flex-wrap:wrap;'
                 f'gap:10px 0;margin-left:auto">{cellules}</div>')

    st.markdown(
        f'<div style="background:linear-gradient(110deg,{C["nuit"]} 0%,'
        f'{C["nuit_2"]} 58%,{C["nuit_3"]} 100%);border-radius:14px;'
        f'padding:20px 26px 0;margin-bottom:16px;overflow:hidden;'
        f'box-shadow:0 6px 22px -12px rgba(7,42,32,.55)">'
        f'<div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">'
        f'<img src="{armoiries_uri()}" alt="Armoiries de la République togolaise" '
        f'style="height:62px;width:auto;flex:0 0 auto;'
        f'filter:drop-shadow(0 2px 6px rgba(0,0,0,.35))">'
        f'<div style="flex:1 1 340px;min-width:280px">'
        f'<div style="font-size:10px;font-weight:800;letter-spacing:1.6px;'
        f'text-transform:uppercase;color:{DRAPEAU[1]}">{objectif}</div>'
        f'<div style="font-size:27px;font-weight:800;color:#fff;line-height:1.15;'
        f'margin-top:5px;letter-spacing:-.4px">{titre}</div></div>'
        f'{blocs}</div>'
        f'<div style="font-size:14.5px;color:{C["sur_nuit"]};opacity:.92;'
        f'margin:12px 0 16px;max-width:940px;line-height:1.55">{accroche}</div>'
        f'{_filet(".9", 4)}</div>', unsafe_allow_html=True)


def section(titre, sous=None):
    st.markdown(
        f'<div style="margin:22px 0 9px">'
        f'<div style="font-size:18px;font-weight:800;color:{C["encre"]};'
        f'letter-spacing:-.2px">{titre}</div>'
        + (f'<div style="font-size:13px;color:{C["sourdine"]};margin-top:2px;'
           f'line-height:1.5">{sous}</div>' if sous else '') + '</div>',
        unsafe_allow_html=True)


def titre_carte(titre, sous=None, couleur=None):
    """En-tête interne d'une carte — à appeler dans un st.container(border=True)."""
    col = couleur or C["foret"]
    st.markdown(
        f'<div class="carte-tete" style="padding:12px 14px 9px;'
        f'border-bottom:1px solid {C["bord"]};margin:-2px -16px 10px;'
        f'padding-left:16px;padding-right:16px">'
        f'<div style="display:flex;align-items:center;gap:9px">'
        f'<span style="width:3px;height:15px;border-radius:2px;background:{col}">'
        f'</span><span style="font-size:14.5px;font-weight:700;color:{C["encre"]}">'
        f'{titre}</span></div>'
        + (f'<div style="font-size:12px;color:{C["sourdine"]};margin-top:4px;'
           f'padding-left:12px;line-height:1.45">{sous}</div>' if sous else '')
        + '</div>', unsafe_allow_html=True)


# ------------------------------------------------------------ sparkline
def sparkline(valeurs, couleur, largeur=132, hauteur=30):
    """Micro-courbe SVG : le mouvement, pas seulement le niveau."""
    v = [x for x in valeurs if x is not None]
    if len(v) < 2:
        return ""
    lo, hi = min(v), max(v)
    etendue = (hi - lo) or 1
    pas = largeur / (len(v) - 1)
    pts = [(i * pas, hauteur - 3 - (x - lo) / etendue * (hauteur - 7))
           for i, x in enumerate(v)]
    ligne = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    aire = f"0,{hauteur} {ligne} {largeur},{hauteur}"
    fx, fy = pts[-1]
    return (f'<svg viewBox="0 0 {largeur} {hauteur}" width="100%" height="{hauteur}" '
            f'preserveAspectRatio="none" style="display:block;margin-top:9px">'
            f'<polygon points="{aire}" fill="{couleur}" opacity=".13"/>'
            f'<polyline points="{ligne}" fill="none" stroke="{couleur}" '
            f'stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="2.9" fill="{couleur}" '
            f'stroke="#fff" stroke-width="1.4"/></svg>')


def kpi(label, valeur, sous="", couleur=None, note=None, serie=None):
    """Tuile de chiffre-clé : niveau, variation, tendance, en une lecture."""
    col = couleur or C["foret"]
    n = len(str(valeur))
    taille = 33 if n <= 7 else (26 if n <= 11 else 20)
    note_html = (f'<span style="font-size:11px;font-weight:800;color:{col};'
                 f'background:{col}1C;border-radius:20px;padding:3px 9px;'
                 f'margin-left:8px;white-space:nowrap">{note}</span>') if note else ""
    spark = sparkline(serie, col) if serie else ""
    return (f'<div class="tuile-kpi" style="background:{C["surface"]};'
            f'border:1px solid {C["bord"]};'
            f'border-top:3px solid {col};border-radius:4px 4px 12px 12px;'
            f'padding:13px 15px 12px;height:100%;display:flex;flex-direction:column;'
            f'box-shadow:0 1px 2px rgba(7,42,32,.05)">'
            f'<div style="font-size:10px;text-transform:uppercase;letter-spacing:.8px;'
            f'color:{C["sourdine"]};font-weight:800;line-height:1.35">{label}</div>'
            f'<div style="margin-top:8px;display:flex;align-items:baseline;'
            f'flex-wrap:wrap">'
            f'<span style="font-size:{taille}px;font-weight:900;color:{col};'
            f'font-variant-numeric:tabular-nums;line-height:1;letter-spacing:-.9px">'
            f'{valeur}</span>{note_html}</div>'
            f'<div style="font-size:11.6px;color:{C["sourdine"]};margin-top:7px;'
            f'line-height:1.45;flex:1">{sous}</div>{spark}</div>')


def kpi_row(cartes):
    cols = st.columns(len(cartes), gap="small")
    for col, args in zip(cols, cartes):
        with col:
            st.markdown(kpi(*args), unsafe_allow_html=True)


# -------------------------------------------------------------- encarts
_ENCARTS = {
    "constat": (C["foret"],   C["foret_l"],   "Constat"),
    "alerte":  (C["risque"],  C["risque_l"],  "Alerte"),
    "action":  (C["energie"], C["energie_l"], "Décision"),
    "methode": (C["urbain"],  C["urbain_l"],  "Méthode"),
}


def encart(kind, texte, titre=None):
    col, bg, defaut = _ENCARTS[kind]
    st.markdown(
        f'<div style="background:{bg};border-left:4px solid {col};'
        f'border-radius:0 10px 10px 0;padding:13px 18px;margin:10px 0 4px">'
        f'<div style="font-size:10px;font-weight:900;letter-spacing:1.2px;'
        f'text-transform:uppercase;color:{col};margin-bottom:5px">'
        f'{titre or defaut}</div>'
        f'<div style="font-size:13.8px;color:{C["encre"]};line-height:1.62">'
        f'{texte}</div></div>', unsafe_allow_html=True)


def legende(*items):
    puces = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'margin-right:18px;font-size:11.5px;color:{C["sourdine"]}">'
        f'<span style="width:10px;height:10px;border-radius:3px;background:{c};'
        f'display:inline-block"></span>{t}</span>' for c, t in items)
    st.markdown(f'<div style="margin-top:-4px;padding:0 4px 6px">{puces}</div>',
                unsafe_allow_html=True)


# ----------------------------------------------------------- pied de page
def pied(page=None):
    """Bandeau de pied : armoiries, sources, reproductibilité."""
    st.markdown(
        f'<div style="background:linear-gradient(110deg,{C["nuit"]} 0%,'
        f'{C["nuit_2"]} 100%);border-radius:14px;padding:0 24px 18px;'
        f'margin-top:30px;overflow:hidden">{_filet(".9", 4)}'
        f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;'
        f'padding-top:16px">'
        f'<img src="{armoiries_uri()}" alt="Armoiries de la République togolaise" '
        f'style="height:44px;width:auto;flex:0 0 auto;opacity:.95">'
        f'<div style="flex:1 1 420px;min-width:260px">'
        f'<div style="font-size:12.5px;font-weight:700;color:#fff">'
        f'République togolaise · Défi Énergie, Climat &amp; Forêts</div>'
        f'<div style="font-size:11px;color:{C["sur_nuit_2"]};margin-top:4px;'
        f'line-height:1.5">{SOURCES}</div></div>'
        f'<div style="font-size:10.5px;color:{C["sur_nuit_2"]};text-align:right;'
        f'line-height:1.6;margin-left:auto">'
        f'Chiffres recalculés depuis les sources<br>'
        f'<code style="background:transparent;color:{DRAPEAU[1]};padding:0">'
        f'python src/verify.py</code> · 42/42 conformes</div>'
        f'</div></div>', unsafe_allow_html=True)


# ================================================================ plotly
def style_fig(fig, titre=None, hauteur=None, legende_h=True, marge_g=8):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=12.5, color=C["encre_2"]),
        title=(dict(text=titre, font=dict(size=14.5, color=C["encre"], family=FONT),
                    x=0, xanchor="left", y=.98, yanchor="top") if titre else None),
        margin=dict(l=marge_g, r=14, t=48 if titre else 14, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=hauteur,
        hoverlabel=dict(font=dict(family=FONT, size=12.5), bgcolor="white",
                        bordercolor=C["bord"]),
        legend=(dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                     font=dict(size=11.5), bgcolor="rgba(0,0,0,0)")
                if legende_h else dict(font=dict(size=11.5))),
    )
    fig.update_xaxes(gridcolor=C["bord"], zeroline=False, linecolor=C["bord"],
                     title_font=dict(size=11.5, color=C["sourdine"]),
                     tickfont=dict(size=11))
    fig.update_yaxes(gridcolor=C["bord"], zeroline=False, linecolor=C["bord"],
                     title_font=dict(size=11.5, color=C["sourdine"]),
                     tickfont=dict(size=11))
    return fig


def annote(fig, x, y, texte, couleur, ax=0, ay=-34, fleche=True):
    """Annotation directe : un décideur lit le graphe, pas la légende."""
    fig.add_annotation(x=x, y=y, text=texte, showarrow=fleche, arrowhead=0,
                       arrowwidth=1.3, arrowcolor=couleur, ax=ax, ay=ay,
                       font=dict(size=11.5, color=couleur, family=FONT),
                       bgcolor="rgba(255,255,255,.9)", borderpad=4)
    return fig


# ---------------------------------------------------------- tableau barres
def barres_donnees(lignes, entetes, score_max=100, couleur=None):
    """Classement à barres de données — lecture d'un coup d'œil."""
    col = couleur or C["foret"]
    score_max = score_max if score_max else 1
    head = "".join(
        f'<th style="text-align:{"right" if i == 0 else "left"};padding:9px 12px;'
        f'color:{C["sur_nuit"]};font-weight:700;font-size:10.5px;'
        f'text-transform:uppercase;letter-spacing:.7px">{h}</th>'
        for i, h in enumerate(entetes))
    fort = f'font-weight:700;color:{C["encre"]}'   # 2e colonne = le nom, mis en avant
    corps = ""
    for i, (cellules, score, badge) in enumerate(lignes):
        bg = C["sunk"] if i % 2 else C["surface"]
        tds = "".join(
            f'<td style="padding:8px 12px;font-size:12.6px;color:{C["encre_2"]};'
            f'text-align:{"right" if j == 0 else "left"};'
            f'font-variant-numeric:tabular-nums;{fort if j == 1 else ""}">'
            f'{v}</td>' for j, v in enumerate(cellules))
        if badge:
            tds = tds[:-5] + (
                f'<span style="font-size:9.5px;color:{C["neutre"]};border:1px solid '
                f'{C["neutre"]};border-radius:8px;padding:0 5px;margin-left:6px;'
                f'white-space:nowrap">{badge}</span></td>')
        pct = max(0, min(100, 100 * score / score_max))
        tds += (f'<td style="padding:8px 12px;min-width:132px">'
                f'<div style="display:flex;align-items:center;gap:9px">'
                f'<div style="flex:1;height:13px;background:{C["neutre_l"]};'
                f'border-radius:3px;overflow:hidden">'
                f'<div style="width:{pct:.0f}%;height:100%;background:{col};'
                f'border-radius:3px"></div></div>'
                f'<span style="font-variant-numeric:tabular-nums;font-size:12.2px;'
                f'font-weight:700;min-width:30px;text-align:right;color:{col}">'
                f'{score:.0f}</span></div></td>')
        corps += f'<tr style="background:{bg};border-top:1px solid {C["bord"]}">{tds}</tr>'
    return (f'<div style="overflow:auto;border:1px solid {C["bord"]};'
            f'border-radius:10px">'
            f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr style="background:{C["nuit_2"]}">{head}'
            f'<th style="text-align:left;padding:9px 12px;color:{C["sur_nuit"]};'
            f'font-weight:700;font-size:10.5px;text-transform:uppercase;'
            f'letter-spacing:.7px">Indice</th></tr></thead>'
            f'<tbody>{corps}</tbody></table></div>')


def fr(x, dec=0):
    """Nombre au format français : 3 720 000 plutôt que 3,720,000."""
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")

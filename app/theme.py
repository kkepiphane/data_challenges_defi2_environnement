"""
Système visuel du tableau de bord — Énergie, Climat & Forêts au Togo.

Registre visuel : le **bulletin statistique institutionnel**, pas le produit
logiciel. Ce que cela implique, concrètement :

- **aucun rail de couleur** en bordure de bloc — ni liseré à gauche des
  encarts, ni bandeau au-dessus des tuiles : la couleur vit dans le chiffre,
  la courbe et le mot, jamais dans une décoration ;
- des filets d'un pixel et des à-plats francs, aucun dégradé ;
- des angles arrondis mesurés (10 px), ni carrés ni bulles ;
- une seule famille typographique (Inter) : la hiérarchie se fait à la
  graisse et au corps, pas au changement de police ;
- la couleur reste sémantique : une teinte, une signification, partout —
  et le vert, qui dit « forêt · propre · solution », ne se pose jamais
  sur un mauvais chiffre : dans une tuile, il annonce une bonne
  nouvelle, pas un domaine.

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


@st.cache_data(show_spinner=False)
def logo_menu():
    """Armoiries et intitulé réunis en un seul SVG, rendu en tête de menu.

    Streamlit place la navigation au-dessus du contenu de la barre latérale :
    seul `st.logo` se rend au-dessus des liens, et il n'accepte qu'une image.
    L'intitulé est donc composé dans le SVG. Le texte est dimensionné pour
    rester lisible même si le conteneur réduit l'image.
    """
    brut = ARMOIRIES.read_text(encoding="utf-8")
    interieur = brut[brut.index(">", brut.index("<svg")) + 1: brut.rindex("</svg>")]
    ech = 54 / 1080
    larg = 750 * ech
    x = larg + 10
    pol = "Inter,'Segoe UI',system-ui,sans-serif"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 236 56" '
        f'width="236" height="56" role="img" '
        f'aria-label="Énergie, Climat et Forêts au Togo">'
        f'<g transform="translate(0,1) scale({ech:.6f})">{interieur}</g>'
        f'<text x="{x:.1f}" y="21" font-family="{pol}" font-size="16.5" '
        f'font-weight="700" fill="#FFFFFF">Énergie, Climat</text>'
        f'<text x="{x:.1f}" y="39" font-family="{pol}" font-size="16.5" '
        f'font-weight="700" fill="#FFFFFF">&amp; Forêts au Togo</text>'
        f'<text x="{x:.1f}" y="52" font-family="{pol}" font-size="11" '
        f'fill="#93BFA6">datalab.gouv.tg</text></svg>')




# ============================================================== palette
# Les couleurs vivent dans `palette.py`, que le rapport et le PowerPoint
# lisent aussi : une teinte se change à un seul endroit, pour les trois
# livrables à la fois. On les ré-exporte ici pour que les vues continuent de
# n'importer que `theme`.
from palette import (C, RAMPE, RAMPE_T, DRAPEAU, FONT, rgba)   # noqa: E402,F401
# Les titres et les chiffres partagent la même famille : c'est la graisse et
# le corps qui font la hiérarchie, pas un changement de police.
FONT_T = FONT
MOIS = ["Janv", "Févr", "Mars", "Avr", "Mai", "Juin",
        "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]

SOURCES = ("Six jeux de données du défi, datalab.gouv.tg — indicateurs Banque Mondiale, "
           "inventaire national des GES 2018, relevés de dix stations météorologiques "
           "2013-2019, zones protégées et forêts classées. Seul apport externe : "
           "les coordonnées des dix stations.")


# ================================================================== CSS
def inject_css():
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"], .stMarkdown {{ font-family:{FONT}; }}
#MainMenu, footer, header [data-testid="stStatusWidget"] {{ visibility:hidden; }}
[data-testid="stHeader"] {{ background:transparent; height:0; }}

.stApp {{ background:{C['canvas']}; }}
.block-container {{ padding-top:1.05rem; padding-bottom:1.2rem; max-width:1340px; }}

/* ---- surfaces : filet d'un pixel, angle net, aucune ombre ---- */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stColumn"]:has(.carte-tete) {{
  background:{C['surface']}; border:1px solid {C['bord']} !important;
  border-radius:10px; box-shadow:0 1px 2px rgba(12,26,20,.04); overflow:hidden;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{ padding:2px 4px; }}
div[data-testid="stColumn"]:has(.carte-tete) {{ padding:0 14px 12px; }}
div[data-testid="stColumn"]:has(.tuile-kpi) {{
  background:transparent; border:none !important; padding:0; overflow:visible;
}}
/* Une tuile isolée dans une colonne doit tout de même remplir sa hauteur :
   la chaîne de conteneurs de Streamlit doit donc la transmettre. */
div[data-testid="stColumn"]:has(.tuile-kpi) [data-testid="stVerticalBlock"],
div[data-testid="stColumn"]:has(.tuile-kpi) [data-testid="stElementContainer"],
div[data-testid="stColumn"]:has(.tuile-kpi) [data-testid="stMarkdown"],
div[data-testid="stColumn"]:has(.tuile-kpi) [data-testid="stMarkdownContainer"] {{
  height:100%; }}

/* ---- cartes de relais : hauteur commune, jamais figée ----
   Elles restent dans des colonnes (chacune porte son lien de page) : c'est
   donc la colonne qui transmet la hauteur, et la carte qui la remplit. */
div[data-testid="stColumn"]:has(.carte-relais),
div[data-testid="stColumn"]:has(.carte-relais) [data-testid="stVerticalBlock"] {{
  height:100%; }}
div[data-testid="stColumn"]:has(.carte-relais)
  [data-testid="stElementContainer"]:has(.carte-relais) {{ flex:1 0 auto; }}
.carte-relais {{ height:100%; box-sizing:border-box; }}

/* ---- rangée de chiffres-clés ----------------------------------------
   Toute la rangée est UNE grille : chaque tuile occupe les mêmes bandes
   (intitulé · nombre · contexte · courbe) grâce à `subgrid`. Les zones
   s'alignent donc d'une tuile à l'autre sans qu'aucune hauteur soit figée —
   un texte plus long pousse la bande pour toute la rangée au lieu de
   déborder sur la zone suivante. C'est ce qui rend le débordement
   structurellement impossible. */
.rangee-kpi {{ display:grid; column-gap:12px; row-gap:0;
  align-items:stretch; margin:2px 0; }}
.tuile-kpi {{ background:{C['surface']}; border:1px solid {C['bord']};
  border-radius:10px; padding:15px 17px; height:100%;
  display:flex; flex-direction:column; }}
.rangee-kpi > .tuile-kpi {{ display:grid; grid-template-rows:subgrid;
  height:auto; }}
@supports not (grid-template-rows:subgrid) {{
  .rangee-kpi > .tuile-kpi {{ display:flex; flex-direction:column; }}
}}
/* L'intitulé annonce le sujet, le nombre répond, le contexte qualifie :
   la tuile se lit d'un trait, « accès rural à l'électricité · 25 % · contre
   96 % en ville ». Aucun filet ne coupe cette phrase. */
.kpi-intitule {{ font-size:11px; font-weight:700; letter-spacing:.55px;
  text-transform:uppercase; color:{C['encre']}; line-height:1.35;
  overflow-wrap:break-word; hyphens:auto; }}
.kpi-chiffre {{ display:flex; align-items:baseline; flex-wrap:wrap;
  row-gap:5px; margin-top:9px; }}
.kpi-nombre {{ font-weight:800; line-height:1; letter-spacing:-.9px;
  white-space:nowrap; font-variant-numeric:tabular-nums; }}
.kpi-pastille {{ font-size:10.5px; font-weight:600; color:{C['sourdine']};
  border:1px solid {C['bord_fort']}; border-radius:3px; padding:2px 7px;
  margin-left:auto; padding-left:7px; align-self:center;
  white-space:nowrap; }}
.kpi-contexte {{ font-size:11.8px; color:{C['sourdine']}; line-height:1.5;
  margin-top:9px; flex:1; overflow-wrap:break-word; hyphens:auto; }}
.kpi-courbe {{ margin-top:10px; min-height:39px; align-self:end;
  width:100%; }}
/* Écran étroit : la grille devient une file qui se replie. L'alignement
   des bandes cède, l'égalité des hauteurs par ligne demeure. */
@media (max-width:1000px) {{
  .rangee-kpi {{ display:flex; flex-wrap:wrap; gap:10px; }}
  .rangee-kpi > .tuile-kpi {{ display:flex; flex-direction:column;
    flex:1 1 210px; height:auto; }}
}}

/* ---- volet latéral : à-plat, pas de dégradé ---- */
section[data-testid="stSidebar"] {{ background:{C['nuit']}; border-right:none; }}
section[data-testid="stSidebar"] * {{ color:{C['sur_nuit']} !important; }}
/* `st.logo(size="large")` plafonne la hauteur au jeton twoXL (~28 px), ce qui
   écrase l'intitulé. On laisse donc la largeur commander et on lève le
   plafond : le SVG garde alors son rapport et son texte reste lisible. */
img[data-testid="stSidebarLogo"] {{
  height:auto !important; max-height:none !important;
  width:100% !important; max-width:212px !important;
  margin:18px 0 14px; }}
section[data-testid="stSidebar"] [data-testid="stLogoLink"],
section[data-testid="stSidebar"] a.stLogoLink {{
  display:block !important; width:100% !important; }}
/* Volet replié, Streamlit déplace le logo dans la barre d'outils, sur fond
   clair : son intitulé, blanc, y devient invisible. On l'y masque — le
   chevron de dépliage suffit à revenir au menu. Streamlit distingue les deux
   emplacements par leur identifiant : `stSidebarLogo` et `stHeaderLogo`. */
img[data-testid="stHeaderLogo"] {{ display:none !important; }}
/* L'en-tête du volet monte au ras de la fenêtre dès que la barre supérieure
   est masquée : on lui rend une respiration, l'emblème ne doit pas toucher
   le bord de l'écran. */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
  padding-top:10px; padding-bottom:4px; }}
/* Le point d'interrogation d'aide est tracé par Streamlit en bleu nuit
   opaque à 60 % — invisible sur l'à-plat vert. Il est dessiné au trait, donc
   c'est `stroke` qu'il faut éclaircir, pas `color`. */
section[data-testid="stSidebar"] [data-testid="stTooltipIcon"] svg {{
  stroke:{C['sur_nuit_2']} !important; }}
section[data-testid="stSidebar"] [data-testid="stTooltipIcon"]:hover svg {{
  stroke:{C['sur_nuit']} !important; }}
section[data-testid="stSidebar"] .stSlider label {{ font-size:12.5px; font-weight:600; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{
  border-radius:8px; padding-top:7px; padding-bottom:7px; font-size:14px; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{
  background:rgba(255,255,255,.07); }}
section[data-testid="stSidebar"] li[aria-current="page"] a,
section[data-testid="stSidebar"] a[aria-current="page"] {{
  background:rgba(255,255,255,.11); font-weight:700; }}
section[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
  background:{C['sur_nuit']} !important; border-color:{C['sur_nuit']} !important; }}

/* ---- contrôles ---- */
div[data-testid="stExpander"] {{
  border:1px solid {C['bord']}; border-radius:10px; background:{C['surface']}; }}
div[data-testid="stExpander"] summary {{ font-size:13.5px; font-weight:600; }}
div[data-testid="stTabs"] button {{ font-size:14.5px; font-weight:600;
  color:{C['sourdine']}; }}
div[data-testid="stTabs"] button[aria-selected="true"] {{ color:{C['encre']}; }}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background:{C['encre']}; }}
label[data-testid="stWidgetLabel"] p {{ font-size:12.5px; font-weight:600;
  color:{C['encre_2']}; }}
div[data-testid="stDataFrame"] {{ border-radius:10px; }}
hr {{ margin:.9rem 0; border-color:{C['bord']}; }}
</style>""", unsafe_allow_html=True)


# =========================================================== composants
def banniere(kicker, titre, accroche):
    """Manchette de page : le sujet, la conclusion en titre, l'accroche.

    Un à-plat sombre, rien d'autre. Aucun chiffre n'y monte : les chiffres
    directeurs sont dans les tuiles, juste en dessous, et les répéter dans
    la manchette faisait lire deux fois la même chose avant d'entrer dans
    la page.
    """
    st.markdown(
        f'<div style="background:{C["nuit"]};border-radius:12px;'
        f'padding:21px 26px 22px;margin-bottom:16px">'
        f'<div style="font-size:11px;font-weight:600;letter-spacing:.9px;'
        f'text-transform:uppercase;color:{C["sur_nuit_2"]}">{kicker}</div>'
        f'<div style="font-family:{FONT_T};font-size:28px;font-weight:800;letter-spacing:-.5px;'
        f'color:#fff;line-height:1.14;margin-top:7px;max-width:1000px">{titre}</div>'
        f'<div style="font-size:14px;color:{C["sur_nuit"]};max-width:930px;'
        f'line-height:1.6;margin-top:14px">{accroche}</div></div>',
        unsafe_allow_html=True)


def section(titre, sous=None):
    st.markdown(
        f'<div style="margin:30px 0 12px">'
        f'<div style="font-family:{FONT_T};font-size:19px;font-weight:800;letter-spacing:-.2px;'
        f'color:{C["encre"]};line-height:1.25">{titre}</div>'
        + (f'<div style="font-size:13px;color:{C["sourdine"]};margin-top:5px;'
           f'line-height:1.5">{sous}</div>' if sous else '') + '</div>',
        unsafe_allow_html=True)


def titre_carte(titre, sous=None, couleur=None):
    """En-tête de carte : le mot porte la couleur, rien ne le souligne.

    Aucun filet ne sépare l'en-tête du contenu — c'est le blanc qui groupe.
    """
    col = couleur or C["encre"]
    st.markdown(
        f'<div class="carte-tete" style="padding:13px 16px 0;'
        f'margin:0 -18px 14px">'
        f'<div style="font-size:14.5px;font-weight:700;color:{col};'
        f'line-height:1.3">{titre}</div>'
        + (f'<div style="font-size:12px;color:{C["sourdine"]};margin-top:4px;'
           f'line-height:1.45">{sous}</div>' if sous else '')
        + '</div>', unsafe_allow_html=True)


# ------------------------------------------------------------ sparkline
def sparkline(valeurs, couleur, periode=None, largeur=150, hauteur=30):
    """Micro-courbe ancrée : ligne de base, aire légère, bornes datées.

    Une courbe qui flotte sans repère se lit comme du bruit. Celle-ci est
    posée sur une ligne de base et bornée par sa période : elle devient une
    information, pas une décoration.
    """
    v = [x for x in valeurs if x is not None]
    if len(v) < 3:                     # deux points ne font pas une tendance
        return ""
    lo, hi = min(v), max(v)
    etendue = (hi - lo) or 1
    hg = hauteur - 11                  # hauteur du tracé, hors bandeau de dates
    pas = largeur / (len(v) - 1)
    pts = [(i * pas, hg - 2 - (x - lo) / etendue * (hg - 5))
           for i, x in enumerate(v)]
    ligne = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    aire = f"0,{hg} {ligne} {largeur},{hg}"
    fx, fy = pts[-1]
    bornes = ""
    if periode:
        bornes = (f'<text x="0" y="{hauteur - 1}" font-family="{FONT}" '
                  f'font-size="8.5" fill="{C["sourdine"]}">{periode[0]}</text>'
                  f'<text x="{largeur}" y="{hauteur - 1}" font-family="{FONT}" '
                  f'font-size="8.5" fill="{C["sourdine"]}" text-anchor="end">'
                  f'{periode[1]}</text>')
    return (f'<svg viewBox="0 0 {largeur} {hauteur}" width="100%" '
            f'height="{hauteur}" preserveAspectRatio="none" '
            f'style="display:block;overflow:visible">'
            f'<polygon points="{aire}" fill="{couleur}" opacity=".10"/>'
            f'<line x1="0" y1="{hg}" x2="{largeur}" y2="{hg}" '
            f'stroke="{C["bord"]}" stroke-width="1"/>'
            f'<polyline points="{ligne}" fill="none" stroke="{couleur}" '
            f'stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="2.6" fill="{couleur}"/>'
            f'{bornes}</svg>')


_UNITES = ("%", "M", "ha/an", "ha", "km²", "km", "°C", "pts", "pt/an",
           "Gg", "j", "/mois", "forêts", "massifs", "Mt", "k/an")


def _scinde(valeur):
    """Sépare le nombre de son unité, pour les composer à deux corps.

    « 5 011 ha » composé d'un seul corps déséquilibre la ligne, et « 25 % »
    y creuse un trou. Le nombre porte la lecture, l'unité l'accompagne.
    """
    s = str(valeur).strip()
    prefixe = ""
    if s.startswith("×"):
        prefixe, s = "×", s[1:].strip()
    for u in sorted(_UNITES, key=len, reverse=True):
        if s.endswith(" " + u):
            return prefixe, s[: -len(u)].strip(), u
    return prefixe, s, ""


# Corps possibles du nombre, du plus ample au plus contenu.
_CORPS = (34, 30, 25, 21, 18)
# Largeur d'un caractère en fraction du corps (Inter, graisse 800). Un chiffre
# tabulaire vaut .60 em ; l'espace des milliers et la virgule, bien moins.
_EM = {" ": .26, "\u00a0": .26, ",": .30, ".": .30, "/": .30, "-": .40}
# Largeur utile d'une tuile : la zone de contenu par défaut du tableau de bord
# (1340 px), moins les gouttières, la marge intérieure et les filets.
LARGEUR_UTILE, GOUTTIERE = 1340, 12


def _largeur_tuile(n):
    """Largeur intérieure d'une tuile dans une rangée de `n`."""
    return (LARGEUR_UTILE - GOUTTIERE * (n - 1)) / n - 36


def _corps(prefixe, nombre, unite, note=None, largeur=None):
    """Corps du nombre : le plus grand qui laisse la ligne tenir d'un trait.

    La ligne porte le nombre, son unité et parfois une pastille. On mesure ce
    que chacun occupe et on descend d'un palier tant que l'ensemble dépasse la
    largeur de la tuile. C'est ce qui évite qu'un « 5 011 ha/an » flanqué
    d'une pastille ne se replie sur l'intitulé — sans rapetisser les nombres
    courts par précaution.
    """
    largeur = largeur or _largeur_tuile(5)
    pastille = 5.9 * len(note) + 26 if note else 0   # corps fixe : 10,5 px
    for c in _CORPS:
        pris = (c * sum(_EM.get(ch, .60) for ch in nombre)
                + (c * .36 + 4 if prefixe else 0)
                + (c * .24 * len(unite) + 4 if unite else 0))
        if pris + pastille <= largeur:
            return c
    return _CORPS[-1]


def kpi(label, valeur, sous="", couleur=None, note=None, serie=None,
        periode=None, corps=None, bandes=3):
    """Chiffre-clé, composé dans l'ordre où on le dit.

    Anatomie en bandes : l'intitulé annonce le sujet, le nombre répond, le
    contexte qualifie, la courbe situe. On lit « accès rural à l'électricité
    · 25 % · contre 96 % en ville » d'une seule traite, sans avoir à
    remonter d'un fragment à l'autre pour reconstituer la phrase. La
    grandeur reste ce qui saute aux yeux : c'est le corps du nombre et sa
    couleur qui s'en chargent, pas sa place dans la tuile.

    Aucune zone n'a de hauteur imposée : c'est la rangée (`kpi_row`) qui
    aligne les bandes. Une tuile ne peut donc plus déborder sur la suivante,
    quelle que soit la longueur du texte.
    """
    col = couleur or C["encre"]
    prefixe, nombre, unite = _scinde(valeur)
    corps = corps or _corps(prefixe, nombre, unite, note)
    pre_html = (f'<span style="font-size:{corps*.6:.0f}px;font-weight:700;'
                f'color:{col};line-height:1;margin-right:4px">{prefixe}</span>'
                ) if prefixe else ""
    unite_html = (f'<span style="font-size:{corps*.46:.0f}px;font-weight:600;'
                  f'color:{col};opacity:.72;margin-left:4px">{unite}</span>'
                  ) if unite else ""
    note_html = f'<span class="kpi-pastille">{note}</span>' if note else ""
    zones = (f'<div class="kpi-intitule">{label}</div>'
             f'<div class="kpi-chiffre">{pre_html}'
             f'<span class="kpi-nombre" style="font-size:{corps}px;'
             f'color:{col}">{nombre}</span>{unite_html}{note_html}</div>'
             f'<div class="kpi-contexte">{sous}</div>')
    if bandes >= 4:
        zones += (f'<div class="kpi-courbe">'
                  f'{sparkline(serie, col, periode) if serie else ""}</div>')
    return f'<div class="tuile-kpi" style="grid-row:span {bandes}">{zones}</div>'


def kpi_row(cartes):
    """Rangée de chiffres-clés — une seule grille, des bandes partagées.

    Les tuiles ne sont pas posées dans des colonnes Streamlit mais dans une
    grille commune dont elles reprennent les bandes (`subgrid`) : nombres,
    intitulés, contextes et courbes s'alignent d'une tuile à l'autre, et un
    texte long fait grandir la bande pour toute la rangée plutôt que de
    dépasser de sa tuile.

    Le corps du nombre est celui de la tuile la plus chargée, à la largeur
    qu'impose le nombre de tuiles : une rangée se lit comme une ligne de
    bulletin, à une seule taille de chiffre.
    """
    bandes = 4 if any(len(c) > 5 and c[5] for c in cartes) else 3
    largeur = _largeur_tuile(len(cartes))
    corps = min(_corps(*_scinde(c[1]), c[4] if len(c) > 4 else None, largeur)
                for c in cartes)
    tuiles = "".join(kpi(*c, corps=corps, bandes=bandes) for c in cartes)
    st.markdown(f'<div class="rangee-kpi" style="grid-template-columns:'
                f'repeat({len(cartes)},minmax(0,1fr))">{tuiles}</div>',
                unsafe_allow_html=True)


# -------------------------------------------------------------- encarts
_ENCARTS = {
    "constat": (C["foret"],   C["foret_l"],   "Constat"),
    "alerte":  (C["risque"],  C["risque_l"],  "Alerte"),
    "action":  (C["energie"], C["energie_l"], "Décision"),
    "methode": (C["urbain"],  C["urbain_l"],  "Méthode"),
}


def encart(kind, texte, titre=None):
    """Bloc de lecture.

    Ni rail latéral, ni filet d'accent en tête : le fond teinté groupe le
    bloc et sa teinte porte déjà la nature du propos (vert = constat,
    rouge = alerte, ambre = décision). Le mot-étiquette fait le reste.
    """
    col, fond, defaut = _ENCARTS[kind]
    st.markdown(
        f'<div style="background:{fond};border:1px solid {col}33;'
        f'border-radius:10px;padding:13px 18px 15px;margin:12px 0 4px">'
        f'<div style="font-size:11px;font-weight:700;letter-spacing:.6px;'
        f'text-transform:uppercase;color:{col};margin-bottom:6px">'
        f'{titre or defaut}</div>'
        f'<div style="font-size:14px;color:{C["encre"]};line-height:1.65">'
        f'{texte}</div></div>', unsafe_allow_html=True)


def legende(*items):
    puces = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:20px;font-size:11.5px;color:{C["sourdine"]}">'
        f'<span style="width:11px;height:3px;background:{c};'
        f'display:inline-block"></span>{t}</span>' for c, t in items)
    st.markdown(f'<div style="margin-top:-2px;padding:0 4px 6px">{puces}</div>',
                unsafe_allow_html=True)


def pied(page=None):
    """Pied de page : armoiries et provenance. Sobre, sans jargon technique.

    Aucun filet ne le sépare de la page : le blanc et la petite graisse
    suffisent à dire qu'on est sorti du propos.
    """
    st.markdown(
        f'<div style="display:flex;align-items:flex-start;gap:16px;'
        f'flex-wrap:wrap;margin-top:52px">'
        f'<img src="{armoiries_uri()}" alt="Armoiries de la République togolaise" '
        f'style="height:42px;width:auto;flex:0 0 auto">'
        f'<div style="flex:1 1 430px;min-width:250px">'
        f'<div style="font-size:12.5px;font-weight:700;color:{C["encre"]}">'
        f'République Togolaise — Énergie, Climat &amp; Forêts</div>'
        f'<div style="font-size:11px;color:{C["sourdine"]};margin-top:4px;'
        f'line-height:1.55;max-width:760px">{SOURCES}</div></div></div>',
        unsafe_allow_html=True)


# ================================================================ plotly
def style_fig(fig, titre=None, hauteur=None, legende_h=True, marge_g=8):
    # `title=None` sérialise en `"title": {}`, que Plotly.js affiche « undefined ».
    # La clé ne doit donc être transmise que s'il y a réellement un titre.
    if titre:
        fig.update_layout(title=dict(
            text=titre, font=dict(size=15, color=C["encre"], family=FONT_T),
            x=0, xanchor="left", y=.98, yanchor="top"))
    fig.update_layout(
        template="plotly_white",
        # Décimale virgule, milliers espace : les gabarits d'infobulle et les
        # graduations sont formatés par Plotly, pas par `fr()`, et doivent
        # eux aussi parler français.
        separators=", ",
        font=dict(family=FONT, size=12.5, color=C["encre_2"]),
        margin=dict(l=marge_g, r=14, t=48 if titre else 14, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=hauteur,
        hoverlabel=dict(font=dict(family=FONT, size=12.5), bgcolor="white",
                        bordercolor=C["bord_fort"]),
        legend=(dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                     font=dict(size=11.5), bgcolor="rgba(0,0,0,0)")
                if legende_h else dict(font=dict(size=11.5))),
    )
    fig.update_xaxes(gridcolor=C["bord"], zeroline=False, linecolor=C["bord_fort"],
                     title_font=dict(size=11.5, color=C["sourdine"]),
                     tickfont=dict(size=11))
    fig.update_yaxes(gridcolor=C["bord"], zeroline=False, linecolor=C["bord_fort"],
                     title_font=dict(size=11.5, color=C["sourdine"]),
                     tickfont=dict(size=11))
    return fig


def annote(fig, x, y, texte, couleur, ax=0, ay=-34, fleche=True,
           row=None, col=None):
    """Annotation directe : un décideur lit le graphe, pas la légende.

    `row`/`col` visent un panneau précis quand la figure en compte plusieurs.
    """
    cible = dict(row=row, col=col) if row else {}
    fig.add_annotation(x=x, y=y, text=texte, showarrow=fleche, arrowhead=0,
                       arrowwidth=1.2, arrowcolor=couleur, ax=ax, ay=ay,
                       font=dict(size=11.5, color=couleur, family=FONT),
                       bgcolor="rgba(255,255,255,.92)", borderpad=3, **cible)
    return fig


# ---------------------------------------------------------- tableau barres
def barres_donnees(lignes, entetes, score_max=100, couleur=None):
    """Classement à barres de données — lecture d'un coup d'œil."""
    col = couleur or C["foret"]
    score_max = score_max if score_max else 1
    head = "".join(
        f'<th style="text-align:{"right" if i == 0 else "left"};padding:9px 12px;'
        f'color:{C["sur_nuit"]};font-weight:600;font-size:10.5px;'
        f'text-transform:uppercase;letter-spacing:.5px">{h}</th>'
        for i, h in enumerate(entetes))
    fort = f'font-weight:600;color:{C["encre"]}'
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
                f'<span style="font-size:9.5px;color:{C["sourdine"]};'
                f'border:1px solid {C["bord_fort"]};padding:0 5px;margin-left:6px;'
                f'white-space:nowrap">{badge}</span></td>')
        pct = max(0, min(100, 100 * score / score_max))
        tds += (f'<td style="padding:8px 12px;min-width:132px">'
                f'<div style="display:flex;align-items:center;gap:9px">'
                f'<div style="flex:1;height:12px;background:{C["neutre_l"]}">'
                f'<div style="width:{pct:.0f}%;height:100%;background:{col}">'
                f'</div></div>'
                f'<span style="font-variant-numeric:tabular-nums;font-size:12.2px;'
                f'font-weight:600;min-width:30px;text-align:right;color:{C["encre"]}">'
                f'{score:.0f}</span></div></td>')
        corps += f'<tr style="background:{bg};border-top:1px solid {C["bord"]}">{tds}</tr>'
    return (f'<div style="overflow:auto;border:1px solid {C["bord"]};'
            f'border-radius:10px">'
            f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr style="background:{C["nuit"]}">{head}'
            f'<th style="text-align:left;padding:9px 12px;color:{C["sur_nuit"]};'
            f'font-weight:600;font-size:10.5px;text-transform:uppercase;'
            f'letter-spacing:.5px">Indice</th></tr></thead>'
            f'<tbody>{corps}</tbody></table></div>')


def fr(x, dec=0):
    """Nombre au format français : 3 720 000 plutôt que 3,720,000.

    Le séparateur de milliers est une espace **insécable** : « 5 011 » ne
    doit jamais se couper en fin de ligne, ni dans une tuile, ni dans un
    tableau, ni sur un graphique.
    """
    return f"{x:,.{dec}f}".replace(",", "\u00a0").replace(".", ",")

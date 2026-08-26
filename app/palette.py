"""
Palette, rampes et fontes — **source unique** des trois livrables.

Le tableau de bord, les figures du rapport HTML et le PowerPoint lisent tous
ce fichier. C'est la seule façon d'éviter la dérive : une couleur changée ici
change partout, et un jury qui compare l'écran, le rapport et la diapositive
voit exactement les mêmes teintes.

Ce module ne dépend de rien — surtout pas de Streamlit : il doit pouvoir être
importé par un script de build (`src/make_figures.py`, `src/make_pptx.py`)
qui tourne hors de l'application.
"""

C = {
    # chrome
    "nuit":      "#0A3325",
    "nuit_2":    "#124A34",
    "sur_nuit":  "#E9F2EC",
    "sur_nuit_2": "#93BFA6",

    # surfaces
    "canvas":    "#EFF2F0",
    "surface":   "#FFFFFF",
    "sunk":      "#F5F7F6",
    "bord":      "#D5DED8",
    "bord_fort": "#B6C4BC",

    # familles sémantiques — une teinte, une signification
    "foret":     "#0F7A4A",   # forêt · propre · solution
    "foret_l":   "#E7F2EB",
    "foret_d":   "#0A5533",
    "energie":   "#B87407",   # énergie · électricité
    "energie_l": "#FBF0DC",
    "risque":    "#B32418",   # biomasse · risque · émissions
    "risque_l":  "#FBE7E4",
    "urbain":    "#125E6B",   # urbain · contexte
    "urbain_l":  "#E2EEF0",
    "charbon":   "#7C441F",   # charbon de bois
    "ardoise":   "#4E5F67",   # CO2 — gaz de référence, neutre
    "neutre":    "#85938B",   # incertain · absent
    "neutre_l":  "#ECEFED",

    # texte
    "encre":     "#0C1A14",
    "encre_2":   "#324239",
    "sourdine":  "#5D6E64",
}
RAMPE = ["#E7F2EB", "#B3D9C3", "#79BE99", "#3AA06D", "#0F7A4A", "#0A5533"]
RAMPE_T = ["#125E6B", "#5E8F93", "#C4A45E", "#B87407", "#B32418"]
DRAPEAU = ("#006A4E", "#FFCE00", "#D21034")

# Sur le web, Inter est chargée depuis Google Fonts et la pile de secours ne
# sert qu'au premier rendu. Dans un fichier PowerPoint, aucune police n'est
# embarquée : le deck doit donc être composé dans une famille présente sur
# toutes les machines, sinon la substitution défait la mise en page.
FAMILLE = "Inter"
FAMILLE_BUREAU = "Segoe UI"
FONT = f"{FAMILLE},'{FAMILLE_BUREAU}',system-ui,sans-serif"


def rgba(cle, alpha):
    """Couleur de la palette en rgba() — pour les aplats de Plotly."""
    return f"rgba({', '.join(str(v) for v in rvb(cle))},{alpha})".replace(", ", ",")


def rvb(cle):
    """Composantes 0-255 d'une couleur de la palette."""
    h = C[cle].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

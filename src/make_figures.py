"""
Figures du rapport — SVG générés directement depuis data/gold/.

Aucune dépendance de rendu (ni kaleido, ni navigateur) : les SVG sont écrits à
la main, donc légers, nets à toute échelle, imprimables et identiques partout.
La palette est celle du tableau de bord.

    python src/make_figures.py   ->  report/figures/*.svg
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT / "data" / "gold"
OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

C = {"energie": "#E29014", "foret": "#1B7A43", "foret_d": "#0C4F2B",
     "risque": "#C0392B", "urbain": "#2E6F9E", "neutre": "#94A3B8",
     "ink": "#152238", "muted": "#6B7A8D", "line": "#E4E9EF"}
FONT = "Inter,'Segoe UI',system-ui,sans-serif"

nat = json.load(open(GOLD / "diagnostic_national.json", encoding="utf-8"))
R = nat["reperes"]


def fr(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def svg(w, h, body, titre, sous=None):
    t = (f'<text x="0" y="17" font-family="{FONT}" font-size="15.5" font-weight="700" '
         f'fill="{C["foret_d"]}">{titre}</text>')
    if sous:
        t += (f'<text x="0" y="35" font-family="{FONT}" font-size="12" '
              f'fill="{C["muted"]}">{sous}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="100%" role="img" aria-label="{titre}">'
            f'<rect width="{w}" height="{h}" fill="none"/>{t}{body}</svg>')


def txt(x, y, s, size=11.5, fill=None, anchor="start", weight="400"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill or C["muted"]}" '
            f'text-anchor="{anchor}">{s}</text>')


def serie(cle):
    s = nat["series"][cle]
    return sorted((int(a), v) for a, v in s.items())


# =============================================================================
# Figure 1 — la preuve : l'accès monte, la forêt recule
# =============================================================================
def fig_preuve():
    W, H = 760, 330
    L, Rm, T, B = 52, 56, 62, 40
    x0, x1 = 1998, 2022
    elec = [(a, v) for a, v in serie("elec_rural") if x0 <= a <= x1]
    foret = [(a, v) for a, v in serie("foret_pct") if x0 <= a <= x1]
    cuis = [(a, v) for a, v in serie("cuisson_rural") if x0 <= a <= x1]

    def px(a):
        return L + (a - x0) / (x1 - x0) * (W - L - Rm)

    def pyg(v, lo=0, hi=40):     # axe gauche : accès %
        return H - B - (v - lo) / (hi - lo) * (H - T - B)

    def pyd(v, lo=21.5, hi=24.5):  # axe droit : couvert forestier %
        return H - B - (v - lo) / (hi - lo) * (H - T - B)

    b = ""
    for g in range(0, 41, 10):
        y = pyg(g)
        b += f'<line x1="{L}" y1="{y:.1f}" x2="{W-Rm}" y2="{y:.1f}" stroke="{C["line"]}"/>'
        b += txt(L - 8, y + 4, f"{g} %", 10.5, anchor="end")
    for g in (22, 23, 24):
        b += txt(W - Rm + 8, pyd(g) + 4, f"{g} %", 10.5, fill=C["foret"])
    for a in (1998, 2004, 2010, 2016, 2022):
        b += txt(px(a), H - B + 17, str(a), 10.5, anchor="middle")

    # aire forêt
    pts = " ".join(f"{px(a):.1f},{pyd(v):.1f}" for a, v in foret)
    b += (f'<polygon points="{px(foret[0][0]):.1f},{H-B} {pts} '
          f'{px(foret[-1][0]):.1f},{H-B}" fill="{C["foret"]}" opacity=".09"/>')
    b += (f'<polyline points="{pts}" fill="none" stroke="{C["foret"]}" '
          f'stroke-width="2.8" stroke-linejoin="round"/>')
    # accès rural
    p2 = " ".join(f"{px(a):.1f},{pyg(v):.1f}" for a, v in elec)
    b += (f'<polyline points="{p2}" fill="none" stroke="{C["energie"]}" '
          f'stroke-width="2.8" stroke-linejoin="round"/>')
    # cuisson propre
    p3 = " ".join(f"{px(a):.1f},{pyg(v):.1f}" for a, v in cuis)
    b += (f'<polyline points="{p3}" fill="none" stroke="{C["risque"]}" '
          f'stroke-width="2.2" stroke-dasharray="4 3"/>')

    b += txt(px(2022) - 6, pyg(elec[-1][1]) - 9, f"{elec[-1][1]:.0f} %", 12,
             C["energie"], "end", "700")
    b += txt(px(2022) - 6, pyd(foret[-1][1]) + 18, f"{foret[-1][1]:.1f} %", 12,
             C["foret"], "end", "700")
    b += txt(px(2016), pyg(cuis[-1][1]) + 17, f"cuisson propre rurale : {cuis[-1][1]:.1f} %",
             11, C["risque"], "middle", "600")

    ly = H - 8
    for i, (col, lab, dash) in enumerate([
            (C["energie"], "Accès rural à l'électricité (axe gauche)", ""),
            (C["foret"], "Couvert forestier (axe droit)", ""),
            (C["risque"], "Cuisson propre rurale", ' stroke-dasharray="4 3"')]):
        x = L + i * 232
        b += (f'<line x1="{x}" y1="{ly-4}" x2="{x+18}" y2="{ly-4}" stroke="{col}" '
              f'stroke-width="2.8"{dash}/>')
        b += txt(x + 24, ly, lab, 10.8)

    return svg(W, H, b, "L'électrification progresse, la forêt recule sans interruption",
               "Togo, 1998-2022 · Banque Mondiale")


# =============================================================================
# Figure 2 — rythme observé contre rythme requis
# =============================================================================
def fig_rythme():
    W, H = 760, 210
    er = R["elec_rural"]
    L, T = 210, 58
    barw = W - L - 130
    vmax = er["rythme_requis_2030"] * 1.05
    lignes = [
        (f"Rythme observé {er['annee_depart']}–{er['annee']}", er["rythme_observe"],
         C["neutre"]),
        ("Rythme requis pour l'accès universel en 2030", er["rythme_requis_2030"],
         C["risque"]),
    ]
    b = ""
    for i, (lab, v, col) in enumerate(lignes):
        y = T + i * 46
        w = max(3, v / vmax * barw)
        b += (f'<rect x="{L}" y="{y}" width="{w:.1f}" height="26" rx="4" fill="{col}"/>')
        b += txt(L - 12, y + 18, lab, 12, C["ink"], "end", "600")
        b += txt(L + w + 10, y + 18, f"+{v:.2f} point/an".replace(".", ","), 12.5,
                 col, "start", "700")
    y = T + 2 * 46 + 14
    b += (f'<rect x="{L}" y="{y}" width="{barw}" height="30" rx="6" '
          f'fill="{C["risque"]}" opacity=".07"/>')
    b += txt(L + 14, y + 20,
             f"soit un effort à multiplier par {er['facteur_acceleration']:.0f}", 13,
             C["risque"], "start", "700")
    b += txt(L - 12, y + 20, "Écart à combler", 12, C["ink"], "end", "600")
    return svg(W, H, b, "L'objectif 2030 demande dix fois le rythme actuel",
               f"Accès rural à l'électricité · au rythme observé, l'accès universel "
               f"tomberait en {er['annee_atteinte_tendanciel']:.0f}")


# =============================================================================
# Figure 3 — combustibles de cuisson, deux enquêtes
# =============================================================================
def fig_combustibles():
    W, H = 760, 280
    cb = R["combustibles"]
    a0, a1 = cb["annees"]
    lignes = [("Bois de chauffe", cb["bois"][0], cb["bois"][1], C["risque"]),
              ("Charbon de bois", cb["charbon"][0], cb["charbon"][1], "#8C4A2F"),
              ("GPL / gaz", cb["gpl"][0], cb["gpl"][1], C["foret"])]
    L, T = 150, 66
    barw = W - L - 150
    vmax = 60
    b = ""
    for i, (lab, v0, v1, col) in enumerate(lignes):
        y = T + i * 62
        b += txt(L - 12, y + 26, lab, 12, C["ink"], "end", "600")
        for j, (v, c, an) in enumerate([(v0, C["neutre"], a0), (v1, col, a1)]):
            yy = y + j * 22
            w = max(2, v / vmax * barw)
            b += f'<rect x="{L}" y="{yy}" width="{w:.1f}" height="18" rx="3" fill="{c}"/>'
            b += txt(L + w + 8, yy + 14, f"{v:.1f} %".replace(".", ","), 11.5, c,
                     "start", "700")
            b += txt(L + 8, yy + 14, str(an), 10, "#ffffff", "start", "700")
        delta = v1 - v0
        signe = "+" if delta > 0 else "−"
        b += txt(W - 8, y + 26, f"{signe}{abs(delta):.1f} pt".replace(".", ","), 12,
                 col if delta > 0 else C["muted"], "end", "700")
    y = T + 3 * 62 - 4
    b += (f'<rect x="{L}" y="{y}" width="{barw + 130}" height="34" rx="6" '
          f'fill="{C["risque"]}" opacity=".07"/>')
    b += txt(L + 14, y + 22,
             f"Total biomasse : {cb['biomasse'][0]:.1f} %  →  {cb['biomasse'][1]:.1f} %  "
             f"— la dépendance ne recule pas".replace(".", ","), 12.5, C["risque"],
             "start", "700")
    return svg(W, H, b, "Le bois de chauffe progresse entre les deux enquêtes",
               f"Combustible principal de cuisson, % des ménages · enquêtes {a0} et {a1}")


# =============================================================================
# Figure 4 — la portée comparée des trois leviers
# =============================================================================
def fig_leviers():
    W, H = 760, 240
    pop = dict(serie("pop_totale"))[max(dict(serie("pop_totale")))]
    biom = pop * R["combustibles"]["biomasse"][1] / 100
    sans = R["ruraux_sans_elec"]["personnes"]
    L, T = 236, 62
    barw = W - L - 150
    vmax = biom * 1.02
    lignes = [
        ("Cuisson propre", biom, C["risque"], f"{fr(biom/1e6, 1)} millions de personnes"),
        ("Électrification rurale décentralisée", sans, C["energie"],
         f"{fr(sans/1e6, 1)} millions de personnes"),
    ]
    b = ""
    for i, (lab, v, col, note) in enumerate(lignes):
        y = T + i * 52
        w = max(4, v / vmax * barw)
        b += f'<rect x="{L}" y="{y}" width="{w:.1f}" height="30" rx="4" fill="{col}"/>'
        b += txt(L - 12, y + 20, lab, 12, C["ink"], "end", "600")
        b += txt(L + w + 10, y + 20, note, 12, col, "start", "700")
    # le 3e levier ne se compte pas en personnes : pas de barre, pas de fausse échelle
    y = T + 2 * 52 + 4
    b += (f'<rect x="{L}" y="{y}" width="{barw+120}" height="30" rx="4" '
          f'fill="{C["foret"]}" opacity=".10"/>')
    b += txt(L - 12, y + 20, "Protection ciblée des forêts", 12, C["ink"], "end", "600")
    b += txt(L + 12, y + 20,
             f"{R['forets']['nb_robustes']} massifs prioritaires · "
             f"{fr(R['forets']['surface_totale_ha'])} ha — ne se compte pas en personnes",
             11.5, C["foret_d"], "start", "600")
    b += txt(L - 12, H - 12,
             f"La cuisson propre concerne {biom/sans:.1f} fois plus de Togolais que "
             f"l'électrification — et agit aussi sur la forêt, la santé et le climat.",
             11.5, C["muted"], "end")
    return svg(W, H, b, "Ce que chaque levier touche réellement",
               "Population directement concernée · population totale "
               f"{fr(pop/1e6, 1)} M")


# =============================================================================
# Figure 5 — le bilan GES change de sens selon l'unité de lecture
# =============================================================================
def fig_ges():
    W, H = 760, 336
    PRG = {"CO2": 1, "CH4": 28, "N2O": 265}
    gz = nat["ges_gaz"]
    secteurs = ["Agriculture & forêts (AFAT)", "Industrie (PIUP)", "Énergie", "Déchets"]
    coul = {"Agriculture & forêts (AFAT)": C["foret"], "Industrie (PIUP)": C["urbain"],
            "Énergie": C["energie"], "Déchets": C["neutre"]}

    def parts(co2e):
        tot = {}
        for r in gz:
            p = PRG[r["gaz"]] if co2e else 1
            tot[r["secteur_court"]] = tot.get(r["secteur_court"], 0) + r["Value"] * p
        s = sum(tot.values())
        return {k: 100 * v / s for k, v in tot.items()}

    brut, co2e = parts(False), parts(True)
    L, T, colw, gap = 150, 78, 92, 66
    hmax = 160
    b = ""
    for j, (lab, dd) in enumerate([("Masse brute (source)", brut),
                                   ("Équivalent CO₂ (PRG AR5)", co2e)]):
        x = L + j * (colw + gap) + 60
        y = T
        for s in secteurs:
            h = dd[s] / 100 * hmax
            b += (f'<rect x="{x}" y="{y:.1f}" width="{colw}" height="{max(h,1.2):.1f}" '
                  f'fill="{coul[s]}" opacity=".92"/>')
            if dd[s] > 5:
                b += txt(x + colw / 2, y + h / 2 + 4, f"{dd[s]:.0f} %", 11.5,
                         "#ffffff", "middle", "700")
            y += h
        b += txt(x + colw / 2, T + hmax + 22, lab, 11.5, C["ink"], "middle", "600")
    ly = T + hmax + 52
    for i, s in enumerate(secteurs):
        x = L + (i % 2) * 300
        yy = ly + (i // 2) * 20
        b += f'<rect x="{x}" y="{yy-9}" width="11" height="11" rx="2" fill="{coul[s]}"/>'
        b += txt(x + 17, yy, s, 11)
    b += txt(L + 60 + colw + 6, T + 12, "→", 20, C["muted"], "middle", "700")
    b += txt(W - 8, T + hmax + 22,
             f"l'énergie passe de {brut['Énergie']:.0f} % à {co2e['Énergie']:.0f} %",
             12, C["energie"], "end", "700")
    return svg(W, H, b, "Le classement des secteurs dépend de l'unité de lecture",
               "Inventaire GES 2018 · le total publié additionne des masses de gaz "
               "à poids égal")


FIGS = {"fig1_preuve.svg": fig_preuve, "fig2_rythme.svg": fig_rythme,
        "fig3_combustibles.svg": fig_combustibles, "fig4_leviers.svg": fig_leviers,
        "fig5_ges.svg": fig_ges}

if __name__ == "__main__":
    for nom, fn in FIGS.items():
        (OUT / nom).write_text(fn(), encoding="utf-8")
        print(f"  {nom:26s} {(OUT/nom).stat().st_size/1024:6.1f} Ko")
    print(f"[OK] {len(FIGS)} figures écrites dans {OUT}")

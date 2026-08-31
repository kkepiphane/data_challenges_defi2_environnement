"""
Assemble le rapport final : injecte les figures SVG dans le gabarit HTML.

    python src/make_report.py   ->  report/rapport.html  (autonome, imprimable)

Le fichier produit ne dépend d'aucune ressource externe hors polices Google :
les figures sont inlinées, ce qui le rend partageable et archivable tel quel.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report"
FIGS = REPORT / "figures"
GOLD = ROOT / "data" / "gold"

LEGENDES = {
    "FIG1": ("fig1_preuve.svg", "Figure 1",
             "Accès rural à l'électricité, accès rural à une cuisson propre et "
             "couvert forestier, 1998-2022. L'accès progresse, la forêt recule, "
             "la cuisson ne bouge pas."),
    "FIG2": ("fig2_rythme.svg", "Figure 2",
             "Rythme d'électrification rurale observé depuis 1998, comparé au rythme "
             "qu'exigerait l'accès universel en 2030."),
    "FIG3": ("fig3_combustibles.svg", "Figure 3",
             "Combustible principal de cuisson entre les deux enquêtes ménages "
             "disponibles. Le total biomasse ne bouge pas ; sa composition se dégrade."),
    "FIG4": ("fig4_leviers.svg", "Figure 4",
             "Population directement concernée par chacun des trois leviers. "
             "L'ordre de priorité des recommandations découle de cette mesure."),
    "FIG6": ("fig6_tapis.svg", "Figure 6",
             "Décomposition de la variation du nombre de ruraux privés "
             "d'électricité entre 1998 et 2022. La somme de l'effet démographique "
             "et de l'effet d'électrification reconstitue la variation observée "
             "au chiffre près."),
    "FIG5": ("fig5_ges.svg", "Figure 5",
             "Répartition sectorielle des émissions 2018 selon l'unité de lecture : "
             "masse brute telle que publiée, puis équivalent CO₂ (PRG 100 ans, AR5)."),
}


def fr(x, d=0):
    """Nombre au format du rapport : espace pour les milliers, virgule décimale."""
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def controles():
    """Chiffres directeurs du rapport, reformatés depuis data/gold/.

    Le rapport est rédigé à la main — c'est un texte, pas un tableau. Sans ce
    garde-fou, une valeur recalculée par le pipeline pourrait cesser de
    correspondre à ce que le rapport affirme, sans que rien ne le signale.
    Chaque entrée est la chaîne exacte attendue dans le document, arrondie
    comme le texte l'arrondit — puisque c'est ce que le lecteur voit.
    """
    R = json.load(open(GOLD / "diagnostic_national.json",
                       encoding="utf-8"))["reperes"]
    tr, rg, er = R["tapis_roulant"], R["regimes_foret"], R["elec_rural"]
    deficit = tr["seuil_moyen_10ans"] - tr["raccordements_moyens_10ans"]
    return {
        "hausse du stock de ruraux sans électricité": fr(tr["variation"]),
        "hausse en pourcentage": f"{tr['variation_pct']:.0f} %",
        "effet démographique": fr(tr["effet_demographie"]),
        "effet d'électrification": fr(abs(tr["effet_acces"])),
        "taux de compensation": f"{tr['taux_compensation']:.0f} %",
        "seuil de stagnation": fr(round(tr["seuil_stagnation"], -2)),
        "raccordements réalisés sur dix ans": fr(tr["raccordements_moyens_10ans"]),
        "seuil moyen sur dix ans": fr(tr["seuil_moyen_10ans"]),
        "déficit annuel": fr(deficit),
        "variation du stock sur dix ans": fr(tr["variation_decennie"]),
        "perte forestière du régime en cours": fr(rg["perte_recente_ha_an"]),
        "rythme d'électrification": fr(er["rythme_observe"], 2),
        "facteur d'accélération": f"{er['facteur_acceleration']:.0f}",
        "année d'atteinte tendancielle": f"{er['annee_atteinte_tendanciel']:.0f}",
    }


def bloc_figure(cle):
    fichier, num, legende = LEGENDES[cle]
    svg = (FIGS / fichier).read_text(encoding="utf-8")
    # le SVG porte déjà son propre titre : on ne le répète pas dans la légende
    return (f'<figure>{svg}'
            f'<figcaption><b>{num}</b> — {legende}</figcaption></figure>')


def main():
    gabarit = (REPORT / "rapport.template.html").read_text(encoding="utf-8")
    manquantes = [c for c in LEGENDES if not (FIGS / LEGENDES[c][0]).exists()]
    if manquantes:
        raise SystemExit(f"Figures absentes : {manquantes}. "
                         "Lancez d'abord : python src/make_figures.py")

    html = re.sub(r"<!--(FIG\d)-->", lambda m: bloc_figure(m.group(1)), gabarit)

    restantes = re.findall(r"<!--FIG\d-->", html)
    if restantes:
        raise SystemExit(f"Marqueurs non résolus : {restantes}")

    # --- cohérence : le texte doit dire ce que le pipeline calcule.
    # On cherche dans le gabarit seul, figures retirées : un chiffre présent
    # uniquement dans un SVG ne prouverait pas que la rédaction est à jour.
    attendus = controles()
    texte = re.sub(r"<svg.*?</svg>", "", gabarit, flags=re.S)
    absents = {k: v for k, v in attendus.items() if v not in texte}
    if absents:
        lignes = "\n".join(
            f"     - {k} : « {v} » introuvable dans le texte"
            for k, v in absents.items())
        raise SystemExit(
            f"[ECART] {len(absents)} chiffre(s) du gold ne figurent plus "
            f"dans le rapport :\n{lignes}\n"
            "   Mettez le gabarit à jour, ou corrigez le contrôle.")

    # 1. version « fragment » : en-tête <title>/<link>/<style> puis contenu.
    #    C'est le format attendu par le publieur d'artefact, qui fournit lui-même
    #    le squelette <!doctype html><head><body>.
    frag = REPORT / "rapport.artifact.html"
    frag.write_text(html, encoding="utf-8")

    # 2. version autonome : document complet, ouvrable et imprimable en local
    #    (sans doctype, un navigateur bascule en quirks mode et casse la mise en page).
    titre = re.search(r"<title>(.*?)</title>", html).group(1)
    complet = ('<!doctype html>\n<html lang="fr">\n<head>\n'
               '<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
               '<meta name="description" content="Rapport du Défi 2 — énergie, '
               'climat et forêts au Togo.">\n'
               f'{html.split("</style>")[0]}</style>\n</head>\n<body>\n'
               f'{html.split("</style>", 1)[1]}\n</body>\n</html>\n')
    autonome = REPORT / "rapport.html"
    autonome.write_text(complet, encoding="utf-8")

    for p in (autonome, frag):
        print(f"[OK] {p.name:26s} {p.stat().st_size/1024:6.0f} Ko  ({titre})")
    print(f"     {len(LEGENDES)} figures inlinées, aucune ressource externe "
          "hors polices Google")
    print(f"     {len(attendus)} chiffres directeurs conformes au fichier gold")


if __name__ == "__main__":
    main()

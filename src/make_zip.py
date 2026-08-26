"""
Archive de rendu du tableau de bord — le projet, et rien d'autre.

    python src/make_zip.py   ->  Defi2_Togo_dashboard.zip

Ce que le jury reçoit : de quoi relancer le tableau de bord chez lui, et de
quoi vérifier d'où viennent les chiffres. Rien d'autre.

Restent donc dehors :
- le PowerPoint, déposé séparément sur la plateforme ;
- les scripts qui fabriquent les autres livrables (`make_pptx`,
  `make_armoiries_png`, `make_figures`, `make_report`) et celui-ci même —
  un dossier de rendu n'est pas un atelier ;
- l'environnement virtuel, l'historique Git, les caches, les verrous Office.

Restent dedans, en plus de l'application : `build_gold.py` et `verify.py`,
qui montrent comment `data/gold/` a été construit à partir de `data/raw/`.
C'est la provenance des chiffres, elle fait partie de l'analyse.
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOM = "Defi2_Togo_dashboard"
ARCHIVE = ROOT / f"{NOM}.zip"
LIMITE_MO = 20

CONTENU = [
    "app",                        # le tableau de bord
    "data",                       # données brutes et données gold
    "docs",                       # provenance et définitions des indicateurs
    "src/build_gold.py",          # data/raw -> data/gold
    "src/verify.py",              # contrôles de cohérence des données
    "requirements.txt",
    "requirements-pipeline.txt",
]                                 # le README est écrit à part, adapté

DOSSIERS_EXCLUS = {"venv", ".venv", "__pycache__", ".git", ".pytest_cache",
                   ".ipynb_checkpoints"}
MOTIFS_EXCLUS = (".pyc", ".pyo", ".log", ".zip", ".pptx", ".docx", ".xlsx")
PREFIXES_EXCLUS = ("~$",)          # verrous Word / PowerPoint
NOMS_EXCLUS = {"secrets.toml"}

# Le README du dépôt décrit aussi le rapport et les scripts qui le
# fabriquent. Dans l'archive, ces fichiers n'existent pas : on retire les
# passages qui les mentionnent, sinon le jury cherche un fichier absent dès
# la première minute. Chaque retrait est vérifié — si le README change et
# qu'un motif ne correspond plus, la construction échoue au lieu de livrer
# un document faux.
RETRAITS = [
    ("Le rapport se lit hors ligne dans un navigateur : ouvrir "
     "`report/rapport.html`\n(document autonome, imprimable en PDF).\n\n", ""),
    ("│   ├── verify.py                 audit : recalcul indépendant depuis data/raw/\n"
     "│   ├── make_figures.py           figures SVG du rapport\n"
     "│   └── make_report.py            assemblage du rapport final\n",
     "│   └── verify.py                 audit : recalcul indépendant depuis data/raw/\n"),
    ("├── report/\n"
     "│   ├── rapport.html              rapport autonome, imprimable\n"
     "│   ├── rapport.template.html     gabarit (source éditable)\n"
     "│   └── figures/                  figures SVG générées\n"
     "│\n", ""),
    ("python src/make_figures.py    # figures SVG du rapport\n"
     "python src/make_report.py     # rapport HTML final\n", ""),
    ("dashboard_defi2_togo/\n", f"{NOM}/\n"),
    ("**Aucun chiffre du rapport\nou du tableau de bord n'est saisi à la main**",
     "**Aucun chiffre du tableau de bord\nn'est saisi à la main**"),
]
# Aucun de ces mots ne doit subsister dans le README livré.
INTERDITS = ("report/", "make_figures", "make_report", "make_pptx", ".pptx",
             "rapport.html")


def readme_adapte():
    texte = (ROOT / "README.md").read_text(encoding="utf-8")
    for motif, remplacement in RETRAITS:
        if motif not in texte:
            raise SystemExit(
                "Le README a changé : ce passage est introuvable, "
                f"l'adaptation ne peut pas être vérifiée —\n{motif[:80]}…")
        texte = texte.replace(motif, remplacement)
    restants = [m for m in INTERDITS if m in texte]
    if restants:
        raise SystemExit(f"Le README livré mentionne encore : {restants}")
    return texte


def retenir(chemin):
    if any(p in DOSSIERS_EXCLUS for p in chemin.parts):
        return False
    if chemin.name.startswith(PREFIXES_EXCLUS) or chemin.name in NOMS_EXCLUS:
        return False
    return chemin.suffix.lower() not in MOTIFS_EXCLUS


def fichiers():
    for entree in CONTENU:
        cible = ROOT / entree
        if not cible.exists():
            print(f"  (absent, ignoré) {entree}")
            continue
        if cible.is_file():
            yield cible
        else:
            yield from (f for f in sorted(cible.rglob("*"))
                        if f.is_file() and retenir(f.relative_to(ROOT)))


def construire():
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    readme = readme_adapte()
    n, brut = 1, len(readme.encode("utf-8"))
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        z.writestr(f"{NOM}/README.md", readme)
        for f in fichiers():
            z.write(f, Path(NOM) / f.relative_to(ROOT))
            n, brut = n + 1, brut + f.stat().st_size
    taille = ARCHIVE.stat().st_size / 1024 / 1024
    print(f"[OK] {n} fichiers, {brut/1024/1024:.1f} Mo compresses en "
          f"{taille:.1f} Mo")
    print(f"     {ARCHIVE}")
    if taille > LIMITE_MO:
        raise SystemExit(f"Archive trop lourde : {taille:.1f} > {LIMITE_MO} Mo")
    return ARCHIVE


if __name__ == "__main__":
    construire()

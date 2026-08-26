"""
Armoiries du Togo en PNG transparent, pour le PowerPoint.

    python src/make_armoiries_png.py   ->  app/assets/armoiries_togo.png

PowerPoint sait afficher du SVG, mais python-pptx ne sait pas en embarquer :
il faut donc un raster. Plutôt qu'un convertisseur supplémentaire à installer,
on utilise le moteur de rendu déjà présent sur la machine — Chrome ou Edge en
mode sans interface — avec un fond transparent. Le résultat est fidèle au SVG
d'origine, et la commande est reproductible.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "app" / "assets" / "armoiries_togo.svg"
PNG = ROOT / "app" / "assets" / "armoiries_togo.png"
COTE = 1200                      # côté du rendu, avant rognage

NAVIGATEURS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]


def navigateur():
    for n in NAVIGATEURS:
        if n.exists():
            return n
    sys.exit("Aucun navigateur trouvé pour le rendu — installez Chrome ou Edge.")


def rendre():
    svg = SVG.read_text(encoding="utf-8")
    # Le SVG est posé seul dans une page transparente, à la taille voulue :
    # le navigateur fait le rendu, on rogne ensuite les marges vides.
    page = (f'<!doctype html><meta charset="utf-8">'
            f'<style>html,body{{margin:0;background:transparent}}'
            f'svg{{width:{COTE}px;height:{COTE}px;display:block}}</style>'
            f'{svg}')
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "armoiries.html"
        brut = Path(tmp) / "brut.png"
        html.write_text(page, encoding="utf-8")
        subprocess.run(
            [str(navigateur()), "--headless=new", "--disable-gpu",
             "--hide-scrollbars", "--force-device-scale-factor=1",
             "--default-background-color=00000000",
             f"--window-size={COTE},{COTE}",
             f"--screenshot={brut}", html.as_uri()],
            check=True, capture_output=True, timeout=120)
        image = Image.open(brut).convert("RGBA")
        cadre = image.getbbox()          # rognage des bords transparents
        if cadre:
            image = image.crop(cadre)
        image.save(PNG)
    return PNG


if __name__ == "__main__":
    chemin = rendre()
    with Image.open(chemin) as im:
        print(f"[OK] {im.size[0]}x{im.size[1]} px, mode {im.mode}, "
              f"{chemin.stat().st_size / 1024:.0f} Ko")
        print(f"     {chemin}")

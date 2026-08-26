# Le bois et la lumière — Énergie, Climat & Forêts au Togo

**Défi 2 · datalab.gouv.tg** — tableau de bord interactif et rapport d'analyse.

> Le Togo veut électrifier tous ses villages d'ici 2030 tout en protégeant ses
> forêts. Les données montrent que ces deux objectifs se jouent au même endroit —
> dans la cuisine des ménages — et que la stratégie actuelle ne regarde pas là.

---

## Démarrage rapide

```bash
pip install -r requirements.txt
streamlit run app/Accueil.py
```

Le tableau de bord s'ouvre sur http://localhost:8501

Le rapport se lit hors ligne dans un navigateur : ouvrir `report/rapport.html`
(document autonome, imprimable en PDF).

---

## Ce que contient le tableau de bord

Six pages, une par objectif du défi, toutes construites sur le même principe :
**la conclusion en haut, la preuve en dessous, les réglages à portée de main.**

| Page | Objectif du défi | Interactions |
|---|---|---|
| 🧭 **Diagnostic** | Vue décisionnelle | Filtre de période global |
| ⚡ **Électrification** | 1 — accès et coupures | Cible d'accès 2030 réglable, projection tendancielle, effort recalculé en personnes |
| 🔥 **Cuisson** | 2 — ménages et biomasse | Simulateur de sortie de la biomasse, attribution du recul forestier paramétrable |
| 🌍 **Inventaire** | 3 et 4 — GES et températures | Sélecteur de gaz, bascule masse brute / équivalent CO₂, choix des stations |
| 🗺️ **Forêts** | 5 — cartographie | Trois curseurs de pondération recalculant carte et classement en direct |
| ✅ **Recommandations** | 6 — recommandations | Simulateur de trajectoire 2030 à trois leviers |

---

## Les cinq résultats

1. **L'accès rural progresse dix fois trop lentement.** +0,91 point par an depuis
   1998, quand l'objectif 2030 en exigerait 9,4. Au rythme observé, l'accès
   universel rural tomberait vers 2104.
2. **Le réseau qui arrive n'est pas fiable.** Les coupures se raréfient (7,2 →
   5,5 par mois entre 2009 et 2016) mais se généralisent : 80,4 % → 93,8 % des
   entreprises touchées.
3. **C'est la marmite, pas l'ampoule, qui consomme la forêt.** 89,4 % des ménages
   cuisinent au bois ou au charbon, part inchangée depuis 2014 — et le bois brut
   a gagné 3,6 points. 5 011 hectares de forêt disparaissent chaque année.
4. **Le « renouvelable » togolais est du bois de feu.** 75,1 % d'énergie finale
   renouvelable pour 11,9 % d'accès à une cuisson propre : l'indicateur de suivi
   officiel se dégradera quand la situation s'améliorera.
5. **Neuf forêts concentrent la priorité.** Sur 53 forêts classées, neuf restent
   dans le top 10 quelle que soit la pondération testée — le classement de tête
   est un résultat des données, pas un choix d'analyste.

---

## Structure du dépôt

```
dashboard_defi2_togo/
├── app/                          tableau de bord Streamlit
│   ├── Accueil.py                point d'entrée : navigation + filtres globaux
│   ├── theme.py                  composants, feuille de style, gabarit Plotly
│   ├── palette.py                couleurs et fontes — source unique
│   ├── data.py                   chargeurs mis en cache
│   ├── assets/                   armoiries de la République togolaise
│   └── views/                    une page par objectif du défi
│       ├── synthese.py           vue décisionnelle
│       ├── acces.py              objectif 1 — accès et fiabilité
│       ├── cuisson.py            objectif 2 — ménages et forêts
│       ├── emissions.py          objectifs 3 et 4 — GES et climat
│       ├── priorisation.py       objectif 5 — carte des 53 forêts
│       └── plan.py               objectif 6 — recommandations
│
├── src/                          pipeline reproductible
│   ├── build_gold.py             bronze -> gold, avec journal des traitements
│   ├── verify.py                 audit : recalcul indépendant depuis data/raw/
│   ├── make_figures.py           figures SVG du rapport
│   └── make_report.py            assemblage du rapport final
│
├── data/
│   ├── raw/                      les 6 jeux de données du défi, intacts
│   └── gold/                     données analytiques + journal_construction.txt
│
├── report/
│   ├── rapport.html              rapport autonome, imprimable
│   ├── rapport.template.html     gabarit (source éditable)
│   └── figures/                  figures SVG générées
│
└── docs/sources.md               sources, correctifs qualité, méthodologie, limites
```

---

## Reconstruire depuis les fichiers bruts

Les six fichiers du défi sont dans `data/raw/`. Tout se régénère depuis eux :

```bash
pip install -r requirements.txt -r requirements-pipeline.txt
python src/build_gold.py      # données analytiques + journal des traitements
python src/verify.py          # audit d'intégrité des chiffres
python src/make_figures.py    # figures SVG du rapport
python src/make_report.py     # rapport HTML final
```

`build_gold.py` écrit `data/gold/journal_construction.txt` : le détail de chaque
correctif appliqué et de chaque chiffre clé recalculé. **Aucun chiffre du rapport
ou du tableau de bord n'est saisi à la main** — tous sont recalculés à chaque
exécution.

## Audit d'intégrité des chiffres

```bash
python src/verify.py
```

Ce script recalcule 42 chiffres clés **directement depuis `data/raw/`**, avec un
code écrit indépendamment du pipeline (lecture `csv` standard, aucune fonction
partagée), et les compare à ce qui est publié. Il sort en erreur au moindre écart.
Dernier passage : **42/42 conformes**.

Trois éléments seulement ne proviennent pas des six fichiers du défi, et sont
signalés comme tels dans l'interface et dans `docs/sources.md` :

1. les **coordonnées des 10 stations météo**, absentes de toutes les sources ;
2. les **facteurs PRG du GIEC** (CH₄ × 28, N₂O × 265), constantes scientifiques
   utilisées pour la lecture en équivalent CO₂ ;
3. les **curseurs des simulateurs**, qui sont des hypothèses réglées par
   l'utilisateur et étiquetées comme telles — elles produisent des projections,
   jamais des données.

---

## Traitements de qualité appliqués

Le détail complet est dans [`docs/sources.md`](docs/sources.md). En résumé :

- **22 % de doublons stricts** supprimés du fichier Banque Mondiale ;
- **précipitations écartées** (valeur constante répétée — les tracer produirait
  une fausse tendance) ;
- **températures au degré entier** : gradient spatial exploité, tendance sur
  7 ans écartée ;
- **16 forêts sur 53** ont un polygone < 10 ha (numérisation partielle) :
  signalées, neutralisées dans l'indice, filtrables ;
- **17 forêts sans année de classement** : aucune imputation, variable écartée
  du score ;
- **reprojection UTM 31N** avant tout calcul de surface ou de distance.

Seul apport externe : les **coordonnées des 10 stations météo**, absentes de tous
les fichiers, sans lesquelles aucun croisement climat × forêt n'est possible.
Elles figurent en clair dans `src/build_gold.py`.

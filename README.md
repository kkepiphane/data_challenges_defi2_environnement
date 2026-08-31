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

Sept pages, une par objectif du défi plus une sur la qualité des données, toutes
construites sur le même principe : **la conclusion en haut, la preuve en dessous,
les réglages regroupés dans un bandeau unique.** Les données de chaque graphique
sont exportables en CSV telles qu'elles sont affichées.

| Page | Objectif du défi | Interactions |
|---|---|---|
| 🧭 **Diagnostic** | Vue décisionnelle | Filtre de période global, cascade de décomposition du stock, exports CSV |
| ⚡ **Électrification** | 1 — accès et coupures | Cible 2030 réglable, enveloppe d'incertitude à 95 % de la pente, raccordements annuels face au seuil démographique, lissage optionnel |
| 🔥 **Cuisson** | 2 — ménages et biomasse | Simulateur de sortie de la biomasse, attribution du recul forestier paramétrable et bornée par la mesure d'usage des sols |
| 🌍 **Inventaire** | 3 et 4 — GES et températures | Sélecteur de gaz, bascule masse brute / équivalent CO₂, choix des stations |
| 🗺️ **Forêts** | 5 — cartographie | Quatre doctrines de priorisation pré-réglées, trois curseurs de pondération recalculant carte et classement en direct, recherche par massif |
| ✅ **Recommandations** | 6 — recommandations | Trois scénarios pré-réglés, simulateur de trajectoire 2030, récapitulatif décisionnel exportable |
| 🔍 **Données** | Méthode et qualité | Audit automatique des 32 séries filtrable par verdict, détail des 62 contrôles d'intégrité |

---

## Les sept résultats

1. **Le taux monte, le nombre de personnes privées d'électricité aussi.** Le taux
   d'accès rural a été multiplié par huit depuis 1998 ; le **nombre** de ruraux
   sans électricité est passé de 3,11 à 3,72 millions, soit **+19 %**. La
   décomposition est une identité comptable : la démographie a ajouté 1 693 547
   personnes non raccordées, l'électrification en a retiré 1 086 596.
2. **Le repère opérationnel n'est pas un taux mais un volume.** Le stock cesse de
   croître exactement quand les raccordements annuels égalent la croissance de la
   population rurale — 65 658 personnes en 2022. Sur 2012-2022, 56 801
   raccordements par an ont été réalisés pour un seuil moyen de 70 557 : le
   déficit de 13 756 par an explique, au chiffre près, les 137 560 personnes
   supplémentaires sans électricité.
3. **Le réseau qui arrive n'est pas fiable.** Les coupures se raréfient (7,2 →
   5,5 par mois entre 2009 et 2016) mais se généralisent : 80,4 % → 93,8 % des
   entreprises touchées.
4. **C'est la marmite, pas l'ampoule, qui consomme la forêt.** 89,4 % des ménages
   cuisinent au bois ou au charbon, part inchangée depuis 2014 — et le bois brut
   a gagné 3,6 points.
5. **La série forestière ne contient que trois mesures indépendantes.** Elle est
   interpolée entre points de référence FAO : la perte n'est pas de 5 011 ha/an
   (moyenne qui ne correspond à aucune année réelle) mais de 9 320 ha/an jusqu'en
   2000, puis **2 960 ha/an depuis** — divisée par 3,1, jamais interrompue.
6. **Ce qui prend la place de la forêt se mesure, et ce n'est pas le bois de feu.**
   Entre 1990 et 2013, la surface agricole a gagné 6 600 km² quand la forêt en
   perdait 1 317 : **cinq fois plus**. Le pays défriche 19 690 ha de terres
   céréalières par an, près de sept fois sa perte forestière, et 46 % de la
   hausse de sa production vient de la surface, non du rendement (1,17 t/ha).
7. **Le « renouvelable » togolais est du bois de feu.** 75,1 % d'énergie finale
   renouvelable pour 11,9 % d'accès à une cuisson propre : l'indicateur de suivi
   officiel se dégradera quand la situation s'améliorera.

Et, pour l'action : **neuf forêts concentrent la priorité.** Sur 53 forêts
classées, neuf restent dans le top 10 quelle que soit la pondération testée — le
classement de tête est un résultat des données, pas un choix d'analyste.

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
│       ├── cuisson.py            objectif 2 — ménages, forêts et usage des sols
│       ├── emissions.py          objectifs 3 et 4 — GES et climat
│       ├── priorisation.py       objectif 5 — carte des 53 forêts
│       ├── plan.py               objectif 6 — recommandations
│       └── donnees.py            méthode, audit qualité et limites
│
├── src/                          pipeline reproductible
│   ├── build_gold.py             bronze -> gold, avec journal des traitements
│   ├── verify.py                 audit : recalcul indépendant depuis data/raw/
│   ├── make_figures.py           figures SVG du rapport
│   ├── make_report.py            assemblage du rapport + contrôle de cohérence
│   └── make_pptx.py              présentation 10 diapositives
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

Ce script recalcule 62 chiffres clés **directement depuis `data/raw/`**, avec un
code écrit indépendamment du pipeline (lecture `csv` standard, aucune fonction
partagée), et les compare à ce qui est publié. Il vérifie aussi les **identités
comptables** sur lesquelles reposent les conclusions — que la somme des deux
effets reconstitue bien la variation du stock de ruraux sans électricité, que le
déficit annuel de raccordement multiplié par dix redonne bien la hausse
observée sur la décennie. Il sort en erreur au moindre écart.
Dernier passage : **62/62 conformes**.

Deux garde-fous complètent cet audit :

- `src/build_gold.py` **audite automatiquement les 32 séries** (valeurs
  distinctes, pentes distinctes, queue gelée) et publie le verdict dans la page
  « Données » du tableau de bord. Six séries portent un défaut structurel qui
  change la lecture, et le tableau de bord en tient compte explicitement ;
- `src/make_report.py` **refuse de produire le rapport** si l'un des 34 chiffres
  directeurs qu'il contient ne correspond plus au fichier gold : le texte rédigé
  à la main ne peut donc pas dériver silencieusement des données.

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
- **couvert forestier lu par régime, pas en moyenne** : la série n'a que trois
  mesures indépendantes, la moyenne 1990-2021 mélange deux rythmes ;
- **comparaison d'usage des sols arrêtée à 2013** : la surface agricole est gelée
  à la même valeur au-delà ;
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

# Sources, méthodologie et traitements

Ce document décrit ce qui entre dans le tableau de bord, ce qui en a été écarté,
et pourquoi. Il est le pendant technique du rapport.

---

## 1. Les six jeux de données du défi

| Fichier (`data/raw/`) | Contenu | Maille | Usage dans le tableau de bord |
|---|---|---|---|
| `indicators-tgo.csv` | Indicateurs Banque Mondiale, Togo | National, annuel | Accès, cuisson, forêt, population, fiabilité, santé |
| `energies-renouvelables-combustibles-et-dechets-de-lenergie-totale-.csv` | Part des renouvelables et déchets dans l'énergie totale | National, annuel | Page « Cuisson & forêts » — le piège du renouvelable |
| `emissions-de-dioxyde-de-carbone-co2-du-secteur-de-lenergie-mt-co2e-.csv` | CO₂ du secteur énergie | National, annuel (1970-2022) | Page « Émissions & climat » — série longue |
| `observationdata-xorttne.csv` | Inventaire GES 2018, secteur × gaz | National, ponctuel | Page « Émissions & climat » — bilan sectoriel et par gaz |
| `observationdata-yvlucze.csv` | Températures mensuelles, 10 stations, 2013-2019 | Ville × mois | Page « Émissions & climat » — gradient et saisonnalité ; composante « stress thermique » de l'indice |
| `file-zones-protegees-forets-classees-*.csv` | 53 forêts classées et zones protégées, géométries WKT | Polygone (EPSG:4326) | Page « Où agir » — carte et indice de vulnérabilité |
| `zones-protegees-forets-classees.csv` | Dictionnaire des champs du fichier forestier | — | Contrôle de cohérence des colonnes |

**Reconstruction complète** — un seul script, chemins relatifs, exécutable
sous Windows comme sous Linux :

```bash
python src/build_gold.py
```

Il écrit `data/gold/` (données analytiques) et
`data/gold/journal_construction.txt` (journal détaillé de tous les
traitements et de tous les chiffres clés recalculés).

---

## 2. Le seul apport externe

Les **coordonnées géographiques des 10 stations météo** et leur rattachement
administratif (région, préfecture) ne figurent dans aucun fichier du défi.
Elles ont été ajoutées à partir de sources géographiques publiques (chefs-lieux
togolais) et sont listées en clair dans `src/build_gold.py`.

C'est le **seul** enrichissement extérieur du travail. Il est indispensable :
sans lui, aucun croisement n'est possible entre le climat (10 villes) et
l'espace forestier (53 polygones), et l'analyse resterait purement nationale.

Les facteurs de PRG utilisés pour la lecture en équivalent CO₂
(CH₄ × 28, N₂O × 265) sont les valeurs AR5 du GIEC à 100 ans ; ils sont affichés
dans l'interface au moment où ils s'appliquent.

---

## 3. Correctifs qualité appliqués aux données

| Problème constaté | Traitement retenu | Pourquoi pas autrement |
|---|---|---|
| Ligne de tags HXL en 2ᵉ ligne de `indicators-tgo.csv` | Filtrée sur `Country ISO3 == "TGO"` | Une lecture naïve produit une ligne fantôme et casse les conversions numériques |
| **22 % de doublons stricts** dans le fichier Banque Mondiale | Déduplication sur `(Indicator Code, Year)` | Sans cela, les moyennes et les comptages sont biaisés |
| Précipitations `AG.LND.PRCP.MM` : valeur constante répétée sur toutes les années | **Écartées** de toute analyse temporelle | Les tracer produirait une fausse tendance plate, présentée comme un résultat |
| Températures au **degré entier** | Gradient spatial exploité, **tendance sur 7 ans non exploitée** | L'écart entre stations (6,4 °C) dépasse largement la précision de mesure ; la dérive annuelle, non |
| **16 forêts sur 53** ont un polygone < 10 ha | Flag « surface incertaine » visible + valeur **neutre (0,5)** dans l'indice + filtre utilisateur | Une surface de 5 ha est incompatible avec le statut de forêt classée : c'est une numérisation partielle, pas une petite forêt. Les exclure d'office reviendrait à décider à la place du décideur |
| Année de classement absente pour **17 forêts** (« Nsp », « Nps », « Jadis ») | Variable **écartée du score**, conservée en descriptif, **aucune imputation** | Imputer une date de classement inventerait de l'information sur un tiers de l'échantillon |
| Inventaire GES : le total publié additionne des **masses** de gaz différents | Les deux lectures sont proposées (masse brute publiée / équivalent CO₂), avec avertissement | Ne présenter que l'une des deux masquerait que la hiérarchie des secteurs dépend d'une convention |
| Coquille dans le libellé source (« mnooxydes d'azote ») | Normalisée en `N2O` à la lecture | — |
| Surfaces et distances calculées en degrés décimaux | Reprojection **UTM 31N (EPSG:32631)** avant tout calcul métrique | Une aire calculée en degrés carrés n'a pas de sens physique |
| Couvert forestier `AG.LND.FRST.K2` : 32 points annuels mais **2 pentes distinctes seulement** — signature d'une interpolation linéaire entre points de référence FAO | Lecture **par régime** : 9 320 ha/an jusqu'en 2000, **2 960 ha/an depuis**. La moyenne 1990-2021 n'est plus employée nulle part | Diviser la perte totale par le nombre d'années donne un chiffre qui ne correspond à aucune année réelle, surestime de 70 % la perte d'aujourd'hui et efface un ralentissement d'un facteur trois |

---

## 4. L'indice de vulnérabilité forestière

Score sur 100 par forêt, combinaison linéaire de trois composantes normalisées
entre 0 et 1 :

| Composante | Poids de référence | Mesure | Justification |
|---|---|---|---|
| **Enclavement** | 0,40 | Distance du centroïde au pôle urbain le plus proche (km, UTM 31N) | Proxy de la dépendance locale au bois-énergie : plus une zone est loin d'une ville raccordée, moins elle a d'alternative à la biomasse |
| **Enjeu / surface** | 0,35 | Superficie du massif, **échelle logarithmique** | L'effet d'une protection est proportionnel à ce qu'elle couvre ; l'échelle log évite qu'un seul très grand massif écrase le classement |
| **Stress thermique** | 0,25 | Température maximale moyenne de la station de rattachement | Les forêts sèches du Nord sont plus exposées au stress hydrique et au feu |

**Les poids sont réglables dans le tableau de bord.** Le classement se recalcule
en direct, carte comprise : le décideur teste sa propre doctrine plutôt que
d'hériter de celle de l'analyste.

**Test de robustesse.** Cinq pondérations différentes ont été appliquées
(0,30/0,40/0,30 · 0,35/0,35/0,30 · 0,40/0,35/0,25 · 0,45/0,30/0,25 ·
0,50/0,30/0,20). **Neuf forêts restent dans le top 10 dans les cinq cas** :
la tête du classement est un résultat des données, pas un artefact de
pondération. Ces neuf massifs sont ceux qui doivent recevoir le premier budget.

---

## 5. Limites explicites

1. **Aucune maille infranationale pour l'énergie.** Ni l'électrification, ni la
   cuisson, ni les émissions ne sont disponibles en dessous du niveau national.
   Le seul croisement spatial rigoureux possible est celui construit ici :
   forêts × stations météo × éloignement urbain.
2. **La fiabilité du réseau est mesurée sur les entreprises**
   (Enterprise Surveys), pas sur les ménages, et sur deux vagues seulement
   (2009 et 2016). C'est la meilleure approximation disponible dans les données
   du défi, et plutôt un minorant de ce que subissent les zones rurales.
3. **Le lien cuisson → déforestation est corrélatif.** Aucun fichier ne mesure
   les prélèvements de bois-énergie. Le simulateur rend donc l'attribution
   **paramétrable** au lieu de la fixer arbitrairement.
4. **L'exposition aux PM2,5 est ambiante**, pas intérieure : elle sous-estime
   l'exposition réelle des ménages qui cuisinent au bois.
5. **Aucun coût, aucun budget** dans les six jeux de données. Les
   recommandations portent donc sur des priorités et des cibles physiques, pas
   sur un plan de financement.
6. Le champ « état de la zone » du dictionnaire forestier n'est pas exporté
   dans le fichier fourni : la vulnérabilité est construite par proxy, pas lue
   directement.

---

## 6. Analyses croisées

| Analyse | Séries croisées | Ce qu'elle établit |
|---|---|---|
| **Tapis roulant démographique** | `EG.ELC.ACCS.RU.ZS` × `SP.RUR.TOTL` | Le nombre de ruraux privés d'électricité a augmenté de 19 % pendant que le taux était multiplié par 8. Décomposition exacte en effet démographique (+1 693 547) et effet d'électrification (−1 086 596) |
| **Seuil de stagnation** | `SP.RUR.TOTL`, variation annuelle | Le volume de raccordements au-dessous duquel le stock augmente : 65 658 en 2022. Sur 2012-2022, déficit de 13 756/an, soit +137 560 personnes |
| **Régimes de déforestation** | `AG.LND.FRST.K2`, écarts successifs | La série n'a que 3 mesures indépendantes ; deux régimes de perte, 9 320 puis 2 960 ha/an |

Ces trois analyses sont recalculées par `src/verify.py` sans réutiliser une
ligne du pipeline, **identités comptables comprises**.

---

## 7. Indicateurs Banque Mondiale mobilisés

| Domaine | Codes |
|---|---|
| Accès électricité | `EG.ELC.ACCS.ZS`, `.RU.ZS`, `.UR.ZS` |
| Fiabilité du réseau | `IC.ELC.OUTG`, `IC.ELC.OUTG.ZS`, `IC.FRM.OUTG.ZS`, `IC.ELC.DURS`, `IC.ELC.TIME` |
| Cuisson propre | `EG.CFT.ACCS.ZS`, `.RU.ZS`, `.UR.ZS` |
| Combustibles de cuisson | `SG.COK.WOOD.ZS`, `SG.COK.CHCO.ZS`, `SG.COK.LPGN.ZS`, `SG.COK.ELEC.ZS` |
| Forêt | `AG.LND.FRST.ZS`, `AG.LND.FRST.K2` |
| Mix énergétique | `EG.FEC.RNEW.ZS` |
| Population | `SP.POP.TOTL`, `SP.RUR.TOTL`, `SP.URB.TOTL`, `SP.RUR.TOTL.ZS` |
| Air et santé | `EN.ATM.PM25.MC.M3`, `SH.STA.AIRP.P5` |
| Contexte | `NY.GDP.PCAP.CD` |

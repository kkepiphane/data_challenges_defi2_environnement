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
| Couvert forestier `AG.LND.FRST.K2` / `.ZS` : **32 points annuels mais seulement 3 mesures indépendantes** (les écarts d'une année à l'autre ne prennent que deux valeurs distinctes — signature d'une interpolation linéaire entre points de référence FAO) | Lecture **par régime** : 9 320 ha/an jusqu'en 2000, **2 960 ha/an depuis**. La moyenne 1990-2021 (5 011 ha/an) n'est plus utilisée comme chiffre de référence, et les simulateurs partent du régime en cours | Diviser la perte totale par le nombre d'années produit un chiffre qui ne correspond à aucune année réelle, surestime de 70 % la perte d'aujourd'hui, et efface un ralentissement d'un facteur 3 |
| Surface agricole `AG.LND.AGRI.K2` / `.ZS` et `AG.LND.ARBL.ZS` : **valeur identique répétée depuis 2013** | Comparaison forêt / agriculture **arrêtée à 2013** | Prolonger la série produirait une fausse stabilisation de l'usage des sols, présentée comme un résultat |

### Audit automatique des séries

Ces correctifs ont d'abord été trouvés à la main, puis **systématisés**. Les
32 séries qui alimentent une page du tableau de bord subissent le même test
automatique (`src/build_gold.py`, section 8.5), dont le résultat est écrit dans
`data/gold/diagnostic_national.json` et publié dans la page « Données » de
l'application. Trois questions par série :

1. **combien de valeurs distinctes ?** Une seule ⇒ la série ne porte aucune
   information temporelle (`AG.LND.PRCP.MM`) ;
2. **combien de pentes distinctes ?** Deux ou trois sur trente ans ⇒ la série est
   interpolée, et le nombre de ruptures de pente donne le nombre de mesures
   réellement indépendantes (`AG.LND.FRST.K2`) ;
3. **les dernières années sont-elles identiques ?** ⇒ queue gelée, la source a
   cessé de mettre la série à jour sans le signaler (`AG.LND.AGRI.K2`).

Résultat : **21 séries sur 32 sans réserve**, 6 portant un défaut structurel qui
change la lecture, 5 trop courtes pour autre chose qu'un contraste.

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
3. **Le lien cuisson → déforestation n'est pas mesuré.** Aucun fichier ne
   quantifie les prélèvements de bois-énergie. Ce que les données permettent, en
   revanche, c'est de mesurer le **moteur concurrent** : entre 1990 et 2013, la
   surface agricole a gagné 6 600 km² quand la forêt en perdait 1 317, soit cinq
   fois plus. Il en découle que la forêt ne peut avoir fourni que 20 % de
   l'expansion agricole, et que celle-ci suffit à elle seule à absorber tout le
   recul forestier — une attribution majoritaire au bois-énergie n'est donc pas
   soutenable. Le simulateur rend l'attribution **paramétrable**, bornée par
   cette mesure au lieu d'être fixée arbitrairement.
4. **La série forestière ne peut pas servir d'indicateur de pilotage.** Avec
   trois mesures indépendantes en trente-deux ans, elle ne détecterait un
   retournement récent qu'au prochain inventaire de référence. D'où la
   recommandation de créer un suivi surfacique annuel par massif.
5. **Les projections en personnes supposent la population rurale constante.**
   C'est une hypothèse conservatrice : la population rurale croît encore
   (+65 658 habitants en 2022), donc l'effort réel dépasse celui affiché.
6. **L'exposition aux PM2,5 est ambiante**, pas intérieure : elle sous-estime
   l'exposition réelle des ménages qui cuisinent au bois. La mortalité
   `SH.STA.AIRP.P5` agrège pollution intérieure et extérieure, ne compte qu'un
   seul point de mesure (2019), et n'est pas imputable à la seule cuisson.
7. **Aucun coût, aucun budget** dans les six jeux de données. Les
   recommandations portent donc sur des priorités et des cibles physiques, pas
   sur un plan de financement.
8. Le champ « état de la zone » du dictionnaire forestier n'est pas exporté
   dans le fichier fourni : la vulnérabilité est construite par proxy, pas lue
   directement.

---

## 6. Indicateurs Banque Mondiale mobilisés

| Domaine | Codes |
|---|---|
| Accès électricité | `EG.ELC.ACCS.ZS`, `.RU.ZS`, `.UR.ZS` |
| Fiabilité du réseau | `IC.ELC.OUTG`, `IC.ELC.OUTG.ZS`, `IC.FRM.OUTG.ZS`, `IC.ELC.DURS`, `IC.ELC.TIME` |
| Cuisson propre | `EG.CFT.ACCS.ZS`, `.RU.ZS`, `.UR.ZS` |
| Combustibles de cuisson | `SG.COK.WOOD.ZS`, `SG.COK.CHCO.ZS`, `SG.COK.LPGN.ZS`, `SG.COK.ELEC.ZS` |
| Forêt | `AG.LND.FRST.ZS`, `AG.LND.FRST.K2` |
| Usage des sols et agriculture | `AG.LND.AGRI.K2`, `AG.LND.AGRI.ZS`, `AG.LND.ARBL.ZS`, `AG.LND.CREL.HA`, `AG.PRD.CREL.MT` |
| Mix énergétique | `EG.FEC.RNEW.ZS`, `EG.EGY.PRIM.PP.KD` |
| Population | `SP.POP.TOTL`, `SP.RUR.TOTL`, `SP.URB.TOTL`, `SP.RUR.TOTL.ZS`, `SP.POP.GROW`, `SP.URB.GROW` |
| Air et santé | `EN.ATM.PM25.MC.M3`, `SH.STA.AIRP.P5` |
| Contexte | `NY.GDP.PCAP.CD`, `NY.GDP.PCAP.KD`, `SL.AGR.EMPL.ZS`, `EN.POP.DNST` |
| Chargé mais écarté après audit | `AG.LND.PRCP.MM` — valeur unique répétée sur 61 ans ; conservé dans le pipeline uniquement pour que l'audit qualité montre pourquoi il est écarté |

### Analyses croisées construites à partir de ces séries

| Analyse | Séries croisées | Ce qu'elle établit |
|---|---|---|
| **Tapis roulant démographique** | `EG.ELC.ACCS.RU.ZS` × `SP.RUR.TOTL` | Le nombre de ruraux privés d'électricité a augmenté de 19 % pendant que le taux d'accès était multiplié par 8. Décomposition exacte en effet démographique et effet d'électrification |
| **Seuil de stagnation** | `SP.RUR.TOTL` (variation annuelle) | Le volume de raccordements annuels au-dessous duquel le stock augmente, année par année |
| **Régimes de déforestation** | `AG.LND.FRST.K2` (écarts successifs) | La série n'a que 3 mesures indépendantes ; deux régimes de perte, 9 320 puis 2 960 ha/an |
| **Usage des sols** | `AG.LND.FRST.K2` × `AG.LND.AGRI.K2` | L'expansion agricole gagne 5,0 fois ce que la forêt perd : borne haute de ce que le bois-énergie peut expliquer |
| **Extensification agricole** | `AG.LND.CREL.HA` × `AG.PRD.CREL.MT` | 46 % de la hausse de production vient de la surface, non du rendement ; +19 690 ha défrichés par an |
| **Incertitude de la trajectoire** | `EG.ELC.ACCS.RU.ZS` (moindres carrés) | Pente 0,99 pt/an, IC 95 % [0,90 ; 1,09], accès universel entre 2091 et 2106 |

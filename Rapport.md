<<<<<<< HEAD
Ce projet démontre la faisabilité technique d'un Système d'Aide à la Décision (SAD) pour la prévention des accidents dans le secteur du BTP (Vinci Construction). L'objectif est d'évaluer de manière proactive le risque d'accident grave avant le début d'une tâche. L'analyse du jeu de données OSHA (10 299 observations BTP) a mis en évidence une fuite de données majeure si les descriptions textuelles post-accident sont exploitées. Pour garantir une application strictement prédictive, le modèle final (LightGBM optimisé via Optuna) s'appuie uniquement sur des variables tabulaires disponibles _a priori_ (météo, âge, métier). Le modèle atteint un Rappel (Recall) de 64,7 % sur la classe des accidents mortels. Ce résultat valide l'architecture logicielle (déployée via un MVP Streamlit) tout en confirmant mathématiquement que les seules données environnementales sont insuffisantes pour une prédiction parfaite, nécessitant l'intégration future de données de conformité terrain.

### Chapitre 1 : Introduction et problématique

Le secteur du BTP est un environnement à haut risque où les accidents ont un coût humain inacceptable et un impact financier majeur (arrêts de chantier, pénalités). Dans ce contexte, l'objectif pour des acteurs comme Vinci Construction est de dépasser la simple conformité réglementaire pour adopter une approche proactive de la sécurité. Ce projet vise à développer un Système d'Aide à la Décision (SAD). Son but n'est pas de remplacer l'expertise humaine ou de déclencher des arrêts de chantier automatiques, mais d'évaluer la probabilité de gravité d'un accident selon des facteurs combinés (météo, tâches, équipements). L'enjeu métier est d'optimiser l'allocation des ressources de prévention sur le terrain. L'étude est réalisée sur un jeu de données de l'OSHA (États-Unis), ce qui implique des différences réglementaires avec les normes européennes. Ce modèle a donc valeur de démonstrateur de faisabilité technique.

### Chapitre 2 : Présentation et compréhension des données 

Le jeu de données exploité regroupe des rapports d'accidents du travail issus de l'OSHA (Occupational Safety and Health Administration) aux États-Unis.

- **Dimensions :** Le jeu de données comprend 53 550 observations pour 24 variables, occupant environ 9.8 MB en mémoire.
    
- **Typologie des variables :**
    
    - **Textuelles libres :** Descriptions des accidents (`abstract`, `event_keyword`).
        
    - **Météorologiques (quantitatives) :** Température (`temp`), humidité (`humidity`), vitesse du vent (`wind_speed`), pression (`pressure`).
        
    - **Catégorielles et géographiques :** État (`state_x`), codes métiers et industriels (`occ_code`, `sic_code`), type d'événement (`event_type`).
        
    - **Temporelles :** Date de l'accident (`date`).
        
- **Variable cible (Target) :** La variable à prédire est `degree_of_inj_x`. Il s'agit d'une classification de la gravité de l'accident encodée numériquement. L'analyse des fréquences révèle 5 classes : la classe 2 est majoritaire (25 972 cas), suivie de la classe 1 (20 678 cas) et de la classe 3 (6 847 cas). Les classes 0 et 4 sont statistiquement marginales (53 cas cumulés). Le dataset ne présente aucune valeur manquante sur cette variable cible.

| **Variable**               | **Type**          | **Explication et Modalités**                                                                                                                                 |
| -------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **degree_of_inj_x**        | Numérique (Cible) | Gravité de la blessure. Modalités : 1 (Mortel), 2 (Sévère/Hospitalisation), 3 (Mineur).                                                                      |
| **fatality**               | Texte             | Issue fatale. Modalité : 'X' (Décès) ou NaN. _Note : Supprimée pour éviter la fuite de données._                                                             |
| **construction**           | Numérique         | Secteur d'activité. Modalité : 1.0 (BTP) ou NaN. _Note : Utilisée comme filtre métier puis supprimée._                                                       |
| **date**                   | Datetime          | Date et heure exactes de l'accident.                                                                                                                         |
| **state_x**                | Texte             | État américain où s'est produit l'accident (ex: 'CA', 'TX'). (50+ modalités).                                                                                |
| **city_x**                 | Texte             | Ville de l'accident. (Très haute cardinalité, milliers de modalités).                                                                                        |
| **zip_x**                  | Numérique         | Code postal américain. (Très haute cardinalité).                                                                                                             |
| **sic_code**               | Numérique         | _Standard Industrial Classification_. Code de l'industrie spécifique de l'entreprise. (Haute cardinalité, 87% de valeurs manquantes sur notre sous-jeu BTP). |
| **occ_code**               | Numérique         | _Occupational Code_. Code métier de la victime (ex: charpentier, grutier). (Haute cardinalité, ~7% manquants).                                               |
| **age_x**                  | Numérique         | Âge de la victime au moment de l'accident (ex: 35, 42).                                                                                                      |
| **sex_x**                  | Texte             | Sexe de la victime. Modalités : 'M' (Masculin), 'F' (Féminin) ou NaN.                                                                                        |
| **event_type**             | Numérique         | Code normalisé par l'OSHA désignant la nature de l'événement (ex: chute de hauteur, électrisation). (15 modalités de 0 à 14).                                |
| **event_keyword**          | Texte             | Mots-clés extraits de l'accident. _Note : Variable textuelle générée après l'accident, source de fuite de données._                                          |
| **abstract / description** | Texte libre       | Résumé narratif rédigé par l'inspecteur OSHA post-accident. _Note : Source principale de fuite de données._                                                  |
| **temp / feels_like**      | Numérique         | Température réelle et ressentie au moment de l'accident (en degrés Fahrenheit ou Celsius selon l'API source).                                                |
| **pressure**               | Numérique         | Pression atmosphérique en hPa.                                                                                                                               |
| **humidity**               | Numérique         | Taux d'humidité dans l'air (%).                                                                                                                              |
| **wind_speed / wind_deg**  | Numérique         | Vitesse du vent (m/s) et direction (degrés).                                                                                                                 |
| **visibility**             | Numérique         | Distance de visibilité en mètres. (~25% de valeurs manquantes sur notre sous-jeu BTP).                                                                       |
| **clouds**                 | Numérique         | Couverture nuageuse (%).                                                                                                                                     |
| **main**                   | Texte             | Résumé météorologique global (ex: 'Clear', 'Rain', 'Snow'). (Faible cardinalité).                                                                            |

### Chapitre 3 : Exploration des données et principaux constats (Brouillon pour le rapport)


L'analyse exploratoire (EDA) a mis en évidence trois contraintes majeures dictant les choix de prétraitement :

- **Cadrage métier :** La variable `construction` indique que seulement 10 299 observations (environ 19 %) relèvent spécifiquement du secteur du BTP. Le jeu de données a été restreint à ce sous-ensemble pour garantir l'alignement avec les cas d'usage de Vinci Construction.

- **Fuite de données (Data Leakage) :** La variable `fatality`, bien qu'utile pour identifier par rétro-ingénierie la classe `1` comme celle des accidents critiques/mortels, doit être exclue des variables explicatives pour empêcher le modèle de tricher.

- **Données textuelles :** La variable `abstract` présente un taux de remplissage quasi total (99,9 %) avec une longueur médiane de 363 caractères, validant la pertinence d'une approche d'extraction de caractéristiques par le traitement du langage naturel (NLP).
   
- **Données météorologiques :** Les variables environnementales (température, vent, humidité) présentent un taux de valeurs manquantes homogène (7 %), nécessitant une imputation statistique.

### Chapitre 4 : Prétraitement et feature engineering 

Note : Ce chapitre détaille le pipeline de prétraitement initial (Phase 1). C'est la vectorisation du texte décrite ici qui a permis de diagnostiquer la fuite de données, justifiant le pivot architectural détaillé au Chapitre 5.

Cette section détaille le pipeline de prétraitement initial (Phase 1). C'est ce pipeline qui a permis de diagnostiquer la fuite de données détaillée au Chapitre 5. Le nettoyage du jeu de données BTP (10 299 observations) a impliqué plusieurs décisions structurelles :

- **Filtrage des variables :** La variable `sic_code` (87 % de valeurs manquantes) a été supprimée, son imputation étant statistiquement invalide.

- **Cible (Target) :** Le filtrage métier a naturellement éliminé les classes aberrantes (0 et 4). Le problème est formulé comme une classification multiclasse stricte : Classe 1 (Mortel), Classe 2 (Sévère), Classe 3 (Mineur).

- **Prévention du Data Leakage :** La séparation des données (Train/Test Split, 80/20) a été effectuée de manière stratifiée avant toute imputation.

- **Encodage et Imputation :** Les variables numériques ont été imputées par la médiane et standardisées. Les variables catégorielles ont été imputées par la valeur la plus fréquente et transformées via One-Hot Encoding.

- **Traitement du texte (NLP) :** La variable `abstract` a été vectorisée à l'aide d'un modèle d'embedding (Sentence-Transformers : `all-MiniLM-L6-v2`), exploitant l'accélération matérielle. Ces vecteurs denses (384 dimensions) ont été concaténés aux données tabulaires, aboutissant à un jeu d'entraînement final de 8 239 observations pour 3 429 caractéristiques.

### Chapitre 5  : Méthodologie de modélisation 

**Pivot architectural : Traitement de la fuite de données (Data Leakage) et création de l'Option B**

La première itération du modèle a mis en évidence une fuite de données critique liée aux variables textuelles (`abstract`, `event_keyword`). Ces informations étant rédigées par l'OSHA _après_ l'accident, leur utilisation biaise mathématiquement l'évaluation et rend le modèle inopérant pour un usage anticipatif (avant le début de la tâche de chantier).

Pour répondre strictement au besoin métier d'anticipation, l'architecture a été révisée :

1. **Suppression des données post-accident :** L'intégralité des variables narratives a été retirée.
    
2. **Restriction aux données a priori :** Le modèle n'exploite que les paramètres initiaux (météorologie, métier de l'intervenant, âge, sexe).
    
3. **Cible :** La cible a été maintenue sur ses 3 classes d'origine (1 : Mortel, 2 : Sévère, 3 : Mineur).
    

**Résultats de la Baseline sans fuite de données :** L'entraînement d'une Régression Logistique sur ces données strictement tabulaires a entraîné une chute drastique des performances. La justesse globale (Accuracy) s'établit à 40 %, et le Rappel (Recall) sur la classe prioritaire (Mortel) tombe à 52 %. Ce résultat valide la suppression de la fuite de données et met en évidence une réalité métier : les seules conditions environnementales et démographiques ne possèdent pas un pouvoir prédictif linéaire suffisant pour déterminer la gravité exacte d'un accident.

### Chapitre 6 : Résultats et limites de l'approche tabulaire stricte

**Bilan technique et décision d'ingénierie : Le choix de la robustesse** 

En apparence, la transition d'un modèle performant à 92 % d'Accuracy (Option A) vers un modèle à 54 % (Option B) semble être une régression. D'un point de vue de l'ingénierie logicielle, c'est l'inverse. Le score de 92 % reposait sur une fuite de données (l'utilisation de rapports rédigés après l'accident), rendant le modèle mathématiquement incapable de fonctionner en conditions réelles avant le début d'un chantier. Nous avons volontairement dégradé la performance statistique pour garantir la viabilité opérationnelle. Le score de 54 % (et 64,7 % de Recall sur les cas mortels) représente la limite mathématique stricte de ce qu'il est possible d'anticiper avec les seules variables initiales (météo, âge, métier) de la base OSHA. C'est le prix d'un modèle intègre, sans fuite de données, et déployable.
Afin de garantir une application strictement prédictive (avant le début de la tâche), les variables textuelles rédigées post-accident ont été exclues pour supprimer toute fuite de données (Data Leakage). Les modèles ont été entraînés uniquement sur les conditions initiales : paramètres météorologiques, âge, sexe et code métier.

Les résultats démontrent une faible capacité prédictive. La Régression Logistique obtient un Rappel (Recall) de 52 % sur la classe critique (Accident mortel). L'utilisation d'un algorithme arborescent non linéaire (LightGBM) permet d'augmenter ce Rappel à 59 % et la justesse globale (Accuracy) à 54 %.

**Conclusion métier :** D'un point de vue statistique, ce résultat prouve que les seules variables environnementales et démographiques ne contiennent pas un signal mathématique suffisant pour discriminer la gravité d'un accident. Les paramètres manquants (respect des normes de sécurité, état de fatigue, défaillance matérielle soudaine) sont les véritables facteurs déterminants, mais ils sont absents des données structurées de l'OSHA. L'anticipation pure de la gravité sur cette base de données est donc techniquement non viable pour un déploiement en production.

**Optimisation des hyperparamètres (Optuna) et Modèle Final :** Afin de maximiser l'extraction du signal prédictif des données tabulaires, une optimisation bayésienne des hyperparamètres a été réalisée via le framework Optuna (50 itérations). La fonction objectif a été configurée pour maximiser spécifiquement le Rappel (Recall) de la classe 1 (Accident mortel). Le modèle LightGBM final (n_estimators=158, learning_rate=0.015, max_depth=11) atteint un Rappel de **64,7 %** sur la classe critique. Ce gain de 5 points par rapport aux paramètres par défaut représente la performance maximale atteignable sur ce jeu de données sans recourir à la fuite de données textuelles. Ce modèle est sauvegardé pour le déploiement du démonstrateur proactif (SAD).
![[Capture d’écran du 2026-08-14 13-04-08.png]]
![[Pasted image 20260814130144.png]]

### Chapitre 7 : Interprétabilité et analyse des erreurs (Brouillon final pour le rapport)

La suppression des variables textuelles (NLP) au profit d'une architecture strictement tabulaire a permis de restaurer une transparence totale du modèle. Contrairement aux embeddings denses ininterprétables, l'algorithme repose désormais sur des variables physiques et démographiques lisibles.

L'analyse de l'importance des variables via la méthode SHAP (SHapley Additive exPlanations) révèle la mécanique de décision du modèle LightGBM pour la prédiction des accidents mortels (Classe 1) :

- **Prédominance des facteurs environnementaux :** Les variables météorologiques continues (température, pression atmosphérique, taux d'humidité) constituent les axes principaux de scission des arbres de décision.
    
- **Facteurs démographiques et métiers :** L'âge de l'intervenant (`age_x`) et certains codes métiers spécifiques (`occ_code`) émergent comme des facteurs secondaires modulant le risque.
    

**Analyse diagnostique :** Bien que le modèle soit désormais 100 % explicable, le diagnostic SHAP met en évidence la faiblesse du signal prédictif (confirmant les 54 % d'Accuracy). Les variables météorologiques, bien qu'utilisées mathématiquement par l'algorithme pour séparer les classes, ne possèdent pas de lien de causalité direct et exclusif avec la mortalité d'un accident. L'outil effectue des corrélations de second plan en l'absence des facteurs de risque primaires (état des équipements, port des EPI). Ce compromis est un standard en ingénierie Machine Learning : nous avons sacrifié la performance artificielle (biaisée par la fuite de données) pour obtenir une explicabilité totale et stricte de la réalité du jeu de données disponible.![[shap_summary_option_b.png]]

### Chapitre 8 : Démonstrateurs et traduction opérationnelle


**Traduction opérationnelle et ergonomie de l'interface** Pour rendre l'outil exploitable par un chef de chantier, les variables d'entrée ont été traduites en langage naturel. Notamment, la variable `occ_code` (composée de codes numériques OSHA opaques) a été couplée à un dictionnaire de mappage dans l'interface. L'utilisateur sélectionne l'intitulé du métier en clair (ex: "Charpentier"), et l'application se charge de transmettre le code correspondant au pipeline de prétraitement pour l'inférence, masquant ainsi la complexité mathématique à l'utilisateur final.

### Chapitre 9 : Limites, conclusions métier et perspectives

**9.1. Limites inhérentes au jeu de données OSHA (Biais de sélection)** 

Le développement des modèles strictement proactifs (Option B) a mis en évidence une limite structurelle de la base de données OSHA. Cette base recense quasi exclusivement des incidents avérés et possède un taux de déclaration très faible pour les accidents mineurs (7 % du jeu de données). Par conséquent, le modèle n'apprend pas à différencier une "situation normale" d'une "situation dangereuse", mais tente de discriminer la gravité d'un accident en sachant que celui-ci a déjà eu lieu. De plus, les variables purement environnementales et démographiques s'avèrent insuffisantes pour établir une prédiction linéaire ou arborescente hautement fiable de la gravité.

**9.2. Perspective 1 : L'automatisation a posteriori par le NLP** 

La variable textuelle `abstract` contient un signal mathématique extrêmement fort (comme prouvé lors de la modélisation initiale). Bien que son usage génère une fuite de données pour une application de prévention, cette donnée pourrait être exploitée pour un autre cas d'usage : la classification automatisée de documents. L'entraînement d'un modèle de Deep Learning (Sentence-Transformers) sur ces descriptions permettrait d'automatiser le tri administratif et la catégorisation des rapports post-accident reçus par Vinci ou l'OSHA, réduisant ainsi le temps de traitement manuel.

**9.3. Perspective 2 : Amélioration du modèle proactif (Système d'Aide à la Décision)** 

Pour que le modèle d'anticipation (Option B) atteigne un niveau de performance compatible avec un déploiement sur les chantiers Vinci, une nouvelle stratégie de collecte de données est requise. L'algorithme doit être alimenté par des variables opérationnelles dynamiques telles que :

- Le taux de conformité du port des EPI (Équipements de Protection Individuelle) avant la tâche.
    
- Le niveau de fatigue déclaré ou la durée du cycle de travail de l'intervenant.
    
- L'état de certification ou de maintenance des équipements utilisés (ex: échafaudages, grues). L'intégration de ces données ciblées permettra de transformer le modèle tabulaire actuel en un véritable outil de prévention proactif.

### Chapitre 10 : Conclusion générale 

**Chapitre 10 : Conclusion générale**

Ce projet démontre la faisabilité technique du développement et du déploiement d'un Système d'Aide à la Décision (SAD) pour la prévention des risques dans le BTP. Le pipeline d'ingénierie complet a été validé : de l'extraction des données brutes à la mise en production d'une interface utilisateur (MVP) sous Streamlit, en passant par l'optimisation bayésienne d'un modèle de Gradient Boosting (LightGBM) et l'analyse d'explicabilité (SHAP).

Cependant, la viabilité opérationnelle de l'outil se heurte aux limites intrinsèques du jeu de données OSHA. L'étude prouve que les seules variables environnementales et démographiques ne contiennent pas le signal mathématique suffisant pour anticiper avec une haute fiabilité la gravité d'un accident (Rappel maximal de 64,7 % sur la classe mortelle). Le MVP répond à la problématique de départ en fournissant l'architecture logicielle requise, mais confirme que le déploiement réel chez Vinci Construction nécessitera l'ingestion de données de terrain plus granulaires (conformité EPI, fatigue, maintenance) pour que les prédictions atteignent le standard industriel attendu.

### Chapitre 11 : Difficultés rencontrées

**Chapitre 11 : Difficultés rencontrées et solutions apportées**

Tout au long du cycle de vie de ce projet, plusieurs obstacles techniques et méthodologiques ont nécessité des ajustements d'architecture :

1. **Fuite de données sémantique (Data Leakage) :**
 
- _Problème :_ La première itération du modèle exploitait les descriptions textuelles via un modèle d'embedding (Sentence-Transformers). Les scores obtenus étaient anormalement élevés (94 % de Rappel). L'analyse de l'importance des variables a révélé que le modèle s'appuyait sur le champ lexical post-accident.

- _Solution :_ Pivot architectural immédiat (Création de l'Option B). Les variables textuelles ont été exclues pour imposer un cadre strictement proactif, basculant l'ingénierie vers une optimisation maximale des données tabulaires restreintes.

2. **Déséquilibre extrême des classes et biais de sélection :**

- _Problème :_ Le jeu de données présentait une sous-représentation massive des accidents mineurs (7 %) par rapport aux accidents graves/mortels (92 %).

- _Solution :_ Rétablissement des 3 classes originelles de l'OSHA, utilisation de l'hyperparamètre `class_weight='balanced'` dans LightGBM, et optimisation bayésienne (Optuna) configurée pour maximiser spécifiquement le Rappel de la classe 1 afin de réduire les faux négatifs.

3. **Gestion stricte des types dans les pipelines Scikit-Learn :**

- _Problème :_ Lors du prétraitement tabulaire, l'imputation de variables catégorielles (contenant à la fois des chaînes de caractères et des valeurs numériques flottantes comme les codes métiers) a provoqué un échec du `OneHotEncoder` lors du tri mathématique des modalités.

- _Solution :_ Forçage explicite du typage en chaîne de caractères (`astype(str)`) pour l'ensemble des variables catégorielles en amont du `ColumnTransformer`, garantissant la stabilité du pipeline lors de l'inférence.

4. **Lisibilité de l'interface utilisateur (MVP) :**

- _Problème :_ Les codes métiers de l'OSHA (ex: 567.0) utilisés par le modèle mathématique sont illisibles pour un décideur métier utilisant l'interface Streamlit.
   
- _Solution :_ Création d'un dictionnaire de mappage bidirectionnel dans le code front-end de l'application, permettant à l'utilisateur de sélectionner des intitulés en langage naturel tout en transmettant les codes exacts au pipeline d'inférence.
=======
Ce projet démontre la faisabilité technique d'un Système d'Aide à la Décision (SAD) pour la prévention des accidents dans le secteur du BTP (Vinci Construction). L'objectif est d'évaluer de manière proactive le risque d'accident grave avant le début d'une tâche. L'analyse du jeu de données OSHA (10 299 observations BTP) a mis en évidence une fuite de données majeure si les descriptions textuelles post-accident sont exploitées. Pour garantir une application strictement prédictive, le modèle final (LightGBM optimisé via Optuna) s'appuie uniquement sur des variables tabulaires disponibles _a priori_ (météo, âge, métier). Le modèle atteint un Rappel (Recall) de 64,7 % sur la classe des accidents mortels. Ce résultat valide l'architecture logicielle (déployée via un MVP Streamlit) tout en confirmant mathématiquement que les seules données environnementales sont insuffisantes pour une prédiction parfaite, nécessitant l'intégration future de données de conformité terrain.
### Chapitre 1 : Introduction et problématique

Le secteur du BTP est un environnement à haut risque où les accidents ont un coût humain inacceptable et un impact financier majeur (arrêts de chantier, pénalités). Dans ce contexte, l'objectif pour des acteurs comme Vinci Construction est de dépasser la simple conformité réglementaire pour adopter une approche proactive de la sécurité. Ce projet vise à développer un Système d'Aide à la Décision (SAD). Son but n'est pas de remplacer l'expertise humaine ou de déclencher des arrêts de chantier automatiques, mais d'évaluer la probabilité de gravité d'un accident selon des facteurs combinés (météo, tâches, équipements). L'enjeu métier est d'optimiser l'allocation des ressources de prévention sur le terrain. L'étude est réalisée sur un jeu de données de l'OSHA (États-Unis), ce qui implique des différences réglementaires avec les normes européennes. Ce modèle a donc valeur de démonstrateur de faisabilité technique.

### Chapitre 2 : Présentation et compréhension des données 

Le jeu de données exploité regroupe des rapports d'accidents du travail issus de l'OSHA (Occupational Safety and Health Administration) aux États-Unis.

- **Dimensions :** Le jeu de données comprend 53 550 observations pour 24 variables, occupant environ 9.8 MB en mémoire.
    
- **Typologie des variables :**
    
    - **Textuelles libres :** Descriptions des accidents (`abstract`, `event_keyword`).
        
    - **Météorologiques (quantitatives) :** Température (`temp`), humidité (`humidity`), vitesse du vent (`wind_speed`), pression (`pressure`).
        
    - **Catégorielles et géographiques :** État (`state_x`), codes métiers et industriels (`occ_code`, `sic_code`), type d'événement (`event_type`).
        
    - **Temporelles :** Date de l'accident (`date`).
        
- **Variable cible (Target) :** La variable à prédire est `degree_of_inj_x`. Il s'agit d'une classification de la gravité de l'accident encodée numériquement. L'analyse des fréquences révèle 5 classes : la classe 2 est majoritaire (25 972 cas), suivie de la classe 1 (20 678 cas) et de la classe 3 (6 847 cas). Les classes 0 et 4 sont statistiquement marginales (53 cas cumulés). Le dataset ne présente aucune valeur manquante sur cette variable cible.

| **Variable**               | **Type**          | **Explication et Modalités**                                                                                                                                 |
| -------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **degree_of_inj_x**        | Numérique (Cible) | Gravité de la blessure. Modalités : 1 (Mortel), 2 (Sévère/Hospitalisation), 3 (Mineur).                                                                      |
| **fatality**               | Texte             | Issue fatale. Modalité : 'X' (Décès) ou NaN. _Note : Supprimée pour éviter la fuite de données._                                                             |
| **construction**           | Numérique         | Secteur d'activité. Modalité : 1.0 (BTP) ou NaN. _Note : Utilisée comme filtre métier puis supprimée._                                                       |
| **date**                   | Datetime          | Date et heure exactes de l'accident.                                                                                                                         |
| **state_x**                | Texte             | État américain où s'est produit l'accident (ex: 'CA', 'TX'). (50+ modalités).                                                                                |
| **city_x**                 | Texte             | Ville de l'accident. (Très haute cardinalité, milliers de modalités).                                                                                        |
| **zip_x**                  | Numérique         | Code postal américain. (Très haute cardinalité).                                                                                                             |
| **sic_code**               | Numérique         | _Standard Industrial Classification_. Code de l'industrie spécifique de l'entreprise. (Haute cardinalité, 87% de valeurs manquantes sur notre sous-jeu BTP). |
| **occ_code**               | Numérique         | _Occupational Code_. Code métier de la victime (ex: charpentier, grutier). (Haute cardinalité, ~7% manquants).                                               |
| **age_x**                  | Numérique         | Âge de la victime au moment de l'accident (ex: 35, 42).                                                                                                      |
| **sex_x**                  | Texte             | Sexe de la victime. Modalités : 'M' (Masculin), 'F' (Féminin) ou NaN.                                                                                        |
| **event_type**             | Numérique         | Code normalisé par l'OSHA désignant la nature de l'événement (ex: chute de hauteur, électrisation). (15 modalités de 0 à 14).                                |
| **event_keyword**          | Texte             | Mots-clés extraits de l'accident. _Note : Variable textuelle générée après l'accident, source de fuite de données._                                          |
| **abstract / description** | Texte libre       | Résumé narratif rédigé par l'inspecteur OSHA post-accident. _Note : Source principale de fuite de données._                                                  |
| **temp / feels_like**      | Numérique         | Température réelle et ressentie au moment de l'accident (en degrés Fahrenheit ou Celsius selon l'API source).                                                |
| **pressure**               | Numérique         | Pression atmosphérique en hPa.                                                                                                                               |
| **humidity**               | Numérique         | Taux d'humidité dans l'air (%).                                                                                                                              |
| **wind_speed / wind_deg**  | Numérique         | Vitesse du vent (m/s) et direction (degrés).                                                                                                                 |
| **visibility**             | Numérique         | Distance de visibilité en mètres. (~25% de valeurs manquantes sur notre sous-jeu BTP).                                                                       |
| **clouds**                 | Numérique         | Couverture nuageuse (%).                                                                                                                                     |
| **main**                   | Texte             | Résumé météorologique global (ex: 'Clear', 'Rain', 'Snow'). (Faible cardinalité).                                                                            |

### Chapitre 3 : Exploration des données et principaux constats (Brouillon pour le rapport)


L'analyse exploratoire (EDA) a mis en évidence trois contraintes majeures dictant les choix de prétraitement :

- **Cadrage métier :** La variable `construction` indique que seulement 10 299 observations (environ 19 %) relèvent spécifiquement du secteur du BTP. Le jeu de données a été restreint à ce sous-ensemble pour garantir l'alignement avec les cas d'usage de Vinci Construction.

- **Fuite de données (Data Leakage) :** La variable `fatality`, bien qu'utile pour identifier par rétro-ingénierie la classe `1` comme celle des accidents critiques/mortels, doit être exclue des variables explicatives pour empêcher le modèle de tricher.

- **Données textuelles :** La variable `abstract` présente un taux de remplissage quasi total (99,9 %) avec une longueur médiane de 363 caractères, validant la pertinence d'une approche d'extraction de caractéristiques par le traitement du langage naturel (NLP).
   
- **Données météorologiques :** Les variables environnementales (température, vent, humidité) présentent un taux de valeurs manquantes homogène (7 %), nécessitant une imputation statistique.

### Chapitre 4 : Prétraitement et feature engineering 

Note : Ce chapitre détaille le pipeline de prétraitement initial (Phase 1). C'est la vectorisation du texte décrite ici qui a permis de diagnostiquer la fuite de données, justifiant le pivot architectural détaillé au Chapitre 5.

Cette section détaille le pipeline de prétraitement initial (Phase 1). C'est ce pipeline qui a permis de diagnostiquer la fuite de données détaillée au Chapitre 5. Le nettoyage du jeu de données BTP (10 299 observations) a impliqué plusieurs décisions structurelles :

- **Filtrage des variables :** La variable `sic_code` (87 % de valeurs manquantes) a été supprimée, son imputation étant statistiquement invalide.

- **Cible (Target) :** Le filtrage métier a naturellement éliminé les classes aberrantes (0 et 4). Le problème est formulé comme une classification multiclasse stricte : Classe 1 (Mortel), Classe 2 (Sévère), Classe 3 (Mineur).

- **Prévention du Data Leakage :** La séparation des données (Train/Test Split, 80/20) a été effectuée de manière stratifiée avant toute imputation.

- **Encodage et Imputation :** Les variables numériques ont été imputées par la médiane et standardisées. Les variables catégorielles ont été imputées par la valeur la plus fréquente et transformées via One-Hot Encoding.

- **Traitement du texte (NLP) :** La variable `abstract` a été vectorisée à l'aide d'un modèle d'embedding (Sentence-Transformers : `all-MiniLM-L6-v2`), exploitant l'accélération matérielle. Ces vecteurs denses (384 dimensions) ont été concaténés aux données tabulaires, aboutissant à un jeu d'entraînement final de 8 239 observations pour 3 429 caractéristiques.

### Chapitre 5  : Méthodologie de modélisation 

**Pivot architectural : Traitement de la fuite de données (Data Leakage) et création de l'Option B**

La première itération du modèle a mis en évidence une fuite de données critique liée aux variables textuelles (`abstract`, `event_keyword`). Ces informations étant rédigées par l'OSHA _après_ l'accident, leur utilisation biaise mathématiquement l'évaluation et rend le modèle inopérant pour un usage anticipatif (avant le début de la tâche de chantier).

Pour répondre strictement au besoin métier d'anticipation, l'architecture a été révisée :

1. **Suppression des données post-accident :** L'intégralité des variables narratives a été retirée.
    
2. **Restriction aux données a priori :** Le modèle n'exploite que les paramètres initiaux (météorologie, métier de l'intervenant, âge, sexe).
    
3. **Cible :** La cible a été maintenue sur ses 3 classes d'origine (1 : Mortel, 2 : Sévère, 3 : Mineur).
    

**Résultats de la Baseline sans fuite de données :** L'entraînement d'une Régression Logistique sur ces données strictement tabulaires a entraîné une chute drastique des performances. La justesse globale (Accuracy) s'établit à 40 %, et le Rappel (Recall) sur la classe prioritaire (Mortel) tombe à 52 %. Ce résultat valide la suppression de la fuite de données et met en évidence une réalité métier : les seules conditions environnementales et démographiques ne possèdent pas un pouvoir prédictif linéaire suffisant pour déterminer la gravité exacte d'un accident.

### Chapitre 6 : Résultats et limites de l'approche tabulaire stricte

**Bilan technique et décision d'ingénierie : Le choix de la robustesse** 

En apparence, la transition d'un modèle performant à 92 % d'Accuracy (Option A) vers un modèle à 54 % (Option B) semble être une régression. D'un point de vue de l'ingénierie logicielle, c'est l'inverse. Le score de 92 % reposait sur une fuite de données (l'utilisation de rapports rédigés après l'accident), rendant le modèle mathématiquement incapable de fonctionner en conditions réelles avant le début d'un chantier. Nous avons volontairement dégradé la performance statistique pour garantir la viabilité opérationnelle. Le score de 54 % (et 64,7 % de Recall sur les cas mortels) représente la limite mathématique stricte de ce qu'il est possible d'anticiper avec les seules variables initiales (météo, âge, métier) de la base OSHA. C'est le prix d'un modèle intègre, sans fuite de données, et déployable.
Afin de garantir une application strictement prédictive (avant le début de la tâche), les variables textuelles rédigées post-accident ont été exclues pour supprimer toute fuite de données (Data Leakage). Les modèles ont été entraînés uniquement sur les conditions initiales : paramètres météorologiques, âge, sexe et code métier.

Les résultats démontrent une faible capacité prédictive. La Régression Logistique obtient un Rappel (Recall) de 52 % sur la classe critique (Accident mortel). L'utilisation d'un algorithme arborescent non linéaire (LightGBM) permet d'augmenter ce Rappel à 59 % et la justesse globale (Accuracy) à 54 %.

**Conclusion métier :** D'un point de vue statistique, ce résultat prouve que les seules variables environnementales et démographiques ne contiennent pas un signal mathématique suffisant pour discriminer la gravité d'un accident. Les paramètres manquants (respect des normes de sécurité, état de fatigue, défaillance matérielle soudaine) sont les véritables facteurs déterminants, mais ils sont absents des données structurées de l'OSHA. L'anticipation pure de la gravité sur cette base de données est donc techniquement non viable pour un déploiement en production.

**Optimisation des hyperparamètres (Optuna) et Modèle Final :** Afin de maximiser l'extraction du signal prédictif des données tabulaires, une optimisation bayésienne des hyperparamètres a été réalisée via le framework Optuna (50 itérations). La fonction objectif a été configurée pour maximiser spécifiquement le Rappel (Recall) de la classe 1 (Accident mortel). Le modèle LightGBM final (n_estimators=158, learning_rate=0.015, max_depth=11) atteint un Rappel de **64,7 %** sur la classe critique. Ce gain de 5 points par rapport aux paramètres par défaut représente la performance maximale atteignable sur ce jeu de données sans recourir à la fuite de données textuelles. Ce modèle est sauvegardé pour le déploiement du démonstrateur proactif (SAD).
![[Capture d’écran du 2026-08-14 13-04-08.png]]
![[Pasted image 20260814130144.png]]

### Chapitre 7 : Interprétabilité et analyse des erreurs (Brouillon final pour le rapport)

La suppression des variables textuelles (NLP) au profit d'une architecture strictement tabulaire a permis de restaurer une transparence totale du modèle. Contrairement aux embeddings denses ininterprétables, l'algorithme repose désormais sur des variables physiques et démographiques lisibles.

L'analyse de l'importance des variables via la méthode SHAP (SHapley Additive exPlanations) révèle la mécanique de décision du modèle LightGBM pour la prédiction des accidents mortels (Classe 1) :

- **Prédominance des facteurs environnementaux :** Les variables météorologiques continues (température, pression atmosphérique, taux d'humidité) constituent les axes principaux de scission des arbres de décision.
    
- **Facteurs démographiques et métiers :** L'âge de l'intervenant (`age_x`) et certains codes métiers spécifiques (`occ_code`) émergent comme des facteurs secondaires modulant le risque.
    

**Analyse diagnostique :** Bien que le modèle soit désormais 100 % explicable, le diagnostic SHAP met en évidence la faiblesse du signal prédictif (confirmant les 54 % d'Accuracy). Les variables météorologiques, bien qu'utilisées mathématiquement par l'algorithme pour séparer les classes, ne possèdent pas de lien de causalité direct et exclusif avec la mortalité d'un accident. L'outil effectue des corrélations de second plan en l'absence des facteurs de risque primaires (état des équipements, port des EPI). Ce compromis est un standard en ingénierie Machine Learning : nous avons sacrifié la performance artificielle (biaisée par la fuite de données) pour obtenir une explicabilité totale et stricte de la réalité du jeu de données disponible.![[shap_summary_option_b.png]]

### Chapitre 8 : Démonstrateurs et traduction opérationnelle


**Traduction opérationnelle et ergonomie de l'interface** Pour rendre l'outil exploitable par un chef de chantier, les variables d'entrée ont été traduites en langage naturel. Notamment, la variable `occ_code` (composée de codes numériques OSHA opaques) a été couplée à un dictionnaire de mappage dans l'interface. L'utilisateur sélectionne l'intitulé du métier en clair (ex: "Charpentier"), et l'application se charge de transmettre le code correspondant au pipeline de prétraitement pour l'inférence, masquant ainsi la complexité mathématique à l'utilisateur final.

### Chapitre 9 : Limites, conclusions métier et perspectives

**9.1. Limites inhérentes au jeu de données OSHA (Biais de sélection)** 

Le développement des modèles strictement proactifs (Option B) a mis en évidence une limite structurelle de la base de données OSHA. Cette base recense quasi exclusivement des incidents avérés et possède un taux de déclaration très faible pour les accidents mineurs (7 % du jeu de données). Par conséquent, le modèle n'apprend pas à différencier une "situation normale" d'une "situation dangereuse", mais tente de discriminer la gravité d'un accident en sachant que celui-ci a déjà eu lieu. De plus, les variables purement environnementales et démographiques s'avèrent insuffisantes pour établir une prédiction linéaire ou arborescente hautement fiable de la gravité.

**9.2. Perspective 1 : L'automatisation a posteriori par le NLP** 

La variable textuelle `abstract` contient un signal mathématique extrêmement fort (comme prouvé lors de la modélisation initiale). Bien que son usage génère une fuite de données pour une application de prévention, cette donnée pourrait être exploitée pour un autre cas d'usage : la classification automatisée de documents. L'entraînement d'un modèle de Deep Learning (Sentence-Transformers) sur ces descriptions permettrait d'automatiser le tri administratif et la catégorisation des rapports post-accident reçus par Vinci ou l'OSHA, réduisant ainsi le temps de traitement manuel.

**9.3. Perspective 2 : Amélioration du modèle proactif (Système d'Aide à la Décision)** 

Pour que le modèle d'anticipation (Option B) atteigne un niveau de performance compatible avec un déploiement sur les chantiers Vinci, une nouvelle stratégie de collecte de données est requise. L'algorithme doit être alimenté par des variables opérationnelles dynamiques telles que :

- Le taux de conformité du port des EPI (Équipements de Protection Individuelle) avant la tâche.
    
- Le niveau de fatigue déclaré ou la durée du cycle de travail de l'intervenant.
    
- L'état de certification ou de maintenance des équipements utilisés (ex: échafaudages, grues). L'intégration de ces données ciblées permettra de transformer le modèle tabulaire actuel en un véritable outil de prévention proactif.

### Chapitre 10 : Conclusion générale 

**Chapitre 10 : Conclusion générale**

Ce projet démontre la faisabilité technique du développement et du déploiement d'un Système d'Aide à la Décision (SAD) pour la prévention des risques dans le BTP. Le pipeline d'ingénierie complet a été validé : de l'extraction des données brutes à la mise en production d'une interface utilisateur (MVP) sous Streamlit, en passant par l'optimisation bayésienne d'un modèle de Gradient Boosting (LightGBM) et l'analyse d'explicabilité (SHAP).

Cependant, la viabilité opérationnelle de l'outil se heurte aux limites intrinsèques du jeu de données OSHA. L'étude prouve que les seules variables environnementales et démographiques ne contiennent pas le signal mathématique suffisant pour anticiper avec une haute fiabilité la gravité d'un accident (Rappel maximal de 64,7 % sur la classe mortelle). Le MVP répond à la problématique de départ en fournissant l'architecture logicielle requise, mais confirme que le déploiement réel chez Vinci Construction nécessitera l'ingestion de données de terrain plus granulaires (conformité EPI, fatigue, maintenance) pour que les prédictions atteignent le standard industriel attendu.

### Chapitre 11 : Difficultés rencontrées

**Chapitre 11 : Difficultés rencontrées et solutions apportées**

Tout au long du cycle de vie de ce projet, plusieurs obstacles techniques et méthodologiques ont nécessité des ajustements d'architecture :

1. **Fuite de données sémantique (Data Leakage) :**
 
- _Problème :_ La première itération du modèle exploitait les descriptions textuelles via un modèle d'embedding (Sentence-Transformers). Les scores obtenus étaient anormalement élevés (94 % de Rappel). L'analyse de l'importance des variables a révélé que le modèle s'appuyait sur le champ lexical post-accident.

- _Solution :_ Pivot architectural immédiat (Création de l'Option B). Les variables textuelles ont été exclues pour imposer un cadre strictement proactif, basculant l'ingénierie vers une optimisation maximale des données tabulaires restreintes.

2. **Déséquilibre extrême des classes et biais de sélection :**

- _Problème :_ Le jeu de données présentait une sous-représentation massive des accidents mineurs (7 %) par rapport aux accidents graves/mortels (92 %).

- _Solution :_ Rétablissement des 3 classes originelles de l'OSHA, utilisation de l'hyperparamètre `class_weight='balanced'` dans LightGBM, et optimisation bayésienne (Optuna) configurée pour maximiser spécifiquement le Rappel de la classe 1 afin de réduire les faux négatifs.

3. **Gestion stricte des types dans les pipelines Scikit-Learn :**

- _Problème :_ Lors du prétraitement tabulaire, l'imputation de variables catégorielles (contenant à la fois des chaînes de caractères et des valeurs numériques flottantes comme les codes métiers) a provoqué un échec du `OneHotEncoder` lors du tri mathématique des modalités.

- _Solution :_ Forçage explicite du typage en chaîne de caractères (`astype(str)`) pour l'ensemble des variables catégorielles en amont du `ColumnTransformer`, garantissant la stabilité du pipeline lors de l'inférence.

4. **Lisibilité de l'interface utilisateur (MVP) :**

- _Problème :_ Les codes métiers de l'OSHA (ex: 567.0) utilisés par le modèle mathématique sont illisibles pour un décideur métier utilisant l'interface Streamlit.
   
- _Solution :_ Création d'un dictionnaire de mappage bidirectionnel dans le code front-end de l'application, permettant à l'utilisateur de sélectionner des intitulés en langage naturel tout en transmettant les codes exacts au pipeline d'inférence.
>>>>>>> bcf19a6016fa0c81a1ab4fc2260844110537a27e

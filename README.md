# 🚧 Vinci ADT : Système de Prévention des Accidents du BTP

Ce dépôt contient le code source d'un démonstrateur de Machine Learning développé pour anticiper les risques d'accidents graves sur les chantiers de construction. 

## 🎯 Objectif Métier
Développer un Système d'Aide à la Décision (SAD) proactif. Le modèle évalue la probabilité d'un accident critique/mortel en se basant sur les conditions initiales du chantier (météo, âge de l'intervenant, métier), permettant ainsi de prioriser les ressources de prévention.

## 🛠️ Stack Technique
* **Langage & Traitement :** Python, Pandas, NumPy
* **Machine Learning :** Scikit-Learn, LightGBM
* **Optimisation :** Optuna (Optimisation bayésienne)
* **Interprétabilité :** SHAP
* **Déploiement :** Streamlit
* **Infrastructure :** Environnement Linux (Ubuntu) avec accélération GPU locale (RTX 5080) lors des phases de tests NLP.

## 🧠 Démarche d'ingénierie
1. **Diagnostic du Data Leakage :** Une première itération incluant des modèles de Deep Learning (Sentence-Transformers) sur les descriptions textuelles a mis en évidence une fuite de données sémantique (94% de Recall biaisé).
2. **Pivot Architectural :** Suppression totale des variables post-accident pour garantir une stricte capacité prédictive *a priori*.
3. **Modélisation Tabulaire :** Entraînement d'un modèle de Gradient Boosting avec compensation du déséquilibre extrême des classes.
4. **Optimisation :** Recherche des hyperparamètres via Optuna, maximisant spécifiquement le Recall de la classe critique pour minimiser les faux négatifs.
5. **Rapport technique :** [Lire le rapport détaillé](Rapport.md)

## 🚀 Utilisation du Démonstrateur (MVP)

Pour lancer l'application Streamlit en local :

1. Cloner le dépôt :
```bash
git clone [https://github.com/VOTRE_USERNAME/Projet_vinci_adt.git](https://github.com/VOTRE_USERNAME/Projet_vinci_adt.git)
cd Projet_vinci_adt


Créer l'environnement virtuel et installer les dépendances :

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Lancer l'interface :

streamlit run app.py

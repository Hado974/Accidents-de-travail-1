import streamlit as st
import pandas as pd
import numpy as np
import joblib
import torch
from sentence_transformers import SentenceTransformer

# 1. Configuration de la page
st.set_page_config(page_title="Vinci ADT - Prévention", layout="wide")
st.title("🚧 Démonstrateur : Anticipation des Risques BTP")
st.info("Instructions : Décrivez la tâche de chantier prévue. L'algorithme évaluera la probabilité d'un accident grave (Option A).")

# 2. Chargement des modèles en cache (pour éviter le rechargement à chaque action)
@st.cache_resource
def load_models():
    lgb_model = joblib.load("Data/processed/lgb_model.joblib")
    preprocessor = joblib.load("Data/processed/preprocessor.joblib")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    nlp_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    return lgb_model, preprocessor, nlp_model

lgb_model, preprocessor, nlp_model = load_models()

# 3. Formulaire utilisateur
with st.form("prediction_form"):
    task_desc = st.text_area("Description de la tâche prévue :", "Montage d'un échafaudage de 10 mètres en extérieur sous une forte pluie.")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Âge de l'intervenant principal :", min_value=18, max_value=65, value=35)
    with col2:
        wind_speed = st.slider("Vitesse du vent estimée (m/s) :", 0.0, 30.0, 5.0)
    
    submit_button = st.form_submit_button(label="Évaluer le risque")

# 4. Inférence
if submit_button:
    with st.spinner("Analyse en cours..."):
        # Création d'un DataFrame respectant strictement l'ordre et le nom des colonnes du Train Set
        data = {
            'state_x': ['CA'], 'city_x': ['Los Angeles'], 'zip_x': [90001],
            'age_x': [age], 'sex_x': ['M'], 'event_type': [1], 'occ_code': [1.0],
            'temp': [20.0], 'feels_like': [20.0], 'pressure': [1013.0],
            'humidity': [50.0], 'clouds': [0.0], 'visibility': [10000.0],
            'wind_speed': [wind_speed], 'wind_deg': [180.0], 'main': ['Clear']
        }
        df_input = pd.DataFrame(data)

        # Prétraitement tabulaire
        tab_features = preprocessor.transform(df_input)

        # Prétraitement NLP (Embedding)
        text_emb = nlp_model.encode([task_desc])

        # Concaténation des vecteurs
        X_final = np.hstack((tab_features, text_emb))

        # Prédiction (Rappel : les classes de LightGBM sont 0, 1, 2)
        pred = lgb_model.predict(X_final)[0]
        probas = lgb_model.predict_proba(X_final)[0]

        # 5. Affichage des résultats
        st.markdown("---")
        st.subheader("📊 Résultat de l'analyse")
        
        # Réajustement de la classe à la norme OSHA (1, 2, 3)
        risk_level = pred + 1
        
        if risk_level == 1:
            st.error("⚠️ ALERTE : Risque d'accident mortel ou critique détecté.")
        elif risk_level == 2:
            st.warning("⚠️ ATTENTION : Risque d'accident sévère (hospitalisation).")
        else:
            st.success("✅ Risque mineur évalué.")
            
        st.write(f"**Détail des probabilités :** Mortel/Critique ({probas[0]:.1%}) | Sévère ({probas[1]:.1%}) | Mineur ({probas[2]:.1%})")
        
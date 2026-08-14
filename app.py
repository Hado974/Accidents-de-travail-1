import streamlit as st
import pandas as pd
import joblib

# 1. Configuration de la page
st.set_page_config(page_title="Vinci ADT - Prévention", layout="wide")
st.title("🚧 Démonstrateur : Anticipation des Risques BTP (Option B)")
st.info("Instructions : Saisissez les paramètres de la tâche de chantier. Le modèle évaluera le risque de manière stricte (sans données post-accident).")

# 2. Chargement des modèles en cache
@st.cache_resource
def load_models():
    lgb_model = joblib.load("Data/processed/lgb_model_option_b.joblib")
    preprocessor = joblib.load("Data/processed/preprocessor_option_b.joblib")
    return lgb_model, preprocessor

lgb_final, preprocessor = load_models()

# Dictionnaire de mappage des métiers (Démonstration basée sur l'importance SHAP)
JOB_MAPPING = {
    "Charpentier / Menuisier (567.0)": "567.0",
    "Manœuvre / Ouvrier BTP (889.0)": "889.0",
    "Couvreur (595.0)": "595.0",
    "Inconnu / Non classé (999.0)": "999.0",
    "Autre métier (saisie manuelle)": "other"
}

# 3. Formulaire utilisateur
with st.form("prediction_form"):
    st.subheader("Paramètres de l'intervention")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age = st.number_input("Âge de l'intervenant :", min_value=18, max_value=70, value=35)
        sex = st.selectbox("Sexe :", options=["M", "F"])
        
        # Interface métier
        job_selection = st.selectbox("Métier de l'intervenant :", options=list(JOB_MAPPING.keys()))
        
        # Gestion du cas "Autre"
        if job_selection == "Autre métier (saisie manuelle)":
            occ_code = st.text_input("Saisissez le code OSHA exact :", value="0.0")
        else:
            occ_code = JOB_MAPPING[job_selection]
        
    with col2:
        temp = st.slider("Température (°C) :", -10.0, 45.0, 20.0)
        wind_speed = st.slider("Vitesse du vent (m/s) :", 0.0, 30.0, 5.0)
        main_weather = st.selectbox("Météo globale :", options=["Clear", "Clouds", "Rain", "Snow"])

    with col3:
        visibility = st.slider("Visibilité (m) :", 0, 10000, 10000)
        humidity = st.slider("Humidité (%) :", 0, 100, 50)
        
    submit_button = st.form_submit_button(label="Évaluer le risque")

# 4. Inférence
if submit_button:
    with st.spinner("Calcul des probabilités en cours..."):
        # Construction du DataFrame avec les variables attendues par le pipeline
        data = {
            'age_x': [age],
            'sex_x': [sex],
            'occ_code': [str(occ_code)], # Forcé en string pour le OneHotEncoder
            'temp': [temp],
            'feels_like': [temp], 
            'pressure': [1013.0], 
            'humidity': [humidity],
            'clouds': [0.0],
            'visibility': [visibility],
            'wind_speed': [wind_speed],
            'wind_deg': [180.0],
            'main': [main_weather]
        }
        df_input = pd.DataFrame(data)

        # Application du prétraitement
        X_processed = preprocessor.transform(df_input)

        # Prédiction 
        pred = lgb_final.predict(X_processed)[0]
        probas = lgb_final.predict_proba(X_processed)[0]

        # 5. Affichage
        st.markdown("---")
        st.subheader("📊 Résultat de l'analyse")
        
        risk_level = pred + 1
        
        if risk_level == 1:
            st.error("⚠️ ALERTE : Haut risque de situation critique/mortelle détecté selon ces paramètres.")
        elif risk_level == 2:
            st.warning("⚠️ ATTENTION : Risque d'accident sévère (hospitalisation).")
        else:
            st.success("✅ Risque évalué comme mineur.")
            
        st.write(f"**Probabilités calculées :** Mortel/Critique ({probas[0]:.1%}) | Sévère ({probas[1]:.1%}) | Mineur ({probas[2]:.1%})")
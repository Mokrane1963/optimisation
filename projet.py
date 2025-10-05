# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 16:03:25 2025

@author: mokrane
"""

import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ======================
# Configuration Streamlit
# ======================
st.set_page_config(page_title="Modélisation TPC", layout="wide")
st.title("🌿 Application de modélisation du TPC")
st.markdown("""
    <div style="text-align: center; font-family: courier;">
      <p style="color: #3366FF; 
                font-weight: bold; 
                font-size: 18px; 
                margin-top: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
        Développé par: Hachemi Mokrane • Septembre 2025
      </p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("Comparez différents modèles : Régression polynomiale, Réseau de neurones et Arbre de décision.")

# ======================
# Fonctions principales
# ======================

def génération_de_données(n_samples=20):
    np.random.seed(42)
    ethanol_concentration = np.random.choice([40, 60, 80], n_samples)
    power_level = np.random.choice([500, 700, 900], n_samples)
    extraction_time = np.random.choice([2, 4, 6], n_samples)
    TPC = (0.0292554255319149 * ethanol_concentration - 0.0065865 * power_level -
           1.24852127659574 * extraction_time + 72.5374138297872)
    TPC = np.round(TPC, 3)
    data = pd.DataFrame({
        'ethanol_concentration': ethanol_concentration,
        'power_level': power_level,
        'extraction_time': extraction_time,
        'TPC': TPC
    })
    return data

def préparation_de_données(data):
    X = data[['ethanol_concentration', 'power_level', 'extraction_time']]
    Y = data['TPC']
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    return X, Y, X_scaled, scaler

def entraîner_une_régression_polynomiale(X, Y, degree=1):
    poly = PolynomialFeatures(degree=degree, include_bias=True)
    X_poly = poly.fit_transform(X)
    model_poly = LinearRegression()
    model_poly.fit(X_poly, Y)
    y_pred = model_poly.predict(X_poly)
    r2_poly = r2_score(Y, y_pred)
    return model_poly, poly, y_pred, r2_poly

def entraîner_réseau_de_neurone(X_scaled, Y, epochs=50, batch_size=1):
    model_nn = Sequential([
        Dense(3, input_dim=3, activation='relu'),
        Dense(10, activation='relu'),
        Dense(1, activation='linear')
    ])
    optimizer = Adam(learning_rate=0.1)
    model_nn.compile(optimizer=optimizer, loss='mean_squared_error')
    history = model_nn.fit(X_scaled, Y, epochs=epochs, batch_size=batch_size,
                           verbose=0, validation_split=0.2)
    predictions_nn = model_nn.predict(X_scaled)
    r2_nn = r2_score(Y, predictions_nn)
    return model_nn, history, predictions_nn, r2_nn

def entraîner_arbre_de_décision(X, Y):
    tree_model = DecisionTreeRegressor()
    tree_model.fit(X, Y)
    tree_predictions = tree_model.predict(X)
    r2_tree = r2_score(Y, tree_predictions)
    return tree_model, tree_predictions, r2_tree

# ======================
# Interface Streamlit
# ======================

# Génération de données
n_samples = st.sidebar.slider("Nombre d’échantillons", 10, 100, 20)
data = génération_de_données(n_samples)
st.subheader("📋 Données générées")
st.dataframe(data)

# Préparation
X, Y, X_scaled, scaler = préparation_de_données(data)

# Paramètres des modèles
st.sidebar.header("Paramètres des modèles")
degree = st.sidebar.slider("Degré du polynôme", 1, 5, 1)
epochs = st.sidebar.slider("Époques (réseau de neurones)", 10, 200, 50)
batch_size = st.sidebar.slider("Taille du batch", 1, 10, 1)

# Sélecteur de modèle
model_choice = st.sidebar.radio(
    "Choisissez le modèle à entraîner / tester",
    ("Régression polynomiale", "Réseau de neurones", "Arbre de décision", "Comparer tous")
)

# Stockage dans session_state
if "models_trained" not in st.session_state:
    st.session_state.models_trained = False
    st.session_state.model_poly = None
    st.session_state.model_nn = None
    st.session_state.tree_model = None
    st.session_state.poly = None
    st.session_state.history = None
    st.session_state.scaler = scaler

# ======================
# Entraînement
# ======================
if st.button("🚀 Entraîner les modèles"):
    with st.spinner("Entraînement en cours..."):
        model_poly, poly, y_pred_poly, r2_poly = entraîner_une_régression_polynomiale(X, Y, degree)
        model_nn, history, predictions_nn, r2_nn = entraîner_réseau_de_neurone(X_scaled, Y, epochs, batch_size)
        tree_model, tree_predictions, r2_tree = entraîner_arbre_de_décision(X, Y)

        # Stocker les modèles
        st.session_state.models_trained = True
        st.session_state.model_poly = model_poly
        st.session_state.poly = poly
        st.session_state.model_nn = model_nn
        st.session_state.history = history
        st.session_state.tree_model = tree_model
        st.session_state.scaler = scaler
        st.session_state.results = {
            "r2_poly": r2_poly,
            "r2_nn": r2_nn,
            "r2_tree": r2_tree,
            "y_pred_poly": y_pred_poly,
            "predictions_nn": predictions_nn,
            "tree_predictions": tree_predictions,
        }

    st.success("✅ Entraînement terminé !")

# ======================
# Affichage des résultats
# ======================
if st.session_state.models_trained:
    results = st.session_state.results
    model_poly = st.session_state.model_poly
    model_nn = st.session_state.model_nn
    tree_model = st.session_state.tree_model
    poly = st.session_state.poly
    history = st.session_state.history
    scaler = st.session_state.scaler

    # Comparaison
    if model_choice == "Comparer tous":
        st.subheader("📊 Comparaison des modèles")
        col1, col2, col3 = st.columns(3)
        col1.metric("R² Régression Polynomiale", f"{results['r2_poly']:.3f}")
        col2.metric("R² Réseau de Neurones", f"{results['r2_nn']:.3f}")
        col3.metric("R² Arbre de Décision", f"{results['r2_tree']:.3f}")

    # Graphiques
    if model_choice in ["Réseau de neurones", "Comparer tous"]:
        st.subheader("📈 Courbe d’apprentissage du réseau de neurones")
        fig, ax = plt.subplots()
        ax.plot(history.history['loss'], label="Erreur d'entraînement")
        if 'val_loss' in history.history:
            ax.plot(history.history['val_loss'], label="Erreur de validation")
        ax.legend()
        ax.set_xlabel("Époques")
        ax.set_ylabel("MSE")
        st.pyplot(fig)

    # ======================
    # Prédiction interactive
    # ======================
    st.subheader("🧮 Prédire une nouvelle valeur")
    ethanol = st.number_input("Concentration en éthanol (%)", 0, 100, 60)
    power = st.number_input("Puissance (W)", 100, 1000, 700)
    extraction = st.number_input("Temps d’extraction (min)", 1, 10, 4)

    if st.button("🔍 Faire une prédiction"):
        nouvelle_entree = np.array([[ethanol, power, extraction]])
        scaler = st.session_state.scaler
        poly = st.session_state.poly

        if model_choice == "Régression polynomiale":
            X_poly = poly.transform(nouvelle_entree)
            prediction = st.session_state.model_poly.predict(X_poly)[0]
            st.info(f"🎯 TPC prédit (régression polynomiale) : **{prediction:.3f}**")

        elif model_choice == "Réseau de neurones":
            X_scaled = scaler.transform(nouvelle_entree)
            prediction = st.session_state.model_nn.predict(X_scaled)[0][0]
            st.info(f"🧠 TPC prédit (réseau de neurones) : **{prediction:.3f}**")

        elif model_choice == "Arbre de décision":
            prediction = st.session_state.tree_model.predict(nouvelle_entree)[0]
            st.info(f"🌳 TPC prédit (arbre de décision) : **{prediction:.3f}**")

        elif model_choice == "Comparer tous":
            X_poly = poly.transform(nouvelle_entree)
            X_scaled = scaler.transform(nouvelle_entree)
            pred_poly = st.session_state.model_poly.predict(X_poly)[0]
            pred_nn = st.session_state.model_nn.predict(X_scaled)[0][0]
            pred_tree = st.session_state.tree_model.predict(nouvelle_entree)[0]

            st.success("✅ Prédictions multiples")
            st.write(f"**Régression polynomiale :** {pred_poly:.3f}")
            st.write(f"**Réseau de neurones :** {pred_nn:.3f}")
            st.write(f"**Arbre de décision :** {pred_tree:.3f}")


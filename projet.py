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

st.set_page_config(page_title="Modélisation TPC", layout="wide")

# ======================
# Fonctions de base
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

st.title("🌿 Application de modélisation du TPC avec différents modèles")
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
# Génération de données
n_samples = st.sidebar.slider("Nombre d’échantillons", 10, 100, 20)
data = génération_de_données(n_samples)
st.subheader("Aperçu des données générées")
st.dataframe(data)

# Préparation des données
X, Y, X_scaled, scaler = préparation_de_données(data)

# Paramètres utilisateur
st.sidebar.header("Paramètres des modèles")
degree = st.sidebar.slider("Degré du polynôme", 1, 5, 1)
epochs = st.sidebar.slider("Époques (réseau de neurones)", 10, 200, 50)
batch_size = st.sidebar.slider("Taille du batch", 1, 10, 1)

# Entraînement
if st.button("🚀 Entraîner les modèles"):
    with st.spinner("Entraînement en cours..."):
        model_poly, poly, y_pred_poly, r2_poly = entraîner_une_régression_polynomiale(X, Y, degree)
        model_nn, history, predictions_nn, r2_nn = entraîner_réseau_de_neurone(X_scaled, Y, epochs, batch_size)
        tree_model, tree_predictions, r2_tree = entraîner_arbre_de_décision(X, Y)

        # Résultats
        st.success("✅ Entraînement terminé !")

        results = pd.DataFrame({
            'Ethanol (%)': X.iloc[:, 0],
            'Puissance (W)': X.iloc[:, 1],
            'Temps (min)': X.iloc[:, 2],
            'TPC Réel': Y,
            'Rég. Poly': np.round(y_pred_poly, 3),
            'Réseau Neurones': np.round(predictions_nn.flatten(), 3),
            'Arbre Décision': np.round(tree_predictions, 3)
        })

        st.subheader("📊 Résultats comparatifs")
        st.dataframe(results)

        col1, col2, col3 = st.columns(3)
        col1.metric("R² Régression Polynomiale", f"{r2_poly:.3f}")
        col2.metric("R² Réseau de Neurones", f"{r2_nn:.3f}")
        col3.metric("R² Arbre de Décision", f"{r2_tree:.3f}")

        # Graphiques
        st.subheader("📈 Courbe d’apprentissage du réseau de neurones")
        fig, ax = plt.subplots()
        ax.plot(history.history['loss'], label="Erreur d'entraînement")
        if 'val_loss' in history.history:
            ax.plot(history.history['val_loss'], label="Erreur de validation")
        ax.set_xlabel("Époques")
        ax.set_ylabel("Erreur quadratique moyenne")
        ax.legend()
        st.pyplot(fig)

        st.subheader("📉 Comparaison des prédictions")
        fig2, ax2 = plt.subplots()
        ax2.plot(Y.values, label="Valeurs réelles", marker='o')
        ax2.plot(predictions_nn, label="Réseau de neurones", linestyle='--', marker='x')
        ax2.plot(tree_predictions, label="Arbre de décision", linestyle='--', marker='*')
        ax2.legend()
        st.pyplot(fig2)

        # Section de prédiction interactive
        st.subheader("🧮 Prédire de nouvelles valeurs")
        ethanol = st.number_input("Concentration en éthanol (%)", min_value=0, max_value=100, value=60)
        power = st.number_input("Puissance (W)", min_value=100, max_value=1000, value=700)
        extraction = st.number_input("Temps d’extraction (min)", min_value=1, max_value=10, value=4)

        nouvelle_entree = np.array([[ethanol, power, extraction]])
        nouvelle_entree_poly = poly.transform(nouvelle_entree)
        prediction_poly = model_poly.predict(nouvelle_entree_poly)
        nouvelle_entree_scaled = scaler.transform(nouvelle_entree)
        prediction_nn = model_nn.predict(nouvelle_entree_scaled)
        prediction_arbre = tree_model.predict(nouvelle_entree)

        st.write(f"**Régression polynomiale :** {prediction_poly[0]:.3f}")
        st.write(f"**Réseau de neurones :** {prediction_nn[0][0]:.3f}")
        st.write(f"**Arbre de décision :** {prediction_arbre[0]:.3f}")

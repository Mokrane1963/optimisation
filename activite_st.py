# -*- coding: utf-8 -*-
"""
Created on Mon May  5 16:18:49 2025

@author: mokrane
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import streamlit as st

# ---------------------------------------------------
# Configuration de la page
# ---------------------------------------------------
st.set_page_config(page_title="Régression Linéaire Interactive", page_icon="📈", layout="centered")
st.title("📈 Régression Linéaire Interactive") 
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
# ---------------------------------------------------
# Section 1 : Saisie des données d'entraînement
# ---------------------------------------------------
st.header("1️⃣ Entrez vos données d'entraînement")

col1, col2 = st.columns(2)
with col1:
    x_input = st.text_input("📏 Superficie de l’appartement (m²) — séparées par des virgules", "100, 200, 300", key="x_input")
with col2:
    y_input = st.text_input("💰 Prix de l’appartement (DZD) — séparées par des virgules", "900000, 1300000, 1700000", key="y_input")

# ---------------------------------------------------
# Traitement des données
# ---------------------------------------------------
try:
    x_train = np.array([float(x.strip()) for x in x_input.split(',')]).reshape(-1, 1)
    y_train = np.array([float(y.strip()) for y in y_input.split(',')])

    if len(x_train) != len(y_train):
        st.error("⚠️ Le nombre de valeurs X et Y doit être identique.")

    else:
        # Entraînement du modèle
        model = LinearRegression()
        model.fit(x_train, y_train)

        # Préparation des données pour le graphique
        x_range = np.linspace(x_train.min(), x_train.max(), 100).reshape(-1, 1)
        y_range = model.predict(x_range)

        # ---------------------------------------------------
        # Affichage du graphique de régression
        # ---------------------------------------------------
        fig, ax = plt.subplots()
        ax.scatter(x_train, y_train, color='red', label="Données d'entraînement")
        ax.plot(x_range, y_range, color='blue', label="Ligne de régression")
        ax.set_xlabel("Superficie (m²)")
        ax.set_ylabel("Prix (DZD)")
        ax.set_title("Régression Linéaire")
        ax.legend()
        st.pyplot(fig)

        # ---------------------------------------------------
        # Section 2 : Prédiction directe
        # ---------------------------------------------------
        st.header("2️⃣ Prédiction du prix")

        x_val = st.number_input("🏠 Quelle est la superficie (en m²) ?", min_value=0, value=120, key="x_val")
        if st.button("🔮 Calculer le prix estimé", key="btn_predict"):
            x_test = np.array([[x_val]])
            y_pred = model.predict(x_test)
            B = model.intercept_
            m = model.coef_[0]

            st.success(f"💰 Le prix estimé d’un logement de **{x_val} m²** est **{round(y_pred[0])} DZD**")
            st.info(f"📏 Équation de la droite : y = {m:.2f}x + {B:.2f}")

            # Graphique avec la prédiction
            fig2, ax2 = plt.subplots()
            ax2.scatter(x_train, y_train, color='green', label="Données d'entraînement")
            ax2.plot(x_range, y_range, color='blue', label="Ligne de régression")
            ax2.scatter(x_val, y_pred, color='red', lw=2, marker='x', s=100, label="Prédiction")
            ax2.set_xlabel("Superficie (m²)")
            ax2.set_ylabel("Prix (DZD)")
            ax2.set_title("Régression Linéaire avec Prédiction")
            ax2.legend()
            st.pyplot(fig2)

        # ---------------------------------------------------
        # Section 3 : Calcul inverse (trouver la surface)
        # ---------------------------------------------------
        st.header("3️⃣ Calcul inverse")

        prix_val = st.number_input("💰 Quel est le prix (en DZD) ?", min_value=0, value=1000000, key="prix_val")
        if st.button("📏 Calculer la surface correspondante", key="btn_inverse"):
            B = model.intercept_
            m = model.coef_[0]
            surface = (prix_val - B) / m
            surface = round(surface, 2)
            st.success(f"🏡 Le logement coûtant **{prix_val} DZD** a une surface estimée de **{surface} m²**")

except ValueError:
    st.error("❌ Veuillez entrer uniquement des valeurs numériques séparées par des virgules.")


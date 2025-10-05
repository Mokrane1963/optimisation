# -*- coding: utf-8 -*-
"""
Created on Mon May  5 16:18:49 2025

@author: mokrane
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import streamlit as st

st.title("Régression Linéaire Interactive")

# Section 1: Saisie des données d'entraînement
st.header("1. Entrez vos données d'entraînement")
col1, col2 = st.columns(2)

with col1:
    x_input = st.text_input("مساحة شقة بالمتر المربع      (séparées par des virgules)", "100, 200, 300")
with col2:
    y_input = st.text_input("سسعر الشقة بالدينار          (séparées par des virgules)", "900000, 1300000, 1700000")

try:
    x_train = np.array([float(x.strip()) for x in x_input.split(',')]).reshape(-1, 1)
    y_train = np.array([float(y.strip()) for y in y_input.split(',')])
    
    if len(x_train) != len(y_train):
        st.error("Le nombre de valeurs X et Y doit être identique")
    else:
        # Entraînement du modèle
        model = LinearRegression()
        model.fit(x_train, y_train)
        
        # Préparation des données pour le graphique
        x_range = np.linspace(x_train.min(), x_train.max(), 100).reshape(-1, 1)
        y_range = model.predict(x_range)
        
        # Affichage du graphique initial
        fig, ax = plt.subplots()
        ax.scatter(x_train, y_train, color='red', label='Données d\'entraînement')
        ax.plot(x_range, y_range, color='blue', label='Ligne de régression')
        ax.set_xlabel("valeurs depentantes")
        ax.set_ylabel("valeurs correspondantes")
        ax.set_title("Régression Linéaire")
        ax.legend()
        st.pyplot(fig)
        
        # Section 2: Prédiction
        st.header("2. Prédiction")
        x = st.number_input("Quelle est le prix d'un logement de (m^2) :", min_value=0, value=4)
        
        if st.button("Calculer le prix d un logement "):
            x_test = np.array([[x]])
            y_pred = model.predict(x_test)
            B = round(model.intercept_)
            m = model.coef_[0]
            
            st.write(f"Le prix d un logement de  {x} m^2 est  de: {round(y_pred[0])}")
            #st.write(f"Le nombre de conifères nécessaires pour protéger {x**2} prix est : {round(y_pred[0])}")
            st.write(f"L'équation de la droite est : y = {m:.2f}x + {B:.2f}")
            
            # Affichage du graphique avec prédiction
            fig2, ax2 = plt.subplots()
            ax2.scatter(x_train, y_train, color='green')
            ax2.plot(x_range, y_range, color='blue')
            ax2.scatter(x, y_pred, color='red', lw=2, marker='x', s=100, label='Prédiction')
            ax2.set_xlabel("valeurs de x ")
            ax2.set_ylabel("valeurs de y")
            ax2.set_title("Régression Linéaire avec Prédiction")
            ax2.legend()
            st.pyplot(fig2)
        
        # Section 3: Calcul inverse
        st.header("3. Calcul inverse")
        surface = st.number_input("Quelle est la surface d un logement dont le prix est':", min_value=0, value=20)
        
        if st.button("Calculer la surface d un logement"):
            B = model.intercept_
            m = model.coef_[0]
            prix = ((surface - B) / m)
            prix=round(prix)
            st.write(f"Calculer la surface d un logement dont le prix  est : {prix:2f} ")

except ValueError:
    st.error("Veuillez entrer des valeurs numériques valides séparées par des virgules")
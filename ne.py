# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 20:48:42 2025

@author: mokrane
"""
import streamlit as st

st.set_page_config(page_title="Calculateur NE555", page_icon="⏱️", layout="centered")

st.title("⏱️ Calculateur de temporisation NE555")
st.write("Ce calculateur vous permet d’estimer la durée d’impulsion générée par un timer NE555 en configuration **monostable** ou **astable**.")

# Sélection du mode
mode = st.radio("Choisir la configuration :", ["Monostable", "Astable"])

# Entrée des valeurs
R1 = st.number_input("Valeur de la résistance R₁ (kΩ)", min_value=0.0, step=0.1)
if mode == "Astable":
    R2 = st.number_input("Valeur de la résistance R₂ (kΩ)", min_value=0.0, step=0.1)
else:
    R2 = 0.0

C1 = st.number_input("Valeur de la capacité C₁ (µF)", min_value=0.0, step=0.1)


# Calcul automatique dès qu'une valeur change
if R1 > 0 and C1 > 0:
    if mode == "Monostable":
        T = 1.1 * (R1 * 1e3) * (C1 * 1e-6)
        formule = "T = 1.1 × R₁ × C₁"
    else:
        T = 0.693 * ((R1 + 2 * R2) * 1e3) * (C1 * 1e-6)
        formule = "T = 0.693 × (R₁ + 2R₂) × C₁"

    st.success(f"⏰ Durée d’impulsion : **{T*1000:.2f} ms**")
    st.latex(formule)
else:
    st.info("Veuillez entrer des valeurs valides pour R₁ et C₁.")

st.markdown("---")
st.caption("Développé avec ❤️ en Streamlit pour calculer les temporisations du NE555.")

# Affichage de la formule
st.markdown("---")
st.markdown("### 📘 Rappels des formules :")
st.latex(r"T_{monostable} = 1.1 \times R_1 \times C_1")
st.latex(r"T_{astable} = 0.693 \times (R_1 + 2R_2) \times C_1")
st.markdown("Les durées sont données en secondes (s) avant conversion en millisecondes (ms).")

st.markdown("---")
st.caption("Développé avec ❤️ en Streamlit pour calculer les temporisations du NE555.")


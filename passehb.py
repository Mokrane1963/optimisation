# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 11:43:37 2025

@author: mokrane
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Configuration de la page ---
st.set_page_config(page_title="Calculateur Filtre RC", page_icon="🎛️", layout="centered")

st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #FFD700; font-weight: bold; font-size: 30px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    🎛️ Calculateur de filtre RC (Passe-bas / Passe-haut)
  </p>
</div>
""", unsafe_allow_html=True)

# --- Style visuel ---
st.markdown("""
<style>
div.stButton > button {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: black !important;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    transition: all 0.2s ease-in-out;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #FFA500, #FF4500);
    color: white !important;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar avec titre en tifinagh ---
st.sidebar.markdown("""
<div style="text-align: center; font-family: 'Tifinaghe-Ircam Unicode sans serif';">
  <p style="
      color: #FFD700; 
      font-weight: bold; 
      font-size: 28px; 
      margin-top: 5px;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">
   ⴰⵣⵓⵍ ⴼⴻⵍⵍⴰⵡⴻⵏ
  </p>
</div>
""", unsafe_allow_html=True)

# --- 🎨 Style des boutons ---
st.markdown("""
<style>
div.stButton > button, div.stDownloadButton > button {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: black !important;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #FFA500, #FF4500);
    color: white !important;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# --- 🎨 Fond dynamique ---
st.sidebar.header("🎨 Fond dégradé de la page")
gradient_type = st.sidebar.selectbox("Type de dégradé", ["linear-gradient", "radial-gradient"])
angle = st.sidebar.slider("Angle (degrés)", 0, 360, 135)
color1 = st.sidebar.color_picker("Couleur 1", "#1E3C72")
color2 = st.sidebar.color_picker("Couleur 2", "#2A5298")
color3 = st.sidebar.color_picker("Couleur 3 (optionnelle)", "#00C9FF")
use_three_colors = st.sidebar.checkbox("Utiliser 3 couleurs", value=False)

if gradient_type == "linear-gradient":
    gradient = f"linear-gradient({angle}deg, {color1}, {color2}{', '+color3 if use_three_colors else ''})"
else:
    gradient = f"radial-gradient(circle, {color1}, {color2}{', '+color3 if use_three_colors else ''})"

page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: {gradient};
    background-attachment: fixed;
}}
[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"] {{
    background: none !important;
}}
h1, h2, h3, p {{
    color: white;
}}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)
# --- Sélection du type de filtre ---
filtre_type = st.radio("🎚️ Choisir le type de filtre :", ["Passe-bas", "Passe-haut"])

st.markdown("---")

# --- Entrée des valeurs ---
col1, col2 = st.columns(2)
with col1:
    R = st.number_input("Résistance R (kΩ)", min_value=0.1, value=10.0, step=0.1)
with col2:
    C = st.number_input("Capacité C (µF)", min_value=0.001, value=0.1, step=0.001)

# --- Bouton de calcul ---
if st.button("🔹 Calculer"):
    R_ohm = R * 1e3
    C_f = C * 1e-6
    tau = R_ohm * C_f
    fc = 1 / (2 * np.pi * tau)

    # --- Affichage des résultats ---
    colA, colB = st.columns(2)
    with colA:
        st.success(f"⏱️ Constante de temps τ = **{tau*1000:.3f} ms**")
    with colB:
        st.success(f"🎵 Fréquence de coupure fₙ = **{fc:.2f} Hz**")

    # --- Réponse fréquentielle ---
    f = np.logspace(0, 5, 500)  # de 1 Hz à 100 kHz
    w = 2 * np.pi * f
    if filtre_type == "Passe-bas":
        H = 1 / np.sqrt(1 + (w * R_ohm * C_f) ** 2)
    else:
        H = (w * R_ohm * C_f) / np.sqrt(1 + (w * R_ohm * C_f) ** 2)
    gain_db = 20 * np.log10(H)

    # --- Graphique de Bode ---
    st.markdown("### 📊 Réponse fréquentielle")
    fig1, ax1 = plt.subplots()
    ax1.semilogx(f, gain_db, color="gold")
    ax1.axvline(fc, color="red", linestyle="--", label=f"fₙ = {fc:.2f} Hz")
    ax1.set_xlabel("Fréquence (Hz)")
    ax1.set_ylabel("Gain (dB)")
    ax1.set_title(f"Réponse en fréquence ({filtre_type})")
    ax1.grid(True, which="both", ls="--")
    ax1.legend()
    st.pyplot(fig1)

    # --- Simulation temporelle ---
    st.markdown("### 🕒 Réponse temporelle à un signal carré")
    t = np.linspace(0, 0.05, 1000)  # 50 ms
    f_in = 100  # fréquence du signal carré d'entrée
    x = 0.5 * (1 + np.sign(np.sin(2 * np.pi * f_in * t)))  # signal carré [0,1]

    # Réponse temporelle du filtre (par convolution)
    dt = t[1] - t[0]
    if filtre_type == "Passe-bas":
        h = (1 / tau) * np.exp(-t / tau)
    else:
        h = (-1 / tau) * np.exp(-t / tau)
    y = np.convolve(x, h)[:len(t)] * dt

    # --- Graphique temporel ---
    fig2, ax2 = plt.subplots()
    ax2.plot(t * 1000, x, label="Entrée (signal carré)", color="orange")
    ax2.plot(t * 1000, y, label=f"Sortie filtrée ({filtre_type})", color="blue")
    ax2.set_xlabel("Temps (ms)")
    ax2.set_ylabel("Amplitude")
    ax2.set_title(f"Réponse temporelle ({filtre_type})")
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)

# --- Rappels théoriques ---
st.markdown("---")
st.markdown("### 📘 Rappels des formules :")
st.latex(r"\tau = R \times C")
st.latex(r"f_c = \dfrac{1}{2\pi R C}")
st.latex(r"H_{passe-bas}(j\omega) = \dfrac{1}{\sqrt{1 + (\omega R C)^2}}")
st.latex(r"H_{passe-haut}(j\omega) = \dfrac{\omega R C}{\sqrt{1 + (\omega R C)^2}}")

st.caption("🧮 Développé avec ❤️ par Hachemi Mokrane — Calculateur RC Streamlit 2025")

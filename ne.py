# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 20:48:42 2025

@author: mokrane
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Configuration de la page ---
st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #8B4513; font-weight: bold; font-size: 30px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    ⏱️ Calculateur de temporisation NE555
  </p>
</div>
""", unsafe_allow_html=True)

st.write(
    "Ce calculateur vous permet d’estimer la **durée d’impulsion**, la **fréquence**, "
    "le **rapport cyclique** et les **temps haut/bas** du timer **NE555** "
    "en configuration **monostable** ou **astable**."
)
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
# --- 🎨 Correction du style des boutons (visibilité sur fond sombre) ---
st.markdown("""
<style>
/* Style général pour tous les boutons Streamlit */
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

/* Effet au survol */
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #FFA500, #FF4500);
    color: white !important;
    box-shadow: 0 0 15px rgba(255, 140, 0, 0.6);
    transform: scale(1.05);
}

/* Ajustement pour les boutons dans la sidebar */
section[data-testid="stSidebar"] div.stButton > button {
    background: linear-gradient(135deg, #00C9FF, #92FE9D);
    color: black !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: linear-gradient(135deg, #92FE9D, #00C9FF);
    color: black !important;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)
st.sidebar.header("🎨 Fond dégradé de la page")

gradient_type = st.sidebar.selectbox(
    "Type de dégradé",
    ["linear-gradient", "radial-gradient"]
)

angle = st.sidebar.slider("Angle (degrés)", 0, 360, 135)
color1 = st.sidebar.color_picker("Couleur 1", "#1E3C72")
color2 = st.sidebar.color_picker("Couleur 2", "#2A5298")
color3 = st.sidebar.color_picker("Couleur 3 (optionnelle)", "#00C9FF")
use_three_colors = st.sidebar.checkbox("Utiliser 3 couleurs", value=False)

if gradient_type == "linear-gradient":
    if use_three_colors:
        gradient = f"linear-gradient({angle}deg, {color1}, {color2}, {color3})"
    else:
        gradient = f"linear-gradient({angle}deg, {color1}, {color2})"
else:
    if use_three_colors:
        gradient = f"radial-gradient(circle, {color1}, {color2}, {color3})"
    else:
        gradient = f"radial-gradient(circle, {color1}, {color2})"

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

#st.subheader("🧾 Code CSS généré :")
#st.code(gradient, language="css")

# --- Sélection du mode ---
mode = st.radio("🧩 Choisir la configuration :", ["Monostable", "Astable"])

st.markdown("---")

# --- Entrées utilisateur ---
col1, col2, col3 = st.columns(3)
with col1:
    R1 = st.number_input("R₁ (kΩ)", min_value=0.0, step=0.1)
with col2:
    R2_disabled = (mode == "Monostable")
    R2 = st.number_input("R₂ (kΩ)", min_value=0.0, step=0.1, disabled=R2_disabled)
with col3:
    C1 = st.number_input("C₁ (µF)", min_value=0.0, step=0.1)

st.markdown("---")

# --- Bouton de calcul ---
calculer = st.button("🔹 Calculer")
graph_placeholder = st.empty()  # pour éviter le bug DOM

if calculer:
    if R1 > 0 and C1 > 0:
        C = C1 * 1e-6
        R1_ohm = R1 * 1e3
        R2_ohm = R2 * 1e3

        if mode == "Monostable":
            T = 1.1 * R1_ohm * C
            st.success(f"⏰ Durée d’impulsion : **{T*1000:.2f} ms**")
            st.latex(r"T = 1.1 \times R_1 \times C_1")

            # Signal unique impulsion
            t = np.linspace(0, T * 3, 500)
            signal = np.where(t < T, 1, 0)

        else:  # Astable
            # --- Formules complètes ---
            T = 0.693 * (R1_ohm + 2 * R2_ohm) * C
            F = 1.44 / ((R1_ohm + 2 * R2_ohm) * C)
            T1 = 0.693 * (R1_ohm + R2_ohm) * C  # temps haut
            T2 = 0.693 * R2_ohm * C             # temps bas
            duty_cycle = (T1 / T) * 100

            # --- Affichage clair ---
            colA, colB, colC = st.columns(3)
            with colA:
                st.success(f"📈 Fréquence : **{F:.2f} Hz**")
            with colB:
                st.success(f"⚙️ Rapport cyclique : **{duty_cycle:.1f}%**")
            with colC:
                st.success(f"⏱️ Période totale : **{T*1000:.2f} ms**")

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🔺 Temps haut (T₁) : **{T1*1000:.2f} ms**")
            with col2:
                st.info(f"🔻 Temps bas (T₂) : **{T2*1000:.2f} ms**")

            # --- Génération du signal carré ---
            t = np.linspace(0, T * 3, 500)
            signal = np.zeros_like(t)
            for i, time in enumerate(t):
                phase = (time % T) / T
                signal[i] = 1 if phase < (T1 / T) else 0

        # --- Graphique (dans le placeholder) ---
        with graph_placeholder:
            fig, ax = plt.subplots()
            ax.plot(t * 1000, signal, linewidth=2)
            ax.set_xlabel("Temps (ms)")
            ax.set_ylabel("Sortie (niveau logique)")
            ax.set_title(f"Forme d’onde NE555 ({mode})")
            ax.set_ylim(-0.2, 1.2)
            ax.grid(True)
            st.pyplot(fig)

    else:
        st.error("⚠️ Veuillez entrer des valeurs valides pour R₁ et C₁ avant de calculer.")

# --- Rappels des formules ---
st.markdown("---")
st.markdown("### 📘 Rappels des formules :")
st.latex(r"T_{monostable} = 1.1 \times R_1 \times C_1")
st.latex(r"F_{astable} = \dfrac{1.44}{(R_1 + 2R_2) \times C}")
st.latex(r"T_{astable} = 0.693 \times (R_1 + 2R_2) \times C")
st.latex(r"T_1 = 0.693 \times (R_1 + R_2) \times C")
st.latex(r"T_2 = 0.693 \times R_2 \times C")
st.latex(r"D = \dfrac{T_1}{T} \times 100")

st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #3366FF; font-weight: bold; font-size: 16px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    Développé par: Hachemi Mokrane • Septembre 2025
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

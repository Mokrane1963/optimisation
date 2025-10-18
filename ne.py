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
    "Ce calculateur estime la **durée d’impulsion**, la **fréquence**, "
    "le **rapport cyclique**, les **temps haut/bas**, et affiche les "
    "**courbes réelles de charge/décharge** du condensateur **et la sortie logique** "
    "du NE555, en modes **monostable** et **astable**."
)

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

# --- Sélection du mode ---
mode = st.radio("🧩 Choisir la configuration :", ["Monostable", "Astable"])
st.markdown("---")

# --- Entrées utilisateur ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    R1 = st.number_input("R₁ (kΩ)", min_value=0.0, step=0.1)
with col2:
    R2_disabled = (mode == "Monostable")
    R2 = st.number_input("R₂ (kΩ)", min_value=0.0, step=0.1, disabled=R2_disabled)
with col3:
    C1 = st.number_input("C₁ (µF)", min_value=0.0, step=0.1)
with col4:
    Vcc = st.number_input("Vcc (V)", min_value=3.0, value=5.0, step=0.5)

st.markdown("---")

# --- Bouton ---
calculer = st.button("🔹 Calculer")
graph_placeholder = st.empty()

if calculer:
    if R1 > 0 and C1 > 0:
        C = C1 * 1e-6
        R1_ohm = R1 * 1e3
        R2_ohm = R2 * 1e3
        Vtrig, Vth = Vcc / 3, (2 / 3) * Vcc

        if mode == "Monostable":
            T = 1.1 * R1_ohm * C
            t = np.linspace(0, T * 1.5, 500)
            Vc = Vcc * (1 - np.exp(-t / (R1_ohm * C)))
            output = np.where(t < T, Vcc, 0)

            st.success(f"⏰ Durée d’impulsion : **{T*1000:.2f} ms**")

            fig, ax1 = plt.subplots()
            ax1.plot(t * 1000, Vc, color="blue", label="Vc (Condensateur)")
            ax1.axhline(Vtrig, color="orange", linestyle="--", label="1/3 Vcc")
            ax1.axhline(Vth, color="yellow", linestyle="--", label="2/3 Vcc")
            ax1.set_xlabel("Temps (ms)")
            ax1.set_ylabel("Tension Vc (V)")
            ax1.grid(True)
            ax1.legend(loc="upper left")

            ax2 = ax1.twinx()
            ax2.plot(t * 1000, output, color="lime", linestyle="--", label="Sortie NE555")
            ax2.set_ylabel("Sortie (V)")
            ax2.legend(loc="upper right")
            ax1.set_title("Mode Monostable — Charge du condensateur et sortie")
            st.pyplot(fig)

        else:
            # === Mode Astable ===
            T1 = 0.693 * (R1_ohm + R2_ohm) * C
            T2 = 0.693 * R2_ohm * C
            T = T1 + T2
            F = 1 / T
            D = (T1 / T) * 100

            st.success(f"📈 Fréquence : **{F:.2f} Hz** | ⏱️ Période : **{T*1000:.2f} ms** | ⚖️ D = **{D:.1f}%**")

            # --- Simulation sur plusieurs cycles ---
            cycles = 3
            t = np.linspace(0, cycles * T, 2000)
            Vc, out = [], []

            for i in t:
                phase = i % T
                if phase < T1:
                    v = Vcc * (1 - np.exp(-phase / ((R1_ohm + R2_ohm) * C)))
                    o = Vcc
                else:
                    v = Vth * np.exp(-(phase - T1) / (R2_ohm * C))
                    o = 0
                Vc.append(v)
                out.append(o)

            # --- Graphique combiné ---
            fig, ax1 = plt.subplots()
            ax1.plot(t * 1000, Vc, color="blue", label="Vc (Condensateur)")
            ax1.axhline(Vth, color="red", linestyle="--", label="2/3 Vcc")
            ax1.axhline(Vtrig, color="yellow", linestyle="--", label="1/3 Vcc")
            ax1.set_xlabel("Temps (ms)")
            ax1.set_ylabel("Tension Vc (V)")
            ax1.grid(True)
            ax1.legend(loc="upper left")

            ax2 = ax1.twinx()
            ax2.plot(t * 1000, out, color="lime", linestyle="-", alpha=0.7, label="Sortie NE555")
            ax2.set_ylabel("Sortie (V)")
            ax2.legend(loc="upper right")
            ax1.set_title("Mode Astable — Charge/Décharge et onde carrée de sortie")
            st.pyplot(fig)

    else:
        st.error("⚠️ Veuillez entrer des valeurs valides pour R₁ et C₁.")

# --- Rappels des formules ---
st.markdown("---")
st.markdown("### 📘 Formules principales :")
st.latex(r"T_{mono} = 1.1 \times R_1 \times C")
st.latex(r"F_{asta} = \dfrac{1.44}{(R_1 + 2R_2) \times C}")
st.latex(r"T_{asta} = 0.693 \times (R_1 + 2R_2) \times C")
st.latex(r"T_1 = 0.693 \times (R_1 + R_2) \times C, \quad T_2 = 0.693 \times R_2 \times C")
st.latex(r"D = \dfrac{T_1}{T_1 + T_2} \times 100")

st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #3366FF; font-weight: bold; font-size: 16px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    Développé par: mok ou si Ali • Octobre 2025
  </p>
</div>
""", unsafe_allow_html=True)


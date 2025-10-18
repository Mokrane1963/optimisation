# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 14:13:59 2025

@author: mokrane
"""

#
# filtres_rlc_app.py
import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Page setup ---
st.set_page_config(page_title="Calculateur RLC", page_icon="🎛️", layout="wide")

# --- En-tête ---
st.markdown("""
<div style="text-align: center; font-family: 'Courier New', monospace;">
  <h1 style="color: #FFD700; font-weight: bold; text-shadow: 2px 2px 6px rgba(0,0,0,0.7);">
    🎛️ Calculateur de filtres — RC / LR / LC (Passe-bas & Passe-haut)
  </h1>
  <p style="color: #E6E6E6; font-size: 15px;">
     Réponse fréquentielle et temporelle (signal carré)
  </p>
</div>
""", unsafe_allow_html=True)

# --- Style général ---
st.markdown("""
<style>
div.stButton > button {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: black !important;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    padding: 0.5em 1.2em;
    transition: all 0.2s ease-in-out;
    box-shadow: 0px 0px 10px rgba(255, 215, 0, 1.1);
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #FFA500, #FF4500);
    color: white !important;
    transform: scale(1.05);
}
h1, h2, h3, p, label, .stMarkdown { color: white !important; }
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #1e3c72, #2a5298);
    background-attachment: fixed;
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
# --- Choix du filtre ---
filter_type = st.selectbox(
    "🔧 Choisir le type de filtre",
    [
        "RC Passe-bas", "RC Passe-haut",
        "LR Passe-bas", "LR Passe-haut",
        "LC Passe-bas", "LC Passe-haut"
    ]
)

# --- Activation/désactivation dynamique ---
use_R = True
use_L = "LR" in filter_type or "LC" in filter_type
use_C = "RC" in filter_type or "LC" in filter_type

col1, col2, col3, col4 = st.columns(4)
with col1:
    R = st.number_input("R (Ω)", min_value=0.0, value=100.0, step=0.1, disabled=not use_R)
with col2:
    L = st.number_input("L (mH)", min_value=0.0, value=10.0, step=0.1, disabled=not use_L)
with col3:
    C = st.number_input("C (µF)", min_value=0.0, value=0.1, step=0.001, disabled=not use_C)
with col4:
    f_in = st.number_input("Fréq. signal carré (Hz)", min_value=1.0, value=500.0, step=1.0)

st.markdown("---")

# --- Bouton calcul ---
if st.button("🔹 Calculer"):
    L_h = L * 1e-3
    C_f = C * 1e-6
    R_val = max(R, 1e-12)
    f = np.logspace(0, 6, 2000)
    w = 2 * np.pi * f

    # === Calcul selon le type ===
    if "RC" in filter_type:
        tau = R_val * C_f
        fc = 1 / (2 * np.pi * tau) if tau > 0 else 0
        if "Passe-bas" in filter_type:
            H = 1 / np.sqrt(1 + (w * tau)**2)
        else:
            H = (w * tau) / np.sqrt(1 + (w * tau)**2)

    elif "LR" in filter_type:
        tau = L_h / R_val
        fc = R_val / (2 * np.pi * L_h) if L_h > 0 else 0
        if "Passe-bas" in filter_type:
            H = 1 / np.sqrt(1 + (w * L_h / R_val)**2)
        else:
            H = (w * L_h / R_val) / np.sqrt(1 + (w * L_h / R_val)**2)

    else:  # LC
        fc = 1 / (2 * np.pi * np.sqrt(max(L_h * C_f, 1e-24)))
        if "Passe-bas" in filter_type:
            H = 1 / np.sqrt((1 - (w**2)*L_h*C_f)**2 + (w*R_val*C_f)**2)
        else:
            H = (w**2)*L_h*C_f / np.sqrt((1 - (w**2)*L_h*C_f)**2 + (w*R_val*C_f)**2)

    st.success(f"🎵 Fréquence de coupure fₙ ≈ **{fc:.2f} Hz**")

    # === Réponse fréquentielle ===
    st.markdown("### 📊 Réponse fréquentielle (Bode)")
    gain_db = 20 * np.log10(np.maximum(H, 1e-30))
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    ax1.semilogx(f, gain_db, color="gold", linewidth=1.6)
    ax1.axvline(fc, color="red", linestyle="--", label=f"fₙ ≈ {fc:.1f} Hz")
    ax1.set_xlabel("Fréquence (Hz)")
    ax1.set_ylabel("Gain (dB)")
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend()
    st.pyplot(fig1)
    plt.close(fig1)

    # === Réponse temporelle ===
    st.markdown("### 🕒 Réponse temporelle (signal carré)")
    t = np.linspace(0, 0.02, 2000)
    x = 0.5 * (1 + np.sign(np.sin(2 * np.pi * f_in * t)))

    if "RC" in filter_type:
        h = (1 / tau) * np.exp(-t / tau)
        y_conv = np.convolve(x, h)[:len(t)] * (t[1] - t[0])
        y = y_conv if "Passe-bas" in filter_type else x - y_conv

    elif "LR" in filter_type:
        tau_lr = L_h / R_val
        h = (1 / tau_lr) * np.exp(-t / tau_lr)
        y_conv = np.convolve(x, h)[:len(t)] * (t[1] - t[0])
        y = y_conv if "Passe-bas" in filter_type else x - y_conv

    else:  # LC
        wn = 2 * np.pi * fc
        damping = R_val / (2 * L_h)
        h = np.exp(-damping * t) * np.sin(wn * t)
        y_conv = np.convolve(x, h)[:len(t)] * (t[1] - t[0])
        y = y_conv if "Passe-bas" in filter_type else x - y_conv

    fig2, ax2 = plt.subplots(figsize=(7, 3.5))
    ax2.plot(t * 1000, x, label="Entrée (signal carré)", color="#FFA500")
    ax2.plot(t * 1000, y, label=f"Sortie ({filter_type})", color="#00FFFF")
    ax2.set_xlabel("Temps (ms)")
    ax2.set_ylabel("Amplitude")
    ax2.legend()
    ax2.grid(True, alpha=0.5)
    st.pyplot(fig2)
    plt.close(fig2)


st.caption("🧮 Développé avec ❤️Streamlit par  Hachemi Mokrane (2025)")


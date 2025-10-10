# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 21:11:44 2025

@author: mokrane
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calculateur de diviseur de tension avec charge", layout="wide")

st.title("Calculateur de diviseur de tension (avec charge)")
st.markdown(
    "Calcule la tension de sortie d'un diviseur R1-R2 avec une charge RL connectée en parallèle sur R2.\n\n"
    "**Formules** :\n\n"
    "- Sans charge : `Vout_no_load = Vin * R2 / (R1 + R2)`\n"
    "- Avec RL : `R2p = (R2 * RL) / (R2 + RL)` puis `Vout_loaded = Vin * R2p / (R1 + R2p)`\n"
)

# --- Entrées utilisateur ---
col1, col2 = st.columns(2)

with col1:
    Vin = st.number_input("Tension d'entrée Vin (V)", value=12.0, format="%.6f")
    R1 = st.number_input("R1 (Ω)", value=10000.0, format="%.6f")
    R2 = st.number_input("R2 (Ω)", value=4700.0, format="%.6f")

with col2:
    RL = st.number_input("RL - Résistance de charge (Ω) (mettre 0 pour pas de charge)", value=100000.0, format="%.6f")
    show_table = st.checkbox("Afficher tableau des puissances et courants", value=True)

# Validation simple
if R1 <= 0 or R2 <= 0 or Vin < 0:
    st.error("Vin doit être ≥ 0, R1 et R2 doivent être strictement > 0.")
    st.stop()

# --- Calculs ---
def parallel(r_a, r_b):
    if r_a <= 0 or r_b <= 0:
        return np.inf
    return 1.0 / (1.0 / r_a + 1.0 / r_b)

Vout_no_load = Vin * (R2 / (R1 + R2))

if RL <= 0:
    # pas de charge (ou RL=0 signifie court-circuit -> traiter comme 'court-circuit' : R2p=0)
    if RL == 0:
        R2p = 0.0
        Vout_loaded = 0.0
    else:
        R2p = R2
        Vout_loaded = Vout_no_load
else:
    R2p = parallel(R2, RL)
    Vout_loaded = Vin * (R2p / (R1 + R2p))

# Erreur relative
if Vout_no_load != 0:
    error_pct = (Vout_loaded - Vout_no_load) / Vout_no_load * 100.0
else:
    error_pct = 0.0

# Courants
# courant dans R1 (arrivé depuis la source) = Vin / (R1 + R2p)
I_total = Vin / (R1 + R2p) if (R1 + R2p) != 0 else np.inf
I_R1 = I_total
I_R2p = Vout_loaded / R2p if R2p not in (0.0, np.inf) else 0.0
I_RL = Vout_loaded / RL if RL > 0 else 0.0

# Puissances
P_R1 = (I_R1 ** 2) * R1
P_R2p = (I_R2p ** 2) * R2p if R2p not in (0.0, np.inf) else 0.0
P_RL = (I_RL ** 2) * RL if RL > 0 else 0.0
P_source = Vin * I_R1

# --- Affichage des résultats ---
st.subheader("Résultats numériques")
res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.metric("Vout (sans charge)", f"{Vout_no_load:.6f} V")
    st.metric("R2 parallèle (R2p)", f"{R2p:.2f} Ω")

with res_col2:
    st.metric("Vout (avec charge)", f"{Vout_loaded:.6f} V")
    st.metric("Erreur relative", f"{error_pct:.4f} %")

with res_col3:
    st.metric("Courant total (I_R1)", f"{I_R1*1000:.6f} mA")
    st.metric("Puissance fournie par la source", f"{P_source:.6f} W")

if show_table:
    st.write("---")
    st.subheader("Courants et puissances (détails)")
    st.write(
        {
            "I_R1 (A)": I_R1,
            "I_R2p (A)": I_R2p,
            "I_RL (A)": I_RL,
            "P_R1 (W)": P_R1,
            "P_R2p (W)": P_R2p,
            "P_RL (W)": P_RL,
        }
    )

# --- Graphique : Vout en fonction de RL ---
st.write("---")
st.subheader("Vout en fonction de RL (échelle logarithmique)")

# Génére une plage de RL allant de 1 Ω à 10 MΩ en échelle log
rl_values = np.logspace(0, 7, num=200)  # 1 Ω à 10^7 Ω
vouts = []
for rl in rl_values:
    r2p_tmp = parallel(R2, rl)
    vout_tmp = Vin * (r2p_tmp / (R1 + r2p_tmp))
    vouts.append(vout_tmp)

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.set_xscale('log')
ax.plot(rl_values, vouts)
ax.axvline(RL if RL > 0 else 1e-9, linestyle='--')
ax.set_xlabel("RL (Ω) - échelle log")
ax.set_ylabel("Vout (V)")
ax.set_title("Vout vs RL")
ax.grid(True, which="both", ls=":", alpha=0.6)
st.pyplot(fig)

# --- Conseils pratiques ---
st.write("---")
st.subheader("Conseils / Interprétation rapide")
st.markdown(
    "- Si `RL >> R2` (beaucoup plus grand), l'effet de la charge est négligeable et `Vout_loaded ≈ Vout_no_load`.\n"
    "- Si `RL` est de l'ordre de `R2` ou plus petit, la tension de sortie s'effondre (R2 en parallèle avec RL diminue la résistance effective).\n"
    "- Pour limiter l'erreur (par ex. < 1%), choisissez R2 beaucoup plus petit que RL (ou placez un buffer suivi du diviseur, ex. un suiveur d'op-amp).\n"
    "- Attention à la dissipation : des résistances trop petites impliquent des courants importants et plus de puissance dissipée dans R1/R2."
)

st.info("Astuce : pour tester un court-circuit sur la sortie, mets RL = 0 (traité comme RL = 0 Ω -> Vout ≈ 0).")

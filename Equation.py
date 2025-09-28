# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 18:25:02 2025

@author: mokrane
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# Fonction utilitaire
# -------------------------

def build_function(expr: str):
    """Construit une fonction f(x) à partir d'une expression donnée par l'utilisateur."""
    def f(x):
        return eval(expr, {"x": x, "np": np, "sin": np.sin, "cos": np.cos,
                           "exp": np.exp, "log": np.log, "tan": np.tan})
    return f

def bisection(f, a, b, tol=1e-6, max_iter=100):
    """Algorithme de la bissection"""
    if f(a) * f(b) > 0:
        return None, []
    iterations = []
    for i in range(max_iter):
        m = (a + b) / 2
        iterations.append((i+1, a, b, m, f(m)))
        if abs(f(m)) < tol or (b - a) / 2 < tol:
            return m, iterations
        if f(a) * f(m) < 0:
            b = m
        else:
            a = m
    return m, iterations

# -------------------------
# Interface Streamlit
# -------------------------

st.title("🔎 Méthode de la bissection")

st.markdown("""
Donnez une **fonction f(x)** (ex: `sin(x)`, `x**2 - 2`, `exp(x) - 3`).  
Puis choisissez un intervalle `[a, b]` et la méthode de bissection cherchera une racine.
""")

# Expression de la fonction
expr = st.text_input("Entrez votre fonction f(x)", value="sin(x)")

# Intervalle
a = st.number_input("Borne a", value=-10.0, step=0.1)
b = st.number_input("Borne b", value=-9.0, step=0.1)

# Paramètres
tol = st.number_input("Tolérance", value=1e-6, format="%.1e")
max_iter = st.slider("Nombre max d'itérations", 1, 200, 50)

# Construire la fonction
try:
    f = build_function(expr)
    test_val = f(0)  # test rapide pour vérifier l'expression
except Exception as e:
    st.error(f"Erreur dans l’expression : {e}")
    st.stop()

# Bouton
if st.button("Lancer la bissection"):
    root, steps = bisection(f, a, b, tol, max_iter)

    if root is None:
        st.error("⚠️ Pas de changement de signe entre a et b → pas de racine garantie.")
    else:
        st.success(f"✅ Racine trouvée : x ≈ {root:.6f}")

        # Tableau des itérations
        st.subheader("Détails des itérations")
        df = pd.DataFrame(steps, columns=["Itération", "a", "b", "Milieu m", "f(m)"])
        st.dataframe(df)

        # Graphique
        st.subheader("Visualisation de la fonction")
        xs = np.linspace(a, b, 400)
        ys = [f(x) for x in xs]
        fig, ax = plt.subplots()
        ax.axhline(0, color="black", linewidth=1)
        ax.plot(xs, ys, label=f"f(x) = {expr}")
        ax.scatter([root], [f(root)], color="red", zorder=5, label="Racine")
        ax.legend()
        st.pyplot(fig)

# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 13:30:08 2025

@author: mokrane
"""
import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimisation avec Lagrangien", page_icon="🧮", layout="centered")

# --- Style simple avec fond dégradé ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
    color: white;
}
.stButton button {
    background-color: #FFDD00;
    color: black !important;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 0.5em 1em;
}
</style>
""", unsafe_allow_html=True)

# --- Titre principal ---
st.markdown("<h2 style='text-align:center;'>🔹 Optimisation sous contrainte (Méthode du Lagrangien)</h2>", unsafe_allow_html=True)
st.write("Entrez une fonction f(x, y) à minimiser et une contrainte g(x, y) = 0.")

# --- Entrées utilisateur ---
f_input = st.text_input("Fonction à minimiser f(x,y) :", value="x**2 + y**2")
g_input = st.text_input("Contrainte g(x,y) = 0 :", value="x + y - 1")

# --- Création des symboles ---
x, y, lam = sp.symbols('x y lam', real=True)

if st.button("Résoudre avec la méthode du Lagrangien"):
    try:
        # Conversion sécurisée
        f = sp.sympify(f_input, locals={'x': x, 'y': y})
        g = sp.sympify(g_input, locals={'x': x, 'y': y})

        # Construction du Lagrangien
        L = f + lam * g

        # Système d’équations
        eqs = [
            sp.Eq(sp.diff(L, x), 0),
            sp.Eq(sp.diff(L, y), 0),
            sp.Eq(g, 0)
        ]

        # Résolution symbolique
        sol = sp.solve(eqs, (x, y, lam), dict=True)

        if sol:
            st.markdown("### ✅ Résultats de la résolution")
            for s in sol:
                x_val, y_val, lam_val = s[x], s[y], s[lam]
                st.write(f"**x = {sp.N(x_val)}**, **y = {sp.N(y_val)}**, **λ = {sp.N(lam_val)}**")

                # Valeur de la fonction à la solution
                f_opt = f.subs({x: x_val, y: y_val})
                st.write(f"**Valeur de f(x,y) = {sp.N(f_opt)}**")

                # --- Partie graphique ---
                st.subheader("📈 Représentation graphique")

                # Création du maillage
                x_vals = np.linspace(float(x_val) - 2, float(x_val) + 2, 200)
                y_vals = np.linspace(float(y_val) - 2, float(y_val) + 2, 200)
                X, Y = np.meshgrid(x_vals, y_vals)

                # Évaluation numérique de f et g
                f_num = sp.lambdify((x, y), f, "numpy")
                g_num = sp.lambdify((x, y), g, "numpy")

                Z = f_num(X, Y)
                G = g_num(X, Y)

                # Tracé des courbes
                fig, ax = plt.subplots(figsize=(7, 6))
                contour = ax.contour(X, Y, Z, levels=20, cmap='viridis')
                ax.clabel(contour, inline=True, fontsize=8, fmt="%.1f")
                ax.contour(X, Y, G, levels=[0], colors='red', linewidths=2, label="Contrainte g(x,y)=0")

                # Point solution
                ax.plot(float(x_val), float(y_val), 'ro', label='Solution optimale')

                # Mise en forme
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.set_title('Courbes de niveau de f(x,y) et contrainte g(x,y)=0')
                ax.legend()
                ax.grid(alpha=0.3)

                st.pyplot(fig)
                 
        else:
            st.warning("⚠️ Aucune solution trouvée symboliquement. Vérifiez la saisie de vos fonctions.")
            
        # --- Détails du calcul symbolique ---
        with st.expander("📘 Détails du calcul symbolique"):
            st.latex(f"\\mathcal{{L}}(x,y,\\lambda) = {sp.latex(L)}")
            st.write("**Équations du système :**")
            st.latex(f"\\frac{{\\partial \\mathcal{{L}}}}{{\\partial x}} = {sp.latex(sp.diff(L, x))} = 0")
            st.latex(f"\\frac{{\\partial \\mathcal{{L}}}}{{\\partial y}} = {sp.latex(sp.diff(L, y))} = 0")
            st.latex(f"g(x,y) = {sp.latex(g)} = 0")

    except Exception as e:
        st.error(f"Erreur lors de l’analyse : {e}")

# --- Explications ---
with st.expander("ℹ️ Rappel de la méthode du Lagrangien"):
    st.markdown(r"""
    Pour résoudre un problème du type :
    \[
    \min_{x,y} f(x,y) \quad \text{sous } g(x,y) = 0
    \]
    on forme le Lagrangien :
    \[
    \mathcal{L}(x,y,\lambda) = f(x,y) + \lambda \, g(x,y)
    \]
    et on cherche les points critiques tels que :
    \[
    \frac{\partial \mathcal{L}}{\partial x} = 0, \quad
    \frac{\partial \mathcal{L}}{\partial y} = 0, \quad
    g(x,y)=0
    \]
    """)

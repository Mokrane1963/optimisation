# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 21:29:12 2025

@author: mokrane
"""
import streamlit as st
from sympy import latex
from sympy.parsing.sympy_parser import parse_expr

st.set_page_config(page_title="Convertisseur Math → LaTeX", page_icon="🧮", layout="centered")
st.title("🧮 Convertisseur interactif d'expressions mathématiques en LaTeX")

st.markdown("Choisis une expression dans la liste ou écris la tienne 👇")

# Liste d’expressions proposées
examples = [
    "x^2 + 3*x - 28",
    "(x+7)*(x-4)",
    "(x + 1)**3 - (x - 1)**3",
    "integrate(x^3 + 2*x, x)",
    "diff(sin(x)*exp(x), x)",
    "Eq(x**2 + 3*x - 28, 0)",
    "Sum(1/n**2, (n, 1, oo))",
    "sin(x)**2 + cos(x)**2",
    "Matrix([[1, 2], [3, 4]]) * Matrix([[x], [y]])",
    "Eq(Derivative(y(x), x, x) + 3*Derivative(y(x), x) + 2*y(x), 0)",
    "binomial(n, k)"
]

# Sélecteur + champ d’entrée personnalisée
selected_expr = st.selectbox("🧠 Sélectionne une expression :", examples)
custom_expr = st.text_input("✍️ Ou entre ta propre expression :", value=selected_expr)

# Traitement
if custom_expr.strip():
    try:
        expr = parse_expr(custom_expr)
        latex_code = latex(expr)

        st.markdown("---")
        st.subheader("🧾 Code LaTeX :")
        st.code(latex_code, language="latex")

        st.subheader("📐 Rendu LaTeX :")
        st.latex(expr)

    except Exception as e:
        st.error(f"Erreur : {e}")


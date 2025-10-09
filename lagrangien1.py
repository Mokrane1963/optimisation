# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 20:26:14 2025

@author: mokrane
"""

import sympy as sp
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus
import re

# ==============================
# Fonction de correction automatique
# ==============================
def corriger_saisie(expr: str) -> str:
    """Corrige les erreurs de saisie communes dans les expressions."""
    expr = expr.lower().replace(" ", "")
    expr = expr.replace("et", "y")   # corrige les autocorrections "et"
    expr = expr.replace("ans", "y")  # corrige les "ans"
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)  # ajoute le * entre nombre et variable
    return expr


# ==============================
# Fonction de parsing linéaire
# ==============================
def analyse_syntaxique(expression):
    expression = expression.replace(" ", "")
    termes = re.findall(r'([+-]?[\d.]*[a-zA-Z]+)', expression)
    analysee = []
    
    for terme in termes:
        signe = 1
        if terme.startswith('-'):
            signe = -1
            terme = terme[1:]
        elif terme.startswith('+'):
            terme = terme[1:]
        
        partie_coef = re.match(r'^[\d.]+', terme)
        partie_variable = terme[len(partie_coef.group()):] if partie_coef else terme
        
        coeff = float(partie_coef.group()) if partie_coef else 1.0
        coeff *= signe
        
        if partie_variable:
            analysee.append((coeff, partie_variable))
    
    return analysee


# ==============================
# Affichage graphique
# ==============================
def affichage_graphique(contraintes, solution_x, solution_y, variables):
    fig, ax = plt.subplots(figsize=(10, 8))
    x_max = max(solution_x * 2, 50) if solution_x > 0 else 50
    x_vals = np.linspace(0, x_max, 400)
    colors = ['blue', 'green', 'red', 'orange', 'purple']
    
    for i, (lhs, op, rhs) in enumerate(contraintes):
        if i < len(colors):
            termes = analyse_syntaxique(lhs)
            if len(termes) == 2:
                a, var1 = termes[0]
                b, var2 = termes[1]
                if b != 0:
                    y_vals = (rhs - a * x_vals) / b
                    label = f'{lhs} {op} {rhs}'
                    ax.plot(x_vals, y_vals, label=label, linewidth=2, color=colors[i])
                    if op == '>=':
                        ax.fill_between(x_vals, y_vals, y_vals + 100, alpha=0.2, color=colors[i])
                    elif op == '<=':
                        ax.fill_between(x_vals, y_vals, 0, alpha=0.2, color=colors[i])
    
    if solution_x is not None and solution_y is not None:
        ax.plot(solution_x, solution_y, 'ro', markersize=10, 
                label=f'Solution ({solution_x:.2f}, {solution_y:.2f})')
    
    ax.set_xlabel(variables[0] if variables else 'x')
    ax.set_ylabel(variables[1] if len(variables) > 1 else 'y')
    ax.set_title('Représentation Graphique de la Solution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if solution_x is not None and solution_y is not None:
        ax.set_xlim(0, max(solution_x * 1.5, 10))
        ax.set_ylim(0, max(solution_y * 1.5, 10))
    else:
        ax.set_xlim(0, 50)
        ax.set_ylim(0, 50)
    
    return fig


# ==============================
# Interface Streamlit
# ==============================
st.set_page_config(page_title="Optimisation linéaire", page_icon="🔢", layout="centered")

# 🎨 Dégradé dynamique
st.sidebar.header("🎨 Fond dégradé")
gradient_type = st.sidebar.selectbox("Type de dégradé", ["linear-gradient", "radial-gradient"])
angle = st.sidebar.slider("Angle (°)", 0, 360, 135)
color1 = st.sidebar.color_picker("Couleur 1", "#1E3C72")
color2 = st.sidebar.color_picker("Couleur 2", "#2A5298")
color3 = st.sidebar.color_picker("Couleur 3 (optionnelle)", "#00C9FF")
use_three_colors = st.sidebar.checkbox("Utiliser 3 couleurs", value=False)

if gradient_type == "linear-gradient":
    gradient = f"linear-gradient({angle}deg, {color1}, {color2}{',' + color3 if use_three_colors else ''})"
else:
    gradient = f"radial-gradient(circle, {color1}, {color2}{',' + color3 if use_three_colors else ''})"

st.markdown(f"""
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
""", unsafe_allow_html=True)

# --- En-tête ---
st.markdown("<h2 style='text-align:center;'>🔹 Résolution de problèmes linéaires à deux variables</h2>", unsafe_allow_html=True)

# ==============================
# Entrées utilisateur
# ==============================
objectif = st.text_input("Fonction économique (ex: max 3x + 5y) :")
n_contraintes = st.number_input("Nombre de contraintes", min_value=1, max_value=10, value=2, step=1)

contraintes = []
for i in range(n_contraintes):
    contrainte = st.text_input(f"Contrainte {i+1} (ex: 2x + 3y <= 12)")
    if contrainte:
        for op in ['<=', '>=', '==', '=']:
            if op in contrainte:
                lhs, rhs = contrainte.split(op, 1)
                contraintes.append((lhs.strip(), op.strip(), float(rhs.strip())))
                break

afficher_graphique = st.checkbox("Afficher le graphique")

# ==============================
# Résolution du problème
# ==============================
if st.button("Résoudre"):
    if not objectif:
        st.error("Veuillez entrer une fonction économique valide.")
    else:
        if objectif.lower().startswith("max"):
            modele_type = LpMaximize
            expression = objectif[3:].strip()
        elif objectif.lower().startswith("min"):
            modele_type = LpMinimize
            expression = objectif[3:].strip()
        else:
            st.error("La fonction doit commencer par 'max' ou 'min'.")
            st.stop()
        
        probleme = LpProblem("Probleme_Lineaire", modele_type)
        termes_objectif = analyse_syntaxique(expression)
        
        variables = set()
        for coeff, var in termes_objectif:
            variables.add(var)
        for lhs, _, _ in contraintes:
            for coeff, var in analyse_syntaxique(lhs):
                variables.add(var)
        variables = sorted(variables)
        
        if len(variables) != 2:
            st.error("⚠️ Cette application ne gère que 2 variables (x et y).")
            st.stop()
        
        lp_vars = LpVariable.dicts("Var", variables, lowBound=0)
        probleme += sum(coeff * lp_vars[var] for coeff, var in termes_objectif)
        
        for lhs, op, rhs in contraintes:
            expression = sum(coeff * lp_vars[var] for coeff, var in analyse_syntaxique(lhs))
            if op == '<=':
                probleme += expression <= rhs
            elif op == '>=':
                probleme += expression >= rhs
            else:
                probleme += expression == rhs
        
        probleme.solve()
        
        st.subheader("Résultats de l'optimisation")
        st.write("**Statut :**", LpStatus[probleme.status])
        
        solution = {var: lp_vars[var].varValue for var in variables}
        var1, var2 = variables
        x_val, y_val = solution[var1], solution[var2]
        
        st.write(f"**Solution optimale :** ({var1}, {var2}) = ({x_val:.2f}, {y_val:.2f})")
        st.write(f"**Valeur optimale :** z = {probleme.objective.value():.2f}")
        
        # --- Affichage des contraintes corrigées ---
        st.write("**Fonction économique :**")
        st.latex(f"\\mathcal{{ {objectif}}}")
        st.write("**Contraintes :**")
        for i, (lhs, op, rhs) in enumerate(contraintes, 1):
            lhs = corriger_saisie(lhs)
            rhs = corriger_saisie(str(rhs))
            st.latex(f"{i}.\\; {lhs} {op} {rhs}")

        if afficher_graphique:
            fig = affichage_graphique(contraintes, x_val, y_val, variables)
            st.pyplot(fig)

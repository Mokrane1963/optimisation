# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 16:26:28 2025

@author: mokrane
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus
import re

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

# --- 🎨 Bloc du testeur de dégradé ---
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


st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #8B4513; font-weight: bold; font-size: 20px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
   🔢 Résolution de problèmes linéaires à deux variables
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; font-family: Tifinaghe-Ircam Unicode sans serif;">
  <p style="color: #726B1E; font-weight: bold; font-size: 24px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
   ⴰⵣⵓⵍ ⴼⴻⵍⵍⴰⵡⴻⵏ
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #3366FF; font-weight: bold; font-size: 18px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    Développé par: Hachemi Mokrane • Septembre 2025
  </p>
</div>
""", unsafe_allow_html=True)

# ==============================
# Entrées utilisateur
# ==============================

st.markdown("**Fonction économique max ou min suivi de : ax + by**")
objectif = st.text_input("Fonction économique: ")  

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

afficher_graphique = st.checkbox("Afficher la représentation graphique")

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
            st.error("⚠️ La résolution est disponible uniquement pour 2 variables (ex: x et y).")
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
        
        solution = {}
        for var in variables:
            val = lp_vars[var].varValue
            solution[var] = val
        
        if len(variables) == 2:
            var1, var2 = variables
            x_val = solution[var1]
            y_val = solution[var2]
            st.write(f"**Solution optimale :** ({var1};{var2}) = ({x_val:.2f};{y_val:.2f})")
        
        optimal_value = probleme.objective.value()
        st.write(f"**Valeur optimale :** z = {optimal_value:.2f}")
        
        st.write("**Détail des valeurs :**")
        for var in variables:
            #st.write(f"- {var} = {solution[var]:.2f}")
            st.markdown(f"<span style='color:#00C9FF;'>{var} = {solution[var]:.2f}</span>", unsafe_allow_html=True)
        if afficher_graphique:
            st.subheader("📈 Représentation Graphique")
            try:
                if x_val is not None and y_val is not None:
                    fig = affichage_graphique(contraintes, x_val, y_val, variables)
                    st.pyplot(fig)
                    st.markdown("""
<div style='color:white; font-size:16px;'>
    <b>Légende du graphique :</b><br><br>
    <ul style='list-style-type: none;'>
        <li><span style='color:blue;'>●</span> <b>Lignes colorées</b> : contraintes</li>
        <li><span style='color:lightgreen;'>⬛</span> <b>Zone ombrée</b> : zone réalisable</li>
        <li><span style='color:red;'>●</span> <b>Point rouge</b> : solution optimale</li>
    </ul>
</div>
""", unsafe_allow_html=True)
                else:
                    st.warning("Impossible d'afficher le graphique : solution non trouvée")
            except Exception as e:
                st.warning(f"Impossible d'afficher le graphique : {e}")
        
        st.markdown("---")
        st.subheader("📋 Résumé")
        
        st.write("**Fonction économique :** ")
        st.markdown(
         f"<span style='color:#FFD700; font-weight:bold;'>{objectif}.</span> " ,
         unsafe_allow_html=True)
        st.write("**Contraintes :**")
        for i, (lhs, op, rhs) in enumerate(contraintes, 1):
            st.markdown(
              
       f"<span style='color:#FFD700; font-weight:bold;'>{i}.</span> "
       f"<span style='color:#00FFFF;'>{lhs}</span> "
       f"<span style='color:white;'>{op}</span> "
       f"<span style='color:#FFA500;'>{rhs}</span>",
       unsafe_allow_html=True
   )

# ==============================
# Instructions
# ==============================
with st.expander("ℹ️ Instructions d'utilisation"):
    st.markdown("""
    **Comment utiliser cette application :**
    
    1. **Fonction économique** : Entrez "max" ou "min" suivi de l'expression (ex: `max 3x + 5y`)
    2. **Nombre de contraintes**
    3. **Contraintes** : Ex `2x + 3y <= 12`
    4. **Graphique** : cochez la case
    5. **Résoudre** : cliquez sur le bouton
    
    **Exemple complet :**
    - Fonction : `min 35x + 34y`
    - Contrainte 1 : `4x + 3y >= 504`
    - Contrainte 2 : `5x + y >= 256`
    - Contrainte 3 : `2x + 5y >= 240`
    """)

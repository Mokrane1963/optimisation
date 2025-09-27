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

# Configuration matplotlib pour Streamlit


# Fonction de parsing pour les expressions linéaires
def parse_expression(expr):
    expr = expr.replace(" ", "")
    terms = re.findall(r'([+-]?[\d.]*[a-zA-Z]+)', expr)
    parsed = []
    
    for term in terms:
        sign = 1
        if term.startswith('-'):
            sign = -1
            term = term[1:]
        elif term.startswith('+'):
            term = term[1:]
        
        coeff_part = re.match(r'^[\d.]+', term)
        var_part = term[len(coeff_part.group()):] if coeff_part else term
        
        coeff = float(coeff_part.group()) if coeff_part else 1.0
        coeff *= sign
        
        if var_part:
            parsed.append((coeff, var_part))
    
    return parsed

def plot_solution_graphique(contraintes, solution_x, solution_y, variables):
    """Affichage graphique de la solution avec les données réelles"""
    
    # Création de la figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Domaine des x
    x_max = max(solution_x * 2, 50) if solution_x > 0 else 50
    x_vals = np.linspace(0, x_max, 400)
    
    # Couleurs pour les différentes contraintes
    colors = ['blue', 'green', 'red', 'orange', 'purple']
    
    # Tracé des contraintes
    for i, (lhs, op, rhs) in enumerate(contraintes):
        if i < len(colors):  # Pour éviter l'index error si trop de contraintes
            termes = parse_expression(lhs)
            if len(termes) == 2:
                a, var1 = termes[0]
                b, var2 = termes[1]
                
                if b != 0:  # Éviter division par zéro
                    y_vals = (rhs - a * x_vals) / b
                    label = f'{lhs} {op} {rhs}'
                    ax.plot(x_vals, y_vals, label=label, linewidth=2, color=colors[i])
                    
                    # Remplissage selon l'opérateur
                    if op == '>=':
                        ax.fill_between(x_vals, y_vals, y_vals + 100, alpha=0.2, color=colors[i])
                    elif op == '<=':
                        ax.fill_between(x_vals, y_vals, 0, alpha=0.2, color=colors[i])
    
    # Point solution
    if solution_x is not None and solution_y is not None:
        ax.plot(solution_x, solution_y, 'ro', markersize=10, 
                label=f'Solution ({solution_x:.2f}, {solution_y:.2f})')
    
    # Mise en forme
    ax.set_xlabel(variables[0] if variables else 'x')
    ax.set_ylabel(variables[1] if len(variables) > 1 else 'y')
    ax.set_title('Représentation Graphique de la Solution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Ajustement des limites
    if solution_x is not None and solution_y is not None:
        ax.set_xlim(0, max(solution_x * 1.5, 10))
        ax.set_ylim(0, max(solution_y * 1.5, 10))
    else:
        ax.set_xlim(0, 50)
        ax.set_ylim(0, 50)
    
    return fig

# ------------------------
# Interface Streamlit
# ------------------------
st.markdown("""
<div style="text-align: center; font-family: Tifinaghe-Ircam Unicode sans serif;">
  <p style="color: #8B4513; 
            font-weight: bold; 
            font-size: 20px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
   ⴰⵣⵓⵍ ⴼⴻⵍⵍⴰⵡⴻⵏ
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #8B4513; 
            font-weight: bold; 
            font-size: 20px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
   🔢 Résolution de problèmes linéaires à deux variables
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-family: Tifinaghe-Ircam Unicode sans serif;">
  <p style="color: #8B4513; 
            font-weight: bold; 
            font-size: 20px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
   ⴰⵣⵓⵍ ⴼⴻⵍⵍⴰⵡⴻⵏ
  </p>
</div>
""", unsafe_allow_html=True)



st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #3366FF; 
            font-weight: bold; 
            font-size: 18px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
    Développé par: Hachemi Mokrane • Septembre 2025
  </p>
</div>
""", unsafe_allow_html=True)

# Choix max/min et saisie de la fonction objectif
st.markdown("**Fonction économique max ou min suivi de : ax + by**")
objectif = st.text_input("Fonction économique: ")  

# Nombre de contraintes
n_contraintes = st.number_input("Nombre de contraintes", min_value=1, max_value=10, value=2, step=1)

# Saisie des contraintes
contraintes = []
for i in range(n_contraintes):
    contrainte = st.text_input(f"Contrainte {i+1} (ex: 2x + 3y <= 12)")  
    if contrainte:
        for op in ['<=', '>=', '==', '=']:
            if op in contrainte:
                lhs, rhs = contrainte.split(op, 1)
                contraintes.append((lhs.strip(), op.strip(), float(rhs.strip())))
                break

# Option pour afficher le graphique
afficher_graphique = st.checkbox("Afficher la représentation graphique")

if st.button("Résoudre"):
    if not objectif:
        st.error("Veuillez entrer une fonction économique valide.")
    else:
        # Type du problème
        if objectif.lower().startswith("max"):
            modele_type = LpMaximize
            expr = objectif[3:].strip()
        elif objectif.lower().startswith("min"):
            modele_type = LpMinimize
            expr = objectif[3:].strip()
        else:
            st.error("La fonction doit commencer par 'max' ou 'min'.")
            st.stop()
        
        probleme = LpProblem("Probleme_Lineaire", modele_type)
        termes_objectif = parse_expression(expr)
        
        # Collecte des variables
        variables = set()
        for coeff, var in termes_objectif:
            variables.add(var)
        for lhs, _, _ in contraintes:
            for coeff, var in parse_expression(lhs):
                variables.add(var)
        variables = sorted(variables)
        
        if len(variables) != 2:
            st.error("⚠️ La résolution est disponible uniquement pour 2 variables (ex: x et y).")
            st.stop()
        
        # Création des variables PuLP
        lp_vars = LpVariable.dicts("Var", variables, lowBound=0)
        
        # Fonction objectif
        probleme += sum(coeff * lp_vars[var] for coeff, var in termes_objectif)
        
        # Contraintes
        for lhs, op, rhs in contraintes:
            expr = sum(coeff * lp_vars[var] for coeff, var in parse_expression(lhs))
            if op == '<=':
                probleme += expr <= rhs
            elif op == '>=':
                probleme += expr >= rhs
            else:
                probleme += expr == rhs
        
        # Résolution
        probleme.solve()
        
        # Résultats
        st.subheader("Résultats de l'optimisation")
        st.write("**Statut :**", LpStatus[probleme.status])
        
        # Récupération des valeurs des variables
        solution = {}
        for var in variables:
            val = lp_vars[var].varValue
            solution[var] = val
        
        # Formatage de l'affichage selon votre demande
        if len(variables) == 2:
            var1, var2 = variables
            x_val = solution[var1]
            y_val = solution[var2]
            
            # Affichage au format (x;y) z=
            st.write(f"**Solution optimale :** ({var1};{var2}) = ({x_val:.2f};{y_val:.2f})")
        
        optimal_value = probleme.objective.value()
        st.write(f"**Valeur optimale :** z = {optimal_value:.2f}")
        
        # Affichage détaillé supplémentaire
        st.write("**Détail des valeurs :**")
        for var in variables:
            st.write(f"- {var} = {solution[var]:.2f}")
        
        # Affichage du graphique si demandé
        if afficher_graphique:
            st.subheader("📈 Représentation Graphique")
            try:
                if x_val is not None and y_val is not None:
                    fig = plot_solution_graphique(contraintes, x_val, y_val, variables)
                    st.pyplot(fig)
                    
                    # Explication du graphique
                    st.markdown("""
                    **Légende du graphique :**
                    - **Lignes colorées** : Représentent les contraintes
                    - **Zone ombrée** : Zone réalisable pour chaque contrainte
                    - **Point rouge** : Solution optimale trouvée
                    """)
                else:
                    st.warning("Impossible d'afficher le graphique : solution non trouvée")
            except Exception as e:
                st.warning(f"Impossible d'afficher le graphique : {e}")
        
        # Information supplémentaire
        st.markdown("---")
        st.subheader("📋 Résumé")
        st.write(f"**Fonction économique :** {objectif}")
        st.write("**Contraintes :**")
        for i, (lhs, op, rhs) in enumerate(contraintes, 1):
            st.write(f"{i}. {lhs} {op} {rhs}")

# Instructions d'utilisation
with st.expander("ℹ️ Instructions d'utilisation"):
    st.markdown("""
    **Comment utiliser cette application :**
    
    1. **Fonction économique** : Entrez "max" ou "min" suivi de l'expression (ex: `max 3x + 5y`)
    2. **Nombre de contraintes** : Sélectionnez le nombre de contraintes
    3. **Contraintes** : Entrez chaque contrainte (ex: `2x + 3y <= 12`)
    4. **Graphique** : Cochez la case pour voir la représentation graphique
    5. **Résoudre** : Cliquez sur le bouton "Résoudre"
    
    **Exemple complet :**
    - Fonction : `min 35x + 34y`
    - Contrainte 1 : `4x + 3y >= 504`
    - Contrainte 2 : `5x + y >= 256`
    - Contrainte 3 : `2x + 5y >= 240`
    """)
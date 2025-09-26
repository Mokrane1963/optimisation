# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 12:59:11 2025

@author: mokrane
"""

import streamlit as st
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus
import re

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

# ------------------------
# Interface Streamlit
# ------------------------


st.markdown("""
<div style="text-align: center; font-family: courier;">
  
  <p style="color: #8B4513; 
            font-weight: bold; 
            font-size: 20px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(rgba(0,0,0,0.1));">
   🔢 Résolution de problèmes linéaires à deux  variables
  </p>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div style="text-align: center; font-family: courier;">

  <p style="color: #3366FF; 
            font-weight: bold; 
            font-size: 18px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(rgba(0,0,0,1.1));">
    Développé par: Hachemi Mokrane • Septembre 2025
  </p>
</div>
""", unsafe_allow_html=True)

# Choix max/min et saisie de la fonction objectif
st.markdown("**Fonction économique  max ou min suivi de :ax + by**")
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
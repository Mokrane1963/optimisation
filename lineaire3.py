# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 14:23:52 2025

@author: mokrane
"""

import streamlit as st
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus
import re

# --- Fonction d’analyse d’une expression linéaire ---
def parse_expression(expr):
    """Parse une expression linéaire en liste de (coefficient, variable)."""
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


# --- Application principale Streamlit ---
def main():
    st.set_page_config(page_title="Solveur de Programmation Linéaire", layout="centered")
    st.title("🔢 Résolution de problèmes linéaires à trois variables")

    # ------------------------
    # Interface Streamlit
    # ------------------------


    st.markdown("""
    <div style="text-align: center; font-family: Tifinaghe-Ircam Unicode sans serif;">
      <p style="color: #8B4513; 
                font-weight: bold; 
                font-size: 24px; 
                margin-top: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
       ⴰⵣⵓⵍ ⴼⴻⵍⴰⵡⴻⵏ
      </p>
    </div>
    """, unsafe_allow_html=True)



    st.markdown("""
    <div style="text-align: center; font-family: courier;">
      <p style="color: #3366FF; 
                font-weight: bold; 
                font-size: 18px; 
                margin-top: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
        Développé par: Hachemi Mokrane • Septembre 2025
      </p>
    </div>
    """, unsafe_allow_html=True)


    # Choix du type de problème
    modele_type_str = st.radio("Type de problème :", ["Maximisation", "Minimisation"])
    modele_type = LpMaximize if modele_type_str == "Maximisation" else LpMinimize

    # Fonction objectif
    expr_objectif = st.text_input("Entrez la fonction économique (ex: 3x + 5y + 2z) :", "")

    # Nombre de contraintes
    n_contraintes = st.number_input("Nombre de contraintes :", min_value=1, max_value=10, step=1, value=3)

    contraintes = []
    for i in range(int(n_contraintes)):
        contraintes.append(st.text_input(f"Contrainte {i+1} (ex: 2x + 3y +z <= 12, x>=0,y>=0,z>=0) :", key=f"c{i}"))

    if st.button("Résoudre"):
        if not expr_objectif.strip():
            st.error("Veuillez entrer la fonction économique.")
            return

        # Création du problème
        probleme = LpProblem("Probleme_Lineaire", modele_type)
        termes_objectif = parse_expression(expr_objectif)

        # Analyse des contraintes
        contraintes_parsed = []
        for c in contraintes:
            if not c.strip():
                continue
            for op in ['<=', '>=', '==', '=']:
                if op in c:
                    lhs, rhs = c.split(op, 1)
                    contraintes_parsed.append((lhs.strip(), op.strip(), float(rhs.strip())))
                    break

        # Collecte des variables
        variables = set(var for _, var in termes_objectif)
        for lhs, _, _ in contraintes_parsed:
            for _, var in parse_expression(lhs):
                variables.add(var)

        # Création des variables PuLP
        lp_vars = LpVariable.dicts("Var", variables, lowBound=0)

        # Ajout de la fonction objectif
        probleme += sum(coeff * lp_vars[var] for coeff, var in termes_objectif)

        # Ajout des contraintes
        for lhs, op, rhs in contraintes_parsed:
            expr = sum(coeff * lp_vars[var] for coeff, var in parse_expression(lhs))
            if op == '<=':
                probleme += expr <= rhs
            elif op == '>=':
                probleme += expr >= rhs
            else:
                probleme += expr == rhs

        # Résolution
        probleme.solve()

        # Affichage des résultats
        st.subheader("📊 Résultats")
        st.write(f"**Statut :** {LpStatus[probleme.status]}")
        st.write("Statut : **(LpStatus[model.status]")
        resultats = {var.name: var.varValue for var in lp_vars.values()}
        st.table(resultats.items())

        st.success(f"**Valeur optimale = {probleme.objective.value():.3f}**")


if __name__ == "__main__":
    main()

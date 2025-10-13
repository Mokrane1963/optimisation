# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 14:23:52 2025

@author: mokrane
"""

import streamlit as st
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus
import re
import pandas as pd


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

    st.markdown("""
    <div style="text-align: center; font-family: courier;">
      <p style="color: #3366FF; font-weight: bold; font-size: 18px; margin-top: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
        Développé par: Hachemi Mokrane • Septembre 2025
      </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Bandeau Amazigh ---
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

    # --- 🎨 Correction du style des boutons ---
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
        box-shadow: 0 0 15px rgba(255, 140, 0, 0.6);
        transform: scale(1.05);
    }
    section[data-testid="stSidebar"] div.stButton > button {
        background: linear-gradient(135deg, #00C9FF, #92FE9D);
        color: black !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: linear-gradient(135deg, #92FE9D, #00C9FF);
        color: black !important;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 🎨 Fond dégradé ---
    st.sidebar.header("🎨 Fond dégradé de la page")
    gradient_type = st.sidebar.selectbox("Type de dégradé", ["linear-gradient", "radial-gradient"])
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

    # === Paramètres du problème linéaire ===
    modele_type_str = st.radio("Type de problème :", ["Maximisation", "Minimisation"])
    modele_type = LpMaximize if modele_type_str == "Maximisation" else LpMinimize

    expr_objectif = st.text_input("Entrez la fonction économique (ex: 3x + 5y + 2z) :", "3x + 5y + 2z")

    n_contraintes = st.number_input("Nombre de contraintes :", min_value=1, max_value=10, step=1, value=4)

    contraintes = []
    for i in range(int(n_contraintes)):
        contraintes.append(st.text_input(f"Contrainte {i+1} (ex: 2x + 3y + z <= 12) :", key=f"c{i}"))

    # === Résolution du problème ===
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
        lp_vars = LpVariable.dicts("", variables, lowBound=0)

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

        # --- Résultats ---
        st.subheader("📊 Résultats du problème linéaire")
        st.write(f"**Statut :** {LpStatus[probleme.status]}")

        # Tableau des valeurs optimales
        resultats = {var_name: v.varValue for var_name, v in lp_vars.items()}
        df_resultats = pd.DataFrame({
            "Variable": list(resultats.keys()),
            "Valeur": list(resultats.values())
        })

        st.table(df_resultats)

        # Valeur optimale
        st.success(f"**Valeur optimale = {probleme.objective.value():.3f}**")


# --- Lancement de l'application ---
if __name__ == "__main__":
    main()


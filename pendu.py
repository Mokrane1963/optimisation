# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 19:17:23 2025

@author: mokrane
"""

import streamlit as st
import random
import string

# -------------------------
# Dictionnaires de mots
# -------------------------
dictionnaire = {
    "Informatique & IA": [
        "algorithme", "reseau", "donnees", "apprentissage",
        "classification", "clustering", "neuronnes", "intelligence",
        "supervise", "non_supervise", "gradient", "perceptron",
        "deep", "reinforcement", "cloud", "python", "matrice",
        "vecteur", "pipeline", "automatisation", "optimisation",
        "token", "chatbot", "modele", "dataset", "overfitting",
        "sous_apprentissage", "normalisation", "backpropagation"
    ],
    "Instructions Python": [
        "print", "input", "if", "else", "elif", "for", "while",
        "break", "continue", "def", "return", "lambda", "yield",
        "import", "from", "as", "class", "try", "except",
        "finally", "raise", "with", "assert", "pass", "global",
        "nonlocal", "True", "False", "None", "in", "is", "and", "or", "not"
    ]
}

# -------------------------
# Initialisation de l'état Streamlit
# -------------------------
if "mot" not in st.session_state:
    st.session_state.categorie = None
    st.session_state.mot = None
    st.session_state.devines = []
    st.session_state.chances = 12

# -------------------------
# Interface
# -------------------------
st.title("🎮 Jeu du mot caché (Clavier Virtuel)")

# Choix de la catégorie
if st.session_state.mot is None:
    st.subheader("👉 Choisissez une catégorie pour commencer :")
    choix = st.radio("Catégorie :", list(dictionnaire.keys()))
    if st.button("Démarrer le jeu"):
        st.session_state.categorie = choix
        st.session_state.mot = random.choice(dictionnaire[choix]).lower()
        st.session_state.devines = []
        st.session_state.chances = 12
        st.rerun()
else:
    mot = st.session_state.mot
    devines = st.session_state.devines
    chances = st.session_state.chances

    st.write(f"📌 Catégorie choisie : **{st.session_state.categorie}**")
    
    # Affichage du mot avec lettres trouvées à la bonne position
    affichage = ""
    echoue = 0
    for caractere in mot:
        if caractere in devines:
            affichage += caractere + " "
        else:
            affichage += "_ "
            echoue += 1
    st.subheader(affichage.strip())

    # Vérification si gagné
    if echoue == 0:
        st.success(f"🎉 Bravo ! Le mot était bien **{mot}**")
        if st.button("Rejouer"):
            st.session_state.clear()
            st.rerun()
        st.stop()

    # Clavier virtuel
    st.subheader("Cliquez sur une lettre :")
    lettres = string.ascii_lowercase
    cols = st.columns(13)
    for i, lettre in enumerate(lettres):
        if lettre not in devines:
            if cols[i % 13].button(lettre.upper()):
                st.session_state.devines.append(lettre)
                if lettre not in mot:
                    st.session_state.chances -= 1
                st.rerun()
        else:
            cols[i % 13].write(" ")  # case vide pour les lettres déjà choisies

    st.write(f"💡 Chances restantes : {st.session_state.chances}")

    # Vérification si perdu
    if st.session_state.chances <= 0:
        st.error(f"💀 Tu as perdu ! Le mot était **{mot}**")
        if st.button("Rejouer"):
            st.session_state.clear()
            st.rerun()

# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 11:43:37 2025

@author: mokrane
"""

# app.py
import streamlit as st
import random
import time

st.set_page_config(page_title="Thlata da", page_icon="🤖", layout="centered")

# --- aide ---
def init_state():
    if "bordure" not in st.session_state:
        st.session_state.bordure = [["" for _ in range(3)] for _ in range(3)]
    if "gagnant" not in st.session_state:
        st.session_state.gagnant = None
    if "cellule_gagnant" not in st.session_state:
        st.session_state.cellule_gagnant = []
    if "en_attente" not in st.session_state:
        st.session_state.en_attente = False
    if "difficulte" not in st.session_state:
        st.session_state.difficulte = "Moyen"

def symbol(cellule):
    if cellule == "R": return "🔴"
    if cellule == "B": return "🔵"
    return "◻️"

def verifie_gagnant(bordure):
    lignes = []
    for i in range(3):
        lignes.append([(i, 0), (i, 1), (i, 2)])
    for j in range(3):
        lignes.append([(0, j), (1, j), (2, j)])
    lignes.append([(0, 0), (1, 1), (2, 2)])
    lignes.append([(0, 2), (1, 1), (2, 0)])

    for ligne in lignes:
        a, b, c = ligne
        va, vb, vc = bordure[a[0]][a[1]], bordure[b[0]][b[1]], bordure[c[0]][c[1]]
        if va != "" and va == vb == vc:
            return va, ligne
    return None, []

def verifie_egalite(bordure):
    return all(bordure[x][y] != "" for x in range(3) for y in range(3))

def jouer_coup(i, j, joueur):
    if st.session_state.bordure[i][j] != "" or st.session_state.gagnant:
        return
    st.session_state.bordure[i][j] = joueur
    w, cellules = verifie_gagnant(st.session_state.bordure)
    if w:
        st.session_state.gagnant = w
        st.session_state.cellule_gagnant = cellules
    elif verifie_egalite(st.session_state.bordure):
        st.session_state.gagnant = "Egalité"

def reset():
    st.session_state.bordure = [["" for _ in range(3)] for _ in range(3)]
    st.session_state.gagnant = None
    st.session_state.cellule_gagnant = []
    st.session_state.en_attente = False

# --- Minimax ---
def minimax(bordure, profendeur, est_maximum):
    gagnant, _ = verifie_gagnant(bordure)
    if gagnant == "B": return 1
    if gagnant == "R": return -1
    if verifie_egalite(bordure): return 0

    if est_maximum:  # ordinateur
        meilleur_score = -999
        for i in range(3):
            for j in range(3):
                if bordure[i][j] == "":
                    bordure[i][j] = "B"
                    score = minimax(bordure, profendeur + 1, False)
                    bordure[i][j] = ""
                    meilleur_score = max(meilleur_score, score)
        return meilleur_score
    else:  # joueur
        meilleur_score = 999
        for i in range(3):
            for j in range(3):
                if bordure[i][j] == "":
                    bordure[i][j] = "R"
                    score = minimax(bordure, profendeur + 1, True)
                    bordure[i][j] = ""
                    meilleur_score = min(meilleur_score, score)
        return meilleur_score

def meilleur_deplacement():
    meilleur_score = -999
    deplacement = None
    for i in range(3):
        for j in range(3):
            if st.session_state.bordure[i][j] == "":
                st.session_state.bordure[i][j] = "B"
                score = minimax(st.session_state.bordure, 0, False)
                st.session_state.bordure[i][j] = ""
                if score > meilleur_score:
                    meilleur_score = score
                    deplacement = (i, j)
    return deplacement

# --- Choix IA selon difficulté ---
def tour_ordinateur():
    if st.session_state.gagnant:
        return
    vide = [(i, j) for i in range(3) for j in range(3) if st.session_state.bordure[i][j] == ""]
    if not vide: return

    deplacement = None
    if st.session_state.difficulte == "Facile":
        deplacement = random.choice(vide)  # hasard total
    elif st.session_state.difficulte == "Moyen":
        if random.random() < 0.5:  # moitié du temps hasard
            deplacement = random.choice(vide)
        else:
            deplacement =meilleur_deplacement()
    else:  # Difficile
        deplacement =meilleur_deplacement()

    if deplacement:
        time.sleep(0.5)  # délai visuel pour simuler réflexion
        jouer_coup(deplacement[0], deplacement[1], "B")

# --- Init ---
init_state()

# --- L'IA joue si en attente ---
if st.session_state.en_attente and st.session_state.gagnant is None:
    tour_ordinateur()
    st.session_state.en_attente = False

# --- UI ---
st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #3366FF; 
            font-weight: bold; 
            font-size: 20px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    Développé par: Hachemi Mokrane • Septembre 2025
  </p>
</div>
""", unsafe_allow_html=True)
st.title(" Thlatha da ")
st.write("Vous jouez 🔴. L’ordinateur joue 🔵.")

# Sélecteur de difficulté
st.session_state.difficulte = st.radio(
    "Difficulté de l’ordinateur :",
    ["Facile", "Moyen", "Difficile"],
    index=["Facile", "Moyen", "Difficile"].index(st.session_state.difficulte)
)

col1, col2, col3 = st.columns([1,6,1])
with col2:
    if st.session_state.gagnant is None:
        st.markdown("**À vous de jouer !**")
    elif st.session_state.gagnant == "egalite":
        st.markdown("**Match nul !**")
    else:
        gagnant = "Vous (🔴)" if st.session_state.gagnant == "R" else "Ordinateur (🔵)"
        st.markdown(f"**Gagnant : {gagnant} 🎉**")

    st.write("")
    for i in range(3):
        colonnes = st.columns(3)
        for j in range(3):
            key = f"btn_{i}_{j}"
            cellule = st.session_state.bordure[i][j]
            etiquette = symbol(cellule)
            if (i, j) in st.session_state.cellule_gagnant:
                etiquette = "⭐ " + etiquette
            disabled = cellule != "" or st.session_state.gagnant is not None
            if colonnes[j].button(etiquette, key=key, disabled=disabled):
                jouer_coup(i, j, "R")   # joueur
                if st.session_state.gagnant is None:
                    st.session_state.en_attente = True  # IA jouera au prochain cycle
                st.rerun()  # montrer d'abord le coup du joueur

    st.write("")
    bordure_lignes = [" | ".join(symbol(c) for c in row) for row in st.session_state.bordure]
    st.text("\n".join(bordure_lignes))

    st.write("")
    if st.button("🔁 Recommencer"):
        reset()
        st.rerun()

st.write("---")
st.write("💡 Astuce : En *Facile*, l’ordinateur joue au hasard (tu peux gagner). En *Difficile*, il est imbattable !")

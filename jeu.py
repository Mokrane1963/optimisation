# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 11:43:37 2025

@author: mokrane
"""

# app.py
import streamlit as st
import random
import time

st.set_page_config(page_title="Thlatha IA", page_icon="🤖", layout="centered")
st.markdown("""
<div style="text-align: center; font-family: Tifinaghe-Ircam Unicode sans serif;">
  <p style="color: #8B4513; 
            font-weight: bold; 
            font-size: 24px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
   ⴰⵣⵓⵍ ⴼⴻⵍⴰⵡⴻⵏ
  </p>
</div>
""", unsafe_allow_html=True)

# --- Aide ---
def etat_iniale():
    if "bordure" not in st.session_state:
        st.session_state.bordure = [["" for _ in range(3)] for _ in range(3)]
    if "gagnant" not in st.session_state:
        st.session_state.gagnant = None
    if "cellule_gagnat" not in st.session_state:
        st.session_state.cellule_gagnat = []
    if "en_attente" not in st.session_state:
        st.session_state.en_attente = False
    if "difficulte" not in st.session_state:
        st.session_state.difficulte = "Moyen"

def symbole(cellule):
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

def verifie_nul(bordure):
    return all(bordure[x][y] != "" for x in range(3) for y in range(3))

def jouer_coup(i, j, player):
    if st.session_state.bordure[i][j] != "" or st.session_state.gagnant:
        return
    st.session_state.bordure[i][j] = player
    w, cellules = verifie_gagnant(st.session_state.bordure)
    if w:
        st.session_state.gagnant = w
        st.session_state.cellule_gagnat = cellules
    elif verifie_nul(st.session_state.bordure):
        st.session_state.gagnant = "Tie"

def renitialisation():
    st.session_state.bordure = [["" for _ in range(3)] for _ in range(3)]
    st.session_state.gagnant = None
    st.session_state.cellule_gagnat = []
    st.session_state.en_attente = False

# --- Minimax IA ---
def minimax(bordure, depth, is_maximizing):
    gagnant, _ = verifie_gagnant(bordure)
    if gagnant == "B": return 1
    if gagnant == "R": return -1
    if verifie_nul(bordure): return 0

    if is_maximizing:  # ordinateur
        score_ilhan = -999
        for i in range(3):
            for j in range(3):
                if bordure[i][j] == "":
                    bordure[i][j] = "B"
                    score = minimax(bordure, depth + 1, False)
                    bordure[i][j] = ""
                    score_ilhan = max(score_ilhan, score)
        return score_ilhan
    else:  # joueur
        score_ilhan = 999
        for i in range(3):
            for j in range(3):
                if bordure[i][j] == "":
                    bordure[i][j] = "R"
                    score = minimax(bordure, depth + 1, True)
                    bordure[i][j] = ""
                    score_ilhan = min(score_ilhan, score)
        return score_ilhan

def meilleur_coup():
    score_ilhan = -999
    deplacement = None
    for i in range(3):
        for j in range(3):
            if st.session_state.bordure[i][j] == "":
                st.session_state.bordure[i][j] = "B"
                score = minimax(st.session_state.bordure, 0, False)
                st.session_state.bordure[i][j] = ""
                if score > score_ilhan:
                    score_ilhan = score
                    deplacement = (i, j)
    return deplacement

# --- Choix IA selon difficulté ---
def tour_ordinateur():
    if st.session_state.gagnant:
        return
    empty = [(i, j) for i in range(3) for j in range(3) if st.session_state.bordure[i][j] == ""]
    if not empty: return

    deplacement = None
    if st.session_state.difficulte == "Facile":
        deplacement = random.choice(empty)  # hasard total
    elif st.session_state.difficulte == "Moyen":
        if random.random() < 0.5:  # moitié du temps hasard
            deplacement = random.choice(empty)
        else:
            deplacement = meilleur_coup()
    else:  # Difficile
        deplacement = meilleur_coup()

    if deplacement:
        time.sleep(0.5)  # délai visuel pour simuler réflexion
        jouer_coup(deplacement[0], deplacement[1], "B")

# --- Init ---
etat_iniale()

# --- L'IA joue si en attente ---
if st.session_state.en_attente and st.session_state.gagnant is None:
    tour_ordinateur()
    st.session_state.en_attente = False

# --- UI ---
st.title("Urar  Thlata da")
st.write("Vous jouez 🔴. L’ordinateur joue 🔵.")

# Sélecteur de difficulté
st.session_state.difficulte = st.radio(
    "Difficulté de l’ordinateur :",
    ["ishel", "citoh", "yu3ar"],
    index=["ishel", "citoh", "yu3ar"].index(st.session_state.difficulte)
)

col1, col2, col3 = st.columns([1,6,1])

# Affichage du statut (toujours visible)
if st.session_state.gagnant is None:
    st.markdown("**d nuvak turart !**")
elif st.session_state.gagnant == "Tie":
    st.markdown("**yiwen ur irvih !** 🤝")
else:
    gagnant = "d kecc (🔴)" if st.session_state.gagnant == "R" else "Ordinateur (🔵)"
    st.markdown(f"### 🏆 irevhen  : {gagnant} 🎉")

st.write("")

# Plateau
col1, col2, col3 = st.columns([1,6,1])
with col2:
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            cle = f"btn_{i}_{j}"
            cellule = st.session_state.bordure[i][j]
            etiquette = symbole(cellule)
            if (i, j) in st.session_state.cellule_gagnat:
                etiquette = "⭐ " + etiquette
            disabled = cellule != "" or st.session_state.gagnant is not None
            if cols[j].button(etiquette, cle=cle, disabled=disabled):
                jouer_coup(i, j, "R")
                if st.session_state.gagnant is None:
                    st.session_state.en_attente = True
                st.rerun()

    st.write("")
    bordure_lignes = [" | ".join(symbole(c) for c in row) for row in st.session_state.bordure]
    st.text("\n".join(bordure_lignes))

    st.write("")
    if st.button("🔁 Recommencer"):
        renitialisation()
        st.rerun()

st.write("---")
st.write("💡 Astuce: En *Facile*, l’ordinateur joue au hasard (tu peux gagner). En *Difficile*, il est imbattable !")

# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 11:43:37 2025

@author: mokrane
"""

# app.py
import streamlit as st
import random
import time

st.set_page_config(page_title="Morpion IA", page_icon="🤖", layout="centered")

# --- Helpers ---
def init_state():
    if "board" not in st.session_state:
        st.session_state.board = [["" for _ in range(3)] for _ in range(3)]
    if "winner" not in st.session_state:
        st.session_state.winner = None
    if "winning_cells" not in st.session_state:
        st.session_state.winning_cells = []
    if "pending_ai" not in st.session_state:
        st.session_state.pending_ai = False
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Moyen"

def symbol(cell):
    if cell == "R": return "🔴"
    if cell == "B": return "🔵"
    return "◻️"

def check_winner(board):
    lines = []
    for i in range(3):
        lines.append([(i, 0), (i, 1), (i, 2)])
    for j in range(3):
        lines.append([(0, j), (1, j), (2, j)])
    lines.append([(0, 0), (1, 1), (2, 2)])
    lines.append([(0, 2), (1, 1), (2, 0)])

    for line in lines:
        a, b, c = line
        va, vb, vc = board[a[0]][a[1]], board[b[0]][b[1]], board[c[0]][c[1]]
        if va != "" and va == vb == vc:
            return va, line
    return None, []

def check_tie(board):
    return all(board[x][y] != "" for x in range(3) for y in range(3))

def play_move(i, j, player):
    if st.session_state.board[i][j] != "" or st.session_state.winner:
        return
    st.session_state.board[i][j] = player
    w, cells = check_winner(st.session_state.board)
    if w:
        st.session_state.winner = w
        st.session_state.winning_cells = cells
    elif check_tie(st.session_state.board):
        st.session_state.winner = "Tie"

def reset():
    st.session_state.board = [["" for _ in range(3)] for _ in range(3)]
    st.session_state.winner = None
    st.session_state.winning_cells = []
    st.session_state.pending_ai = False

# --- Minimax IA ---
def minimax(board, depth, is_maximizing):
    winner, _ = check_winner(board)
    if winner == "B": return 1
    if winner == "R": return -1
    if check_tie(board): return 0

    if is_maximizing:  # ordinateur
        best_score = -999
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    board[i][j] = "B"
                    score = minimax(board, depth + 1, False)
                    board[i][j] = ""
                    best_score = max(best_score, score)
        return best_score
    else:  # joueur
        best_score = 999
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    board[i][j] = "R"
                    score = minimax(board, depth + 1, True)
                    board[i][j] = ""
                    best_score = min(best_score, score)
        return best_score

def best_move():
    best_score = -999
    move = None
    for i in range(3):
        for j in range(3):
            if st.session_state.board[i][j] == "":
                st.session_state.board[i][j] = "B"
                score = minimax(st.session_state.board, 0, False)
                st.session_state.board[i][j] = ""
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move

# --- Choix IA selon difficulté ---
def computer_play():
    if st.session_state.winner:
        return
    empty = [(i, j) for i in range(3) for j in range(3) if st.session_state.board[i][j] == ""]
    if not empty: return

    move = None
    if st.session_state.difficulty == "Facile":
        move = random.choice(empty)  # hasard total
    elif st.session_state.difficulty == "Moyen":
        if random.random() < 0.5:  # moitié du temps hasard
            move = random.choice(empty)
        else:
            move = best_move()
    else:  # Difficile
        move = best_move()

    if move:
        time.sleep(0.5)  # délai visuel pour simuler réflexion
        play_move(move[0], move[1], "B")

# --- Init ---
init_state()

# --- L'IA joue si en attente ---
if st.session_state.pending_ai and st.session_state.winner is None:
    computer_play()
    st.session_state.pending_ai = False

# --- UI ---
st.title("Urar  Thlata da")
st.write("Vous jouez 🔴. L’ordinateur joue 🔵.")

# Sélecteur de difficulté
st.session_state.difficulty = st.radio(
    "Difficulté de l’ordinateur :",
    ["Facile", "Moyen", "Difficile"],
    index=["Facile", "Moyen", "Difficile"].index(st.session_state.difficulty)
)

col1, col2, col3 = st.columns([1,6,1])

# Affichage du statut (toujours visible)
if st.session_state.winner is None:
    st.markdown("**À vous de jouer !**")
elif st.session_state.winner == "Tie":
    st.markdown("**Match nul !** 🤝")
else:
    gagnant = "Vous (🔴)" if st.session_state.winner == "R" else "Ordinateur (🔵)"
    st.markdown(f"### 🏆 Gagnant : {gagnant} 🎉")

st.write("")

# Plateau
col1, col2, col3 = st.columns([1,6,1])
with col2:
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            key = f"btn_{i}_{j}"
            cell = st.session_state.board[i][j]
            label = symbol(cell)
            if (i, j) in st.session_state.winning_cells:
                label = "⭐ " + label
            disabled = cell != "" or st.session_state.winner is not None
            if cols[j].button(label, key=key, disabled=disabled):
                play_move(i, j, "R")
                if st.session_state.winner is None:
                    st.session_state.pending_ai = True
                st.rerun()

    st.write("")
    board_lines = [" | ".join(symbol(c) for c in row) for row in st.session_state.board]
    st.text("\n".join(board_lines))

    st.write("")
    if st.button("🔁 Recommencer"):
        reset()
        st.rerun()

st.write("---")
st.write("💡 Astuce: En *Facile*, l’ordinateur joue au hasard (tu peux gagner). En *Difficile*, il est imbattable !")

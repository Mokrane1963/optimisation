# -*- coding: utf-8 -*-
"""
Created on Sun Oct 19 12:06:36 2025

@author: mokrane
"""

import streamlit as st
import pandas as pd
from collections import defaultdict
import json
import os

# =========================
# 🎨 CONFIGURATION DE LA PAGE
# =========================
st.set_page_config(layout="wide", page_title="Amawal - Dictionnaire Amazigh", page_icon="📖")

# ---------- STYLE GLOBAL ----------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f5f7fa, #dbe9ff);
    color: #222;
    font-family: 'Segoe UI', sans-serif;
}

.header {
    color: #2563eb;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 10px;
    font-size: 42px !important;
    text-align: center;
    margin-bottom: 5px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.subtitle {
    text-align: center;
    font-size: 16px;
    color:#3b82f6;
    margin-bottom: 40px;
}

.word-detail {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 25px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}
.word-detail:hover {
    transform: scale(1.01);
    box-shadow: 0 6px 12px rgba(0,0,0,0.08);
}
p, li, div {
    font-size: 18px !important;
}
.arabic {
    font-family: 'Traditional Arabic', Arial;
    font-size: 22px !important;
    color: #111827;
}
.success-message {
    text-align: center;
    font-weight: bold;
    color: #1d4ed8;
    font-size: 18px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}
.footer {
    text-align: center;
    font-size: 15px;
    color: #2563eb;
    margin-top: 40px;
    font-style: italic;
}

/* Animation pour le symbole Amazigh */
.flag {
    font-size: 60px;
    animation: float 2s ease-in-out infinite;
    color: #e63946;
    text-shadow: 0px 0px 8px rgba(255,0,0,0.4);
}
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
    100% { transform: translateY(0px); }
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🏴 EN-TÊTE AVEC SYMBOLE AMAZIGH ⵣ
# =========================

st.markdown("""
<div style="text-align:center; margin-top:-10px;">
  <span class="flag">ⵣ</span>
  <h1 class='header'>Amawal s Tmazight</h1>
  <p class='subtitle'>📘 Dictionnaire bilingue Tamazight - Français</p>
  <p style="color: #2563eb; font-weight: bold; font-size: 17px; margin-top: 5px; font-family:courier;">
    Développé par : <span style="color:#1d4ed8;">Hachemi Mokrane</span> • Septembre 2025
  </p>
</div>
""", unsafe_allow_html=True)

# =========================
# ⚙️ INITIALISATION
# =========================
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()

@st.cache_data
def load_excel(filepath):
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        if len(df.columns) < 3:
            st.error("Le fichier doit contenir au moins 3 colonnes : Mot, Définition, Phrase")
            return None

        dict_mots = defaultdict(dict)
        for _, row in df.iterrows():
            mot = str(row[0]).strip()
            definition = str(row[1]).strip()
            phrase = str(row[2]).strip()
            dict_mots[mot] = {
                'définition': definition,
                'phrase': phrase,
                'longueur': len(mot),
                'position': hash(mot) % 1000
            }
        return dict_mots
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        return None

# =========================
# 🧭 SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Options")
    export_format = st.radio("Format d'export :", ["TXT", "JSON"])
    st.divider()
    st.header("⭐ Favoris")
    if st.session_state.favorites:
        for fav in sorted(st.session_state.favorites):
            if st.button(f"❌ {fav}", key=f"remove_{fav}"):
                st.session_state.favorites.remove(fav)
                st.rerun()
    else:
        st.info("Aucun favori pour le moment.")

# =========================
# 📚 CHARGEMENT DU FICHIER
# =========================
file_path = os.path.join(os.path.dirname(__file__), "Amaoual.xlsx")

if not os.path.exists(file_path):
    st.error(f"❌ Le fichier '{file_path}' est introuvable.")
else:
    dict_mots = load_excel(file_path)

    if dict_mots:
        search_query = st.text_input("🔍 Recherche un mot ou une définition :", placeholder="Tapez un mot en Tamazight ou en Français...")

        filtered_words = [
            mot for mot in dict_mots
            if not search_query or 
               search_query.lower() in mot.lower() or 
               search_query.lower() in dict_mots[mot]['définition'].lower() or
               search_query.lower() in dict_mots[mot]['phrase'].lower()
        ] or list(dict_mots.keys())

        if filtered_words:
            selected_word = st.selectbox("📖 Sélectionnez un mot :", sorted(filtered_words))
            details = dict_mots[selected_word]

            # --- Actions principales ---
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⭐ Ajouter aux favoris" if selected_word not in st.session_state.favorites else "★ Retirer des favoris"):
                    if selected_word in st.session_state.favorites:
                        st.session_state.favorites.remove(selected_word)
                    else:
                        st.session_state.favorites.add(selected_word)
                    st.rerun()
            with col2:
                if export_format == "TXT":
                    txt_data = f"{selected_word}\nDéfinition: {details['définition']}\nContexte: {details['phrase']}"
                    st.download_button(
                        label="📄 Exporter en TXT",
                        data=txt_data,
                        file_name=f"dictionnaire_{selected_word}.txt",
                        mime="text/plain"
                    )
                else:
                    json_data = json.dumps({selected_word: details}, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📝 Exporter en JSON",
                        data=json_data,
                        file_name=f"dictionnaire_{selected_word}.json",
                        mime="application/json"
                    )

            # --- Affichage du mot sélectionné ---
            st.markdown('<div class="word-detail">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:#1d4ed8;'>{selected_word.upper()}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p class='arabic'>{details['définition']}</p>", unsafe_allow_html=True)
            st.divider()
            

            # --- Message de fin ---
            st.markdown("<p class='success-message'>❤️ Tanemirt-nwen  ❤️</p>", unsafe_allow_html=True)
        else:
            st.warning("Aucun mot ne correspond à votre recherche.")

# =========================
# 👣 PIED DE PAGE
# =========================
st.markdown("<p class='footer'>© 2025 - Projet linguistique Amazigh • Tous droits réservés.</p>", unsafe_allow_html=True)

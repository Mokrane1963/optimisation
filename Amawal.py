# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 20:22:30 2025

@author: mokrane
"""

import streamlit as st
import pandas as pd
from collections import defaultdict
from io import BytesIO
import json
import os

# Configuration de la page
st.set_page_config(layout="wide", page_title="Dcitionnaire amazigh", page_icon="📖")
st.markdown("""
<style>
.subtitle {
    text-align: center;
    font-size: 14px;
    color:#3498db;
    margin-bottom: 20px;
}
.header {
    color: #4F8BF9;
    border-bottom: 3px solid #4F8BF6;
    padding-bottom: 10px;
    font-size: 36px !important;
    text-align: center;  /* ✅ centrage horizontal */
}
p, li, div {
    font-size: 18px !important;
}
.arabic {
    font-family: 'Traditional Arabic', Arial;
    font-size: 22px !important;
}
.word-detail {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header'>Amawal s t mazight</h1>", 
            
            
            
            unsafe_allow_html=True)


# Style CSS personnalisé
st.markdown("""
<style>
    .arabic { font-family: 'Traditional Arabic', Arial; font-size: 1.2em; }
    .word-detail { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .header { color: #4F8BF9; border-bottom: 2px solid #4F8BF6; padding-bottom: 10px; }
    .word-list { max-height: 600px; overflow-y: auto; }
    .favorite { color: #FF4B4B !important; }
    .search-box { margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #3366FF; font-weight: bold; font-size: 18px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    Développé par: Hachemi Mokrane • Septembre 2025
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.subtitle {
    text-align: left;
    font-size: 14px;
    color:#3498db;
    margin-bottom: 20px;
}
h1, h2, h3 {
    font-size: 26px !important;
}
p, li, div {
    font-size: 18px !important;
}
.arabic {
    font-family: 'Traditional Arabic', Arial;
    font-size: 22px !important;
}
.word-detail {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
}
.header {
    color: #4F8BF9;
    border-bottom: 3px solid #4F8BF6;
    padding-bottom: 10px;
    font-size: 30px !important;
}
</style>
""", unsafe_allow_html=True)

# Initialisation de la session
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()

# Fonction pour charger les données Excel
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



# Sidebar pour les fonctionnalités
with st.sidebar:
    st.header("⚙️ Fonctions")
    export_format = st.radio("Exporter en", ["TXT", "JSON"])
    st.divider()
    st.header("⭐ Favoris")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            if st.button(f"❌ {fav}", key=f"remove_{fav}"):
                st.session_state.favorites.remove(fav)
                st.rerun()

# 🔹 Chargement automatique du fichier amaoual.xlsx
file_path = os.path.join(os.path.dirname(__file__), "Amaoual.xlsx")

# Vérifier s’il existe
if not os.path.exists(file_path):
    st.error(f"❌ Le fichier '{file_path}' est introuvable dans le dossier de l’application.")
else:
    dict_mots = load_excel(file_path)

    if dict_mots:
        search_query = st.text_input("🔍 Recherche textuelle", placeholder="Entrez un mot ou une définition")

        # Filtrage par recherche
        filtered_words = [
            mot for mot in dict_mots
            if not search_query or 
               search_query.lower() in mot.lower() or 
               search_query.lower() in dict_mots[mot]['définition'].lower() or
               search_query.lower() in dict_mots[mot]['phrase'].lower()
        ] or list(dict_mots.keys())

        if filtered_words:
            selected_word = st.selectbox("Sélectionnez un mot :", filtered_words)
            details = dict_mots[selected_word]

            # Actions
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
                        label="📄 Exporter TXT",
                        data=txt_data,
                        file_name=f"dictionnaire_{selected_word}.txt",
                        mime="text/plain"
                    )
                else:
                    json_data = json.dumps({selected_word: details}, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📝 Exporter JSON",
                        data=json_data,
                        file_name=f"dictionnaire_{selected_word}.json",
                        mime="application/json"
                    )

            # Affichage des détails
            st.markdown('<div class="word-detail">', unsafe_allow_html=True)
            st.markdown(f"**{selected_word.upper()}**")
            st.markdown(f"<p class='arabic'>{details['définition']}</p>", unsafe_allow_html=True)
            st.divider()
            st.markdown("""
            <div style="text-align: center; font-family: courier;">
              <p style="color: #3366FF; font-weight: bold; font-size: 18px; margin-top: 10px;
                        text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
                 ❤️Merci d'avoir utiliser notre application  ❤️"
              </p>
            </div>
            """, unsafe_allow_html=True)
           
            st.divider()
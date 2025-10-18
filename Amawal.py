# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 20:22:30 2025

@author: mokrane
"""

import streamlit as st
import pandas as pd
from collections import defaultdict
from io import BytesIO
import os
import json  

# ============================================
# Configuration de la page
# ============================================
st.set_page_config(layout="wide", page_title="Asegzawal", page_icon="📖")

st.markdown("""
<style>
.subtitle {
    text-align: left;
    font-size: 10px;
    color:#3498db;
    margin-bottom: 20px;
}
</style>
<p class="subtitle">Asegzawal Tamazight→Tafrancist — programmé par : Hachemi Mokrane (Avril 2025)</p>
""", unsafe_allow_html=True)

# --- Style CSS personnalisé ---
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

# ============================================
# Initialisation de la session
# ============================================
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()

# ============================================
# Fonctions utilitaires
# ============================================

# Exporter en pseudo-PDF (texte brut dans un fichier téléchargeable)
def export_to_pdf(word, details):
    pdf_content = f"""
    Dictionnaire Linguistique - Fiche : {word}
    =========================================

    Définition : {details['définition']}
    Contexte : {details['phrase']}

    Métadonnées :
    - Longueur du mot : {details['longueur']}
    - Position : {details['position']}
    """
    return BytesIO(pdf_content.encode())

# Charger un fichier Excel (brut)
@st.cache_data
def load_excel(file):
    try:
        df = pd.read_excel(file, engine="openpyxl")
        if len(df.columns) < 3:
            st.error("Le fichier doit contenir au moins 3 colonnes : Mot, Définition, Phrase")
            return None

        dict_mots = defaultdict(dict)
        for _, row in df.iterrows():
            mot = str(row[0]).strip()
            definition = str(row[1]).strip()
            phrase = str(row[2]).strip()

            dict_mots[mot] = {
                "définition": definition,
                "phrase": phrase,
                "longueur": len(mot),
                "position": hash(mot) % 1000
            }

        return dict_mots

    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {str(e)}")
        return None

# Gestion sécurisée du chargement (fichier local ou téléversé)
def safe_load_excel(uploaded_file):
    try:
        if uploaded_file is not None and not isinstance(uploaded_file, str):
            # Lecture depuis fichier uploadé (bytes)
            file_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
            return load_excel(BytesIO(file_bytes))

        if isinstance(uploaded_file, str):
            if not os.path.exists(uploaded_file):
                st.error(f"Fichier introuvable : {uploaded_file}")
                return None
            return load_excel(uploaded_file)

        return None

    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return None

# ============================================
# Interface principale
# ============================================

st.markdown("<h1 class='header'>📖 Asegzawal</h1>", unsafe_allow_html=True)

# --- Barre latérale ---
with st.sidebar:
    st.header("⚙️ Fonctions")
    export_format = st.radio("Exporter en", ["TXT", "JSON"])
    st.divider()
    st.header("⭐ Favoris")
    if st.session_state.favorites:
        for fav in list(st.session_state.favorites):
            if st.button(f"❌ {fav}", key=f"remove_{fav}"):
                st.session_state.favorites.remove(fav)
                st.rerun()

# --- Zone principale ---
uploaded_file = st.file_uploader("📤 Téléversez votre fichier Excel", type=["xlsx", "xls"])
search_query = st.text_input("🔍 Recherche textuelle", placeholder="Entrez un mot ou une définition")

# Charger depuis fichier téléversé ou fichier local amaoual.xlsx
if uploaded_file:
    dict_mots = safe_load_excel(uploaded_file)
else:
    local_file = "amaoual.xlsx"
    dict_mots = safe_load_excel(local_file) if os.path.exists(local_file) else None

# ============================================
# Affichage du contenu
# ============================================
if dict_mots:
    filtered_words = [
        mot for mot in dict_mots
        if not search_query
        or search_query.lower() in mot.lower()
        or search_query.lower() in dict_mots[mot]["définition"].lower()
        or search_query.lower() in dict_mots[mot]["phrase"].lower()
    ] or list(dict_mots.keys())

    if filtered_words:
        selected_word = st.selectbox("Sélectionnez un mot :", filtered_words)
        details = dict_mots[selected_word]

        # --- Actions ---
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
                txt_data = f"{selected_word}\nDéfinition : {details['définition']}\nContexte : {details['phrase']}"
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

        # --- Affichage du mot sélectionné ---
        st.markdown('<div class="word-detail">', unsafe_allow_html=True)
        st.markdown(f"### {selected_word.upper()}")
        st.markdown(f"<p class='arabic'>{details['définition']}</p>", unsafe_allow_html=True)
        st.divider()

        st.markdown("**Métadonnées :**")
        cols = st.columns(2)
        cols[0].metric("Longueur", details["longueur"])
        cols[1].metric("Position", details["position"])

        st.divider()
        st.markdown(f"**Contexte :**  \n{details['phrase']}")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Veuillez téléverser un fichier Excel ou placer 'amaoual.xlsx' dans le même dossier que app.py.")
    st.markdown("""
    **Exemple de format attendu :**
    | Mot     | Définition            | Phrase                 |
    |---------|-----------------------|------------------------|
    | zwadj   | n.ar. le mariage      | Célébration du zwadj   |
    | zubagh  | n. pierre précieuse   | La zubagh étincelante  |
    """)

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 18:17:28 2025

@author: mokrane
"""

import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Calculateur de résistance ", layout="centered")
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
st.sidebar.header("🎨 Fond dégradé de la page")

gradient_type = st.sidebar.selectbox(
    "Type de dégradé",
    ["linear-gradient", "radial-gradient"]
)

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
# --- 🎨 Correction du style des boutons (visibilité sur fond sombre) ---
st.markdown("""
<style>
/* Style général pour tous les boutons Streamlit */
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

/* Effet au survol */
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #FFA500, #FF4500);
    color: white !important;
    box-shadow: 0 0 15px rgba(255, 140, 0, 0.6);
    transform: scale(1.05);
}

/* Ajustement pour les boutons dans la sidebar */
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

# ---------- tables ----------
couleurs_hex = {
    "Noir": "#000000", "Marron": "#6B3E26", "Rouge": "#FF0000", "Orange": "#FFA500",
    "Jaune": "#FFFF00", "Vert": "#008000", "Bleu": "#0000FF", "Violet": "#800080",
    "Gris": "#808080", "Blanc": "#FFFFFF", "Or": "#C9B037", "Argent": "#C0C0C0"
}

valeurs = {
    "Noir": 0, "Marron": 1, "Rouge": 2, "Orange": 3, "Jaune": 4,
    "Vert": 5, "Bleu": 6, "Violet": 7, "Gris": 8, "Blanc": 9
}

multiplicateurs = {
    "Noir": 1, "Marron": 10, "Rouge": 100, "Orange": 1_000,
    "Jaune": 10_000, "Vert": 100_000, "Bleu": 1_000_000,
    "Violet": 10_000_000, "Gris": 100_000_000, "Blanc": 1_000_000_000,
    "Or": 0.1, "Argent": 0.01
}

tolerances = {
    "Marron": 1, "Rouge": 2, "Vert": 0.5, "Bleu": 0.25,
    "Violet": 0.1, "Gris": 0.05, "Or": 5, "Argent": 10
}

# ---------- helper : normalisation des noms ----------
# ======================
# 🔧 Fonction de correction des noms de couleurs
# ======================
def normaliser_nom_couleur(nom: str) -> str:
    """
    Corrige les variations de nom (accents, fautes de frappe, minuscules, etc.)
    pour assurer la cohérence entre les sélecteurs et les dictionnaires.
    """
    nom = nom.strip().capitalize()
    corrections = {
        "Ou": "Argent",
        "Or ": "Or",
        "Brun": "Marron",
        "Brown": "Marron",
        "Gray": "Gris",
        "Grey": "Gris"
    }
    return corrections.get(nom, nom)


# ---------- UI : selectboxes centraux + swatch ----------
st.title("💡 Calculateur de résistance (4 bandes)")
st.markdown("""
<div style="text-align: center; font-family: courier;">
  <p style="color: #3366FF; font-weight: bold; font-size: 18px; margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,1.1);">
    Développé par: Hachemi Mokrane • Octobre 2025
  </p>
</div>
""", unsafe_allow_html=True)
st.subheader("Sélection des bandes")
col1, col2 = st.columns(2)
with col1:
    b1 = st.selectbox("1ère bande (chiffre)", list(valeurs.keys()), index=1)
    st.markdown(f"<div style='display:inline-block;width:16px;height:12px;background:{couleurs_hex[b1]};border:1px solid #000;'></div>  {b1}", unsafe_allow_html=True)
    b2 = st.selectbox("2ème bande (chiffre)", list(valeurs.keys()), index=0)
    st.markdown(f"<div style='display:inline-block;width:16px;height:12px;background:{couleurs_hex[b2]};border:1px solid #000;'></div>  {b2}", unsafe_allow_html=True)

with col2:
    b3 = st.selectbox("3ème bande (multiplicateur)", list(multiplicateurs.keys()), index=1)
    # affichage swatch si dans couleurs_hex sinon gris
    sw3 = couleurs_hex.get(b3, "#CCCCCC")
    st.markdown(f"<div style='display:inline-block;width:16px;height:12px;background:{sw3};border:1px solid #000;'></div>  {b3}", unsafe_allow_html=True)

    b4 = st.selectbox("4ème bande (tolérance)", list(tolerances.keys()), index=list(tolerances.keys()).index("Argent"))
    sw4 = couleurs_hex.get(b4, "#C9B037")
    st.markdown(f"<div style='display:inline-block;width:16px;height:12px;background:{sw4};border:1px solid #000;'></div>  {b4}", unsafe_allow_html=True)

# ---------- normalisation au cas où ----------
b1 = normaliser_nom_couleur(b1)
b2 = normaliser_nom_couleur(b2)
b3 = normaliser_nom_couleur(b3)
b4 = normaliser_nom_couleur(b4)

# ======================
# 🎯 Bouton de calcul
# ======================
if st.button("🧮 Calculer la résistance"):
    # Vérification et calcul
    if b1 not in valeurs or b2 not in valeurs:
        st.error("Les deux premières bandes doivent être des couleurs numériques (Noir, Marron, Rouge...).")
    else:
        if b3 not in multiplicateurs:
            st.error("La 3ème bande doit être un multiplicateur (ex: Marron, Rouge, Orange...).")
        else:
            # tolérance : si nom inconnu, on met 5% par défaut
            tol = tolerances.get(b4, None)
            if tol is None:
                st.warning(f"Tolérance '{b4}' non reconnue — valeur par défaut ±5% utilisée.")
                tol = 5

            # ---------- calcul explicite ----------
            a = valeurs[b1]
            bb = valeurs[b2]
            m = multiplicateurs[b3]
            valeur = (a * 10 + bb) * m

            # format lisible
            if valeur >= 1_000_000:
                valeur_aff = f"{valeur/1_000_000:.2f} MΩ"
            elif valeur >= 1_000:
                valeur_aff = f"{valeur/1_000:.2f} kΩ"
            else:
                valeur_aff = f"{valeur:.2f} Ω"

            # ---------- affichage du résultat ----------
            st.markdown(f"""
            <div style="background:#0A2647;padding:12px;border-radius:8px;box-shadow:0 4px 10px rgba(0,0,0,0.3);">
              <b style="color:#FFD700">Calcul :</b>
              <span style="color:white"> ({a} × 10 + {bb}) × {m} = <strong>{valeur:.2f} Ω</strong></span><br>
              <span style="color:#00FFAA; font-size:18px;">💬 Résistance = <strong>{valeur_aff}</strong> ± {tol}%</span>
            </div>
            """, unsafe_allow_html=True)

            # ======================
            # 🧱 Dessin de la résistance
            # ======================
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.axis("off")

            # Corps principal
            ax.add_patch(plt.Rectangle((0, 0.3), 6, 0.4, color="#F4E1C1", ec="black"))
            # Connexions
            ax.plot([-1, 0], [0.5, 0.5], color="gray", linewidth=5)
            ax.plot([6, 7], [0.5, 0.5], color="gray", linewidth=5)

            # Positions et couleurs
            positions = [1.2, 2.2, 3.2, 4.8]
            colors_map = {
                "Noir": "black", "Marron": "#6B3E26", "Rouge": "red", "Orange": "orange",
                "Jaune": "yellow", "Vert": "green", "Bleu": "blue", "Violet": "purple",
                "Gris": "gray", "Blanc": "white", "Or": "#C9B037", "Argent": "#C0C0C0"
            }

            for i, color in enumerate([b1, b2, b3, b4]):
                ax.add_patch(plt.Rectangle((positions[i], 0.3), 0.2, 0.4, color=colors_map[color]))

            ax.set_xlim(-1, 7)
            ax.set_ylim(0, 1)
            st.pyplot(fig)

            # ======================
            # 💾 Téléchargement
            # ======================
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("📸 Télécharger le graphique", data=buf.getvalue(),
                               file_name="resistance.png", mime="image/png")

            texte = f"Résistance = {valeur_aff} ± {tol}%"
            st.download_button("📥 Télécharger les résultats", data=texte.encode("utf-8"), file_name="resultat_resistance.txt")

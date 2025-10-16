# -*- coding: utf-8 -*-
"""
Created on Mon May  5 20:24:59 2025

@author: mokrane
"""

import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import requests, zipfile, io, os

# ==============================
# 🔹 Fonction de téléchargement
# ==============================
@st.cache_data
def telecharger_natural_earth():
    """Télécharge et extrait les shapefiles Natural Earth nécessaires."""
    dossiers = {
        "countries": {
            "url": "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip",
            "nom": "ne_110m_admin_0_countries"
        },
        "sovereignty": {
            "url": "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_sovereignty.zip",
            "nom": "ne_110m_admin_0_sovereignty"
        },
        "cities": {
            "url": "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_populated_places.zip",
            "nom": "ne_10m_populated_places"
        }
    }

    dossier_data = "data"
    os.makedirs(dossier_data, exist_ok=True)

    fichiers = {}
    for cle, info in dossiers.items():
        zip_path = os.path.join(dossier_data, f"{info['nom']}.zip")
        shp_path = os.path.join(dossier_data, f"{info['nom']}.shp")

        if not os.path.exists(shp_path):
            st.write(f"Téléchargement de {info['nom']} ...")
            r = requests.get(info["url"])
            r.raise_for_status()  # ✅ pour afficher une erreur claire si le téléchargement échoue
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(dossier_data)

        fichiers[cle] = shp_path

    return fichiers



# ==============================
# 🔹 Fonctions de traitement
# ==============================
def charger_shapefile(fichier_shp):
    """Charge un shapefile et retourne un GeoDataFrame."""
    return gpd.read_file(fichier_shp)

def filtrer_pays(contour_gdf, gdf_villes, nom_pays):
    pays_contour = contour_gdf[contour_gdf["ADMIN"] == nom_pays]
    villes_pays = gdf_villes[gdf_villes["ADM0NAME"] == nom_pays]
    capitale = None
    if "FEATURECLA" in villes_pays.columns:
        capitales = villes_pays[villes_pays["FEATURECLA"] == "Admin-0 capital"]
        if not capitales.empty:
            capitale = capitales["NAME"].values[0]
    return pays_contour, villes_pays, capitale

def obtenir_infos_pays(pays_gdf):
    if not pays_gdf.empty:
        infos = {
            "Nom": pays_gdf["ADMIN"].values[0],
            "Population Estimée": pays_gdf["POP_EST"].values[0],
            "Continent": pays_gdf["CONTINENT"].values[0],
            "Code ISO": pays_gdf["ISO_A3"].values[0],
            "Sous-Région": pays_gdf["SUBREGION"].values[0],
            "Économie": pays_gdf["ECONOMY"].values[0],
            "Groupe de revenu": pays_gdf["INCOME_GRP"].values[0],
        }
        return infos
    else:
        return "Aucune information disponible pour ce pays."

# ==============================
# 🔹 Fonctions d'affichage
# ==============================
def afficher_contour_pays(pays_gdf, nom_pays):
    fig, ax = plt.subplots(figsize=(10, 10))
    pays_gdf.boundary.plot(ax=ax, color="blue", linewidth=1, linestyle="dashed")
    ax.set_title(f"Contour de {nom_pays}")
    st.pyplot(fig)

def afficher_villes_pays(pays_gdf, villes_gdf, nom_pays, capitale):
    fig, ax = plt.subplots(figsize=(10, 10))
    pays_gdf.boundary.plot(ax=ax, color="black", linewidth=1, linestyle="dashed")
    villes_gdf.plot(ax=ax, color="skyblue", edgecolor="black", markersize=10)

    for x, y, label in zip(villes_gdf.geometry.x, villes_gdf.geometry.y, villes_gdf["NAME"]):
        ax.text(x, y, label, ha="left", color="black", fontsize=8)

    ax.set_title(f"Carte de {nom_pays}\nCapitale : {capitale}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    st.pyplot(fig)

def afficher_position_ville(pays_gdf, ville_info, nom_pays, ville_souhaitee):
    """Affiche la position d'une ville spécifique sur la carte du pays."""
    if ville_info is None or ville_info.empty:
        st.warning(f"La ville '{ville_souhaitee}' n'a pas été trouvée dans {nom_pays}.")
        return

    try:
        longitude = float(ville_info.geometry.x.values[0])
        latitude = float(ville_info.geometry.y.values[0])
    except Exception as e:
        st.error(f"Erreur lors de la lecture des coordonnées : {e}")
        return

    # --- Carte ---
    fig, ax = plt.subplots(figsize=(10, 10))
    pays_gdf.boundary.plot(ax=ax, color="blue", linewidth=1, linestyle="dashed")

    ax.scatter(longitude, latitude, color="red", s=100, label=ville_souhaitee)
    ax.text(longitude + 0.2, latitude + 0.2, ville_souhaitee, color="black", fontsize=12)

    ax.set_title(f"Position de {ville_souhaitee} dans {nom_pays}")
    ax.legend()
    st.pyplot(fig)

    # --- Informations détaillées ---
    st.subheader(f"Informations sur {ville_souhaitee}")

    wilaya = ville_info["ADM1NAME"].values[0] if "ADM1NAME" in ville_info.columns else "Non disponible"
    feature = ville_info["FEATURECLA"].values[0] if "FEATURECLA" in ville_info.columns else "Inconnue"

    st.write({
        "Nom": ville_info["NAME"].values[0],
        "Latitude": latitude,
        "Longitude": longitude,
        "Wilaya": wilaya,
        "Classification": feature
    })


# ==============================
# 🔹 Application principale
# ==============================
st.set_page_config(layout="wide", page_title="Visualisation Géographique")

# Téléchargement des shapefiles
fichiers = telecharger_natural_earth()

contour_gdf = charger_shapefile(fichiers["countries"])
villes_gdf = charger_shapefile(fichiers["cities"])
souverineté_gdf = charger_shapefile(fichiers["sovereignty"])

# Sidebar
with st.sidebar:
    st.markdown("***Auteur: Hachemi Mokrane***")
    st.title("Options de visualisation")

    liste_pays = sorted(contour_gdf["ADMIN"].unique())
    nom_pays = st.selectbox("Sélectionnez un pays", liste_pays)

    pays_gdf, villes_pays_gdf, capitale = filtrer_pays(contour_gdf, villes_gdf, nom_pays)

    if not villes_pays_gdf.empty:
        liste_villes = sorted(villes_pays_gdf["NAME"].unique())
        ville_souhaitee = st.selectbox("Sélectionnez une ville", liste_villes)
    else:
        ville_souhaitee = None
        st.warning("Aucune ville disponible pour ce pays")

# Contenu principal
st.title(f"Visualisation géographique de {nom_pays}")

if nom_pays:
    st.header("Informations du pays")
    infos_pays = obtenir_infos_pays(souverineté_gdf[souverineté_gdf["ADMIN"] == nom_pays])
    st.write(infos_pays)

    st.header(f"Contour de {nom_pays}")
    afficher_contour_pays(pays_gdf, nom_pays)

    if capitale:
        st.subheader(f"Capitale : {capitale}")

    if not villes_pays_gdf.empty:
        st.header(f"Villes de {nom_pays}")
        afficher_villes_pays(pays_gdf, villes_pays_gdf, nom_pays, capitale)

        if ville_souhaitee:
            ville_info = villes_pays_gdf[villes_pays_gdf["NAME"] == ville_souhaitee]
            afficher_position_ville(pays_gdf, ville_info, nom_pays, ville_souhaitee)

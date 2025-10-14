# -*- coding: utf-8 -*-
"""
Created on Mon May  5 20:24:59 2025

@author: mokrane
"""

import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import zipfile
import io
import requests

# =========================
# --- Téléchargement des shapefiles Natural Earth ---
# =========================
@st.cache_data
def telecharger_natural_earth():
    urls = {
        "countries": "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip",
        "sovereignty": "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_sovereignty.zip",
      
       
    }

    fichiers = {}
    dossier_cache = "natural_earth_cache"
    os.makedirs(dossier_cache, exist_ok=True)

    for nom, url in urls.items():
        chemin_zip = os.path.join(dossier_cache, f"{nom}.zip")
        chemin_shp = os.path.join(dossier_cache, f"{nom}.shp")

        if not os.path.exists(chemin_shp):
            try:
                r = requests.get(url)
                r.raise_for_status()
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(dossier_cache)
                st.success(f"✅ {nom} téléchargé et extrait.")
            except Exception as e:
                st.error(f"Erreur téléchargement {nom}: {e}")
        else:
            st.info(f"ℹ️ {nom} déjà présent en cache.")
        fichiers[nom] = chemin_shp

    return fichiers


# =========================
# --- Fonctions utilitaires ---
# =========================
def charger_shapefile(fichier_shp):
    return gpd.read_file(fichier_shp)


def filtrer_pays(contour_gdf, gdf_villes, nom_pays):
    pays_contour = contour_gdf[contour_gdf["ADMIN"] == nom_pays]
    villes_pays = gdf_villes[gdf_villes["ADM0NAME"] == nom_pays]
    capitale = (
        villes_pays[villes_pays["FEATURECLA"] == "Admin-0 capital"]["NAME"].values[0]
        if not villes_pays.empty
        else None
    )
    return pays_contour, villes_pays, capitale


def obtenir_infos_pays(pays_gdf):
    if not pays_gdf.empty:
        return {
            "Nom": pays_gdf["ADMIN"].values[0],
            "Population Estimée": pays_gdf["POP_EST"].values[0],
            "Continent": pays_gdf["CONTINENT"].values[0],
            "Code ISO": pays_gdf["ISO_A3"].values[0],
            "Sous-Région": pays_gdf["SUBREGION"].values[0],
            "Économie": pays_gdf["ECONOMY"].values[0],
            "Groupe de revenu": pays_gdf["INCOME_GRP"].values[0],
        }
    return {}


def afficher_position_ville(pays_gdf, ville_info, nom_pays, ville_souhaitee):
    if not ville_info.empty:
        longitude = ville_info.geometry.x.values[0]
        latitude = ville_info.geometry.y.values[0]

        fig, ax = plt.subplots(figsize=(10, 10))
        pays_gdf.boundary.plot(ax=ax, color="blue", linewidth=1)
        ax.scatter(longitude, latitude, color="red", s=80)
        ax.text(longitude, latitude, ville_souhaitee, fontsize=12, color="black")

        ax.set_title(f"Position de {ville_souhaitee} dans {nom_pays}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        st.pyplot(fig)

        st.subheader(f"Informations sur {ville_souhaitee}")
        st.write({
            "Nom": ville_info["NAME"].values[0],
            "Latitude": latitude,
            "Longitude": longitude,
            "Wilaya": ville_info.get("ADM1NAME", ["Inconnue"])[0],
            "Classification": ville_info.get("FEATURECLA", ["Non spécifiée"])[0],
        })
    else:
        st.warning("Ville non trouvée.")


# =========================
# --- Interface principale Streamlit ---
# =========================
st.set_page_config(layout="wide", page_title="Visualisation Géographique")

# Chargement des shapefiles (une seule fois)
fichiers = telecharger_natural_earth()
contour_gdf = charger_shapefile(fichiers["countries"])
souverineté_gdf = charger_shapefile(fichiers["sovereignty"])

# --- Chargement du fichier local des villes ---
fichier_shp_villes_local = r"D:\Natural earth\tools\508_fix_10m_populated_places_metadata\ne_10m_populated_places_modified.SHP"
if os.path.exists(fichier_shp_villes_local):
    st.success("✅ Fichier local des villes chargé.")
    villes_gdf = charger_shapefile(fichier_shp_villes_local)
else:
    st.warning("⚠️ Fichier local introuvable — les villes ne seront pas affichées correctement.")
    villes_gdf = gpd.GeoDataFrame()

# =========================
# --- Barre latérale ---
# =========================
with st.sidebar:
    st.title("🌍 Options de visualisation")

    liste_pays = sorted(contour_gdf["ADMIN"].unique())
    nom_pays = st.selectbox("Sélectionnez un pays", liste_pays, key="pays")

    # Recherche de ville
    recherche_ville = st.text_input("🔍 Rechercher une ville :")

    # On ne filtre que si un pays est choisi
    if nom_pays and not villes_gdf.empty:
        pays_gdf, villes_pays_gdf, capitale = filtrer_pays(contour_gdf, villes_gdf, nom_pays)

        if recherche_ville:
            villes_filtrees = villes_pays_gdf[villes_pays_gdf["NAME"].str.contains(recherche_ville, case=False, na=False)]
        else:
            villes_filtrees = villes_pays_gdf

        if not villes_filtrees.empty:
            liste_villes = sorted(villes_filtrees["NAME"].unique())
            ville_souhaitee = st.selectbox("Sélectionnez une ville", liste_villes, key=f"ville_{nom_pays}")
        else:
            st.warning("Aucune ville trouvée.")
            ville_souhaitee = None
    else:
        ville_souhaitee = None

# =========================
# --- Contenu principal ---
# =========================
if nom_pays:
    st.title(f"Visualisation géographique de {nom_pays}")

    # 🔄 On récupère les données du pays sélectionné (mise à jour dynamique)
    pays_gdf, villes_pays_gdf, capitale = filtrer_pays(contour_gdf, villes_gdf, nom_pays)
    infos_pays = obtenir_infos_pays(souverineté_gdf[souverineté_gdf["ADMIN"] == nom_pays])

    # --- Informations pays ---
    st.header("Informations du pays sélectionné")
    st.write(infos_pays)

    # --- Affichage des villes ---
    if ville_souhaitee:
        ville_info = villes_gdf[villes_gdf["NAME"] == ville_souhaitee].copy()
        afficher_position_ville(pays_gdf, ville_info, nom_pays, ville_souhaitee)
    else:
        st.info("Sélectionnez une ville pour voir ses détails.")

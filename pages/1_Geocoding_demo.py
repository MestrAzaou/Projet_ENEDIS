#!/usr/bin/env python
# coding: utf-8

# # I - Imports

# In[ ]:


import pandas as pd
import numpy as np
import re
import json
from datetime import datetime

import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import plugins

import requests as r

from folium.plugins import MarkerCluster

import geopandas as gpd

import branca

st.subheader('Geocoding')

# on va installer unidecode pour retirer les accents sur les noms de villes dans les deux DF (celle du CVL et celle des accidents)


# # II - Import des bases 

# ## 2.1 Import et nettoyage de la base "Accident"

# In[ ]:


df_A = pd.read_excel("C:/users/Antoine/OneDrive/Bureau/export_Accident.xlsx", na_values=r'\N')


# ### 2.2.1 Suppression de colonnes

# In[ ]:


#on supprime les colonnes en trop qui ne serviront pas

df_A.drop(columns=['Référence', 'Année', 'Mois', 'Jour', 'Accident connu le ', 'Agent (Collège)', 'Agent (Tranche âge)', 'Heure', 'Tranche horaire', 'Situation de la victime', 'Agent (âge)', 'Agent (Sexe)', 'Prestataire', 'Lésions provoquées', 'Linky', 'Tiers impliqué', 'Rapport police ', ' Evènement à haut potentiel de gravité ', 'Témoignage (Témoin)', 'Nom', 'Témoignage (1ère personnes avisée)', 'Personne avisée', 'Mesures conservatoires prises', "Nombre d'actions", "Date de l'entretien", "Date de l'analyse", 'Rejet CPAM', "Elements principaux de l'entretien"], axis=1, inplace=True)


# In[ ]:


# suppressions complémentaires

df_A.drop(columns=["Nature de l'accident", "Cause", " gravité", "Nombre de jours d'arrêt", "Fire", " préciser", "préciser"], axis=1, inplace=True)


# In[ ]:


# suppressions complémentaires

df_A.drop(columns=['Mesures conservatoires prises  ?', 'Localisation', 'PDL', ], axis=1, inplace=True)


# ### 2.2.2 Transformation de la colonne des dates en format date

# In[ ]:


df_A['Date'] = pd.to_datetime(df_A['Date'], format='%d/%m/%Y')


# In[ ]:


df_A['Date'] = df_A['Date'].apply(lambda time: time.strftime('%Y-%m-%d'))


# ### 2.2.3 Conservation de la condition d'état "clôturé"

# In[ ]:


# on ne garde que les colonnes dans l'état 'clôturé'

df_A = df_A[df_A['Etat'] == 'Clôturé']


# ### 2.2.4 Nouvel index et suppression du précédent

# In[ ]:


#on remet un index au propre qui part de zéro

df_A = df_A.reset_index()


# In[ ]:


# on supprime la colonne de l'ancien index qui ne sert plus à rien

df_A.drop(columns=['index'], axis=1, inplace=True)


# ### 2.2.5 Création d'une colonne à vide "Villes"

# In[ ]:


df_A['Villes']=np.nan


# ### 2.2.6 Importation de la dataframe des Presque Accidents localisés

# In[ ]:


df_PA_loc = pd.read_csv("C:/users/Antoine/OneDrive/Bureau/export_geo_PA2.csv", na_values=r'\N')


# In[ ]:


df_PA_loc.rename(columns={'Ville':'Villes'}, inplace=True)


# ## 2.2 Import de la base géolocalisation CVL (Excel)

# In[ ]:


df_loc = pd.read_excel("C:/users/Antoine/OneDrive/Bureau/contours-geographiques-des-communes-2020.xlsx", na_values=r'\N')


# # III - Création d'une liste de communes et récupération dans le DF Accidents

# ## 3.1 Liste de communes

# In[ ]:


# création de la liste à partir du df_loc

liste_comm = []
for town in df_loc['Nom commune'].unique():
    town = town.lower()
    liste_comm.append(town)

#print(len(liste_comm))
#liste_comm


# In[ ]:


import unidecode

for i in range(len(liste_comm)):
    # remove accent
    liste_comm[i] = unidecode.unidecode(liste_comm[i])


# In[ ]:


# rangement par ordre alphabétique
liste_comm = sorted(liste_comm)


# ## 3.2 Récupération des communes dans le DF Accidents

# ### 3.2.1 A partir de la colonne "Commune/Ville"

# In[ ]:


# On regarde pour la colonne adresse

liste_lieu_adresse = df_A['Lieu,Adresse'].unique().tolist()
liste_lieu_adresse = [x for x in liste_lieu_adresse if pd.isnull(x) == False and x != 'nan']

#liste_lieu_adresse


# In[ ]:


#len(liste_lieu_adresse)

#181 sur les 206


# In[ ]:


# On regarde pour la colonne adresse

liste_adresse = df_A['Adresse'].unique().tolist()
liste_adresse = [x for x in liste_adresse if pd.isnull(x) == False and x != 'nan']


# In[ ]:


#len(liste_adresse)
# 22 sur les 206 : à voir si certaines complètent la colonne "Lieu,Adresse"


# In[ ]:


# On regarde pour la colonne Commune

liste_commune_ville = df_A['Commune/Ville'].unique().tolist()
liste_commune_ville = [x for x in liste_commune_ville if pd.isnull(x) == False and x != 'nan']


# In[ ]:


#len(liste_commune_ville)
## 31 sur 206


# In[ ]:


# On regarde pour la colonne "Préciser"(de la colonne "Commune/Ville")

liste_preciser = df_A['Préciser'].unique().tolist()
liste_preciser = [x for x in liste_preciser if pd.isnull(x) == False and x != 'nan']


# In[ ]:


#len(liste_preciser)
# 157 sur 206


# In[ ]:


#Split des lieux et adresses (df['Lieu,Adresse']) que l'on fait passer en minuscule

liste_match_lieu_adresse = [] #on va créer une liste qui va matcher les noms de communes de la base geoloc avec celle des accidents
for v in liste_lieu_adresse: #le v correspondant à chaque ligne d'adresse individuelle
    liste_nom_splites = v.split() # on splite chaque adresse à ce niveau
    for l in liste_nom_splites:
        if l.lower() in liste_comm:
            liste_match_lieu_adresse.append(l.lower())
#liste_match_lieu_adresse


# In[ ]:


#len(liste_match_lieu_adresse)
# 106 résultats de matchs des communes avec la colonne "Lieu,Adresse"


# In[ ]:


# On reprend la même méthode avec la liste "Adresse" des témoins

liste_match_adresse = [] 
for v in liste_adresse: 
    liste_nom_splites_2 = v.split()
    for l in liste_nom_splites_2:
        if l.lower() in liste_comm:
            liste_match_adresse.append(l.lower())
#len(liste_adresse)


# In[ ]:


# On reprend la même méthode avec la liste "Commune/Ville"

liste_match_commune_ville = [] 
for v in liste_commune_ville: 
    liste_nom_splites_3 = v.split()
    for l in liste_nom_splites_3:
        if l.lower() in liste_comm:
            liste_match_commune_ville.append(l.lower())
#liste_match_commune_ville


# In[ ]:


#len(liste_match_commune_ville)


# In[ ]:


# On reprend la même méthode avec la liste "Préciser"

liste_match_preciser = [] 
for v in liste_preciser: 
    liste_nom_splites_4 = v.split()
    for l in liste_nom_splites_4:
        if l.lower() in liste_comm:
            liste_match_preciser.append(l.lower())
#liste_match_preciser


# In[ ]:


#len(liste_match_preciser)


# Comme le DF_accident "Adresse/lieux" a permis des matchs, on va créer via une boucle une nouvelle colonne "ville" que l'on va agrémenter des résultats du matchs (donc beaucoup de NaN au départ)

# ### 3.2.2 Création d'une fonction qui va recherche les communes dans le DF Accident

# #### a. Boucle à partir de "Lieu,Adresse"

# In[ ]:


# Il faut parcourir la colonne "Lieu,Adresse" et vérifier le match avec les noms des communes issues des listes définies plus hauts

# Peut être créer une fonction pour retourner la commune qui matche

def recherche_commune(adr):
    liste_villes = []
    if pd.isnull(adr) == False and adr != 'nan':
        liste_split = adr.split()
        for i in range(len(liste_split)):
            #remove accents
            liste_split[i] = unidecode.unidecode(liste_split[i]).lower()
        for l in liste_split:
            if l.lower() in liste_comm:
                liste_villes.append(l.lower())
                if len(liste_villes) == 1:
                    return l.lower()


# In[ ]:


#adresse = '2 rue de la logerie 37210 parcay meslay'
#recherche_commune(adresse)


# In[ ]:


#df_A[df_A['Villes'].isna()]['Lieu,Adresse'].head(50)


# ### 3.2.3 Nettoyage manuel des colonnes et appendage de la colonne "Ville"

# #### a. Fonction vérif

# In[ ]:


# Fonction pour vérifier l'apparence de ce genre de commune dans la liste globale des villes du CVL

def verif(commune, ligne):
    print(f"Appartenance de la commune {commune} à la ligne {ligne}:")
    return commune in liste_comm


# #### b. Abondage de la colonne "Villes"

# In[ ]:


#verif("tivernon", 6)


# In[ ]:


df_A.loc[df_A.index[0], 'Villes'] = "mont-pres-chambord"


# In[ ]:


df_A.loc[df_A.index[1], 'Villes'] = "villiers-sur-loir"


# In[ ]:


# ligne 2 : entre travail et domicile (pas exploitable)


# In[ ]:


#nettoyage manuel ligne 3 - La clavaude (la ville de nancay en réalité)

df_A.loc[df_A.index[3], 'Villes'] = "nancay"


# In[ ]:


df_A.loc[df_A.index[4], 'Villes'] = "bourgueil"


# In[ ]:


df_A.loc[df_A.index[5], 'Villes'] = "darvoy"


# In[ ]:


df_A.loc[df_A.index[6], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[7], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[8], 'Villes'] = "chateauroux"


# In[ ]:


df_A.loc[df_A.index[9], 'Villes'] = "bouville"


# In[ ]:


df_A.loc[df_A.index[10], 'Villes'] = "coullons"


# In[ ]:


df_A.loc[df_A.index[11], 'Villes'] = "precy"


# In[ ]:


# ligne 12 : au centre de formation de Nantes (pas exploitable)


# In[ ]:


df_A.loc[df_A.index[13], 'Villes'] = "nancay"


# In[ ]:


df_A.loc[df_A.index[14], 'Villes'] = "bourges"


# In[ ]:


df_A.loc[df_A.index[15], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[16], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[17], 'Villes'] = "ardon"


# In[ ]:


df_A.loc[df_A.index[18], 'Villes'] = "chassignolles"


# In[ ]:


df_A.loc[df_A.index[19], 'Villes'] = "paudy"


# In[ ]:


df_A.loc[df_A.index[20], 'Villes'] = "migne"


# In[ ]:


df_A.loc[df_A.index[21], 'Villes'] = "la chaussee-saint-victor"


# In[ ]:


df_A.loc[df_A.index[22], 'Villes'] = "maillebois"


# In[ ]:


df_A.loc[df_A.index[23], 'Villes'] = "la chaussee-saint-victor"


# In[ ]:


df_A.loc[df_A.index[24], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[25], 'Villes'] = "poulaines"


# In[ ]:


df_A.loc[df_A.index[26], 'Villes'] = "la chaussee-saint-victor"


# In[ ]:


df_A.loc[df_A.index[27], 'Villes'] = "saint-jean-de-la-ruelle"


# In[ ]:


df_A.loc[df_A.index[28], 'Villes'] = "epernon"


# In[ ]:


df_A.loc[df_A.index[29], 'Villes'] = "saint-cyr-en-val"


# In[ ]:


df_A.loc[df_A.index[30], 'Villes'] = "la chaussee-saint-victor"


# In[ ]:


df_A.loc[df_A.index[31], 'Villes'] = "mulsans"


# In[ ]:


df_A.loc[df_A.index[32], 'Villes'] = "poupry"


# In[ ]:


df_A.loc[df_A.index[33], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[34], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[35], 'Villes'] = "blancafort"


# In[ ]:


df_A.loc[df_A.index[36], 'Villes'] = "olivet"


# In[ ]:


# ligne 37 pas exploitable


# In[ ]:


df_A.loc[df_A.index[38], 'Villes'] = "continvoir"


# In[ ]:


df_A.loc[df_A.index[39], 'Villes'] = "chateauroux"


# In[ ]:


df_A.loc[df_A.index[40], 'Villes'] = "saint-doulchard"


# In[ ]:


df_A.loc[df_A.index[41], 'Villes'] = "chateauroux"


# In[ ]:


df_A.loc[df_A.index[42], 'Villes'] = "saint-jean-de-la-ruelle"


# In[ ]:


df_A.loc[df_A.index[43], 'Villes'] = "chateau-renault"


# In[ ]:


df_A.loc[df_A.index[44], 'Villes'] = "parcay-meslay"


# In[ ]:


df_A.loc[df_A.index[45], 'Villes'] = "la chaussee-saint-victor"


# In[ ]:


df_A.loc[df_A.index[46], 'Villes'] = "la chaussee-saint-victor"


# In[ ]:


df_A.loc[df_A.index[47], 'Villes'] = "marolles"


# In[ ]:


# ligne 48 : pas exploitable


# In[ ]:


df_A.loc[df_A.index[49], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[50], 'Villes'] = "briare"


# In[ ]:


df_A.loc[df_A.index[51], 'Villes'] = "ingre"


# In[ ]:


df_A.loc[df_A.index[52], 'Villes'] = "tours"


# In[ ]:


# ligne 53 pas exploitable


# In[ ]:


df_A.loc[df_A.index[54], 'Villes'] = "meauce"


# In[ ]:


df_A.loc[df_A.index[55], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[56], 'Villes'] = "bourges"


# In[ ]:


df_A.loc[df_A.index[57], 'Villes'] = "clemont"


# In[ ]:


df_A.loc[df_A.index[58], 'Villes'] = "vineuil"


# In[ ]:


df_A.loc[df_A.index[59], 'Villes'] = "yzeures-sur-creuse"


# In[ ]:


df_A.loc[df_A.index[60], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[61], 'Villes'] = "luynes"


# In[ ]:


df_A.loc[df_A.index[62], 'Villes'] = "jeu-les-bois"


# In[ ]:


df_A.loc[df_A.index[63], 'Villes'] = "villedieu-sur-indre"


# In[ ]:


df_A.loc[df_A.index[64], 'Villes'] = "vaupillon"


# In[ ]:


df_A.loc[df_A.index[65], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[66], 'Villes'] = "tours"


# In[ ]:


# pour le poste source de collumeaux, mettre ferrieres-en-gatinais

df_A.loc[df_A.index[67], 'Villes'] = "ferrieres-en-gatinais"


# In[ ]:


df_A.loc[df_A.index[68], 'Villes'] = "neuvy-le-roi"


# In[ ]:


df_A.loc[df_A.index[69], 'Villes'] = "neuille-pont-pierre"


# In[ ]:


df_A.loc[df_A.index[70], 'Villes'] = "fay-aux-loges"


# In[ ]:


df_A.loc[df_A.index[71], 'Villes'] = "lacs"


# In[ ]:


df_A.loc[df_A.index[72], 'Villes'] = "chateauroux"


# In[ ]:


df_A.loc[df_A.index[73], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[74], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[75], 'Villes'] = "saint-georges-sur-arnon"


# In[ ]:


df_A.loc[df_A.index[76], 'Villes'] = "luray"


# In[ ]:


df_A.loc[df_A.index[77], 'Villes'] = "olivet"


# In[ ]:


df_A.loc[df_A.index[78], 'Villes'] = "mereau"


# In[ ]:


df_A.loc[df_A.index[79], 'Villes'] = "digny"


# In[ ]:


df_A.loc[df_A.index[80], 'Villes'] = "neuilly-le-brignon"


# In[ ]:


df_A.loc[df_A.index[81], 'Villes'] = "chateauroux"


# In[ ]:


# ligne 82 : 4 rue des genets (plus d'une ville correspond en CVL) : pas exploitable


# In[ ]:


df_A.loc[df_A.index[83], 'Villes'] = "saint-ouen"


# In[ ]:


# ligne 84 : département de l'indre : pas exploitable


# In[ ]:


df_A.loc[df_A.index[85], 'Villes'] = "amboise"


# In[ ]:


df_A.loc[df_A.index[86], 'Villes'] = "villerbon"


# In[ ]:


df_A.loc[df_A.index[87], 'Villes'] = "bourges"


# In[ ]:


df_A.loc[df_A.index[88], 'Villes'] = "chartres"


# In[ ]:


df_A.loc[df_A.index[89], 'Villes'] = "saint-pryve-saint-mesmin"


# In[ ]:


df_A.loc[df_A.index[90], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[91], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[92], 'Villes'] = "cussay"


# In[ ]:


df_A.loc[df_A.index[93], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[94], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[95], 'Villes'] = "ferolles"


# In[ ]:


df_A.loc[df_A.index[96], 'Villes'] = "epiais"


# In[ ]:


df_A.loc[df_A.index[97], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[98], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[99], 'Villes'] = "briare"


# In[ ]:


df_A.loc[df_A.index[100], 'Villes'] = "la ferte-saint-aubin"


# In[ ]:


df_A.loc[df_A.index[101], 'Villes'] = "chemery"


# In[ ]:


df_A.loc[df_A.index[102], 'Villes'] = "chateauroux"


# In[ ]:


df_A.loc[df_A.index[103], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[104], 'Villes'] = "saran"


# In[ ]:


df_A.loc[df_A.index[105], 'Villes'] = "saint-hilaire-saint-mesmin"


# In[ ]:


df_A.loc[df_A.index[106], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[107], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[108], 'Villes'] = "deols"


# In[ ]:


df_A.loc[df_A.index[109], 'Villes'] = "chartres"


# In[ ]:


df_A.loc[df_A.index[110], 'Villes'] = "bourges"


# In[ ]:


df_A.loc[df_A.index[111], 'Villes'] = "poilly-lez-gien"


# In[ ]:


df_A.loc[df_A.index[112], 'Villes'] = "chartres"


# In[ ]:


df_A.loc[df_A.index[113], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[114], 'Villes'] = "olivet"


# In[ ]:


df_A.loc[df_A.index[115], 'Villes'] = "vendome"


# In[ ]:


df_A.loc[df_A.index[116], 'Villes'] = "orleans"


# In[ ]:


# ligne 117 : Paris (pas exploitable)


# In[ ]:


df_A.loc[df_A.index[118], 'Villes'] = "tivernon"


# In[ ]:


df_A.loc[df_A.index[119], 'Villes'] = "amboise"


# In[ ]:


df_A.loc[df_A.index[120], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[121], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[122], 'Villes'] = "montcresson"


# In[ ]:


df_A.loc[df_A.index[123], 'Villes'] = "la chapelle-du-noyer"


# In[ ]:


df_A.loc[df_A.index[124], 'Villes'] = "pannes"


# In[ ]:


df_A.loc[df_A.index[125], 'Villes'] = "perrusson"


# In[ ]:


df_A.loc[df_A.index[126], 'Villes'] = "saint-amand-montrond"


# In[ ]:


df_A.loc[df_A.index[127], 'Villes'] = "artannes-sur-indre"


# In[ ]:


df_A.loc[df_A.index[128], 'Villes'] = "argenton-sur-creuse"


# In[ ]:


df_A.loc[df_A.index[129], 'Villes'] = "chambourg-sur-indre"


# In[ ]:


df_A.loc[df_A.index[130], 'Villes'] = "la chatre"


# In[ ]:


df_A.loc[df_A.index[131], 'Villes'] = "la chatre"


# In[ ]:


df_A.loc[df_A.index[132], 'Villes'] = "moulins-sur-cephons"


# In[ ]:


df_A.loc[df_A.index[133], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[134], 'Villes'] = "chalette-sur-loing"


# In[ ]:


df_A.loc[df_A.index[135], 'Villes'] = "joue-les-tours"


# In[ ]:


# ligne 136 : venissieux (Rhône)


# In[ ]:


df_A.loc[df_A.index[137], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[138], 'Villes'] = "neung-sur-beuvron"


# In[ ]:


df_A.loc[df_A.index[139], 'Villes'] = "girolles"


# In[ ]:


df_A.loc[df_A.index[140], 'Villes'] = "gracay"


# In[ ]:


df_A.loc[df_A.index[141], 'Villes'] = "neuvy-sur-barangeon"


# In[ ]:


df_A.loc[df_A.index[142], 'Villes'] = "la guerche-sur-l'aubois"


# In[ ]:


df_A.loc[df_A.index[143], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[144], 'Villes'] = "fortan"


# In[ ]:


# ligne 145 : lignez (inconnu au bataillon)


# In[ ]:


df_A.loc[df_A.index[146], 'Villes'] = "romorantin-lanthenay"


# In[ ]:


df_A.loc[df_A.index[147], 'Villes'] = "ormes"


# In[ ]:


df_A.loc[df_A.index[148], 'Villes'] = "saint-branchs"


# In[ ]:


df_A.loc[df_A.index[149], 'Villes'] = "gracay"


# In[ ]:


df_A.loc[df_A.index[150], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[151], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[152], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[153], 'Villes'] = "lussault-sur-loire"


# In[ ]:


df_A.loc[df_A.index[154], 'Villes'] = "corquilleroy"


# In[ ]:


df_A.loc[df_A.index[155], 'Villes'] = "trouy"


# In[ ]:


df_A.loc[df_A.index[156], 'Villes'] = "corquilleroy"


# In[ ]:


df_A.loc[df_A.index[157], 'Villes'] = "tours"


# In[ ]:


# ligne 158 : en bas de l'escalier de la sortie principale (pas exploitable)


# In[ ]:


df_A.loc[df_A.index[159], 'Villes'] = "bourges"


# In[ ]:


df_A.loc[df_A.index[160], 'Villes'] = "chateauroux"


# In[ ]:


df_A.loc[df_A.index[161], 'Villes'] = "ouzouer-sur-trezee"


# In[ ]:


df_A.loc[df_A.index[162], 'Villes'] = "couddes"


# In[ ]:


df_A.loc[df_A.index[163], 'Villes'] = "chateauroux"


# In[ ]:


df_A.loc[df_A.index[164], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[165], 'Villes'] = "hanches"


# In[ ]:


df_A.loc[df_A.index[166], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[167], 'Villes'] = "saint-jean-de-la-ruelle"


# In[ ]:


df_A.loc[df_A.index[168], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[169], 'Villes'] = "hanches"


# In[ ]:


# ligne 170 : bureau 211 (non exploitable)


# In[ ]:


df_A.loc[df_A.index[171], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[172], 'Villes'] = "olivet"


# In[ ]:


df_A.loc[df_A.index[173], 'Villes'] = "chouze-sur-loire"


# In[ ]:


df_A.loc[df_A.index[174], 'Villes'] = "blois"


# In[ ]:


df_A.loc[df_A.index[175], 'Villes'] = "senantes"


# In[ ]:


df_A.loc[df_A.index[176], 'Villes'] = "ormes"


# In[ ]:


df_A.loc[df_A.index[177], 'Villes'] = "epernon"


# In[ ]:


df_A.loc[df_A.index[178], 'Villes'] = "saint-just"


# In[ ]:


df_A.loc[df_A.index[179], 'Villes'] = "saint-lucien"


# In[ ]:


df_A.loc[df_A.index[180], 'Villes'] = "saint-doulchard"


# In[ ]:


df_A.loc[df_A.index[181], 'Villes'] = "chalette-sur-loing"


# In[ ]:


df_A.loc[df_A.index[182], 'Villes'] = "olivet"


# In[ ]:


# ligne 183 : sur le trajet (pas exploitable)


# In[ ]:


df_A.loc[df_A.index[184], 'Villes'] = "loches"


# In[ ]:


df_A.loc[df_A.index[185], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[186], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[187], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[188], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[189], 'Villes'] = "bruere-allichamps"


# In[ ]:


df_A.loc[df_A.index[190], 'Villes'] = "la riche"


# In[ ]:


df_A.loc[df_A.index[191], 'Villes'] = "yvoy-le-marron"


# In[ ]:


df_A.loc[df_A.index[192], 'Villes'] = "montargis"


# In[ ]:


df_A.loc[df_A.index[193], 'Villes'] = "chartres"


# In[ ]:


df_A.loc[df_A.index[194], 'Villes'] = "saint-lubin-des-joncherets"


# In[ ]:


df_A.loc[df_A.index[195], 'Villes'] = "saint-avertin"


# In[ ]:


df_A.loc[df_A.index[196], 'Villes'] = "tours"


# In[ ]:


df_A.loc[df_A.index[197], 'Villes'] = "salbris"


# In[ ]:


df_A.loc[df_A.index[198], 'Villes'] = "montargis"


# In[ ]:


df_A.loc[df_A.index[199], 'Villes'] = "orleans"


# In[ ]:


df_A.loc[df_A.index[200], 'Villes'] = "montargis"


# In[ ]:


df_A.loc[df_A.index[201], 'Villes'] = "saint-cyr-en-val"


# In[ ]:


df_A.loc[df_A.index[202], 'Villes'] = "bueil-en-touraine"


# In[ ]:


df_A.loc[df_A.index[203], 'Villes'] = "rians"


# In[ ]:


df_A.loc[df_A.index[204], 'Villes'] = "epineuil-le-fleuriel"


# In[ ]:


df_A.loc[df_A.index[205], 'Villes'] = "romorantin-lanthenay"


# In[ ]:


df_A.loc[df_A.index[206], 'Villes'] = "bourges"


# ## 3.3 Merge du dataframe accident avec les latitudes et longitudes de l'autre DF

# In[ ]:


# Suppression des NaN dans la colonne Villes

df_A.dropna(subset=['Villes'], inplace=True)


# In[ ]:


#df_A['Villes'].isna().sum()


# In[ ]:


from unidecode import unidecode

# remplacer les noms de la colonne "Nom commune" en minuscule pour permettre le merge

df_loc['Nom commune'] = df_loc['Nom commune'].apply(unidecode)

#df_loc['Nom commune']


# In[ ]:


#df_loc['Nom commune']


# In[ ]:


df_loc["Nom commune"] = df_loc["Nom commune"].map(lambda x: x.lower())


# In[ ]:


#df_loc['Nom commune']


# In[ ]:


# Création d'un nouveau dataframe

df_A_loc = pd.merge(df_A, df_loc, left_on='Villes', right_on='Nom commune', how='left')

#df_A_loc.head()


# In[ ]:


#df_A_loc.info()


# In[ ]:


#nettoyage après le merge

df_A_loc.drop(columns=['Nom région', 
                       "Zone d'emploi 2010", 
                       "Code officiel arrondissement départemental", 
                       "Code Iso 3166-3 Zone", 
                       "Type", 
                       "Nom officiel arrondissement départemental",
                       "Code région", 
                       "Code Zone Emploi 2010",
                       "Code Bassin de Vie 2012", 
                       "Nom EPCI",
                       "Code EPCI", 
                       "Code TUU2017",
                       "Libellé TUU2017",
                       "Code catégorie commune dans l'aire urbaine 2010",
                       "Libellé catégorie commune dans l'aire urbaine 2010",
                       "Code Unité Urbaine 2010",
                       "Type de commune",
                       "Tranche taille aire urbaine 2017",
                       "Code Tranche détaillée d'unité urbaine 2017",
                       "Libellé tranche détaillée UU 2017",
                       "Code Aire Urbaine 2010",
                       "Code canton",
                       "SIREN commune", 
                       "UM",
                       "DUM",
                       "SDUM",
                       "FSDUM",
                       "Site",
                       "Poste Source",
                       'Libellé tranche taille aire urbaine 2017'],
              inplace=True)


# In[ ]:


#df_A_loc.head()


# In[ ]:


#df_A_loc.info()


# ## 3.4 Création colonne longitude et latitude

# In[ ]:


coordonnees = pd.DataFrame(df_A_loc['Geo point'].str.replace(',','').str.split(' '), index=df_A_loc.index)


# In[ ]:


for i in range(len(coordonnees)):
    df_A_loc.loc[df_A_loc.index[i], 'Latitude'] = coordonnees['Geo point'][i][0]
    df_A_loc.loc[df_A_loc.index[i], 'Longitude'] = coordonnees['Geo point'][i][1]


# # IV - Cartographie

# ## 4.1 Création de la carte générale centrée sur la région

# In[ ]:


lien = "https://nominatim.openstreetmap.org/?q=Centre+Val+de+Loire&format=json&limit=1"
boundingbox = r.get(lien).json()[0]["boundingbox"]
#boundingbox


# In[ ]:


map_fr = folium.Map()


# In[ ]:


# création des clusters

marker_cluster = MarkerCluster().add_to(map_fr)


# In[ ]:


map_fr.fit_bounds(
   [
        [46.3471572, 0.0527585], # sud ouest
        [48.9410263, 3.1286392] # nord est
    ]
)
#map_fr


# ## 4.2 Centralisation sur la région

# In[ ]:


reg = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions/centre-val-de-loire/region-centre-val-de-loire.geojson"


# In[ ]:


# Une methode de "geopandas" permet de transformer en DataFrame des pages de données "raw".
df_reg = gpd.read_file(reg)

#df_reg


# In[ ]:


#df_reg['geometry'][0]


# In[ ]:


folium.GeoJson(df_reg).add_to(map_fr)

#map_fr


# # V. Création des balises d'information et des clusters

# ## 5.1 Création des clusters

# ## 5.2 Création des balises d'information

# In[ ]:


# création de la fonction qui insère les balises

def popup_html(row, df):
    i = row
    Villes_name=df['Villes'].iloc[i].title()
    famille_name=df['Famille de danger'].iloc[i] 
    Date=df['Date'].iloc[i]

    left_col_color = "#2C75FF" #bleu d'Enedis
    right_col_color = "#96CD32" #vert d'Enedis
    
    html = """<!DOCTYPE html>
<html>
    <table style="height: 100px; width: 300px;">
<tbody>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Villes</span></td>
<td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(Villes_name) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Date</span></td>
<td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(Date) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #FFFFFF;">Famille de danger</span></td>
<td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(famille_name) + """
</tr>
</tbody>
</table>
</html>
"""
    return html


# In[ ]:


# Dataframe des accidents (df_A_loc)

for i in range(0,len(df_A_loc)):
    html = popup_html(i, df_A_loc)
    iframe = branca.element.IFrame(html=html,width=300,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
        location=[df_A_loc.iloc[i]['Latitude'], df_A_loc.iloc[i]['Longitude']],
        popup=popup,
        icon=folium.Icon(color='red', icon='ambulance', prefix='fa')
        ).add_to(marker_cluster)

#st_data = st_folium(map_fr, width=700)


# In[ ]:


# Dataframe des Presque Accidents (df_PA_loc)

for i in range(0,len(df_PA_loc)):
    html = popup_html(i, df_PA_loc)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
        location=[df_PA_loc.iloc[i]['Latitude'], df_PA_loc.iloc[i]['Longitude']],
        popup=popup,
        icon=folium.Icon(color='orange', icon='info-sign')
        ).add_to(marker_cluster)

#st_data = st_folium(map_fr, width=700)


# # VI. Fonction input départementale

# In[ ]:


lien2 = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"


# In[ ]:


df_dep = gpd.read_file(lien2)


# In[ ]:


#df_dep


# 6 départements en Centre-Val de Loire.
# Cher (18)
# Eure-et-Loir (28)
# Indre (36)
# Indre-et-Loire (37)
# Loir-et-Cher (41)
# Loiret (45)

# In[ ]:


cond_CVL = (df_dep['nom'] == "Cher") | (df_dep['nom'] == "Eure-et-Loir") | (df_dep['nom'] == "Indre") | (df_dep['nom'] == "Indre-et-Loire") | (df_dep['nom'] == "Loir-et-Cher") | (df_dep['nom'] == "Loiret")


# In[ ]:


df_dep_cvl = df_dep[cond_CVL].reset_index(drop=True)
#df_dep_cvl


# In[ ]:


# une autre map pour le input départemental

map_fr0 = folium.Map()


# In[ ]:


map_fr0.fit_bounds(
   [
        [46.3471572, 0.0527585], # sud ouest
        [48.9410263, 3.1286392] # nord est
    ]
)
#map_fr0


# In[ ]:


df_dep_18 = df_dep[df_dep['code'] == '18']
df_dep_28 = df_dep[df_dep['code'] == '28']
df_dep_36 = df_dep[df_dep['code'] == '36']
df_dep_37 = df_dep[df_dep['code'] == '37']
df_dep_41 = df_dep[df_dep['code'] == '41']
df_dep_45 = df_dep[df_dep['code'] == '45']


# In[ ]:


# def carte(departement, type_evenement):
#     map_fr0 = folium.Map()                                  # on réinitialise la map_fr0
#     map_fr0.fit_bounds(                                     # focus sur la région CVL
#    [
#         [46.3471572, 0.0527585], # sud ouest
#         [48.9410263, 3.1286392] # nord est
#     ]
#     )
#     folium.GeoJson(df_dep_cvl).add_to(map_fr0)              # on affiche en calque tous les départements
#     map_fr0
#     df_departement = df_dep[df_dep['code'] == departement]  # on créé le df en variable local
#     folium.GeoJson(df_departement).add_to(map_fr0)          # on affiche le département
#     # partie accidents ou presqu'accidents
#     if type_evenement == 1:
#         df_A_departement = df_A_loc[df_A_loc["Code département"] == departement]
#         for i in range(0,len(df_A_departement)):            # on affiche les accidents via Marker
#             html = popup_html(i, df_A_departement)
#             iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
#             popup = folium.Popup(folium.Html(html, script=True), max_width=500)
#             folium.Marker(
#             location=[df_A_departement.iloc[i]['Latitude'], df_A_departement.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
#             popup=popup,
#             icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
#         ).add_to(map_fr0)
#     elif type_evenement == 2:
#         df_PA_departement = df_PA_loc[df_PA_loc["Code département"] == departement]
#         for i in range(0,len(df_PA_departement)):           # idem avec les presqu'accidents
#             html = popup_html(i, df_PA_departement)
#             iframe = branca.element.IFrame(html=html,width=510,height=280)
#             popup = folium.Popup(folium.Html(html, script=True), max_width=500)
#             folium.Marker(
#             location=[df_PA_departement.iloc[i]['Latitude'], df_PA_departement.iloc[i]['Longitude']],
#             popup=popup,
#             icon=folium.Icon(color='orange', icon='info-sign'),
#         ).add_to(map_fr0)
#     return st_folium(map_fr0, width=700)


# In[ ]:


#fonction saisies
#def saisies():
#    liste_dep = [18, 28, 36, 37, 41, 45]
#    dep = st.number_input("Choisissez un département de la région Centre Val de Loire en rentrant son code à 2 chiffres : ", min_value=0, max_value=100, step=1)
    #if dep.isdigit() == False:
    #    while dep.isdigit() == False:
#    st.write("Votre saisie doit être composée de 2 chiffres et faire partie des codes de départements de la région Centre Val de Loire :", liste_dep)
    #        dep = st.text_input("Choisissez à nouveau un département de la région Centre Val de Loire en rentrant son code : ")
    #dep = int(dep)
    #if dep not in liste_dep:
    #    while dep not in liste_dep:
    #        st.write("Le code de département saisi n'est pas dans la région Centre Val de Loire !", liste_dep)
    #        dep = st.text_input("Choisissez un département de la région Centre Val de Loire en rentrant son code à 2 chiffres : ")
    #        if dep.isdigit() == False:
    #            while dep.isdigit() == False:
    #                st.write("Votre saisie doit être composée de 2 chiffres et faire partie des codes de départements de la région Centre Val de Loire :", liste_dep)
    #                dep = st.number_input("Choisissez à nouveau un département de la région Centre Val de Loire en rentrant son code : ")
    #dep = int(dep)
#    event = st.number_input("Souhaitez-vous visualiser les accidents ou les presqu'accidents pour ce département ?\nTapez :\n - 1 pour accidents\n - 2 pour presqu'accidents\n\n", min_value=1, max_value=2, step=1)
#    if (event != 1) and (event != 2):
#        while (event != 1) and (event != 2):
#            st.write("Le choix n'est pas pertinent !")
#            event = st.number_input("Souhaitez-vous visualiser les accidents ou les presqu'accidents pour ce département ?\nTapez :\n - 1 pour accidents\n - 2 pour presqu'accidents\n\n", min_value=1, max_value=2, step=1)
#    return carte(dep, event)


# In[ ]:


#ne fonctionne pas en l'état avec les presque accidents

#saisies()


# In[ ]:


m = folium.Map()
m.fit_bounds(
   [
        [46.3471572, 0.0527585], # sud ouest
        [48.9410263, 3.1286392] # nord est
    ]
)
folium.GeoJson(df_reg).add_to(m)
fg = folium.plugins.MarkerCluster(control=False)
m.add_child(fg)
g1 = plugins.FeatureGroupSubGroup(fg,'Accidents')
m.add_child(g1)
g2 = plugins.FeatureGroupSubGroup(fg,"Presqu'accidents")
m.add_child(g2)
for i in range(0,len(df_PA_loc)):
    html = popup_html(i, df_PA_loc)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
      location=[df_PA_loc.iloc[i]['Latitude'], df_PA_loc.iloc[i]['Longitude']],
      popup=popup,
      icon=folium.Icon(color='orange', icon='info-sign'),
   ).add_to(g1)
for i in range(0,len(df_A_loc)):
    html = popup_html(i, df_A_loc)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
      location=[df_A_loc.iloc[i]['Latitude'], df_A_loc.iloc[i]['Longitude']],
      popup=popup,
      icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
   ).add_to(g2)
l = folium.LayerControl().add_to(m)
st_folium(m, width=700)


# In[ ]:


m1 = folium.Map()
m1.fit_bounds(
   [
        [46.3471572, 0.0527585], # sud ouest
        [48.9410263, 3.1286392] # nord est
    ]
)
fg1 = folium.FeatureGroup()
m1.add_child(fg1)
g1 = plugins.FeatureGroupSubGroup(fg1,'Dép 18 & Accidents')
m1.add_child(g1)
g2 = plugins.FeatureGroupSubGroup(fg1,"Dép 18 & Presqu'accidents")
m1.add_child(g2)
g3 = plugins.FeatureGroupSubGroup(fg1,'Dép 28 & Accidents')
m1.add_child(g3)
g4 = plugins.FeatureGroupSubGroup(fg1,"Dép 28 & Presqu'accidents")
m1.add_child(g4)
g5 = plugins.FeatureGroupSubGroup(fg1,'Dép 36 & Accidents')
m1.add_child(g5)
g6 = plugins.FeatureGroupSubGroup(fg1,"Dép 36 & Presqu'accidents")
m1.add_child(g6)
g7 = plugins.FeatureGroupSubGroup(fg1,'Dép 37 & Accidents')
m1.add_child(g7)
g8 = plugins.FeatureGroupSubGroup(fg1,"Dép 37 & Presqu'accidents")
m1.add_child(g8)
g9 = plugins.FeatureGroupSubGroup(fg1,'Dép 41 & Accidents')
m1.add_child(g9)
g10 = plugins.FeatureGroupSubGroup(fg1,"Dép 41 & Presqu'accidents")
m1.add_child(g10)
g11 = plugins.FeatureGroupSubGroup(fg1,'Dép 45 & Accidents')
m1.add_child(g11)
g12 = plugins.FeatureGroupSubGroup(fg1,"Dép 45 & Presqu'accidents")
m1.add_child(g12)
df_A_departement_18 = df_A_loc[df_A_loc["Code département"] == 18]
folium.GeoJson(df_dep_18).add_to(g1)
for i in range(0,len(df_A_departement_18)):            # on affiche les accidents via Marker
    html = popup_html(i, df_A_departement_18)
    iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_A_departement_18.iloc[i]['Latitude'], df_A_departement_18.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
    popup=popup,
    icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
).add_to(g1)
df_PA_departement_18 = df_PA_loc[df_PA_loc["Code département"] == 18]
folium.GeoJson(df_dep_18).add_to(g2)
for i in range(0,len(df_PA_departement_18)):
    html = popup_html(i, df_PA_departement_18)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_PA_departement_18.iloc[i]['Latitude'], df_PA_departement_18.iloc[i]['Longitude']],
    popup=popup,
    icon=folium.Icon(color='orange', icon='info-sign'),
).add_to(g2)
df_A_departement_28 = df_A_loc[df_A_loc["Code département"] == 28]
folium.GeoJson(df_dep_28).add_to(g3)
for i in range(0,len(df_A_departement_28)):            # on affiche les accidents via Marker
    html = popup_html(i, df_A_departement_28)
    iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_A_departement_28.iloc[i]['Latitude'], df_A_departement_28.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
    popup=popup,
    icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
).add_to(g3)
df_PA_departement_28 = df_PA_loc[df_PA_loc["Code département"] == 28]
folium.GeoJson(df_dep_28).add_to(g4)
for i in range(0,len(df_PA_departement_28)):
    html = popup_html(i, df_PA_departement_28)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_PA_departement_28.iloc[i]['Latitude'], df_PA_departement_28.iloc[i]['Longitude']],
    popup=popup,
    icon=folium.Icon(color='orange', icon='info-sign'),
).add_to(g4)
df_A_departement_36 = df_A_loc[df_A_loc["Code département"] == 36]
folium.GeoJson(df_dep_36).add_to(g5)
for i in range(0,len(df_A_departement_36)):            # on affiche les accidents via Marker
    html = popup_html(i, df_A_departement_36)
    iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_A_departement_36.iloc[i]['Latitude'], df_A_departement_36.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
    popup=popup,
    icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
).add_to(g5)
df_PA_departement_36 = df_PA_loc[df_PA_loc["Code département"] == 36]
folium.GeoJson(df_dep_36).add_to(g6)
for i in range(0,len(df_PA_departement_36)):
    html = popup_html(i, df_PA_departement_36)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_PA_departement_36.iloc[i]['Latitude'], df_PA_departement_36.iloc[i]['Longitude']],
    popup=popup,
    icon=folium.Icon(color='orange', icon='info-sign'),
).add_to(g6)
df_A_departement_37 = df_A_loc[df_A_loc["Code département"] == 37]
folium.GeoJson(df_dep_37).add_to(g7)
for i in range(0,len(df_A_departement_37)):            # on affiche les accidents via Marker
    html = popup_html(i, df_A_departement_37)
    iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_A_departement_37.iloc[i]['Latitude'], df_A_departement_37.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
    popup=popup,
    icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
).add_to(g7)
df_PA_departement37 = df_PA_loc[df_PA_loc["Code département"] == 37]
folium.GeoJson(df_dep_37).add_to(g8)
for i in range(0,len(df_PA_departement37)):
    html = popup_html(i, df_PA_departement37)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_PA_departement37.iloc[i]['Latitude'], df_PA_departement37.iloc[i]['Longitude']],
    popup=popup,
    icon=folium.Icon(color='orange', icon='info-sign'),
).add_to(g8)
df_A_departement_41 = df_A_loc[df_A_loc["Code département"] == 41]
folium.GeoJson(df_dep_41).add_to(g9)
for i in range(0,len(df_A_departement_41)):            # on affiche les accidents via Marker
    html = popup_html(i, df_A_departement_41)
    iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_A_departement_41.iloc[i]['Latitude'], df_A_departement_41.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
    popup=popup,
    icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
).add_to(g9)
df_PA_departement_41 = df_PA_loc[df_PA_loc["Code département"] == 41]
folium.GeoJson(df_dep_41).add_to(g10)
for i in range(0,len(df_PA_departement_41)):
    html = popup_html(i, df_PA_departement_41)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_PA_departement_41.iloc[i]['Latitude'], df_PA_departement_41.iloc[i]['Longitude']],
    popup=popup,
    icon=folium.Icon(color='orange', icon='info-sign'),
).add_to(g10)
df_A_departement_45 = df_A_loc[df_A_loc["Code département"] == 45]
folium.GeoJson(df_dep_45).add_to(g11)
for i in range(0,len(df_A_departement_45)):            # on affiche les accidents via Marker
    html = popup_html(i, df_A_departement_45)
    iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_A_departement_45.iloc[i]['Latitude'], df_A_departement_45.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
    popup=popup,
    icon=folium.Icon(color='red', icon='ambulance', prefix='fa'),
).add_to(g11)
df_PA_departement_45 = df_PA_loc[df_PA_loc["Code département"] == 45]
folium.GeoJson(df_dep_45).add_to(g12)
for i in range(0,len(df_PA_departement_45)):
    html = popup_html(i, df_PA_departement_45)
    iframe = branca.element.IFrame(html=html,width=510,height=280)
    popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(
    location=[df_PA_departement_45.iloc[i]['Latitude'], df_PA_departement_45.iloc[i]['Longitude']],
    popup=popup,
    icon=folium.Icon(color='orange', icon='info-sign'),
).add_to(g12)
l = folium.LayerControl().add_to(m1)
st_folium(m1, width=700)


# Fonction qui utilise la valeur choisie et qui affiche un graphique associé au service
value = st.selectbox('Choisissez une année', [2021, 2022])

def afficher_map_annee(value):
    m4 = folium.Map()
    m4.fit_bounds(
   [
        [46.3471572, 0.0527585], # sud ouest
        [48.9410263, 3.1286392] # nord est
    ]
    )
    fg4 = folium.plugins.MarkerCluster(control=False)
    m4.add_child(fg4)
    g1 = plugins.FeatureGroupSubGroup(fg4,'Département 18')
    m4.add_child(g1)
    g2 = plugins.FeatureGroupSubGroup(fg4,"Département 36")
    m4.add_child(g2)
    g3 = plugins.FeatureGroupSubGroup(fg4,"Département 41")
    m4.add_child(g3)
    g4 = plugins.FeatureGroupSubGroup(fg4,"Département 37")
    m4.add_child(g4)
    g5 = plugins.FeatureGroupSubGroup(fg4,"Département 28")
    m4.add_child(g5)
    g6 = plugins.FeatureGroupSubGroup(fg4,"Département 45")
    m4.add_child(g6)
    df_value = df_PA_loc[df_PA_loc['Année'] == int(value)]
    df_value_18 = df_value[(df_value["Code département"] == 18)]
    folium.GeoJson(df_dep_18).add_to(g1)
    for i in range(0,len(df_value_18)):            # on affiche les accidents via Marker
        html = popup_html(i, df_value_18)
        iframe = branca.element.IFrame(html=html,width=510,height=280)                           # avec la fenêtre et le code HTML via branca
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Marker(
        location=[df_value_18.iloc[i]['Latitude'], df_value_18.iloc[i]['Longitude']],  # on se sert des colonnes Lat et Long
        popup=popup,
        icon=folium.Icon(color='orange', icon='info-sign'),
    ).add_to(g1)
    df_value_36 = df_value[df_value["Code département"] == 36]
    folium.GeoJson(df_dep_36).add_to(g2)
    for i in range(0,len(df_value_36)):
        html = popup_html(i, df_value_36)
        iframe = branca.element.IFrame(html=html,width=510,height=280)
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Marker(
        location=[df_value_36.iloc[i]['Latitude'], df_value_36.iloc[i]['Longitude']],
        popup=popup,
        icon=folium.Icon(color='orange', icon='info-sign'),
    ).add_to(g2)
    df_value_41 = df_value[df_value["Code département"] == 41]
    folium.GeoJson(df_dep_41).add_to(g3)
    for i in range(0,len(df_value_41)):
        html = popup_html(i, df_value_41)
        iframe = branca.element.IFrame(html=html,width=510,height=280)
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Marker(
        location=[df_value_41.iloc[i]['Latitude'], df_value_41.iloc[i]['Longitude']],
        popup=popup,
        icon=folium.Icon(color='orange', icon='info-sign'),
    ).add_to(g3)
    df_value_37 = df_value[(df_value["Code département"] == 37)]
    folium.GeoJson(df_dep_37).add_to(g4)
    for i in range(0,len(df_value_37)):            
        html = popup_html(i, df_value_37)
        iframe = branca.element.IFrame(html=html,width=510,height=280)                           
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Marker(
        location=[df_value_37.iloc[i]['Latitude'], df_value_37.iloc[i]['Longitude']],  
        popup=popup,
        icon=folium.Icon(color='orange', icon='info-sign'),
    ).add_to(g4)
    df_value_28 = df_value[(df_value["Code département"] == 28)]
    folium.GeoJson(df_dep_28).add_to(g5)
    for i in range(0,len(df_value_28)):            
        html = popup_html(i, df_value_28)
        iframe = branca.element.IFrame(html=html,width=510,height=280)                           
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Marker(
        location=[df_value_28.iloc[i]['Latitude'], df_value_28.iloc[i]['Longitude']],  
        popup=popup,
        icon=folium.Icon(color='orange', icon='info-sign'),
    ).add_to(g5)
    df_value_45 = df_value[(df_value["Code département"] == 45)]
    folium.GeoJson(df_dep_45).add_to(g6)
    for i in range(0,len(df_value_45)):            
        html = popup_html(i, df_value_45)
        iframe = branca.element.IFrame(html=html,width=510,height=280)                           
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Marker(
        location=[df_value_45.iloc[i]['Latitude'], df_value_45.iloc[i]['Longitude']],  
        popup=popup,
        icon=folium.Icon(color='orange', icon='info-sign'),
    ).add_to(g6)
    l = folium.LayerControl().add_to(m4)
    return st_folium(m4, width=700)

afficher_map_annee(value)
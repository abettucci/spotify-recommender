import streamlit as st
import requests
import urllib.parse
from main import logueo_spotify, get_track_recommender, recommendation_genre_seeds, get_related_artists

def make_clickable(link):
    return f'<a href="{link}" target="_blank">{link}</a>'

# Create a title for the web app.
st.title("Spotify API Recommender")

sp_client = logueo_spotify()

available_genres = st.selectbox("Generos posibles", recommendation_genre_seeds(sp_client), 0)

##### RECOMENDADOR DE TRACKS EN FUNCION DE ARTISTA, GENERO Y TRACKS #####

# Take user input
seed_artists = st.text_input("Artistas de referencia", "")
seed_genres = str(st.text_input("Generos de referencia", "")).lower()
seed_tracks = st.text_input("Cancion de referencia", "")
# country = st.text_input("Pais de origen de la cancion a recomendar:", "")
limit = st.text_input("Cantidad de recomendaciones", "")
# Create a button to submit the form.
submit = st.button("Submit")

# If the button is clicked.
if submit:
    dict_results = get_track_recommender(sp_client, seed_artists, seed_genres, seed_tracks, 1 if limit=='' else int(limit), None)
    dict_results['song_url'] = dict_results['song_url'].apply(make_clickable)
    st.markdown(dict_results.to_html(escape=False), unsafe_allow_html=True)

##### BUSCADOR DE ARTISTAS SIMILARES EN FUNCION DE ARTISTAS #####
artists_names = st.text_input("Artistas de referencia", "")
# Create a button to submit the form.
submit2 = st.button("Submit")

# If the button is clicked.
if submit2:
    dict_results = get_related_artists(sp_client, artists_names)
    st.markdown(dict_results.to_html(escape=False), unsafe_allow_html=True)
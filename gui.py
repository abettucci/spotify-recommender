import streamlit as st
import requests
import urllib.parse
from main import logueo_spotify, get_track_recommender, recommendation_genre_seeds

# Create a title for the web app.
st.title("Spotify API Recommender")

sp_client = logueo_spotify()

available_genres = st.selectbox("Generos posibles", recommendation_genre_seeds(sp_client), 0)

# Take user input for the city, query, and max price.
seed_artists = st.text_input("Artistas de referencia", "")
seed_genres = str(st.text_input("Generos de referencia", "")).lower()
seed_tracks = st.text_input("Cancion de referencia", "")
# country = st.text_input("Pais de origen de la cancion a recomendar:", "")
limit = st.text_input("Cantidad de recomendaciones", "")

# Create a button to submit the form.
submit = st.button("Submit")

# If the button is clicked.
if submit:

    results = get_track_recommender(sp_client, seed_artists, seed_genres, seed_tracks, 1 if limit=='' else int(limit), None)
    
    # Display the length of the results list.
    st.write(f"Number of results: {len(results)}")
    
    # # Iterate over the results list to display each item.
    # for item in results:
    #     st.header(item["title"])
    #     img_url = item["image"]
    #     st.image(img_url, width=200)
    #     st.write(item["price"])
    #     st.write(item["location"])
    #     st.write(f"https://www.facebook.com{item['link']}")
    #     st.write("----")
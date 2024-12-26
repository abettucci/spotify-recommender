import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
pd.set_option('display.max_colwidth', None)

def logueo_spotify():
     client_id = os.getenv('client_id')
     client_secret = os.getenv('client_secret')
     sp_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
                                                  client_id = client_id,
                                                  client_secret = client_secret,     
                                                  redirect_uri = 'https://spotify-recommender-fdgfxtwf3xed9ufqnilaan.streamlit.app',
                                                  # redirect_uri = 'http://localhost:3000',
                                                  scope=[# Tracks, albums, artistas guardados en Biblioteca
                                                       "user-library-read",
                                                       # User Info
                                                       "user-read-email",
                                                       "user-read-private",
                                                       # Accounts followed
                                                       "user-follow-read",
                                                       # Crear, modificar playlists
                                                       "playlist-read-private",
                                                       "playlist-read-collaborative",
                                                       "ugc-image-upload",
                                                       # Estadisticas de escucha del user
                                                       "user-top-read",
                                                       # Escuchas
                                                       "user-read-currently-playing",
                                                       "user-read-playback-state",
                                                       "user-read-recently-played"
                                                       ],
                                                       open_browser=False))
     return sp_client

def recommendation_genre_seeds(sp_client):
     return sp_client.recommendation_genre_seeds() 

def get_artists_genres(sp_client, artists_names):
     #### Leemos los artistas del text input separados por coma y los convertimos a lista de ID para el input del recomendador
     # artists_names = [item.strip("'") for item in artists_names.split(',')]
     artists_names_list = [name.strip("'") for name in artists_names.split(',')]
     artists_id_list = []
     for artist_name in artists_names_list:
          artist_data = sp_client.search(q=artist_name, type='artist')
          # Obtener el ID del primer artista en los resultados
          if artist_data['artists']['items']:
               artist = artist_data['artists']['items'][0]
               artists_id_list.append(artist['id'])
          else:
               print(f"No se encontraron resultados para {artist_name}")
     
     artist_genres_list = []
     for artist_id in artists_id_list:
          artist_genres_list.append(sp_client.artist(artist_id)["genres"])

     return artist_genres_list

def get_related_artists(sp_client, artists_names):
     #### Leemos los artistas del text input separados por coma y los convertimos a lista de ID para el input del recomendador
     artists_names_list = [name.strip("'") for name in artists_names.split(',')]
     artists_id_list = []
     for artist_name in artists_names_list:
          artist_data = sp_client.search(q=artist_name, type='artist')
          # Obtener el ID del primer artista en los resultados
          if artist_data['artists']['items']:
               artist = artist_data['artists']['items'][0]
               artists_id_list.append(artist['id'])
          else:
               print(f"No se encontraron resultados para {artist_name}")
     
     artist_related_artists = []
     for artist_id in artists_id_list:
          artist_related_artists.append(sp_client.artist_related_artists(artist_id))

     return artist_related_artists

def get_track_recommender(sp_client, artists_names, seed_genres, tracks_names, limit, country=None):
          
     #### Leemos los artistas del text input separados por coma y los convertimos a lista de ID para el input del recomendador
     artists_names_list = ','.split(artists_names)
     artists_id_list = []
     for artist_name in artists_names_list:
          artist_data = sp_client.search(q=artist_name, type='artist')
          # Obtener el ID del primer artista en los resultados
          if artist_data['artists']['items']:
               artist = artist_data['artists']['items'][0]
               artists_id_list.append(artist['id'])
          else:
               print(f"No se encontraron resultados para {artist_name}")
     seed_artists = ','.join(artists_id_list)

     #### Leemos los tracks del text input separados por coma y los convertimos a lista de ID para el input del recomendador
     tracks_names_list = ','.split(tracks_names)
     tracks_id_list = []
     for track_name in tracks_names_list:
          track_data = sp_client.search(q=track_name, type='track')
          # Obtener el ID del primer artista en los resultados
          if track_data['tracks']['items']:
               track = track_data['tracks']['items'][0]
               tracks_id_list.append(track['id'])
          else:
               print(f"No se encontraron resultados para {track_name}")
     seed_tracks = ','.join(tracks_id_list)

     #### Formateamos los generos
     genres = seed_genres.split(',')
     seed_genres = [genre.strip().replace(' ', '-') for genre in genres]
     seed_genres = ','.join(seed_genres)

     # Convertir en listas si no lo están y manejar si no hay valores (None)
     seed_artists = seed_artists.split(',') if seed_artists else None
     seed_genres = seed_genres.split(',') if seed_genres else None
     seed_tracks = seed_tracks.split(',') if seed_tracks else None

     recommendations = sp_client.recommendations(seed_artists=seed_artists, 
                                                 seed_genres=seed_genres, 
                                                 seed_tracks=seed_tracks, 
                                                 limit=limit, 
                                                 country=country)

     
     songs_data = []
     # Iteramos sobre las canciones en 'tracks'
     for track in recommendations['tracks']:
          song_info = {
               'song_name': track['name'],  # Nombre de la canción
               'artist_name': track['artists'][0]['name'],  # Nombre del artista
               'album_name': track['album']['name'],  # Nombre del álbum
               'song_url': track['external_urls']['spotify'],  # URL de la canción en Spotify
          }
          # Añadimos la información de la canción al diccionario
          songs_data.append(song_info)

     # Convertimos la lista de diccionarios a un DataFrame de pandas
     song_recomendations_dict = pd.DataFrame(songs_data)
     
     # results = sp.current_user_top_artists()
     # results = sp_client.current_user_recently_played()

     # results = sp.current_user_saved_tracks()
     # for idx, item in enumerate(results['items']):
     #     track = item['track']
     #     print(idx, track['artists'][0]['name'], " – ", track['name'])

     return song_recomendations_dict

# sp_client = logueo_spotify()
# sp_client.user()
# sp_client.audio_analysis()
# sp_client.audio_features()
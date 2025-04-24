import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import tensorflow as tf
import numpy as np
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta
import os
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from scipy.spatial.distance import cdist
from matplotlib import pyplot as plt
from collections import defaultdict
from scipy.spatial.distance import cdist
from collections import defaultdict
import warnings
import joblib
import ast

warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# client_id = os.getenv('client_id')
# client_secret = os.getenv('client_secret')

client_id = '15b3ce0d808243708ebd24340d70f9c0'
client_secret = 'c5159ef672b145bf879dda11ac9f4077'

def logueo_spotify():
     sp_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
                                                  client_id = client_id,
                                                  client_secret = client_secret,     
                                                  redirect_uri = 'https://spotify-recommender-fdgfxtwf3xed9ufqnilaan.streamlit.app',
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
     genres = sp_client.recommendation_genre_seeds()
     return genres

def get_track_recommender_by_search(sp_client, genre, artist, year, tag): # tag:hipster traer P10 de popularidad
     genre = "jazz"
     # artist = "Miles Davis"
     query = f"genre:{genre}" # artist:{artist}"
     encoded_query = urllib.parse.quote(query) # Realiza el URL encoding de la consulta
     recommendation = sp_client.search(q=encoded_query,limit=1, type="track")

     return recommendation

def get_played_in_recent_period(sp_client, period_type, periods_back):
     today = datetime.now()
     all_songs = []

     # Calcular las fechas de inicio y fin de cada periodo
     periods = []
     for i in range(periods_back):
          if period_type == 'week':
               # Calcular la semana actual menos `i` semanas
               end_of_period = today - timedelta(weeks=i)
               start_of_period = end_of_period - timedelta(days=6)  # Una semana de duración
          elif period_type == 'month':
               # Calcular el mes actual menos `i` meses
               month = (today.month - i - 1) % 12 + 1
               year = today.year - (today.month - i - 1) // 12
               start_of_period = datetime(year, month, 1)
               next_month = month % 12 + 1
               next_month_year = year + (month // 12)
               end_of_period = datetime(next_month_year, next_month, 1) - timedelta(days=1)
          else:
               raise ValueError("Invalid period_type. Use 'week' or 'month'.")

          periods.append((start_of_period, end_of_period))

     # Iterar por cada periodo
     for start_date, end_date in periods:
          start_timestamp = int(start_date.timestamp()) * 1000
          end_timestamp = int((end_date + timedelta(days=1)).timestamp()) * 1000

          current_after = start_timestamp
          while current_after < end_timestamp:
               # Llamar a la API
               response = sp_client.current_user_recently_played(
                    limit=50, after=current_after
               )
               played_songs = response.get("items", [])
               all_songs.extend(played_songs)

               # Si no se recuperaron canciones, salir del bucle
               if not played_songs:
                    break

               # Actualizar el timestamp `after` para continuar iterando
               current_after = max(
                    song["played_at"] for song in played_songs
               )
               current_after = int(datetime.fromisoformat(current_after[:-1]).timestamp()) * 1000

     df_song_results = convertir_a_dataframe(all_songs)

     return df_song_results

def get_played_on_specific_days(sp_client, target_day_name, weeks_back=4):
     # Mapeo de días en español a índices (0 = Lunes, 6 = Domingo)
     day_name_to_index = {
          "Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3,
          "Viernes": 4, "Sábado": 5, "Domingo": 6
     }

     # Verificar si el día proporcionado es válido
     if target_day_name not in day_name_to_index:
          raise ValueError(f"Día inválido: {target_day_name}. Usa uno de: {', '.join(day_name_to_index.keys())}.")

     target_weekday = day_name_to_index[target_day_name]
     today = datetime.now()
     all_songs = []

     # Encontrar los últimos `weeks_back` días objetivo
     weekdays = []
     for i in range(weeks_back):
          # Retrocede en semanas y encuentra el día objetivo más cercano
          delta_days = (today.weekday() - target_weekday) % 7 + i * 7
          target_date = today - timedelta(days=delta_days)
          weekdays.append(target_date)

     # Iterar por cada fecha objetivo
     for day in weekdays:
          start_of_day = datetime(day.year, day.month, day.day)
          end_of_day = start_of_day + timedelta(days=1)

          # Convertir a timestamps en milisegundos
          start_timestamp = int(start_of_day.timestamp()) * 1000
          end_timestamp = int(end_of_day.timestamp()) * 1000

          current_after = start_timestamp
          while current_after < end_timestamp:
               # Llamar a la API
               response = sp_client.current_user_recently_played(
                    limit=50, after=current_after
               )
               played_songs = response.get("items", [])
               all_songs.extend(played_songs)

               # Si no se recuperaron canciones, salir del bucle
               if not played_songs:
                    break

               # Actualizar el timestamp `after` para continuar iterando
               current_after = max(
                    song["played_at"] for song in played_songs
               )
               current_after = int(datetime.fromisoformat(current_after[:-1]).timestamp()) * 1000

     df_song_results = convertir_a_dataframe(all_songs)

     return df_song_results

def get_historical_played(sp_client, start_date, end_date):     
     # Convertir fechas a timestamps en milisegundos
     start_timestamp = int(start_date.timestamp()) * 1000
     end_timestamp = int(end_date.timestamp()) * 1000

     all_played_songs = []
     current_after = start_timestamp

     while current_after < end_timestamp:
          # Llamar a la API de Spotify
          response = sp_client.current_user_recently_played(
               limit=50, 
               after=current_after
          )

          # Agregar canciones recuperadas
          played_songs = response.get("items", [])

          # print(played_songs)

          all_played_songs.extend(played_songs)

          # Si no hay más canciones o no se recuperaron resultados, detener la iteración
          if not played_songs:
               break

          # Actualizar el parámetro `after` para la siguiente iteración
          current_after = max(
               song["played_at"] for song in played_songs
          )
          current_after = int(datetime.fromisoformat(current_after[:-1]).timestamp()) * 1000
     
     df_song_results = convertir_a_dataframe(all_played_songs)

     return df_song_results

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

def convertir_a_dataframe(all_played_songs):
     data_played_songs = []
     # Rellenamos el diccionario de sellers
     for song in all_played_songs:
          fila = {
               "track_name" : song["track"]["name"],
               "played_at" : song["played_at"],
               "artist" : song["track"]["album"]["artists"][0]["name"],
               "album" : song["track"]["album"]["name"]
          }
          data_played_songs.append(fila)

     df_song_results = pd.DataFrame(data_played_songs)

     # Agregar una columna de conteo por canción (track_name, artist, album)
     df_song_results["count"] = df_song_results.groupby(["track_name", "artist", "album"])["track_name"].transform("count")

     # Eliminar duplicados si deseas mostrar solo una fila por canción
     df_song_results_unique = df_song_results.drop_duplicates(subset=["track_name", "artist", "album"]).reset_index(drop=True)

     return df_song_results_unique

############## Build Recommender System ##########################################
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']

def find_song(name, artist, audio_features):
    song_data = defaultdict()
    results = sp.search(q= 'track: {} artist: {}'.format(name, artist), limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    track_audio_features = audio_features.loc[audio_features['track_id']==track_id]
    
    # Si no se encuentran características de audio (porque deprecaron el endpoint de la API de Spotify) entonces buscamos en FMA
    if track_audio_features.empty:
        pass
    else:
        # Si se encuentran características de audio, usar la primera fila
        song_data['name'].append(name)
        song_data['artist'].append(artist)
        song_data['explicit'].append(int(results['explicit']))
        song_data['duration_ms'].append(results['duration_ms'])
        song_data['popularity'].append(results['popularity'])

        # Añadir valores de track_audio_features al diccionario
        track_audio_features_row = track_audio_features.iloc[0]
        for column in track_audio_features.columns:
            song_data[column].append(track_audio_features_row[column])

    # Crear y devolver el DataFrame
    return pd.DataFrame(song_data)

def get_song_data(dict_song_artist, spotify_data, audio_features):
    try:
        song_data = spotify_data[
            (spotify_data['name'].str.lower() == dict_song_artist['name'].lower()) &
            (spotify_data['artists'].apply(lambda artist_list: dict_song_artist['artist'].lower() in 
                                          [a.lower() for a in artist_list]))
        ].iloc[0]
        return song_data
    except IndexError:
        return find_song(dict_song_artist['name'], dict_song_artist['artist'], audio_features)

def get_mean_vector(list_song_artist_dict, spotify_data, audio_features):
    
    song_vectors = []
    
    for dict_song_artist in list_song_artist_dict:
        # Filtrar datos de base de datos entera de spotify_data para traer la info de las canciones que estamos usando de 
        # input (cada song en song_list)
        song_data = get_song_data(dict_song_artist, spotify_data, audio_features)

        # Forzar DataFrame si es Series
        if isinstance(song_data, pd.Series):
            song_data = song_data.to_frame().T

        if song_data.empty:
            print(f"No se encontró información para: {dict_song_artist['name']} ({dict_song_artist['artist']})")
            continue

        try:
            song_vector = song_data[number_cols].values
            song_vectors.append(song_vector)
        except KeyError as e:
            print("Error al extraer columnas:", e)

    if not song_vectors:
        print("No se encontraron vectores de canciones.")
        return None
    
    # Asegurar que todos los vectores sean de forma (15,) en lugar de (1, 15)
    song_vectors_flattened = [vec.flatten() for vec in song_vectors]

    # Largo esperado
    N = len(number_cols)

    # Filtrar solo los vectores con la longitud correcta
    song_vectors_list = [vec for vec in song_vectors_flattened if len(vec) == N]

    # Convertir a matriz NumPy
    song_matrix = np.array(song_vectors_list)

    # Verificar si song_matrix está vacío
    if song_matrix.size == 0:
        print("Error: song_matrix está vacío después del filtrado.")

    return np.mean(song_matrix, axis=0)

def flatten_dict_list(dict_list):
    
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
            
    return flattened_dict

# Cargar datos
def load_data():
     data = pd.read_csv("data/data.csv")
     genre_data = pd.read_csv('data/data_by_genres.csv')
     artists_data = pd.read_csv('data/data_by_artist.csv')
     audio_features = pd.read_csv('spotify-tracks-dataset.csv')

     # Eliminar duplicados
     duplicated_rows = audio_features.duplicated().sum()
     if duplicated_rows == 0:
          print('There are 0 rows that are duplicated, which means each row in the DataFrame is unique.')
     else:
          print(f'There are {duplicated_rows} rows that are duplicated so we need to drop those {duplicated_rows} rows')
          audio_features = audio_features.drop_duplicates()
          print(f'After drop duplicated rows, there are {data.shape[0]} rows left')
     
     return data, genre_data, audio_features, artists_data

# Entrenar y guardar modelos
def train_and_save_models(data, genre_data, audio_features, artists_data):
     # Crear directorio si no existe (con rutas absolutas para mayor seguridad)
     os.makedirs('models', exist_ok=True)

     # Pipeline para géneros
     genre_pipeline = Pipeline([
          ('scaler', StandardScaler()),
          ('kmeans', KMeans(n_clusters=10))
     ])
     genre_pipeline.fit(genre_data.select_dtypes(np.number))

     # Pipeline para canciones
     song_pipeline = Pipeline([
          ('scaler', StandardScaler()),
          ('kmeans', KMeans(n_clusters=20))
     ])
     song_pipeline.fit(data.select_dtypes(np.number))

     # Pipeline para artistas
     artist_pipeline = Pipeline([
          ('scaler', StandardScaler()),
          ('kmeans', KMeans(n_clusters=20))
     ])
     artist_pipeline.fit(artists_data.select_dtypes(np.number))
    
     # Guardar modelos y datos
     joblib.dump(genre_pipeline, os.path.join('models', 'genre_pipeline.joblib'))
     joblib.dump(song_pipeline, os.path.join('models', 'song_pipeline.joblib'))
     joblib.dump(artist_pipeline, os.path.join('models', 'artist_pipeline.joblib'))
     joblib.dump(data, os.path.join('models', 'spotify_data.joblib'))
     joblib.dump(audio_features, os.path.join('models', 'audio_features.joblib'))

# Función de recomendación principal
def get_track_recommender(list_song_artist_dict, n_songs, song_pipeline, spotify_data, audio_features):
    # Obtener recomendaciones
    song_center = get_mean_vector(list_song_artist_dict, spotify_data, audio_features)
    scaler = song_pipeline.steps[0][1]
    scaled_data = scaler.transform(spotify_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])
    
    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin([s['name'] for s in list_song_artist_dict])]
    return rec_songs[['name','artists']].to_dict(orient='records')

# Obtener tamaño de los modelos en MB
def get_model_size(model_path):
    size_bytes = os.path.getsize(model_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

# Inicialización
if __name__ == "__main__":
     data, genre_data, audio_features, artists_data = load_data()
     train_and_save_models(data, genre_data, audio_features, artists_data)
     print("Modelos entrenados y guardados en /models/")

     # print(f"\nTamaño de los modelos:")
     # print(f"- genre_pipeline.joblib: {get_model_size('models/genre_pipeline.joblib'):.2f} MB")
     # print(f"- song_pipeline.joblib: {get_model_size('models/song_pipeline.joblib'):.2f} MB")
     # print(f"- spotify_data.joblib: {get_model_size('models/spotify_data.joblib'):.2f} MB")
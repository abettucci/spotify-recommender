import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = '15b3ce0d808243708ebd24340d70f9c0',
                                               client_secret = 'c5159ef672b145bf879dda11ac9f4077',
                                               redirect_uri = 'http://localhost:3000',
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
                                                    ]))


# results = sp.current_user_top_artists()
results = sp.current_user_recently_played()

print(results)

# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'], " – ", track['name'])
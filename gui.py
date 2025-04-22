import streamlit as st
import os
from datetime import datetime, timedelta
import joblib
from main import (
    logueo_spotify, 
    get_track_recommender, 
    get_historical_played,
    get_played_on_specific_days,
    get_played_in_recent_period
)

try:
    print("Contenido de models/:", os.listdir("models"))

    song_pipeline = joblib.load('models/song_pipeline.joblib')
    spotify_data = joblib.load('models/spotify_data.joblib')
except FileNotFoundError:
    st.error("Error: Modelos no encontrados. Ejecuta main.py primero.")
    st.stop()

# Configuración inicial
st.set_page_config(page_title="Spotify Recommender", layout="wide")
sp_client = logueo_spotify()

# Título de la app
st.title("Spotify API Recommender")

# --- Pestañas para separar las features ---
tab1, tab2 = st.tabs(["🎵 Recomendar canciones", "📅 Últimas reproducidas"])

with tab1:
    # --- Feature 1: Recomendar canciones ---
    st.header("Recomendar canciones basadas en tus favoritas")
    
    # Inicializar lista de canciones en session_state
    if 'song_list' not in st.session_state:
        st.session_state.song_list = []

    # Formulario para agregar canciones
    with st.form("song_form"):
        col1, col2 = st.columns(2)
        with col1:
            song_name = st.text_input("Nombre de la canción", key="song_name")
        with col2:
            artist_name = st.text_input("Artista", key="artist_name")
        
        add_button = st.form_submit_button("Agregar canción")

        # Validar y agregar a la lista
        if add_button:
            if not song_name or not artist_name:
                st.error("¡Debes completar ambos campos!")
            else:
                st.session_state.song_list.append({"name": song_name, "artist": artist_name})
                st.success(f"✅ Canción agregada: '{song_name}' de '{artist_name}'")

    # Mostrar lista de canciones agregadas
    st.subheader("Tus canciones seleccionadas")
    if st.session_state.song_list:
        for idx, song in enumerate(st.session_state.song_list, 1):
            st.write(f"{idx}. {song['name']} - {song['artist']}")
    else:
        st.warning("No hay canciones agregadas aún.")

    # Botón para generar recomendaciones
    with st.form("recommend_form"):
        limit = st.number_input("Número de recomendaciones", min_value=1, max_value=20, value=5)
        submit_recommend = st.form_submit_button("Generar recomendaciones")

        if submit_recommend and st.session_state.song_list:
            print([song["name"] for song in st.session_state.song_list])
            # Llamar a la función de recomendación (ajusta según tu implementación)
            recommendations = get_track_recommender([song["name"] for song in st.session_state.song_list],
                                                    limit,
                                                    song_pipeline, 
                                                    spotify_data)
            
            # Mostrar resultados
            if recommendations:
                st.success("🎧 Recomendaciones:")
                for track in recommendations:
                    st.write(f"- {track['name']} by {track['artist']}")
            else:
                st.error("No se encontraron recomendaciones.")
        elif submit_recommend:
            st.error("¡Agrega al menos una canción!")

with tab2:
    # --- Feature 2: Últimas canciones reproducidas ---
    st.header("Tus últimas canciones reproducidas")
    
    # Opciones de filtrado
    with st.expander("Filtrar por período"):
        col1, col2, col3 = st.columns(3)
        with col1:
            last_n_days = st.selectbox("Últimos días", list(range(0, 31)), 0, placeholder="Elegi cuantos dias de info")
        with col2:
            target_day_name = st.selectbox("Día de la semana", ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'], 0, placeholder="Elegi un dia de la semana")
        with col3:
            last_n_weeks = st.selectbox("Últimas semanas", list(range(0, 5)), 0, placeholder="Elegi cuantas semanas de info")
    
    # Botón para buscar
    if st.button("Buscar canciones"):
        if last_n_days > 0:
            df_songs = get_historical_played(sp_client, datetime.now() - timedelta(days=last_n_days), datetime.now())
        elif target_day_name:
            df_songs = get_played_on_specific_days(sp_client, target_day_name)
        elif last_n_weeks > 0:
            df_songs = get_played_in_recent_period(sp_client, 'week', last_n_weeks)
        else:
            st.warning("Selecciona un filtro válido.")
            df_songs = None

        # Mostrar resultados
        if df_songs is not None:
            st.write(f"🎶 Canciones encontradas: {len(df_songs)}")
            st.dataframe(df_songs)
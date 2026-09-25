import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

st.set_page_config(page_title="BPM Matcher & Playlists", page_icon="🎵", layout="wide")

st.title("🎵 BPM Matcher — Playlists & Hits par Tempo")
st.write("Trouvez des morceaux populaires filtrés au BPM exact sans erreur.")

st.sidebar.header("🔑 Configuration Spotify API")
client_id = st.sidebar.text_input("Client ID Spotify", type="password")
client_secret = st.sidebar.text_input("Client Secret Spotify", type="password")

st.sidebar.markdown("""
---
**Comment obtenir vos clés gratuites :**
1. Allez sur [developer.spotify.com](https://developer.spotify.com/dashboard)
2. Connectez-vous et créez une **App** (nom libre).
3. Copiez le **Client ID** et le **Client Secret** ci-dessus.
""")

if not client_id or not client_secret:
    st.info("👈 Veuillez entrer vos identifiants Spotify API dans le menu de gauche pour démarrer.")
    st.stop()

try:
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception as e:
    st.error("Erreur de connexion à l'API Spotify. Vérifiez vos clés.")
    st.stop()

st.header("🔍 Recherche & Filtrage BPM")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input("Rechercher un genre, artiste ou mot-clé (ex: Afrobeats, Bikutsi, House, Pop)", "Afrobeats")

with col2:
    target_bpm = st.number_input("BPM Cible", min_value=40, max_value=220, value=120, step=1)

with col3:
    tolerance = st.slider("Tolérance BPM (+/-)", min_value=0, max_value=10, value=0)

min_bpm = target_bpm - tolerance
max_bpm = target_bpm + tolerance

if st.button("🔎 Rechercher les morceaux"):
    with st.spinner("Analyse et calcul des BPM en cours..."):
        results = sp.search(q=search_query, limit=30, type="track")
        tracks = results["tracks"]["items"]

        if not tracks:
            st.warning("Aucun morceau trouvé pour cette recherche.")
        else:
            track_ids = [track["id"] for track in tracks]
            audio_features = sp.audio_features(track_ids)

            matching_tracks = []
            for track, features in zip(tracks, audio_features):
                if features:
                    bpm = round(features["tempo"])
                    if min_bpm <= bpm <= max_bpm:
                        matching_tracks.append({
                            "title": track["name"],
                            "artist": ", ".join([artist["name"] for artist in track["artists"]]),
                            "bpm": bpm,
                            "cover": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                            "preview_url": track["preview_url"],
                            "external_url": track["external_urls"]["spotify"]
                        })

            st.subheader(f"🎧 Morceaux trouvés autour de {target_bpm} BPM ({len(matching_tracks)} résultats)")

            if not matching_tracks:
                st.warning(f"Aucun morceau trouvé à {target_bpm} BPM (tolérance +/- {tolerance}). Essayez d'augmenter la tolérance.")
            else:
                cols = st.columns(3)
                for index, track in enumerate(matching_tracks):
                    with cols[index % 3]:
                        st.markdown(f"### {track['title']}")
                        st.write(f"**Artiste :** {track['artist']}")
                        st.write(f"🥁 **BPM :** `{track['bpm']}`")
                        if track["cover"]:
                            st.image(track["cover"], use_column_width=True)
                        if track["preview_url"]:
                            st.audio(track["preview_url"])
                        else:
                            st.write(f"[Écouter sur Spotify]({track['external_url']})")
                        st.markdown("---")

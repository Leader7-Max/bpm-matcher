import streamlit as st
import requests
import yt_dlp

st.set_page_config(page_title="BPM Matcher Pro", page_icon="🎵", layout="wide")

st.title("🎵 BPM Matcher Pro — Hits & Nouveautés")
st.write("Trouvez les hits les plus écouter du moment avec accès aux morceaux entiers.")

# Choix de la catégorie
genre_choice = st.selectbox(
    "🔥 Choisis ton style ou les tendances :",
    [
        "🔥 Top Hits & Tendances Globales",
        "🌍 Afrobeats / Amapiano / Coupé-Décalé",
        "🎤 Rap / Hip-Hop / Trap",
        "💃 Zouglou / Bikutsi / Makossa",
        "🎧 Electro / Dancehall / Shatta",
        "🔍 Recherche personnalisée (nom d'artiste/titre)"
    ]
)

custom_query = ""
if genre_choice == "🔍 Recherche personnalisée (nom d'artiste/titre)":
    custom_query = st.text_input("Titre ou Artiste :", value="Burna Boy")

st.divider()

col1, col2 = st.columns(2)
with col1:
    target_bpm = st.number_input("BPM cible (indicatif) :", min_value=40, max_value=220, value=120)
with col2:
    tolerance = st.slider("Tolérance (± BPM) :", min_value=1, max_value=20, value=10)

submit_button = st.button("🚀 Charger les morceaux", type="primary")

def get_youtube_audio(title, artist):
    """Recherche le morceau entier sur YouTube."""
    search_query = f"ytsearch1:{title} {artist} official audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                return video.get('url'), video.get('webpage_url')
    except Exception:
        return None, None
    return None, None

if submit_button:
    st.info("Chargement des dernières nouveautés et hits...")

    # Définition de la requête selon le choix
    if genre_choice == "🔥 Top Hits & Tendances Globales":
        url = "https://api.deezer.com/chart/0/tracks?limit=30"
    elif genre_choice == "🌍 Afrobeats / Amapiano / Coupé-Décalé":
        url = "https://api.deezer.com/search?q=afrobeats%20amapiano&limit=30"
    elif genre_choice == "🎤 Rap / Hip-Hop / Trap":
        url = "https://api.deezer.com/search?q=rap%20hip%20hop&limit=30"
    elif genre_choice == "💃 Zouglou / Bikutsi / Makossa":
        url = "https://api.deezer.com/search?q=bikutsi%20zouglou&limit=30"
    elif genre_choice == "🎧 Electro / Dancehall / Shatta":
        url = "https://api.deezer.com/search?q=dancehall%20shatta&limit=30"
    else:
        url = f"https://api.deezer.com/search?q={custom_query}&limit=30"

    res = requests.get(url).json()
    tracks = res.get("data", [])

    if not tracks:
        st.error("Aucun morceau trouvé. Essaie une autre recherche.")
    else:
        st.success(f"**{len(tracks)}** morceaux populaires chargés !")
        
        for track in tracks:
            track_id = track.get("id")
            # Récupération détails
            res_details = requests.get(f"https://api.deezer.com/track/{track_id}").json()
            
            bpm = res_details.get("bpm", 0)
            release_date = res_details.get("release_date", "N/C")
            album_name = res_details.get("album", {}).get("title", "Single / Album")
            album_cover = res_details.get("album", {}).get("cover_medium", "")

            # Affichage
            col_img, col_info, col_audio = st.columns([1, 2, 2])
            
            with col_img:
                if album_cover:
                    st.image(album_cover, use_container_width=True)
            
            with col_info:
                st.markdown(f"### **{track.get('title')}**")
                st.markdown(f"👤 **Artiste :** {track.get('artist', {}).get('name')}")
                st.markdown(f"💿 **Album :** {album_name}")
                st.markdown(f"📅 **Date de sortie :** `{release_date}`")
                
                if bpm > 0:
                    st.markdown(f"⚡ **Tempo détecté :** `{bpm} BPM`")
                else:
                    st.markdown("⚡ **Tempo :** *Analyse en cours / Détection automatique*")

            with col_audio:
                # Intégration YouTube pour morceau entier
                audio_url, yt_page_url = get_youtube_audio(track.get('title'), track.get('artist', {}).get('name'))
                
                if audio_url:
                    st.caption("▶️ Morceau entier (YouTube) :")
                    st.audio(audio_url, format="audio/mp3")
                elif track.get("preview"):
                    st.caption("🎧 Extrait 30s (Deezer) :")
                    st.audio(track.get("preview"), format="audio/mp3")

                if yt_page_url:
                    st.markdown(f"[📺 Voir le clip complet sur YouTube]({yt_page_url})")

            st.divider()
  

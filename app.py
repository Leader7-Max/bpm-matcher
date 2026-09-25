import streamlit as st
import requests
import yt_dlp

# Configuration de la page
st.set_page_config(page_title="BPM Matcher Pro", page_icon="🎧", layout="wide")

# CSS personnalisé pour un design moderne & sobre
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .track-card {
        background-color: #1e222d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        border: 1px solid #2e3440;
    }
    .bpm-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 0.9em;
    }
    .date-badge {
        background-color: #2b303c;
        color: #d8dee9;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85em;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎧 BPM Matcher Pro")
st.caption("Sélectionne ton style musical, ton BPM exact et écoute les titres entiers directement.")

# Menu déroulant séparé par style précis
genre_choice = st.selectbox(
    "🎵 Choisissez un style musical ou une tendance :",
    [
        "🔥 Top Hits & Tendances Globales",
        "🇨🇲 Bikutsi",
        "🇨🇮 Zouglou",
        "🇨🇲 Makossa",
        "🌍 Afrobeats",
        "🇿🇦 Amapiano",
        "🇨🇮 Coupé-Décalé",
        "🎤 Rap / Trap",
        "💃 Shatta / Dancehall",
        "🔍 Recherche personnalisée (Artiste / Titre)"
    ]
)

custom_query = ""
if genre_choice == "🔍 Recherche personnalisée (Artiste / Titre)":
    custom_query = st.text_input("Saisissez un artiste ou un titre :", value="Burna Boy")

st.divider()

col1, col2 = st.columns(2)
with col1:
    target_bpm = st.number_input("BPM cible :", min_value=40, max_value=220, value=120)
with col2:
    tolerance = st.slider("Tolérance (± BPM) :", min_value=1, max_value=20, value=10)

submit_button = st.button("🚀 Charger la sélection", type="primary", use_container_width=True)

def get_youtube_info(title, artist):
    """Recherche la vidéo officielle sur YouTube et renvoie l'URL pour intégration."""
    search_query = f"ytsearch1:{title} {artist} official video"
    ydl_opts = {'format': 'best', 'noplaylist': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                return video.get('webpage_url')
    except Exception:
        return None
    return None

if submit_button:
    st.info("Chargement et analyse de la sélection...")

    # Correspondance précise des requêtes
    queries = {
        "🔥 Top Hits & Tendances Globales": None,
        "🇨🇲 Bikutsi": "bikutsi",
        "🇨🇮 Zouglou": "zouglou",
        "🇨🇲 Makossa": "makossa",
        "🌍 Afrobeats": "afrobeats",
        "🇿🇦 Amapiano": "amapiano",
        "🇨🇮 Coupé-Décalé": "coupe decale",
        "🎤 Rap / Trap": "rap trap",
        "💃 Shatta / Dancehall": "shatta dancehall"
    }

    if genre_choice == "🔥 Top Hits & Tendances Globales":
        url = "https://api.deezer.com/chart/0/tracks?limit=40"
    elif genre_choice == "🔍 Recherche personnalisée (Artiste / Titre)":
        url = f"https://api.deezer.com/search?q={custom_query}&limit=40"
    else:
        q = queries.get(genre_choice, "music")
        url = f"https://api.deezer.com/search?q={q}&limit=40"

    res = requests.get(url).json()
    tracks = res.get("data", [])

    if not tracks:
        st.error("Aucun morceau trouvé pour cette sélection.")
    else:
        st.success(f"**{len(tracks)}** morceaux récupérés.")
        
        for track in tracks:
            track_id = track.get("id")
            res_details = requests.get(f"https://api.deezer.com/track/{track_id}").json()
            
            bpm = res_details.get("bpm", 0)
            release_date = res_details.get("release_date", "Inconnue")
            album_name = res_details.get("album", {}).get("title", "Single")
            album_cover = res_details.get("album", {}).get("cover_medium", "")

            # Carte visuelle
            st.markdown('<div class="track-card">', unsafe_allow_html=True)
            
            col_img, col_info, col_player = st.columns([1, 2, 2.5])
            
            with col_img:
                if album_cover:
                    st.image(album_cover, use_container_width=True)
            
            with col_info:
                st.markdown(f"### **{track.get('title')}**")
                st.markdown(f"👤 **Artiste :** {track.get('artist', {}).get('name')}")
                st.markdown(f"💿 **Album :** {album_name}")
                
                bpm_display = f"{bpm} BPM" if bpm > 0 else "Tempo variable"
                st.markdown(f'<span class="bpm-badge">⚡ {bpm_display}</span> &nbsp; <span class="date-badge">📅 {release_date}</span>', unsafe_allow_html=True)

            with col_player:
                yt_url = get_youtube_info(track.get('title'), track.get('artist', {}).get('name'))
                if yt_url:
                    st.caption("▶️ Lecteur intégré (Morceau entier YouTube) :")
                    st.video(yt_url)
                elif track.get("preview"):
                    st.caption("🎧 Extrait 30s (Deezer) :")
                    st.audio(track.get("preview"), format="audio/mp3")

            st.markdown('</div>', unsafe_allow_html=True)
            st.divider()
  

import streamlit as st
import requests
import yt_dlp

st.set_page_config(page_title="BPM Matcher Pro", page_icon="🎵", layout="wide")

st.title("🎵 BPM Matcher Pro — Multi-Plateformes & Titres Entiers")
st.write("Analyse minutieuse : Hits du moment, BPM exact, album, date de sortie et lecture du morceau entier via YouTube.")

mode = st.radio(
    "Source des données :",
    ["🔥 Top Hits & Tendances les plus écoutés", "🔍 Recherche spécifique (Genre / Artiste)"],
    horizontal=True
)

st.divider()

with st.form("filter_form"):
    if mode == "🔍 Recherche spécifique (Genre / Artiste)":
        query = st.text_input("Genre, artiste ou titre :", value="Afrobeats")
    else:
        query = None

    col1, col2 = st.columns(2)
    with col1:
        target_bpm = st.number_input("BPM cible :", min_value=40, max_value=220, value=120)
    with col2:
        tolerance = st.slider("Tolérance (± BPM) :", min_value=0, max_value=10, value=2)

    submit_button = st.form_submit_button("Lancer la recherche minutieuse")

def get_youtube_audio(title, artist):
    """Recherche le morceau entier sur YouTube et extrait l'URL audio."""
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
    st.info("Extraction des métadonnées (BPM, album, date) et recherche des flux entiers...")

    if mode == "🔥 Top Hits & Tendances les plus écoutés":
        url = "https://api.deezer.com/chart/0/tracks?limit=50"
    else:
        url = f"https://api.deezer.com/search?q={query}&limit=40"

    res = requests.get(url).json()
    tracks = res.get("data", [])

    if not tracks:
        st.warning("Aucun morceau trouvé.")
    else:
        matched_tracks = []
        progress_bar = st.progress(0)

        for idx, track in enumerate(tracks):
            track_id = track.get("id")
            res_details = requests.get(f"https://api.deezer.com/track/{track_id}").json()
            
            bpm = res_details.get("bpm", 0)
            release_date = res_details.get("release_date", "Inconnue")
            album_name = res_details.get("album", {}).get("title", "Album inconnu")
            album_cover = res_details.get("album", {}).get("cover_medium", "")

            if (target_bpm - tolerance) <= bpm <= (target_bpm + tolerance) and bpm > 0:
                matched_tracks.append({
                    "title": track.get("title"),
                    "artist": track.get("artist", {}).get("name"),
                    "album": album_name,
                    "release_date": release_date,
                    "bpm": bpm,
                    "cover": album_cover,
                    "deezer_link": track.get("link")
                })

            progress_bar.progress((idx + 1) / len(tracks))

        progress_bar.empty()

        if matched_tracks:
            st.success(f"**{len(matched_tracks)}** morceau(x) minutieusement sélectionné(s) à **{target_bpm} BPM** !")
            for item in matched_tracks:
                col_img, col_info, col_audio = st.columns([1, 2, 2])
                
                with col_img:
                    if item["cover"]:
                        st.image(item["cover"], use_container_width=True)
                
                with col_info:
                    st.markdown(f"### **{item['title']}**")
                    st.markdown(f"👤 **Artiste :** {item['artist']}")
                    st.markdown(f"💿 **Album :** {item['album']}")
                    st.markdown(f"📅 **Sortie :** `{item['release_date']}`")
                    st.markdown(f"⚡ **Tempo :** `{item['bpm']} BPM`")

                with col_audio:
                    # Extraction du flux audio YouTube complet
                    audio_url, yt_page_url = get_youtube_audio(item['title'], item['artist'])
                    
                    if audio_url:
                        st.caption("Morceau entier (Source YouTube) :")
                        st.audio(audio_url, format="audio/mp3")
                    else:
                        st.caption("Morceau indisponible en écoute directe.")

                    st.markdown(f"[▶️ Voir la vidéo sur YouTube]({yt_page_url}) | [🎧 Ouvrir sur Deezer]({item['deezer_link']})")

                st.divider()
        else:
            st.warning("Aucun morceau trouvé à ce tempo exact dans la sélection. Augmente légèrement la tolérance.")
      

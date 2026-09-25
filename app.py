import streamlit as st
import requests

st.set_page_config(page_title="BPM Matcher", page_icon="🎵", layout="centered")

st.title("🎵 BPM Matcher — Nouveautés & Hits par Tempo")
st.write("Découvrez les hits et nouveautés les plus écoutés, filtrés selon votre BPM exact.")

# Mode de recherche
mode = st.radio(
    "Choisissez le mode :",
    ["🔥 Nouveautés & Hits du moment (Top Charts)", "🔍 Recherche par Genre / Artiste"],
    horizontal=True
)

st.divider()

# Formulaire de recherche
with st.form("bpm_form"):
    if mode == "🔍 Recherche par Genre / Artiste":
        genre_or_artist = st.text_input("Genre, artiste ou style :", value="Afrobeats")
    else:
        genre_or_artist = None
        st.caption("L'application va analyser les morceaux les plus populaires du moment.")

    col1, col2 = st.columns(2)
    with col1:
        target_bpm = st.number_input("BPM cible :", min_value=40, max_value=220, value=120)
    with col2:
        tolerance = st.slider("Tolérance (± BPM) :", min_value=0, max_value=10, value=2)

    submit_button = st.form_submit_button("Lancer le filtrage BPM")

if submit_button:
    st.info(f"Analyse des morceaux autour de **{target_bpm} BPM**...")
    
    # Récupération des données Deezer selon le mode sélectionné
    if mode == "🔥 Nouveautés & Hits du moment (Top Charts)":
        url = "https://api.deezer.com/chart/0/tracks?limit=50"
    else:
        url = f"https://api.deezer.com/search?q={genre_or_artist}&limit=40"

    res = requests.get(url).json()
    tracks = res.get("data", [])

    if not tracks:
        st.warning("Aucun morceau trouvé.")
    else:
        matched_tracks = []
        progress_bar = st.progress(0)

        for idx, track in enumerate(tracks):
            # Récupération des détails pour extraire le BPM
            track_id = track.get("id")
            res_details = requests.get(f"https://api.deezer.com/track/{track_id}").json()
            bpm = res_details.get("bpm", 0)

            # Filtrage selon le BPM et la tolérance
            if (target_bpm - tolerance) <= bpm <= (target_bpm + tolerance) and bpm > 0:
                matched_tracks.append({
                    "title": track.get("title"),
                    "artist": track.get("artist", {}).get("name"),
                    "bpm": bpm,
                    "preview": track.get("preview"),
                    "link": track.get("link")
                })

            progress_bar.progress((idx + 1) / len(tracks))

        progress_bar.empty()

        # Affichage des résultats
        if matched_tracks:
            st.success(f"**{len(matched_tracks)}** morceau(x) trouvé(s) à **{target_bpm} BPM** !")
            for item in matched_tracks:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**[{item['title']}]({item['link']})** — {item['artist']}")
                    st.caption(f"Tempo : **{item['bpm']} BPM**")
                with col_b:
                    if item["preview"]:
                        st.audio(item["preview"], format="audio/mp3")
                st.divider()
        else:
            st.warning("Aucun morceau ne correspond à ce tempo exact dans la sélection actuelle. Augmente un peu la tolérance (ex: ±5 BPM).")
            

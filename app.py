import streamlit as st
import requests
import base64
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BPM MATCHER PRO — DJ OXYGÈNE",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE PREMIUM
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, rgba(120,80,255,.18), transparent 30%),
        radial-gradient(circle at top right, rgba(0,220,255,.10), transparent 28%),
        #07080d;
    color: #ffffff;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 32px;
    border-radius: 25px;
    background: linear-gradient(
        135deg,
        rgba(25,25,40,.98),
        rgba(10,11,18,.98)
    );
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 20px 70px rgba(0,0,0,.45);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: clamp(30px, 5vw, 58px);
    margin: 0;
    font-weight: 900;
    letter-spacing: -2px;
}

.hero p {
    color: #b8bfd1;
    font-size: 17px;
    margin-top: 10px;
}

.badge {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    margin: 4px;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.12);
    font-size: 13px;
}

.section-title {
    font-size: 25px;
    font-weight: 800;
    margin-top: 25px;
    margin-bottom: 15px;
}

.track-card {
    background: linear-gradient(
        145deg,
        rgba(24,25,36,.98),
        rgba(12,13,20,.98)
    );
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0 12px 35px rgba(0,0,0,.30);
}

.track-title {
    font-size: 20px;
    font-weight: 800;
    color: white;
}

.track-meta {
    color: #aeb5c7;
    font-size: 14px;
    margin-top: 5px;
}

.source-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,.09);
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 8px;
}

.bpm {
    display: inline-block;
    padding: 8px 13px;
    border-radius: 12px;
    background: rgba(0,220,255,.10);
    border: 1px solid rgba(0,220,255,.25);
    color: #6eeaff;
    font-weight: 800;
    margin-top: 10px;
}

.info-box {
    padding: 15px;
    border-radius: 15px;
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.08);
    color: #d8dbea;
    margin-bottom: 15px;
}

.status {
    padding: 12px;
    border-radius: 12px;
    background: rgba(255,255,255,.05);
    margin-bottom: 8px;
    border: 1px solid rgba(255,255,255,.08);
}

.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 13px;
    font-weight: 800;
}

.stTextInput input,
.stNumberInput input {
    background: #11131c !important;
    color: white !important;
    border-radius: 12px !important;
}

label {
    color: #ffffff !important;
    font-weight: 700 !important;
}

footer {
    visibility: hidden;
}

@media (max-width: 768px) {

    .block-container {
        padding: 1rem;
    }

    .hero {
        padding: 22px;
    }

    .track-card {
        padding: 14px;
    }

    .track-title {
        font-size: 17px;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SECRETS
# ============================================================

def get_secret(name):
    try:
        value = st.secrets.get(name, "")
        return str(value).strip()
    except Exception:
        return ""


SPOTIFY_CLIENT_ID = get_secret("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = get_secret("SPOTIFY_CLIENT_SECRET")
YOUTUBE_API_KEY = get_secret("YOUTUBE_API_KEY")


# ============================================================
# SPOTIFY
# ============================================================

@st.cache_data(ttl=3300)
def get_spotify_token(client_id, client_secret):

    if not client_id or not client_secret:
        return None, "Secrets Spotify manquants."

    try:

        auth = base64.b64encode(
            f"{client_id}:{client_secret}".encode()
        ).decode()

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials"
            },
            timeout=15
        )

        if response.status_code != 200:
            return None, f"Spotify HTTP {response.status_code}: {response.text[:300]}"

        data = response.json()

        return data.get("access_token"), None

    except Exception as e:
        return None, str(e)


def search_spotify(query):

    token, error = get_spotify_token(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET
    )

    if not token:
        return [], error or "Spotify non disponible."

    try:

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={
                "Authorization": f"Bearer {token}"
            },
            params={
                "q": query,
                "type": "track",
                "limit": 10,
                "market": "FR"
            },
            timeout=15
        )

        if response.status_code != 200:

            if response.status_code == 401:
                return [], "Spotify : authentification refusée (401)."

            if response.status_code == 403:
                return [], "Spotify : accès refusé (403). Vérifie les restrictions de ton application."

            if response.status_code == 429:
                return [], "Spotify : trop de requêtes (429)."

            return [], f"Spotify HTTP {response.status_code}"

        data = response.json()

        tracks = []

        for item in data.get("tracks", {}).get("items", []):

            artists = ", ".join(
                artist.get("name", "")
                for artist in item.get("artists", [])
            )

            images = item.get("album", {}).get("images", [])

            cover = images[0]["url"] if images else ""

            tracks.append({
                "source": "Spotify",
                "title": item.get("name", "Titre inconnu"),
                "artist": artists,
                "album": item.get("album", {}).get("name", ""),
                "cover": cover,
                "url": item.get("external_urls", {}).get(
                    "spotify",
                    ""
                ),
                "preview": item.get("preview_url"),
                "date": item.get("album", {}).get("release_date", ""),
            })

        return tracks, None

    except Exception as e:
        return [], f"Spotify : {e}"


# ============================================================
# DEEZER
# ============================================================

def search_deezer(query):

    try:

        response = requests.get(
            "https://api.deezer.com/search",
            params={
                "q": query,
                "limit": 10
            },
            timeout=15
        )

        if response.status_code != 200:
            return [], f"Deezer HTTP {response.status_code}"

        data = response.json()

        tracks = []

        for item in data.get("data", []):

            artist = item.get("artist", {})

            album = item.get("album", {})

            tracks.append({
                "source": "Deezer",
                "title": item.get("title", "Titre inconnu"),
                "artist": artist.get("name", ""),
                "album": album.get("title", ""),
                "cover": album.get("cover_medium", ""),
                "url": item.get("link", ""),
                "preview": item.get("preview", ""),
                "date": ""
            })

        return tracks, None

    except Exception as e:
        return [], f"Deezer : {e}"


# ============================================================
# YOUTUBE
# ============================================================

def search_youtube(query):

    if not YOUTUBE_API_KEY:

        return [], (
            "YouTube non configuré. "
            "Ajoute YOUTUBE_API_KEY dans les Secrets Streamlit."
        )

    try:

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 10,
                "regionCode": "FR",
                "relevanceLanguage": "fr",
                "key": YOUTUBE_API_KEY
            },
            timeout=15
        )

        if response.status_code != 200:

            try:
                error_data = response.json()
                message = (
                    error_data
                    .get("error", {})
                    .get("message", "")
                )
            except Exception:
                message = ""

            if response.status_code == 400:
                return [], f"YouTube HTTP 400 : clé/API invalide. {message}"

            if response.status_code == 403:
                return [], (
                    "YouTube HTTP 403 : quota dépassé, "
                    "API non activée ou clé refusée. "
                    f"{message}"
                )

            if response.status_code == 429:
                return [], "YouTube : trop de requêtes."

            return [], f"YouTube HTTP {response.status_code}: {message}"

        data = response.json()

        videos = []

        for item in data.get("items", []):

            video_id = item.get("id", {}).get("videoId")

            if not video_id:
                continue

            snippet = item.get("snippet", {})

            thumbnails = snippet.get("thumbnails", {})

            thumbnail = (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or thumbnails.get("default", {}).get("url")
                or ""
            )

            videos.append({
                "source": "YouTube",
                "title": snippet.get("title", "Vidéo"),
                "artist": snippet.get("channelTitle", ""),
                "album": "YouTube",
                "cover": thumbnail,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "preview": None,
                "date": snippet.get("publishedAt", "")[:10]
            })

        return videos, None

    except Exception as e:
        return [], f"YouTube : {e}"


# ============================================================
# RECHERCHE UNIVERSELLE
# ============================================================

def universal_search(query, source):

    all_results = []
    errors = []

    if source in ["🌐 Toutes les plateformes", "🟢 Spotify"]:

        spotify_results, error = search_spotify(query)

        all_results.extend(spotify_results)

        if error:
            errors.append(error)

    if source in ["🌐 Toutes les plateformes", "🔵 Deezer"]:

        deezer_results, error = search_deezer(query)

        all_results.extend(deezer_results)

        if error:
            errors.append(error)

    if source in ["🌐 Toutes les plateformes", "🔴 YouTube"]:

        youtube_results, error = search_youtube(query)

        all_results.extend(youtube_results)

        if error:
            errors.append(error)

    return all_results, errors


# ============================================================
# BPM
# ============================================================

def bpm_match(target, tolerance, estimated):

    if not estimated:
        return "BPM CIBLE"

    difference = abs(target - estimated)

    if difference <= tolerance:
        return "MATCH"

    return "ÉCART"


def energy_from_bpm(bpm):

    if bpm < 100:
        return "🌙 Warm-up"

    if bpm < 115:
        return "🕺 Groove"

    if bpm < 130:
        return "🔥 Peak Time"

    return "🚀 High Energy"


# ============================================================
# AFFICHAGE
# ============================================================

def render_track(track, target_bpm):

    source = track.get("source", "")

    if source == "Spotify":
        source_badge = "🟢 SPOTIFY"

    elif source == "Deezer":
        source_badge = "🔵 DEEZER"

    else:
        source_badge = "🔴 YOUTUBE"

    st.markdown('<div class="track-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])

    with col1:

        cover = track.get("cover", "")

        if cover:
            st.image(
                cover,
                use_container_width=True
            )
        else:
            st.markdown(
                "🎧",
                unsafe_allow_html=True
            )

    with col2:

        st.markdown(
            f'<div class="source-badge">{source_badge}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="track-title">{track.get("title", "")}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="track-meta">'
            f'{track.get("artist", "")}'
            f'</div>',
            unsafe_allow_html=True
        )

        if track.get("album"):
            st.markdown(
                f'<div class="track-meta">'
                f'💿 {track.get("album")}'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="bpm">'
            f'🎯 BPM CIBLE : {target_bpm}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.write("")

        if track.get("url"):

            st.link_button(
                "▶️ OUVRIR",
                track["url"],
                use_container_width=True
            )

        if track.get("preview"):

            st.audio(
                track["preview"]
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

<h1>🎧 BPM MATCHER PRO</h1>

<p>
DJ OXYGÈNE — Recherche musicale universelle,
BPM cible et accès direct aux plateformes.
</p>

<div>
<span class="badge">🟢 Spotify</span>
<span class="badge">🔵 Deezer</span>
<span class="badge">🔴 YouTube</span>
<span class="badge">🎯 BPM Matcher</span>
<span class="badge">📱 Mobile Ready</span>
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎛️ DJ CONTROL")

    source = st.radio(
        "SOURCE MUSICALE",
        [
            "🌐 Toutes les plateformes",
            "🟢 Spotify",
            "🔵 Deezer",
            "🔴 YouTube"
        ]
    )

    st.markdown("### 📡 État des services")

    spotify_ok = bool(
        SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
    )

    youtube_ok = bool(YOUTUBE_API_KEY)

    if spotify_ok:
        st.markdown(
            '<div class="status">🟢 Spotify configuré</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status">⚪ Spotify non configuré</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="status">🔵 Deezer disponible</div>',
        unsafe_allow_html=True
    )

    if youtube_ok:
        st.markdown(
            '<div class="status">🔴 YouTube configuré</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status">⚪ YouTube non configuré</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown("### 🎚️ BPM")

    target_bpm = st.number_input(
        "BPM cible",
        min_value=60,
        max_value=220,
        value=110,
        step=1
    )

    tolerance = st.slider(
        "Tolérance BPM",
        min_value=1,
        max_value=20,
        value=8
    )

    st.markdown(
        f"""
        <div class="info-box">
        🎯 BPM cible : <b>{target_bpm}</b><br>
        📏 Tolérance : ±{tolerance} BPM<br>
        ⚡ Zone : <b>{energy_from_bpm(target_bpm)}</b>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RECHERCHE
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Recherche DJ universelle</div>',
    unsafe_allow_html=True
)

query = st.text_input(
    "Recherche",
    placeholder="Exemple : Burna Boy, Coupé Décalé, Amapiano, Shatta...",
    key="music_search"
)

styles = [
    "Afrobeats",
    "Amapiano",
    "Bikutsi",
    "Makossa",
    "Zouglou",
    "Coupé-Décalé",
    "Shatta",
    "Bouyon",
    "Dancehall",
    "Rap Français"
]

st.markdown("### 🎵 Styles rapides")

cols = st.columns(5)

selected_style = None

for index, style in enumerate(styles):

    with cols[index % 5]:

        if st.button(
            style,
            key=f"style_{index}"
        ):
            selected_style = style

if selected_style:
    query = selected_style


search_clicked = st.button(
    "🚀 LANCER LA RECHERCHE",
    type="primary",
    use_container_width=True
)


# ============================================================
# RESULTATS
# ============================================================

if search_clicked:

    if not query.strip():

        st.warning(
            "⚠️ Entre un artiste, un morceau ou un style musical."
        )

    else:

        with st.spinner(
            "🔎 Recherche sur les plateformes..."
        ):

            results, errors = universal_search(
                query.strip(),
                source
            )

        # ----------------------------------------------------
        # STATISTIQUES
        # ----------------------------------------------------

        spotify_count = sum(
            1 for r in results
            if r["source"] == "Spotify"
        )

        deezer_count = sum(
            1 for r in results
            if r["source"] == "Deezer"
        )

        youtube_count = sum(
            1 for r in results
            if r["source"] == "YouTube"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "🎵 TOTAL",
            len(results)
        )

        c2.metric(
            "🟢 SPOTIFY",
            spotify_count
        )

        c3.metric(
            "🔵 DEEZER",
            deezer_count
        )

        c4.metric(
            "🔴 YOUTUBE",
            youtube_count
        )

        # ----------------------------------------------------
        # ALERTES API
        # ----------------------------------------------------

        if errors:

            with st.expander(
                "⚠️ Informations / diagnostics"
            ):

                for error in errors:
                    st.warning(error)

        # ----------------------------------------------------
        # RESULTATS PAR SOURCE
        # ----------------------------------------------------

        if not results:

            st.error(
                "❌ Aucun résultat disponible."
            )

        else:

            if spotify_count:

                st.markdown(
                    '<div class="section-title">'
                    '🟢 Spotify'
                    '</div>',
                    unsafe_allow_html=True
                )

                for track in results:

                    if track["source

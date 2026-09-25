import streamlit as st
import requests
import base64

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BPM MATCHER PRO — DJ OXYGÈNE",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS PREMIUM
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(111, 66, 193, .20), transparent 30%),
            radial-gradient(circle at 90% 0%, rgba(0, 180, 255, .12), transparent 30%),
            #07090f;
        color: white;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 32px;
        border-radius: 25px;
        background: linear-gradient(
            135deg,
            rgba(28, 30, 43, .98),
            rgba(10, 11, 18, .98)
        );
        border: 1px solid rgba(255,255,255,.12);
        box-shadow: 0 20px 60px rgba(0,0,0,.40);
        margin-bottom: 25px;
    }

    .hero h1 {
        margin: 0;
        font-size: clamp(30px, 5vw, 58px);
        font-weight: 900;
        letter-spacing: -2px;
    }

    .hero p {
        color: #b8bfd0;
        font-size: 17px;
        margin-top: 10px;
    }

    .badge {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px;
        border-radius: 999px;
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.10);
        font-size: 13px;
        font-weight: 700;
    }

    .section-title {
        font-size: 25px;
        font-weight: 850;
        margin: 25px 0 15px 0;
    }

    .track-card {
        background: linear-gradient(
            145deg,
            rgba(25,27,38,.98),
            rgba(12,14,21,.98)
        );
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 20px;
        padding: 17px;
        margin-bottom: 15px;
        box-shadow: 0 12px 35px rgba(0,0,0,.30);
    }

    .track-title {
        font-size: 20px;
        font-weight: 850;
        color: #ffffff;
    }

    .track-meta {
        color: #adb5c7;
        font-size: 14px;
        margin-top: 5px;
    }

    .source-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: rgba(255,255,255,.08);
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .bpm-badge {
        display: inline-block;
        margin-top: 10px;
        padding: 8px 13px;
        border-radius: 12px;
        background: rgba(0,210,255,.08);
        border: 1px solid rgba(0,210,255,.20);
        color: #6eeaff;
        font-weight: 800;
    }

    .info-box {
        padding: 15px;
        border-radius: 15px;
        background: rgba(255,255,255,.05);
        border: 1px solid rgba(255,255,255,.08);
        color: #d8dbea;
        margin-bottom: 15px;
    }

    .status-box {
        padding: 11px;
        border-radius: 12px;
        background: rgba(255,255,255,.05);
        border: 1px solid rgba(255,255,255,.08);
        margin-bottom: 8px;
        font-weight: 700;
    }

    .stButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 12px;
        font-weight: 800;
    }

    .stTextInput input,
    .stNumberInput input {
        background: #11131c !important;
        color: #ffffff !important;
        border-radius: 12px !important;
    }

    label {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        .hero {
            padding: 22px;
        }

        .track-card {
            padding: 13px;
        }

        .track-title {
            font-size: 17px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SECRETS
# ============================================================

def get_secret(name):
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


SPOTIFY_CLIENT_ID = get_secret("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = get_secret("SPOTIFY_CLIENT_SECRET")


# ============================================================
# SPOTIFY — TOKEN
# ============================================================

@st.cache_data(ttl=3300)
def get_spotify_token(client_id, client_secret):

    if not client_id or not client_secret:
        return None, "Les Secrets Spotify sont absents."

    try:
        credentials = f"{client_id}:{client_secret}"

        encoded = base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials"
            },
            timeout=15,
        )

        if response.status_code != 200:
            return (
                None,
                f"Spotify HTTP {response.status_code} : "
                f"{response.text[:300]}"
            )

        data = response.json()

        token = data.get("access_token")

        if not token:
            return None, "Spotify n'a pas fourni de token."

        return token, None

    except Exception as error:
        return None, f"Erreur Spotify : {error}"


# ============================================================
# SPOTIFY — RECHERCHE
# ============================================================

def search_spotify(query):

    token, error = get_spotify_token(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
    )

    if not token:
        return [], error

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
                "market": "FR",
            },
            timeout=15,
        )

        if response.status_code != 200:

            if response.status_code == 401:
                return [], (
                    "Spotify : authentification refusée (401)."
                )

            if response.status_code == 403:
                return [], (
                    "Spotify : accès refusé (403). "
                    "Vérifie les restrictions de ton application."
                )

            if response.status_code == 429:
                return [], (
                    "Spotify : trop de requêtes (429)."
                )

            return [], (
                f"Spotify HTTP {response.status_code} : "
                f"{response.text[:250]}"
            )

        data = response.json()

        results = []

        for item in data.get("tracks", {}).get("items", []):

            artists = ", ".join(
                artist.get("name", "")
                for artist in item.get("artists", [])
            )

            images = item.get("album", {}).get("images", [])

            cover = ""

            if images:
                cover = images[0].get("url", "")

            results.append(
                {
                    "source": "Spotify",
                    "title": item.get("name", "Titre inconnu"),
                    "artist": artists,
                    "album": item.get("album", {}).get("name", ""),
                    "cover": cover,
                    "url": item.get("external_urls", {}).get(
                        "spotify",
                        "",
                    ),
                    "preview": item.get("preview_url"),
                    "date": item.get("album", {}).get(
                        "release_date",
                        "",
                    ),
                }
            )

        return results, None

    except Exception as error:
        return [], f"Erreur Spotify : {error}"


# ============================================================
# DEEZER — RECHERCHE
# ============================================================

def search_deezer(query):

    try:

        response = requests.get(
            "https://api.deezer.com/search",
            params={
                "q": query,
                "limit": 10,
            },
            timeout=15,
        )

        if response.status_code != 200:
            return [], (
                f"Deezer HTTP {response.status_code}"
            )

        data = response.json()

        results = []

        for item in data.get("data", []):

            artist = item.get("artist", {})
            album = item.get("album", {})

            results.append(
                {
                    "source": "Deezer",
                    "title": item.get(
                        "title",
                        "Titre inconnu",
                    ),
                    "artist": artist.get(
                        "name",
                        "",
                    ),
                    "album": album.get(
                        "title",
                        "",
                    ),
                    "cover": album.get(
                        "cover_medium",
                        "",
                    ),
                    "url": item.get(
                        "link",
                        "",
                    ),
                    "preview": item.get(
                        "preview",
                        "",
                    ),
                    "date": "",
                }
            )

        return results, None

    except Exception as error:
        return [], f"Erreur Deezer : {error}"


# ============================================================
# RECHERCHE UNIVERSELLE
# ============================================================

def universal_search(query, source):

    results = []
    errors = []

    if source in [
        "🌐 Toutes les plateformes",
        "🟢 Spotify",
    ]:

        spotify_results, spotify_error = search_spotify(query)

        results.extend(spotify_results)

        if spotify_error:
            errors.append(spotify_error)

    if source in [
        "🌐 Toutes les plateformes",
        "🔵 Deezer",
    ]:

        deezer_results, deezer_error = search_deezer(query)

        results.extend(deezer_results)

        if deezer_error:
            errors.append(deezer_error)

    return results, errors


# ============================================================
# ÉNERGIE
# ============================================================

def energy_from_bpm(bpm):

    if bpm < 100:
        return "🌙 Warm-up"

    if bpm < 115:
        return "🕺 Groove"

    if bpm < 130:
        return "🔥 Peak Time"

    return "🚀 High Energy"


# ============================================================
# AFFICHAGE D'UN TITRE
# ============================================================

def render_track(track, target_bpm):

    source = track.get("source", "")

    if source == "Spotify":
        badge = "🟢 SPOTIFY"
    elif source == "Deezer":
        badge = "🔵 DEEZER"
    else:
        badge = "🎵 SOURCE"

    st.markdown(
        '<div class="track-card">',
        unsafe_allow_html=True,
    )

    col_image, col_info = st.columns(
        [1, 4]
    )

    with col_image:

        cover = track.get("cover", "")

        if cover:
            st.image(
                cover,
                use_container_width=True,
            )
        else:
            st.markdown(
                "🎧",
                unsafe_allow_html=True,
            )

    with col_info:

        st.markdown(
            f'<div class="source-badge">{badge}</div>',
            unsafe_allow_html=True,
        )

        title = track.get(
            "title",
            "Titre inconnu",
        )

        artist = track.get(
            "artist",
            "",
        )

        album = track.get(
            "album",
            "",
        )

        st.markdown(
            f'<div class="track-title">{title}</div>',
            unsafe_allow_html=True,
        )

        if artist:
            st.markdown(
                f'<div class="track-meta">'
                f'🎤 {artist}'
                f'</div>',
                unsafe_allow_html=True,
            )

        if album:
            st.markdown(
                f'<div class="track-meta">'
                f'💿 {album}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="bpm-badge">'
            f'🎯 BPM CIBLE : {target_bpm}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        url = track.get("url", "")

        if url:
            st.link_button(
                "▶️ OUVRIR SUR LA PLATEFORME",
                url,
                use_container_width=True,
            )

        preview = track.get("preview")

        if preview:
            st.audio(preview)

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🎧 BPM MATCHER PRO</h1>

        <p>
            DJ OXYGÈNE — Recherche musicale intelligente
            pour Spotify et Deezer.
        </p>

        <span class="badge">🟢 Spotify</span>
        <span class="badge">🔵 Deezer</span>
        <span class="badge">🎯 BPM Matcher</span>
        <span class="badge">📱 Mobile Ready</span>

    </div>
    """,
    unsafe_allow_html=True,
)


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
        ],
    )

    st.markdown("### 📡 État des services")

    if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:

        st.markdown(
            '<div class="status-box">'
            '🟢 Spotify configuré'
            '</div>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<div class="status-box">'
            '⚪ Spotify non configuré'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="status-box">'
        '🔵 Deezer disponible'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### 🎚️ BPM")

    target_bpm = st.number_input(
        "BPM cible",
        min_value=60,
        max_value=220,
        value=110,
        step=1,
    )

    tolerance = st.slider(
        "Tolérance BPM",
        min_value=1,
        max_value=20,
        value=8,
    )

    st.markdown(
        f"""
        <div class="info-box">
            🎯 BPM cible : <b>{target_bpm}</b><br>
            📏 Tolérance : <b>±{tolerance}</b> BPM<br>
            ⚡ Énergie : <b>{energy_from_bpm(target_bpm)}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RECHERCHE
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🔎 Recherche DJ universelle'
    '</div>',
    unsafe_allow_html=True,
)

query = st.text_input(
    "Artiste, morceau ou style",
    placeholder=(
        "Exemple : Burna Boy, Amapiano, "
        "Coupé-Décalé, Shatta..."
    ),
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
    "Rap Français",
]

st.markdown("### 🎵 Styles rapides")

style_columns = st.columns(5)

for index, style in enumerate(styles):

    with style_columns[index % 5]:

        if st.button(
            style,
            key=f"style_{index}",
        ):
            query = style


search_clicked = st.button(
    "🚀 LANCER LA RECHERCHE",
    type="primary",
    use_container_width=True,
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
            "🔎 Recherche sur Spotify et Deezer..."
        ):

            results, errors = universal_search(
                query.strip(),
                source,
            )

        spotify_count = sum(
            1
            for item in results
            if item.get("source") == "Spotify"
        )

        deezer_count = sum(
            1
            for item in results
            if item.get("source") == "Deezer"
        )

        total = len(results)

        st.markdown(
            '<div class="section-title">'
            '📊 Résultats'
            '</div>',
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "🎵 TOTAL",
            total,
        )

        c2.metric(
            "🟢 SPOTIFY",
            spotify_count,
        )

        c3.metric(
            "🔵 DEEZER",
            deezer_count,
        )

        if errors:

            with st.expander(
                "⚠️ Diagnostics des plateformes"
            ):

                for error in errors:
                    st.warning(error)

        if not results:

            st.error(
                "❌ Aucun résultat disponible."
            )

        else:

            # ------------------------------------------------
            # SPOTIFY
            # ------------------------------------------------

            if spotify_count > 0:

                st.markdown(
                    '<div class="section-title">'
                    '🟢 Spotify'
                    '</div>',
                    unsafe_allow_html=True,
                )

                for track in results:

                    if track.get("source") == "Spotify":
                        render_track(
                            track,
                            target_bpm,
                        )

            # ------------------------------------------------
            # DEEZER
            # ------------------------------------------------

            if deezer_count > 0:

                st.markdown(
                    '<div class="section-title">'
                    '🔵 Deezer'
                    '</div>',
                    unsafe_allow_html=True,
                )

                for track in results:

                    if track.get("source") == "Deezer":
                        render_track(
                            track,
                            target_bpm,
                        )


# ============================================================
# INFORMATIONS
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div class="info-box">

    <b>🎯 À propos du BPM Matcher</b><br><br>

    Le BPM indiqué actuellement correspond au
    <b>BPM cible choisi par le DJ</b>.

    Cette version ne prétend pas connaître automatiquement
    le BPM réel de chaque morceau.

    Spotify et Deezer servent ici à rechercher les morceaux
    et à fournir les liens directs vers les plateformes.

    <br><br>

    🚀 Une future version pourra analyse

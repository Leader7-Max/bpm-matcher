import streamlit as st
import requests
import base64

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BPM MATCHER PRO — DJ OXYGÈNE",
    page_icon="🎧",
    layout="wide"
)

# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #080a10;
        color: white;
    }

    .main-title {
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #aeb4c2;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .card {
        background: #11141d;
        border: 1px solid #292e3b;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 15px;
    }

    .title {
        font-size: 20px;
        font-weight: 800;
        color: white;
    }

    .artist {
        color: #b6bdca;
        margin-top: 5px;
    }

    .source {
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .bpm {
        display: inline-block;
        margin-top: 10px;
        padding: 7px 12px;
        border-radius: 10px;
        background: #172630;
        color: #66e5ff;
        font-weight: 800;
    }

    .box {
        background: #11141d;
        border: 1px solid #292e3b;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
    }

    @media (max-width: 700px) {
        .main-title {
            font-size: 32px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
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
# SPOTIFY TOKEN
# ============================================================

def get_spotify_token():

    if not SPOTIFY_CLIENT_ID:
        return None, "SPOTIFY_CLIENT_ID est absent."

    if not SPOTIFY_CLIENT_SECRET:
        return None, "SPOTIFY_CLIENT_SECRET est absent."

    try:

        credentials = (
            SPOTIFY_CLIENT_ID
            + ":"
            + SPOTIFY_CLIENT_SECRET
        )

        encoded = base64.b64encode(
            credentials.encode()
        ).decode()

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": "Basic " + encoded,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials"
            },
            timeout=15
        )

        if response.status_code != 200:

            return None, (
                "Spotify HTTP "
                + str(response.status_code)
                + " : "
                + response.text[:300]
            )

        data = response.json()

        token = data.get("access_token")

        if not token:
            return None, "Spotify n'a pas fourni de token."

        return token, None

    except Exception as error:

        return None, "Erreur Spotify : " + str(error)


# ============================================================
# SPOTIFY SEARCH
# ============================================================

def search_spotify(query):

    token, error = get_spotify_token()

    if not token:
        return [], error

    try:

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={
                "Authorization": "Bearer " + token
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
                return [], "Spotify : authentification refusée."

            if response.status_code == 403:
                return [], (
                    "Spotify : accès refusé (403). "
                    "Vérifie ton application Spotify."
                )

            if response.status_code == 429:
                return [], "Spotify : trop de requêtes."

            return [], (
                "Spotify HTTP "
                + str(response.status_code)
            )

        data = response.json()

        results = []

        tracks = data.get("tracks", {}).get(
            "items",
            []
        )

        for item in tracks:

            artists = []

            for artist in item.get("artists", []):
                artists.append(
                    artist.get("name", "")
                )

            artist_name = ", ".join(artists)

            images = item.get(
                "album",
                {}
            ).get(
                "images",
                []
            )

            cover = ""

            if images:
                cover = images[0].get(
                    "url",
                    ""
                )

            results.append({
                "source": "Spotify",
                "title": item.get(
                    "name",
                    "Titre inconnu"
                ),
                "artist": artist_name,
                "album": item.get(
                    "album",
                    {}
                ).get(
                    "name",
                    ""
                ),
                "cover": cover,
                "url": item.get(
                    "external_urls",
                    {}
                ).get(
                    "spotify",
                    ""
                ),
                "preview": item.get(
                    "preview_url"
                )
            })

        return results, None

    except Exception as error:

        return [], "Erreur Spotify : " + str(error)


# ============================================================
# DEEZER SEARCH
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

            return [], (
                "Deezer HTTP "
                + str(response.status_code)
            )

        data = response.json()

        results = []

        for item in data.get("data", []):

            artist = item.get(
                "artist",
                {}
            )

            album = item.get(
                "album",
                {}
            )

            results.append({
                "source": "Deezer",
                "title": item.get(
                    "title",
                    "Titre inconnu"
                ),
                "artist": artist.get(
                    "name",
                    ""
                ),
                "album": album.get(
                    "title",
                    ""
                ),
                "cover": album.get(
                    "cover_medium",
                    ""
                ),
                "url": item.get(
                    "link",
                    ""
                ),
                "preview": item.get(
                    "preview",
                    ""
                )
            })

        return results, None

    except Exception as error:

        return [], "Erreur Deezer : " + str(error)


# ============================================================
# UNIVERSAL SEARCH
# ============================================================

def universal_search(query, source):

    results = []
    errors = []

    if source in [
        "🌐 Toutes les plateformes",
        "🟢 Spotify"
    ]:

        spotify_results, spotify_error = (
            search_spotify(query)
        )

        results.extend(
            spotify_results
        )

        if spotify_error:
            errors.append(
                spotify_error
            )

    if source in [
        "🌐 Toutes les plateformes",
        "🔵 Deezer"
    ]:

        deezer_results, deezer_error = (
            search_deezer(query)
        )

        results.extend(
            deezer_results
        )

        if deezer_error:
            errors.append(
                deezer_error
            )

    return results, errors


# ============================================================
# BPM ENERGY
# ============================================================

def get_energy(bpm):

    if bpm < 100:
        return "🌙 Warm-up"

    if bpm < 115:
        return "🕺 Groove"

    if bpm < 130:
        return "🔥 Peak Time"

    return "🚀 High Energy"


# ============================================================
# TRACK CARD
# ============================================================

def display_track(track, target_bpm):

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    image_col, info_col = st.columns(
        [1, 4]
    )

    with image_col:

        cover = track.get(
            "cover",
            ""
        )

        if cover:

            st.image(
                cover,
                use_container_width=True
            )

        else:

            st.write("🎧")

    with info_col:

        source = track.get(
            "source",
            ""
        )

        if source == "Spotify":

            source_text = "🟢 SPOTIFY"

        elif source == "Deezer":

            source_text = "🔵 DEEZER"

        else:

            source_text = "🎵 MUSIQUE"

        st.markdown(
            '<div class="source">'
            + source_text
            + '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="title">'
            + str(track.get("title", ""))
            + '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="artist">'
            + str(track.get("artist", ""))
            + '</div>',
            unsafe_allow_html=True
        )

        if track.get("album"):

            st.write(
                "💿 "
                + str(track.get("album"))
            )

        st.markdown(
            '<div class="bpm">'
            + "🎯 BPM CIBLE : "
            + str(target_bpm)
            + '</div>',
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

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🎧 BPM MATCHER PRO'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'DJ OXYGÈNE — Recherche musicale Spotify + Deezer'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🎛️ DJ CONTROL")

    source = st.radio(
        "SOURCE",
        [
            "🌐 Toutes les plateformes",
            "🟢 Spotify",
            "🔵 Deezer"
        ]
    )

    st.subheader("📡 Services")

    if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:

        st.success(
            "🟢 Spotify configuré"
        )

    else:

        st.warning(
            "⚪ Spotify non configuré"
        )

    st.info(
        "🔵 Deezer disponible"
    )

    st.divider()

    st.subheader("🎚️ BPM")

    target_bpm = st.number_input(
        "BPM cible",
        min_value=60,
        max_value=220,
        value=110,
        step=1
    )

    tolerance = st.slider(
        "Tolérance",
        min_value=1,
        max_value=20,
        value=8
    )

    st.markdown(
        '<div class="box">'
        + "🎯 BPM : <b>"
        + str(target_bpm)
        + "</b><br>"
        + "📏 Tolérance : ±"
        + str(tolerance)
        + " BPM<br>"
        + "⚡ "
        + get_energy(target_bpm)
        + '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# SEARCH
# ============================================================

st.header("🔎 Recherche DJ")

query = st.text_input(
    "Artiste, morceau ou style",
    placeholder=(
        "Exemple : Burna Boy, Amapiano, "
        "Coupé-Décalé..."
    )
)

st.subheader("🎵 Styles rapides")

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

style_columns = st.columns(5)

for index, style in enumerate(styles):

    with style_columns[index % 5]:

        if st.button(
            style,
            key="style_" + str(index)
        ):

            query = style


search = st.button(
    "🚀 LANCER LA RECHERCHE",
    type="primary",
    use_container_width=True
)


# ============================================================
# RESULTS
# ============================================================

if search:

    if not query.strip():

        st.warning(
            "⚠️ Entre un artiste, un morceau ou un style."
        )

    else:

        with st.spinner(
            "🔎 Recherche en cours..."
        ):

            results, errors = universal_search(
                query.strip(),
                source
            )

        spotify_count = 0
        deezer_count = 0

        for item in results:

            if item.get("source") == "Spotify":
                spotify_count += 1

            if item.get("source") == "Deezer":
                deezer_count += 1

        st.divider()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🎵 TOTAL",
            len(results)
        )

        col2.metric(
            "🟢 SPOTIFY",
            spotify_count
        )

        col3.metric(
            "🔵 DEEZER",
            deezer_count
        )

        if errors:

            st.warning(
                "⚠️ Certains services ont rencontré un problème."
            )

            with st.expander(
                "Voir les détails"
            ):

                for error in errors:

                    st.write(
                        "• " + error
                    )

        if not results:

            st.error(
                "❌ Aucun résultat trouvé."
            )

        else:

            if spotify_count > 0:

                st.header(
                    "🟢 Spotify"
                )

                for track in results:

                    if track.get("source") == "Spotify":

                        display_track(
                            track,
                            target_bpm
                        )

            if deezer_count > 0:

                st.header(
                    "🔵 Deezer"
                )

                for track in results:

                    if track.get("source") == "Deezer":

                        display_track(
                            track,
                            target_bpm
                        )


# ============================================================
# INFORMATION
# ============================================================

st.divider()

st.info(
    "🎯 Le BPM affiché correspond actuellement au BPM cible "
    "choisi par le DJ. La détection automatique du BPM réel "
    "sera ajoutée dans une prochaine version."
)


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "🎧 BPM MATCHER PRO — DJ OXYGÈNE | Spotify + Deezer"
                     )

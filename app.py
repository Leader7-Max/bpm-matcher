import streamlit as st
import requests
import base64

# ============================================================
# 🎧 BPM MATCHER PRO V2 — DJ OXYGÈNE
# ============================================================

st.set_page_config(
    page_title="BPM Matcher Pro V2 — DJ Oxygène",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 🎨 DESIGN PREMIUM
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 5% 0%, rgba(255, 0, 100, .12), transparent 28%),
        radial-gradient(circle at 95% 5%, rgba(100, 50, 255, .13), transparent 30%),
        #08090f;
    color: #ffffff;
}

/* ================= HERO ================= */

.hero {
    padding: 32px;
    border-radius: 26px;
    margin-bottom: 25px;

    background:
        linear-gradient(
            135deg,
            rgba(255, 0, 100, .18),
            rgba(100, 40, 255, .13)
        ),
        #11121a;

    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 25px 70px rgba(0,0,0,.45);
}

.hero-title {
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -2px;
}

.hero-title span {
    color: #ff287b;
}

.hero-subtitle {
    color: #aeb1bd;
    margin-top: 5px;
}

/* ================= CARDS ================= */

.track-card {
    background:
        linear-gradient(
            145deg,
            rgba(27,28,39,.98),
            rgba(14,15,22,.98)
        );

    border: 1px solid rgba(255,255,255,.08);
    border-radius: 20px;
    padding: 18px;
    margin: 14px 0;

    box-shadow:
        0 15px 40px rgba(0,0,0,.30);
}

/* ================= SEARCH BOX ================= */

.search-panel {
    background: #12141d;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 22px;
    padding: 24px;
    margin-bottom: 25px;
}

/* ================= INPUTS ================= */

div[data-baseweb="input"] {
    background: #20232e !important;
    border: 1px solid #555968 !important;
    border-radius: 12px !important;
}

div[data-baseweb="input"] input {
    color: #ffffff !important;
    background: transparent !important;
    font-weight: 600 !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #aeb2bf !important;
    opacity: 1 !important;
}

/* SELECTBOX */

div[data-baseweb="select"] > div {
    background: #20232e !important;
    border: 1px solid #555968 !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] * {
    color: #ffffff !important;
}

/* NUMBER INPUT */

.stNumberInput input {
    background: #20232e !important;
    color: #ffffff !important;
    border-radius: 12px !important;
}

/* ================= BUTTONS ================= */

.stButton > button {
    min-height: 46px;
    border-radius: 12px;

    background: #191b25;
    color: #ffffff;

    border: 1px solid #3e414e;

    font-weight: 800;
}

.stButton > button:hover {
    border-color: #ff287b;
    color: #ffffff;
}

/* ================= PRIMARY BUTTON ================= */

button[kind="primary"] {
    background:
        linear-gradient(
            90deg,
            #ff176f,
            #8c35ff
        ) !important;

    border: none !important;
}

/* ================= TRACK ================= */

.track-title {
    font-size: 20px;
    font-weight: 800;
}

.artist {
    color: #ff4f96;
    font-weight: 700;
}

.meta {
    color: #9296a4;
    font-size: 13px;
}

.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 9px;
    margin-top: 8px;
    margin-right: 5px;
    font-size: 12px;
    font-weight: 800;
}

.badge-bpm {
    background: rgba(255,40,123,.13);
    color: #ff579c;
    border: 1px solid rgba(255,40,123,.25);
}

.badge-type {
    background: rgba(130,80,255,.14);
    color: #b28cff;
    border: 1px solid rgba(130,80,255,.25);
}

/* ================= SECTION ================= */

.section-title {
    font-size: 25px;
    font-weight: 900;
    margin-bottom: 5px;
}

.section-subtitle {
    color: #8d919e;
    margin-bottom: 20px;
}

/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: #0b0c12;
    border-right: 1px solid rgba(255,255,255,.07);
}

.sidebar-logo {
    text-align: center;
    font-size: 46px;
}

.sidebar-title {
    text-align: center;
    font-size: 20px;
    font-weight: 900;
}

.sidebar-subtitle {
    text-align: center;
    color: #707482;
    font-size: 11px;
    letter-spacing: 2px;
}

/* ================= FOOTER ================= */

.footer {
    text-align: center;
    color: #646875;
    font-size: 11px;
    padding: 35px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 🔐 SPOTIFY AUTHENTICATION
# ============================================================

def get_credentials():

    try:
        client_id = st.secrets["SPOTIFY_CLIENT_ID"]
        client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]

        return client_id, client_secret

    except Exception:

        with st.sidebar.expander("🔐 Configuration Spotify"):

            client_id = st.text_input(
                "Client ID",
                type="password"
            )

            client_secret = st.text_input(
                "Client Secret",
                type="password"
            )

        return client_id, client_secret


client_id, client_secret = get_credentials()


# ============================================================
# 🎫 ACCESS TOKEN
# ============================================================

@st.cache_data(ttl=3300)
def get_access_token(client_id, client_secret):

    if not client_id or not client_secret:
        return None

    credentials = f"{client_id}:{client_secret}"

    encoded = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    try:

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=headers,
            data=data,
            timeout=15
        )

        if response.status_code != 200:
            return None

        return response.json().get("access_token")

    except requests.RequestException:

        return None


token = get_access_token(
    client_id,
    client_secret
)


# ============================================================
# 🔎 SPOTIFY SEARCH
# ============================================================

@st.cache_data(ttl=300)
def spotify_search(
    query,
    token,
    search_type="track",
    market="FR",
    limit=10
):

    if not token:
        return None, "Spotify non connecté."

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": query,
        "type": search_type,
        "market": market,
        "limit": min(limit, 10),
        "offset": 0
    }

    try:

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code == 401:
            return None, "Authentification Spotify refusée."

        if response.status_code == 429:
            return None, "Spotify limite temporairement les requêtes."

        if response.status_code != 200:
            return None, f"Spotify a répondu avec le code {response.status_code}."

        data = response.json()

        return data.get(
            "tracks",
            {}
        ).get(
            "items",
            [] 
        ), None

    except requests.RequestException as error:

        return None, f"Erreur réseau : {error}"


# ============================================================
# 🎯 CONSTRUCTION DE REQUÊTE
# ============================================================

def build_query(search_mode, text, style):

    text = text.strip()

    if search_mode == "🎵 Titre":

        if text:
            return f"track:{text}"

        return f"genre:{style}"

    if search_mode == "🎤 Artiste":

        if text:
            return f"artist:{text}"

        return f"genre:{style}"

    if search_mode == "🎼 Style":

        if text:
            return f"{style} {text}"

        return f"genre:{style}"

    # Recherche libre

    if text:
        return text

    return style


# ============================================================
# 🧠 MATCHING BPM — SANS FAUSSE DONNÉE
# ============================================================

def bpm_zone(target):

    if target < 100:
        return "🧊 WARM-UP"

    if target < 118:
        return "💃 GROOVE"

    if target < 135:
        return "🔥 PEAK TIME"

    return "⚡ HIGH ENERGY"


# ============================================================
# 🎵 AFFICHAGE DES MORCEAUX
# ============================================================

def display_track(track):

    name = track.get(
        "name",
        "Titre inconnu"
    )

    artists = ", ".join(
        artist.get("name", "")
        for artist in track.get(
            "artists",
            []
        )
    )

    album = track.get(
        "album",
        {}
    )

    album_name = album.get(
        "name",
        "Album inconnu"
    )

    release_date = album.get(
        "release_date",
        "—"
    )

    images = album.get(
        "images",
        []
    )

    cover = None

    if images:
        cover = images[0].get("url")

    spotify_url = track.get(
        "external_urls",
        {}
    ).get(
        "spotify"
    )

    st.markdown(
        '<div class="track-card">',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        [1.1, 4, 1.5]
    )

    # COVER
    with col1:

        if cover:

            st.image(
                cover,
                use_container_width=True
            )

    # INFO
    with col2:

        st.markdown(
            f'<div class="track-title">{name}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="artist">{artists}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="meta">💿 {album_name} • 📅 {release_date}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <span class="badge badge-type">
            🎵 SPOTIFY
            </span>

            <span class="badge badge-bpm">
            🎚️ BPM à analyser
            </span>
            """,
            unsafe_allow_html=True
        )

    # BOUTON
    with col3:

        if spotify_url:

            st.link_button(
                "▶ Ouvrir Spotify",
                spotify_url,
                use_container_width=True
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# 🎨 HEADER
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
🎧 BPM <span>MATCHER PRO</span>
</div>

<div class="hero-subtitle">
DJ OXYGÈNE • SMART MUSIC SEARCH • CLUB • AFRO • URBAN
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">🎧</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-title">DJ OXYGÈNE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">BPM MATCHER PRO V2</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 🎛️ PARAMÈTRES")

    market = st.selectbox(
        "🌍 Marché Spotify",
        [
            "FR",
            "CH",
            "CM",
            "BE",
            "CA",
            "US",
            "GB"
        ],
        index=0
    )

    st.caption(
        "FR = France • CH = Suisse • CM = Cameroun"
    )

    st.divider()

    if token:

        st.success(
            "🟢 Spotify connecté"
        )

    else:

        st.error(
            "🔴 Spotify non connecté"
        )


# ============================================================
# 🔥 RECHERCHE
# ============================================================

st.markdown(
    '<div class="section-title">🔥 Recherche DJ intelligente</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Recherche par titre, artiste, style ou combinaison personnalisée.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="search-panel">',
    unsafe_allow_html=True
)

# MODE

search_mode = st.selectbox(
    "🔎 Type de recherche",
    [
        "🔎 Recherche libre",
        "🎵 Titre",
        "🎤 Artiste",
        "🎼 Style"
    ]
)

# TEXTE

query_text = st.text_input(
    "✍️ Ta recherche",
    placeholder=(
        "Ex : Burna Boy, Fally Ipupa, Calm Down, Amapiano..."
    )
)

# STYLE

styles = [
    "Tous les styles",
    "Afrobeats",
    "Amapiano",
    "Afro House",
    "Bikutsi",
    "Makossa",
    "Zouglou",
    "Coupé-Décalé",
    "Shatta",
    "Bouyon",
    "Dancehall",
    "Reggae",
    "Rap Français",
    "Hip-Hop",
    "R&B",
    "Reggaeton",
    "House",
    "Tech House",
    "Electro",
    "Pop",
    "Rock"
]

style = st.selectbox(
    "🎼 Style musical",
    styles
)

# BPM

bpm_col1, bpm_col2 = st.columns(2)

with bpm_col1:

    target_bpm = st.number_input(
        "🎚️ BPM cible",
        min_value=40,
        max_value=220,
        value=120,
        step=1
    )

with bpm_col2:

    tolerance = st.number_input(
        "± Tolérance BPM",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )

st.caption(
    f"Zone d'énergie estimée : {bpm_zone(target_bpm)}"
)

# BOUTON

search_button = st.button(
    "🚀 RECHERCHER SUR SPOTIFY",
    type="primary",
    use_container_width=True
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 🚀 EXÉCUTION RECHERCHE
# ============================================================

if search_button:

    if not token:

        st.error(
            "🔐 Spotify n'est pas connecté. "
            "Vérifie tes Secrets Streamlit."
        )

    else:

        final_query = build_query(
            search_mode,
            query_text,
            style
        )

        # Si "Tous les styles" est sélectionné
        if style == "Tous les styles":

            if not query_text.strip():

                st.warning(
                    "Entre un titre, un artiste ou une recherche."
                )

                st.stop()

            final_query = query_text.strip()

        st.markdown(
            f"### 🔎 Résultats pour : `{final_query}`"
        )

        with st.spinner(
            "🎧 Recherche dans le catalogue Spotify..."
        ):

            results, error = spotify_search(
                final_query,
                token,
                "track",
                market,
                10
            )

        if error:

            st.error(error)

        elif not results:

            st.warning(
                "Aucun résultat trouvé."
            )

            st.info(
                "Essaie par exemple : "
                "`Burna Boy`, `Fally Ipupa`, "
                "`Amapiano` ou un titre précis."
            )

        else:

            st.success(
                f"🎧 {len(results)} résultat(s) trouvé(s)"
            )

            for track in results:

                display_track(track)


# ============================================================
# ℹ️ INFORMATIONS
# ============================================================

with st.expander("ℹ️ À propos du BPM Matcher"):

    st.markdown("""
### 🎧 BPM Matcher Pro V2

Cette version est conçue pour permettre une recherche musicale
simple et flexible depuis Spotify.

**Recherche disponible :**

- 🎵 Titre
- 🎤 Artiste
- 🎼 Style
- 🔎 Recherche libre
- 🌍 Marché Spotify
- 🎚️ BPM cible
- ± Tolérance

### ⚠️ BPM

Le BPM affiché comme **BPM cible** correspond au BPM que tu recherches.

Spotify ne fournit pas nécessairement le BPM réel du morceau dans
les données actuellement accessibles à cette application.

Le système n'invente donc pas un BPM.

### 🎯 Prochaine évolution

Une future version pourra ajouter une véritable analyse BPM
à partir d'une source de données compatible ou d'un fichier audio
fourni par le DJ.
""")


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
🎧 BPM MATCHER PRO V2 • DJ OXYGÈNE<br>
SMART SEARCH • AFRO • URBAN • CLUB
</div>
""", unsafe_allow_html=True)

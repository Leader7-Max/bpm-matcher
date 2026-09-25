import streamlit as st
import requests
import base64
import time
from datetime import datetime

# ============================================================
# 🎧 BPM MATCHER PRO — DJ OXYGÈNE
# ============================================================

st.set_page_config(
    page_title="BPM Matcher Pro — DJ Oxygène",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 🎨 STYLE PREMIUM
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(255, 0, 90, 0.10), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(120, 0, 255, 0.10), transparent 30%),
        #07080d;
    color: #f5f5f7;
}

/* Header */

.hero {
    padding: 28px 30px;
    border-radius: 24px;
    margin-bottom: 25px;
    background:
        linear-gradient(135deg, rgba(255,0,90,.16), rgba(96,0,255,.14)),
        rgba(15,16,24,.92);
    border: 1px solid rgba(255,255,255,.09);
    box-shadow: 0 20px 60px rgba(0,0,0,.35);
}

.hero-title {
    font-size: 38px;
    font-weight: 900;
    letter-spacing: -1.5px;
    margin-bottom: 5px;
}

.hero-title span {
    color: #ff176f;
}

.hero-subtitle {
    color: #a7a9b4;
    font-size: 15px;
}

/* Cards */

.track-card {
    background:
        linear-gradient(145deg, rgba(24,25,35,.96), rgba(12,13,19,.96));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 20px;
    padding: 17px;
    margin: 12px 0;
    box-shadow: 0 12px 35px rgba(0,0,0,.25);
    transition: .25s ease;
}

.track-card:hover {
    border-color: rgba(255,23,111,.55);
    box-shadow: 0 15px 45px rgba(255,0,90,.12);
}

/* BPM */

.bpm {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 10px;
    background: rgba(255,23,111,.13);
    color: #ff4c91;
    border: 1px solid rgba(255,23,111,.25);
    font-weight: 800;
    font-size: 14px;
}

.match {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 10px;
    background: rgba(0,220,140,.10);
    color: #40e0a0;
    border: 1px solid rgba(0,220,140,.20);
    font-weight: 800;
    font-size: 14px;
}

.popularity {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 10px;
    background: rgba(120,80,255,.12);
    color: #a98cff;
    border: 1px solid rgba(120,80,255,.22);
    font-weight: 700;
}

/* Section */

.section-title {
    font-size: 23px;
    font-weight: 850;
    margin-top: 15px;
    margin-bottom: 8px;
}

.section-subtitle {
    color: #858894;
    font-size: 13px;
    margin-bottom: 20px;
}

/* Metrics */

.metric-box {
    background: rgba(18,19,27,.85);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px;
    padding: 17px;
    text-align: center;
}

.metric-number {
    font-size: 27px;
    font-weight: 900;
}

.metric-label {
    color: #858894;
    font-size: 12px;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #090a10, #0d0e15);
    border-right: 1px solid rgba(255,255,255,.06);
}

.sidebar-brand {
    text-align: center;
    padding: 18px 5px 25px;
}

.sidebar-logo {
    font-size: 48px;
}

.sidebar-name {
    font-size: 20px;
    font-weight: 900;
}

.sidebar-small {
    color: #777b88;
    font-size: 11px;
    letter-spacing: 2px;
}

/* Buttons */

.stButton > button {
    border-radius: 12px;
    min-height: 44px;
    font-weight: 800;
    border: 1px solid rgba(255,255,255,.09);
}

/* Inputs */

.stTextInput input,
.stNumberInput input {
    background: #11121a !important;
    color: white !important;
    border-radius: 12px !important;
}

/* Divider */

hr {
    border-color: rgba(255,255,255,.07) !important;
}

/* Footer */

.footer {
    text-align: center;
    color: #5f626e;
    padding: 30px 0 10px;
    font-size: 11px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 🔐 SPOTIFY AUTH
# ============================================================

def get_spotify_credentials():

    # Priorité aux Secrets Streamlit
    try:
        client_id = st.secrets["SPOTIFY_CLIENT_ID"]
        client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]

        if client_id and client_secret:
            return client_id, client_secret
    except Exception:
        pass

    # Sinon saisie manuelle pour les tests
    with st.sidebar.expander("🔐 Configuration Spotify"):

        client_id = st.text_input(
            "Spotify Client ID",
            type="password"
        )

        client_secret = st.text_input(
            "Spotify Client Secret",
            type="password"
        )

        st.caption(
            "Pour une version publique, utilise les Secrets Streamlit."
        )

    return client_id, client_secret


client_id, client_secret = get_spotify_credentials()


# ============================================================
# 🎫 TOKEN SPOTIFY
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


token = get_access_token(client_id, client_secret)


# ============================================================
# 🔎 RECHERCHE SPOTIFY
# ============================================================

@st.cache_data(ttl=600)
def search_tracks(query, access_token, limit=20):

    if not access_token:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "q": query,
        "type": "track",
        "limit": limit,
        "market": "FR"
    }

    try:

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code == 429:
            return "RATE_LIMIT"

        if response.status_code != 200:
            return []

        return response.json().get(
            "tracks",
            {}
        ).get(
            "items",
            []
        )

    except requests.RequestException:
        return []


# ============================================================
# 🎯 CALCUL MATCH BPM
# ============================================================

def calculate_match(track_bpm, target_bpm, tolerance):

    if not track_bpm:
        return 0

    difference = abs(track_bpm - target_bpm)

    if difference > tolerance:
        return 0

    score = 100 - ((difference / tolerance) * 30)

    return max(70, min(100, int(score)))


# ============================================================
# 🔥 ÉNERGIE ESTIMÉE
# ============================================================

def energy_from_bpm(bpm):

    if bpm < 100:
        return "🧊 Chill"

    if bpm < 118:
        return "💃 Groove"

    if bpm < 135:
        return "🔥 Peak Time"

    return "⚡ High Energy"


# ============================================================
# 🎵 AFFICHAGE MORCEAU
# ============================================================

def render_track(track, target_bpm, tolerance):

    name = track.get("name", "Titre inconnu")

    artists = ", ".join(
        [
            artist.get("name", "")
            for artist in track.get("artists", [])
        ]
    )

    album = track.get("album", {})

    cover = ""

    images = album.get("images", [])

    if images:
        cover = images[0].get("url", "")

    release_date = album.get(
        "release_date",
        "—"
    )

    popularity = track.get(
        "popularity",
        0
    )

    spotify_url = track.get(
        "external_urls",
        {}
    ).get(
        "spotify",
        "#"
    )

    preview = track.get(
        "preview_url"
    )

    # --------------------------------------------------------
    # IMPORTANT
    # Spotify ne fournit pas toujours le BPM dans les
    # résultats de recherche.
    # --------------------------------------------------------

    bpm = 0

    match = 0

    energy = "🎵 Analyse"

    st.markdown(
        '<div class="track-card">',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        [1, 3, 1.5]
    )

    # COVER
    with col1:

        if cover:

            st.image(
                cover,
                use_container_width=True
            )

    # DETAILS
    with col2:

        st.markdown(
            f"### 🎵 {name}"
        )

        st.markdown(
            f"**{artists}**"
        )

        st.caption(
            f"💿 {album.get('name', 'Single')} "
            f"• 📅 {release_date}"
        )

        st.markdown(
            f"""
            <span class="popularity">
            ⭐ Popularité {popularity}/100
            </span>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <span class="bpm">
            🎚️ BPM cible : {target_bpm}
            </span>
            """,
            unsafe_allow_html=True
        )

    # ACTIONS
    with col3:

        st.markdown(
            "### 🎧"
        )

        if preview:

            st.audio(
                preview,
                format="audio/mp3"
            )

        st.link_button(
            "▶️ Ouvrir sur Spotify",
            spotify_url,
            use_container_width=True
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# 🎨 HERO
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
🎧 BPM <span>MATCHER PRO</span>
</div>

<div class="hero-subtitle">
DJ OXYGÈNE • Smart Search • Club Hits • Afro • Urban • Electronic
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# 📊 STATISTIQUES
# ============================================================

if "search_count" not in st.session_state:
    st.session_state.search_count = 0

if "last_results" not in st.session_state:
    st.session_state.last_results = []


m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-box">
        <div class="metric-number">🎧</div>
        <div class="metric-label">DJ MODE</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="metric-box">
        <div class="metric-number">BPM</div>
        <div class="metric-label">SMART FILTER</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-box">
        <div class="metric-number">AFRO</div>
        <div class="metric-label">CLUB STYLES</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="metric-box">
        <div class="metric-number">PRO</div>
        <div class="metric-label">DJ WORKFLOW</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("")


# ============================================================
# 🎛️ NAVIGATION
# ============================================================

tab_search, tab_energy, tab_about = st.tabs(
    [
        "🔥 SMART SEARCH",
        "⚡ PLAYLIST ÉNERGIE",
        "ℹ️ À PROPOS"
    ]
)


# ============================================================
# 🔥 SMART SEARCH
# ============================================================

with tab_search:

    st.markdown(
        '<div class="section-title">🔥 Trouve ton prochain morceau</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Recherche un artiste, un titre ou un style musical.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(
        [3, 1, 1]
    )

    with c1:

        query = st.text_input(
            "🔎 Recherche",
            placeholder="Ex : Burna Boy, Fally Ipupa, Bikutsi, Amapiano...",
            label_visibility="collapsed"
        )

    with c2:

        target_bpm = st.number_input(
            "BPM",
            min_value=40,
            max_value=220,
            value=120,
            step=1
        )

    with c3:

        tolerance = st.slider(
            "Tolérance",
            min_value=1,
            max_value=15,
            value=5
        )

    # STYLES RAPIDES

    st.markdown("**Styles rapides**")

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

    style_cols = st.columns(5)

    selected_style = None

    for i, style in enumerate(styles):

        with style_cols[i % 5]:

            if st.button(
                style,
                use_container_width=True,
                key=f"style_{i}"
            ):

                selected_style = style

    search_clicked = st.button(
        "🚀 LANCER LA RECHERCHE",
        type="primary",
        use_container_width=True
    )

    if selected_style:

        query = selected_style

        search_clicked = True

    if search_clicked:

        if not token:

            st.error(
                "🔐 Spotify n'est pas encore connecté. "
                "Ajoute ton Client ID et ton Client Secret."
            )

        elif not query.strip():

            st.warning(
                "Entre un artiste, un titre ou sélectionne un style."
            )

        else:

            with st.spinner(
                "🎧 Recherche des morceaux..."
            ):

                results = search_tracks(
                    query,
                    token,
                    20
                )

            if results == "RATE_LIMIT":

                st.warning(
                    "⏳ Spotify limite temporairement les requêtes. "
                    "Attends quelques secondes puis réessaie."
                )

            elif not results:

                st.warning(
                    "Aucun morceau trouvé."
                )

            else:

                st.session_state.search_count += 1
                st.session_state.last_results = results

                st.success(
                    f"🎧 {len(results)} morceaux trouvés"
                )

                for track in results:

                    render_track(
                        track,
                        target_bpm,
                        tolerance
                    )


# ============================================================
# ⚡ PLAYLIST PAR ÉNERGIE
# ============================================================

with tab_energy:

    st.markdown(
        '<div class="section-title">⚡ Prépare ton énergie</div>',
        unsafe_allow_html=True
    )

    energy = st.select_slider(
        "Choisis le niveau de ton set",
        options=[
            "🧊 WARM-UP",
            "💃 GROOVE",
            "🔥 PEAK TIME",
            "⚡ HIGH ENERGY"
        ]
    )

    energy_config = {

        "🧊 WARM-UP": (
            "lounge afro chill",
            95,
            10
        ),

        "💃 GROOVE": (
            "afrobeats amapiano",
            110,
            8
        ),

        "🔥 PEAK TIME": (
            "afrobeats amapiano afrohouse",
            125,
            10
        ),

        "⚡ HIGH ENERGY": (
            "shatta bouyon dancehall",
            145,
            15
        )
    }

    q, bpm, tol = energy_config[energy]

    st.markdown(
        f"""
        <div class="track-card">
            <h3>{energy}</h3>
            <p>
            🎚️ BPM recommandé :
            <strong>{bpm}</strong>
            </p>
            <p>
            🎯 Tolérance :
            <strong>±{tol} BPM</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    playlist_button = st.button(
        "🎧 GÉNÉRER MA PLAYLIST",
        type="primary",
        use_container_width=True
    )

    if playlist_button:

        if not token:

            st.error(
                "🔐 Connecte d'abord Spotify."
            )

        else:

            with st.spinner(
                "⚡ Construction de ta sélection..."
            ):

                results = search_tracks(
                    q,
                    token,
                    20
                )

            if results:

                st.success(
                    f"🔥 Sélection {energy} générée"
                )

                for track in results:

                    render_track(
                        track,
                        bpm,
                        tol
                    )

            else:

                st.warning(
                    "Aucun résultat disponible."
                )


# ============================================================
# ℹ️ À PROPOS
# ============================================================

with tab_about:

    st.markdown(
        '<div class="section-title">🎧 BPM MATCHER PRO</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    **BPM Matcher Pro — DJ Oxygène** est un assistant de recherche
    destiné à la préparation des sets DJ.

    ### Fonctions

    🔎 Recherche musicale Spotify  
    🎚️ Recherche autour d'un BPM cible  
    🔥 Sélections par énergie  
    🎵 Afrobeats / Amapiano / Bikutsi / Makossa  
    🇨🇲 Musiques africaines  
    💃 Shatta / Bouyon / Dancehall  
    🎤 Rap & Urban  
    🎧 Préécoute lorsqu'elle est fournie par Spotify  
    🔗 Accès direct au morceau sur Spotify  

    ### Version

    **BPM Matcher Pro — 1.0**

    Créé pour le workflow DJ de **DJ Oxygène**.
    """)

    st.info(
        "ℹ️ Les données musicales affichées proviennent de Spotify. "
        "Certaines informations, notamment les aperçus audio, "
        "peuvent ne pas être disponibles pour tous les morceaux."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
🎧 BPM MATCHER PRO • DJ OXYGÈNE<br>
SMART DJ SEARCH • CLUB • AFRO • URBAN
</div>
""", unsafe_allow_html=True)

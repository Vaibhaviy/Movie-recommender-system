


import streamlit as st
import pickle
import requests
import os
import random
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]


# ============================================================
# LOAD MODEL DATA
# ============================================================

movies = pickle.load(open("movies.pkl", "rb"))
similar_movies = pickle.load(open("similarity_small.pkl", "rb"))


# ============================================================
# TMDB API
# ============================================================

@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    headers = {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            poster_url = (
                f"https://image.tmdb.org/t/p/w500"
                f"{poster_path}"
            )
        else:
            poster_url = None

        # Get release year
        release_date = data.get("release_date", "")

        if release_date:
            release_year = release_date[:4]
        else:
            release_year = "N/A"

        # Get rating
        rating = data.get("vote_average", 0)

        # Get overview
        overview = data.get(
            "overview",
            "No overview available."
        )

        # Get genres
        genres = data.get("genres", [])

        genre_names = [
            genre["name"]
            for genre in genres
        ]

        return {
            "poster": poster_url,
            "overview": overview,
            "rating": rating,
            "year": release_year,
            "genres": genre_names
        }

    except requests.exceptions.RequestException:
        return {
            "poster": None,
            "overview": "Movie information could not be loaded.",
            "rating": 0,
            "year": "N/A",
            "genres": []
        }


# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

# def recommend(movie):

#     movie_index = movies[movies["title"] == movie].index[0]

#     distances = similarity[movie_index]

#     movies_list = sorted(
#         list(enumerate(distances)),
#         reverse=True,
#         key=lambda x: x[1]
#     )[1:6]

#     recommended_movies = []
#     recommended_details = []

#     for i in movies_list:

#         movie_id = movies.iloc[i[0]].movie_id

#         movie_title = movies.iloc[i[0]].title

#         details = fetch_movie_details(movie_id)

#         recommended_movies.append(movie_title)
#         recommended_details.append(details)

#     return recommended_movies, recommended_details

def recommend(movie):

    movie_index = movies[movies["title"] == movie].index[0]

    # Get precomputed similar movies
    movies_list = similar_movies[movie_index][:5]

    recommended_movies = []
    recommended_details = []

    for movie_index, similarity_score in movies_list:

        movie_id = movies.iloc[movie_index].movie_id

        movie_title = movies.iloc[movie_index].title

        details = fetch_movie_details(movie_id)

        recommended_movies.append(movie_title)
        recommended_details.append(details)

    return recommended_movies, recommended_details


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# ORIGINAL ROTATING TAGLINES
# (written for this app — not lines from any film, so nothing
# here is quoted/copyrighted movie dialogue)
# ============================================================

TAGLINES = [
    "Every great story starts with someone hitting play.",
    "Good taste in movies is just good taste in stories, worn loudly.",
    "The right recommendation is a little bit of magic and a little bit of math.",
    "Somewhere between the popcorn and the credits, a new favorite is born.",
    "A great film finds you exactly when you need it.",
    "Cinema is the art of showing you a life you'll never live, from the inside.",
]


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
   GLOBAL PAGE
   ======================================================== */

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(255, 75, 110, 0.08),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 80%,
            rgba(255, 143, 75, 0.07),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #0f0f18,
            #171724
        );

    color: #ffffff;
}


/* ========================================================
   HIDE STREAMLIT DEFAULT UI
   ======================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* ========================================================
   MAIN CONTAINER
   ======================================================== */

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* ========================================================
   HEADER
   ======================================================== */

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;

    background:
        linear-gradient(
            90deg,
            #ff4b6e,
            #ff8f4b,
            #ffc05c
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    margin-top: 20px;
    margin-bottom: 6px;

    letter-spacing: -0.5px;
}


.subtitle {
    text-align: center;
    color: #ffffff !important;
    font-size: 17px;
    font-weight: 500;
    margin-bottom: 8px;
}


.tagline {
    text-align: center;
    color: #ffb08a !important;
    font-size: 14px;
    font-style: italic;
    font-weight: 500;
    margin-bottom: 35px;
    opacity: 0.95;
}


/* ========================================================
   SELECT MOVIE LABEL
   ======================================================== */

div[data-testid="stSelectbox"] label {
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 700 !important;
}


/* ========================================================
   SELECTBOX
   ======================================================== */

div[data-baseweb="select"] > div {
    background-color: #20202b !important;
    border: 1px solid #3a3a48 !important;
    border-radius: 10px !important;
    min-height: 48px;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}


div[data-baseweb="select"] > div:hover {
    border-color: #ff4b6e !important;

    box-shadow:
        0 0 12px
        rgba(255, 75, 110, 0.12);
}


/* Selected movie */

div[data-baseweb="select"] span {
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}


div[data-baseweb="select"] input {
    color: #ffffff !important;
}


/* Dropdown */

ul[role="listbox"] {
    background-color: #20202b !important;
}


ul[role="listbox"] li {
    color: #ffffff !important;
    background-color: #20202b !important;
}


ul[role="listbox"] li:hover {
    background-color: #30303d !important;
}


/* ========================================================
   FIND MOVIES BUTTON
   ======================================================== */

div.stButton > button {
    width: 100%;
    min-height: 48px;

    margin-top: 10;
    margin-bottom: 0;

    background:
        linear-gradient(
            90deg,
            #ff4b6e,
            #ff8f4b
        );

    color: #ffffff !important;

    font-size: 15px;
    font-weight: 700;

    border: none;
    border-radius: 10px;

    padding: 10px 14px;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}


div.stButton > button:hover {
    color: #ffffff !important;

    transform: translateY(-2px);

    box-shadow:
        0 8px 20px
        rgba(255, 75, 110, 0.35);
}


div.stButton > button p {
    color: #ffffff !important;
}


/* ========================================================
   SECTION TITLE
   ======================================================== */

.section-title {
    font-size: 25px;
    font-weight: 700;

    color: #ffffff !important;

    margin-top: 35px;
    margin-bottom: 20px;

    border-left: 5px solid #ff4b6e;

    padding-left: 12px;
}


/* ========================================================
   MOVIE CARDS
   ======================================================== */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        linear-gradient(
            160deg,
            #1c1c28,
            #16161f
        ) !important;

    border-radius: 14px !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.12)
        !important;

    padding: 8px !important;

    min-height: 650px;

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease,
        border-color 0.25s ease;
}


div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-6px);

    box-shadow:
        0 16px 30px
        rgba(255, 75, 110, 0.20);

    border-color:
        rgba(255, 75, 110, 0.50)
        !important;
}


/* ========================================================
   POSTER
   ======================================================== */

div[data-testid="stImage"] {
    width: 100%;
}


div[data-testid="stImage"] img {
    border-radius: 10px;
    width: 100%;
    object-fit: cover;
}


/* ========================================================
   RANK BADGE
   ======================================================== */

.rank {
    display: inline-block;

    color: #ffd080 !important;

    font-size: 12px;
    font-weight: 700;

    letter-spacing: 0.3px;
    text-transform: uppercase;

    background:
        rgba(255, 179, 71, 0.12);

    border:
        1px solid
        rgba(255, 179, 71, 0.35);

    border-radius: 999px;

    padding: 4px 10px;

    margin-bottom: 10px;
}


/* ========================================================
   MOVIE TITLE
   ======================================================== */

.movie-title {
    font-size: 18px;
    font-weight: 700;

    color: #ffffff !important;

    margin-top: 10px;

    line-height: 1.4;

    min-height: 50px;
}


/* ========================================================
   MOVIE INFORMATION
   ======================================================== */

.movie-info {
    color: #eeeeF5 !important;

    font-size: 14px;
    font-weight: 500;

    line-height: 1.6;

    margin-top: 5px;
}


/* ========================================================
   GENRE PILLS
   ======================================================== */

.genre-pill {
    display: inline-block;

    color: #ffffff !important;

    font-size: 12px;
    font-weight: 500;

    background:
        rgba(255, 255, 255, 0.08);

    border:
        1px solid
        rgba(255, 255, 255, 0.14);

    border-radius: 999px;

    padding: 3px 9px;

    margin:
        3px 3px 0 0;
}


/* ========================================================
   OVERVIEW EXPANDER
   ======================================================== */

div[data-testid="stExpander"] {
    border-radius: 10px !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.14)
        !important;

    background-color:
        rgba(255, 255, 255, 0.03)
        !important;

    margin-top: 10px;
}


div[data-testid="stExpander"] summary {
    color: #ffffff !important;

    font-size: 14px !important;

    font-weight: 700 !important;
}


div[data-testid="stExpander"] summary span {
    color: #ffffff !important;
}


/* Overview text */

div[data-testid="stExpander"] p {
    color: #ffffff !important;

    font-size: 14px !important;

    line-height: 1.65 !important;
}


div[data-testid="stExpander"] div {
    color: #ffffff !important;
}


/* ========================================================
   GENERAL STREAMLIT TEXT
   ======================================================== */

[data-testid="stMarkdownContainer"] p {
    color: #ffffff;
}


[data-testid="stMarkdownContainer"] {
    color: #ffffff;
}


/* ========================================================
   DIVIDER
   ======================================================== */

hr {
    border-color:
        rgba(255, 255, 255, 0.10) !important;
}


/* ========================================================
   MOBILE RESPONSIVENESS
   ======================================================== */

@media (max-width: 768px) {

    .main-title {
        font-size: 34px;
    }

    .subtitle {
        font-size: 14px;
    }

    .tagline {
        font-size: 12px;
    }

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎬 Movie Recommender System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Discover movies similar to the ones you love '
    'using content-based recommendation'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="tagline">🎞️ "{random.choice(TAGLINES)}"</div>',
    unsafe_allow_html=True
)


# ============================================================
# MOVIE SELECTION
# ============================================================

col1, col2 = st.columns([5, 1])

with col1:

    selected_movie = st.selectbox(
        "Select a movie",
        movies["title"].values
    )

with col2:

    recommend_clicked = st.button(
        "🍿 Find Movies"
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

if recommend_clicked:

    with st.spinner("Finding similar movies..."):

        recommendations, details = recommend(
            selected_movie
        )

    st.markdown(
        '<div class="section-title">'
        '🎯 Recommended for you'
        '</div>',
        unsafe_allow_html=True
    )

    # Create 5 columns
    cols = st.columns(5)

    for i in range(5):

        with cols[i]:

            with st.container(border=True):

                movie_title = recommendations[i]
                movie_details = details[i]

                # Rank
                if i == 0:
                    rank_text = "🏆 Top Pick"
                else:
                    rank_text = f"#{i + 1} Match"

                st.markdown(
                    f'<div class="rank">{rank_text}</div>',
                    unsafe_allow_html=True
                )

                # Poster
                if movie_details["poster"]:

                    st.image(
                        movie_details["poster"],
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Poster not available"
                    )

                # Movie title
                st.markdown(
                    f'<div class="movie-title">'
                    f'{movie_title}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Rating + year
                rating = movie_details["rating"]
                year = movie_details["year"]

                st.markdown(
                    f'<div class="movie-info">'
                    f'⭐ {rating:.1f}/10 &nbsp; '
                    f'📅 {year}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Genres
                genres = movie_details["genres"]

                if genres:

                    genre_html = "".join(
                        f'<span class="genre-pill">{g}</span>'
                        for g in genres[:3]
                    )

                    st.markdown(
                        f'<div style="margin-top:6px;">{genre_html}</div>',
                        unsafe_allow_html=True
                    )

                # Overview
                overview = movie_details["overview"]

                with st.expander("📝 Overview"):

                    st.write(overview)


# ============================================================
# FOOTER / PROJECT INFORMATION
# ============================================================

st.markdown("---")

# st.markdown(
#     """
#     <div style="text-align:center; color:#888;">

#     🎬 <b>Movie Recommender System</b>

#     <br>

#     Content-Based Recommendation using
#     <b>CountVectorizer</b> and
#     <b>Cosine Similarity</b>

#     <br><br>

#     Movie posters and information provided by TMDB

#     </div>
#     """,
#     unsafe_allow_html=True
# )

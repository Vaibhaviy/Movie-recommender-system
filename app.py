


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

    /* Main background */
    .stApp {
        background: linear-gradient(
            135deg,
            #0f0f18,
            #171724
        );
    }

    /* Hide Streamlit menu */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Main title */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #ffb347;
        margin-top: 20px;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #aaaab5;
        font-size: 17px;
        margin-bottom: 10px;
    }

    /* Rotating tagline */
    .tagline {
        text-align: center;
        color: #ff8f4b;
        font-size: 14px;
        font-style: italic;
        font-weight: 500;
        margin-bottom: 35px;
        opacity: 0.9;
    }

    /* Section title */
    .section-title {
        font-size: 25px;
        font-weight: 700;
        color: white;
        margin-top: 35px;
        margin-bottom: 20px;
        border-left: 5px solid #ff4b6e;
        padding-left: 12px;
    }

    .movie-title {

    font-size: 17px;

    font-weight: 700;

    color: #ffffff;

    margin-top: 10px;

    min-height: 48px;

    height: 48px;

    line-height: 1.35;

    overflow: hidden;

    display: -webkit-box;

    -webkit-line-clamp: 2;

    -webkit-box-orient: vertical;

}

    /* Movie information */
    .movie-info {
        color: #bdbdc7;
        font-size: 13px;
        line-height: 1.5;
    }

    .overview {

    color: #c8c8d0;

    font-size: 14px;

    line-height: 1.6;

    margin-top: 8px;

    height: 125px;

    overflow: hidden;

    display: -webkit-box;

    -webkit-line-clamp: 5;

    -webkit-box-orient: vertical;

}

    .rank {

    display: inline-block;

    color: #ffb347;

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

    min-height: 26px;

    box-sizing: border-box;

}

    /* Genre pills */
    .genre-pill {
        display: inline-block;
        color: #d8d8e2;
        font-size: 11px;
        font-weight: 500;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 999px;
        padding: 2px 9px;
        margin: 2px 3px 0 0;
    }

    /* ========================================================
   FIND MOVIES BUTTON
   ======================================================== */

div.stButton {
    display: flex;
    align-items: flex-end;
    height: 100%;
}

div.stButton > button {

    width: 100%;

    min-height: 50px;

    background:
        linear-gradient(
            90deg,
            #ff4b6e,
            #ff8f4b
        );

    color: white;

    font-weight: 700;

    border: none;

    border-radius: 10px;

    padding: 10px 14px;

    margin-bottom: 100px;
    margin-top:20px;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

div.stButton > button:hover {

    color: white;

    border: none;

    transform: translateY(-2px);

    box-shadow:
        0 8px 18px
        rgba(255, 75, 110, 0.35);
}

    /* Select box */
    div[data-baseweb="select"] > div {
        background-color: #20202b;
        border-radius: 8px;
        transition: border-color 0.2s ease;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: #ff4b6e !important;
    }

    /* ========================================================
   MOVIE CARDS
   ======================================================== */

div[data-testid="stVerticalBlockBorderWrapper"] {

    background:
        linear-gradient(
            160deg,
            #1c1c28,
            #15151f
        ) !important;

    border-radius: 14px !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.10) !important;

    padding: 10px !important;

    min-height: 700px;

    height: 700px;

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease,
        border-color 0.25s ease;

    box-sizing: border-box;

    overflow: hidden;
}


div[data-testid="stVerticalBlockBorderWrapper"]:hover {

    transform: translateY(-6px);

    box-shadow:
        0 16px 30px
        rgba(255, 75, 110, 0.22);

    border-color:
        rgba(255, 75, 110, 0.45) !important;
}

    /* ========================================================
   POSTERS
   ======================================================== */

div[data-testid="stImage"] {

    height: 330px;

    overflow: hidden;

}


div[data-testid="stImage"] img {

    width: 100%;

    height: 330px;

    object-fit: cover;

    border-radius: 10px;

}

    /* Expander styling */
    .stExpander {
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
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

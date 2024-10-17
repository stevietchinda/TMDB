import requests
import time
import streamlit as st
from requests.exceptions import RequestException
from config import TMDB_API_KEY 

#Lancement du ficher 
# streamlit run app.py

# Fonction pour gérer les erreurs et retry
def handle_api_errors(func):
    def wrapper(*args, **kwargs):
        max_retries = 5
        retry_wait_time = 2  
        retries = 0

        while retries < max_retries:
            try:
                response = func(*args, **kwargs)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Trop de requêtes
                    print("Too many requests. Waiting before retrying...")
                    time.sleep(retry_wait_time)
                elif response.status_code in [500, 503]:  # Erreurs serveur
                    print(f"Server error {response.status_code}. Retrying...")
                    time.sleep(retry_wait_time)
                elif response.status_code in [401, 403]:  # Problèmes d'autorisation
                    return f"Authorization error: {response.status_code}. Check your API key."
                elif response.status_code == 404:  # Ressource non trouvée
                    return f"Movie with ID {kwargs['movie_id']} not found."
                else:
                    return f"Unexpected error: {response.status_code}"
            except RequestException as e:
                print(f"Request failed: {e}. Retrying...")
                time.sleep(retry_wait_time)
            retries += 1

        return f"Failed after {max_retries} retries."
    
    return wrapper

@handle_api_errors
def tmdb_request(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    return requests.get(url, params=params)

# Fonction pour obtenir les détails du film
def get_movie_details(movie_id):
    data = tmdb_request(movie_id)

    if isinstance(data, dict):  
        movie_details = {
            "title": data.get("title"),
            "release_date": data.get("release_date"),
            "genres": [genre['name'] for genre in data.get("genres", [])],
            "popularity": data.get("popularity"),
            "vote_average": data.get("vote_average")
        }
        return movie_details
    else:
        return data

# Mise en cache 
@st.cache_data(ttl=3600)  # Cache pour une durée d'une heure
def get_movie_details_cached(movie_id):
    return get_movie_details(movie_id)

# Interface Streamlit
st.title("Les films")

# Récupération de l'ID du film via l'interface utilisateur
movie_id = st.text_input("Enter Movie ID", "550")

# Bouton pour obtenir les détails du film
if st.button("Details des films"):
    details = get_movie_details_cached(movie_id)
    st.write(details)
    

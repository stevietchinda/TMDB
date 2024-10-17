import requests
import gzip
import json
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import text

# Générer l'URL du fichier à télécharger
BASE_URL = "http://files.tmdb.org/p/exports/"
date_today = datetime.datetime.now().strftime("%m_%d_%Y")
file_name = f"movie_ids_{date_today}.json.gz"
download_url = f"{BASE_URL}{file_name}"

# Télécharge le fichier .gz depuis l'URL générée
response = requests.get(download_url, stream=True)
if response.status_code == 200:
    with open("movie_ids.json.gz", "wb") as f:
        f.write(response.content)
    print("Fichier téléchargé avec succès.")
else:
    print(f"Impossible de télécharger le fichier. Statut : {response.status_code}")
    exit()

# Décompresse le fichier .gz et lire les lignes JSON
movie_data = []
try:
    with gzip.open("movie_ids.json.gz", "rb") as gz_file:
        for line in gz_file:
            movie_data.append(json.loads(line.decode('utf-8')))
    print("Fichier décompressé et lignes lues avec succès.")
except Exception as e:
    print(f"Erreur lors de la décompression du fichier : {e}")
    exit()

# Transforme le JSON en DataFrame
df = pd.DataFrame(movie_data)

# Connexion à une base de données relationnelle avec SQLAlchemy
engine = sqlalchemy.create_engine('sqlite:///tmdb_movies.db')

# Insertion des données dans la base de données
try:
    df.to_sql('movies', con=engine, if_exists='replace', index=False)
    print("Données insérées dans la base de données avec succès.")
except Exception as e:
    print(f"Erreur lors de l'insertion des données dans la base de données : {e}")
    exit()

# Compte le nombre d'enregistrements insérés
with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM movies"))
    count = result.fetchone()[0]
    print(f"Nombre d'enregistrements dans la table 'movies' : {count}")

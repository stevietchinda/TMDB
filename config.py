import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('token_API')

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
import asyncio
import aiohttp
import time
from aiocache.serializers import JsonSerializer
from aiocache import cached
from config import TMDB_API_KEY

BASE_URL = 'https://api.themoviedb.org/3'

liste_url = [f"{BASE_URL}/movie/550?api_key={TMDB_API_KEY}",  
            f"{BASE_URL}/movie/552?api_key={TMDB_API_KEY}",
            f"{BASE_URL}/movie/552?api_key={TMDB_API_KEY}"]

# Fonction asynchrone pour effectuer une requête API
@cached(ttl=3600, serializer=JsonSerializer()) # Cache d'une heure avec format JSON
async def fetch_data_with_cache(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()  # Retourne la réponse en format JSON
            else:
                return f"Error: {response.status}"
    except Exception as e:
        return f"Request failed: {e}"
    
    
# Fonction pour gérer plusieurs requêtes en parallèle
async def fetch_all_data_with_cache(api_routes):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for route in api_routes:
            tasks.append(fetch_data_with_cache(session, route))
        # Lancer toutes les requêtes de manière asynchrone et attendre leur achèvement
        results = await asyncio.gather(*tasks)
        return results
    
    
# Fonction principale pour simuler la charge élevée
def simulate_high_load_with_cache(api_routes, num_requests=1000):
    start_time = time.time()
    loop = asyncio.get_event_loop()

    for _ in range(num_requests):  # Simulation de `num_requests` requêtes
        results = loop.run_until_complete(fetch_all_data_with_cache(api_routes))
        # Afficher les résultats partiellement pour éviter de surcharger la console
        print(results[:3])  # Juste un échantillon des premières réponses

    print(f"Total time for {num_requests} requests with cache: {time.time() - start_time:.2f} seconds")

# Simulation d'une charge élevée (1000 requêtes) avec cache
simulate_high_load_with_cache(liste_url, num_requests=2)
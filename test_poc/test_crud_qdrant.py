import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import Distance, VectorParams

from sentence_transformers import SentenceTransformer

import cityhash

CITIES_DATA = "cities_data"

def hash_string(string):
    """Hashes a string into an unsigned 64-bit integer (CityHash64 algorithm)."""
    return cityhash.CityHash64(string)


def index_data(file_path: str):
    first_collection = client.recreate_collection(
        collection_name=CITIES_DATA,
        vectors_config=VectorParams(
            size=VECTOR_DIM_SIZE, distance=Distance.COSINE)
    )
    print(first_collection)

    cities_data = read_json_file(file_path)
    if cities_data:
        # Now you have the data as a list
        for city in cities_data:
            id = hash_string(json.dumps(city))
            corpus = ' '.join(city['travelTypes']) + " - " + \
                city['name'] + " - " + city['description']
            city_embedding = model.encode(
                corpus, convert_to_tensor=True).tolist()

            print(f"Indexing City: {city['name']}, Latitude: {city['lat']}, Longitude: {city['lon']}, id {id}")
            # Add more fields as needed

            p = PointStruct(id=id, vector=city_embedding,
                            payload={"city": city})
            operation_info = client.upsert(
                collection_name=CITIES_DATA,
                wait=True,
                points=[p]
            )

    # indexing
    client.create_payload_index(
        collection_name=CITIES_DATA,
        field_name="city.population",
        field_schema="integer",
    )
    client.create_payload_index(
        collection_name=CITIES_DATA,
        field_name="city.travelTypes",
        field_schema="keyword",
    )
    client.create_payload_index(
        collection_name=CITIES_DATA,
        field_name="city",
        field_schema="geo",
    )


# Initialize the client
client = QdrantClient("localhost", port=6333)  # For production

MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
model = SentenceTransformer(MODEL_NAME)
VECTOR_DIM_SIZE = model.get_sentence_embedding_dimension()


def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def run_query(query: str, radius_in_km: int, geo_location, travelTypes = [], avg_population = 10000000):
    r_in_km = 1000.0 * radius_in_km
    query_embedding = model.encode(query, convert_to_tensor=True).tolist()

    search_result = client.search(
        collection_name=CITIES_DATA,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="city.population",
                    range=models.Range(
                        gt=None,
                        gte=None,
                        lt=avg_population,
                        lte=None
                    ),
                ),
                models.FieldCondition(
                    key="city.travelTypes",
                    match=models.MatchAny(any=travelTypes),
                ),
                models.FieldCondition(
                    key="city",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(
                            lat= geo_location['lat'],
                            lon= geo_location['lon']
                        ),
                        radius=r_in_km,
                    ),
                )
            ]
        ),
        query_vector=query_embedding,
        limit=5
    )
    return search_result


# main start
file_path = './data/top_cities_vietnam.json'

# 1. create collecion and index data
index_data(file_path)

# 2. run_query
query = 'Any travel place with cool climate and sunny beach'
radius_in_km = 1000
avg_population = 1000000
geo_location = {'lat':10.7619578, 'lon': 106.6873586}
categories = ["History", "Nightlife"]
search_result = run_query(query, radius_in_km, geo_location, categories, avg_population)

# 3. Print results
print('\n\n Query: ' + query)
i = 0
for rs in search_result:
    i = i + 1
    print(str(i) + ":" + rs.payload['city']['name'] + ', ' + rs.payload['city']['description'])
    
city_data = client.get_po(
    collection_name=CITIES_DATA,
    ids=[3754852833135301533]  # Fetch the point with the given profile_id
)
print(city_data)

# The answer should be
#  Query: Any travel place with cool climate and sunny beach
# 1:Nha Trang, A popular beach resort town with pristine beaches, vibrant nightlife, and island hopping opportunities.
# 2:Quy Nhon, A coastal city with long stretches of beaches, historical Cham sites, and less crowded than more popular destinations.
# 3:Con Dao, An archipelago with pristine beaches, historical sites of former prisons, and protected natural areas for hiking and diving.
# 4:Hoi An, A UNESCO World Heritage city with charming ancient streets, well-preserved architecture, and a laid-back atmosphere.
# 5:Hue, The former imperial capital of Vietnam, steeped in history with a majestic citadel, tombs of past emperors, and the serene Perfume River.
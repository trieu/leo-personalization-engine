from personalization import get_all_collection_names_in_qdrant, init_db_personalization
init_db_personalization()

from personalization_router import api_personalization
VERSION_API = "0.0.1"
SERVICE_NAME = "LEO Personalization Engine API"

# default
@api_personalization.get("/")
async def root():
    return {"status": "API is ready","service":SERVICE_NAME, "version":VERSION_API}

# collections
@api_personalization.get("/collections")
async def collections():
    return get_all_collection_names_in_qdrant()

api_service = api_personalization
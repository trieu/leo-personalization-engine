
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, MatchExcept, Filter
from qdrant_client.http.models import VectorParams, Distance, FieldCondition
from sentence_transformers import SentenceTransformer
import hashlib


# Initialize Qdrant client (Assuming Qdrant is running locally)
qdrant_client = QdrantClient(host="localhost", port=6333)

# Create collections for profile and product in Qdrant
PROFILE_COLLECTION = "cdp_profile"
PRODUCT_COLLECTION = "cdp_product"

MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'

VECTOR_MODEL = SentenceTransformer(MODEL_NAME)
VECTOR_DIM_SIZE = VECTOR_MODEL.get_sentence_embedding_dimension() 
PROFILE_VECTOR_SIZE = VECTOR_DIM_SIZE
PRODUCT_VECTOR_SIZE = VECTOR_DIM_SIZE * 3

# Function to get the text embeddings
def get_text_embedding(text):
    if not text or not isinstance(text, str):
        print(f"Error: Invalid text input for embedding: {text}")
        return np.zeros(VECTOR_DIM_SIZE)  # Return a zero vector if the text is invalid
    
    # Generate embeddings using the VECTOR_MODEL
    text_embedding = VECTOR_MODEL.encode(text, convert_to_tensor=True)
    
    # Ensure tensor is on CPU before converting to NumPy
    if text_embedding.is_cuda:
        numpy_embedding = text_embedding.cpu().numpy()
    else:
        numpy_embedding = text_embedding.numpy()
    
    return numpy_embedding


# Updated function to create collection in Qdrant
def create_qdrant_collection_if_not_exists(collection_name: str, vector_size: int):
    # Check if collection already exists
    existing_collections = qdrant_client.get_collections().collections
    if collection_name not in [col.name for col in existing_collections]:
        # Create collection with vectors_config
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"Collection '{collection_name}' created successfully.")
    else:
        print(f"Collection '{collection_name}' already exists.")

# Create collections if not exist
create_qdrant_collection_if_not_exists(PROFILE_COLLECTION, PROFILE_VECTOR_SIZE)
create_qdrant_collection_if_not_exists(PRODUCT_COLLECTION, PRODUCT_VECTOR_SIZE)


# Build profile vector based on attributes
def build_profile_vector(page_view_keywords, purchase_keywords, interest_keywords):        
    # Ensure none of the input lists are empty to avoid issues
    if not page_view_keywords or not purchase_keywords or not interest_keywords:
        print("Error: One or more keyword lists are empty.")
        return None

    # Get embeddings for page views, purchases, and interests
    page_view_vectors = np.array([get_text_embedding(k) for k in page_view_keywords])
    purchase_vectors = np.array([get_text_embedding(k) for k in purchase_keywords])
    interest_vectors = np.array([get_text_embedding(k) for k in interest_keywords])

    # Aggregate vectors by averaging or weighted sum
    page_view_vector = np.mean(page_view_vectors, axis=0)
    purchase_vector = np.mean(purchase_vectors, axis=0)
    interest_vector = np.mean(interest_vectors, axis=0)

    # Final profile vector by combining (weights can be adjusted)
    profile_vector = 0.3 * page_view_vector + 0.4 * purchase_vector + 0.3 * interest_vector
    return profile_vector


# Build product vector based on attributes
def build_product_vector(product_name, product_category, product_keywords):
    # Can use advanced models like BERT for better embeddings
    name_vector = get_text_embedding(product_name)
    category_vector = get_text_embedding(product_category)
    keyword_vectors = np.array([get_text_embedding(k) for k in product_keywords])

    # Aggregate keyword vectors by averaging
    keyword_vector = np.mean(keyword_vectors, axis=0)

    # Final product vector by concatenating all (can use other combination strategies)
    product_vector = np.concatenate([name_vector, category_vector, keyword_vector])
    return product_vector

# Convert string to point_id using hashlib for large dataset
def string_to_point_id(input_string):
    # Use SHA-256 hash and convert it to an integer with 16 digits
    # the resulting integer to a range between 0 and 99,999,999,999,999,999 (16 digits).
    return int(hashlib.sha256(input_string.encode('utf-8')).hexdigest(), 16) % (10 ** 16) 

# Helper function to add vectors to Qdrant collection
def add_vector_to_qdrant(collection_name:str, object_id, vector, payload):
    point_id = string_to_point_id(str(object_id))
    point = PointStruct(
        id=point_id,  # Use profile_id as the point ID
        vector=vector.tolist(),  # Store the vector
        payload=payload
    )    
    qdrant_client.upsert(
        collection_name=collection_name,
        points=[point]
    )

# Function to add profile to Qdrant
def add_profile_to_qdrant(profile_id, page_view_keywords, purchase_keywords, interest_keywords, additional_info):
    profile_vector = build_profile_vector(page_view_keywords, purchase_keywords, interest_keywords)

    if profile_vector is None:
        print(f"Error: Could not generate a valid vector for profile {profile_id}.")
        return

    # Save profile vector to Qdrant
    payload = {"profile_id": profile_id, "additional_info": additional_info}
    payload['page_view_keywords'] = page_view_keywords
    payload['purchase_keywords'] = purchase_keywords
    payload['interest_keywords'] = interest_keywords
    add_vector_to_qdrant(PROFILE_COLLECTION, profile_id, profile_vector, payload)
    print(f"Profile {profile_id} added to Qdrant")
    return profile_id


# Function to add product to Qdrant
def add_product_to_qdrant(product_id, product_name, product_category, product_keywords, additional_info):
    product_vector = build_product_vector(product_name, product_category, product_keywords)
    
    if product_vector is None:
        print(f"Error: Could not generate a valid vector for product {product_id}.")
        return

    # Save product vector to Qdrant
    payload = {"product_id": product_id, "name": product_name,
               "category": product_category, "additional_info": additional_info}
    add_vector_to_qdrant(PRODUCT_COLLECTION, product_id, product_vector, payload)
    print(f"Product {product_id} added to Qdrant")
    return product_id


# Recommend products based on profile vector
def recommend_products_for_profile(profile_id, top_n=8, except_product_ids=[]):
    try:
        point_id = string_to_point_id(profile_id)
        profile_data = qdrant_client.retrieve(
            collection_name=PROFILE_COLLECTION,
            ids=[point_id]  # Fetch the point with the given profile_id
        )
        print(profile_data)

        # Check if profile exists and has a vector
        if not profile_data or len(profile_data) == 0:
            print(f"Profile {profile_id} not found in Qdrant.")
            return []
        
        profile = profile_data[0]
        if len(profile.payload) == 0:
            print(f"Profile {profile_id} does not have a vector in Qdrant.")
            return []

        profile_vector = build_profile_vector(
            profile.payload['page_view_keywords'],
            profile.payload['purchase_keywords'],
            profile.payload['interest_keywords']
        )
         
        vector = np.concatenate([profile_vector, profile_vector, profile_vector])

        # Use profile vector to search for closest products in the product collection
        search_results = qdrant_client.search(
            collection_name=PRODUCT_COLLECTION,
            query_vector= vector,            
            query_filter=Filter(
                must=[
                    FieldCondition(
                       key="product_id", match=MatchExcept(**{"except": except_product_ids})
                    )
                ]
            ),
            limit=top_n
        )

        # Extract product information from the search results
        recommended_products = [
            {
                "product_id": result.payload.get('product_id'),
                "product_name": result.payload.get('name'),
                "product_category": result.payload.get('category'),
                "brand": result.payload.get('additional_info')['brand'],
                "price": result.payload.get('additional_info')['price'],
                "score": result.score
            }
            for result in search_results
        ]

        return {"profile":profile.payload, "recommended_products": recommended_products} 

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []


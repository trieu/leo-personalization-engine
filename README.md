# LEO Personalization Engine API

This API provides personalized product recommendations using Qdrant for vector similarity search. It allows you to:

- Add user profiles with their interests, purchase history, and other attributes.
- Add product data with categories, keywords, and additional information.
- Get real-time product recommendations for a specific user profile.

## Requirements

- Python 3.10+
- FastAPI
- Pydantic
- Qdrant Vector Database. Refer to the Qdrant documentation for instructions: https://qdrant.tech/documentation/quick-start/
- Qdrant client library (install with `pip install qdrant-client`)

## Installation

1. Clone the repository:
```bash
   git clone https://github.com/trieu/leo-personalization-engine
```

2. Create env
```bash
    python -m venv env
    source env/bin/activate
```

3. Install the dependencies:
```bash
   pip install -r requirements.txt
```

4. Start the Qdrant server:
```bash
   ./start_qdrant.sh
```

5. Next, create a .env file by coping the file sample.env or create your own file with content:
```
    QDRANT_HOST=localhost
    QDRANT_PORT=6333

    API_HOST=0.0.0.0
    API_PORT=8000
```

## Running the API

```bash
uvicorn main:api_personalization --reload 
```
This will start the API server. You can access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### Profiles

- **`POST /add-profile/`**
    - Adds a single user profile to the database.
    - Request body: `ProfileRequest` object (see below)
    - Response: `{"status": "Profile added successfully"}`
- **`POST /add-profiles/`**
    - Adds multiple user profiles to the database in bulk.
    - Request body: List of `ProfileRequest` objects 
    - Response: `{"status": "All profiles added successfully"}`
- **`POST /check-profile-for-recommendation/`**
    - Add or update a profile, then  get real-time recommendations for the profile
    - Request body: `ProfileRequest` object
    - Response: List of recommended products (see example below)

### Products

- **`POST /add-product/`**
    - Adds a single product to the database.
    - Request body: `ProductRequest` object (see below)
    - Response: `{"status": "Product added successfully"}`
- **`POST /add-products/`**
    - Adds multiple products to the database in bulk.
    - Request body: List of `ProductRequest` objects
    - Response: `{"status": "All products added successfully"}`

### Recommendations

- **`GET /recommend/{profile_id}`**
    - Gets personalized product recommendations for a given profile ID.
    - Path parameters:
        - `profile_id`: The ID of the user profile.
    - Query parameters:
        - `top_n` (optional): The maximum number of recommendations to return (default: 8).
        - `except_product_ids` (optional): Comma-separated string of product IDs to exclude from recommendations (e.g., "item_1,item_3").
    - Response: List of recommended product IDs (see example below)

## Data Models

**ProfileRequest:**

```json
{
    "profile_id": "user123",
    "page_view_keywords": ["smartphone", "electronics"],
    "purchase_keywords": ["headphones", "bluetooth"],
    "interest_keywords": ["music", "technology"],
    "additional_info": {"age": 25, "location": "USA"},
    "max_recommendation_size": 10, 
    "except_product_ids": ["item_5", "item_10"] 
}
```

**ProductRequest:**

```json
{
    "product_id": "item_1",
    "product_name": "Wireless Headphones",
    "product_category": "Electronics",
    "product_keywords": ["music", "bluetooth", "noise-cancelling"],
    "additional_info": {"brand": "Sony", "price": 200}
}
```

## Example Usage

### Adding a Profile

```bash
curl -X POST \
  http://localhost:8000/add-profile/ \
  -H 'Content-Type: application/json' \
  -d '{
    "profile_id": "user123",
    "page_view_keywords": ["smartphone", "electronics"],
    "purchase_keywords": ["headphones", "bluetooth"],
    "interest_keywords": ["music", "technology"],
    "additional_info": {"age": 25, "location": "USA"}
}'
```
### Getting Recommendations

```bash
curl -X GET \
  "http://localhost:8000/recommend/user123?top_n=5&except_product_ids=item_2,item_4" 
```

## Future Improvements

- Implement more sophisticated vectorization techniques for user profiles and product data. 
- Add support for more advanced filtering and ranking options for recommendations.
- Integrate with a user interface for managing profiles and products.
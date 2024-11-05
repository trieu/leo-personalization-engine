from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from arango import ArangoClient
from arango.database import Database


class ProfileRequest(BaseModel):
    profile_id: str
    page_view_keywords: List[str]
    purchase_keywords: List[str]
    interest_keywords: List[str]
    additional_info: dict
    max_recommendation_size: int = Field(8, description="Default recommendation is 8")
    except_product_ids: List[str] = []
    journey_maps: List[str] = []


class ProductRequest(BaseModel):
    product_id: str
    product_name: str
    product_category: str
    product_keywords: List[str]
    additional_info: dict
    journey_maps: List[str] = []


class Customer360:
    def __init__(self, db: Database):
        self.db = db
        self.customer_collection = "customers"
        self.product_collection = "products"
        self.relationship_collection = "relationships"

        # Ensure collections exist
        if not self.db.has_collection(self.customer_collection):
            self.db.create_collection(self.customer_collection)
        if not self.db.has_collection(self.product_collection):
            self.db.create_collection(self.product_collection)
        if not self.db.has_collection(self.relationship_collection):
            # Specify edge=True only in create_collection
            self.db.create_collection(self.relationship_collection, edge=True)

    def add_profile(self, profile: ProfileRequest):
        """
        Adds a profile to the customers collection.
        """
        profile_data = profile.dict()
        profile_data["_key"] = profile.profile_id

        if not self.db[self.customer_collection].has(profile.profile_id):
            self.db[self.customer_collection].insert(profile_data)
        else:
            self.db[self.customer_collection].update(profile_data)

    def add_product(self, product: ProductRequest):
        """
        Adds a product to the products collection.
        """
        product_data = product.dict()
        product_data["_key"] = product.product_id

        if not self.db[self.product_collection].has(product.product_id):
            self.db[self.product_collection].insert(product_data)
        else:
            self.db[self.product_collection].update(product_data)

    def link_profile_to_product(self, profile_id: str, product_id: str, relationship_type: str):
        """
        Creates a relationship between a profile and a product.
        """
        edge_data = {
            "_from": f"{self.customer_collection}/{profile_id}",
            "_to": f"{self.product_collection}/{product_id}",
            "relationship": relationship_type
        }
        
        self.db[self.relationship_collection].insert(edge_data)

    def get_profile_360(self, profile_id: str) -> Optional[Dict]:
        """
        Retrieves a complete 360-degree view of a profile, linking data sources and relationships.
        """
        profile = self.db[self.customer_collection].get(profile_id)
        if not profile:
            return None
        
        # Find connected products with relationships
        query = f"""
        FOR edge IN {self.relationship_collection}
            FILTER edge._from == @profile_id
            FOR product IN {self.product_collection}
                FILTER product._id == edge._to
                RETURN {{
                    product: product,
                    relationship: edge.relationship
                }}
        """
        cursor = self.db.aql.execute(query, bind_vars={"profile_id": f"{self.customer_collection}/{profile_id}"})
        linked_products = [entry for entry in cursor]
        
        profile["linked_products"] = linked_products
        return profile

    def query_relationship(self, profile_id: str, relationship_type: str) -> List[Dict]:
        """
        Queries specific relationships for a profile.
        """
        query = f"""
        FOR edge IN {self.relationship_collection}
            FILTER edge._from == @profile_id AND edge.relationship == @relationship_type
            FOR product IN {self.product_collection}
                FILTER product._id == edge._to
                RETURN product
        """
        cursor = self.db.aql.execute(query, bind_vars={
            "profile_id": f"{self.customer_collection}/{profile_id}",
            "relationship_type": relationship_type
        })
        
        return [product for product in cursor]


# Example Usage

# Initialize ArangoDB connection
client = ArangoClient()
db = client.db("test_db", username="root", password="123456")

# Initialize Customer360 instance
customer360 = Customer360(db=db)

# Add a profile and a product
profile = ProfileRequest(
    profile_id="P123",
    page_view_keywords=["electronics", "smartphones"],
    purchase_keywords=["iPhone", "Samsung"],
    interest_keywords=["technology", "gadgets"],
    additional_info={"age": 30, "location": "NYC"},
    except_product_ids=["X123", "Y456"],
    journey_maps=["map1", "map2"]
)
customer360.add_profile(profile)

product = ProductRequest(
    product_id="PR001",
    product_name="iPhone 13",
    product_category="Smartphones",
    product_keywords=["Apple", "iPhone", "Mobile"],
    additional_info={"color": "black", "storage": "128GB"},
    journey_maps=["map1"]
)
customer360.add_product(product)

# Link profile to product
customer360.link_profile_to_product("P123", "PR001", "purchased")

# Retrieve profile 360 view
profile_360_view = customer360.get_profile_360("P123")
print(profile_360_view)

# Query specific relationship
purchase_data = customer360.query_relationship("P123", "purchased")
print(purchase_data)

from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel, Field

from personalization import add_profile_to_qdrant, add_product_to_qdrant, recommend_products_for_profile


# FastAPI initialization
api_personalization = FastAPI()

# default
@api_personalization.get("/")
async def index():
    return {"message": "API of CDP Recommendation"}


# Pydantic models for request data
class ProfileRequest(BaseModel):
    profile_id: str
    page_view_keywords: List[str]
    purchase_keywords: List[str]
    interest_keywords: List[str]
    additional_info: dict
    max_recommendation_size: int = Field(8, description="Default recommendation is 8")
    except_product_ids: List[str] = []


class ProductRequest(BaseModel):
    product_id: str
    product_name: str
    product_category: str
    product_keywords: List[str]
    additional_info: dict


# Endpoint to add profile
@api_personalization.post("/add-profile/")
async def add_profile(profile: ProfileRequest):
    try:
        add_profile_to_qdrant(
            profile.profile_id,
            profile.page_view_keywords,
            profile.purchase_keywords,
            profile.interest_keywords,
            profile.additional_info
        )
        return {"status": "Profile added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to check profile and get recommendation in real-time
@api_personalization.post("/check-profile-for-recommendation/")
async def add_profile(profile: ProfileRequest):
    try:
        profile_id = add_profile_to_qdrant(
            profile.profile_id,
            profile.page_view_keywords,
            profile.purchase_keywords,
            profile.interest_keywords,
            profile.additional_info
        )        
        top_n = profile.max_recommendation_size
        except_product_ids = profile.except_product_ids
        rs = recommend_products_for_profile(profile_id, top_n, except_product_ids)
        if not rs:
            raise HTTPException(
                status_code=404, detail="Profile not found or no recommendations available")
        return rs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to add multiple profiles
@api_personalization.post("/add-profiles/")
async def add_profiles(profiles: List[ProfileRequest]):
    try:
        for profile in profiles:
            add_profile_to_qdrant(
                profile.profile_id,
                profile.page_view_keywords,
                profile.purchase_keywords,
                profile.interest_keywords,
                profile.additional_info
            )
        return {"status": "All profiles added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to add product
@api_personalization.post("/add-product/")
async def add_product(product: ProductRequest):
    try:
        add_product_to_qdrant(
            product.product_id,
            product.product_name,
            product.product_category,
            product.product_keywords,
            product.additional_info
        )
        return {"status": "Product added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to add multiple products
@api_personalization.post("/add-products/")
async def add_products(products: List[ProductRequest]):
    try:
        for product in products:
            add_product_to_qdrant(
                product.product_id,
                product.product_name,
                product.product_category,
                product.product_keywords,
                product.additional_info
            )
        return {"status": "All products added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to recommend products based on profile
@api_personalization.get("/recommend/{profile_id}")
async def recommend(profile_id: str, top_n: int = 8, except_product_ids: str = ""):
    try:
        rs = recommend_products_for_profile(profile_id, top_n, except_product_ids.split(","))
        if not rs:
            raise HTTPException(
                status_code=404, detail="Profile not found or no recommendations available")
        return rs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


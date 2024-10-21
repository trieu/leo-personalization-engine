from typing import List
from pydantic import BaseModel, Field

# Pydantic models for request data
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
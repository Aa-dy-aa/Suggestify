from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
from content_based import ContentBasedFiltering

# Initialize FastAPI app
app = FastAPI(
    title="Product Recommendation API",
    version="1.0.0",
    description="API for generating product recommendations using content-based filtering"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy recommender initialization to avoid heavy work at import time
recommender = None

def get_recommender():
    global recommender
    if recommender is None:
        try:
            recommender = ContentBasedFiltering()
        except Exception as e:
            print(f"Error initializing recommender: {str(e)}")
            raise
    return recommender

# Data Models
class Product(BaseModel):
    asin: str
    title: str
    description: Optional[str]
    price: Optional[float]
    category_id: Optional[int]
    stars: Optional[float]
    num_reviews: Optional[int]
    category_name: Optional[str]
    explanation: Optional[str]
    similarity_score: Optional[float]
    
class RecommendationResponse(BaseModel):
    recommendations: List[Product]
    count: int
    query_type: str
    query_value: str

@app.get("/", tags=["Health"])
def read_root():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": "Welcome to the Amazon Product Recommendation System API",
        "version": "1.0.0"
    }
    raise

# Pydantic models for request/response validation
class RecommendationRequest(BaseModel):
    asin: Optional[str] = Field(None, description="Amazon Standard Identification Number")
    title: Optional[str] = Field(None, description="Product title or partial title")
    top_n: Optional[int] = Field(5, ge=1, le=20, description="Number of recommendations to return")

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    count: int
    query_type: str
    query_value: str

# Error handler for common exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )

@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to the Product Recommendation API!",
        "version": "1.0.0",
        "endpoints": {
            "/recommendations/by_asin/{asin}": "Get recommendations by product ASIN",
            "/recommendations/by_title": "Get recommendations by product title",
            "/recommendations/by_category/{asin}": "Get category-specific recommendations"
        }
    }

@app.get(
    "/recommendations/by_asin/{asin}",
    response_model=RecommendationResponse,
    tags=["Recommendations"]
)
async def get_recommendations_by_asin(
    asin: str = Path(..., description="Product ASIN to get recommendations for"),
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    """
    Get product recommendations based on ASIN (Amazon Standard Identification Number)
    """
    try:
        r = get_recommender()
        recommendations = r.get_recommendations(asin, top_n)
        if recommendations is None or recommendations.empty:
            raise HTTPException(status_code=404, detail=f"No recommendations found for ASIN: {asin}")
        
        return {
            "recommendations": recommendations.to_dict(orient='records'),
            "count": len(recommendations),
            "query_type": "asin",
            "query_value": asin
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/recommendations/by_title",
    response_model=RecommendationResponse,
    tags=["Recommendations"]
)
async def get_recommendations_by_title(
    title: str = Query(..., description="Product title or partial title"),
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    """
    Get product recommendations based on product title
    """
    try:
        r = get_recommender()
        recommendations = r.get_recommendations_by_title(title, top_n)
        if recommendations is None or recommendations.empty:
            raise HTTPException(status_code=404, detail=f"No products found matching title: {title}")
        
        return {
            "recommendations": recommendations.to_dict(orient='records'),
            "count": len(recommendations),
            "query_type": "title",
            "query_value": title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/recommendations/by_category/{asin}",
    response_model=RecommendationResponse,
    tags=["Recommendations"]
)
async def get_recommendations_by_category(
    asin: str = Path(..., description="Product ASIN to get category recommendations for"),
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    """
    Get product recommendations from the same category as the specified product
    """
    try:
        r = get_recommender()
        recommendations = r.get_similar_in_category(asin, top_n)
        if recommendations is None or recommendations.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No category recommendations found for ASIN: {asin}"
            )
        
        return {
            "recommendations": recommendations.to_dict(orient='records'),
            "count": len(recommendations),
            "query_type": "category",
            "query_value": asin
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/titles", tags=["Products"])
async def get_product_titles(limit: int = Query(100, ge=1, le=1000, description="Maximum number of titles to return")):
    """
    Return a list of product titles for client-side fuzzy search.
    """
    try:
        # Safely get titles from the recommender's data
        r = get_recommender()
        if not hasattr(r, 'data'):
            raise HTTPException(status_code=500, detail="Recommender data not available")
        titles = r.data['title'].dropna().astype(str).head(limit).tolist()
        return {"titles": titles, "count": len(titles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))








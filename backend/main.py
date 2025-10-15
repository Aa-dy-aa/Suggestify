from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from content_based import ContentBasedFiltering
from typing import List, Optional, Dict, Any

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

# Lazy recommender initialization
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

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )

# Helper to add imgUrl to each recommendation
def add_img_url(recommendations_df: pd.DataFrame) -> List[Dict[str, Any]]:
    recs = []
    for rec in recommendations_df.to_dict(orient="records"):
        rec["imgUrl"] = rec.get("imgUrl") or "https://via.placeholder.com/300x200?text=No+Image"
        recs.append(rec)
    return recs

# ---------------------------------------------------
# RECOMMENDATION ENDPOINTS
# ---------------------------------------------------

@app.get("/recommendations/by_asin/{asin}", tags=["Recommendations"])
async def get_recommendations_by_asin(
    asin: str = Path(..., description="Product ASIN to get recommendations for"),
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    try:
        r = get_recommender()
        recommendations = r.get_recommendations(asin, top_n)
        if recommendations is None or recommendations.empty:
            raise HTTPException(status_code=404, detail=f"No recommendations found for ASIN: {asin}")
        return {
            "recommendations": add_img_url(recommendations),
            "count": len(recommendations),
            "query_type": "asin",
            "query_value": asin
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/by_title", tags=["Recommendations"])
async def get_recommendations_by_title(
    title: str = Query(..., description="Product title or partial title"),
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    try:
        r = get_recommender()
        recommendations = r.get_recommendations_by_title(title, top_n)
        if recommendations is None or recommendations.empty:
            raise HTTPException(status_code=404, detail=f"No products found matching title: {title}")
        return {
            "recommendations": add_img_url(recommendations),
            "count": len(recommendations),
            "query_type": "title",
            "query_value": title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/by_category/{asin}", tags=["Recommendations"])
async def get_recommendations_by_category(
    asin: str = Path(..., description="Product ASIN to get category recommendations for"),
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return")
):
    try:
        r = get_recommender()
        recommendations = r.get_similar_in_category(asin, top_n)
        if recommendations is None or recommendations.empty:
            raise HTTPException(status_code=404, detail=f"No category recommendations found for ASIN: {asin}")
        return {
            "recommendations": add_img_url(recommendations),
            "count": len(recommendations),
            "query_type": "category",
            "query_value": asin
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to fetch product titles for fuzzy search
@app.get("/api/products/titles", tags=["Products"])
async def get_product_titles(limit: int = Query(100, ge=1, le=1000, description="Maximum number of titles to return")):
    try:
        r = get_recommender()
        if not hasattr(r, "data"):
            raise HTTPException(status_code=500, detail="Recommender data not available")
        titles = r.data['title'].dropna().astype(str).head(limit).tolist()
        return {"titles": titles, "count": len(titles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

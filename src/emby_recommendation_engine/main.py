from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Emby Recommendation Engine",
    description="A recommendation engine for Emby media server",
    version="1.0.0"
)

# Pydantic models for request/response
class Item(BaseModel):
    id: int
    title: str
    genre: Optional[str] = None
    rating: Optional[float] = None

class RecommendationRequest(BaseModel):
    user_id: int
    limit: int = 10

class RecommendationResponse(BaseModel):
    recommendations: List[Item]
    user_id: int

# In-memory storage for demo
items = [
    Item(id=1, title="The Matrix", genre="Sci-Fi", rating=8.7),
    Item(id=2, title="Inception", genre="Sci-Fi", rating=8.8),
    Item(id=3, title="The Godfather", genre="Crime", rating=9.2),
]

@app.get("/")
async def root():
    return {"message": "Welcome to Emby Recommendation Engine"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/items", response_model=List[Item])
async def get_items():
    return items

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    return {"error": "Item not found"}

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    # Simple recommendation logic - return top rated items
    sorted_items = sorted(items, key=lambda x: x.rating or 0, reverse=True)
    recommendations = sorted_items[:request.limit]
    
    return RecommendationResponse(
        recommendations=recommendations,
        user_id=request.user_id
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

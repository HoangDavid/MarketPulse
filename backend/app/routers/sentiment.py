from fastapi import APIRouter
import main

router = APIRouter()

@router.post("/analyze-sentiment")
async def analyze_sentiment(data:dict):
    texts = data.get("texts", [])
    batch_size = data.get("batch_size", 4)
    if not texts:
        return {"error": "No texts provided"}
    
    sentiment_pipeline = main.models["sentiment_pipeline"]
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        results.extend(sentiment_pipeline(batch))
    
    return {"sentiment_results": results}
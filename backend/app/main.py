from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import reddit, yahoo, sentiment
# Dict to hold preloaded pretrained models
models = {}

# Preload model upon app initialization
@asynccontextmanager
async def lifespan(app:FastAPI):
    from transformers import pipeline
    models["sentiment_pipeline"] = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
    yield
    models.clear()



app = FastAPI(lifespan=lifespan)
# Include Reddit router
app.include_router(reddit.router, prefix="/api", tags=["Reddit"])

# Include Yahoo router
app.include_router(yahoo.router, prefix="/api", tags=["Yahoo"])

# Include Sentiment Model router
app.include_router(sentiment.router, prefix="/api", tags=["Sentiment"])

@app.get("/")
async def root():
    return {"message": "Welcome to the MarketPulse!"}



# Note to self:
#   To run the app for FASTAPI: uvicorn main:app --reload
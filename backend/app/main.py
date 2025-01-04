from fastapi import FastAPI
from routers import yahoo, market_sentiment, social_sentiment
from services.resource_init import lifespan


app = FastAPI(lifespan=lifespan)
# Include Reddit router
app.include_router(social_sentiment.router, prefix="/api", tags=["social-sentiment"])

# Include Yahoo router
app.include_router(yahoo.router, prefix="/api", tags=["Yahoo"])

# Include Market sentiment indicator router
app.include_router(market_sentiment.router, prefix="/api", tags="Market Sentiment")

@app.get("/")
async def root():
    return {"message": "Welcome to the MarketPulse!"}



# Note to self:
#   To run the app for FASTAPI: uvicorn main:app --reload
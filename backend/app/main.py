from fastapi import FastAPI
from routers import market_sentiment, social_sentiment, stock_price
from services.resource_init import lifespan


app = FastAPI(lifespan=lifespan)
# Include Reddit router
app.include_router(social_sentiment.router, prefix="/api", tags=["social-sentiment"])

# Include Yahoo router
app.include_router(stock_price.router, prefix="/api", tags=["stock-price"])

# Include Market sentiment indicator router
app.include_router(market_sentiment.router, prefix="/api", tags=["market-sentiment"])

@app.get("/")
async def root():
    return {"message": "Welcome to the MarketPulse!"}



# Note to self:
#   To run the app for FASTAPI: uvicorn main:app --reload
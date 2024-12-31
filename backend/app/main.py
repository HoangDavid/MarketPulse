from fastapi import FastAPI
from routers import reddit, yahoo

app = FastAPI()

# Include Reddit router
app.include_router(reddit.router, prefix="/api", tags=["Reddit"])

# Include Yahoo router
app.include_router(yahoo.router, prefix="/api", tags=["Yahoo"])


@app.get("/")
async def root():
    return {"message": "Welcome to the MarketPulse!"}



# Note to self:
#   To run the app for FASTAPI: uvicorn main:app --reload
from fastapi import FastAPI
from routers import reddit

app = FastAPI()

# Include Reddit router
app.include_router(reddit.router, prefix="/api", tags=["Reddit"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Reddit API Service!"}



# Note to self:
#   To run the app for FASTAPI: uvicorn main:app --reload
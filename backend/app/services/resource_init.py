from transformers import pipeline
from fastapi import FastAPI
from contextlib import asynccontextmanager
# Dict to hold preloaded pretrained models
MODELS = {}

# Preload model upon app initialization
@asynccontextmanager
async def lifespan(app:FastAPI):
    MODELS["social_sentiment"] = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
    MODELS["finance_sentiment"] = pipeline("text-classification", model="ProsusAI/finbert")
    yield
    MODELS.clear()


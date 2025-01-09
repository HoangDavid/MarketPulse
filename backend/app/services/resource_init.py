from fastapi import FastAPI
from torch.nn.functional import softmax
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer
from contextlib import asynccontextmanager
from pathlib import Path
# Dict to hold preloaded pretrained models
MODELS = {}

# TODO: convert model ONX runtime for faster inference
# Preload model upon app initialization
@asynccontextmanager
async def lifespan(app:FastAPI):
    # MODELS["social_sentiment"] = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
    
    PROJECT_DIR = Path(__file__).parent.parent
    model_path = PROJECT_DIR / 'onnx_model'

    model = ORTModelForSequenceClassification.from_pretrained(
                model_path, file_name="model_quantized.onnx", repo_type="model")
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    MODELS["social_sentiment"] = {
        "model": model,
        "tokenizer": tokenizer,
        "predict": lambda text: predict_sentiment(model, tokenizer, text),
    }

    yield
    MODELS.clear()



# Helper function for inference
def predict_sentiment(model, tokenizer, text: str):
    # Tokenize input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    # Perform inference
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = softmax(logits, dim=1)

    return probabilities[0]


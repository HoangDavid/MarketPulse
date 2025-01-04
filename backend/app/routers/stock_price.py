from fastapi import APIRouter, HTTPException
# from services.yahoo import fetch_stock_data, fetch_live_stock_data

router = APIRouter()

@router.get("/yahoo/{ticker}/historical")
async def get_stock_data(ticker:str, start_date:str, end_date:str, interval: str = "1h"):
    return None
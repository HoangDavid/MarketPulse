from fastapi import APIRouter, HTTPException
from services.yahoo import fetch_stock_data, fetch_live_stock_data

router = APIRouter()

@router.get("/yahoo/{ticker}/historical")
async def get_stock_data(ticker:str, start_date:str, end_date:str, interval: str = "1h"):
    """
    API endpoint to fetch historical stock data.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        interval (str): Time interval (default: "1h").

    Returns:
        JSON: Historical stock data.
    """
    data = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval)
    if data is None:
        return HTTPException(status_code=500, detail="Error fetching historical stock data.")
    else:
        return data
    
@router.get("/yahoo/{ticker}/live")
async def get_live_stock_data(ticker:str):
    """
    API endpoint to fetch the latest stock price.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").

    Returns:
        JSON: Latest stock price information.
    """
    data = fetch_live_stock_data(ticker=ticker)
    if data is None:
        return HTTPException(status_code=500, detail="Error fetching historical stock data.")
    else:
        return data
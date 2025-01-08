import pandas as pd
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from services.yahoo import fetch_stock_data

router = APIRouter()

@router.get("/stock-price/{ticker}")
async def get_stock_data(ticker: str, time_filter: str = "year", interval: str = "1d"):
    try:
        now = datetime.now()

        cutoff_date = None
        if time_filter == "year":
            start_year = (now - timedelta(days=365)).year
            cutoff_date = datetime(start_year, 1, 1)
        elif time_filter == "month":
            d = (now - timedelta(days=30))
            cutoff_date = datetime(d.year, d.month, 1)

        # To calculate daily stock returns
        start_date = cutoff_date - timedelta(days=5)
        
        data = await fetch_stock_data(ticker=ticker, start_date=start_date.strftime('%Y-%m-%d'),
                                        end_date=now.strftime('%Y-%m-%d'), 
                                        interval=interval)
        

        data["timestamp"] = data["Date"]
        data["price"] = data[f"Close_{ticker}"]
        data["return"] = data["price"].pct_change()
        data = data[pd.to_datetime(data["timestamp"]) >= cutoff_date]
        
        data = data[["timestamp", "price", "return"]].to_dict(orient="records")
        

        return {f"{ticker}": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
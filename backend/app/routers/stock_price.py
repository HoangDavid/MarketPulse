import pandas as pd
from util.util import convert_time_filter
from datetime import timedelta
from fastapi import APIRouter, HTTPException
from services.yahoo import fetch_stock_data

router = APIRouter()

@router.get("/stock-price/{ticker}")
async def get_stock_data(ticker: str, time_filter: str = "year", interval: str = "1d"):
    try:
        
        start_date, end_date, interval = convert_time_filter(time_filter=time_filter)
        print(end_date)

        # To calculate daily stock returns
        cutoff_date = start_date - timedelta(days=5)
        
        data = await fetch_stock_data(ticker=ticker, start_date=cutoff_date.strftime('%Y-%m-%d'),
                                        end_date=end_date.strftime('%Y-%m-%d'), 
                                        interval=interval)
        

        data["timestamp"] = data["Date"]
        data["price"] = data[f"Close_{ticker}"]
        data["return"] = data["price"].pct_change()
        data = data[pd.to_datetime(data["timestamp"]) >= start_date]
        
        data = data[["timestamp", "price", "return"]].to_dict(orient="records")
        

        return {f"{ticker}": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
import pandas as pd
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from services.yahoo import fetch_stock_data


router = APIRouter()

# CBOE Votatility Index (VIX)
@router.get("/market-sentiment/vix")
async def get_vix(moving_avg: int = 50, interval: str = "1d"):
    # Moving average unit is in days
    try: 
        # Make sure the cutoff isat least a year from now
        now = datetime.now()
        start_year = (now - timedelta(days=365)).year
        cutoff_date = datetime(start_year, 1, 1)

        # Make sure to have enough data to caculate vix
        start_date = cutoff_date - timedelta(days=80)

        vix_data = await fetch_stock_data("^VIX", start_date=start_date.strftime('%Y-%m-%d'),
                                           end_date=now.strftime('%Y-%m-%d'), 
                                           interval=interval)
        
        # Calculate moving avg of vix
        vix_data[f"MA_{moving_avg}"] = vix_data["Close_^VIX"].rolling(window=moving_avg).mean()
        vix_data = vix_data[pd.to_datetime(vix_data["Date"]) >= cutoff_date]
        vix_data["timestamp"] = vix_data["Date"]
        vix_data = vix_data[["timestamp", f"MA_{moving_avg}"]].to_dict('records')
     
        return {"VIX": vix_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

# Calculate the NYSE highs and lows
@router.get("/market-sentiment/highs_lows")
async def get_highs_lows(window_size: int = 52, interval: str = "1d"):
    # Moving average unit is in weeks
    try:  
        # Make sure the cutoff isat least a year from now
        now = datetime.now()
        start_year = (now - timedelta(days=365)).year
        cutoff_date = datetime(start_year, 1, 1)

        # Make sure to have enough data to caculate NYSE highs lows
        start_date = cutoff_date - timedelta(days=730)

        nyse_data = await fetch_stock_data("^NYA", start_date=start_date.strftime('%Y-%m-%d'),
                                           end_date=now.strftime('%Y-%m-%d'), 
                                           interval=interval)

        nyse_data[f"{window_size}_weeks_high"] = nyse_data["High_^NYA"].rolling(window=window_size * 7).max()
        nyse_data[f"{window_size}_weeks_low"] = nyse_data["Low_^NYA"].rolling(window=window_size * 7).min()
        nyse_data = nyse_data[pd.to_datetime(nyse_data["Date"]) >= cutoff_date]

        nyse_data["timestamp"] = nyse_data["Date"]
        nyse_data = nyse_data[["timestamp", f"{window_size}_weeks_high", f"{window_size}_weeks_low"]].to_dict('records')
        
        return {"NYSE High and Lows": nyse_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# TODO: Calculate put/call options ratios
@router.get("/market-sentiment/put_call_ratios")
async def get_putcall_ratio(time_filter: str = "year", moving_avg: int = 5, interval: str = "1d"):
    try:  
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# TODO: Calculate S&P500 market momentum
@router.get("/market-sentiment/market_momentum")
async def get_market_momentum(time_filter: str = "year", moving_avg: int = 125, interval: str = "1d"):
    try:  
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

  
# TODO: Calculate yield spread: junk bonds vs. investment grade
@router.get("/market-sentiment/yield_spread")
async def get_yield_spread():
    pass


# TODO: Calculate safe haven demand
@router.get("market-sentiment/safe_haven_demand")
async def get_safe_haven_demand():
    pass


# TODO: Calculate stock price breadth: McClellan Volume Summation Index
@router.get("market-sentiment/stock_price_breadth")
async def get_stock_price_breadth():
    pass






'''
TODO:
- vix index with 50 days moving average
- Net new 52-week highs and lows on NYSE
- 5-day average put/call ratio
- Market momentum: S&P 500 and its 125-day moving average
- Yield spread: junk bonds vs. investment grade
- Difference in 20-day stock and bond returns
- McClellan Volume Summation Index
'''


#  Check on multithreading and concurrency
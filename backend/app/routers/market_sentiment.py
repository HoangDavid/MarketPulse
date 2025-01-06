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
        start_date = cutoff_date - timedelta(days=moving_avg * 2)

        vix_data = await fetch_stock_data("^VIX", start_date=start_date.strftime('%Y-%m-%d'),
                                           end_date=now.strftime('%Y-%m-%d'), 
                                           interval=interval)
        
        # Calculate moving avg of vix
        vix_data[f"VIX_{moving_avg}"] = vix_data["Close_^VIX"].rolling(window=moving_avg).mean()
        vix_data = vix_data[pd.to_datetime(vix_data["Date"]) >= cutoff_date]
        vix_data["timestamp"] = vix_data["Date"]
        vix_data["VIX"] = vix_data["Close_^VIX"]
        
        #  Calculate the fear and greed score (/100)
        vix_data["diff"] = vix_data["VIX"] - vix_data[f"VIX_{moving_avg}"]
        diff_mean = vix_data["diff"].mean()
        diff_std = vix_data["diff"].std()
        vix_data["z_score"] = (vix_data["diff"] - diff_mean) / diff_std
        vix_data["fear_greed_score"] = vix_data["z_score"].apply(
            lambda z: 100 - ((max(min(z, 2), -2) + 2) * 25))
    
        vix_data = vix_data[["timestamp", "VIX", f"VIX_{moving_avg}", "fear_greed_score"]].to_dict('records')
     
        return {"VIX": vix_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

# Calculate S&P500 market momentum
@router.get("/market-sentiment/market_momentum")
async def get_market_momentum(time_filter: str = "year", moving_avg: int = 125, interval: str = "1d"):
    try: 
        # Make sure the cutoff is a year from now
        now = datetime.now()
        start_year = (now - timedelta(365)).year
        cutoff_date = datetime(start_year, 1, 1)

        # Make sure there is enough data for moving average
        start_date = cutoff_date - timedelta(moving_avg * 2)

        mm_data = await fetch_stock_data("^GSPC", start_date=start_date.strftime('%Y-%m-%d'),
                                   end_date=now.strftime('%Y-%m-%d'),
                                   interval=interval)
        
        # Calculate moving avg of S&P500 market momentum
        mm_data[f"S&P500_{moving_avg}"] = mm_data["Close_^GSPC"].rolling(window=moving_avg).mean()
        mm_data["timestamp"] = mm_data ["Date"]
        mm_data["S&P500"] = mm_data["Close_^GSPC"]

        # Calculate the fear and greed score (out of 100)
        mm_data["diff"] = mm_data["S&P500"] - mm_data[f"S&P500_{moving_avg}"]
        mm_data["diff_change"] = mm_data["diff"].diff()
        mean_change = mm_data["diff_change"].mean()
        std_change = mm_data["diff_change"].std()
        mm_data["z_score"] = (mm_data["diff_change"] - mean_change) / std_change
        mm_data["fear_greed_score"] = mm_data["z_score"].apply(
            lambda z: 100 - ((max(min(z, 3), -3) + 3) * (100 / 6)))
        mm_data = mm_data [pd.to_datetime(mm_data["Date"]) >= cutoff_date]

        mm_data = mm_data[["timestamp", "S&P500", f"S&P500_{moving_avg}", "fear_greed_score"]].to_dict('records')
     
        return {"market_momentum": mm_data }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# TODO: Calculate safe haven demand
@router.get("market-sentiment/safe_haven_demand")
async def get_safe_haven_demand(difference: int = 20, interval: str = "1d"):
    try:
         # Make sure the cutoff is a year from now
        now = datetime.now()
        start_year = (now - timedelta(365)).year
        cutoff_date = datetime(start_year, 1, 1)

        # Make sure there is enough data for moving average
        start_date = cutoff_date - timedelta(difference * 2)

        # S&P 500 ETF represent stocks
        spy = await fetch_stock_data("SPY", start_date=start_date.strftime('%Y-%m-%d'),
                                     end_date=now.strftime('%Y-%m-%d'),
                                     interval=interval)
        
        #  20+ Year Treasury Bond ETF represent bonds
        tlt = await fetch_stock_data("TLT", start_date=start_date.strftime('%Y-%m-%d'),
                                     end_date=now.strftime('%Y-%m-%d'),
                                     interval=interval)
        
        
        

        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# TODO: Calculate yield spread: junk bonds vs. investment grade
@router.get("/market-sentiment/yield_spread")
async def get_yield_spread():
    pass

# TODO: Calculate stock price breadth: McClellan Volume Summation Index
@router.get("market-sentiment/stock_price_breadth")
async def get_stock_price_breadth():
    pass


#  TODO: Calculate the NYSE highs and lows (maybe: high computational power)
@router.get("/market-sentiment/highs_lows")
async def get_highs_lows(window_size: int = 52, interval: str = "1d"):
    # Moving average unit is in weeks
    try:  
        return None

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")






'''
TODO:
- vix index with 50 days moving average
- Net new 52-week highs and lows on NYSE
- 5-day average put/call ratio -> cannot be done (paywall / no puts and calls ratio that is available for historical )
- Market momentum: S&P 500 and its 125-day moving average
- Yield spread: junk bonds vs. investment grade
- Difference in 20-day stock and bond returns
- McClellan Volume Summation Index
'''

# TODO: check how to each index is fear and greed
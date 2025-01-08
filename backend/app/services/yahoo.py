import yfinance as yf
import pandas as pd
from datetime import timedelta
import os
import asyncio
from fastapi import HTTPException

# Define a semaphore to limit the downloads
semaphore = asyncio.Semaphore(os.cpu_count() * 2)

# Fetch stock data from Yahoo API
async def fetch_stock_data(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    try: 
        async with semaphore:
            data = await asyncio.to_thread(
                yf.download,
                ticker,
                threads=True,
                start=start_date,
                end=end_date,
                interval=interval
                )
        
        if data.empty:
            raise ValueError(f"No data avalaible for {ticker}")
        
        data.reset_index(inplace=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(filter(None, col)).strip() for col in data.columns]

        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime('%Y-%m-%d')
        
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


# CBOE Votatility Index (VIX)
async def fetch_vix(start_date: str, end_date: str, moving_avg: int = 50, interval: str = "1d") -> pd.DataFrame:
    # Moving average unit is in days
    try: 
        # Make sure to have enough data to caculate vix
        cutoff_date = start_date - timedelta(days=moving_avg * 2)

        vix_data = await fetch_stock_data("^VIX", start_date=cutoff_date.strftime('%Y-%m-%d'),
                                           end_date=end_date.strftime('%Y-%m-%d'), 
                                           interval=interval)
        
        # Calculate moving avg of vix
        vix_data[f"VIX_{moving_avg}"] = vix_data["Close_^VIX"].rolling(window=moving_avg).mean()
        vix_data = vix_data[pd.to_datetime(vix_data["Date"]) >= start_date]
        vix_data["timestamp"] = vix_data["Date"]
        vix_data["VIX"] = vix_data["Close_^VIX"]
        
        #  Calculate the fear and greed score (/100)
        vix_data["diff"] = vix_data["VIX"] - vix_data[f"VIX_{moving_avg}"]
        diff_mean = vix_data["diff"].mean()
        diff_std = vix_data["diff"].std()
        vix_data["z_score"] = (vix_data["diff"] - diff_mean) / diff_std
        vix_data["fear_greed_score"] = vix_data["z_score"].apply(
            lambda z: 100 - ((max(min(z, 2), -2) + 2) * 25))
        
        # Select display collumns
        vix_data = vix_data[["timestamp", "VIX", f"VIX_{moving_avg}", "fear_greed_score"]]
     
        return vix_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


# Calculate S&P500 market momentum
async def fetch_market_momentum(start_date: str, end_date: str, moving_avg: int = 125, interval: str = "1d") -> pd.DataFrame:
    try: 
        # Make sure to have enough data to caculate vix
        cutoff_date = start_date - timedelta(days=moving_avg * 2)

        mm_data = await fetch_stock_data("^GSPC", start_date=cutoff_date.strftime('%Y-%m-%d'),
                                   end_date=end_date.strftime('%Y-%m-%d'),
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
        mm_data = mm_data [pd.to_datetime(mm_data["Date"]) >= start_date]

        # Select display collumns
        mm_data = mm_data[["timestamp", "S&P500", f"S&P500_{moving_avg}", "fear_greed_score"]]
     
        return mm_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


# Calculate safe haven demand
async def fetch_safe_haven_demand(start_date: str, end_date: str, difference: int = 20, interval: str = "1d") -> pd.DataFrame:
    try:
       # Make sure to have enough data to caculate vix
        cutoff_date = start_date - timedelta(days=difference * 2)

        # S&P 500 ETF represent stocks
        spy = await fetch_stock_data("SPY", start_date=cutoff_date.strftime('%Y-%m-%d'),
                                     end_date=end_date.strftime('%Y-%m-%d'),
                                     interval=interval)
        
        # 20+ Year Treasury Bond ETF represent bonds
        tlt = await fetch_stock_data("TLT", start_date=cutoff_date.strftime('%Y-%m-%d'),
                                     end_date=end_date.strftime('%Y-%m-%d'),
                                     interval=interval)
        
        # Calculate the percentage change in {difference} trading days
        spy["return_20"] = spy["Close_SPY"].pct_change(difference)
        tlt["return_20"] = tlt["Close_TLT"].pct_change(difference)

        merged = pd.DataFrame({
            "timestamp": spy["Date"],
            "SPY_return_20": spy["return_20"],
            "TLT_return_20": tlt["return_20"]
        }).dropna()

        # Calculate the fear / greed score
        merged["safe_haven"] = merged["SPY_return_20"] - merged["TLT_return_20"]
        merged_mean = merged["safe_haven"].mean()
        merged_std = merged["safe_haven"].std()
        merged["z_score"] = (merged["safe_haven"] - merged_mean) / merged_std
        merged["fear_greed_score"] = merged["z_score"].apply(
            lambda z: 100 - ((max(min(z, 2), -2) + 2) * 25))
        merged = merged[pd.to_datetime(merged["timestamp"]) >= start_date]

        # Select display collumns
        merged = merged[["timestamp", "safe_haven", "fear_greed_score"]]
        
        return merged
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Yield spread: junk bonds vs investment grade
async def fetch_yield_spread(start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
    try:
        # Junk Bond ETF (HYG)
        hyg = await fetch_stock_data("HYG", start_date=start_date.strftime('%Y-%m-%d'),
                                        end_date=end_date.strftime('%Y-%m-%d'),
                                        interval=interval)

        # Investment Grade Bond ETF (LQD)
        lqd = await fetch_stock_data("LQD", start_date=start_date.strftime('%Y-%m-%d'),
                                        end_date=end_date.strftime('%Y-%m-%d'),
                                        interval=interval)
        
        # Calculate the rolling dividend yields (as a proxy for bond yields)
        hyg["yield"] = hyg["Close_HYG"].pct_change(periods=1) + 1
        lqd["yield"] = lqd["Close_LQD"].pct_change(periods=1) + 1  

        # Merge the data on the timestamp
        merged = pd.DataFrame({
            "timestamp": hyg["Date"],
            "HYG_yield": hyg["yield"],
            "LQD_yield": lqd["yield"]
        }).dropna()

        # Calculate the yield spread
        merged["yield_spread"] = merged["HYG_yield"] - merged["LQD_yield"]

        # Calculate the fear/greed score
        merged_mean = merged["yield_spread"].mean()
        merged_std = merged["yield_spread"].std()
        merged["z_score"] = (merged["yield_spread"] - merged_mean) / merged_std
        merged["fear_greed_score"] = merged["z_score"].apply(
            lambda z: 100 - ((max(min(z, 2), -2) + 2) * 25)
        )

        # Select display columns
        merged = merged[["timestamp", "yield_spread", "fear_greed_score"]]
        return merged

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

  
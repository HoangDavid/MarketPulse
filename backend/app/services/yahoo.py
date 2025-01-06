import yfinance as yf
import pandas as pd
import os
import asyncio


# Define a semaphore to limit the downloads
semaphore = asyncio.Semaphore(os.cpu_count() * 2)

# Fetch ticker data from Yahoo API
async def fetch_stock_data(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    
    async with semaphore:
        data = await asyncio.to_thread(
            yf.download,
            ticker, 
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
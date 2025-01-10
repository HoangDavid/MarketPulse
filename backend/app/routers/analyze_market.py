import time
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter
from util.util import convert_time_filter
from routers.stock_price import get_stock_data
from services.reddit import fetch_social_sentiment
from services.yahoo import fetch_vix, fetch_yield_spread, \
    fetch_safe_haven_demand, fetch_market_momentum


router = APIRouter()

@router.get("/analyze-market/{company}")
async def analyze_market(ticker: str, company: str, time_filter: str = "year"):

    # Calculate latency for for total analysis
    start = time.time()

    start_date, end_date, interval = convert_time_filter(time_filter=time_filter)

    # Get stock price
    stock_data = await get_stock_data(ticker=ticker, 
                    time_filter=time_filter,interval=interval)
    stock_data = pd.DataFrame(stock_data[ticker])

    # Get social sentiment
    social_data = await fetch_social_sentiment(subreddit="technology", 
                    query=company, time_filter=time_filter)

    # Get market sentiment indicators
    vix = await fetch_vix(start_date=start_date, 
                    end_date=end_date, interval=interval)
    mm = await fetch_market_momentum(start_date=start_date, 
                    end_date=end_date, interval=interval)
    sh = await fetch_safe_haven_demand(start_date=start_date, 
                    end_date=end_date, interval=interval)
    ys = await fetch_yield_spread(start_date=start_date, 
                    end_date=end_date, interval=interval)
    
    # TODO: detect spike in sentiment
    # TODO: rolling correlations between stock and greed / fear score

    print(social_data)
    '''
    - positive spike sentiment and positive correlation suggests increase stock and greed (momentum) -> mark event + action: Momentum trade
    - negative spike sentiment and positive correlation suggests decrease stock and greed (fight or flight)-> mark event + action: Potential exit
    - else give mixed signal -> actional insights
    '''
    ### Fill the gaps between sentiment using interpolation and forward filling
    
    # Threshold for interpolation (days)
    social_data['timestamp'] = pd.to_datetime(social_data['timestamp'])
    social_data.set_index('timestamp', inplace=True)

    # Plot the data
    # Resample the data to daily frequency  
    social_data_resampled = social_data[['sentiment']].resample('D').mean()
    social_data_resampled['is_original'] = ~social_data_resampled['sentiment'].isna()

# Interpolate missing values
    social_data_resampled['sentiment'] = social_data_resampled['sentiment'].interpolate()

    # Apply a 7-day rolling average
    social_data_resampled['rolling_sentiment'] = social_data_resampled['sentiment'].rolling(window=7, min_periods=1).mean()

    # Plot the rolling average
    plt.figure(figsize=(12, 6))
    plt.plot(
        social_data_resampled.index,
        social_data_resampled['rolling_sentiment'],
        label='7-Day Rolling Average',
        color='orange',
        linestyle='--'
    )

    plt.scatter(
        social_data_resampled[social_data_resampled['is_original']].index,
        social_data_resampled[social_data_resampled['is_original']]['rolling_sentiment'],
        label='Original Data (on Rolling Avg)',
        color='blue',
        zorder=5
    )
    plt.title('Sentiment Data with 7-Day Rolling Average (Based on Calendar Days)')
    plt.xlabel('Timestamp')
    plt.ylabel('Sentiment')
    plt.legend()
    plt.grid(True)
    plt.show()
    latency = time.time() - start

    return {"latency": latency}
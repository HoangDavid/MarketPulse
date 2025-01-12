import time
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter
from routers.stock_price import get_stock_data
from services.reddit import fetch_social_sentiment
from util.util import convert_time_filter, process_sentiment_data\
        ,calculate_fear_greed_score,  calculate_rolling_correlations


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
    stock_start_date = pd.to_datetime(stock_data["timestamp"]).min()

    # Get fear greed score
    fear_greed_score = await calculate_fear_greed_score(start_date=start_date, end_date=end_date, interval=interval)

    #  Calculate the rolling correlations between fear/greed score and stock price
    rolling_correlations = calculate_rolling_correlations(stock_data=stock_data, fear_greed_score=fear_greed_score)

    # Get social sentiment
    social_data = await fetch_social_sentiment(subreddit="technology", 
                    query=company, time_filter=time_filter)
    
    extreme_pos_threshold, extreme_neg_threshold, social_data = process_sentiment_data(start_date=stock_start_date, data=social_data)

    '''
    - positive spike sentiment and positive correlation suggests increase stock and greed (momentum) -> mark event + action: Momentum trade
    - negative spike sentiment and positive correlation suggests decrease stock and greed (fight or flight)-> mark event + action: Potential exit
    - else give mixed signal -> actional insights
    '''

    # Identify momentum trade, potential exit, and mixed signals

    latency = time.time() - start

    return {"latency": latency, "test": rolling_correlations.to_dict("records")}
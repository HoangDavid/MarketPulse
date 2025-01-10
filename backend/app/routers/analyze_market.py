import time
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter
from util.util import convert_time_filter, process_sentiment_data
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
    # stock_data = await get_stock_data(ticker=ticker, 
    #                 time_filter=time_filter,interval=interval)
    # stock_data = pd.DataFrame(stock_data[ticker])

    # Get social sentiment
    social_data = await fetch_social_sentiment(subreddit="technology", 
                    query=company, time_filter=time_filter)
    
    print("Done fetching sentiment data")

    # Get market sentiment indicators
    # vix = await fetch_vix(start_date=start_date, 
    #                 end_date=end_date, interval=interval)
    # mm = await fetch_market_momentum(start_date=start_date, 
    #                 end_date=end_date, interval=interval)
    # sh = await fetch_safe_haven_demand(start_date=start_date, 
    #                 end_date=end_date, interval=interval)
    # ys = await fetch_yield_spread(start_date=start_date, 
    #                 end_date=end_date, interval=interval)
    
    # TODO: detect spike in sentiment
    # TODO: rolling correlations between stock and greed / fear score

    '''
    - positive spike sentiment and positive correlation suggests increase stock and greed (momentum) -> mark event + action: Momentum trade
    - negative spike sentiment and positive correlation suggests decrease stock and greed (fight or flight)-> mark event + action: Potential exit
    - else give mixed signal -> actional insights
    '''
    ### Fill the gaps between sentiment using interpolation and forward filling
    
    
    process_sentiment_data("ADD START DATE STOCK", social_data)

    latency = time.time() - start

    return {"latency": latency}
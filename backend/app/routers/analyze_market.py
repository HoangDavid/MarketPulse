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
    # TODO: Spear correlation with market sentiment and social sentiment
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
    
    # TODO: add time lagged analysis -1, -2 so to not miss sentiment that the day is closed
    print(stock_data)
    print(social_data)
    print(vix)
    print(mm)
    print(sh)
    print(ys)
    

    return {}
from fastapi import APIRouter, HTTPException
from util.util import convert_time_filter, calculate_fear_greed_score
from services.yahoo import fetch_vix, fetch_market_momentum, fetch_safe_haven_demand, fetch_yield_spread



router = APIRouter()
# Fetch market sentiment indicators
@router.get("/market-sentiment/{indicator}")
async def get_market_sentiment(indicator: str, time_filter: str = "year"):
    try:
        start_date, end_date, interval = await convert_time_filter(time_filter)

        data = None
        if indicator == "vix":
            data = await fetch_vix(start_date=start_date, end_date=end_date, interval=interval)
        elif indicator == "market_momentum":
            data = await fetch_market_momentum(start_date=start_date, end_date=end_date, interval=interval)
        elif indicator == "safe_haven":
            data = await fetch_safe_haven_demand(start_date=start_date, end_date=end_date, interval=interval)
        elif indicator == "yield_spread":
            data = await fetch_yield_spread(start_date=start_date, end_date=end_date, interval=interval)
        elif indicator == "fear_greed_score":
            data = await calculate_fear_greed_score(start_date=start_date, end_date=end_date, interval=interval)
        
        data = data.to_dict("records")
        return {f'{indicator}': data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)} from get_market_sentiment")
    

'''
TODO:
- Real time for one day API calling
'''
from fastapi import APIRouter, HTTPException
# import services.yahoo

router = APIRouter()

# TODO: Calculate CBOE Votatility Index (VIX)
@router.get("/market-sentiment/vix")
async def get_vix(time_filter: str = "year", moving_avg: int = 50, interval: str = "1d"):
    try:  
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

# TODO: Calculate the NYSE highs and lows
@router.get("/market-sentiment/highs_lows")
async def get_highs_lows(time_filter: str = "year", moving_avg: int = 52, interval: str = "1d"):
    try:  
        return None
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

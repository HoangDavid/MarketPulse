import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker:str, start_date:str, end_date:str, interval="1hr"):
    """
    Fetch historical stock data from Yahoo Finance.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
        start_date (str): Start date in "YYYY-MM-DD" format.
        end_date (str): End date in "YYYY-MM-DD" format.
        interval (str): Time interval (e.g., "1h", "1d").

    Returns:
        DataFrame: Historical stock data.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        print(data)
        df = pd.DataFrame(data)
        df.columns = ["_".join(col) for col in data.columns]
        converted_data = df.to_dict(orient="records")
        return converted_data
    except:
        # return None if failed to fetch
        return None
    
def fetch_live_stock_data(ticker):
    """
    Fetch the latest stock price for a given ticker.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").

    Returns:
        dict: Latest stock price information.
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d", interval="1m")
        df = pd.DataFrame(data)
        converted_data = df.to_dict(orient="records")
        return converted_data
    except:
        # return None if failed to fetch
        return None
    

# Fetch CBOE Volatility Index (VIX) from Yahoo Finance
def fetch_vix_data():
    vix_intraday = yf.download('^VIX', interval='1h', period='1d')  # Last 5 days with 1-hour interval
    
    # BUG: parsing error when changing interval from 1h to 1d
    if vix_intraday.empty:
        raise ValueError("No intraday VIX data available")
    
    vix_intraday.reset_index(inplace=True)
    vix_intraday["Datetime"] = vix_intraday["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return [{"Datetime": row["Datetime"], "Close": row["Close"]} for _, row in vix_intraday.iterrows()]


# TODO: convert all time to EST time 
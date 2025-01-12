import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from services.yahoo import fetch_vix, fetch_yield_spread, \
    fetch_safe_haven_demand, fetch_market_momentum



### Calculate rolling correlations between fear / greed score and stock price
def calculate_rolling_correlations(stock_data:pd.DataFrame, fear_greed_score: pd.DataFrame, window_size: int = 7) -> pd.DataFrame:

    stock_data.set_index('timestamp', inplace=True)
    fear_greed_score.set_index('timestamp', inplace=True)

    data = pd.concat([stock_data, fear_greed_score], axis=1)

    data = data.dropna()

    data["correlation"] = data["price"].rolling(window=window_size).corr(data["fear_greed_score"])

    data.reset_index(inplace=True)
    data = data.fillna(0)

    return data


### Calculate fear / greed score from market indicator
async def calculate_fear_greed_score(start_date: str, end_date: str, interval: str) -> pd.DataFrame:

    # Fetch the market sentiment indicators
    vix = await fetch_vix(start_date=start_date, 
                    end_date=end_date, interval=interval)
    mm = await fetch_market_momentum(start_date=start_date, 
                    end_date=end_date, interval=interval)
    sh = await fetch_safe_haven_demand(start_date=start_date, 
                    end_date=end_date, interval=interval)
    ys = await fetch_yield_spread(start_date=start_date, 
                    end_date=end_date, interval=interval)

    data = pd.concat([vix[['timestamp', 'fear_greed_score']], 
                     mm[['timestamp', 'fear_greed_score']], 
                     sh[['timestamp', 'fear_greed_score']], 
                     ys[['timestamp', 'fear_greed_score']]])
    
    data = (
        data.groupby('timestamp', as_index=False)
        .filter(lambda x: len(x) == 4)
        .groupby('timestamp', as_index=False)['fear_greed_score']
        .mean()
        )
    
    return data

### Fill missing data, moving average, and detect spikes
def process_sentiment_data(start_date: datetime, data: pd.DataFrame, threshold: int = 5, 
                           rolling_avg: int = 7, pos_std_multiplier: int = 1.5, neg_std_multiplier: int = 2):
    '''
        threshold: 5 -> interpolation within 5 trading days else backward / forward fill
        rolling_avg: 7 -> smoother trend of sentiment
        pos_std_multiplier: 1.5 -> the larger the greater the extreme sentiment threshold
        neg_std_multiplier: 2 -> the larger the greater the extreme sentiment threshold
    '''
    # TODO: fill missing data from start_date
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    date_range = pd.date_range(start=start_date, end=data['timestamp'].max())

    # Reindex to add all dates
    merged = pd.DataFrame({'timestamp': date_range})
    merged = merged.merge(data, on='timestamp', how='left')

    # Calculate the gaps of missing data
    merged['sentiment_filled'] = merged['sentiment'].copy()
    gap_sizes = merged['timestamp'].diff().dt.days
    large_gaps = gap_sizes > threshold
    small_gaps = ~large_gaps

    # Interpolation for small gaps of missing data
    merged.loc[small_gaps, "sentiment_filled"] = merged.loc[small_gaps, "sentiment_filled"].interpolate(method="linear")

    # Backward / Forward fill for larger gaps of missing data
    merged.loc[large_gaps, "sentiment_filled"] = merged["sentiment_filled"].ffill().bfill()
    merged["sentiment_filled"] = merged["sentiment_filled"].bfill()

    # Rolling average for smoother trends of sentiment
    merged["is_filled"] = merged['sentiment'].isna()
    merged["rolling_avg"] = merged["sentiment_filled"].rolling(window=rolling_avg, min_periods=1).mean()

    # Threshold for extreme spikes
    positive_spike_threshold = merged["rolling_avg"].mean() + merged["rolling_avg"].std() * pos_std_multiplier
    negative_spike_threshold = merged["rolling_avg"].mean() - merged["rolling_avg"].std() * neg_std_multiplier

    # Detect extreme
    merged["positive_spike"] = (merged["rolling_avg"] > positive_spike_threshold) & (~merged['is_filled'])
    merged["negative_spike"] = (merged["rolling_avg"] < negative_spike_threshold) & (~merged['is_filled'])

    # Fill nan values with empty string
    merged = merged.fillna("")

    ### PLOT FOR DEGBUGGING
    # plt.figure(figsize=(12, 6))
    # plt.plot(merged['timestamp'], merged['rolling_avg'], label='Rolling Average', color='blue', linestyle='--')
    # positive_spikes = merged[merged['positive_spike']]
    # plt.scatter(positive_spikes['timestamp'], positive_spikes['rolling_avg'], color='green', label='Extreme Positive Spikes (Original)', zorder=5)
    # negative_spikes = merged[merged['negative_spike']]
    # plt.scatter(negative_spikes['timestamp'], negative_spikes['rolling_avg'], color='red', label='Extreme Negative Spikes (Original)', zorder=5)
    # plt.axhline(positive_spike_threshold, color='green', linestyle='--', label='Positive Spike Threshold')
    # plt.axhline(negative_spike_threshold, color='red', linestyle='--', label='Negative Spike Threshold')
    # plt.xlabel('Timestamp')
    # plt.ylabel('Rolling Average Sentiment')
    # plt.title('Rolling Average with Extreme Positive and Negative Spikes (Original Points Only)')
    # plt.legend()
    # plt.grid()
    # plt.show()

    # Select columns
    merged["sentiment"] = merged["rolling_avg"]
    merged["timestamp"] = merged["timestamp"].dt.strftime('%Y-%m-%d')
    merged = merged[['timestamp', 'sentiment', 'positive_spike', 'negative_spike', 'article url', 'title', 'top comment']]

    return positive_spike_threshold, negative_spike_threshold, merged


### Convert time filter to start and end dates
def convert_time_filter(time_filter: str):
    start_date = None
    end_date = datetime.now()
    interval = "1d"
    
    if time_filter == "year":
        start_year = (end_date - timedelta(days=365)).year
        start_date = datetime(start_year, 1, 1)   
    elif time_filter == "month":
        d = (end_date - timedelta(days=30))
        start_date = datetime(d.year, d.month, 1)
    elif time_filter == "week":
        start_date = end_date - timedelta(days=7)
    elif time_filter == "day":
        #  TODO: add for live streaming
        interval = "1h"

    return  start_date, end_date, interval

    


import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException
from routers.stock_price import get_stock_data
from services.reddit import fetch_social_sentiment
from util.util import convert_time_filter, process_sentiment_data\
        ,calculate_fear_greed_score,  calculate_rolling_correlations


router = APIRouter()

@router.get("/analyze-market/{company}")
async def analyze_market(ticker: str, company: str, time_filter: str = "year"):
    try:

        # Calculate latency for for total analysis
        start = time.time()

        start_date, end_date, interval = convert_time_filter(time_filter=time_filter)

        # Get stock price
        stock_data = await get_stock_data(ticker=ticker, 
                        time_filter=time_filter,interval=interval)
        stock_data = pd.DataFrame(stock_data[ticker])

        # Get fear greed score
        fear_greed_score = await calculate_fear_greed_score(start_date=start_date, end_date=end_date, interval=interval)

        #  Calculate the rolling correlations between fear/greed score and stock price
        rolling_correlations = await calculate_rolling_correlations(stock_data=stock_data, fear_greed_score=fear_greed_score)
        start_sentiment_date = pd.to_datetime(rolling_correlations['timestamp']).min()

        # Get social sentiment
        social_data = await fetch_social_sentiment(subreddit="technology", 
                        query=company, time_filter=time_filter)
        
        extreme_pos_threshold, extreme_neg_threshold, social_data = await process_sentiment_data(start_date=start_sentiment_date, data=social_data)

        '''
        - positive spike sentiment and positive correlation suggests increase stock and greed (momentum) -> mark event + action: Momentum trade
        - negative spike sentiment and positive correlation suggests decrease stock and greed (fight or flight)-> mark event + action: Potential exit
        - else give mixed signal -> actional insights
        '''

        # Merge based on stock price timestamps
        merged = pd.merge(
            rolling_correlations,
            social_data,
            on='timestamp',
            how='left'
        )

        # Identify signals
        conditions = [
            (merged["positive_spike"] & (merged['correlation'] > 0.3)),
            (merged["negative_spike"] & (merged['correlation'] > 0.3)),
            ((merged['positive_spike'] | merged['negative_spike']) & (merged['correlation'] <= 0))
        ]
        options = ['Momentum trade', 'Potential exit', 'Mixed signal']

        merged['action'] = np.select(
            conditions,
            options,
            default='no signal'
        )

        # # PLOT FOR DEBUGGING
        # signals_data = merged[merged['action'] != 'no signal']
        # fig, ax1 = plt.subplots(figsize=(14, 7))
        # ax1.plot(
        #     merged['timestamp'],
        #     merged['price'],
        #     label='Stock Price (Trading Days)',
        #     color='red',
        #     linestyle='-'
        # )
        # ax1.set_ylabel('Stock Price', color='red')
        # ax1.tick_params(axis='y', labelcolor='red')
        # ax2 = ax1.twinx()
        # ax2.plot(
        #     merged['timestamp'],
        #     merged['sentiment'],
        #     label='Sentiment (All Days)',
        #     color='blue',
        #     linestyle='--'
        # )
        # ax2.set_ylabel('Sentiment', color='blue')
        # ax2.tick_params(axis='y', labelcolor='blue')
        # colors = {'Momentum trade': 'green', 'Potential exit': 'orange', 'Mixed signal': 'purple'}
        # for action, color in colors.items():
        #     filtered_data = signals_data[signals_data['action'] == action]
        #     ax2.scatter(
        #         filtered_data['timestamp'],
        #         filtered_data['sentiment'],
        #         label=f'Signal: {action}',
        #         color=color,
        #         s=100,
        #         alpha=0.8
        #     )
        # fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.85), bbox_transform=ax1.transAxes)
        # plt.title('Stock Price and Sentiment with Signals')
        # plt.grid()
        # plt.tight_layout()
        # plt.show()
    
        merged = merged.fillna("")
        merged = merged.to_dict("records")

        latency = time.time() - start

        return {"latency": latency,
                "extreme postive threshold": extreme_pos_threshold, 
                "extreme negative threshold": extreme_neg_threshold,
                "market analyzed": merged}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
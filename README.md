# Real Time Public Sentiment and Stock Price Analysis

# Overview

## Inspiration
Market Sentiment Indicators, such as the **CBOE Volatility Index (VIX)**, **S&P 500 Market Momentum**, and **Yield Spreads**, are well-established tools used to gauge investor behavior and predict market movements. These indicators provide valuable insights into fear, greed, and risk appetite within the financial markets. For instance:
- **VIX** measures expected volatility, helping investors anticipate potential market shifts.
- **Market Momentum** reveal trends, highlighting periods of strong or weak market performance.
- **Yield spreads** reflect investor confidence in riskier assets versus safer alternatives.
- **SafeHaven** reflect investor bullishness as they invest in long term bonds

While these tools are powerful on their own, they primarily rely on quantitative data from traditional financial sources.

### The Power of Combining Social Sentiment

In the digital age, **social media** has emerged as a significant force in shaping market sentiment. Platforms like **Reddit** can amplify emotions and opinions, often leading to rapid, sentiment-driven moves in stock prices. For example:
- A viral post about a company's product or management decision can quickly sway public perception.
- Trending hashtags or discussions on platforms like **Twitter** or **r/WallStreetBets** can trigger massive buying or selling pressures.

By coupling traditional Market Sentiment Indicators with **social sentiment analysis**, we can gain a more holistic view of market dynamics. Social sentiment captures real-time reactions, opinions, and emotions from the crowd, complementing the data-driven insights from Market Sentiment Indicators. Together, these provide a more comprehensive framework for understanding and predicting market movements, enabling investors to make better-informed decisions in a rapidly evolving landscape.


## Architecture
### Data Collection and Sentiment Spike Detection

The system is designed to analyze and detect sentiment spikes in online discussions, particularly from the **r/technology** subreddit. Here’s how it works:

1. **Data Collection**:
   - Reddit submissions are fetched using the Reddit API from the **r/technology** subreddit.
   - Submissions include titles, top comments, upvote/downvote metrics, and discussion statistics.

2. **Interest Rate Calculation**:
   - Each Reddit post is assigned a **score out of 100** as a sum of the following (equal weights):
     - **Total Upvotes/Downvotes**: Gauging overall reception.
     - **Discussion Volume**: The number of comments on the post.
     - **Discussion Quality**: Weighted contribution of high-ranking comments, sorted by number of upvotes and comments

3. **Sentiment Calculation**:
   - **Weighted Sentiments**:
     - **Title Sentiment**: Contributes **30%** to the overall sentiment.
     - **Top 5 Comment Sentiments**: Contribute **70%** to the overall sentiment.
    
   - The final sentiment score of a post is calculated as:  
     - Post Sentiment = (Title Sentiment × 0.3) + (Top Comments Sentiment × 0.7) 
     - The sentiment score is weighted with interest score:  Weighted Sentiment (out of 100) = Post Sentiment × Interest Rate 

   - The above approach is robust because the following might happen
     - **Positive Title with Negative Comments**:
        - Could indicate disagreement or skepticism among users.
     - **Negative Title with Positive Comments**:
        - May reflect support for the subject despite external criticism.

4. **Data Preparation and Smoothing**
   - Standardizes timestamps and fills missing dates.
   - Uses interpolation for small data gaps and forward/backward fill for larger gaps.
   - Applies a rolling average to smooth sentiment trends.

5. **Spike Detection**
   - **Thresholds**:
     - Positive Spike: Mean + (Std. Dev × Positive Multiplier).
     - Negative Spike: Mean - (Std. Dev × Negative Multiplier).
     - Positive Multiplier is slighter smaller than Negative Multiplier because public sentiment tend to be more **negative**
   - Flags positive and negative spikes based on these thresholds, excluding interpolated data.

---
### Model Optimization

The system utilizes the [DistilBERT Sentiment Analysis Model](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) to analyze post sentiments. However, processing a year's worth of Reddit data (~10 minutes) was deemed too slow for production use. To address this:

**Optimized DistilBERT with ONNX**:
   - The model was quantized to **INT8** precision, which significantly reduces inference time.
   - Results:
     - Original Model: ~10 minutes for a year’s data.
     - Quantized Model: ~2 minutes for a year’s data (5x faster).
   - **Trade-offs**: While the optimized model is faster, there’s a slight decrease in sentiment analysis accuracy.

This optimized pipeline ensures rapid and efficient sentiment analysis, making the system scalable (For reference, I ran this model on a M2 chip with 8GB RAM Macbook)

---
### Fear & Greed Score and Market Sentiment Indicators

1. **CBOE Volatility Index (VIX)**:
   - Tracks expected volatility in the S&P 500 over the next 30 days.
   - Calculates a moving average (e.g., 50-day) to compare with current VIX levels.
   - **Fear & Greed Score**:
     - Derived from the z-score of the VIX difference relative to its moving average.
     - Higher volatility = Higher fear.

2. **S&P 500 Market Momentum**:
   - Compares the S&P 500 level to its 125-day moving average.
   - **Fear & Greed Score**:
     - Calculated using the z-score of changes in momentum.
     - Above moving average = Greed; Below = Fear.

3. **Safe Haven Demand**:
   - Measures the performance difference between stocks (SPY) and Treasury bonds (TLT) over 20 days.
   - **Fear & Greed Score**:
     - Higher bond demand relative to stocks indicates Fear.

4. **Yield Spread**:
   - Compares yields of Junk Bond ETF (HYG) and Investment-Grade ETF (LQD).
   - **Fear & Greed Score**:
     - Narrow spread = Greed; Wider spread = Fear.

Each indicator is normalized to generate a **Fear & Greed Score** on a 0–100 scale

---
### Actionable Insights

1. **Momentum Trade**:
   - **Condition**: Positive rolling correlation (7 trading days) between stock price and Fear & Greed Score, both increasing, coupled with rising sentiment.
   - **Action**: Signals a bullish market environment. Consider momentum-based trades in highly correlated assets.

2. **Potential Exit**:
   - **Condition**: Positive rolling correlation, both stock price and Fear & Greed Score decreasing, with sentiment increasing.
   - **Action**: Indicates bearish sentiment and a potential downturn. Adjust the portfolio by reducing exposure to correlated assets.

3. **Mixed Signals**:
   - **Condition**: Scenarios not meeting the above criteria.
   - **Action**: Suggests uncertainty or lack of clear trends. Exercise caution and monitor closely for emerging patterns.

**Why This Helps Investors**:
- **Momentum Trades**: In a bullish environment, strong sentiment and correlation across sectors suggest opportunities to capitalize on upward trends in correlated assets.
- **Safe-Haven Adjustments**: During bearish periods, high correlations and sentiment shifts signal a need to pivot towards safer investments like negatively correlated assets or bonds, protecting against volatility and potential losses.

---
# Installation and Setup Guide
## Dependencies
### Step 1: Create Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```
### Step 2: Install Backend Dependencies
```bash
# Navigate to backend directory
cd backend

# Install required Python packages
pip install -r requirements.txt
```
### Step 3: Install Frontend Dependencies
```bash
# Navigate to frontend directory  
cd frontend

# Install required npm packages
yarn install
```
## Configuration & Usage

### Step 1: Configure Reddit API
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create a new application and get your credentials
3. Add your Reddit API credentials to the configuration file:
```bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USER_AGENT=your_user_agent
```

### Step 2: Start Backend Server
```bash
# Navigate to backend directory
cd backend

# Start FastAPI server
uvicorn main:app --reload
```
The API will be available at http://localhost:8000

### Step 3: Start Frontend Server
```bash
# Navigate to frontend directory
cd frontend

# Start development server
yarn run dev
```
The API will be available at http://localhost:8000

# Demo
[Watch the video](https://youtu.be/8WFTdLFnzp4)




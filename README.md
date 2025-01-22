# Real Time Public Sentiment and Stock Price Analysis
# Overview
## Inspiration
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

This optimized pipeline ensures rapid and efficient sentiment analysis, making the system scalable for long-term data processing.

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




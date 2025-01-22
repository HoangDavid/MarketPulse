# Real Time Public Sentiment and Stock Price Analysis

# Overview

# Architecture

## Calculate and detect sentiments spikes
pull from Reddit API
pull reddit submissions from r/technology and calculate sentiments
post interest rate is calculated using total upvotes/downvotes, discussion volume, discussion quality of a submission -> score is out of 100
Then, calculate the weighted sentiments of each post 0.3 title_weight and 0.7 top 5 comment_weights sentiments then add both
Then the sentiment of a post is the sentiment * the interest rate

Drawback:
- A positive title could have negative comments, reflecting disagreement or skepticism.
- A negative title could have positive comments, showing support for a company despite criticism.\

Model Optimization: 
With the default [link to model: https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english] distilbert model
-> sentiment analysis of a year worth data takes about 10' -> too slow
-> solution Optimized DistilBert for faster inference using ONX: quantized the model for INT8  ~ 2' minute for a year worth data (5x faster but trade of for some performance)


## Fear Greed Score and Market Sentiment Indicators 
pull from Yahoo API 
Fear and Greed 

Market Momentum

Safe Haven

Vix

Yield spread indicator:
- HYG: Tracks the iBoxx $ High Yield Corporate Bond Index
- LQD: Tracks the iBoxx $ Investment Grade Corporate Bond Index.

## Architecture

### Sentiment Spike Detection

The system is designed to analyze and detect sentiment spikes in online discussions, particularly from the **r/technology** subreddit. Here’s how it works:

1. **Data Collection**:
   - Reddit submissions are fetched using the Reddit API from the **r/technology** subreddit.
   - Submissions include titles, top comments, upvote/downvote metrics, and discussion statistics.

2. **Interest Rate Calculation**:
   - Each Reddit post is assigned a **score out of 100** based on:
     - **Total Upvotes/Downvotes**: Gauging overall reception.
     - **Discussion Volume**: The number of comments on the post.
     - **Discussion Quality**: Weighted contribution of high-ranking comments.

3. **Sentiment Calculation**:
   - **Weighted Sentiments**:
     - **Title Sentiment**: Contributes **30%** to the overall sentiment.
     - **Top 5 Comment Sentiments**: Contribute **70%** to the overall sentiment.
   - The final sentiment score of a post is calculated as:
     \[
     \text{Post Sentiment} = (\text{Title Sentiment} \times 0.3) + (\text{Top Comments Sentiment} \times 0.7)
     \]
   - **Weighted Post Sentiment**:
     - The sentiment score is further adjusted using the interest rate:
       \[
       \text{Weighted Sentiment} = \text{Post Sentiment} \times \text{Interest Rate}
       \]

#### Drawbacks:
- **Positive Title with Negative Comments**:
  - Could indicate disagreement or skepticism among users.
- **Negative Title with Positive Comments**:
  - May reflect support for the subject despite external criticism.

---

### Model Optimization

The system utilizes the [DistilBERT Sentiment Analysis Model](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) to analyze post sentiments. However, processing a year's worth of Reddit data (~10 minutes) was deemed too slow for production use. To address this:

1. **Optimized DistilBERT with ONNX**:
   - The model was quantized to **INT8** precision, which significantly reduces inference time.
   - Results:
     - Original Model: ~10 minutes for a year’s data.
     - Quantized Model: ~2 minutes for a year’s data (5x faster).
   - **Trade-offs**: While the optimized model is faster, there’s a slight decrease in sentiment analysis accuracy.

This optimized pipeline ensures rapid and efficient sentiment analysis, making the system scalable for long-term data processing.


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




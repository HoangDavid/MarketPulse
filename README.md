# MarketPulse-Real-Time-Public-Sentiment-and-Stock-Price-Analytics

how to install dependecies: pip install -r requirements.txt

Post influence score

r/technology
- A positive title could have negative comments, reflecting disagreement or skepticism.
- A negative title could have positive comments, showing support for a company despite criticism.

Yield spread indicator:
- HYG: Tracks the iBoxx $ High Yield Corporate Bond Index
- LQD: Tracks the iBoxx $ Investment Grade Corporate Bond Index.

Getting historical sentiment / stock takes ~ 8 - 10 minutes

Optimized DistilBert for faster inference using ONX: quantized the model for INT8  ~ 1 minute for a year worth data

https://youtu.be/8WFTdLFnzp4


Dependencies:
step 1: create a virtual enviroment
step 2: cd backend -> pip install -r requirements.txt
step 3: cd frontend -> yarn install

To Use:
Step 1: Reddit API using your credentials
Step 2: start the FASTAPI backend by using the following command: cd backend -> uvicorn main:app
Step 3: start the frontend: cd frontend -> yarn run dev

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
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USER_AGENT=your_user_agent

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




import asyncpraw
import asyncio
import math
import os
import time
from fastapi import HTTPException
import pandas as pd
from decouple import config
from datetime import datetime
from zoneinfo import ZoneInfo
from services.resource_init import MODELS

# Initialize the Reddit client
reddit = asyncpraw.Reddit(
    client_id=config("REDDIT_CLIENT_ID"),
    client_secret=config("REDDIT_SECRET"),
    user_agent=config("REDDIT_USER_AGENT"),
    username=config("REDDIT_USERNAME"),
    password=config("REDDIT_PASSWORD"),
)

# Take into account the computer resource
semaphore = asyncio.Semaphore(os.cpu_count() * 2) 



### Fetch reddit posts from Reddit API
# limit = 251 (trading days in a year)
async def fetch_reddit_posts(
        subreddit_name: str, query: str, 
        time_filter: str, limit: int) -> list:
    '''
    Args:
        subreddit_name (str): The name of the subreddit (e.g., 'stocks').
        query (str): The search query within the subreddit.
        time_filter: search the submissions (hour, day, week, month, year, all)
        batch_size (int): Number of posts to fetch per batch.
        start_date (datetime): Start of the time range.
    '''
    
    subreddit = await reddit.subreddit(subreddit_name)

    # Run the processing of the reddit post concurrently
    async def fetch_one_post(submission: asyncpraw.models.Submission):
        async with semaphore:
            # Top 10 most interacted comment
            submission.comment_sort = "top"
            submission.comment_limit = 10
            await submission.load()
            await submission.comments.replace_more(limit=0)

            interest_score = engagement_rate(submission)

            time_stamp = None
            if time_filter in ["year", "month", "week"]:
                time_stamp = datetime.fromtimestamp(submission.created_utc, ZoneInfo("US/Eastern")).strftime('%Y-%m-%d')
            elif time_filter == "day":
                time_stamp = datetime.fromtimestamp(submission.created_utc, ZoneInfo("US/Eastern")).strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                "title": submission.title,
                "timestamp": time_stamp,
                "interest score": interest_score,
                "article url": submission.url, 
                "comments": [(comment.body, comment.score)  for comment in submission.comments]
            }

    # Queue the tasks to run concurrently
    tasks = []
    async for submission in subreddit.search(f'title:{query}', time_filter=time_filter, sort="top", limit=limit):
        tasks.append(fetch_one_post(submission))

    posts = await asyncio.gather(*tasks, return_exceptions=False)

    # Sort posts by timestamp
    sorted_posts = sorted(posts, key=lambda x: x["timestamp"])
    
    return sorted_posts



### Calculate the influential index of a submission based of engagement rate in the comments volume, 
def engagement_rate(submission: asyncpraw.models.Submission, max_interest: int=100000) -> float:
    try:
        # Metrics:
        post_score = submission.score
        upvote_ratio = submission.upvote_ratio
        total_comments = submission.num_comments
        top_comments = submission.comments

        # Calculate interest:
        post_interest = post_score * upvote_ratio
        discussion_volume = total_comments
        discussion_quality = (
            sum(comment.score for comment in top_comments if not isinstance(comment, asyncpraw.models.MoreComments)) 
            / (1 + math.log(post_score + 1) + math.log(total_comments + 1))
        )
        
        # Calculate the weighted total interest in a post
        total_interest = post_interest + discussion_volume + discussion_quality
        
        normalized_interest = (total_interest / max_interest) * 100
        
        return normalized_interest

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



### Calculate social sentiment
async def fetch_social_sentiment(subreddit: str, query: str, time_filter: str, limit: int = 250) -> pd.DataFrame:
    """
    API endpoint to fetch Reddit posts from a subreddit.

    Args:
        subreddit (str): Subreddit name.
        query (str): query within the subreddit
        sort_by (str): sort the post by hot, popularity, best, relevance
        limit (int): Number of posts to fetch (default: 10).

    Returns:
        JSON response with that subreddit posts sentiment score
    """
    try:
        # Run the the sentiment analysis in parrallel
        async def analyze_post_sentiment(post: dict):
            async with semaphore:
                sentiment = await calculate_post_sentiment(post['title'], post['comments'], post["interest score"])
                return {
                    "timestamp": post["timestamp"],
                    "sentiment": sentiment,
                    "article url": post["article url"],
                    "title": post["title"],
                    "top comment": post["comments"][0][0] if len(post["comments"]) > 0 else "",
                    "article url": post["article url"],
                }

        posts = await fetch_reddit_posts(subreddit, query, time_filter, limit)
        
        tasks = [analyze_post_sentiment(post) for post in posts]
        
        analyzed_sentiment = await asyncio.gather(*tasks, return_exceptions=False)
        # TODO: store data in MongoDB and use Redis for fast retrieval
                                                
        analyzed_sentiment = pd.DataFrame(analyzed_sentiment)

        # Get the top post of each day
        analyzed_sentiment['Abs'] = analyzed_sentiment['sentiment'].abs()
        analyzed_sentiment = analyzed_sentiment.loc[analyzed_sentiment.groupby('timestamp')['Abs'].idxmax()]
        analyzed_sentiment = analyzed_sentiment.drop(columns=['Abs'])

        return analyzed_sentiment

    except Exception as e:
        # TODO:Logging in the server and send a payload to the client
        raise HTTPException(status_code=500, detail=str(e))
   


### Analyze each submission sentiment
async def calculate_post_sentiment(title: str, comments: list, interest_score: float, title_weight: float = 0.3, comments_weight: float = 0.7) -> dict:
    try:
        total_votes = sum(comment[1] for comment in comments) # avoid division by 0
        sentiment_scores = []
        
        # Run the model for comments sentiment analysis
        for comment in comments:
            # Model max input token is 512
            sentiments = await asyncio.to_thread(
                MODELS['social_sentiment']["predict"], 
                comment[0][:512]
                )
        
            sentiment_scores.append({
                "NEGATIVE": sentiments[0],
                "POSITIVE": sentiments[1],
                "weight": comment[1] / total_votes
             })

        # Aggregrate the seniments from the comments
        comments_negative_score = sum(s["NEGATIVE"] * s["weight"] for s in sentiment_scores)
        comments_positive_score = sum(s["POSITIVE"] * s["weight"] for s in sentiment_scores)

        
        # Run the model for title sentiment analysis
        title_sentiment = await asyncio.to_thread(
            MODELS['social_sentiment']["predict"],
            title
            )

        overall_negative_score = title_sentiment[0] * title_weight + comments_negative_score * comments_weight
        overall_positive_score = title_sentiment[1] * title_weight + comments_positive_score * comments_weight

        # normalized score
        sum_score = overall_positive_score + overall_negative_score
        if sum_score > 0:
            overall_positive_score = overall_positive_score / sum_score
            overall_negative_score = overall_negative_score / sum_score

        # Calculate net sentiment with weighted interest score
        net_sentiment = (overall_positive_score - overall_negative_score) * interest_score
        return net_sentiment.item()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
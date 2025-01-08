import asyncio
import os
import time
from fastapi import APIRouter, HTTPException
from services.reddit import fetch_reddit_posts
from services.resource_init import MODELS


router = APIRouter()
semaphore = asyncio.Semaphore(os.cpu_count() * 2) 

@router.get("/social-sentiment/{subreddit}")
async def analyze_social_sentiment(subreddit: str, query: str, time_filter: str, limit: int = None):
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
        # Start time for latency check
        start_time = time.perf_counter()
        
        # Run the the sentiment analysis in parrallel
        async def analyze_post_sentiment(post: dict):
            async with semaphore:
                sentiment = await get_post_sentiment(post['title'], post['comments'], post["interest score"])
                return {
                    "title": post["title"],
                    "timestamp": post["timestamp"],
                    "interest score": post["interest score"],
                    "article url": post["article url"],
                    "top comment": post["comments"][0][0] if len(post["comments"]) > 0 else "",
                    "sentiment": sentiment
                }

        posts = await fetch_reddit_posts(subreddit, query, time_filter, limit)
        
        tasks = [analyze_post_sentiment(post) for post in posts]
        
        analyzed_sentiment = await asyncio.gather(*tasks, return_exceptions=False)

        # Calculate the latency for the operation
        end_time = time.perf_counter()
        latency = end_time - start_time

        # TODO: store data in MongoDB and use Redis for fast retrieval                                        
        
        return {"subreddit": subreddit, "latency": latency ,"analyzed_sentiment": analyzed_sentiment}

    except Exception as e:
        # TODO:Logging in the server and send a payload to the client
        raise HTTPException(status_code=500, detail=str(e))
    

# Analyze each submission sentiment
async def get_post_sentiment(title: str, comments: list, interest_score: float, title_weight: float = 0.3, comments_weight: float = 0.7) -> dict:
    try:
        total_votes = sum(comment[1] for comment in comments) or 1 # avoid division by 0
        sentiment_scores = []
        
        # Run the model for comments sentiment analysis
        for comment in comments:
            # Model max input token is 512
            sentiments = await asyncio.to_thread(
                MODELS['social_sentiment'], 
                comment[0][:512], 
                return_all_scores=True)

            for sentiment in sentiments[0]:
                sentiment_scores.append({
                    "label": sentiment["label"],
                    "score": sentiment["score"],
                    "weight": comment[1] / total_votes
                })

        # Aggregrate the seniments from the comments
        comments_negative_score = sum(s["score"] * s["weight"] for s in sentiment_scores if s["label"] == "NEGATIVE")
        comments_positive_score = sum(s["score"] * s["weight"] for s in sentiment_scores if s["label"] == "POSITIVE")

        
        # Run the model for title sentiment analysis
        title_sentiment = await asyncio.to_thread(
            MODELS['social_sentiment'],
            title, 
            return_all_scores=True)
    
        title_score = {}
        for sentiment in title_sentiment[0]:
            title_score[sentiment['label']] = sentiment["score"]

        overall_positive_score = title_score["POSITIVE"] * title_weight + comments_positive_score * comments_weight
        overall_negative_score = title_score["NEGATIVE"] * title_weight + comments_negative_score * comments_weight

        # normalized score
        sum_score = overall_positive_score + overall_negative_score
        if sum_score > 0:
            overall_positive_score = overall_positive_score / sum_score
            overall_negative_score = overall_negative_score / sum_score

        overall_label = ""
        if overall_positive_score > overall_negative_score:
            overall_label = "POSITIVE"
        elif overall_positive_score < overall_negative_score:
            overall_label = "NEGATIVE"
        else:
            overall_label = "NEUTRAL"
        
        # Calculate net sentiment with weighted interest score
        net_sentiment = (overall_positive_score - overall_negative_score) * interest_score
        return {
            "label": overall_label,
            "sentiment": net_sentiment
        }
    
    except Exception as e:
        print(e)
        return {}

    
    


    
    
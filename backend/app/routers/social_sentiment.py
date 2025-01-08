import time
from fastapi import APIRouter, HTTPException
from services.reddit import fetch_social_sentiment


router = APIRouter()

@router.get("/social-sentiment/{subreddit}")
async def get_social_sentiment(subreddit: str, query: str, time_filter: str, limit: int = None):
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
        
        # Fetch social sentiment
        analyzed_sentiment = await fetch_social_sentiment(
            subreddit=subreddit, query=query, time_filter=time_filter, limit=limit)
        
        analyzed_sentiment = analyzed_sentiment.to_dict("records")
    
        # Calculate the latency for the operation
        end_time = time.perf_counter()
        latency = end_time - start_time

        # TODO: store data in MongoDB and use Redis for fast retrieval                                        
        
        return {"subreddit": subreddit, "latency": latency ,"analyzed_sentiment": analyzed_sentiment}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


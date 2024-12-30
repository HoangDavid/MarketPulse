from fastapi import APIRouter, HTTPException
from services.reddit import fetch_reddit_posts
router = APIRouter()

@router.get("/reddit/{subreddit}")
async def get_reddit_posts(subreddit: str, query: str, sort_by: str, limit: int = 10):
    """
    API endpoint to fetch Reddit posts from a subreddit.

    Args:
        subreddit (str): Subreddit name.
        query (str): query within the subreddit
        sort_by (str): sort the post by hot, popularity, best, relevance
        limit (int): Number of posts to fetch (default: 10).

    Returns:
        JSON response with subreddit posts.
    """
    try:
        posts = await fetch_reddit_posts(subreddit, query, sort_by, limit)
        return {"subreddit": subreddit, "sort_by": sort_by, "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
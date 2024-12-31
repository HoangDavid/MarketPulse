import asyncio
from asyncpraw import Reddit
from decouple import config

# Initialize the Reddit client
reddit = Reddit(
    client_id=config("REDDIT_CLIENT_ID"),
    client_secret=config("REDDIT_SECRET"),
    user_agent=config("REDDIT_USER_AGENT"),
    username=config("REDDIT_USERNAME"),
    password=config("REDDIT_PASSWORD"),
)

async def fetch_reddit_posts(subreddit: str, query: str, sort_by: str, limit: int = 10):
    """
    Fetch posts from a specified subreddit.

    Args:
        subreddit_name (str): The name of the subreddit (e.g., 'stocks').
        query (str): query within the subreddit
        sort_by (str): sort the post by hot, popularity, best, relevance
        limit (int): The number of posts to fetch (default: 10).

    Returns:
        list[dict]: A list of posts as dictionaries.
    """
    subreddit = await reddit.subreddit(subreddit)
    posts = []

    # Fetch new posts
    async for submission in subreddit.search(query, limit=limit, sort=sort_by):
        post = {
            "id": submission.id,
            "title": submission.title,
            "created_utc": submission.created_utc,
            "upvotes": submission.score,
            "comments": submission.num_comments,
            "url": submission.url,
            "subreddit": subreddit,
        }
        posts.append(post)

    return posts

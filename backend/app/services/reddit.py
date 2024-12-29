import asyncio
from asyncpraw import Reddit
from asyncpraw.models import Submission
from decouple import config

# Initialize the Reddit client
reddit = Reddit(
    client_id=config("REDDIT_CLIENT_ID"),
    client_secret=config("REDDIT_SECRET"),
    user_agent=config("REDDIT_USER_AGENT")
)

async def fetch_reddit_posts(subreddit_name: str, limit: int = 10):
    """
    Fetch posts from a specified subreddit.

    Args:
        subreddit_name (str): The name of the subreddit (e.g., 'stocks').
        limit (int): The number of posts to fetch (default: 10).

    Returns:
        list[dict]: A list of posts as dictionaries.
    """
    subreddit = await reddit.subreddit(subreddit_name)
    posts = []

    # Fetch new posts
    async for submission in subreddit.new(limit=limit):
        post = {
            "id": submission.id,
            "title": submission.title,
            "body": submission.selftext,
            "created_utc": submission.created_utc,
            "upvotes": submission.score,
            "comments": submission.num_comments,
            "url": submission.url,
            "subreddit": subreddit_name,
        }
        posts.append(post)

    return posts

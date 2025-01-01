import asyncio
from asyncpraw import Reddit
from decouple import config
from datetime import datetime
from zoneinfo import ZoneInfo

# Initialize the Reddit client
reddit = Reddit(
    client_id=config("REDDIT_CLIENT_ID"),
    client_secret=config("REDDIT_SECRET"),
    user_agent=config("REDDIT_USER_AGENT"),
    username=config("REDDIT_USERNAME"),
    password=config("REDDIT_PASSWORD"),
)

async def fetch_reddit_posts(subreddit_name: str, query: str, sort_by: str, limit: int):
    print(f"Fetching posts from subreddit: {subreddit_name}, query: {query}, sort_by: {sort_by}, limit: {limit}")
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
    subreddit = await reddit.subreddit(subreddit_name)
    posts = []

    # Fetch new posts
    async for submission in subreddit.search(query, limit=limit, sort=sort_by):
        post = {
            "id": submission.id,
            "title": submission.title,
            "time_stamp": datetime.fromtimestamp(submission.created_utc, tz=ZoneInfo("US/Eastern")),
            "upvotes": submission.score,
            "comments": submission.num_comments,
            "url": submission.url,
            "subreddit": subreddit_name,
        }
        posts.append(post)

    return posts

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

async def fetch_reddit_posts(
        subreddit_name: str, query: str, 
        time_filter: str, limit: int = None):
    '''
    Args:
        subreddit_name (str): The name of the subreddit (e.g., 'stocks').
        query (str): The search query within the subreddit.
        time_filter: search the submissions (hour, day, week, month, year, all)
        batch_size (int): Number of posts to fetch per batch.
        start_date (datetime): Start of the time range.
    '''
    
    subreddit = await reddit.subreddit(subreddit_name)
    posts = []

    async for submission in subreddit.search(query, time_filter=time_filter, sort="new", limit=limit):
        post = {
            "title": submission.title,
            "time_stamp": datetime.fromtimestamp(submission.created_utc, tz=ZoneInfo("US/Eastern")),
            "upvotes": submission.score,
            "comments": submission.num_comments,
            "body": submission.selftext,
        }
        
        posts.append(post)

    return posts


def clean_post():
    ...


'''
r/technology: news and public opinion on the matter -> use distilbert/Finbert to sentiment on a headline
r/
TODO:
- fetch posts until the first 
- filter posts to remove noises 
- filter batch process the comments for sentiment as well
'''
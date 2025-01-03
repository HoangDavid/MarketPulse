import asyncpraw
import asyncio
import math
import logging
import os
from decouple import config
from datetime import datetime
from zoneinfo import ZoneInfo


# Logging for server
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Initialize the Reddit client
reddit = asyncpraw.Reddit(
    client_id=config("REDDIT_CLIENT_ID"),
    client_secret=config("REDDIT_SECRET"),
    user_agent=config("REDDIT_USER_AGENT"),
    username=config("REDDIT_USERNAME"),
    password=config("REDDIT_PASSWORD"),
)

semaphore = asyncio.Semaphore(os.cpu_count() * 2) 

# Used for historical and updating sentiment of posts throughout the week
async def fetch_reddit_posts(
        subreddit_name: str, query: str, 
        time_filter: str, limit: int = None) -> list:
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

    # Run the processing of the reddit post concurrently
    async def fetch_one_post(submission: asyncpraw.models.Submission):
        async with semaphore:
            # Top 5 most interacted comment
            submission.comment_sort = "top"
            submission.comment_limit = 5
            await submission.load()
            await submission.comments.replace_more(limit=0)

            interest_score = engagement_rate(submission)
            
            return {
                "title": submission.title,
                "timestamp": datetime.fromtimestamp(
                    submission.created_utc, ZoneInfo("US/Eastern")
                ).strftime('%Y-%m-%d %H:%M:%S'),
                "interest score": interest_score,
                "comments": [comment.body for comment in submission.comments]
            }

    # Queue the tasks to run concurrently
    tasks = []
    async for submission in subreddit.search(f'title:{query}', time_filter=time_filter, sort="top", limit=limit):
        tasks.append(fetch_one_post(submission))

    posts = await asyncio.gather(*tasks, return_exceptions=False)
    
    return posts

# Calculate the influential index of a submission based of engagement rate in the comments volume, 
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
        logging.error(f"Error calculating engagement rate for submission{submission.title}:{e}", exc_info=True)
        return 0
    

    
    
    

'''
Rolling correlation: to mark events
- r/technology: news and public opinion on the matter -> use distilbert/Finbert to sentiment on a headline
- r/walstreetbets as well to aid sparse data
TODO:
- filter posts to remove noises 
- filter batch process the comments for sentiment as well
'''
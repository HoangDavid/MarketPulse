import asyncpraw
import math
from decouple import config
from datetime import datetime
from zoneinfo import ZoneInfo


# Initialize the Reddit client
reddit = asyncpraw.Reddit(
    client_id=config("REDDIT_CLIENT_ID"),
    client_secret=config("REDDIT_SECRET"),
    user_agent=config("REDDIT_USER_AGENT"),
    username=config("REDDIT_USERNAME"),
    password=config("REDDIT_PASSWORD"),
)

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

    async for submission in subreddit.search(f'title:{query}', time_filter=time_filter, sort="top", limit=limit):
        # Only take top 5 comments
        engagement_score = await is_influential(submission)
        break
        posts.append(engagement_score)
    return posts




# Calculate the influential index of a submission based of engagement rate in the comments volume, 
async def is_influential(submission: asyncpraw.models.Submission, max_interest: int=100000) -> bool:
    try:
        submission.comment_sort = "top"
        submission.comment_limit = 5
        await submission.load()
        await submission.comments.replace_more(limit=0)

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
        # Below 1 is filtered out
        print(normalized_interest)
        
        return len(submission.comments) 

    except Exception as e:
        print(f"Error fetching comments {e}")
        return 0
    

    
    
    
    
    

'''
Rolling correlation: to mark events
- r/technology: news and public opinion on the matter -> use distilbert/Finbert to sentiment on a headline
- r/walstreetbets as well to aid sparse data
TODO:
- filter posts to remove noises 
- filter batch process the comments for sentiment as well
'''
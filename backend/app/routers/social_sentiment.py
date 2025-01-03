from fastapi import APIRouter, HTTPException
from services.reddit import fetch_reddit_posts
from services.resource_init import MODELS
router = APIRouter()

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
        ret = []
        posts = await fetch_reddit_posts(subreddit, query, time_filter, limit)
        for post in posts:
            sentiment = get_post_sentiment(post['title'], post['comments'])
            ret.append({
                "title": post["title"],
                "timestamp": post["timestamp"],
                "interest score": post["interest score"],
                "article url": post["article url"],
                "sentiment": sentiment
            })
            break
        
        return {"subreddit": subreddit, "analyzed_setiment": ret}
    except Exception as e:
        # TODO:Logging in the server and send a payload to the client
        raise HTTPException(status_code=500, detail=str(e))
    

# Analyze each submission sentiment
def get_post_sentiment(title: str, comments: list, title_weight: float = 0.4, comments_weight: float = 0.6) -> dict:
    try:
        total_votes = sum(comment[1] for comment in comments) or 1 # avoid division by 0
        sentiment_scores = []
        
        # Run the model for comments sentiment analysis
        for comment in comments:
            sentiments = MODELS['social_sentiment'](comment[0], return_all_scores=True)[0]
            for sentiment in sentiments:
                sentiment_scores.append({
                    "label": sentiment["label"],
                    "score": sentiment["score"],
                    "weight": comment[1] / total_votes
                })

        # Aggregrate the seniments from the comments
        comments_positive_score = sum(s["score"] * s["weight"] for s in sentiment_scores if s["label"] == "NEGATIVE")
        comments_negative_score = sum(s["score"] * s["weight"] for s in sentiment_scores if s["label"] == "POSITIVE")
        
        # Run the model for title sentiment analysis
        title_sentiment = MODELS['social_sentiment'](title, top_k=None)[0]
        title_score = {}
        for sentiment in title_sentiment:
            title_score[title_sentiment['label']] = title_sentiment["score"]

        overall_positive_score = title_score.get("POSITIVE", 0) * title_weight + comments_positive_score * comments_weight
        overall_negative_score = title_score.get("NEGATIVE", 0) * title_weight + comments_negative_score * comments_weight

        overall_label = ""
        if overall_positive_score > overall_negative_score:
            overall_label = "POSITIVE"
        elif overall_positive_score < overall_negative_score:
            overall_label = "NEGATIVE"
        else:
            overall_label = "NEUTRAL"

        return {
            "label": overall_label,
            "POSITIVE": overall_positive_score,
            "NEGATIVE": overall_negative_score
        }
    
    except Exception as e:
        print(e)
        return {}

    
    


    
    
"""Reddit scraper."""
import praw
import json

with open('app.credentials', 'r') as f:
    credentials = json.loads(f.read())

reddit = praw.Reddit(client_id=credentials['client_id'],
                     client_secret=credentials['client_secret'],
                     user_agent=credentials['user_agent'],
                     username=credentials['username'])


def get_submissions(topic, count, type):
    """Gets the given count of submissions of given type."""
    subreddits = reddit.subreddit(topic)
    if type == 'new':
        subm = subreddits.new(limit=count)
    elif type == 'hot':
        subm = subreddits.hot(limit=count)
    elif type == 'top':
        subm = subreddits.top(limit=count)
    else:
        subm = subreddits.controversial(limit=count)
    return [{
        'id': s.id,
        'author': s.author.name,
        'full_name': s.name,
        'title': s.title,
        'text': s.selftext,
        'score': s.score,
        'upvote_ratio': s.upvote_ratio,
        'is_nfsw': s.over_18,
        'comments': [comment.body for comment in s.comments],
        'time': s.created_utc,
        'url': s.url
    } for s in subm]

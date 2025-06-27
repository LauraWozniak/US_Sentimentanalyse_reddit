import praw
import pandas as pd
import os
import time

with open('cred/Client_id.txt.gitignore') as f: client_id = f.read().strip()
with open('cred/Key.txt.gitignore') as f: client_secret = f.read().strip()
with open('cred/useragent.txt.gitignore') as f: user_agent = f.read().strip()
with open('cred/pw.txt.gitignore') as f: password = f.read().strip()
with open('cred/un.txt.gitignore') as f: username = f.read().strip()

data_dir = "../data/raw"
# Using Praw to not get rate limited
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)


SUBREDDIT = "MogelPackung"
LIMIT = 100
POSTS = []
COMMENTS = []

#nur nach neuen posts suchen die nach dem letzten post im csv erstellt wurden
#TODO besseren loop damit nicht nur nach datum Raus sind
#Posts werden nach 6 monaten Archiviert/ können nicht mehr kommentiert werden
posts_path = os.path.join(data_dir, "reddit_posts.csv")
if os.path.exists(posts_path):
    df_existing = pd.read_csv(posts_path)
    latest_timestamp = df_existing["created_utc"].max()
else:
    df_existing = pd.DataFrame()
    latest_timestamp = 0
    print("No previous post data found. Fetching fresh.")

# Fetch posts
for post in reddit.subreddit(SUBREDDIT).new(limit=LIMIT):
    if post.created_utc <= latest_timestamp:
        continue
    POSTS.append({
        'id': post.id,
        'title': post.title,
        'score': post.score,
        'upvote_ratio': post.upvote_ratio,
        'author': str(post.author),
        'num_comments': post.num_comments,
        'created_utc': post.created_utc,
        'selftext': post.selftext,
        'permalink': f"https://reddit.com{post.permalink}"
    })

    post.comments.replace_more(limit=0)  # Remove "load more" threads

    for comment in post.comments.list():
        COMMENTS.append({
            'post_id': post.id,
            'comment_body': comment.body,
            'comment_author': str(comment.author),
            'comment_score': comment.score,
            'comment_created_utc': comment.created_utc
        })

    time.sleep(2)

# csv

os.makedirs(data_dir, exist_ok=True)

df_new_posts = pd.DataFrame(POSTS)
if not df_existing.empty:
    df_combined = pd.concat([df_existing, df_new_posts], ignore_index=True)
else:
    df_combined = df_new_posts
df_combined.to_csv(posts_path, index=False)



#Automod Exception
comments_path = os.path.join(data_dir, "reddit_comments.csv")

df_comments = pd.DataFrame(COMMENTS)

# Remove AutoModerator and bot signature
df_comments = df_comments[
    (df_comments['comment_author'] != "AutoModerator") &
    (~df_comments['comment_body'].str.contains("I am a bot, and this action was performed automatically", na=False))
]

# Save cleaned comments
df_comments.to_csv(comments_path, mode='a', header=not os.path.exists(comments_path), index=False)
print("Saved posts and comments.")

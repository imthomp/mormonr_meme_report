import sqlite3
import os
import requests
import json
import zipfile
import shutil
import pytz
from datetime import datetime

destination_directory = 'twitter_data'
meme_directory = os.path.join(destination_directory, 'memes')
path_to_zip_file = './twitter-2023-10-11-3d617ff4033ccc334de0e457100148d7791fe92f3733a151eb93fcd60fcb1c34.zip'

# Create SQLite database and table
conn = sqlite3.connect('memes.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS memes (
    date TEXT NOT NULL,
    local_file TEXT NOT NULL,
    likes_count INTEGER
)
''')
conn.commit()

# Ensure directories exist
for dir_path in [destination_directory, meme_directory]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Backup logic
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
backup_directory = os.path.join(destination_directory, f'backup_{timestamp}')
if os.path.exists(destination_directory):
    if os.path.exists(backup_directory):
        print(f"Backup directory {backup_directory} already exists! Choose a different path or remove the existing one.")
        exit(1)
    else:
        shutil.copytree(destination_directory, backup_directory)
else:
    print(f"Source directory {destination_directory} does not exist.")
    exit(1)

# Extract tweets.js from the zip file
extracted_tweets_path = 'data/tweets.js'
with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
    zip_ref.extract(extracted_tweets_path, destination_directory)

# The path to the extracted tweets.js file
tweets_js_path = os.path.join(destination_directory, extracted_tweets_path)

# Load tweets from tweets.js
tweets = []  # Initialize tweets as an empty list
with open(tweets_js_path, 'r', encoding='utf-8') as f:
    content = f.read()
    json_content = content.replace("window.YTD.tweets.part0 = ", "")
    try:
        tweets = json.loads(json_content)
        # For testing purposes, uncomment the next line to process only the first 10 tweets
        tweets = tweets[:100]
    except json.JSONDecodeError as e:
        print(f"Error occurred while parsing JSON. Details: {e}")
        print(f"Content leading to error:\n{json_content[:1000]}...")  # Print the first 1000 characters
        exit(1)  # Terminate the script

# Process tweets
for tweet in tweets:
    try:
        date = tweet['tweet']['created_at']
        media = tweet['tweet'].get('entities', {}).get('media', [])
        likes_count = tweet['tweet'].get('favorite_count', 0)

        if media:
            # Convert UTC date to Mountain Time (MT) and format it
            utc_date = datetime.strptime(date, "%a %b %d %H:%M:%S %z %Y")
            mt_timezone = pytz.timezone('US/Mountain')
            mt_date = utc_date.astimezone(mt_timezone)
            # formatted_date = mt_date.strftime("%Y-%m-%d %I:%M %p %Z")
            formatted_date = mt_date.strftime("%B %d, %Y")
            
            meme_url = media[0]['media_url_https']
            sanitized_date = formatted_date.replace(":", "_").replace(" ", "_")
            local_file = os.path.join(meme_directory, f"{sanitized_date}.png")
            
            response = requests.get(meme_url)
            with open(local_file, 'wb') as f:
                f.write(response.content)
            
            cursor.execute(
                "INSERT INTO memes (date, local_file, likes_count) VALUES (?, ?, ?)", 
                (formatted_date, os.path.basename(local_file), likes_count)
            )
            conn.commit()
            print(f"Processed tweet from {formatted_date}")

    except Exception as e:
        print(f"Error processing tweet from {formatted_date}. Error: {e}")

# Cleanup
os.remove(tweets_js_path)

conn.close()
print("Script completed successfully!")

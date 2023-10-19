## extract_memes_from_twitter_data.py

import sqlite3
import os
import requests
import json
import zipfile
import pytz
from datetime import datetime

destination_directory = 'twitter_data'
meme_directory = os.path.join(destination_directory, 'memes')
path_to_zip_file = './twitter-2023-10-11-3d617ff4033ccc334de0e457100148d7791fe92f3733a151eb93fcd60fcb1c34.zip'

def init_database():
    conn = sqlite3.connect('memes.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS memes")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memes (
        date TEXT NOT NULL,
        local_file TEXT NOT NULL,
        likes_count INTEGER
    )
    ''')
    return conn, cursor

def remove_directory(path):
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)

def ensure_directories():
    # Remove the directory if it already exists
    remove_directory(destination_directory)

    # Recreate the directories
    for dir_path in [destination_directory, meme_directory]:
        os.makedirs(dir_path)

def extract_tweets(path_to_zip_file):
    extracted_tweets_path = 'data/tweets.js'
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extract(extracted_tweets_path, destination_directory)

    tweets_js_path = os.path.join(destination_directory, extracted_tweets_path)
    with open(tweets_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
        json_content = content.replace("window.YTD.tweets.part0 = ", "")
        return json.loads(json_content)

def process_tweet(tweet, cursor):
    if 'retweeted_status' in tweet['tweet']:
        return

    try:
        date = tweet['tweet']['created_at']
        media = tweet['tweet'].get('entities', {}).get('media', [])
        likes_count = tweet['tweet'].get('favorite_count', 0)

        if media:
            utc_date = datetime.strptime(date, "%a %b %d %H:%M:%S %z %Y")
            mt_timezone = pytz.timezone('US/Mountain')
            mt_date = utc_date.astimezone(mt_timezone)
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
            print(f"Processed tweet from {formatted_date}")

    except Exception as e:
        print(f"Error processing tweet from {date}. Error: {e}")


def main():
    ensure_directories()

    conn, cursor = init_database()
    tweets = extract_tweets(path_to_zip_file)
    # testing
    tweets = tweets[:100]

    for tweet in tweets:
        process_tweet(tweet, cursor)

    conn.commit()
    conn.close()
    print("Script completed successfully!")

if __name__ == "__main__":
    main()

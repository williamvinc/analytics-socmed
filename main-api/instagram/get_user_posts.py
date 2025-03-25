import pandas as pd
import requests
import json
import sys
import os
from utils.mysql_connector import connect_to_db, save_dataframe_to_db, connect_to_sqlalchemy
from dependencies import *
import datetime

from dotenv import load_dotenv
load_dotenv()

mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")
table_name = "instagram_post"
instagram_user_key = os.getenv("INSTAGRAM_USER_POSTS_KEY")
instagram_user_url = os.getenv("INSTAGRAM_USER_URL")

if __name__ == "__main__":
    ########################## Start Requesting Data ##########################

    # API FROM https://rapidapi.com/omarmhaimdat/api/instagram230

    url = instagram_user_url

    querystring = {"username":"cpcm.id", "count": 50}

    headers = {
    	"x-rapidapi-key": instagram_user_key,
    	"x-rapidapi-host": "instagram230.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response = response.json()

    print("Saving to JSON")

    json_file_path = "main-api/instagram/dependencies/cpcm_data.json"

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {json_file_path}")

    except Exception as e:
        print(f"Error saving to JSON: {e}")

    ########################## Stop ##########################    
        

    ################## USE OFFLINE DATA ##################

    # with open("main-api/instagram/dependencies/cpcm_data.json") as f:
    #     response = json.load(f)
        
    ################## DUMMY DATA ##################

    data = []

    for index, item in enumerate(response['items']):
        try:
            pk = item['pk']
            play_count = item.get('play_count', 0)
            comment_count = item['comment_count']
            like_count = item['like_count']
            video_duration = item.get('video_duration', 0)
            crawl_time = pd.Timestamp.now()
            post_timestamp_unix = item['taken_at']
            post_timestamp = pd.to_datetime(post_timestamp_unix, unit='s')
            caption = item.get('caption', {}).get('text', '')
            username = item['user']['username']

            item_data = {
                'pk': pk,
                'username': username,
                'caption': caption,
                'post_timestamp': post_timestamp,
                'comment_count': comment_count,
                'like_count': like_count,
                'play_count': play_count,
                'video_duration': video_duration,
                'crawl_time': crawl_time
            }

            data.append(item_data)

            print(f"Processed index: {index}")

        except KeyError as e:
            print(f"Error: Key not found in data: {e}")
        except Exception as e:
            print(f"General Error: {e}")

    df = pd.DataFrame(data)
    print(df)

    db_connection = connect_to_db()
    if db_connection:
        table_name = "instagram_post"
        save_dataframe_to_db(df, db_connection, table_name)
        db_connection.close()
        print("Data saved to DB")
    else:
        print("Connection to DB failed")
    

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
table_name = "youtube_posts"
youtube_user_key = os.getenv("YOUTUBE_KEY")
youtube_videos_url = os.getenv("YOUTUBE_VIDEO_URL")

if __name__ == "__main__":
    ########################## Start Requesting Data ##########################

    # https://rapidapi.com/omarmhaimdat/api/youtube-v2 200 req / month

    url = "https://youtube-v2.p.rapidapi.com/channel/videos"

    querystring = {"channel_id": "UCYgy7wucmLwYwL2b_Z0h9OQ"}

    headers = {
    	"x-rapidapi-key": youtube_user_key,
    	"x-rapidapi-host": "youtube-v2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response)
    response = response.json()

    print("Saving to JSON")

    json_file_path = "main-api/youtube/dependencies/youtube_cpcm_posts_data.json"

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {json_file_path}")

    except Exception as e:
        print(f"Error saving to JSON: {e}")

    ########################## Stop ##########################    
        

    ################## USE OFFLINE DATA ##################

    # with open("main-api/youtube/dependencies/youtube_cpcm_posts_data.json") as f:
    #     response = json.load(f)
        
    ################## DUMMY DATA ##################

    data = []

    for index, item in enumerate(response['videos']):
        try:
            video_id = item['video_id']
            title = item.get('title', 'null')
            number_of_views = item['number_of_views']
            video_length = item['video_length']
            description = item['description']
            published_time = item['published_time']
            is_live_content = item.get('is_live_content', 'null')
            crawl_time = pd.Timestamp.now()

            item_data = {
                'video_id': video_id,
                'title': title,
                'number_of_views': number_of_views,
                'video_length': video_length,
                'description': description,
                'published_time': published_time,
                'is_live_content': is_live_content,
                'crawl_time': crawl_time,
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
        table_name = table_name
        save_dataframe_to_db(df, db_connection, table_name)
        db_connection.close()
        print("Data saved to DB")
    else:
        print("Connection to DB failed")
    

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

table_name = "youtube_user"
youtube_user_key = os.getenv("YOUTUBE_KEY")
youtube_user_url = os.getenv("YOUTUBE_URL")

if __name__ == "__main__":
    ########################## Start Requesting Data ##########################

    # https://rapidapi.com/omarmhaimdat/api/youtube-v2 200 req / month

    url = youtube_user_url

    querystring = {"channel_id":"UCYgy7wucmLwYwL2b_Z0h9OQ"}

    headers = {
    	"x-rapidapi-key": youtube_user_key,
    	"x-rapidapi-host": "youtube-v2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response)
    response = response.json()

    print("Saving to JSON")

    json_file_path = "/root/socmed_api/analytics-socmed/main-api/youtube/dependencies/youtube_cpcm_data.json"

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {json_file_path}")

    except Exception as e:
        print(f"Error saving to JSON: {e}")

    ########################## Stop ##########################    
        

    ################## USE OFFLINE DATA ##################

    # with open("main-api/youtube/dependencies/youtube_cpcm_data.json") as f:
    #     response = json.load(f)
        
    ################## DUMMY DATA ##################
    
    process_subscriber_count = lambda x: int(x.split(" ")[0].replace(",", ""))
    process_view_count = lambda x: int(x.replace(",", "").split(" ")[0])
    process_creation_date = lambda x: pd.to_datetime(x.replace("Joined ", ""))
    process_video_count = lambda x: int(x.split(" ")[0])

    data = []

    crawl_time = datetime.datetime.now()
    channel_id = response["channel_id"]
    title = response["title"]
    subscriber_count = process_subscriber_count(response["subscriber_count"])
    view_count = process_view_count(response["view_count"])
    creation_date = process_creation_date(response["creation_date"])
    video_count = process_video_count(response["video_count"])
    

    item_data = {
        'crawl_time': crawl_time,
        'channel_id': channel_id,
        'title': title,
        'subscriber_count': subscriber_count,
        'view_count': view_count,
        'creation_date': creation_date,
        'video_count': video_count
    }

    data.append(item_data)


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


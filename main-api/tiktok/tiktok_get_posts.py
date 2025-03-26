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
table_name = "tiktok_posts"
tiktok_user_key = os.getenv("TIKTOK_USER_KEY")
tiktok_user_url = os.getenv("TIKTOK_USER_URL")

if __name__ == "__main__":
    ########################## Start Requesting Data ##########################

    # https://rapidapi.com/scraptik-api-scraptik-api-default/api/scraptik 50 req / month

    url = tiktok_user_url

    querystring = {"user_id":"7216354296395629573", "count":"50"}

    headers = {
    	"x-rapidapi-key": tiktok_user_key,
    	"x-rapidapi-host": "scraptik.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response)
    response = response.json()

    print("Saving to JSON")

    json_file_path = "/root/socmed_api/analytics-socmed/main-api/tiktok/dependencies/tiktok_cpcm_posts_data.json"

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {json_file_path}")

    except Exception as e:
        print(f"Error saving to JSON: {e}")

    ########################## Stop ##########################    
        

    ################## USE OFFLINE DATA ##################

    # with open("main-api/tiktok/dependencies/tiktok_cpcm_posts_data.json") as f:
    #     response = json.load(f)
        
    ################## DUMMY DATA ##################

    data = []

    for index, item in enumerate(response['aweme_list']):
        try:
            create_time_unix = item['create_time']
            create_time = pd.to_datetime(create_time_unix, unit='s')
            is_hash_tag = item.get('is_hash_tag', 0)
            description = item.get('desc', 'null')
            aweme_id = item['statistics'].get("aweme_id", "id")
            comment_count = item['statistics'].get("comment_count", 0)
            digg_count = item['statistics'].get("digg_count", 0)
            download_count = item['statistics'].get("download_count", 0)
            forward_count = item['statistics'].get("forward_count", 0)
            lose_comment_count = item['statistics'].get("lose_comment_count", 0)
            lose_count = item['statistics'].get("lose_count", 0)
            play_count = item['statistics'].get("play_count", 0)
            share_count = item['statistics'].get("share_count", 0)
            whatsapp_share_count = item['statistics'].get("whatsapp_share_count", 0)
            crawl_time = pd.Timestamp.now()

            item_data = {
                'create_time': create_time,
                'is_hash_tag': is_hash_tag,
                'description' : description,
                'aweme_id': aweme_id,
                'comment_count': comment_count,
                'digg_count': digg_count,
                'download_count': download_count,
                'forward_count': forward_count,
                'lose_comment_count': lose_comment_count,
                'lose_count': lose_count,
                'play_count': play_count,
                'share_count': share_count,
                'whatsapp_share_count': whatsapp_share_count,
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
        table_name = "tiktok_posts"
        save_dataframe_to_db(df, db_connection, table_name)
        db_connection.close()
        print("Data saved to DB")
    else:
        print("Connection to DB failed")
    

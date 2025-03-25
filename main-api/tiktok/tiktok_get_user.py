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
table_name = "tiktok_user"
tiktok_user_key = os.getenv("TIKTOK_USER_KEY")
tiktok_user_url = os.getenv("TIKTOK_USER_URL")

if __name__ == "__main__":
    ########################## Start Requesting Data ##########################

    ## https://rapidapi.com/scraptik-api-scraptik-api-default/api/scraptik/

    url = tiktok_user_url

    querystring = {"user_id":"7216354296395629573"}

    headers = {
    	"x-rapidapi-key": tiktok_user_key,
    	"x-rapidapi-host": "scraptik.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response)
    response = response.json()

    print("Saving to JSON")

    json_file_path = "main-api/tiktok/dependencies/tiktok_cpcm_data.json"

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {json_file_path}")

    except Exception as e:
        print(f"Error saving to JSON: {e}")

    ########################## Stop ##########################    
        

    ################## USE OFFLINE DATA ##################

    # with open("main-api/tiktok/dependencies/tiktok_cpcm_data.json") as f:
    #     response = json.load(f)
        
    ################## DUMMY DATA ##################

    data = []

    crawl_time = datetime.datetime.now()
    follower_count = response['aweme_list'][0]['author']['follower_count']
    following_count = response['aweme_list'][0]['author']['following_count']
    signature = response['aweme_list'][0]['author']['signature']
    uid = response['aweme_list'][0]['author']['uid']
    bio_url = response['aweme_list'][0]['author']['custom_verify']
    nickname = response['aweme_list'][0]['author']['nickname']
    unique_id = response['aweme_list'][0]['author']['unique_id']
    

    item_data = {
        'crawl_time': crawl_time,
        'following_count': following_count,
        'follower_count': follower_count,
        'signature': signature,
        'uid': uid,
        'bio_url': bio_url,
        'nickname': nickname,
        'unique_id': unique_id
    }

    data.append(item_data)


    df = pd.DataFrame(data)
    print(df)

    db_connection = connect_to_db()
    if db_connection:
        table_name = "tiktok_user"
        save_dataframe_to_db(df, db_connection, table_name)
        db_connection.close()
        print("Data saved to DB")
    else:
        print("Connection to DB failed")


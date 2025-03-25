import pandas as pd
import requests
import json
import sys
import os
from utils.mysql_connector import connect_to_db, save_dataframe_to_db

from dotenv import load_dotenv
load_dotenv()

instagram_user_data_url = os.getenv("INSTAGRAM_INFO_URL")
instagram_user_data_key = os.getenv("INSTAGRAM_INFO_KEY")

if __name__ == "__main__":
    ##API FROM https://rapidapi.com/rocketapi/api/rocketapi-for-developers

    url = instagram_user_data_url

    payload = { "username": "cpcm.id" }
    headers = {
    	"x-rapidapi-key": instagram_user_data_key,
    	"x-rapidapi-host": "rocketapi-for-developers.p.rapidapi.com",
    	"Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    print("Saving to JSON")

    json_file_path = "main-api/instagram/dependencies/cpcm_instagram_info.json"

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {json_file_path}")

    except Exception as e:
        print(f"Error saving to JSON: {e}")

    ################## USE OFFLINE DATA ##################
    # with open("main-api/instagram/dependencies/cpcm_instagram_info.json") as f:
    #     data = json.load(f)
    ################## OFFLIEN DATA ##################


    try:
        username = data['response']['body']['data']['user']['username']
        biography = data['response']['body']['data']['user']['biography']
        edge_follow_count = data['response']['body']['data']['user']['edge_follow']['count']
        edge_followed_by_count = data['response']['body']['data']['user']['edge_followed_by']['count']
        crawl_time = pd.Timestamp.now()

        print(f"Username: {username}")
        print(f"Biography: {biography}")
        print(f"Edge Follow Count: {edge_follow_count}")
        print(f"Edge Followed By Count: {edge_followed_by_count}")
        print(f"Crawl Time: {crawl_time}")

        df = pd.DataFrame({
            'username': [username],
            'biography': [biography],
            'edge_follow_count': [edge_follow_count],
            'edge_followed_by_count': [edge_followed_by_count],
            'crawl_time': [crawl_time]
        })

        db_connection = connect_to_db()
        if db_connection:
            save_dataframe_to_db(df, db_connection, 'instagram_user_data')
            db_connection.close()
            print("Data saved to DB")
        else:
            print("Connection to DB failed")

    except KeyError as e:
        print(f"Error: Key not found in data: {e}")

    except Exception as e:
        print(f"General Error: {e}")



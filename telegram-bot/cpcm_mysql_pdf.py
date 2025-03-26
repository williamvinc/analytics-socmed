import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import fitz
import textwrap

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": os.getenv("MYSQL_PORT"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

output_folder = "/root/socmed_api/analytics-socmed/telegram-bot/data"
os.makedirs(output_folder, exist_ok=True)

db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

def fetch_latest_data(table):
    query = f"""
    SELECT * FROM {table} 
    WHERE crawl_time = (SELECT MAX(crawl_time) FROM {table})
    """
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)

def save_to_pdf(filename, data_dict, title):
    doc = fitz.open()
    page = doc.new_page()
    font_size = 10
    y_position = 50
    line_spacing = 15
    max_width = 80
    wrapper = textwrap.TextWrapper(width=max_width)

    page.insert_text((50, y_position), title, fontsize=font_size + 2)
    y_position += line_spacing * 2

    for section_title, df in data_dict.items():
        page.insert_text((50, y_position), section_title, fontsize=font_size + 1)
        y_position += line_spacing
        
        headers = " | ".join(df.columns)
        page.insert_text((50, y_position), headers, fontsize=font_size)
        y_position += line_spacing
        
        for i in range(len(df)):
            row_text = " | ".join(str(df.iloc[i, j]) for j in range(len(df.columns)))
            wrapped_lines = wrapper.wrap(row_text)
            
            for line in wrapped_lines:
                page.insert_text((50, y_position), line, fontsize=font_size)
                y_position += line_spacing
                
                if y_position > 750:
                    page = doc.new_page()
                    y_position = 50
        
            y_position += line_spacing
        y_position += line_spacing
    
    file_path = os.path.join(output_folder, filename)
    doc.save(file_path)
    doc.close()
    print(f"Saved: {file_path}")

data_instagram = {
    "Instagram User Data": fetch_latest_data("instagram_user_data"),
    "Instagram Post Data": fetch_latest_data("instagram_post")
}
data_tiktok = {
    "TikTok User Data": fetch_latest_data("tiktok_user"),
    "TikTok Post Data": fetch_latest_data("tiktok_posts")
}
data_youtube = {
    "YouTube User Data": fetch_latest_data("youtube_user"),
    "YouTube Post Data": fetch_latest_data("youtube_posts")
}

save_to_pdf("instagram_data.pdf", data_instagram, "Instagram Data")
save_to_pdf("tiktok_data.pdf", data_tiktok, "TikTok Data")
save_to_pdf("youtube_data.pdf", data_youtube, "YouTube Data")

db.close()
cursor.close()

print("Export selesai!")

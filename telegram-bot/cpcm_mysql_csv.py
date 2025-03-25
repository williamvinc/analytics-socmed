import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": os.getenv("MYSQL_PORT"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

tables = [
    "instagram_post", "instagram_user_data",
    "tiktok_posts", "tiktok_user",
    "youtube_posts", "youtube_user"
]

output_folder = "telegram-bot/data"
os.makedirs(output_folder, exist_ok=True)

db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

def save_to_csv(table_name, df):
    file_path = os.path.join(output_folder, f"{table_name}.csv")
    df.to_csv(file_path, index=False, sep=';')
    print(f"Saved: {file_path}")

for table in tables:
    cursor.execute(f"SELECT * FROM {table}")
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    
    df = pd.DataFrame(data, columns=columns)
    save_to_csv(table, df)

db.close()
cursor.close()

print("Export selesai!")
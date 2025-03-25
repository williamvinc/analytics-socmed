import google.generativeai as genai
from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat
from dotenv import load_dotenv
from prompts.cpcm_prompts import system_prompts
import os
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "dbname": os.getenv("MYSQL_DATABASE"),
    "port": int(os.getenv("MYSQL_PORT"))
}

genai.configure(api_key=GOOGLE_API_KEY)

class MyVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        GoogleGeminiChat.__init__(self, config={'api_key': GOOGLE_API_KEY, 'model': GEMINI_MODEL})

vn = MyVanna()

vn.connect_to_mysql(**config)


## ======================================== Train Instagram Data ========================================

df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('instagram_post', 'instagram_user_data', 'tiktok_posts', 'tiktok_user', 'youtube_posts', 'youtube_user');")
plan = vn.get_training_plan_generic(df_information_schema)
plan
vn.train(plan=plan)

vn.train(documentation="All tables is about social media such youtube, tiktok and instagram. Each social media consist of 2 tables, one for user data and one for post data. The user data table contains information about the user such as followers, following, subscriber and etc. The post data table contains information about the post such as play count, like count, and etc.")

vn.train(ddl="""
    CREATE TABLE IF not exists instagram_post (
        pk varchar(50) PRIMARY KEY,
        play_count BIGINT,
        comment_count INTEGER,
        like_count INTEGER,
        video_duration FLOAT,
        crawl_time TIMESTAMP,
        post_timestamp TIMESTAMP,
        caption TEXT,
        username varchar(50)
    );

""")

vn.train(ddl="""
    CREATE TABLE instagram_user_data (
        username varchar(50) PRIMARY KEY,
        biography varchar(250),
        edge_follow_count integer,
        edge_followed_by_count integer,
        crawl_time TIMESTAMP
    )

""")

vn.train(
    question="Berapa jumlah rata-rata pengikut (followers) pengguna Instagram?",
    sql="SELECT AVG(edge_followed_by_count) FROM instagram_user_data;"
)

vn.train(
    question="Siapa pengguna Instagram dengan jumlah pengikut terbanyak?",
    sql="SELECT username, edge_followed_by_count FROM instagram_user_data ORDER BY edge_followed_by_count DESC LIMIT 1;"
)

vn.train(
    question="Berapa rata-rata jumlah akun yang diikuti oleh pengguna Instagram?",
    sql="SELECT AVG(edge_follow_count) FROM instagram_user_data;"
)

vn.train(
    question="Berapa rata-rata jumlah like per post di Instagram?",
    sql="SELECT AVG(like_count) FROM instagram_post;"
)

vn.train(
    question="Post mana yang memiliki jumlah like terbanyak?",
    sql="SELECT pk, like_count FROM instagram_post ORDER BY like_count DESC LIMIT 1;"
)

vn.train(
    question="Berapa total jumlah komentar di semua post Instagram?",
    sql="SELECT SUM(comment_count) FROM instagram_post;"
)

vn.train(
    question="Berapa rata-rata jumlah komentar per post di Instagram?",
    sql="SELECT AVG(comment_count) FROM instagram_post;"
)

vn.train(
    question="Berapa rata-rata durasi video di post Instagram?",
    sql="SELECT AVG(video_duration) FROM instagram_post WHERE video_duration IS NOT NULL;"
)

vn.train(
    question="Berapa rata-rata jumlah tayangan (play count) per post di Instagram?",
    sql="SELECT AVG(play_count) FROM instagram_post WHERE play_count IS NOT NULL;"
)

vn.train(
    question="Berapa total jumlah tayangan (play count) di semua post Instagram dalam 30 hari terakhir?",
    sql="SELECT SUM(play_count) FROM instagram_post WHERE crawl_time >= NOW() - INTERVAL 30 DAY AND play_count IS NOT NULL;"
)

vn.train(
    question="Berapa jumlah rata-rata pengikut pengguna Instagram dalam 7 hari terakhir?",
    sql="SELECT AVG(edge_followed_by_count) FROM instagram_user_data WHERE crawl_time >= NOW() - INTERVAL 7 DAY;"
)

vn.train(
    question="Siapa pengguna Instagram dengan pertumbuhan pengikut terbanyak dalam 30 hari terakhir?",
    sql="""
    SELECT username, (MAX(edge_followed_by_count) - MIN(edge_followed_by_count)) AS follower_growth
    FROM instagram_user_data
    WHERE crawl_time >= NOW() - INTERVAL 30 DAY
    GROUP BY username
    ORDER BY follower_growth DESC
    LIMIT 1;
    """
)

vn.train(
    question="Post mana yang memiliki jumlah komentar terbanyak dalam 7 hari terakhir?",
    sql="SELECT pk, comment_count FROM instagram_post WHERE crawl_time >= NOW() - INTERVAL 7 DAY ORDER BY comment_count DESC LIMIT 1;"
)

vn.train(
    question="Berapa rata-rata jumlah like per post dalam 7 hari terakhir?",
    sql="SELECT AVG(like_count) FROM instagram_post WHERE crawl_time >= NOW() - INTERVAL 7 DAY;"
)

## ======================================== End of Train Instagram Data ========================================

## ======================================== Train TikTok Data ========================================

vn.train(ddl="""
    CREATE TABLE tiktok_user (
        crawl_time TIMESTAMP,
        following_count INTEGER,
        follower_count INTEGER,
        signature VARCHAR(100),
        uid VARCHAR(100) PRIMARY KEY,
        bio_url VARCHAR(100),
        nickname VARCHAR(100),
        unique_id VARCHAR(100)
    )
""")

vn.train(ddl="""
    CREATE TABLE tiktok_posts (
        create_time TIMESTAMP,
        "desc" TEXT,
        is_hash_tag int,
        aweme_id BIGINT PRIMARY KEY,
        comment_count INTEGER,
        digg_count BIGINT,
        download_count INTEGER,
        forward_count INTEGER,
        lose_comment_count INTEGER,
        lose_count INTEGER,
        play_count BIGINT,
        share_count INTEGER,
        whatsapp_share_count INTEGER,
        crawl_time TIMESTAMP
    )
""")

vn.train(
    question="Berapa jumlah rata-rata follower pengguna TikTok dalam 7 hari terakhir?",
    sql="SELECT AVG(follower_count) FROM tiktok_user WHERE crawl_time >= NOW() - INTERVAL 7 DAY;"
)

vn.train(
    question="Siapa pengguna TikTok dengan pertumbuhan follower terbanyak dalam 30 hari terakhir?",
    sql="""
    SELECT nickname, (MAX(follower_count) - MIN(follower_count)) AS follower_growth
    FROM tiktok_user 
    WHERE crawl_time >= NOW() - INTERVAL 30 DAY
    GROUP BY nickname
    ORDER BY follower_growth DESC
    LIMIT 1;
    """
)

vn.train(
    question="Berapa rata-rata jumlah play count per post dalam 7 hari terakhir?",
    sql="SELECT AVG(play_count) FROM tiktok_posts WHERE crawl_time >= NOW() - INTERVAL 7 DAY;"
)

vn.train(
    question="Berapa total jumlah like (digg_count) di semua post dalam 30 hari terakhir?",
    sql="SELECT SUM(digg_count) FROM tiktok_posts WHERE crawl_time >= NOW() - INTERVAL 30 DAY;"
)

vn.train(
    question="Post mana yang memiliki jumlah play count terbanyak dalam 7 hari terakhir?",
    sql="SELECT aweme_id, play_count FROM tiktok_posts WHERE crawl_time >= NOW() - INTERVAL 7 DAY ORDER BY play_count DESC LIMIT 1;"
)

vn.train(
    question="Berapa rata-rata jumlah komentar per post dalam 30 hari terakhir?",
    sql="SELECT AVG(comment_count) FROM tiktok_posts WHERE crawl_time >= NOW() - INTERVAL 30 DAY;"
)

vn.train(
    question="Berapa total jumlah share di semua post TikTok dalam 7 hari terakhir?",
    sql="SELECT SUM(share_count) FROM tiktok_posts WHERE crawl_time >= NOW() - INTERVAL 7 DAY;"
)

vn.train(
    question="Berapa total jumlah post yang telah diunduh oleh pengguna dalam 30 hari terakhir?",
    sql="SELECT SUM(download_count) FROM tiktok_posts WHERE crawl_time >= NOW() - INTERVAL 30 DAY;"
)



## ======================================== End of Train TikTok Data ========================================

## ======================================== Train Youtube Data ========================================

vn.train(ddl="""
    CREATE TABLE youtube_user (
        channel_id VARCHAR(50) PRIMARY KEY,
        title VARCHAR(100),
        subscriber_count INTEGER,
        view_count BIGINT,
        creation_date VARCHAR(50),
        video_count INTEGER,
        crawl_time TIMESTAMP
    )
""")

vn.train(ddl="""
    CREATE TABLE youtube_posts (
        video_id VARCHAR(50) PRIMARY KEY,
        title VARCHAR(100),
        number_of_views BIGINT,
        video_length VARCHAR(50),
        description TEXT,
        published_time VARCHAR(50),
        is_live_content VARCHAR(10),
        crawl_time TIMESTAMP
    )
""")

vn.train(
    question="Berapa jumlah rata-rata subscriber channel YouTube?",
    sql="SELECT AVG(subscriber_count) FROM youtube_user;"
)

vn.train(
    question="Siapa channel YouTube dengan jumlah subscriber terbanyak?",
    sql="SELECT title, subscriber_count FROM youtube_user ORDER BY subscriber_count DESC LIMIT 1;"
)

vn.train(
    question="Berapa rata-rata jumlah total view per channel YouTube?",
    sql="SELECT AVG(view_count) FROM youtube_user;"
)

vn.train(
    question="Berapa rata-rata jumlah video per channel YouTube?",
    sql="SELECT AVG(video_count) FROM youtube_user;"
)

vn.train(
    question="Siapa channel YouTube dengan total jumlah view terbanyak?",
    sql="SELECT title, view_count FROM youtube_user ORDER BY view_count DESC LIMIT 1;"
)

vn.train(
    question="Berapa rata-rata jumlah penayangan per video YouTube?",
    sql="SELECT AVG(number_of_views) FROM youtube_posts;"
)

vn.train(
    question="Video mana yang memiliki jumlah penayangan terbanyak?",
    sql="SELECT title, number_of_views FROM youtube_posts ORDER BY number_of_views DESC LIMIT 1;"
)

vn.train(
    question="Berapa rata-rata jumlah penayangan per video YouTube dalam 7 hari terakhir?",
    sql="SELECT AVG(number_of_views) FROM youtube_posts WHERE crawl_time >= NOW() - INTERVAL 7 DAY;"
)

vn.train(
    question="Video mana yang memiliki jumlah penayangan terbanyak dalam 7 hari terakhir?",
    sql="SELECT title, number_of_views FROM youtube_posts WHERE crawl_time >= NOW() - INTERVAL 7 DAY ORDER BY number_of_views DESC LIMIT 1;"
)

vn.train(
    question="Berapa rata-rata jumlah subscriber channel YouTube dalam 30 hari terakhir?",
    sql="SELECT AVG(subscriber_count) FROM youtube_user WHERE crawl_time >= NOW() - INTERVAL 30 DAY;"
)

vn.train(
    question="Siapa channel YouTube dengan pertumbuhan subscriber terbanyak dalam 30 hari terakhir?",
    sql="""
    SELECT title, (MAX(subscriber_count) - MIN(subscriber_count)) AS subscriber_growth
    FROM youtube_user
    WHERE crawl_time >= NOW() - INTERVAL 30 DAY
    GROUP BY title
    ORDER BY subscriber_growth DESC
    LIMIT 1;
    """
)

vn.train(
    question="Berapa rata-rata jumlah video per channel dalam 7 hari terakhir?",
    sql="SELECT AVG(video_count) FROM youtube_user WHERE crawl_time >= NOW() - INTERVAL 7 DAY;"
)

vn.train(
    question="Video mana yang merupakan live content?",
    sql="SELECT title FROM youtube_posts WHERE is_live_content = 'true';"
)

vn.train(
    question="Video mana yang merupakan live content dalam 30 hari terakhir?",
    sql="SELECT title FROM youtube_posts WHERE is_live_content = 'true' AND crawl_time >= NOW() - INTERVAL 30 DAY;"
)


## ======================================== End of Train Youtube Data ========================================

training_data = vn.get_training_data()
print(training_data)

questions = input("Masukkan pertanyaan: ")

result = vn.ask(question=questions, allow_llm_to_see_data=True, print_results=False)

model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=f"Kamu diberikan pertanyaan: {questions}, dan kamu mendapatkan sebuah return dari query. Tolong berikan jawaban yang comprehensif berdasarkan jawaban dari query {result}")

try:
    response = model.generate_content(questions)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
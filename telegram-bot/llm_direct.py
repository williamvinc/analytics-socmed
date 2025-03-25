import os
import pandas as pd
import google.generativeai as genai
from langchain.document_loaders import CSVLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
import os
from dotenv import load_dotenv
load_dotenv()

DATA_PATH = "telegram-bot/data/"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

genai.configure(api_key=GOOGLE_API_KEY)

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

loader = CSVLoader("data/tiktok-posts.csv", encoding="windows-1252")
documents = loader.load()

db = Chroma.from_documents(documents, embedding_function)
query = "description mana yang memiliki share count terbanyak"
docs = db.similarity_search(query)
print(docs[0].page_content)



# prompt = f"""
# Kamu adalah sebuah chat bot dan memiliki data video TikTok, berikut adalah deskripsi dan jumlah view dari video tersebut:

# {df_tiktok[["description", "play_count"]].to_string(index=False)}

# jawab dengan singkat sesuai pertanyaan: {query} 
# """

# model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=prompt)
# response = model.generate_content(prompt)

# print(response.text)


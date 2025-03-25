import chromadb
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# setting the environment

DATA_PATH = r"telegram-bot/data"
CHROMA_PATH = r"telegram-bot/chroma_db"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="cpcm_social_media")


# user_query = input("berapa followers instagram saya?")
user_query = "berapa followers instagram saya?"

results = collection.query(
    query_texts=[user_query],
    n_results=1
)

print(results['documents'])
print(results['metadatas'])

genai.configure(api_key=GOOGLE_API_KEY)


system_prompt = """
Kamu adalah seorang data analyst. Kamu akan diberikan data yang saya kumpulkan.
Berikut adalah data yang kamu miliki:
--------------------
The data:
"""+str(results['documents'])+"""
"""

model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)

#print(system_prompt)

def handle_response(text: str):
    processed: str = text.lower()
    try:
        response = model.generate_content(processed)
        return(response.text)
    except Exception as e:
        return(f"Error: {e}")

print("\n\n---------------------\n\n")
print(handle_response("apa signature saya di tiktok?"))
import chromadb

CHROMA_PATH = r"telegram-bot/chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="cpcm_social_media")

query = "berapa banyak followers saya di instagram?"

results = collection.query(
    query_texts=[query],
    n_results=50
)
print(results['metadatas'])
print(results['documents'])
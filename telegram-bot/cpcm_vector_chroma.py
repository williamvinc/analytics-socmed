from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import os

# setting the environment
DATA_PATH = r"telegram-bot/data/"
CHROMA_PATH = r"telegram-bot/chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="cpcm_social_media")

# loading CSV documents
csv_files = [f for f in os.listdir(DATA_PATH) if f.endswith(".csv")]

raw_documents = []
for file in csv_files:
    loader = CSVLoader(file_path=os.path.join(DATA_PATH, file))
    raw_documents.extend(loader.load())

# splitting the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

# preparing data to be added in ChromaDB
documents = []
metadata = []
ids = []

for i, chunk in enumerate(chunks):
    documents.append(chunk.page_content)
    ids.append(f"ID{i}")
    metadata.append(chunk.metadata)

# adding to ChromaDB
collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)

print("Data berhasil dimasukkan ke ChromaDB!")

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "db")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

EMBEDDING_MODEL = "models/gemini-embedding-2"
LLM_MODEL = "gemini-1.5-flash"

COLLECTION_NAME = "document_knowledge_base"

MAX_HISTORY_TURNS = 5
DISTANCE_THRESHOLD = 0.8

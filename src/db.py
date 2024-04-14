from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
database = client["init_db"]
embeddings_db = client["embeddings"]
users_collection = database["users"]
files_collection = database["files"]
embeddings_collection = embeddings_db["embeddings"]



from pymongo import MongoClient

# initialize MongoDB python client
client = MongoClient(os.getenv('MONGO_URL'))

DB_NAME = "embeddings"
COLLECTION_NAME = "embeddings"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
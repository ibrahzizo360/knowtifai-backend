from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
database = client["init_db"]
users_collection = database["users"]
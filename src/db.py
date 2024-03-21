from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
database = client["init_db"]
user_collection = database["users"]
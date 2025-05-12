import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os

MONGODB_USER = os.getenv("MONGODB_USER", "nimbus")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "nimbus123")
MONGODB_HOST = "localhost"  # Use "localhost" or "mongo" based on your setup
# MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")  # Use "localhost" or "mongo" based on your setup
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_DB = os.getenv("MONGODB_DB", "nimbus")

def get_db_client():
    """Create and return a reusable MongoDB client."""
    uri = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}?authSource=admin"
    # print("Connecting to MongoDB...", uri)
    client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
    return client

async def ping_server():
    """Ping the MongoDB server to test the connection."""
    client = get_db_client()
    try:
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

# Ensure the function is properly awaited
if __name__ == "__main__":
    asyncio.run(ping_server())

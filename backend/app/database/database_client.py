from pymongo import MongoClient
from ..config.settings import settings

# singleton client -> initialize to None
_client: MongoClient | None = None
_db = None


def get_client():
    global _client, _db
    if _client is None:
        _client = MongoClient(
            settings.MONGODB_URL,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
        )
    _db = _client[settings.MONGODB_DB_NAME]
    # verify connection
    _client.admin.command('ping')
    print('MongoDB connected successfully (synchronous)')
    return _client


def get_db():
    get_client()
    return _db


def close_mongo_connection():
    global _client
    if _client:
        _client.close()
        print('MongoDB connection closed successfully')

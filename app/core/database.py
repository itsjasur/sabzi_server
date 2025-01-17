import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure

DATABASE_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")


class Database:
    def __init__(self, url: str = DATABASE_URL):
        self.url = url
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                self.url,
                minPoolSize=10,
                maxPoolSize=100,
                serverSelectionTimeoutMS=5000,
            )
            self.db = self.client["sabzi_db"]
            # await self.client.admin.command("ping")
        except ConnectionFailure as e:
            # logger.error(f"Database connection failed: {e}")
            raise

    async def close(self):
        if self.client:
            self.client.close()

    @property
    def users(self) -> AsyncIOMotorCollection:
        if self.db is None:
            raise ConnectionError("Database not connected")
        return self.db["users"]

    @property
    def verifications(self) -> AsyncIOMotorCollection:
        if self.db is None:
            raise ConnectionError("Database not connected")
        return self.db["verifications"]


database = Database()


async def get_database() -> Database:
    return database

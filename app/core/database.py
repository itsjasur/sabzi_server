from typing import Optional
from annotated_types import T
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from app.core.config import core_settings
from pymongo.errors import ConnectionFailure


class Database:

    client: AsyncIOMotorClient = None
    database: AsyncIOMotorClient = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
            # await self.client.admin.command("ping")
            self.database = self.client["sabzi_db"]

        except ConnectionFailure as e:
            raise

    async def close(self):
        if self.client is not None:
            self.client.close()

    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        if self.database is not None:
            return self.database[collection_name]
        else:
            raise ConnectionError("Database not connected")


DB = Database()

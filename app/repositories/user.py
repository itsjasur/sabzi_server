from datetime import datetime, timedelta, timezone
from bson import ObjectId
from fastapi import Depends, HTTPException

from app.core.database import Database, database, get_database
from app.models.user import UserStatus, Verification, User


class UserRepository:
    def __init__(self, database: Database = Depends(get_database)):
        self.database = database
        self.collection = database.users

    async def get_user_by_id(self, id: str) -> User | None:
        doc = await self.collection.find_one({"_id": ObjectId(oid=id)})
        return doc

    async def get_user_by_phone_number(self, phone_number: str) -> User | None:
        doc = await self.collection.find_one({"phone_number": phone_number})

        if not doc:
            return None

        user = User(**doc)
        return user


class VerificationRepository:
    def __init__(self, database: Database = Depends(get_database)):
        self.database = database
        self.collection = database.verifications

    async def add_verification(self, verification: Verification) -> str:
        dict = verification.model_dump(by_alias=True)
        result = await self.collection.insert_one(dict)
        return str(result.inserted_id)

    async def check_verification_limit(self, phone_number: str) -> bool:
        five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)

        count = await self.collection.count_documents(
            {
                "phone_number": phone_number,
                "created_date": {"$gte": five_minutes_ago},
            }
        )

        return count >= 5

    async def get_verification_by_id(self, id: str) -> Verification:
        doc = await self.collection.find_one({"_id": ObjectId(oid=id)})
        if not doc:
            raise HTTPException(status_code=404, detail=f"INVALID_OR_EXPIRED_TOKEN")
        return Verification(**doc)

    async def decrement_attempts(self, id: ObjectId) -> bool:
        result = await self.collection.update_one(
            {"_id": id},
            {"$inc": {"attempts": -1}},
        )

    async def get_verification_by_token(self, token: str) -> Verification:
        doc = await self.collection.find_one({"token": token})
        if not doc:
            raise HTTPException(status_code=404, detail=f"INVALID_REQUEST")
            # return None
        return Verification(**doc)

    async def update_verification(self, verification: Verification) -> bool:
        result = await self.collection.update_one(
            {"_id": verification.id},
            {"$set": verification.model_dump(exclude={"id"})},
        )

    async def get_random_usernames(self) -> list:
        result = await database.users.aggregate(
            [
                # Stage 1: filters for active users only
                {"$match": {"status": UserStatus.verified.value}},
                # Stage 2: get random sample
                {"$sample": {"size": 20}},
                # Stage 3: project only the username field
                {"$project": {"username": 1, "_id": 0}},
            ]
        ).to_list()

        return result

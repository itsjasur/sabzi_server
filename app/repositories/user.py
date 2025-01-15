from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException
from app.core.database import DB
from app.models.user import UserCreate, UserResponse


class UserRepository:
    @staticmethod
    async def get_user_by_id(user_id: str) -> UserResponse:

        collection = DB.get_collection("users")
        doc = await collection.find_one({"_id": ObjectId(oid=user_id)})

        user = UserResponse(**doc, id=doc["_id"])

        return user

    @staticmethod
    async def create_user(user: UserCreate) -> ObjectId:

        user_dict = user.model_dump(by_alias=True)

        collection = DB.get_collection("users")
        result = await collection.insert_one(user_dict)

        print(result)

        return result.inserted_id

    @staticmethod
    async def get_users() -> list[UserResponse]:
        users: list[UserResponse] = []

        collection = DB.get_collection("users")
        documents = await collection.find({}).to_list()

        users = [UserResponse(**doc, id=doc["_id"]) for doc in documents]

        return users


#
#
#
#
# @staticmethod
# async def get_user(user_id: str) -> Optional[User]:
#     user = await DB.database["users"].find_one({"_id": ObjectId(user_id)})
#     return User(**user) if user else None

# @staticmethod
# async def get_users(skip: int = 0, limit: int = 100) -> list[User]:
#     users = []
#     cursor = DB.database["users"].find().skip(skip).limit(limit)
#     async for document in cursor:
#         users.append(User(**document))
#     return users

# @staticmethod
# async def update_user(user_id: str, update_data: dict) -> bool:
#     result = await DB.database["users"].update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
#     return result.modified_count > 0

# @staticmethod
# async def delete_user(user_id: str) -> bool:
#     result = await DB.database["users"].delete_one({"_id": ObjectId(user_id)})
#     return result.deleted_count > 0

# # Example of method using multiple collections
# @staticmethod
# async def get_user_with_posts(user_id: str) -> Optional[dict]:
#     user = await DB.database["users"].find_one({"_id": ObjectId(user_id)})
#     if not user:
#         return None

#     posts = []
#     cursor = DB.database["posts"].find({"user_id": ObjectId(user_id)})
#     async for post in cursor:
#         posts.append(post)

#     return {"user": User(**user), "posts": posts}

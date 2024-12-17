from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from app.core.config import core_settings


# load_dotenv()
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

engine = create_engine(core_settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def db_conn():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def db_conn():
#     db = SessionLocal()
#     try:
#         yield db
#     except SQLAlchemyError as e:
#         db.rollback()
#         # print(f"Database error: {str(e)}")
#         print(f"Database error. Reason: {e}")

#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred") from e

#     except:
#         print(f"Unexpected Database error")
#         raise

#     finally:
#         db.close()


DB = Annotated[Session, Depends(db_conn)]


# session.scalar() is equivalent to session.execute().scalar()
# session.scalars() is equivalent to session.execute().scalars()

# select one
# db.scalars(select(Listing).where(Listing.key == listing_key)).first()
# listing = db.scalar(select(Listing).where(Listing.key == listing_key)) #when 1 row or None expected
# listing = db.execute(select(Listing).where(User.key == listing_key)).scalars().first()

# Get first match or None
# listing = session.scalars(select(User).where(User.key == "as!23sdf5tasdfas")).first()


# Get all matches
# listings = session.scalars(select(User).where(User.key == "as!23sdf5tasdfas")).all()

# SELECT IN
# stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))
# session.scalars(stmt)


# SELECT ONE
# stmt = select(User).where(User.name == "patrick")
# session.scalars(stmt).one()


# Select One - fetch a single user by ID
#  stmt = select(User).where(User.id == user_id)
#     result = session.execute(stmt)
#     return result.scalar_one_or_none()


# Select Many - fetch all users
#   stmt = select(User).where(User.age >= min_age).order_by(User.name)
#     result = session.execute(stmt)
#     return list(result.scalars())


# Update - update email for a user
#    stmt = (
#         update(User)
#         .where(User.id == user_id)
#         .values(email=new_email)
#     )
#     session.execute(stmt)
#     session.commit()


# Delete - delete users by age
#    stmt = delete(User).where(User.age > max_age)
#     session.execute(stmt)
#     session.commit()


# delete where in
#  stmt = (
#         delete(User)
#         .where(User.id.in_(user_ids))
#     )
#     session.execute(stmt)
#     session.commit()


# delete where
# stmt = (
#     delete(User)
#     .where(
#         or_(
#             User.email.in_(emails),
#             User.name.in_(names)
#         )
#     )
# )
# session.execute(stmt)
# session.commit()


# Create conditions for each age range
# conditions = [
#     User.age.between(min_age, max_age)
#     for min_age, max_age in age_ranges
# ]

# stmt = (
#     delete(User)
#     .where(or_(*conditions))
# )
# session.execute(stmt)
# session.commit()


# # Method 3: Insert many rows at once
# users = [
#     {"name": "John", "email": "john@example.com", "age": 25},
#     {"name": "Jane", "email": "jane@example.com", "age": 30}
# ]
# session.execute(insert(User), users)
# session.commit()

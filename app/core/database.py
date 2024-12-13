import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session


load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# engine = create_engine(core_settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def db_conn():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred") from e

    except:
        raise
    finally:
        db.close()


DB = Annotated[Session, Depends(db_conn)]


# removes all migration guides
# rm alembic/versions/*.py
# rm alembic/versions/*

# Generate a migration
# alembic revision --autogenerate -m "description of changes"


# Apply the migration
# alembic upgrade head

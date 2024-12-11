import os
from typing import Annotated
from fastapi import Depends, HTTPException, logger, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import core_settings
from sqlalchemy.orm import Session


engine = create_engine(core_settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def db_conn():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred") from e

    except:
        raise
    finally:
        db.close()


DB = Annotated[Session, Depends(db_conn)]


# Generate a migration
# alembic revision --autogenerate -m "description of changes"


# Apply the migration
# alembic upgrade head

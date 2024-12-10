from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite URL this will create a file named sql_app.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# create engine with SQLite support for multiple threads
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  # needed for SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency for FastAPI
def db_conn():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # Generate a migration
# alembic revision --autogenerate -m "add full_name column"

# # Apply the migration
# alembic upgrade head

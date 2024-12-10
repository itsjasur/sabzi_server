# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import db_conn
import models

app = FastAPI()


@app.get("/users/")
def read_users(db: Session = Depends(db_conn)):
    users = db.query(models.User).all()
    return users

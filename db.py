import os

from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, Boolean, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
if (
    not POSTGRES_USER
    or not POSTGRES_PASSWORD
    or not POSTGRES_DB
    or not POSTGRES_HOST
    or not POSTGRES_PORT
):
    raise ValueError(
        "POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT must be set"
    )


DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)


class Message(Base):  # type: ignore
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(engine)

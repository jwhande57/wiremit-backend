from sqlalchemy import Column, Integer, String, Float, DateTime
from pydantic import BaseModel
from database import Base
from typing import List

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Rate(Base):
    __tablename__ = "rates"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    usd_gbp = Column(Float)
    usd_zar = Column(Float)
    zar_gbp = Column(Float)

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RateOut(BaseModel):
    usd_to_gbp: float
    usd_to_zar: float
    zar_to_gbp: float

class HistoricalRate(BaseModel):
    timestamp: str
    usd_gbp: float
    usd_zar: float
    zar_gbp: float
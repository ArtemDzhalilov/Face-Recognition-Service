from sqlalchemy import Column, String, Time
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    login = Column(String, primary_key=True)
    password = Column(String)
    ip = Column(String)
    lastlogintime = Column(Time)
    api_key = Column(String)
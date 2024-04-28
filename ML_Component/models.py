from sqlalchemy import Column, String
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Faces(Base):
    __tablename__ = 'result_faces'

    embedding = Column(String, primary_key=True)
    fullname = Column(String)
    description = Column(String)
    owner = Column(String)
class devices(Base):
    __tablename__ = 'devices'

    name = Column(String, primary_key=True)
    owner = Column(String)


class RequestFace(BaseModel):
    image: List[float]


class Face(BaseModel):
    image: List[float]
    FullName: str
    Description: str


class ResultFace(BaseModel):
    embedding: List[float]
    full_name: str
    description: str

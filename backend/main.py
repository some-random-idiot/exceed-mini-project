from xmlrpc.client import DateTime, boolean
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from numpy import int16

from pymongo import MongoClient
from pydantic import BaseModel


class Database(BaseModel):
    status: boolean
    name: str
    start_time: DateTime
    end_time: DateTime
    current_duration: int
    room: int


client = MongoClient('mongodb://localhost', 27017)

db = client["mini_project"]
collection = db["database"]

app = FastAPI()
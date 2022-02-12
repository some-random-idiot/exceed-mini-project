import datetime
from sqlite3 import Time
from xmlrpc.client import DateTime, boolean
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pandas import Timedelta

from pymongo import MongoClient
from pydantic import BaseModel


class Record(BaseModel):
    status: boolean
    start_time: datetime.time
    end_time: datetime.time
    duration: datetime.timedelta
    room: int


client = MongoClient('mongodb://localhost', 27017)

db = client["mini_project"]
collection = db["database"]


app = FastAPI()

@app.get("/get-room/{room}")
def get_room(room: int):
    result = collection.find_one({"room": room}, {"_id": 0})
    if result:
        return {
                "room": result["room"],
                "status": result["status"],
                "duration": result["current_duration"]
                }
    return {
        "room": room,
        "status": True
    }
from fastapi import FastAPI
import datetime
from sqlite3 import Time
from xmlrpc.client import DateTime, boolean
from fastapi.encoders import jsonable_encoder
from numpy import empty

from pymongo import MongoClient
from pydantic import BaseModel


class Record():
    status: boolean
    start_time: datetime.time
    end_time: datetime.time
    current_duration: datetime.timedelta
    room: int


client = MongoClient('mongodb://localhost', 27017)

db = client["mini_project"]
collection = db["database"]


app = FastAPI()

def ave(room):
    result = collection.find({"room": room}, {"_id": 0})
    result_list = []
    time_Delta = 0
    for record in result:
        time_Delta += (record["end_time"] - record["start_time"])
    return time_Delta/len(result_list)

@app.get("/get-room/{room}")
def get_room(room: int):
    """Get the record in the database

    Example
    Someone in the restroom :
        {
            "room": 1,
            "status": true,
            "start_time": "11:00",
            "average": 60
        }
    Someone not in the restroom:
        {
            "room": 1,
            "status": false,
            "average": 60
        } 
    No one in the restroom yet:
        {
            "room": 1,
            "status": false
        }
    """
    result = collection.find({"room": room}, {"_id": 0})
    result_list = []
    for record in result:
        result_list.append(record)
    if result_list == []:
        return {
                "room": room,
                "status": 1
                }
    result = result_list[-1]
    if not result["status"]:
        return {
                "room": result["room"],
                "status": result["status"],
                }
    elif result["status"]:
        return {
                "room": result["room"],
                "status": result["status"],
                "start_time": result["start_time"],
                "current_duration": result["current_duration"]    
                }

import datetime
from sqlite3 import Time
from xmlrpc.client import DateTime, boolean
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder

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

def ave(room):
    result = collection.find({"room": room}, {"_id": 0})
    result_list = []
    for record in result:
        result_list.append(record["duration"])
    return sum(result_list)/len(result_list)

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
    result = collection.find_one({"room": room}, {"_id": 0})
    if result["status"] == False:
        return {
                "room": result["room"],
                "status": result["status"],
                "average": ave(room)
                }
    elif result["status"] == True:
        return {
                "room": result["room"],
                "status": result["status"],
                "start_time": result["start_time"],
                "average": ave(room)
                }
    return {
        "room": room,
        "status": False
    }

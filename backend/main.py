import datetime

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder

from pymongo import MongoClient
from pydantic import BaseModel


class Record(BaseModel):
    status: int  # 1 if the record is active (someone is in the restroom).
    name: Optional[str]
    start_time: Optional[datetime.time]
    current_duration: Optional[datetime.timedelta]
    room: int


client = MongoClient('mongodb://localhost', 27017)

db = client["mini_project"]
collection = db["database"]

app = FastAPI()


def ave(room):
    result = collection.find({"room": room}, {"_id": 0})
    result_list = []
    for record in result:
        result_list.append(record["current_duration"])
    return sum(result_list) / len(result_list)


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
    if not result_list:
        return {
            "room": room,
            "status": False
        }
    result = result_list[-1]
    if not result["status"]:
        return {
            "room": result["room"],
            "status": result["status"],
            "average": ave(room)
        }
    elif result["status"]:
        return {
            "room": result["room"],
            "status": result["status"],
            "start_time": result["start_time"],
            "current_duration": result["current_duration"],
            "average": ave(room)
        }


@app.post("/update-room")
async def update_room(record: Record):
    """Creates a new record in the database.
    This is used when there are no previous records of a room, or the latest record has already ended.
    It automatically creates timestamp and duration.

    Example request:
    {
        "status": 1,
        "name": "John Doe",
        "room": 2
    }
    """
    if record["status"] == 1 or collection.find_one({"room": record["room"]}) is None:
        record = jsonable_encoder(record)
        record["status"] = 1
        record["start_time"] = str(datetime.datetime.now().time().strftime("%H:%M:%S"))
        record["current_duration"] = str(datetime.timedelta(0))
        collection.insert_one(record)
        return {"status": "success"}
    elif record["status"] == 0:
        # Get the latest record.
        records = collection.find({"room": record["room"]}, {"_id": 0})
        record_list = []
        for record in records:
            record_list.append(record)
        target_record = record_list[-1]

        # Check if the attributes are valid.
        has_attribute = False
        for attribute in record:
            has_attribute = attribute in target_record

        if has_attribute:
            collection.update_one({"_id": target_record["_id"]}, {"$set": record})
            # Update the duration.
            current_duration = str(
                datetime.datetime.strptime(datetime.datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S")
                - datetime.datetime.strptime(target_record["start_time"], "%H:%M:%S"))
            collection.update_one({"_id": target_record["_id"]}, {"$set": {"current_duration": current_duration}})
            return {"status": "success"}
        else:
            return {"status": "failure",
                    "message": "No such attribute detected. Please check the request body."}

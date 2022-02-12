import datetime
from xmlrpc.client import boolean

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder

from pymongo import MongoClient
from pydantic import BaseModel


class Record(BaseModel):
    status: boolean  # True if the record is active (someone is in the restroom).
    name: str
    start_time: datetime.time
    current_duration: datetime.timedelta
    room: int


client = MongoClient('mongodb://localhost', 27017)

db = client["mini_project"]
collection = db["database"]

app = FastAPI()


@app.post("/create-room")
def create_room(record: Record):
    """Creates a new record in the database.
    This is used when there are no previous records of a room, or the latest record has already ended.
    If provided status is False, it will get changed to True automatically.

    Example request:
    {
        "status": true,
        "name": "John Doe",
        "start_time": "10:00",
        "current_duration": "00:00:00",
        "room": 1
    }
    """
    record = jsonable_encoder(record)
    record["status"] = True
    collection.insert_one(record)
    return {"status": "success"}


@app.put("/update-room/{room}")
async def update_room(room: int, request: Request):
    """Updates the latest record of a room in the database.
    If a record's 'status' is False, it rejects the update.

    Example request:
    {
        "status": false,
        "current_duration": "00:10:00"
    }
    """
    attributes = await request.json()
    if "name" in attributes:
        return {"status": "failure",
                "message": "Name update attempt detected. Please create a new record instead."}

    if collection.find_one({"room": room}):
        # Get the latest record.
        records = collection.find({"room": room})
        record_list = []
        for record in records:
            record_list.append(record)
        target_record = record_list[-1]

        if target_record["status"]:
            # Check if the attributes are valid.
            has_attribute = False
            for attribute in attributes:
                has_attribute = attribute in target_record

            if has_attribute:
                collection.update_one({"_id": target_record["_id"]}, {"$set": attributes})
                return {"status": "success"}
            else:
                return {"status": "failure",
                        "message": "No such attribute detected. Please check the request body."}
        else:
            return {"status": "failure",
                    "message": "The latest record has already ended. Please create a new record instead."}
    else:
        return {"status": "failure",
                "message": f"No previous record of room {room} found. Please create a new record."}

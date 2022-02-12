import datetime

from typing import Optional

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder

from pymongo import MongoClient
from pydantic import BaseModel


class Record(BaseModel):
    status_room1: int
    status_room2: int
    status_room3: int
    name: Optional[str]
    start_time: Optional[datetime.time]
    current_duration: Optional[datetime.timedelta]
    room: Optional[int]


client = MongoClient('mongodb://localhost', 27017)

db = client["mini_project"]
collection = db["database"]

app = FastAPI()


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
    record = dict(record)
    for i in range(1, 4):
        print(record)
        # Get the latest record.
        records = collection.find({"room": i})
        record_list = []
        for r in records:
            record_list.append(r)

        # If there is no record, create a new one.
        if len(record_list) == 0:
            target_record = {"status": 0}
        else:
            target_record = record_list[-1]

        if (record[f"status_room{i}"] == 1 or collection.find_one({"room": i}) is None) and not target_record["status"]:
            record[f"status_room{i}"] = 1
            record_formatted = {f"status": record[f"status_room{i}"],
                                "start_time": str(datetime.datetime.now().time().strftime("%H:%M:%S")),
                                "current_duration": str(datetime.timedelta(0)),
                                "room": i}
            collection.insert_one(record_formatted)
        elif record[f"status_room{i}"] == 0:
            # Check if the attributes are valid.
            has_attribute = False
            for attribute in record:
                has_attribute = attribute in target_record

            if has_attribute:
                collection.update_one({"_id": target_record["_id"]}, {"$set": {"status": 0}})
                # Update the duration.
                current_duration = str(
                    datetime.datetime.strptime(datetime.datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S")
                    - datetime.datetime.strptime(target_record["start_time"], "%H:%M:%S"))
                collection.update_one({"_id": target_record["_id"]}, {"$set": {"current_duration": current_duration}})
            else:
                return {"status": "failure",
                        "message": "No such attribute detected. Please check the request body."}
    return {"status": "success"}

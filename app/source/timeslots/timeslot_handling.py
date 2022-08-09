from time import time
from typing import Optional
from datetime import datetime, timedelta

from bson import ObjectId
from bson.errors import InvalidId
from injector import T
from uvloop import install

from app.db.db import get_database
from app.routes.models import TimeSlot, DailySlotConfiguration


def add_timeslot(timestamp, user_id, db):
    try:
        timeslot_id = ObjectId()
        timeslot = TimeSlot(id=timeslot_id, user_id=user_id, timestamp=timestamp)
    except:
        return False

    try:
        insert_status = db.timeslots.replace_one(
            {"timestamp": timestamp, "user_id": user_id}, 
            timeslot.mongo(), 
            upsert=True
            )
    except:
        timeslot_id = None
    finally:
        return timeslot_id


def load_timeslot_by_id(timeslot_id, db):

    try:
        timeslot = db.timeslots.find_one(ObjectId(timeslot_id))
        timeslot = TimeSlot.from_mongo(timeslot) 
    except:
        timeslot = {}
    finally:
        return timeslot


def hide_timeslot(timeslot, db):

    try:
        mongo_timeslot_id = ObjectId(timeslot.id)
    except InvalidId:
        return False

    try:
        custom_timeslot = db.timeslots.count_documents({"_id": mongo_timeslot_id})
    except:
        custom_timeslot = False

    try:
        if custom_timeslot:
            update_status = db.timeslots.replace_one({"_id": mongo_timeslot_id}, {"$set": {"hidden": True}})
        else:
            update_status = db.timeslots.insert_one(timeslot.mongo())
        update_status = update_status.acknowledged
    except:
        mongo_timeslot_id = None
    finally:
        return mongo_timeslot_id


def load_timeslots(user_id):
    db = get_database()

    try:
        timeslots = db.timeslots.find({"user_id": user_id})
        timeslots = [TimeSlot.from_mongo(timeslot) for timeslot in timeslots]
    except:
        timeslots = []
    finally:
        return timeslots


def load_timeslots_by_days(dates: list, date_format: str, base_date: datetime, user_id: str):
    db = get_database()

    try:
        #iso_date = datetime.strptime(date, date_format)
        custom_timeslots = db.timeslots.find({"user_id": user_id, "timestamp": {"$gte": base_date }})#, "$lt": iso_date+timedelta(days=1)}})
        custom_timeslots = [TimeSlot.from_mongo(timeslot) for timeslot in custom_timeslots]
    except:
        custom_timeslots = []

    try:
        timeslot_configuration = db.dailySlotConfigurations.find_one({"user_id": user_id})
    except:
        timeslot_configuration = {"daily_timestamps": []}

    recurring_timeslots = []
    for date in dates:
        recurring_timeslots += [
            TimeSlot(
                id=ObjectId(), 
                user_id=user_id, 
                timestamp=datetime.strptime(date + hour_of_day.strftime("%H:%M"), date_format+"%H:%M")
                ) 
            for hour_of_day in timeslot_configuration["daily_timestamps"]]
    recurring_timeslots = [slot for slot in recurring_timeslots if slot.timestamp > base_date]

    custom_timeslots_timestamps = [timeslot.timestamp for timeslot in custom_timeslots]
    recurring_timeslots = [timeslot for timeslot in recurring_timeslots if timeslot.timestamp not in custom_timeslots_timestamps]

    timeslots = custom_timeslots + recurring_timeslots
    timeslots = [timeslot for timeslot in timeslots if not timeslot.hidden]
    timeslots = sorted(timeslots, key=lambda slot: slot.timestamp)

    daily_timeslots = {
        "weekdays": dates,
        "timeslots": timeslots
    }
    return daily_timeslots


def update_timeslot_draft(timeslot):
    db = get_database()

    try:
        if timeslot.id:
            mongo_timeslot_id = ObjectId(timeslot.id)
        else:
            mongo_timeslot_id = ObjectId()
            timeslot.id = mongo_timeslot_id
    except InvalidId:
        return False

    try:
        update_status = db.timeslots.replace_one({"_id": mongo_timeslot_id}, timeslot.mongo(), upsert=True)
        update_status = update_status.acknowledged
    except:
        update_status = False
    finally:
        return update_status


def get_weekly_timeslots(user_id):
    base_date = datetime.utcnow()
    numdays = 7

    date_format = "%Y-%m-%d"
    date_list = [base_date + timedelta(days=x) for x in range(numdays)]
    date_list = [date.strftime(date_format) for date in date_list]

    weekly_timeslots = load_timeslots_by_days(date_list, date_format, base_date, user_id)

    return weekly_timeslots


def add_recurring_timeslot(hour_of_day, user_id):
    db = get_database()

    try:
        update_status = db.dailySlotConfigurations.update_one(
            {"user_id": user_id},
            {"$push": {"daily_timestamps": hour_of_day}}
            )
        update_status = update_status.acknowledged
    except:
        update_status = False
    finally:
        return update_status

def get_timeslot_configuration(user_id, db):

    try:
        timeslot_configuration = db.dailySlotConfigurations.find_one({"user_id": user_id})
        timeslot_configuration = DailySlotConfiguration.from_mongo(timeslot_configuration)
        timeslot_configuration.daily_timestamps = sorted(timeslot_configuration.daily_timestamps, key=lambda slot: slot.strftime("%H:%M"))
    except:
        timeslot_configuration = None
    finally:
        return timeslot_configuration


def remove_timeslot_from_configuration(timeslot, user_id, db):
    try:
        remove_status = db.dailySlotConfigurations.update_one({"user_id": user_id}, {"$pull": {"daily_timestamps": timeslot}})
        remove_status = remove_status.acknowledged
    except:
        remove_status = False
    finally:
        return remove_status
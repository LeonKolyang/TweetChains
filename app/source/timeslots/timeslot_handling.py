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


def hide_timeslot(timeslot, db):

    try:
        mongo_timeslot_id = ObjectId(timeslot.id)
    except InvalidId:
        return False

    try:
        update_status = db.timeslots.replace_one({"_id": mongo_timeslot_id}, timeslot.mongo(), upsert=True)
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


def load_timeslots_by_days(dates: list, date_format: str, user_id: str):
    db = get_database()
    daily_timeslots = []

    for date in dates:
        
        try:
            iso_date = datetime.strptime(date, date_format)
            custom_timeslots = db.timeslots.find({"user_id": user_id, "timestamp": {"$gte": iso_date, "$lt": iso_date+timedelta(days=1)}})
            custom_timeslots = [TimeSlot.from_mongo(timeslot) for timeslot in custom_timeslots]
        
        except:
            custom_timeslots = []
        
        try:
            recurring_timeslots = db.dailySlotConfigurations.find_one({"user_id": user_id})
            recurring_timeslots = [
                TimeSlot(id=ObjectId(), user_id=user_id, timestamp=datetime.strptime(date + hour_of_day.strftime("%H:%M"), date_format+"%H:%M")) 
                for hour_of_day in recurring_timeslots["daily_timestamps"]]
        except:
            recurring_timeslots = []

        custom_timeslots_timestamps = [timeslot.timestamp for timeslot in custom_timeslots]

        recurring_timeslots = [timeslot for timeslot in recurring_timeslots if timeslot.timestamp not in custom_timeslots_timestamps]

        timeslots = custom_timeslots + recurring_timeslots
        timeslots = [timeslot for timeslot in timeslots if not timeslot.hidden]
        timeslots = sorted(timeslots, key=lambda slot: slot.timestamp)

        date_timeslots = {
            "weekday": date,
            "timeslots": timeslots}
        daily_timeslots.append(date_timeslots)

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
    base_date = datetime.today()
    numdays = 7

    date_format = "%Y-%m-%d"
    date_list = [base_date + timedelta(days=x) for x in range(numdays)]
    date_list = [date.strftime(date_format) for date in date_list]

    weekly_timeslots = load_timeslots_by_days(date_list, date_format, user_id)

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
        timeslot_configuration.daily_timestamps = sorted(timeslot_configuration.daily_timestamps)
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
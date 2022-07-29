import json
from datetime import datetime
from fastapi import APIRouter, Response
from requests import delete

from app.routes.models import AppUser, TimeSlot, RecurringTimeSlot
from app.source.timeslots.timeslot_handling import add_recurring_timeslot, add_timeslot, \
    get_timeslot_configuration, get_weekly_timeslots, hide_timeslot, load_timeslots, remove_timeslot_from_configuration, update_timeslot_draft
from app.core.logging import logger
from app.db.db import get_database

router = APIRouter()

@router.get("/get-timeslots", tags=["timeslot_handling"])
async def get_timeslots(user_id):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)

    timeslots = load_timeslots(token["user_id"])

    return timeslots


@router.post("/assign-draft-to-timeslot", tags=["timeslot_handling"])
async def assign_draft_to_timeslot(timeslot: TimeSlot):
    update_status = update_timeslot_draft(timeslot)

    return str(update_status)


@router.post("/remove-draft-from-timeslot", tags=["timeslot_handling"])
async def assign_draft_to_timeslot(timeslot: TimeSlot):
    update_status = update_timeslot_draft(timeslot)

    return str(update_status)


@router.post("/create-daily-timeslot", tags=["timeslot_handling"])
async def create_daily_timeslot(recurring_timeslot: RecurringTimeSlot):
    """Write timestamp in the users configuration file.
    Upon reading the users timeslots, the configuration is used to autogenerate recurring daily timeslots.
    
    hour_of_day timestamp format: HH:MM:SS
    Args:
        recurring_timeslot (RecurringTimeSlot): Contains the timestamp and user_id

    Returns:
        bool: update status
    """
    update_status = add_recurring_timeslot(hour_of_day=recurring_timeslot.hour_of_day, user_id=recurring_timeslot.user_id)

    return str(update_status)


@router.get("/weekly-timeslots", tags=["timeslot_handling"])
async def get_user_weekly_timeslot(user_id):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)

    timeslots = get_weekly_timeslots(token["user_id"])
    return timeslots


@router.post("/add-custom-timeslot", tags=["timeslot_handling"])
async def add_custom_timeslot(timeslot: TimeSlot):
    timeslot_id = update_timeslot_draft(timeslot)
    
    return timeslot_id


@router.post("/hide-timeslot", tags=["timeslot_handling"])
async def hide_single_timeslot(timeslot: TimeSlot):
    db = get_database()

    timeslot.hidden = True 
    timeslot_id = hide_timeslot(timeslot, db)
    
    return str(timeslot_id)


@router.get("/timeslot-configuration")
async def get_users_timeslot_configuration(user_id):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)
    user_id = token["user_id"]
    db = get_database()

    configuration = get_timeslot_configuration(user_id, db)
    return configuration


@router.post("/remove-timeslot-from-configuration")
async def remove_from_configuration(recurring_timeslot: RecurringTimeSlot):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)
    user_id = token["user_id"]
    db = get_database()

    delete_status = remove_timeslot_from_configuration(recurring_timeslot.hour_of_day, user_id, db)

    return str(delete_status)
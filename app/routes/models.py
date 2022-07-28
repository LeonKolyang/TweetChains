from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field

from app.db.model_utils import OID, MongoModel

class ApiResponse(BaseModel):
    pass


class AppUser(BaseModel):
    user_id: str

class Tweet(BaseModel):
    tweet_text: str
    tweet_id: Optional[str]

class TweetID(BaseModel):
    tweet_id: str

class TweetDraft(MongoModel):
    id: OID = Field()
    user_id: str = Field()
    tweet_text: str = Field()
    creation_timestamp: datetime = Field()

class TimeSlot(MongoModel):
    id: OID | None = Field()
    user_id: str = Field()
    timestamp: datetime = Field()
    assigned_draft: str | None = Field()
    hidden: bool = Field(default=False)

class RecurringTimeSlot(BaseModel):
    user_id: str
    hour_of_day: str 

class DailySlotConfiguration(MongoModel):
    id: OID = Field()
    user_id: str = Field()
    daily_timestamps: list[str] = Field()

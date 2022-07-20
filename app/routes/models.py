from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field

from app.db.model_utils import OID, MongoModel

class ApiResponse(BaseModel):
    pass


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
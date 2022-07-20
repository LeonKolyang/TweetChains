from typing import Optional
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from app.db.db import get_database
from app.routes.models import Tweet, TweetDraft


def store_tweet_draft(tweet_text: str, tweet_id: Optional[str], user_id: str) -> Optional[ObjectId]:
    timestamp = datetime.utcnow()

    tweet_id = ObjectId(tweet_id) if tweet_id else ObjectId()
    tweet_draft = TweetDraft(id=tweet_id, user_id=user_id, tweet_text=tweet_text, creation_timestamp=timestamp)

    db = get_database()
    insert_status = db.tweetDrafts.replace_one({"_id": tweet_id}, tweet_draft.mongo(), upsert=True)

    if insert_status.acknowledged:
        return tweet_id
    else:
        return None


def load_tweet_draft(tweet_id: str) -> Optional[Tweet]:
    db = get_database()

    try:
        mongo_tweet_id = ObjectId(tweet_id)
    except InvalidId:
        return None

    try:
        tweet = db.tweetDrafts.find_one(mongo_tweet_id)
        tweet = TweetDraft.from_mongo(tweet)
    except:
        tweet = None
    finally:
        return tweet


def load_tweet_drafts_for_user(user_id: str) -> Optional[list]:
    db = get_database()

    try:
        tweet_drafts = db.tweetDrafts.find({"user_id" : user_id})
        tweet_drafts = [TweetDraft.from_mongo(tweet) for tweet in list(tweet_drafts)]
    except:
        tweet_drafts = None
    finally:
        return tweet_drafts



def delete_tweet_draft(tweet_id: str) -> bool:
    db = get_database()

    try:
        mongo_tweet_id = ObjectId(tweet_id)
    except InvalidId:
        return False

    try:
        delete_status = db.tweetDrafts.delete_one({"_id": mongo_tweet_id})
    except:
        delete_status = False
    finally:
        return delete_status.acknowledged



import json
from fastapi import APIRouter, Response, Query
from typing import Optional
from app.db.db import get_database

from app.routes.models import ScheduledTweet, Tweet, TweetID
from app.source.timeslots.timeslot_handling import load_timeslot_by_id
from app.source.tweets.post_tweet import post_tweet_to_api, post_tweet_to_schedule_queue
from app.source.tweets.draft_handling import store_tweet_draft, load_tweet_draft, load_tweet_drafts_for_user, delete_tweet_draft

from app.core.logging import logger

router = APIRouter()

@router.post("/store-draft", tags=["tweet_handling"])
async def store_tweet(tweet: Tweet):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)
    
    tweet_text = tweet.tweet_text
    tweet_id = tweet.tweet_id

    tweet_id = store_tweet_draft(tweet_text, tweet_id, token["user_id"])

    return str(tweet_id)


@router.post("/tweet", tags=["tweet_handling"])
async def post_tweet(tweet_id: TweetID):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)

    tweet_id = tweet_id.tweet_id
    tweet = load_tweet_draft(tweet_id)

    tweet_text = tweet.tweet_text
    api_response = post_tweet_to_api(tweet_text, token)
    
    return api_response


@router.post("/schedule-tweet", tags=["tweet_handling"])
async def schedule_tweet(scheduled_tweet: ScheduledTweet):
    db = get_database()

    with open("token.json", "r") as token_file:
        token = json.load(token_file)

    tweet_id = scheduled_tweet.tweet_id
    tweet = load_tweet_draft(tweet_id)

    timeslot_id = scheduled_tweet.timeslot_id
    timeslot = load_timeslot_by_id(timeslot_id, db)

    tweet_text = tweet.tweet_text
    timslot_timestamp = timeslot.timestamp
    api_response = post_tweet_to_schedule_queue(tweet_text, timslot_timestamp, token)
    
    return str(api_response)


@router.get("/get-drafts", tags=["tweet_handling"])
async def load_drafts(draft_ids: list | None = Query(default=[])):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)
    user_id = token["user_id"]

    tweet_drafts = load_tweet_drafts_for_user(draft_ids, user_id)

    return {"drafts": tweet_drafts}


@router.post("/delete-draft", tags=["tweet_handling"])
async def delete_draft(tweet_id: TweetID):
    tweet_id = tweet_id.tweet_id
    delete_status = delete_tweet_draft(tweet_id)
    return str(delete_status)
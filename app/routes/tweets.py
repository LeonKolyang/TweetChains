import json
from fastapi import APIRouter, Response

from app.routes.models import Tweet, TweetID
from app.source.tweets.post_tweet import post_tweet_to_api
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


@router.get("/get-drafts", tags=["tweet_handling"])
async def load_drafts():
    with open("token.json", "r") as token_file:
        token = json.load(token_file)
    user_id = token["user_id"]

    tweet_drafts = load_tweet_drafts_for_user(user_id)

    return {"drafts": tweet_drafts}


@router.post("/delete-draft", tags=["tweet_handling"])
async def delete_draft(tweet_id: TweetID):
    tweet_id = tweet_id.tweet_id
    delete_status = delete_tweet_draft(tweet_id)
    return str(delete_status)
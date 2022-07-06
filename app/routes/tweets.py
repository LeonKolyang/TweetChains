import json
from fastapi import APIRouter, Response
from pydantic import BaseModel
from app.source.tweets.post_tweet import post_tweet_to_api

from app.core.logging import logger

router = APIRouter()

class Tweet(BaseModel):
    tweet_text: str

@router.post("/tweet", tags=["user_handling"])
async def post_tweet(tweet: Tweet):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)
    print(tweet)
    tweet_text = tweet.tweet_text
    print(tweet_text)

    api_response = post_tweet_to_api(tweet_text, token)
    
    return api_response
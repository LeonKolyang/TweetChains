from urllib.parse import urlparse
from requests_oauthlib import OAuth1Session
import os
import json
from datetime import datetime
from rq import Queue
from redis import Redis

from app.core.di import get_twitter_auth_config
from app.source.users.authentication import load_oauth_session
from app.core.logging import logger


def post_tweet_to_api(tweet_text, token, consumer_key=None, consumer_secret=None):
    oauth = load_oauth_session(token["oauth_token"], token["oauth_token_secret"], consumer_key, consumer_secret)
    logger.info("Tweet scheduled")
    payload = {"text": tweet_text}

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    return json_response


def post_tweet_to_schedule_queue(tweet_text, token):
    twitter_auth_config = get_twitter_auth_config()

    #user_id = str(token["user_id"])
    #url = urlparse("redis://default:BUX6whhvsjm0vri2nWxuqTQzSrtdRiYh@redis-11576.c3.eu-west-1-1.ec2.cloud.redislabs.com:11576")
    url = urlparse("redis://localhost:6379")
    r = Redis(host=url.hostname, port=url.port, password=url.password)
    queue = Queue(name="default", connection=r)

    # Schedules job to be run at 9:15, October 10th in the local timezone
    #job = queue.enqueue_at(
    #    datetime(2022, 8, 1, 22, 51), 
    job = queue.enqueue(
        post_tweet_to_api, 
        kwargs={ 
            "tweet_text": tweet_text, 
            "token": token,
            "consumer_key": twitter_auth_config.consumer_key,
            "consumer_secret": twitter_auth_config.consumer_secret 
            }
        )







def post_tweet_standalone(tweet_text):
    twitter_auth_config = get_twitter_auth_config()

    # Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.
    payload = {"text": tweet_text}

    # Get request token
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(twitter_auth_config.consumer_key, client_secret=twitter_auth_config.consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token: %s" % resource_owner_key)

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        twitter_auth_config.consumer_key,
        client_secret=twitter_auth_config.consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    # Make the request
    oauth = OAuth1Session(
        twitter_auth_config.consumer_key,
        client_secret=twitter_auth_config.consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
from requests_oauthlib import OAuth1Session
from requests_oauthlib.oauth1_session import TokenRequestDenied

from app.core.di import get_twitter_auth_config
from app.core.logging import logger


def get_request_token() -> dict:
    twitter_auth_config = get_twitter_auth_config()

    # Get request token
    request_token_url = f"https://api.twitter.com/oauth/request_token"
    oauth = OAuth1Session(twitter_auth_config.consumer_key,
                          client_secret=twitter_auth_config.consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
        response_success = True
    except ValueError as e:
        logger.error(
            "There may have been an issue with the consumer_key or consumer_secret you entered.")
        logger.debug(e)
        fetch_response = {}
        response_success = False

    fetched_token = {
        "oauth_token": fetch_response.get("oauth_token"),
        "oauth_token_secret": fetch_response.get("oauth_token_secret"),
        "oauth_callback_confirmed": response_success
    }

    return fetched_token


def get_access_token(oauth_token, oauth_token_secret, oauth_verifier) -> dict:
    twitter_auth_config = get_twitter_auth_config()

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        twitter_auth_config.consumer_key,
        client_secret=twitter_auth_config.consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
        verifier=oauth_verifier,
    )
    try:
        oauth_tokens = oauth.fetch_access_token(access_token_url)
    except TokenRequestDenied as e:
        logger.error(
            "There may have been an issue with the consumer secrets or user secrets you entered.")
        logger.debug(e)
        oauth_tokens = {}
    return oauth_tokens


def load_oauth_session(access_token, access_token_secret, consumer_key=None, consumer_secret=None):
    twitter_auth_config = get_twitter_auth_config()

    consumer_key = consumer_key if consumer_key else twitter_auth_config.consumer_key
    consumer_secret = consumer_secret if consumer_secret else twitter_auth_config.consumer_secret

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    return oauth

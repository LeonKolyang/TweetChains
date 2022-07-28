from http import HTTPStatus
import json

from fastapi import APIRouter, Response
from app.source.users.authentication import get_request_token, get_access_token, load_oauth_session
from app.source.users.user_information import create_user_configuration, fetch_profile_picture_url
from app.core.logging import logger

router = APIRouter()



@router.get("/request-token", tags=["user_handling"])
async def request_application_token() -> dict:
    """This endpoint returns the tokens to start browser-based authentication in your app.
    It's step #1 of the "Implementing Log in with Twitter" authentication flow.#
    Requests must provide these query parameters:
    - `callback_url`, the `AuthSession.getRedirectUrl()` for your app#
    Responses will provide this structure:
    - `oauth_token`, the request token to start the auth flow
    - `oauth_token_secret`, the request token secret to start the auth flow
    - `oauth_callback_confirmed`, if the callback is listed in your Twitter app settings.#
    @see https://developer.twitter.com/en/docs/basics/authentication/guides/log-in-with-twitter
    @see https://developer.twitter.com/en/docs/basics/authentication/api-reference/request_token
    @see https://github.com/draftbit/twitter-lite#app-authentication-example

    Returns:
        dict: Twitter application tokens
    """
    token = get_request_token()
    logger.info("Application token successfully acquired")
    return token


@router.get("/access-token", tags=["user_handling"])
async def request_access_token(oauth_token: str, oauth_token_secret: str, oauth_verifier: str) -> dict:
    """This endpoint "converts" both the request tokens and browser-based auth tokens to an access token.
    It's step #3 of the "Implementing Log in with Twitter" authentication flow.#
    Requests must provide these query parameters:
    - `oauth_token`, the request token that started the auth flow
    - `oauth_token_secret`, the request token secret that started the auth flow
    - `oauth_verifier`, the verification code received from browser-based auth flow#
    Responses will provide this structure:
    - `oauth_token`, the access token for API calls on behalf of the user
    - `oauth_token_secret`, the access token secret for API calls on behalf of the user
    - `user_id`, the id of the Twitter account that is authenticated
    - `screen_name`, the username of the Twitter account that is authenticated#
    @see https://developer.twitter.com/en/docs/basics/authentication/guides/log-in-with-twitter
    @see https://developer.twitter.com/en/docs/basics/authentication/api-reference/access_token
    @see https://github.com/draftbit/twitter-lite#app-authentication-example

    Args:
        oauth_token (str): request token that started the auth flow
        oauth_token_secret (str): request token secret that started the auth flow
        oauth_verifier (str): verification code received from browser-based auth flow

    Returns:
        dict: User tokens

    """
    token = get_access_token(oauth_token, oauth_token_secret, oauth_verifier)
    if not token:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    logger.info("User token successfully acquired")

    create_user_configuration(token["user_id"])

    with open("token.json", "w") as token_file:
        json.dump(token, token_file)
    return token


@router.get("/profile-picture-url", tags=["user_handling"])
async def get_profile_picture_url(user_id):
    with open("token.json", "r") as token_file:
        token = json.load(token_file)
    profile_picture_url = fetch_profile_picture_url(token)

    profile_picture_url = profile_picture_url.replace("_normal", "")
    
    return profile_picture_url


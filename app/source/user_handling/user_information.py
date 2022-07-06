from http import HTTPStatus

from app.source.user_handling.authentication import load_oauth_session

def fetch_profile_picture_url(token):
    oauth = load_oauth_session(token["oauth_token"], token["oauth_token_secret"])

    parameters = {
        "user.fields": "profile_image_url"
    }
    
    # Making the request
    response = oauth.get(
        "https://api.twitter.com/2/users/me",
        params=parameters
    )

    profile_picture_url = ""

    if response.status_code == HTTPStatus.OK:
        response_data = response.json()
        profile_picture_url = response_data["data"]["profile_image_url"]

    return profile_picture_url

from http import HTTPStatus

from bson import ObjectId
from app.db.db import get_database
from app.core.logging import logger

from app.source.users.authentication import load_oauth_session
from app.routes.models import DailySlotConfiguration


def create_user_configuration(user_id):
    db = get_database()

    configuration_id = ObjectId()
    configuration = DailySlotConfiguration(id=configuration_id, user_id=user_id, daily_timestamps=[])

    try:
        status = db.dailySlotConfigurations.replace_one(
            {"user_id": user_id}, 
            configuration.mongo(), 
            upsert=True
            )
    except:
        configuration_id = None
        logger.error(f"Failed to create configuration for user {user_id}")
    finally:
        return configuration_id


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

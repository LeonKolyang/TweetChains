from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app.core import config
from app.main import app

client = TestClient(app)


def test_api_request_token_ok():
    """Should return 200."""

    # Successful request.
    response = client.get(
        "/request-token",
        #headers={"Accept": "application/json", "Authorization": api_token,},
    )
    assert response.status_code == HTTPStatus.OK

    token_response = response.json()

    assert isinstance(token_response["oauth_token"], str)
    assert isinstance(token_response["oauth_token_secret"], str)
    assert isinstance(token_response["oauth_callback_confirmed"], bool)



def test_api_access_token_invalid_token():
    """Should return 204."""

    # Authorized but should raise 400 error.
    response = client.get(
        "/access-token", 
        #headers={"Accept": "application/json", "Authorization": api_token,},
        params=dict(
            oauth_token= "foo", 
            oauth_token_secret= "bar", 
            oauth_verifier= "tests"
            )
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


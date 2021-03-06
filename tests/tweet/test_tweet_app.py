import json
import pytest
import requests
import TwitterAPI

from src.tweet import app
from src.layers.shared_files.python.news_bot_config import NewsBotConfig

config = NewsBotConfig({'global_config': {'log_level': 'INFO'}})


@pytest.fixture
def event():
    with open("events/tweet_message.json") as f:
        return json.load(f)


def test_app_normal(event, mocker):
    r = requests.Response()
    r.status_code = 200
    r._content = '{"id_str": "12345"}'.encode()
    res = TwitterAPI.TwitterResponse(r, None)
    mocker.patch('TwitterAPI.TwitterAPI.request', return_value=res)

    ret = app.handle(event, config)
    assert ret == {'Results': {'dummy': '12345'}}


def test_app_already_retweeted(event, mocker):
    r = requests.Response()
    r.status_code = 403
    error = {"errors": [{"code": 187, "message": "Status is a duplicate."}]}
    r._content = json.dumps(error).encode()
    res = TwitterAPI.TwitterResponse(r, None)
    mocker.patch('TwitterAPI.TwitterAPI.request', return_value=res)

    ret = app.handle(event, config)
    assert ret == {'Results': {'dummy': None}}


def test_app_abnormal(event, mocker):
    r = requests.Response()
    r.status_code = 401  # authorization error
    r._content = '{}'.encode()
    res = TwitterAPI.TwitterResponse(r, None)
    mocker.patch('TwitterAPI.TwitterAPI.request', return_value=res)

    with pytest.raises(Exception):
        app.handle(event, config)


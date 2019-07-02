import boto3

from src.collect_tweets import app
from src.layers.shared_files.python.twitter import Tweet, TweetHandleOptions, TwitterList
from src.layers.shared_files.python.message import CollectTweetsMessage
from src.layers.shared_files.python.news_bot_config import NewsBotConfig

sns_client = boto3.client('sns', endpoint_url='http://localstack:4575')
config = NewsBotConfig({'global_config': {'log_level': 'INFO'}})


def test_collect_tweets(mocker):
    mocker.patch('TwitterAPI.TwitterAPI.request', return_value=[{'id': 123}])
    ret = app.collect_tweets(app.twitter_api, TwitterList('slug', 'owner'), 10)
    assert len(ret) == 1
    assert ret[0].id == 123


def test_notify_message():
    app.notify_message(
        sns_client,
        app.target_topic,
        CollectTweetsMessage(Tweet({'id': 1}), TweetHandleOptions()),
        config.logger
    )

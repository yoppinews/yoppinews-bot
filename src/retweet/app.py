# -*- coding: utf-8 -*-

import os
import json

from logging import Logger
from TwitterAPI import TwitterAPI

from message import RetweetMessage
from news_bot_config import NewsBotConfig

# env_vars
stage = os.environ['Stage']
config_bucket = os.environ['ConfigBucket']
config_key_name = os.environ['ConfigKeyName']
consumer_key = os.environ['TwitterConsumerKey']
consumer_secret = os.environ['TwitterConsumerSecret']
access_token_key = os.environ['TwitterAccessTokenKey']
access_token_secret = os.environ['TwitterAccessTokenSecret']

# api clients
twitter = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)


def lambda_handler(event, _):
    config = NewsBotConfig.initialize(stage, config_bucket, config_key_name)
    return handle(event, config)


def handle(event: dict, config: NewsBotConfig):
    records = event['Records']
    ids = []
    for r in records:
        mid = r['Sns']['MessageId']
        ids.append(mid)
        config.logger.info(json.dumps({
            'event': 'app:handle',
            'details': {'MessageId': mid}
        }))
        message = json.loads(r['Sns']['Message'])
        retweet_message = RetweetMessage.of(message)
        retweet(retweet_message, config.logger)
    return {
        'MessageIds': ids
    }


def retweet(message: RetweetMessage, logger: Logger) -> str:
    r = twitter.request('statuses/retweet/:%s' % message.id_str)
    content = json.loads(r.response.content.decode())
    if r.status_code < 200 or r.status_code >= 300:
        logger.error(json.dumps({
            'event': 'retweet:retweet:error',
            'details': content,
        }))
        # ignore error_code 327: You have already retweeted this Tweet.
        if not any(e.get('code', 0) == 327 for e in content.get('errors', [])):
            r.response.raise_for_status()
    else:
        logger.debug(json.dumps({
            'event': 'retweet:retweet:debug',
            'details': content,
        }))
    return message.id_str

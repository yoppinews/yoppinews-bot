# -*- coding: utf-8 -*-

import os
import json
import boto3
import concurrent.futures
from typing import List
from logging import Logger


from TwitterAPI import TwitterAPI

from twitter import TwitterList, Tweet
from message import CollectTweetsMessage
from key_value_store import DDBTableWithLocalCache
from news_bot_config import NewsBotConfig, CollectTweetsListConfig

# env_vars
stage = os.environ['Stage']
config_bucket = os.environ['ConfigBucket']
config_key_name = os.environ['ConfigKeyName']
consumer_key = os.environ['TwitterConsumerKey']
consumer_secret = os.environ['TwitterConsumerSecret']
access_token_key = os.environ['TwitterAccessTokenKey']
access_token_secret = os.environ['TwitterAccessTokenSecret']
target_topic = os.environ['TargetTopic']
ddb_table_name = os.environ['DDBCacheTable']

# api clients
twitter_api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
sns_client = boto3.client('sns') if stage != 'local' \
    else boto3.client('sns', endpoint_url='http://localstack:4575')
ddb = boto3.resource('dynamodb') if stage != 'local' \
    else boto3.resource('dynamodb', endpoint_url='http://localstack:4569')
ddb_table = ddb.Table(ddb_table_name) if stage != 'local' \
    else ddb.Table('CollectTweets')

# cache
ddb_table_with_cache = DDBTableWithLocalCache('original_id', ddb_table)


def lambda_handler(_, __):
    config = NewsBotConfig.initialize(stage, config_bucket, config_key_name)
    ddb_table_with_cache.set_logger(config.logger)
    return handle(config)


def handle(
    config: NewsBotConfig,
    twitter: TwitterAPI = twitter_api,
    cached_ddb_table: DDBTableWithLocalCache = ddb_table_with_cache,
    sns=sns_client
):
    list_configs = config.twitter_target_lists
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pool.map(lambda l: handle_list(twitter, l, cached_ddb_table, sns, config.logger), list_configs)
    return {}


def handle_list(
    api: TwitterAPI,
    list_config: CollectTweetsListConfig,
    cached_ddb_table: DDBTableWithLocalCache,
    sns,
    logger: Logger
):
    tweets = collect_tweets(api, list_config.twitter_list, list_config.count)
    handle_tweets(tweets, list_config, cached_ddb_table, sns, logger)


def collect_tweets(api: TwitterAPI, twitter_list: TwitterList, count: int) -> List[Tweet]:
    res = api.request('lists/statuses', {
        'owner_screen_name': twitter_list.owner_screen_name,
        'slug': twitter_list.slug,
        'count': count,
        'tweet_mode': 'extended',
    })
    return [Tweet(x) for x in res]


def handle_tweets(
    tweet_list: List[Tweet],
    list_config: CollectTweetsListConfig,
    cached_ddb_table: DDBTableWithLocalCache,
    sns,
    logger: Logger,
):
    new = 0
    for status in tweet_list:
        if cached_ddb_table.get(status.original_id):
            continue
        else:
            message = CollectTweetsMessage(status, list_config.options)
            logger.info(message)
            notify_message(sns, target_topic, message, logger)
            cached_ddb_table.put(status.dictionary)
            new += 1
    logger.info(json.dumps({
        'event': 'collect_tweets:handle_tweets:count',
        'details': {
            'list_slug': list_config.twitter_list.slug,
            'list_owner': list_config.twitter_list.owner_screen_name,
            'new': new,
            'sum': len(tweet_list)
        }
    }))


def notify_message(sns, topic: str, message: CollectTweetsMessage, logger: Logger):
    j = json.dumps(message.dictionary, ensure_ascii=False)
    logger.debug(json.dumps({
        'event': 'collect_tweets:notify_message:item',
        'details': message.dictionary
    }, ensure_ascii=False))
    res = sns.publish(
        TopicArn=topic,
        Message=j,
    )
    logger.info(json.dumps({
        'event': 'collect_tweets:notify_message:message_id',
        'details': {'status_original_id': message.tweet.original_id, 'status_id': message.tweet.id, 'return': res}
    }, ensure_ascii=False))


# -*- coding: utf-8 -*-

import os
import json
import boto3
import string
import concurrent.futures
from typing import Optional
from logging import Logger

from tweet_handlers import TweetHandlers
from message import CollectTweetsMessage, RetweetMessage, TweetMessage, \
    DetectRelatedImageMessage, DetectRelatedURLMessage
from news_bot_config import NewsBotConfig
from related_tweet_detector import RelatedTweetDetector

stage = os.environ['Stage']
config_bucket = os.environ['ConfigBucket']
config_key_name = os.environ['ConfigKeyName']
tweet_topic = os.environ['TweetTopic']
retweet_topic = os.environ['RetweetTopic']
detect_related_image = os.environ['DetectImageFunction']
detect_related_url = os.environ['DetectURLFunction']

# api clients
sns_client = boto3.client('sns') if stage != 'local' \
    else boto3.client('sns', endpoint_url='http://localstack:4575')
lambda_client = boto3.client('lambda') if stage != 'local' \
    else boto3.client('lambda', endpoint_url='http://localstack:4574')


def lambda_handler(event, _):
    config = NewsBotConfig.initialize(stage, config_bucket, config_key_name)
    handlers = TweetHandlers(
        retweet_handler=lambda m, k: retweet_handler(m, k, config.logger),
        image_handler=lambda m: image_handler(m, config),
        url_handler=lambda m: url_handler(m, config),
    )
    return handle(event, config, handlers)


def handle(event: dict, config: NewsBotConfig, handlers: TweetHandlers):
    keyword_detector = config.keyword_detector
    tweet_detector = RelatedTweetDetector(keyword_detector)
    records = event['Records']
    messages = [CollectTweetsMessage.of(json.loads(r['body'])) for r in records]
    with concurrent.futures.ThreadPoolExecutor() as pool:
        pool.map(lambda m: handle_message(m, tweet_detector, handlers, config.logger), messages)
    return {}


def handle_message(
    message: CollectTweetsMessage,
    detector: RelatedTweetDetector,
    handlers: TweetHandlers,
    logger: Logger,
):
    result = detector.detect(message.tweet, message.options)
    logger.info(json.dumps({
        'event': 'detect_related_tweet:handle_message',
        'details': {
            'status_id': message.tweet.id,
            'result': result.dictionary
        }
    }, ensure_ascii=False))
    if result.retweet_needed:
        handlers.retweet_handler(message, result.matched_keyword)
    if result.image_detection_needed:
        handlers.image_handler(message)
    if result.url_detection_needed:
        handlers.url_handler(message)


def retweet_handler(message: CollectTweetsMessage, detected_text: Optional[str], logger: Logger):
    m = RetweetMessage(str(message.tweet.original_id), {
        'detector': 'detect_related_tweet',
        'detected_text': detected_text,
    })
    retweet(m, logger)


def image_handler(message: CollectTweetsMessage, config: NewsBotConfig):
    logger = config.logger
    if config.detect_face_source_image_url is None:
        logger.warning(json.dumps({
            'event': 'detect_related_tweet:image_handler',
            'details': 'config.detect_face_source_image_url is None'
        }, ensure_ascii=False))
        return

    for image_url in message.tweet.media_https_urls:
        try:
            payload = json.dumps(DetectRelatedImageMessage(image_url).dictionary).encode('utf-8')
            res = lambda_client.invoke(
                FunctionName=detect_related_image,
                InvocationType='RequestResponse',
                Payload=payload,
            )
            similarity = json.loads(res['Payload'].read().decode("utf-8")).get('similarity', 0)
            dic = {
                'status_id': message.tweet.id,
                'image_url': image_url,
                'similarity': '{0:.2f}'.format(similarity),
                'status_url': message.tweet.status_url,
            }
            logger.debug(json.dumps({
                'event': 'detect_related_tweet:image_handler',
                'details': dic,
            }, ensure_ascii=False))
            if similarity >= config.detect_face_similarity_threshold:
                retweet_message = RetweetMessage(str(message.tweet.original_id), {
                    'detector': 'detect_related_image',
                    'image_url': image_url,
                    'similarity': similarity,
                })
                retweet(retweet_message, logger)
                if config.image_detection_message_template:
                    template = string.Template(json.dumps(config.image_detection_message_template, ensure_ascii=False))
                    status = template.substitute(dic).strip("\"")
                    tweet_message = TweetMessage(status)
                    tweet(tweet_message, logger)
                return
        except Exception as e:
            logger.error(json.dumps({
                'event': 'detect_related_tweet:image_handler:error',
                'details': e.__str__()
            }, ensure_ascii=False))


def url_handler(message: CollectTweetsMessage, config: NewsBotConfig):
    logger = config.logger
    for url in message.tweet.get_urls():
        try:
            payload = json.dumps(DetectRelatedURLMessage(url).dictionary).encode('utf-8')
            res = lambda_client.invoke(
                FunctionName=detect_related_url,
                InvocationType='RequestResponse',
                Payload=payload,
            )
            result = json.loads(res['Payload'].read().decode("utf-8"))
            detected_text = result.get('detected_text', None)
            selector = result.get('selector', None)
            dic = {
                'status_id': message.tweet.id,
                'url': url,
                'detected_text': detected_text,
                'selector': selector,
                'status_url': message.tweet.status_url,
            }
            logger.debug(json.dumps({
                'event': 'detect_related_tweet:url_handler',
                'details': dic
            }, ensure_ascii=False))
            if detected_text is not None:
                retweet_message = RetweetMessage(str(message.tweet.original_id), {
                    'detector': 'detect_related_url',
                    'image_url': url,
                    'detected_text': detected_text,
                })
                retweet(retweet_message, logger)
                if config.url_detection_message_template:
                    template = string.Template(json.dumps(config.url_detection_message_template, ensure_ascii=False))
                    status = template.substitute(dic).strip("\"")
                    tweet_message = TweetMessage(status)
                    tweet(tweet_message, logger)
                return
        except Exception as e:
            logger.error(json.dumps({
                'event': 'detect_related_tweet:url_handler:error',
                'details': e.__str__()
            }, ensure_ascii=False))


def tweet(m: TweetMessage, logger: Logger):
    j = json.dumps(m.dictionary, ensure_ascii=False)
    logger.debug(json.dumps({
        'event': 'detect_related_tweet:tweet:item',
        'details': m.dictionary
    }, ensure_ascii=False))
    res = sns_client.publish(
        TopicArn=tweet_topic,
        Message=j,
    )
    logger.info(json.dumps({
        'event': 'detect_related_tweet:tweet:message_id',
        'details': {'text': m.status, 'return': res}
    }, ensure_ascii=False))


def retweet(m: RetweetMessage, logger: Logger):
    j = json.dumps(m.dictionary, ensure_ascii=False)
    logger.debug(json.dumps({
        'event': 'detect_related_tweet:retweet:item',
        'details': m.dictionary
    }, ensure_ascii=False))
    res = sns_client.publish(
        TopicArn=retweet_topic,
        Message=j,
    )
    logger.info(json.dumps({
        'event': 'detect_related_tweet:retweet:message_id',
        'details': {'status_original_id': m.id_str, 'return': res}
    }, ensure_ascii=False))

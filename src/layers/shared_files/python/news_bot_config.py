# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List, Optional

import yaml
import boto3
import datetime
import logging

from twitter import TwitterList, TweetHandleOptions
from keyword_detector import KeywordDetector


class NewsBotConfig:
    def __init__(self, dic: dict):
        self._dic = dic
        self._logger = NewsBotConfig._get_logger(self.log_level)

    @staticmethod
    def initialize(stage: str, config_bucket: str, config_key_name: str) -> NewsBotConfig:
        bucket = boto3.resource('s3').Bucket(config_bucket) if stage != 'local' \
            else boto3.resource('s3', endpoint_url='http://localstack:4572').Bucket(config_bucket)
        timestamp = datetime.datetime.utcnow().timestamp()
        config_path = '/tmp/config.' + str(timestamp)
        bucket.download_file(config_key_name, config_path)
        f = open(config_path, "r")
        dic = yaml.load(f, Loader=yaml.SafeLoader)
        f.close()
        return NewsBotConfig(dic)

    @property
    def log_level(self) -> str:
        return self._dic.get('global_config', {}).get('log_level', 'INFO')

    @staticmethod
    def _get_logger(log_level):
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        numeric_level = getattr(logging, log_level.upper(), None)
        handler.setLevel(numeric_level)
        logger.setLevel(numeric_level)
        logger.handlers = [handler]
        logger.propagate = False
        return logger

    @property
    def logger(self):
        return self._logger

    @property
    def detect_face_similarity_threshold(self) -> int:
        return self._dic.get('global_config', {}).get('detect_face_similarity_threshold', 99)

    @property
    def detect_face_source_image_url(self) -> Optional[str]:
        return self._dic.get('global_config', {})\
            .get('detect_face_source_image_url', None)

    @property
    def image_detection_message_template(self) -> Optional[str]:
        return self._dic.get('detect_related_tweet', {}).get('image_detection_message_template', None)

    @property
    def twitter_target_lists(self) -> List[CollectTweetsListConfig]:
        lists = self._dic.get('twitter_config', {}).get('target_lists', [])
        result = []
        for l in lists:
            try:
                tw_list = TwitterList(l['slug'], l['owner_screen_name'])
                options = TweetHandleOptions.of(l)
                count = l.get('count', 10)
                result.append(CollectTweetsListConfig(tw_list, options, count))
            except KeyError:
                continue
        return result

    @property
    def keyword_detector(self) -> KeywordDetector:
        keyword_config = self._dic.get('keyword_config', {})
        return KeywordDetector(
            global_keywords=keyword_config.get('keywords', []),
            user_specific_keywords=keyword_config.get('user_related_keywords', {}),
            ignored_users=keyword_config.get('ignored_users', []),
            ignored_keywords=keyword_config.get('ignored_keywords', []),
        )


class CollectTweetsListConfig:
    def __init__(self, twitter_list: TwitterList, options: TweetHandleOptions, count: int):
        self._twitter_list = twitter_list
        self._options = options
        self._count = count

    @property
    def twitter_list(self) -> TwitterList:
        return self._twitter_list

    @property
    def options(self) -> TweetHandleOptions:
        return self._options

    @property
    def count(self) -> int:
        return self._count

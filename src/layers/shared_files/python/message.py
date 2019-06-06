# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional, List

from twitter import Tweet, TweetHandleOptions


class CollectTweetsMessage:
    def __init__(self, tweet: Tweet, options: TweetHandleOptions):
        self._tweet = tweet
        self._options = options

    @staticmethod
    def of(d: dict) -> Optional[CollectTweetsMessage]:
        try:
            tweet = Tweet(d['tweet'])
            options = TweetHandleOptions.of(d['options'])
            return CollectTweetsMessage(tweet, options)
        except KeyError:
            return None

    @property
    def dictionary(self) -> dict:
        return {
            'tweet': self._tweet.dictionary,
            'options': self._options.dictionary,
        }

    @property
    def tweet(self) -> Tweet:
        return self._tweet

    @property
    def options(self) -> TweetHandleOptions:
        return self._options


class RetweetMessage:
    def __init__(self, id_str: str):
        self._id_str = id_str

    @staticmethod
    def of(d: dict) -> Optional[RetweetMessage]:
        try:
            return RetweetMessage(d['id'])
        except KeyError:
            return None

    @property
    def id_str(self):
        return self._id_str


class TweetMessage:
    def __init__(self, status: str):
        self._status = status

    @staticmethod
    def of(d: dict) -> Optional[TweetMessage]:
        try:
            return TweetMessage(d['status'])
        except KeyError:
            return None

    @property
    def status(self):
        return self._status


class DetectRelatedImageMessage:
    def __init__(self, image_url: str):
        self._image_url = image_url

    @staticmethod
    def of(d: dict) -> Optional[DetectRelatedImageMessage]:
        try:
            return DetectRelatedImageMessage(d['image_url'])
        except KeyError:
            return None

    @property
    def image_url(self) -> str:
        return self._image_url

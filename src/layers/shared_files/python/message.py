# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional

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

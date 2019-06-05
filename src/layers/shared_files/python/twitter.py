# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from enum import Enum
from typing import Optional, List


class TwitterList:
    def __init__(self, slug: str, owner_screen_name: str):
        self._slug = slug
        self._owner_screen_name = owner_screen_name

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def owner_screen_name(self) -> str:
        return self._owner_screen_name


class Tweet(object):
    def __init__(self, status: dict):
        self._status = status
        self._status['original_id'] = self.original_id

    @property
    def id(self) -> int:
        return self._status.get('id')

    @property
    def full_text(self) -> str:
        return self._status.get('full_text')

    @property
    def screen_name(self) -> str:
        return self._status['user']['screen_name']

    @property
    def original_id(self) -> int:
        try:
            return self._status['retweeted_status']['id']
        except KeyError:
            return self._status['id']

    @property
    def original_screen_name(self) -> str:
        if self.is_retweet:
            return self._status['retweeted_status']['user']['screen_name']
        else:
            return self._status['user']['screen_name']

    @property
    def is_reply(self) -> bool:
        return 'in_reply_to_status_id' in self._status and isinstance(self._status.get('in_reply_to_status_id'), int)

    @property
    def is_retweet(self) -> bool:
        return 'retweeted_status' in self._status

    @property
    def is_quoted(self) -> bool:
        return 'quoted_status' in self._status

    @property
    def quoted_full_text(self) -> Optional[str]:
        return self._status.get('quoted_status', {}).get('full_text', None)

    @property
    def is_retweeted_by_me(self) -> bool:
        return self._status.get('retweeted') or False

    @property
    def has_media(self) -> bool:
        try:
            media = self._status['entities']['media']
            return isinstance(media, list) and len(media) > 0
        except KeyError:
            return False

    @property
    def media_https_urls(self) -> List[str]:
        try:
            return [medium['media_url_https'] for medium in self._status['extended_entities']['media']]
        except KeyError:
            return []

    @property
    def status_url(self) -> str:
        original_screen_name = self.original_screen_name
        original_id = str(self.original_id)
        return f'https://twitter.com/{original_screen_name}/status/{original_id}'

    @property
    def dictionary(self) -> dict:
        return self._status

    def has_urls(self, include_quoted_tweet=False) -> bool:
        return len(self.get_urls(include_quoted_tweet)) > 0

    def get_urls(self, include_quoted_tweet=False) -> List[str]:
        try:
            return [
                dic['expanded_url']
                for dic
                in self._status['entities']['urls']
                if include_quoted_tweet or not re.match('https://twitter.com/', dic['expanded_url'])
            ]
        except KeyError:
            return []


class TweetEvaluateOption(Enum):
    NONE = 'NONE'
    EVALUATE = 'EVALUATE'
    ALWAYS = 'ALWAYS'


class TweetHandleOptions:
    def __init__(
        self,
        always_retweet: bool = False,
        include_retweet: bool = False,
        include_reply: bool = False,
        include_quoted_text: bool = False,
        evaluate_image: TweetEvaluateOption = TweetEvaluateOption.NONE,
        evaluate_url: TweetEvaluateOption = TweetEvaluateOption.NONE,
    ):
        self._always_retweet = always_retweet
        self._include_retweet = include_retweet
        self._include_reply = include_reply
        self._include_quoted_text = include_quoted_text
        self._evaluate_image = evaluate_image
        self._evaluate_url = evaluate_url

    @staticmethod
    def of(d: dict) -> Optional[TweetHandleOptions]:
        options = TweetHandleOptions(
            always_retweet=d.get('always_retweet', False),
            include_retweet=d.get('include_retweet', False),
            include_reply=d.get('include_reply', False),
            include_quoted_text=d.get('include_quoted_text', False),
            evaluate_image=TweetEvaluateOption[d.get('evaluate_image', 'NONE')],
            evaluate_url=TweetEvaluateOption[d.get('evaluate_url', 'NONE')],
        )
        return options

    @property
    def always_retweet(self) -> bool:
        return self._always_retweet

    @property
    def include_retweet(self) -> bool:
        return self._include_retweet

    @property
    def include_reply(self) -> bool:
        return self._include_reply

    @property
    def include_quoted_text(self) -> bool:
        return self._include_quoted_text

    @property
    def evaluate_image(self) -> TweetEvaluateOption:
        return self._evaluate_image

    @property
    def evaluate_url(self) -> TweetEvaluateOption:
        return self._evaluate_url

    @property
    def dictionary(self) -> dict:
        return {
            'always_retweet': self._always_retweet,
            'include_retweet': self._include_retweet,
            'include_reply': self._include_reply,
            'include_quoted_text': self._include_quoted_text,
            'evaluate_image': self._evaluate_image.name,
            'evaluate_url': self._evaluate_url.name
        }

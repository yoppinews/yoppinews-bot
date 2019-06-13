# -*- coding: utf-8 -*-

from typing import Callable

from message import CollectTweetsMessage


class TweetHandlers:
    def __init__(
        self,
        retweet_handler: Callable[[CollectTweetsMessage], None],
        image_handler: Callable[[CollectTweetsMessage], None],
        url_handler: Callable[[CollectTweetsMessage], None],
    ):
        self._retweet_handler = retweet_handler
        self._image_handler = image_handler
        self._url_handler = url_handler

    @property
    def retweet_handler(self) -> Callable[[CollectTweetsMessage], None]:
        return self._retweet_handler

    @property
    def image_handler(self) -> Callable[[CollectTweetsMessage], None]:
        return self._image_handler

    @property
    def url_handler(self) -> Callable[[CollectTweetsMessage], None]:
        return self._url_handler

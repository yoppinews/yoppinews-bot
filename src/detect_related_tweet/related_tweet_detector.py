# -*- coding: utf-8 -*-

import json
from typing import Optional

from twitter import Tweet, TweetEvaluateOption, TweetHandleOptions
from keyword_detector import KeywordDetector


class RelatedTweetDetectionResult:
    def __init__(
        self,
        matched_keyword: Optional[str] = None,
        retweet_needed: bool = False,
        image_detection_needed: bool = False,
        url_detection_needed: bool = False
    ):
        self._matched_keyword = matched_keyword
        self._retweet_needed = retweet_needed
        self._image_detection_needed = image_detection_needed
        self._url_detection_needed = url_detection_needed

    def __eq__(self, other) -> bool:
        if isinstance(other, RelatedTweetDetectionResult):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    @property
    def matched_keyword(self) -> Optional[str]:
        return self._matched_keyword

    @property
    def retweet_needed(self) -> bool:
        return self._retweet_needed

    @property
    def image_detection_needed(self) -> bool:
        return self._image_detection_needed

    @property
    def url_detection_needed(self) -> bool:
        return self._url_detection_needed

    @property
    def dictionary(self) -> dict:
        return {
            'matched_keyword': self._matched_keyword,
            'retweet_needed': self._retweet_needed,
            'image_detection_needed': self._image_detection_needed,
            'url_detection_needed': self._url_detection_needed,
        }


class RelatedTweetDetector:
    def __init__(self, keyword_detector: KeywordDetector):
        self._keyword_detector = keyword_detector

    def _meet_precondition(self, tweet: Tweet, options: TweetHandleOptions) -> bool:
        if tweet.is_retweeted_by_me:
            return False
        if self._keyword_detector.matched_ignore_condition(tweet.full_text, tweet.original_screen_name):
            return False
        if tweet.is_quoted and \
                self._keyword_detector.matched_ignore_condition(tweet.quoted_full_text, tweet.original_screen_name):
            return False
        return (not tweet.is_retweet or options.include_retweet) and \
               (not tweet.is_reply or options.include_reply)

    @staticmethod
    def _image_detection_needed(tweet: Tweet, has_related_keyword: bool, evaluate_image: TweetEvaluateOption) -> bool:
        if len(tweet.media_https_urls) == 0 or evaluate_image == TweetEvaluateOption.NONE:
            return False
        return not has_related_keyword or evaluate_image == TweetEvaluateOption.ALWAYS

    @staticmethod
    def _url_detection_needed(tweet: Tweet, has_related_keyword: bool, evaluate_image: TweetEvaluateOption) -> bool:
        if len(tweet.get_urls()) == 0 or evaluate_image == TweetEvaluateOption.NONE:
            return False
        return not has_related_keyword or evaluate_image == TweetEvaluateOption.ALWAYS

    def _related_keyword(self, tweet: Tweet, options: TweetHandleOptions) -> Optional[str]:
        if not self._meet_precondition:
            return None
        k = self._keyword_detector.find_related_keyword(tweet.full_text, tweet.screen_name)
        if k is None and tweet.is_quoted and options.include_quoted_text:
            return self._keyword_detector.find_related_keyword(tweet.quoted_full_text, tweet.screen_name)
        return k

    def detect(self, tweet: Tweet, options: TweetHandleOptions) -> RelatedTweetDetectionResult:
        if not self._meet_precondition(tweet, options):
            return RelatedTweetDetectionResult(None, False, False)
        keyword = None
        retweet_needed = options.always_retweet
        if not retweet_needed:
            keyword = self._related_keyword(tweet, options)
            retweet_needed = keyword is not None
        image_detection_needed = self._image_detection_needed(tweet, retweet_needed, options.evaluate_image)
        url_detection_needed = self._url_detection_needed(tweet, retweet_needed, options.evaluate_url)
        return RelatedTweetDetectionResult(keyword, retweet_needed, image_detection_needed, url_detection_needed)

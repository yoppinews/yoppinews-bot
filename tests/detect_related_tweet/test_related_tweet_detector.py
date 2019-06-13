import json
import pytest

from twitter import Tweet, TweetHandleOptions, TweetEvaluateOption
from keyword_detector import KeywordDetector
from src.detect_related_tweet.related_tweet_detector import RelatedTweetDetector, RelatedTweetDetectionResult
from src.layers.shared_files.python.news_bot_config import NewsBotConfig

config = NewsBotConfig({'global_config': {'log_level': 'INFO'}})


@pytest.mark.parametrize(
    'options,expected', [
        (TweetHandleOptions(), RelatedTweetDetectionResult()),
        (TweetHandleOptions(always_retweet=True), RelatedTweetDetectionResult(retweet_needed=True)),
        (TweetHandleOptions(include_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_reply=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_quoted_text=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
    ]
)
def test_tweet_keyword_unmatched(options: TweetHandleOptions, expected: RelatedTweetDetectionResult):
    with open("events/tweets/tweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == expected


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_tweet_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/tweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テスト']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_keywords=['ツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_users=['gomi_ningen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize(
    'options,expected', [
        (TweetHandleOptions(), RelatedTweetDetectionResult()),
        (TweetHandleOptions(always_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(always_retweet=True, include_reply=True), RelatedTweetDetectionResult(retweet_needed=True)),
        (TweetHandleOptions(include_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_reply=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_quoted_text=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
    ]
)
def test_reply_tweet_keyword_unmatched(options: TweetHandleOptions, expected: RelatedTweetDetectionResult):
    with open("events/tweets/reply_tweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == expected


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_reply_tweet_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/reply_tweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テスト']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet and options.include_reply else None,
        retweet_needed=options.include_reply
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet and options.include_reply else None,
        retweet_needed=options.include_reply
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_keywords=['ツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_users=['gomi_ningen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize(
    'options,expected', [
        (TweetHandleOptions(), RelatedTweetDetectionResult()),
        (TweetHandleOptions(always_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(always_retweet=True, include_retweet=True),
         RelatedTweetDetectionResult(retweet_needed=True)),
        (TweetHandleOptions(include_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_reply=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_quoted_text=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
    ]
)
def test_retweet_keyword_unmatched(options: TweetHandleOptions, expected: RelatedTweetDetectionResult):
    with open("events/tweets/retweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == expected


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(always_retweet=True, include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_retweet_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/retweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テスト']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if options.include_retweet and not options.always_retweet else None,
        retweet_needed=options.include_retweet
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if options.include_retweet and not options.always_retweet else None,
        retweet_needed=options.include_retweet
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_keywords=['ツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi2ngen': ['テスト']},
        ignored_users=['gomi2ngen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize(
    'options', [
        TweetHandleOptions(),
        TweetHandleOptions(always_retweet=True),
        TweetHandleOptions(include_retweet=True),
        TweetHandleOptions(always_retweet=True, include_retweet=True),
        TweetHandleOptions(include_reply=True),
        TweetHandleOptions(include_quoted_text=True),
        TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
        TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
        TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
        TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
    ]
)
def test_retweeted_tweet_keyword_unmatched(options: TweetHandleOptions):
    with open("events/tweets/retweeted_tweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(always_retweet=True, include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_retweeted_tweet_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/retweeted_tweet.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テスト']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_keywords=['ツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi2ngen': ['テスト']},
        ignored_users=['gomi2ngen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize(
    'options,expected', [
        (TweetHandleOptions(), RelatedTweetDetectionResult()),
        (
            TweetHandleOptions(always_retweet=True),
            RelatedTweetDetectionResult(retweet_needed=True)
        ),
        (
            TweetHandleOptions(always_retweet=True, include_retweet=True),
            RelatedTweetDetectionResult(retweet_needed=True)
        ),
        (TweetHandleOptions(include_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_reply=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_quoted_text=True), RelatedTweetDetectionResult()),
        (
            TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
            RelatedTweetDetectionResult(image_detection_needed=True)
        ),
        (
            TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
            RelatedTweetDetectionResult(image_detection_needed=True)
        ),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
    ]
)
def test_tweet_with_image_keyword_unmatched(options: TweetHandleOptions, expected: RelatedTweetDetectionResult):
    with open("events/tweets/tweet_with_image.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == expected


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(always_retweet=True, include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_tweet_with_image_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/tweet_with_image.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テスト']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True,
        image_detection_needed=options.evaluate_image == TweetEvaluateOption.ALWAYS
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True,
        image_detection_needed=options.evaluate_image == TweetEvaluateOption.ALWAYS
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_keywords=['ツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi2ngen': ['テスト']},
        ignored_users=['gomi_ningen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize(
    'options,expected', [
        (TweetHandleOptions(), RelatedTweetDetectionResult()),
        (TweetHandleOptions(always_retweet=True), RelatedTweetDetectionResult(retweet_needed=True)),
        (TweetHandleOptions(include_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_reply=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_quoted_text=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
    ]
)
def test_tweet_with_quoted_text_keyword_unmatched(options: TweetHandleOptions, expected: RelatedTweetDetectionResult):
    with open("events/tweets/tweet_with_quoted_text.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == expected


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_tweet_with_quoted_text_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/tweet_with_quoted_text.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テストツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テストツイート' if options.include_quoted_text else None,
        retweet_needed=True if options.include_quoted_text or options.always_retweet else False
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テストツイート']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テストツイート' if options.include_quoted_text else None,
        retweet_needed=True if options.include_quoted_text or options.always_retweet else False
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テストツイート']},
        ignored_keywords=['テストツイ']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テストツイート']},
        ignored_users=['gomi_ningen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize(
    'options,expected', [
        (TweetHandleOptions(), RelatedTweetDetectionResult()),
        (
            TweetHandleOptions(always_retweet=True),
            RelatedTweetDetectionResult(retweet_needed=True)
        ),
        (
            TweetHandleOptions(always_retweet=True, include_retweet=True),
            RelatedTweetDetectionResult(retweet_needed=True)
        ),
        (TweetHandleOptions(include_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_reply=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_quoted_text=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE), RelatedTweetDetectionResult()),
        (TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS), RelatedTweetDetectionResult()),
        (
            TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
            RelatedTweetDetectionResult(url_detection_needed=True)
        ),
        (
            TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
            RelatedTweetDetectionResult(url_detection_needed=True)
        ),
    ]
)
def test_tweet_with_url_keyword_unmatched(options: TweetHandleOptions, expected: RelatedTweetDetectionResult):
    with open("events/tweets/tweet_with_url.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == expected


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(always_retweet=True, include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_tweet_with_url_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/tweet_with_url.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テスト']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True,
        url_detection_needed=options.evaluate_url == TweetEvaluateOption.ALWAYS
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True,
        url_detection_needed=options.evaluate_url == TweetEvaluateOption.ALWAYS
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_keywords=['ツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi2ngen': ['テスト']},
        ignored_users=['gomi_ningen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()


@pytest.mark.parametrize(
    'options,expected', [
        (TweetHandleOptions(), RelatedTweetDetectionResult()),
        (
            TweetHandleOptions(always_retweet=True),
            RelatedTweetDetectionResult(retweet_needed=True)
        ),
        (
            TweetHandleOptions(always_retweet=True, include_retweet=True),
            RelatedTweetDetectionResult(retweet_needed=True)
        ),
        (TweetHandleOptions(include_retweet=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_reply=True), RelatedTweetDetectionResult()),
        (TweetHandleOptions(include_quoted_text=True), RelatedTweetDetectionResult()),
        (
            TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
            RelatedTweetDetectionResult(image_detection_needed=True)
        ),
        (
            TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
            RelatedTweetDetectionResult(image_detection_needed=True)
        ),
        (
            TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE, evaluate_url=TweetEvaluateOption.EVALUATE),
            RelatedTweetDetectionResult(image_detection_needed=True, url_detection_needed=True)
        ),
        (
            TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS, evaluate_url=TweetEvaluateOption.ALWAYS),
            RelatedTweetDetectionResult(image_detection_needed=True, url_detection_needed=True)
        ),
        (
            TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
            RelatedTweetDetectionResult(url_detection_needed=True)
        ),
        (
            TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
            RelatedTweetDetectionResult(url_detection_needed=True)
        ),
    ]
)
def test_tweet_with_image_and_url_keyword_unmatched(options: TweetHandleOptions, expected: RelatedTweetDetectionResult):
    with open("events/tweets/tweet_with_image_and_url.json") as f:
        j = json.load(f)
    tweet = Tweet(j)
    keyword_detector = KeywordDetector(global_keywords=['hogefuga'])
    d = RelatedTweetDetector(keyword_detector)
    res = d.detect(tweet, options)
    assert res == expected


@pytest.mark.parametrize('options', [
    TweetHandleOptions(),
    TweetHandleOptions(always_retweet=True),
    TweetHandleOptions(include_retweet=True),
    TweetHandleOptions(always_retweet=True, include_retweet=True),
    TweetHandleOptions(include_reply=True),
    TweetHandleOptions(include_quoted_text=True),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_image=TweetEvaluateOption.ALWAYS),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.EVALUATE),
    TweetHandleOptions(evaluate_url=TweetEvaluateOption.ALWAYS),
])
def test_tweet_with_image_and_url_keyword_matched(options: TweetHandleOptions):
    with open("events/tweets/tweet_with_image_and_url.json") as f:
        j = json.load(f)
    tweet = Tweet(j)

    res = RelatedTweetDetector(KeywordDetector(
        global_keywords=['テスト']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True,
        image_detection_needed=options.evaluate_image == TweetEvaluateOption.ALWAYS,
        url_detection_needed=options.evaluate_url == TweetEvaluateOption.ALWAYS
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']}
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult(
        matched_keyword='テスト' if not options.always_retweet else None,
        retweet_needed=True,
        image_detection_needed=options.evaluate_image == TweetEvaluateOption.ALWAYS,
        url_detection_needed=options.evaluate_url == TweetEvaluateOption.ALWAYS
    )
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi_ningen': ['テスト']},
        ignored_keywords=['ツイート']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()
    res = RelatedTweetDetector(KeywordDetector(
        user_specific_keywords={'gomi2ngen': ['テスト']},
        ignored_users=['gomi_ningen']
    )).detect(tweet, options)
    assert res == RelatedTweetDetectionResult()

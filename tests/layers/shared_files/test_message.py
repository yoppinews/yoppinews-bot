from src.layers.shared_files.python.twitter import Tweet, TweetHandleOptions, TweetEvaluateOption
from src.layers.shared_files.python.message import CollectTweetsMessage


def test_collect_tweets_message_init():
    tweet = Tweet({'id': 1234})
    options = TweetHandleOptions()
    message = CollectTweetsMessage(tweet, options)
    assert message.tweet == tweet
    assert message.options == options
    assert message.dictionary == {
        'tweet': tweet.dictionary,
        'options': options.dictionary,
    }


def test_collect_tweets_message_of():
    message = CollectTweetsMessage.of({
        'tweet': {'id': 1234},
        'options': {}
    })
    assert message.tweet.id == 1234
    assert not message.options.always_retweet
    assert not message.options.include_retweet
    assert not message.options.include_reply
    assert not message.options.include_quoted_text
    assert message.options.evaluate_url.value == TweetEvaluateOption.NONE.value
    assert message.options.evaluate_image.value == TweetEvaluateOption.NONE.value

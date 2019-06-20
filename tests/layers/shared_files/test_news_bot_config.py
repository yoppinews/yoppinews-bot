from src.layers.shared_files.python.news_bot_config import NewsBotConfig


def test_config_default():
    config = NewsBotConfig({})
    assert config.log_level == 'INFO'
    assert config.detect_face_similarity_threshold == 99
    assert config.detect_face_source_image_url is None
    assert config.twitter_target_lists == []
    assert config.image_detection_message_template is None


def test_image_detection_message_template():
    config = NewsBotConfig({'detect_related_tweet': {'image_detection_message_template': 'template'}})
    assert config.image_detection_message_template == 'template'

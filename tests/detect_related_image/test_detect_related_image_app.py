import json
import pytest

from src.detect_related_image import app
from src.layers.shared_files.python.news_bot_config import NewsBotConfig

config = NewsBotConfig({'global_config': {'log_level': 'INFO'}})


@pytest.fixture
def event():
    with open("events/detect_related_image_message.json") as f:
        return json.load(f)


def test_app_normal(event, mocker):
    mocker.patch('src.detect_related_image.app.detect_related_image', return_value=95)

    ret = app.handle(event, b'image', 90, None, config.logger)
    assert ret == {'similarity': 95}

import json
import pytest

from src.detect_related_url import app
from src.layers.shared_files.python.news_bot_config import NewsBotConfig
from message import DetectRelatedURLMessage

config = NewsBotConfig({
    'global_config': {'log_level': 'INFO'},
    'detect_related_url': {
        'selectors': {
            'http(s)?://example.com': 'body'
        }
    },
    'keyword_config': {
        'keywords': [
            'hoge'
        ]
    }
})


@pytest.fixture
def event():
    with open("events/detect_related_url_message.json") as f:
        return json.load(f)


def test_app_normal(event, mocker):
    url = 'http://example.com'
    selector = 'body'
    keyword = 'hoge'

    mocker.patch('src.detect_related_url.app.get_selected_text', return_value=keyword)

    m = DetectRelatedURLMessage(url)
    ret = app.handle(m, selector, {}, config)
    assert ret == {
        'url': url,
        'selector': selector,
        'detected_text': keyword,
    }

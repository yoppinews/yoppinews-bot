from src.detect_related_url.css_selectors import CSSSelector


def test_get_selector():
    s = CSSSelector(
        selectors={
            'http(s)?://53ningen.com/hoge': '.wrapper',
            'http(s)?://53ningen.com/fuga': 'article'
        },
        ignored_urls=[
            'http(s)?://example.com'
        ]
    )
    assert s.get_selector('https://53ningen.com/hoge') == '.wrapper'
    assert s.get_selector('https://53ningen.com/hoge/fuga') == '.wrapper'
    assert s.get_selector('http://53ningen.com/hoge/fuga') == '.wrapper'
    assert s.get_selector('http://53ningen.com/hoge') == '.wrapper'
    assert s.get_selector('https://53ningen.com/fuga/hoge') == 'article'
    assert s.get_selector('https://53ningen.com/fuga') == 'article'
    assert s.get_selector('http://53ningen.com/fuga/hoge') == 'article'
    assert s.get_selector('http://53ningen.com/fuga') == 'article'
    assert s.get_selector('https://example.com') is None
    assert s.get_selector('https://example.com/hoge/fuga') is None
    assert s.get_selector('http://example.com') is None
    assert s.get_selector('http://example.com/hoge/fuga') is None


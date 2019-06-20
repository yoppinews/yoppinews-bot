from src.layers.shared_files.python.keyword_detector import KeywordDetector


def test_keyword_detector_global_keyword():
    d = KeywordDetector(['word'], {}, [])
    assert d.find_related_keyword('contains related keyword') == 'word'
    assert d.find_related_keyword('non-related text') is None


def test_keyword_detector_user_related_keyword():
    d = KeywordDetector(['hoge'], {'user1': ['test']}, [])
    assert d.find_related_keyword('test', 'user1') == 'test'
    assert d.find_related_keyword('test', 'user2') is None
    assert d.find_related_keyword('fuga', 'user1') is None
    assert d.find_related_keyword('fuga', 'user2') is None


def test_keyword_detector_ignored_keywords():
    d = KeywordDetector(
        global_keywords=['hoge'],
        user_specific_keywords={'user1': ['test']},
        ignored_keywords=['ge', 'st'],
    )
    assert d.find_related_keyword('test', 'user1') is None
    assert d.find_related_keyword('test', 'user2') is None
    assert d.find_related_keyword('hoge', 'user1') is None
    assert d.find_related_keyword('hoge', 'user2') is None


def test_keyword_detector_ignored_users():
    d = KeywordDetector(
        global_keywords=['hoge'],
        user_specific_keywords={'user1': ['test']},
        ignored_users=['user1', 'user2']
    )
    assert d.find_related_keyword('test', 'user1') is None
    assert d.find_related_keyword('test', 'user2') is None
    assert d.find_related_keyword('hoge', 'user1') is None
    assert d.find_related_keyword('hoge', 'user2') is None

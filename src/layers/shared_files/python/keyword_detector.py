# -*- coding: utf-8 -*-

from typing import Optional, List, Dict


class KeywordDetector:
    def __init__(
        self,
        global_keywords: List[str] = None,
        user_specific_keywords: Dict[str, List[str]] = None,
        ignored_keywords: List[str] = None,
        ignored_users: List[str] = None,
    ):
        self._global_keywords = global_keywords or []
        self._user_specific_keywords = user_specific_keywords or {}
        self._ignored_keywords = ignored_keywords or []
        self._ignored_users = ignored_users or []

    @property
    def global_keywords(self) -> List[str]:
        return self._global_keywords

    @property
    def user_specific_keywords(self) -> Dict[str, List[str]]:
        return self._user_specific_keywords

    @property
    def ignored_keywords(self) -> List[str]:
        return self._ignored_keywords

    @property
    def ignored_users(self) -> List[str]:
        return self._ignored_users

    def matched_ignore_condition(self, text: str, user_id: str = '') -> bool:
        return user_id in self._ignored_users or \
               any([text.count(k) for k in self._ignored_keywords])

    def find_related_keyword(self, text: str, user_id: str = '') -> Optional[str]:
        if self.matched_ignore_condition(text, user_id):
            return None
        for k in self.global_keywords:
            if text.count(k):
                return k
        for k in self._user_specific_keywords.get(user_id, []):
            if k in text:
                return k
        return None

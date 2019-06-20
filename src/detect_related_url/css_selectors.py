# -*- coding: utf-8 -*-

import re
from typing import Dict, List, Optional


class CSSSelector:
    def __init__(self, selectors: Dict[str, str], ignored_urls: List[str]):
        self._selectors = selectors
        self._ignored_urls = ignored_urls

    def get_selector(self, url: str) -> Optional[str]:
        for u in self._ignored_urls:
            if re.match(u, url):
                return None
        for reg, selector in self._selectors.items():
            if re.match(reg, url):
                return selector
        return 'body'

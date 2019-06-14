# -*- coding: utf-8 -*-

import os
import json
from typing import Optional
from logging import Logger

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions

from message import DetectRelatedURLMessage
from css_selectors import CSSSelector
from news_bot_config import NewsBotConfig

stage = os.environ['Stage']
config_bucket = os.environ['ConfigBucket']
config_key_name = os.environ['ConfigKeyName']

web_driver = None


def lambda_handler(event, _):
    config = NewsBotConfig.initialize(stage, config_bucket, config_key_name)
    global web_driver
    if web_driver is None:
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--log-level=0")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-application-cache")
        options.add_argument('--disable-popup-blocking')
        options.add_argument("--disable-infobars")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--enable-logging")
        options.add_argument("--v=99")
        options.add_argument("--single-process")
        options.add_argument("--ignore-certificate-errors")
        options.binary_location = "/opt/bin/headless-chromium"
        web_driver = Chrome(executable_path="/opt/bin/chromedriver", chrome_options=options)
    message = DetectRelatedURLMessage.of(event)
    s = CSSSelector(config.detect_url_selectors, config.detect_url_ignored_urls)
    selector = s.get_selector(message.url)
    return handle(message, selector, web_driver, config)


def handle(message: DetectRelatedURLMessage, selector: str, driver: Chrome, config: NewsBotConfig):
    url = message.url
    logger = config.logger
    text = get_selected_text(url, selector, driver, logger)
    detected_text = config.keyword_detector.find_related_keyword(text)
    res = {
        'url': url,
        'selector': selector,
        'detected_text': detected_text,
    }
    logger.info(json.dumps(res, ensure_ascii=False))
    return res


def get_selected_text(url: str, selector: str, driver: Chrome, logger: Logger) -> Optional[str]:
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selector)))
        return driver.find_element_by_css_selector(selector).text
    except TimeoutException as e:
        logger.error(json.dumps({
            'event': 'detect_related_url:get_selected_text:timeout',
            'details': {
                'url': url,
                'selector': selector,
                'error': e.__str__()
            }
        }, ensure_ascii=False))
        return None

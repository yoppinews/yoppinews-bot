# -*- coding: utf-8 -*-

import json
import decimal
import datetime
from logging import Logger
from typing import Optional
from botocore.exceptions import ClientError


class InMemoryKeyValueStore:
    def __init__(self, dic: Optional[dict] = None):
        self.dic = dic or {}

    def get(self, key: object) -> Optional[object]:
        return self.dic.get(key, None)

    def put(self, key: object, item: object):
        self.dic[key] = item


class DDBTableWithLocalCache:
    def __init__(self, hash_key_name: str, ddb_table, in_memory_cache: InMemoryKeyValueStore = InMemoryKeyValueStore({})):
        self._hash_key_name = hash_key_name
        self._in_memory_cache = in_memory_cache
        self._table = ddb_table
        self._logger: Optional[Logger] = None

    def set_logger(self, logger: Logger):
        self._logger = logger

    @property
    def _has_logger(self) -> bool:
        return self._logger is not None

    def get(self, key: object) -> Optional[object]:
        local_cache = self._in_memory_cache.get(key)
        if local_cache:
            if self._has_logger:
                self._logger.debug(json.dumps({
                    'event': 'DDBTableWithLocalCache:get',
                    'details': {'key': key, 'local_cache': True, 'remote_cache': False}
                }))
            return local_cache
        try:
            res = self._table.get_item(Key={self._hash_key_name: key})
            if 'Item' not in res:
                if self._has_logger:
                    self._logger.debug(json.dumps({
                        'event': 'DDBTableWithLocalCache:get',
                        'details': {'key': key, 'local_cache': False, 'remote_cache': False}
                    }))
                return None

            if self._has_logger:
                self._logger.debug(json.dumps({
                    'event': 'DDBTableWithLocalCache:get',
                    'details': {'key': key, 'local_cache': False, 'remote_cache': True}
                }))
            item = res['Item']
            self._in_memory_cache.put(key, item)
            return item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                if self._has_logger:
                    self._logger.debug(json.dumps({
                        'event': 'DDBTableWithLocalCache:get',
                        'details': {'key': key, 'local_cache': False, 'remote_cache': False}
                    }))
                return None
            else:
                raise

    def put(self, item: dict, ttl: int = 60 * 60 * 24 * 14):
        key = item.get(self._hash_key_name)
        if self.get(key) is not None:
            return
        item['ttl'] = datetime.datetime.utcnow().timestamp() + ttl
        storable = self._to_storable(item)
        res = self._table.put_item(Item=storable)
        self._in_memory_cache.put(key, storable)
        if self._has_logger:
            self._logger.debug(json.dumps({
                'event': 'DDBTableWithLocalCache:put',
                'details': {'key': key, 'ddb_response': res}
            }))

    @staticmethod
    def _to_storable(item: object) -> object:
        text = json.dumps(item, ensure_ascii=False)
        text = text.replace(': ""', ':null')
        return json.loads(text, parse_float=decimal.Decimal)

import boto3

from src.layers.shared_files.python.key_value_store import InMemoryKeyValueStore, DDBTableWithLocalCache


def test_in_memory_key_value_store_get_put():
    s = InMemoryKeyValueStore()
    assert s.get('key') is None
    s.put('key1', 'value1')
    assert s.get('key1') == 'value1'
    s.put('key1', 'value2')
    assert s.get('key1') == 'value2'
    obj = {'k': 'v'}
    s.put('key2', obj)
    assert s.get('key2') == obj


def test_ddb_table_with_local_cache_get_put():
    ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:4569')
    table_name = 'test_ddb_table_with_local_cache_get_put'
    try:
        table = ddb.create_table(
            TableName="test_ddb_table_with_local_cache_get_put",
            KeySchema=[{
                'AttributeName': 'hash_key',
                'KeyType': 'HASH'
            }],
            AttributeDefinitions=[{
                'AttributeName': 'hash_key',
                'AttributeType': 'S'
            }],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        obj1 = {'hash_key': 'k1', 'k1': 'v1'}
        obj2 = {'hash_key': 'k2', 'k2': 'v2'}
        in_memory = InMemoryKeyValueStore()
        s = DDBTableWithLocalCache('hash_key', table, in_memory)
        assert s.get('key') is None
        assert in_memory.get('key') is None
        s.put(obj1)
        assert s.get('k1')['k1'] == obj1['k1']
        assert in_memory.get('k1')['k1'] == obj1['k1']
        s.put(obj2)
        assert s.get('k2')['k2'] == obj2['k2']
    finally:
        ddb.Table(table_name).delete()



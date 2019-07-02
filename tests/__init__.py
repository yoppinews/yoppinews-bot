import os

os.environ['Stage'] = 'local'
os.environ['ConfigBucket'] = 'news-bot'
os.environ['ConfigKeyName'] = 'config.json'
os.environ['TwitterConsumerKey'] = 'dummy'
os.environ['TwitterConsumerSecret'] = 'dummy'
os.environ['TwitterAccessTokenKey'] = 'dummy'
os.environ['TwitterAccessTokenSecret'] = 'dummy'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy'
os.environ['AWS_ACCESS_KEY_ID'] = 'dummy'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['TargetTopic'] = 'arn:aws:sns:us-east-1:123456789012:TestTopic'
os.environ['DDBCacheTable'] = 'CollectTweets'

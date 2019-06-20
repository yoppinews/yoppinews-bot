import os
import sys

os.environ['TargetTopic'] = 'arn:sns:dummy'
os.environ['DDBCacheTable'] = 'CollectTweets'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../../src/layers/shared_files/python/"))

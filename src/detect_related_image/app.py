# -*- coding: utf-8 -*-

import os
import json
import boto3
import requests
from logging import Logger
from botocore.exceptions import ClientError

from message import DetectRelatedImageMessage
from news_bot_config import NewsBotConfig

stage = os.environ['Stage']
config_bucket = os.environ['ConfigBucket']
config_key_name = os.environ['ConfigKeyName']

rekognition_cli = boto3.client('rekognition', region_name='us-east-1')

source_img = None


def lambda_handler(event, _):
    config = NewsBotConfig.initialize(stage, config_bucket, config_key_name)
    config.logger.info(json.dumps({
        'event': 'detect_related_image:lambda_handler:event',
        'details': event,
    }))
    try:
        global source_img
        if source_img is None:
            source_img = requests.get(config.detect_face_source_image_url).content
        return handle(event, source_img, config.detect_face_similarity_threshold, rekognition_cli, config.logger)
    except Exception as e:
        config.logger.error(json.dumps({
            'event': 'detect_related_image:detect_related_image',
            'details': e.__str__()
        }))
        raise e


def handle(event: dict, source_image: bytes, similarity_threshold: int, rekognition, logger: Logger):
    message = DetectRelatedImageMessage.of(event)
    similarity = detect_related_image(message, source_image, similarity_threshold, rekognition, logger)
    return {'similarity': similarity}


def detect_related_image(
    message: DetectRelatedImageMessage,
    source_image: bytes,
    similarity_threshold: int,
    rekognition,
    logger: Logger
) -> int:
    try:
        target_image = requests.get(message.image_url).content
        res = rekognition.compare_faces(
            SourceImage={'Bytes': source_image},
            TargetImage={'Bytes': target_image},
            SimilarityThreshold=similarity_threshold
        )
        logger.debug(json.dumps({
            'event': 'detect_related_image:detect_related_image',
            'details': res
        }))
        if res['FaceMatches'] is None or len(list(res['FaceMatches'])) == 0:
            return 0
        return res['FaceMatches'][0]['Similarity']
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', None)
        expected_error_codes = [
            'InvalidParameterException',
            'InvalidImageFormatException',
            'ImageTooLargeException'
        ]
        if error_code and error_code in expected_error_codes:
            return 0
        else:
            raise

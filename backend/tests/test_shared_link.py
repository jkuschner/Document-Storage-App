import copy
import json
import os
import time

import boto3
import pytest
from moto import mock_aws

os.environ['SHARED_LINKS_TABLE'] = 'test-shared-links-table'
os.environ['FILE_BUCKET'] = 'test-file-bucket'

from lambda_functions.shared_link.handler import lambda_handler #noqa: E402

@pytest.fixture
def aws_env():
    """Single mock_aws fixture to cover DynamoDB + S3."""
    with mock_aws():
        yield


@pytest.fixture
def dynamodb_table(aws_env):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.create_table(
        TableName='test-shared-links-table',
        KeySchema=[{'AttributeName': 'shareToken', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'shareToken', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST',
    )
    return table


@pytest.fixture
def s3_bucket(aws_env):
    s3 = boto3.client('s3', region_name='us-west-2')
    s3.create_bucket(Bucket='test-file-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )
    s3.put_object(
        Bucket='test-file-bucket',
        Key='test-user/test-file/document.pdf',
        Body=b'test-content',
    )
    return s3


@pytest.fixture
def valid_share_record():
    return {
        'shareToken': 'valid-link-123',
        'fileId': 'file-456',
        'userId': 'test-user-123',
        's3Key': 'test-user/test-file/document.pdf',
        'fileName': 'document.pdf',
        'expiresAt': int(time.time()) + 3600,
    }


@pytest.fixture
def expired_share_record():
    return {
        'shareToken': 'expired-link-456',
        'fileId': 'file-789',
        'userId': 'test-user-123',
        's3Key': 'test-user/old-file/expired.pdf',
        'fileName': 'expired.pdf',
        'expiresAt': int(time.time()) - 3600,
    }


def test_shared_link_success(dynamodb_table, s3_bucket, valid_share_record):
    dynamodb_table.put_item(Item=valid_share_record)

    event = {'pathParameters': {'linkId': 'valid-link-123'}}
    response = lambda_handler(event, None)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['fileName'] == 'document.pdf'

    assert 'downloadUrl' in body
    download_url = body['downloadUrl']
    assert (
        'X-Amz-Algorithm' in download_url          # real AWS SigV4
        or 'AWSAccessKeyId' in download_url         # Moto SigV2
        or 'Signature' in download_url              # Moto SigV2
    )

    assert body['expiresAt'] == valid_share_record['expiresAt']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'


def test_shared_link_missing_link_id(dynamodb_table):
    event = {'pathParameters': {}}
    response = lambda_handler(event, None)
    assert response['statusCode'] == 400


def test_shared_link_not_found(dynamodb_table):
    event = {'pathParameters': {'linkId': 'missing-link'}}
    response = lambda_handler(event, None)
    assert response['statusCode'] == 404


def test_shared_link_expired(dynamodb_table, expired_share_record):
    dynamodb_table.put_item(Item=expired_share_record)
    event = {'pathParameters': {'linkId': 'expired-link-456'}}
    response = lambda_handler(event, None)
    assert response['statusCode'] == 404
    assert 'expired' in json.loads(response['body'])['error'].lower()


def test_shared_link_missing_s3_key(dynamodb_table):
    invalid_record = {
        'linkId': 'invalid-link-789',
        'fileId': 'file-123',
        'fileName': 'test.pdf',
        'expiresAt': int(time.time()) + 3600,
    }
    dynamodb_table.put_item(Item=invalid_record)

    event = {'pathParameters': {'linkId': 'invalid-link-789'}}
    response = lambda_handler(event, None)
    assert response['statusCode'] == 500


def test_shared_link_presigned_url_format(dynamodb_table, s3_bucket, valid_share_record):
    record = copy.deepcopy(valid_share_record)
    record['linkId'] = 'format-link'
    dynamodb_table.put_item(Item=record)

    event = {'pathParameters': {'linkId': 'format-link'}}
    response = lambda_handler(event, None)
    body = json.loads(response['body'])
    download_url = body['downloadUrl']

    assert 'test-file-bucket' in download_url
    assert 'X-Amz-Credential' in download_url
    assert 'X-Amz-Expires' in download_url
    assert 'X-Amz-Signature' in download_url
    assert 'response-content-disposition' in download_url.lower()
    assert 'document.pdf' in download_url


def test_shared_link_cors_headers(dynamodb_table):
    event = {'pathParameters': {'linkId': 'missing'}}
    response = lambda_handler(event, None)
    headers = response['headers']
    assert headers['Access-Control-Allow-Origin'] == '*'
    assert 'Access-Control-Allow-Headers' in headers
    assert 'Access-Control-Allow-Methods' in headers


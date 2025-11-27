import copy
import json
import os
from datetime import datetime, timedelta

import boto3
import pytest
from moto import mock_aws

os.environ['FILES_TABLE_NAME'] = 'test-files-table'
os.environ['SHARED_LINKS_TABLE_NAME'] = 'test-shared-links-table'
os.environ['SHARE_BASE_URL'] = 'https://api.example.com/test'

from lambda_functions.share_file.handler import lambda_handler  # noqa: E402

@pytest.fixture
def aws_env():
    with mock_aws():
        yield


@pytest.fixture
def dynamodb_tables(aws_env):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    files_table = dynamodb.create_table(
        TableName='test-files-table',
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'},
            {'AttributeName': 'fileId', 'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {'AttributeName': 'fileId', 'AttributeType': 'S'},
        ],
        BillingMode='PAY_PER_REQUEST',
    )

    shared_links_table = dynamodb.create_table(
        TableName='test-shared-links-table',
        KeySchema=[{'AttributeName': 'linkId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'linkId', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST',
    )

    return files_table, shared_links_table

@pytest.fixture
def sample_file_record():
    return {
        'userId': 'test-user-123',
        'fileId': 'file-456',
        'fileName': 'document.pdf',
        's3Key': 'test-user-123/file-456/document.pdf',
        'uploadedAt': '2025-11-17T10:00:00Z',
    }


@pytest.fixture
def valid_event():
    return {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'test-user-123',
                }
            }
        },
        'pathParameters': {
            'fileId': 'file-456',
        },
        'body': json.dumps({'expirationHours': 24}),
    }


def test_share_file_success(dynamodb_tables, sample_file_record, valid_event):
    files_table, shared_links_table = dynamodb_tables
    files_table.put_item(Item=sample_file_record)

    response = lambda_handler(valid_event, None)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['shareUrl'].startswith('https://api.example.com/test/shared/')
    assert 'expiresAt' in body

    link_id = body['shareUrl'].split('/')[-1]
    record = shared_links_table.get_item(Key={'linkId': link_id})
    assert 'Item' in record
    assert record['Item']['fileId'] == 'file-456'
    assert record['Item']['userId'] == 'test-user-123'
    assert record['Item']['s3Key'] == sample_file_record['s3Key']
    assert record['Item']['fileName'] == sample_file_record['fileName']


def test_share_file_missing_jwt_claims(valid_event):
    event = copy.deepcopy(valid_event)
    event['requestContext'] = {}

    response = lambda_handler(event, None)
    assert response['statusCode'] == 401
    assert 'Unauthorized' in json.loads(response['body'])['error']


def test_share_file_missing_file_id(valid_event):
    event = copy.deepcopy(valid_event)
    event['pathParameters'] = {}

    response = lambda_handler(event, None)
    assert response['statusCode'] == 400


def test_share_file_not_found(dynamodb_tables, valid_event):
    _, _ = dynamodb_tables
    response = lambda_handler(valid_event, None)
    assert response['statusCode'] == 404


def test_share_file_wrong_owner(dynamodb_tables, sample_file_record, valid_event):
    files_table, _ = dynamodb_tables
    files_table.put_item(Item=sample_file_record)

    event = copy.deepcopy(valid_event)
    event['requestContext']['authorizer']['claims']['sub'] = 'other-user'

    response = lambda_handler(event, None)
    assert response['statusCode'] == 404


def test_share_file_custom_expiration(dynamodb_tables, sample_file_record, valid_event):
    files_table, _ = dynamodb_tables
    files_table.put_item(Item=sample_file_record)

    event = copy.deepcopy(valid_event)
    event['body'] = json.dumps({'expirationHours': 48})

    response = lambda_handler(event, None)
    body = json.loads(response['body'])
    expires_at = datetime.fromisoformat(body['expiresAt'].replace('Z', '+00:00'))
    expected = datetime.utcnow() + timedelta(hours=48)
    assert abs((expires_at - expected).total_seconds()) < 10


def test_share_file_expiration_clamping(dynamodb_tables, sample_file_record, valid_event):
    files_table, _ = dynamodb_tables
    files_table.put_item(Item=sample_file_record)

    event = copy.deepcopy(valid_event)
    event['body'] = json.dumps({'expirationHours': 0})
    assert lambda_handler(event, None)['statusCode'] == 200

    event['body'] = json.dumps({'expirationHours': 1000})
    assert lambda_handler(event, None)['statusCode'] == 200
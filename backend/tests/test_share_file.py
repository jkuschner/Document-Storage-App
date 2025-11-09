# tests/test_share_file.py
import json
import os
import pytest
import boto3
from moto import mock_aws

from lambda_functions.share_file.handler import lambda_handler

#TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_USER_ID = 'test-user'
TEST_FILENAME = 'document_to_share.txt'
TEST_FILE_ID = 'abc123'
FILES_TABLE = 'files-dev'
LINKS_TABLE = 'SharedLinksTable-dev'


MOCK_EVENT = {
        'pathParameters': {'fileId': TEST_FILE_ID},
        'queryStringParameters': {'userId': TEST_USER_ID},
        'body': json.dumps({'expirationHours': 2})
}

@mock_aws
def test_share_file_url_is_generated():
    """
    Tests that the handler successfully generates a presigned URL and verifies its components.
    """
    # Create mock S3 environment
    os.environ['FILES_TABLE_NAME'] = 'files-dev'
    os.environ['SHARED_LINKS_TABLE_NAME'] = 'SharedLinksTable-dev'

    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)

    #s3_client = boto3.client('s3', region_name=TEST_REGION)
    #s3_client.create_bucket(
        #Bucket=TEST_BUCKET_NAME,
        #CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    #)

    dynamodb.create_table(
        TableName= FILES_TABLE,
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'}, 
            {'AttributeName': 'fileId', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {'AttributeName': 'fileId', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    dynamodb.create_table(
        TableName=LINKS_TABLE,
        KeySchema=[
            {'AttributeName': 'shareToken', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'shareToken', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    files_table = dynamodb.Table(FILES_TABLE)
    files_table.put_item(Item={'userId': TEST_USER_ID, 'fileId': TEST_FILE_ID, 'filename': TEST_FILENAME})
    
    # Call the handler
    import importlib
    import lambda_functions.share_files.handler as handler_module
    importlib.reload(handler_module)
    response = handler_module.lambda_handler(MOCK_EVENT, None,dynamodb_resource=dynamodb)

    # Check the response structure and URL content
    assert response['statusCode'] == 200
    body_data = json.loads(response['body'])

    # check that a URL was returned
    #assert 'url' in body_data
    #generated_url = body_data['url']

    # Check the URL contains key S3 elements
    #assert TEST_BUCKET_NAME in generated_url
    #assert TEST_FILENAME in generated_url

    # check for expiration query parameter
    #assert 'Expires=' in generated_url

    assert 'shareUrl' in body_data
    assert 'shareToken' in body_data
    assert 'expiresAt' in body_data
    assert body_data['message'] == 'Share link created successfully'

@mock_aws
def test_share_file_missing_filename():
    """
    Tests the handler's response when the filename query parameter is missing.
    """
    os.environ['FILES_TABLE_NAME'] = FILES_TABLE
    os.environ['SHARED_LINKS_TABLE_NAME'] = LINKS_TABLE

    # Create mock tables so DynamoDB calls don’t fail
    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)
    dynamodb.create_table(
        TableName=FILES_TABLE,
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'},
            {'AttributeName': 'fileId', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {'AttributeName': 'fileId', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    dynamodb.create_table(
        TableName=LINKS_TABLE,
        KeySchema=[{'AttributeName': 'shareToken', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'shareToken', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    # Call the handler with an empty event
    missing_event = {}

    import importlib
    import lambda_functions.share_files.handler as handler_module
    importlib.reload(handler_module)
    response = handler_module.lambda_handler(missing_event, None,dynamodb_resource=dynamodb)

    # Check for 400 Bad Request and correct message
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'fileId is required' in body['error']

    # Check for 400 Bad Request
    #assert 'Missing filename query parameter' in json.loads(response['body'])['message']
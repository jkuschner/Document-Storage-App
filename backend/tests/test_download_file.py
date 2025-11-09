# tests/test_download_file.py
import json
import os
import pytest
import boto3
import base64
from moto import mock_aws

from lambda_functions.download_file.handler import lambda_handler

TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_FILENAME = 'test_document.txt'
TEST_CONTENT = b'This is the content of the document.'
TEST_USER_ID = 'test-user'
TEST_TABLE_NAME = 'files-dev'

MOCK_EVENT = {
    "pathParameters": {"fileId": TEST_FILENAME},
    "queryStringParameters": {"userId": TEST_USER_ID},
}

@mock_aws
def test_download_file_success():
    """
    Tests successful file retrieval and verification of the base64-encoded body.
    """
    os.environ["FILE_BUCKET_NAME"] = TEST_BUCKET_NAME
    os.environ["FILES_TABLE_NAME"] = TEST_TABLE_NAME

    # Create bucket and place a file
    s3_client = boto3.client('s3', region_name=TEST_REGION)
    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)

    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )
    s3_client.put_object(
        Bucket=TEST_BUCKET_NAME, 
        Key=TEST_FILENAME, 
        Body=TEST_CONTENT,
        ContentType='text/plain'
    )

    table = dynamodb.create_table(
        TableName=TEST_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "userId", "KeyType": "HASH"},
            {"AttributeName": "fileId", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "fileId", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table.meta.client.get_waiter("table_exists").wait(TableName=TEST_TABLE_NAME)

    # Insert mock record
    table.put_item(
        Item={
            "userId": TEST_USER_ID,
            "fileId": TEST_FILENAME,
            "s3Key": TEST_FILENAME,
            "fileName": TEST_FILENAME
        }
    )

    import importlib
    import lambda_functions.download_file.handler as handler_module
    importlib.reload(handler_module)
    # Call the handler
    response = handler_module.lambda_handler(MOCK_EVENT, None)
    
    # Check the response
    assert response['statusCode'] == 200
    body = json.loads(response["body"])
    assert "downloadUrl" in body
    assert body["fileId"] == TEST_FILENAME
    assert body["fileName"] == TEST_FILENAME
    assert body["downloadUrl"].startswith("https://")

    #assert response['isBase64Encoded'] == True
    #assert response['headers']['Content-Type'] == 'text/plain'

    # Verify the decoded body matches the original content
    #decoded_content = base64.b64decode(response['body']).decode('utf-8')
    #assert decoded_content == TEST_CONTENT.decode('utf-8')

@mock_aws
def test_download_file_not_found():
    """
    Tests that the handler returns a 404 when the file does not exist.
    """
    # Create an empty bucket

    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME
    os.environ['FILES_TABLE_NAME'] = TEST_TABLE_NAME

    s3_client = boto3.client('s3', region_name=TEST_REGION)
    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)

    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )

    table = dynamodb.create_table(
        TableName=TEST_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "userId", "KeyType": "HASH"},
            {"AttributeName": "fileId", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "fileId", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table.meta.client.get_waiter("table_exists").wait(TableName=TEST_TABLE_NAME)

    # Insert mock record
    table.put_item(
        Item={
            "userId": TEST_USER_ID,
            "fileId": TEST_FILENAME,
            "s3Key": TEST_FILENAME,
            "fileName": TEST_FILENAME
        }
    )

    missing_event = {
        'pathParameters': {'fileId': 'nonexistent-file'},
        'queryStringParameters': {'userId': TEST_USER_ID}
    }

    import lambda_functions.download_file.handler as handler_module
    import importlib
    importlib.reload(handler_module)

    # Call the handler
    response = handler_module.lambda_handler(missing_event, None)

    # Check for 404 Not Found
    assert response['statusCode'] == 404
    body_data = json.loads(response['body'])
    assert 'error' in body
    assert 'not found' in body_data['message']
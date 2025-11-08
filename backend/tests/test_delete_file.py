# tests/test_delete_file.py
import json
import os
import pytest
import boto3
import time
from moto import mock_aws

from lambda_functions.delete_file.handler import lambda_handler

TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_FILENAME = 'file_to_delete.txt'
TEST_CONTENT = 'Temporary content'
TEST_USER_ID = 'test-user'
TEST_TABLE_NAME = 'files-dev'

MOCK_EVENT = {
    'queryStringParameters': {'filename': TEST_FILENAME} 
}

@mock_aws
def test_delete_file_success():
    """
    Tests successful deletion by confirming the file is gone from S3.
    """

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
        Body=TEST_CONTENT
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
        }
    )

    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME
    os.environ["FILES_TABLE_NAME"] = TEST_TABLE_NAME

    import importlib
    from lambda_functions.delete_file import handler
    importlib.reload(handler)

    event = {
        "pathParameters": {"fileId": TEST_FILENAME},
        "queryStringParameters": {"userId": TEST_USER_ID},
    }

    # call the handler
    response = lambda_handler(event, None)

    # Check statusCode
    assert response['statusCode'] == 200

    # Check file is gone from S3
    with pytest.raises(s3_client.exceptions.NoSuchKey):
        s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=TEST_FILENAME)

    result = table.get_item(Key={"userId": TEST_USER_ID, "fileId": TEST_FILENAME})
    assert "Item" not in result

@mock_aws
def test_delete_nonexistent_file_success():
    """
    Tests deleting a file that doesnt exist
    """
    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME
    os.environ['FILES_TABLE_NAME'] = TEST_TABLE_NAME
    dynamodb = boto3.client('dynamodb', region_name=TEST_REGION)
    dynamodb.create_table(
        TableName=TEST_TABLE_NAME,
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

    # This fileId doesn't exist in the table
    missing_event = {
        'pathParameters': {'fileId': 'nonexistent-file'},
        'queryStringParameters': {'userId': TEST_USER_ID}
    }
    response = lambda_handler(missing_event, None)

    # Expect 404 (File not found)
    assert response['statusCode'] == 404
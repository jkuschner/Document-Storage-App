# tests/test_delete_file.py
import json
import os
import pytest
import boto3
import time
from moto import mock_aws

TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_FILENAME = 'file_to_delete.txt'
TEST_CONTENT = 'Temporary content'
TEST_USER_ID = 'test-user'
TEST_TABLE_NAME = 'files-dev'

MOCK_EVENT = {
    "pathParameters": {"fileId": TEST_FILENAME},
    "queryStringParameters": {"userId": TEST_USER_ID},
    "requestContext": {
        "authorizer": {
            "claims": {
                "sub": TEST_USER_ID
            }
        }
    }
}

@mock_aws
def test_delete_file_success():
    """
    Tests successful deletion by confirming the file is gone from S3.
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
    time.sleep(0.2)

    # Insert mock record
    table.put_item(
        Item={
            "userId": TEST_USER_ID,
            "fileId": TEST_FILENAME,
            "s3Key": TEST_FILENAME,
        }
    )

    import lambda_functions.delete_file.handler as handler_module
    import importlib
    importlib.reload(handler_module)

    handler_module.boto3 = boto3

    response = handler_module.lambda_handler(MOCK_EVENT, None)

    # Check statusCode
    assert response['statusCode'] == 200

    # Check file is gone from S3
    
    from botocore.exceptions import ClientError

    with pytest.raises(ClientError) as exc:
        s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=TEST_FILENAME)
    assert exc.value.response['Error']['Code'] == 'NoSuchKey'

    result = table.get_item(Key={"userId": TEST_USER_ID, "fileId": TEST_FILENAME})
    assert "Item" not in result

@mock_aws
def test_delete_nonexistent_file_success():
    """
    Tests deleting a file that doesnt exist
    """
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
            {'AttributeName': 'userId', 'KeyType': 'HASH'},
            {'AttributeName': 'fileId', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {'AttributeName': 'fileId', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    table.meta.client.get_waiter("table_exists").wait(TableName=TEST_TABLE_NAME)
    time.sleep(0.3)

    # This fileId doesn't exist in the table
    missing_event = {
    "pathParameters": {"fileId": "nonexistent-file"},
    "queryStringParameters": {"userId": TEST_USER_ID},
    "requestContext": {
        "authorizer": {
            "jwt": {
                "claims": {
                    "sub": TEST_USER_ID
                }
            }
        }
    }
}

    import lambda_functions.delete_file.handler as handler_module
    import importlib
    importlib.reload(handler_module)

    response = handler_module.lambda_handler(missing_event, None)

    # Expect 404 (File not found)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['error'] == 'File not found'
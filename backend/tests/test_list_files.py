# tests/test_list_files.py
import json
import os
import pytest
import boto3
from moto import mock_aws
#import importlib

# Import the handler function
#from lambda_functions.list_files.handler import lambda_handler as handler_module

# name must match handler's default or environment variable
#TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_USER_ID = 'test-user'
TEST_TABLE_NAME = 'files-dev'

@mock_aws
def test_list_files_with_content():
    """
    tests the handler when the S3 bucket contains files
    """
    # Set environment variables
    #os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME
    os.environ['FILES_TABLE_NAME'] = TEST_TABLE_NAME

    # Create the mock bucket
    #s3_client = boto3.client('s3', region_name=TEST_REGION)
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)

    #s3_client.create_bucket(
        #Bucket=TEST_BUCKET_NAME,
        #CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    #)

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

    table.put_item(
        Item={
            "userId": TEST_USER_ID,
            "fileId": 'file_a.txt',
            "fileName": 'file_a.txt'
        }
    )

    table.put_item(
        Item={
            "userId": TEST_USER_ID,
            "fileId": 'file_b.pdf',
            "fileName": 'file_b.pdf'
        }
    )

    # add files to mock bucket
    #s3_client.put_object(Bucket=TEST_BUCKET_NAME, 
                         #Key='user/file_a.txt', 
                         #Body='Hello, I am file a.')
    #s3_client.put_object(Bucket=TEST_BUCKET_NAME,
                         #Key='user/file_b.pdf',
                         #Body='This is file b.')

    import importlib
    import lambda_functions.list_files.handler as handler_module
    importlib.reload(handler_module)

    # Call the handler
    response = handler_module.lambda_handler({"queryStringParameters": {"userId": TEST_USER_ID}}, None)

    # Check statusCode
    assert response['statusCode'] == 200

    body_data = json.loads(response['body'])

    # Check files were retrieved correctly
    #expected_files = ['user/file_a.txt', 'user/file_b.pdf']
    #assert sorted(body_data['files']) == sorted(expected_files)
    #assert 'listed 2 files' in body_data['message']

    assert 'files' in body_data
    assert 'count' in body_data
    assert body_data['count'] == 2
    file_ids = [item['fileId'] for item in body_data['files']]
    assert sorted(file_ids) == ["file_a.txt", "file_b.pdf"]


@mock_aws
def test_list_files_empty_bucket():
    """
    Tests the handler when the S3 bucket is empty.
    """
    #os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME
    os.environ['FILES_TABLE_NAME'] = TEST_TABLE_NAME

    # Create mock bucket, but add no files
    #s3_client = boto3.client('s3', region_name=TEST_REGION)
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)

    #s3_client.create_bucket(
        #Bucket=TEST_BUCKET_NAME,
        #CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    #)

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

    # 2. EXECUTE: Call the handler
    #response = lambda_handler({}, None)
    #import importlib
    #import lambda_functions.list_files.handler as handler_module
    import importlib
    import lambda_functions.list_files.handler as handler_module
    importlib.reload(handler_module)
    
    response = handler_module.lambda_handler({'queryStringParameters': {'userId': TEST_USER_ID}}, None)

    # 3. ASSERT: Check the response
    assert response['statusCode'] == 200

    body_data = json.loads(response['body'])
    assert 'files' in body_data
    assert 'count' in body_data
    # Check that the file list is empty
    assert body_data['files'] == []
    #assert 'listed 0 files' in body_data['message']
    assert body_data['count'] == 0
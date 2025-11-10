import json
import os
import pytest
import boto3
from moto import mock_aws

# Import your Lambda handlers
from lambda_functions.upload_file.handler import lambda_handler as upload_handler
from lambda_functions.list_files.handler import lambda_handler as list_handler
from lambda_functions.delete_file.handler import lambda_handler as delete_handler

# Constants for the test
TEST_BUCKET = "test-dummy-bucket"
TEST_REGION = "us-west-2"
TEST_USER = "test-user"
TEST_FILE = "integration_test_file.txt"
FILES_TABLE = "files-dev"


@mock_aws
def test_file_operations():
    """End-to-end integration test: upload → list → delete → verify deletion."""

    # Set environment variables for Lambda handlers
    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET
    os.environ['FILES_TABLE_NAME'] = FILES_TABLE

    # Create mock S3 bucket
    s3_client = boto3.client('s3', region_name=TEST_REGION)
    s3_client.create_bucket(
        Bucket=TEST_BUCKET,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )

    # Create mock DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)
    dynamodb.create_table(
        TableName=FILES_TABLE,
        KeySchema=[
            {"AttributeName": "userId", "KeyType": "HASH"},
            {"AttributeName": "fileId", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "fileId", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST"
    )
  
    # Upload file
  
    upload_event = {
        "body": json.dumps({
            "fileName": TEST_FILE,
            "userId": TEST_USER,
            "contentType": "text/plain"
        })
    }
    upload_response = upload_handler(upload_event, None, dynamodb_resource=dynamodb)
    assert upload_response['statusCode'] == 200
    upload_body = json.loads(upload_response['body'])
    file_id = upload_body['fileId']
    assert "uploadUrl" in upload_body
    assert upload_body["message"] == "Upload URL generated successfully"

    # List files
    
    list_event = {"queryStringParameters": {"userId": TEST_USER}}
    list_response = list_handler(list_event, None, dynamodb_resource=dynamodb)
    assert list_response['statusCode'] == 200
    files_list = json.loads(list_response['body'])["files"]
    assert any(f["fileId"] == file_id for f in files_list)

    
    # Delete file
   
    delete_event = {
        "pathParameters": {"fileId": file_id},
        "queryStringParameters": {"userId": TEST_USER}
    }
    delete_response = delete_handler(delete_event, None, dynamodb_resource=dynamodb)
    assert delete_response['statusCode'] == 200
    delete_body = json.loads(delete_response['body'])
    assert delete_body["message"] == "File deleted successfully"

    # Verify deletion
   
    list_response_after_delete = list_handler(list_event, None, dynamodb_resource=dynamodb)
    files_after_delete = json.loads(list_response_after_delete['body'])["files"]
    assert not any(f["fileId"] == file_id for f in files_after_delete)

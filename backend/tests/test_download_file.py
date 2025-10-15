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

MOCK_EVENT = {
    'queryStringParameters': {'filename': TEST_FILENAME},
}

@mock_aws
def test_download_file_success():
    """
    Tests successful file retrieval and verification of the base64-encoded body.
    """
    # Create bucket and place a file
    s3_client = boto3.client('s3', region_name=TEST_REGION)
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
    
    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME

    # Call the handler
    response = lambda_handler(MOCK_EVENT, None)
    
    # Check the response
    assert response['statusCode'] == 200
    assert response['isBase64Encoded'] == True
    assert response['headers']['Content-Type'] == 'text/plain'

    # Verify the decoded body matches the original content
    decoded_content = base64.b64decode(response['body']).decode('utf-8')
    assert decoded_content == TEST_CONTENT.decode('utf-8')
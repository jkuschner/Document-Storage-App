# tests/test_share_file.py
import json
import os
import pytest
import boto3
from moto import mock_aws

from lambda_functions.share_file.index import lambda_handler

TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_FILENAME = 'document_to_share.txt'

MOCK_EVENT = {
    'queryStringParameters': {'filename': TEST_FILENAME},
}

@mock_aws
def test_share_file_url_is_generated():
    """
    Tests that the handler successfully generates a presigned URL and verifies its components.
    """
    # Create mock S3 environment
    s3_client = boto3.client('s3', region_name=TEST_REGION)
    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )
    
    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME 
    
    # Call the handler
    response = lambda_handler(MOCK_EVENT, None)

    # Check the response structure and URL content
    assert response['statusCode'] == 200
    body_data = json.loads(response['body'])

    # check that a URL was returned
    assert 'url' in body_data
    generated_url = body_data['url']

    # Check the URL contains key S3 elements
    assert TEST_BUCKET_NAME in generated_url
    assert TEST_FILENAME in generated_url

    # check for expiration query parameter
    assert 'Expires=' in generated_url

@mock_aws
def test_share_file_missing_filename():
    """
    Tests the handler's response when the filename query parameter is missing.
    """
    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME
    
    # Call the handler with an empty event
    missing_event = {}
    response = lambda_handler(missing_event, None)

    # Check for 400 Bad Request
    assert response['statusCode'] == 400
    assert 'Missing filename query parameter' in json.loads(response['body'])['message']
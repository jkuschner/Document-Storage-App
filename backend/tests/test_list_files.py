# tests/test_list_files.py
import json
import os
import pytest
import boto3
from moto import mock_aws

# Import the handler function
from lambda_functions.list_files.handler import lambda_handler

# name must match handler's default or environment variable
TEST_BUCKET_NAME = 'test-dummy-bucket'

@mock_aws
def test_list_files_with_content():
    """
    tests the handler when the S3 bucket contains files
    """
    # Create the mock bucket and add files
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, 
                         Key='user/file_a.txt', 
                         Body='Hello, I am file a.')
    s3_client.put_object(Bucket=TEST_BUCKET_NAME,
                         Key='user/file_b.pdf',
                         Body='This is file b.')
    
    # set environment variable
    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME

    # Call the handler
    response = lambda_handler({}, None)

    # Check statusCode
    assert response['statusCode'] == 200

    body_data = json.loads(response['body'])

    # Check files were retrieved correctly
    expected_files = ['user/file_a.txt', 'user/file_b.pdf']
    assert sorted(body_data['files']) == sorted(expected_files)
    assert 'listed 2 files' in body_data['message']
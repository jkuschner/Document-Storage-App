# tests/test_delete_file.py
import json
import os
import pytest
import boto3
from moto import mock_aws

from lambda_functions.delete_file.handler import lambda_handler

TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_FILENAME = 'file_to_delete.txt'
TEST_CONTENT = 'Temporary content'

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
    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )
    s3_client.put_object(
        Bucket=TEST_BUCKET_NAME,
        Key=TEST_FILENAME,
        Body=TEST_CONTENT
    )

    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME

    # call the handler
    response = lambda_handler(MOCK_EVENT, None)

    # Check statusCode
    assert response['statusCode'] == 204

    # Check file is gone from S3
    with pytest.raises(s3_client.exceptions.NoSuchKey):
        s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=TEST_FILENAME)

@mock_aws
def test_delete_nonexistent_file_success():
    """
    Tests deleting a file that doesnt exist
    """
    s3_client = boto3.client('s3', region_name=TEST_REGION)
    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )

    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME

    missing_event = {'queryStringParameters': {'filename': 'nonexistent.txt'}}
    response = lambda_handler(missing_event, None)

    # Check statusCode
    assert response['statusCode'] == 204
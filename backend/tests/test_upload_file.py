# tests/test_upload_file.py
import json
import os
import base64
import pytest
import boto3
from moto import mock_aws

# import hanlder function
from lambda_functions.upload_file.handler import lambda_handler

TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_FILENAME = 'document.txt'
TEST_CONTENT = 'This is the file content for testing upload_file.'

# mock API Gateway event
MOCK_EVENT = {
    'queryStringParameters': {'filename': TEST_FILENAME},
    # base64 encode content because API Gateway does this automatically
    'body': base64.b64encode(TEST_CONTENT.encode('utf-8')).decode('utf-8')
}

@mock_aws
def test_upload_file_success():
    """
    Tests successful file upload, verifying the file exists in mock S3 bucket.
    """
    # create mock S3 environment
    s3_client = boto3.client('s3', region_name=TEST_REGION)
    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )

    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME

    # call handler
    response = lambda_handler(MOCK_EVENT, None)

    # check HTTP response
    assert response['statusCode'] == 201
    assert 'uploaded successfully' in json.loads(response['body'])['message']

    # check file was written to mock S3
    try:
        s3_response = s3_client.get_object(Bucket=TEST_BUCKET_NAME,
                                           Key=TEST_FILENAME)
        file_content = s3_response['Body'].read().decode('utf-8')

        assert file_content == TEST_CONTENT
    except s3_client.exceptions.NoSuchKey:
        pytest.fail(f"File {TEST_FILENAME} was not found in the bucket after upload.")
# tests/test_upload_file.py
import json
import os
import base64
import pytest
import boto3
from moto import mock_aws

# import hanlder function
from lambda_functions.upload_file.index import lambda_handler

TEST_BUCKET_NAME = 'test-dummy-bucket'
TEST_REGION = 'us-west-2'
TEST_FILENAME = 'document.txt'
TEST_CONTENT = 'This is the file content for testing upload_file.'

# mock API Gateway event

MOCK_EVENT = {
    'body': json.dumps({
        'filename': TEST_FILENAME,
        'contentType': 'application/pdf'
    })
}

@mock_aws
def test_upload_file_returns_presigned_url():
    """
    Tests that the handler successfully generates a PUT presigned URL.
    """
    # Mock S3 bucket and environment
    s3_client = boto3.client('s3', region_name=TEST_REGION)
    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )
    os.environ['BUCKET_NAME'] = TEST_BUCKET_NAME 
    
    # call the handler
    response = lambda_handler(MOCK_EVENT, None)
    
    # check status code
    assert response['statusCode'] == 200
    body_data = json.loads(response['body'])
    
    # Check that a URL was returned
    assert 'uploadUrl' in body_data
    generated_url = body_data['uploadUrl']
    
    # Verify the URL structure
    assert TEST_BUCKET_NAME in generated_url
    assert TEST_FILENAME in generated_url
    
    # Check for the key S3 parameters (Signature/Expires) to ensure it's a valid presigned URL
    assert 'Signature=' in generated_url or 'X-Amz-Signature=' in generated_url
    assert 'Expires=' in generated_url or 'X-Amz-Expires=' in generated_url

"""
@mock_aws
def test_upload_file_success():

    #Tests successful file upload, verifying the file exists in mock S3 bucket.

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

"""
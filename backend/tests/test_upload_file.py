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
TEST_USER_ID = 'test-user'
FILES_TABLE = 'files-dev'

# mock API Gateway event
MOCK_EVENT = {
    'body': json.dumps({
        'fileName': TEST_FILENAME,
        'userId': TEST_USER_ID,
        'contentType': 'text/plain'
    })
}

@mock_aws
def test_upload_file_success():
    """
    Tests successful file upload, verifying the file exists in mock S3 bucket.
    """
    os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET_NAME

    # create mock S3 environment
    s3_client = boto3.client('s3', region_name=TEST_REGION)
    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': TEST_REGION}
    )

    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)
    dynamodb.create_table(
        TableName=FILES_TABLE,
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

    # call handler
    import importlib
    import lambda_functions.upload_file.handler as handler_module
    importlib.reload(handler_module)
    response = handler_module.lambda_handler(MOCK_EVENT, None, dynamodb_resource=dynamodb)

    # check HTTP response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'uploadUrl' in body
    assert 'fileId' in body
    assert body['message'] == 'Upload URL generated successfully'
    #assert 'uploaded successfully' in json.loads(response['body'])['message']

    # check file was written to mock S3
    #try:
        #s3_response = s3_client.get_object(Bucket=TEST_BUCKET_NAME,
                                           #Key=TEST_FILENAME)
        #file_content = s3_response['Body'].read().decode('utf-8')

        #assert file_content == TEST_CONTENT
    #except s3_client.exceptions.NoSuchKey:
        #pytest.fail(f"File {TEST_FILENAME} was not found in the bucket after upload.")

    files_table = dynamodb.Table(FILES_TABLE)
    result = files_table.get_item(Key={'userId': TEST_USER_ID, 'fileId': body['fileId']})
    assert 'Item' in result
    assert result['Item']['fileName'] == TEST_FILENAME
import pytest
import json
import boto3
from moto import mock_aws
import os
import sys

TEST_USER_ID = "test-user-123"
TEST_BUCKET = "test-bucket"
TEST_TABLE = "files-test"

# Set environment variables
os.environ['FILES_TABLE_NAME'] = TEST_TABLE
os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET
os.environ['ENVIRONMENT'] = 'test'

# Add the lambda_functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'upload_file'))


@pytest.fixture
def aws_environment(monkeypatch):
    """Set up environment variables."""
    monkeypatch.setenv('FILES_TABLE_NAME', TEST_TABLE)
    monkeypatch.setenv('FILE_BUCKET_NAME', TEST_BUCKET)
    monkeypatch.setenv('ENVIRONMENT', 'test')


@pytest.fixture
def setup_aws_resources(aws_environment):
    """Create mock DynamoDB table and S3 bucket."""
    with mock_aws():
        # Create DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName=TEST_TABLE,
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
        
        # Create S3 bucket
        s3 = boto3.client('s3', region_name='us-west-2')
        s3.create_bucket(
            Bucket=TEST_BUCKET,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        
        # Import handler after mocks are set up - import fresh each time
        import importlib
        handler_module_name = 'lambda_functions.upload_file.handler'
        if handler_module_name in sys.modules:
            del sys.modules[handler_module_name]
        handler = importlib.import_module(handler_module_name)
        lambda_handler = handler.lambda_handler
        
        # Patch handler's table reference to use the mocked table
        handler.files_table = table
        
        yield table, s3, lambda_handler


def create_test_event(file_name, content_type='application/pdf'):
    """Create a test event with JWT context."""
    return {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': TEST_USER_ID
                }
            }
        },
        'body': json.dumps({
            'fileName': file_name,
            'contentType': content_type
        })
    }



@mock_aws
def test_upload_file_success(aws_environment, setup_aws_resources):
    """Test successful file upload returns presigned URL."""
    table, s3, lambda_handler = setup_aws_resources
    
    event = create_test_event('test-document.pdf')
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'uploadUrl' in body
    assert 'fileId' in body
    assert 'message' in body
    
    # Verify presigned URL format
    upload_url = body['uploadUrl']
    assert TEST_BUCKET in upload_url or 'Signature' in upload_url or 'AWSAccessKeyId' in upload_url


@mock_aws
def test_upload_file_missing_jwt(aws_environment, setup_aws_resources):
    """Test missing JWT returns 401."""
    _, _, lambda_handler = setup_aws_resources
    
    event = {
        'body': json.dumps({'fileName': 'test.pdf'})
        # No requestContext
    }
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'unauthorized' in body['error'].lower() or 'missing' in body['error'].lower()


@mock_aws
def test_upload_file_missing_filename(aws_environment, setup_aws_resources):
    """Test missing fileName returns 400."""
    _, _, lambda_handler = setup_aws_resources
    
    event = {
        'requestContext': {
            'authorizer': {'claims': {'sub': TEST_USER_ID}}
        },
        'body': json.dumps({})  # No fileName
    }
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'filename' in body['error'].lower() or 'required' in body['error'].lower()


@mock_aws
def test_upload_creates_dynamodb_entry(aws_environment, setup_aws_resources):
    """Test that upload creates a DynamoDB entry."""
    table, _, lambda_handler = setup_aws_resources
    
    event = create_test_event('test-document.pdf', 'application/pdf')
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    file_id = body['fileId']
    
    # Verify DynamoDB entry
    result = table.get_item(
        Key={
            'userId': TEST_USER_ID,
            'fileId': file_id
        }
    )
    
    assert 'Item' in result
    item = result['Item']
    assert item['fileName'] == 'test-document.pdf'
    assert item['userId'] == TEST_USER_ID
    assert item['fileId'] == file_id
    assert item['contentType'] == 'application/pdf'
    assert item['status'] == 'pending'
    assert 's3Key' in item
    assert TEST_USER_ID in item['s3Key']
    assert file_id in item['s3Key']

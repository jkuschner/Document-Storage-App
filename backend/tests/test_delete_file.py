import pytest
import json
import boto3
from moto import mock_aws
import os
import sys

TEST_USER_ID = "test-user-123"
TEST_FILE_ID = "file-456"
TEST_BUCKET = "test-bucket"
TEST_TABLE = "files-test"

# Set environment variables
os.environ['FILES_TABLE_NAME'] = TEST_TABLE
os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET
os.environ['ENVIRONMENT'] = 'test'

# Add the lambda_functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'delete_file'))


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
        handler_module_name = 'lambda_functions.delete_file.handler'
        if handler_module_name in sys.modules:
            del sys.modules[handler_module_name]
        handler = importlib.import_module(handler_module_name)
        lambda_handler = handler.lambda_handler
        
        # Patch handler's table reference to use the mocked table
        handler.files_table = table
        
        yield table, s3, lambda_handler


def create_test_event(file_id):
    """Create a test event with JWT context."""
    return {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': TEST_USER_ID
                }
            }
        },
        'pathParameters': {
            'fileId': file_id
        }
    }


@mock_aws
def test_delete_file_success(aws_environment, setup_aws_resources):
    """Test successful file deletion removes from S3 and DynamoDB."""
    table, s3, lambda_handler = setup_aws_resources
    
    # Setup DynamoDB entry
    s3_key = f'{TEST_USER_ID}/{TEST_FILE_ID}/test-document.pdf'
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': TEST_FILE_ID,
        'fileName': 'test-document.pdf',
        's3Key': s3_key
    })
    
    # Setup S3 file
    s3.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=b'Test file content'
    )
    
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'message' in body
    assert 'deleted' in body['message'].lower()
    assert body['fileId'] == TEST_FILE_ID
    
    # Verify file is deleted from S3
    with pytest.raises(s3.exceptions.NoSuchKey):
        s3.get_object(Bucket=TEST_BUCKET, Key=s3_key)
    
    # Verify file is deleted from DynamoDB
    result = table.get_item(
        Key={
            'userId': TEST_USER_ID,
            'fileId': TEST_FILE_ID
        }
    )
    assert 'Item' not in result


@mock_aws
def test_delete_file_missing_jwt(aws_environment, setup_aws_resources):
    """Test missing JWT returns 401."""
    _, _, lambda_handler = setup_aws_resources
    
    event = {
        'pathParameters': {'fileId': TEST_FILE_ID}
        # No requestContext
    }
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'unauthorized' in body['error'].lower() or 'missing' in body['error'].lower()


@mock_aws
def test_delete_file_not_found(aws_environment, setup_aws_resources):
    """Test deleting non-existent file returns 404."""
    _, _, lambda_handler = setup_aws_resources
    
    event = create_test_event('nonexistent-file-id')
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'not found' in body['error'].lower()


@mock_aws
def test_delete_file_wrong_owner(aws_environment, setup_aws_resources):
    """Test deleting another user's file returns 404 (not found for this user)."""
    table, s3, lambda_handler = setup_aws_resources
    
    # Create file belonging to another user
    other_user_id = 'other-user-789'
    s3_key = f'{other_user_id}/{TEST_FILE_ID}/other-file.pdf'
    table.put_item(Item={
        'userId': other_user_id,
        'fileId': TEST_FILE_ID,
        'fileName': 'other-file.pdf',
        's3Key': s3_key
    })
    
    s3.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=b'Other user content'
    )
    
    # Try to delete with TEST_USER_ID
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    # Should return 404 (not found for this user) since composite key doesn't match
    assert response['statusCode'] == 404


@mock_aws
def test_delete_file_removes_from_dynamodb(aws_environment, setup_aws_resources):
    """Test that deletion removes the DynamoDB entry."""
    table, s3, lambda_handler = setup_aws_resources
    
    # Setup file
    s3_key = f'{TEST_USER_ID}/{TEST_FILE_ID}/test.pdf'
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': TEST_FILE_ID,
        'fileName': 'test.pdf',
        's3Key': s3_key
    })
    
    s3.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=b'Content'
    )
    
    # Verify file exists in DynamoDB before deletion
    result = table.get_item(
        Key={
            'userId': TEST_USER_ID,
            'fileId': TEST_FILE_ID
        }
    )
    assert 'Item' in result
    
    # Delete file
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    
    # Verify file is removed from DynamoDB
    result = table.get_item(
        Key={
            'userId': TEST_USER_ID,
            'fileId': TEST_FILE_ID
        }
    )
    assert 'Item' not in result

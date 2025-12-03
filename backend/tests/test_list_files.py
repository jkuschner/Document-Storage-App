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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'list_files'))


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
        handler_module_name = 'lambda_functions.list_files.handler'
        if handler_module_name in sys.modules:
            del sys.modules[handler_module_name]
        handler = importlib.import_module(handler_module_name)
        lambda_handler = handler.lambda_handler
        
        # Patch handler's table reference to use the mocked table
        handler.files_table = table
        
        yield table, s3, lambda_handler


def create_test_event():
    """Create a test event with JWT context."""
    return {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': TEST_USER_ID
                }
            }
        }
    }


@mock_aws
def test_list_files_success(aws_environment, setup_aws_resources):
    """Test listing user's files returns files from DynamoDB."""
    table, _, lambda_handler = setup_aws_resources
    
    # Add test files to DynamoDB
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': 'file-1',
        'fileName': 'document1.pdf',
        's3Key': f'{TEST_USER_ID}/file-1/document1.pdf',
        'contentType': 'application/pdf',
        'uploadDate': '2024-01-01T00:00:00'
    })
    
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': 'file-2',
        'fileName': 'document2.txt',
        's3Key': f'{TEST_USER_ID}/file-2/document2.txt',
        'contentType': 'text/plain',
        'uploadDate': '2024-01-02T00:00:00'
    })
    
    event = create_test_event()
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'files' in body
    assert 'count' in body
    assert body['count'] == 2
    assert len(body['files']) == 2
    
    # Verify file IDs are present
    file_ids = [f['fileId'] for f in body['files']]
    assert 'file-1' in file_ids
    assert 'file-2' in file_ids


@mock_aws
def test_list_files_empty(aws_environment, setup_aws_resources):
    """Test listing files when user has none returns empty array."""
    _, _, lambda_handler = setup_aws_resources
    
    event = create_test_event()
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'files' in body
    assert 'count' in body
    assert body['count'] == 0
    assert body['files'] == []


@mock_aws
def test_list_files_missing_jwt(aws_environment, setup_aws_resources):
    """Test missing JWT returns 401."""
    _, _, lambda_handler = setup_aws_resources
    
    event = {}  # No requestContext
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'unauthorized' in body['error'].lower() or 'missing' in body['error'].lower()


@mock_aws
def test_list_files_only_own_files(aws_environment, setup_aws_resources):
    """Test that only files for the authenticated user are returned."""
    table, _, lambda_handler = setup_aws_resources
    
    # Add file for TEST_USER_ID
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': 'file-own',
        'fileName': 'my-file.pdf',
        's3Key': f'{TEST_USER_ID}/file-own/my-file.pdf'
    })
    
    # Add file for another user
    other_user_id = 'other-user-456'
    table.put_item(Item={
        'userId': other_user_id,
        'fileId': 'file-other',
        'fileName': 'other-file.pdf',
        's3Key': f'{other_user_id}/file-other/other-file.pdf'
    })
    
    event = create_test_event()
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['count'] == 1
    assert len(body['files']) == 1
    assert body['files'][0]['fileId'] == 'file-own'
    assert body['files'][0]['userId'] == TEST_USER_ID

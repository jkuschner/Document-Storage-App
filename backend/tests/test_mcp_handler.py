import pytest
import json
import boto3
from moto import mock_aws
import os
import sys
from io import BytesIO
from PyPDF2 import PdfWriter

TEST_USER_ID = "test-user-123"
TEST_FILE_ID = "file-456"
TEST_BUCKET = "test-bucket"
TEST_TABLE = "files-test"

# Set environment variables before importing handler
os.environ['FILES_TABLE_NAME'] = TEST_TABLE
os.environ['FILE_BUCKET_NAME'] = TEST_BUCKET
os.environ['ENVIRONMENT'] = 'test'

# Add the lambda_functions directory to the path
handler_path = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'mcp_handler')
sys.path.insert(0, handler_path)

# Import handler - will be reloaded in fixtures to use mocked resources
import importlib
import handler
from handler import lambda_handler


@pytest.fixture
def aws_environment(monkeypatch):
    """Set up environment variables."""
    monkeypatch.setenv('FILES_TABLE_NAME', TEST_TABLE)
    monkeypatch.setenv('FILE_BUCKET_NAME', TEST_BUCKET)
    monkeypatch.setenv('ENVIRONMENT', 'test')


@pytest.fixture
def setup_aws_resources(aws_environment):
    """Create mock DynamoDB table and S3 bucket."""
    # Use mock_aws context manager to ensure mocking is active
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
        
        # Create S3 bucket (use a unique name to avoid conflicts)
        s3 = boto3.client('s3', region_name='us-west-2')
        try:
            s3.create_bucket(
                Bucket=TEST_BUCKET,
                CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
            )
        except Exception:
            # Bucket might already exist from previous test run, that's ok
            pass
        
        # Patch handler's table reference to use the mocked table
        handler.table = table
        
        yield table, s3


def create_test_event(action, resource_id=None, use_body_auth=False):
    """Create a test event with proper JWT context."""
    event = {
        'body': json.dumps({
            'action': action,
            'resource_id': resource_id,
            'userId': TEST_USER_ID if use_body_auth else None
        })
    }
    
    if not use_body_auth:
        event['requestContext'] = {
            'authorizer': {
                'claims': {
                    'sub': TEST_USER_ID
                }
            }
        }
    
    return event


# Test 1: resources/list - success
def test_resources_list_success(aws_environment, setup_aws_resources):
    """Test listing user's files."""
    # Setup DynamoDB
    table, _ = setup_aws_resources
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': TEST_FILE_ID,
        'fileName': 'test.pdf',
        's3Key': f'{TEST_USER_ID}/{TEST_FILE_ID}/test.pdf',
        'contentType': 'application/pdf',
        'fileSize': int(1024)  # Use int instead of letting DynamoDB convert to Decimal
    })
    
    # Add another file
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': 'file-789',
        'fileName': 'document.txt',
        's3Key': f'{TEST_USER_ID}/file-789/document.txt',
        'contentType': 'text/plain',
        'fileSize': int(512)  # Use int instead of letting DynamoDB convert to Decimal
    })
    
    # Call handler with action='resources/list'
    event = create_test_event('resources/list')
    response = lambda_handler(event, None)
    
    # Assert 200 and files returned
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'resources' in body
    assert len(body['resources']) == 2
    
    # Check resource structure
    resource_ids = [r['id'] for r in body['resources']]
    assert TEST_FILE_ID in resource_ids
    assert 'file-789' in resource_ids
    
    # Check one resource in detail
    test_resource = next(r for r in body['resources'] if r['id'] == TEST_FILE_ID)
    assert test_resource['name'] == 'test.pdf'
    assert test_resource['mimeType'] == 'application/pdf'
    assert test_resource['size'] == 1024


# Test 2: resources/list - empty
def test_resources_list_empty(aws_environment, setup_aws_resources):
    """Test listing files when user has none."""
    event = create_test_event('resources/list')
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'resources' in body
    assert len(body['resources']) == 0


# Test 3: resources/read - success
def test_resources_read_success(aws_environment, setup_aws_resources):
    """Test reading file content."""
    # Setup DynamoDB and S3
    table, s3 = setup_aws_resources
    s3_key = f'{TEST_USER_ID}/{TEST_FILE_ID}/test.txt'
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': TEST_FILE_ID,
        'fileName': 'test.txt',
        's3Key': s3_key,
        'contentType': 'text/plain'
    })
    
    # Setup S3
    s3.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=b'This is the file content to read.'
    )
    
    event = create_test_event('resources/read', resource_id=TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'content' in body
    assert body['content'] == 'This is the file content to read.'
    assert body['fileName'] == 'test.txt'


# Test 4: resources/read - PDF text extraction
def test_resources_read_pdf_extraction(aws_environment, setup_aws_resources):
    """Test reading PDF file with text extraction."""
    # Create a simple PDF
    from PyPDF2 import PdfWriter
    pdf_writer = PdfWriter()
    # Create a blank page
    pdf_writer.add_blank_page(width=612, height=792)
    pdf_buffer = BytesIO()
    pdf_writer.write(pdf_buffer)
    pdf_content = pdf_buffer.getvalue()
    
    table, s3 = setup_aws_resources
    s3_key = f'{TEST_USER_ID}/{TEST_FILE_ID}/test.pdf'
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': TEST_FILE_ID,
        'fileName': 'test.pdf',
        's3Key': s3_key,
        'contentType': 'application/pdf'
    })
    
    s3.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=pdf_content
    )
    
    event = create_test_event('resources/read', resource_id=TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'content' in body
    assert body['fileName'] == 'test.pdf'


# Test 5: resources/read - file not found
def test_resources_read_not_found(aws_environment, setup_aws_resources):
    """Test reading non-existent file returns 404."""
    event = create_test_event('resources/read', resource_id='nonexistent-file')
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'not found' in body['error'].lower()


# Test 6: resources/read - wrong owner (404)
def test_resources_read_wrong_owner(aws_environment, setup_aws_resources):
    """Test reading another user's file returns 404 (not found for this user)."""
    table, s3 = setup_aws_resources
    other_user_id = 'other-user-456'
    s3_key = f'{other_user_id}/{TEST_FILE_ID}/test.txt'
    
    table.put_item(Item={
        'userId': other_user_id,
        'fileId': TEST_FILE_ID,
        'fileName': 'test.txt',
        's3Key': s3_key
    })
    
    s3.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=b'Other user content'
    )
    
    # Query with TEST_USER_ID but file belongs to other_user_id
    # Since composite key is (userId, fileId), this will return 404
    event = create_test_event('resources/read', resource_id=TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'not found' in body['error'].lower()


# Test 7: Missing JWT - returns 401
def test_missing_jwt_returns_401(aws_environment):
    """Test that missing JWT returns 401."""
    event = {
        'body': json.dumps({'action': 'resources/list'})
        # No requestContext, no Authorization header, no userId in body
    }
    response = lambda_handler(event, None)
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'unauthorized' in body['error'].lower() or 'missing' in body['error'].lower()


# Test 8: Internal Lambda call with userId in body
def test_internal_call_with_body_userid(aws_environment, setup_aws_resources):
    """Test that userId in body works for internal Lambda-to-Lambda calls."""
    table, _ = setup_aws_resources
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': TEST_FILE_ID,
        'fileName': 'test.txt',
        's3Key': f'{TEST_USER_ID}/{TEST_FILE_ID}/test.txt'
    })
    
    event = {
        'body': json.dumps({
            'action': 'resources/list',
            'userId': TEST_USER_ID  # Internal call passes userId in body
        })
    }
    
    response = lambda_handler(event, None)
    # Should work - not return 401
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'resources' in body


# Test 9: Invalid action - returns 400
def test_invalid_action_returns_400(aws_environment):
    """Test that invalid action returns 400."""
    event = create_test_event('invalid-action')
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'invalid action' in body['error'].lower()


# Test 10: Missing resource_id for resources/read
def test_resources_read_missing_resource_id(aws_environment):
    """Test that missing resource_id returns 400."""
    event = create_test_event('resources/read', resource_id=None)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'resource_id' in body['error'].lower() or 'missing' in body['error'].lower()


# Test 11: S3 file not found
def test_resources_read_s3_not_found(aws_environment, setup_aws_resources):
    """Test reading file when S3 object doesn't exist."""
    table, _ = setup_aws_resources
    table.put_item(Item={
        'userId': TEST_USER_ID,
        'fileId': TEST_FILE_ID,
        'fileName': 'test.txt',
        's3Key': f'{TEST_USER_ID}/{TEST_FILE_ID}/test.txt'
    })
    
    # Don't create S3 object
    event = create_test_event('resources/read', resource_id=TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body


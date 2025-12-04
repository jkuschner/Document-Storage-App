import pytest
import json
import boto3
from moto import mock_aws
from unittest.mock import patch, MagicMock
import os
import sys

TEST_USER_ID = "test-user-123"
TEST_FILE_ID = "file-456"

# Set environment variables before importing handler
os.environ['MCP_HANDLER_ARN'] = 'arn:aws:lambda:us-west-2:123456789:function:mcp-handler'
os.environ['FILES_TABLE_NAME'] = 'files-test'
os.environ['FILE_BUCKET_NAME'] = 'test-bucket'
os.environ['ENVIRONMENT'] = 'test'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'chat_handler'))

from handler import lambda_handler


@pytest.fixture
def aws_environment(monkeypatch):
    """Set up environment variables."""
    monkeypatch.setenv('MCP_HANDLER_ARN', 'arn:aws:lambda:us-west-2:123456789:function:mcp-handler')
    monkeypatch.setenv('FILES_TABLE_NAME', 'files-test')
    monkeypatch.setenv('FILE_BUCKET_NAME', 'test-bucket')
    monkeypatch.setenv('ENVIRONMENT', 'test')


def create_test_event(file_id, file_name=None):
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
            'fileId': file_id,
            'file_name': file_name or 'test.pdf'  # Handler uses file_name, not fileName
        })
    }


# Test 1: Successful summarization
@mock_aws
@patch('handler.bedrock_runtime')
@patch('handler.lambda_client')
def test_chat_success(mock_lambda, mock_bedrock, aws_environment):
    """Test successful file summarization."""
    # Mock mcp_handler response
    mock_lambda.invoke.return_value = {
        'Payload': MagicMock(read=lambda: json.dumps({
            'statusCode': 200,
            'body': json.dumps({'content': 'This is the file content to summarize.'})
        }).encode())
    }
    
    # Mock Bedrock response
    mock_bedrock.invoke_model.return_value = {
        'body': MagicMock(read=lambda: json.dumps({
            'content': [{'text': 'This is a summary of the document.'}]
        }).encode())
    }
    
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'summary' in body
    assert body['summary'] == 'This is a summary of the document.'
    assert body['fileName'] == 'test.pdf'
    assert 'model' in body
    
    # Verify mcp_handler was called correctly
    mock_lambda.invoke.assert_called_once()
    invoke_args = mock_lambda.invoke.call_args
    assert invoke_args[1]['FunctionName'] == 'arn:aws:lambda:us-west-2:123456789:function:mcp-handler'
    
    # Verify Bedrock was called
    mock_bedrock.invoke_model.assert_called_once()


# Test 2: Missing JWT - returns 401
@mock_aws
def test_missing_jwt_returns_401(aws_environment):
    """Test that missing JWT returns 401."""
    event = {
        'body': json.dumps({'fileId': TEST_FILE_ID})
        # No requestContext
    }
    response = lambda_handler(event, None)
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'unauthorized' in body['error'].lower() or 'missing' in body['error'].lower()


# Test 3: Missing fileId - returns 400
@mock_aws
def test_missing_file_id_returns_400(aws_environment):
    """Test that missing fileId returns 400."""
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {'sub': TEST_USER_ID}
            }
        },
        'body': json.dumps({})  # No fileId
    }
    response = lambda_handler(event, None)
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'fileid' in body['error'].lower() or 'missing' in body['error'].lower()


# Test 4: MCP handler returns error
@mock_aws
@patch('handler.lambda_client')
def test_mcp_handler_error(mock_lambda, aws_environment):
    """Test handling of mcp_handler errors."""
    mock_lambda.invoke.return_value = {
        'Payload': MagicMock(read=lambda: json.dumps({
            'statusCode': 404,
            'body': json.dumps({'error': 'File not found'})
        }).encode())
    }
    
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    # Should propagate the error
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body or 'File not found' in body.get('error', '')


# Test 5: MCP handler returns 403 (access denied)
@mock_aws
@patch('handler.lambda_client')
def test_mcp_handler_access_denied(mock_lambda, aws_environment):
    """Test handling of mcp_handler 403 errors."""
    mock_lambda.invoke.return_value = {
        'Payload': MagicMock(read=lambda: json.dumps({
            'statusCode': 403,
            'body': json.dumps({'error': 'Access denied'})
        }).encode())
    }
    
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 403


# Test 6: Bedrock error
@mock_aws
@patch('handler.bedrock_runtime')
@patch('handler.lambda_client')
def test_bedrock_error(mock_lambda, mock_bedrock, aws_environment):
    """Test handling of Bedrock API errors."""
    # Mock successful mcp_handler
    mock_lambda.invoke.return_value = {
        'Payload': MagicMock(read=lambda: json.dumps({
            'statusCode': 200,
            'body': json.dumps({'content': 'File content'})
        }).encode())
    }
    
    # Mock Bedrock error
    mock_bedrock.invoke_model.side_effect = Exception('Bedrock API error')
    
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'bedrock' in body['error'].lower() or 'summarization' in body['error'].lower()


# Test 7: Content truncation for large files
@mock_aws
@patch('handler.bedrock_runtime')
@patch('handler.lambda_client')
def test_content_truncation(mock_lambda, mock_bedrock, aws_environment):
    """Test that large content is truncated before sending to Bedrock."""
    # Create large content (> 100KB)
    large_content = 'A' * 150000
    
    mock_lambda.invoke.return_value = {
        'Payload': MagicMock(read=lambda: json.dumps({
            'statusCode': 200,
            'body': json.dumps({'content': large_content})
        }).encode())
    }
    
    mock_bedrock.invoke_model.return_value = {
        'body': MagicMock(read=lambda: json.dumps({
            'content': [{'text': 'Summary'}]
        }).encode())
    }
    
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    
    # Verify Bedrock was called with truncated content
    call_args = mock_bedrock.invoke_model.call_args
    body_str = call_args[1]['body']
    body_dict = json.loads(body_str)
    prompt = body_dict['messages'][0]['content']
    
    # Content should be truncated to ~100KB
    assert len(prompt) < len(large_content)
    assert 'truncated' in prompt.lower()


# Test 8: Invalid JSON in event body
@mock_aws
def test_invalid_json_body(aws_environment):
    """Test handling of invalid JSON in event body."""
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {'sub': TEST_USER_ID}
            }
        },
        'body': 'invalid json{'
    }
    response = lambda_handler(event, None)
    
    # Should handle gracefully (either 400 or 500)
    assert response['statusCode'] in [400, 500]


# Test 9: Empty file content
@mock_aws
@patch('handler.bedrock_runtime')
@patch('handler.lambda_client')
def test_empty_file_content(mock_lambda, mock_bedrock, aws_environment):
    """Test handling of empty file content."""
    mock_lambda.invoke.return_value = {
        'Payload': MagicMock(read=lambda: json.dumps({
            'statusCode': 200,
            'body': json.dumps({'content': ''})
        }).encode())
    }
    
    mock_bedrock.invoke_model.return_value = {
        'body': MagicMock(read=lambda: json.dumps({
            'content': [{'text': 'Summary of empty document'}]
        }).encode())
    }
    
    event = create_test_event(TEST_FILE_ID)
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'summary' in body


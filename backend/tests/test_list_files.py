# tests/test_list_files.py
import json
import pytest

# Import the handler function directly now that __init__.py is present
from lambda_functions.list_files.handler import lambda_handler

def test_list_files_response_structure():
    """
    Tests that the lambda_handler returns a valid HTTP response structure
    with the expected status code and body content.
    """
    # Call the Lambda handler with empty event/context objects
    response = lambda_handler({}, None)
    
    # Check the required HTTP structure
    assert 'statusCode' in response
    assert response['statusCode'] == 200
    assert 'body' in response

    # Check the JSON content inside the body
    body_data = json.loads(response['body'])
    assert 'message' in body_data
    assert 'Hello from list_files Lambda' in body_data['message']
    assert 'files' in body_data
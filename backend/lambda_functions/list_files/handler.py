# lambda_functions/list_files/handler.py
import json

def lambda_handler(event, context):
    """
    The entry point for the AWS Lambda execution.
    Returns a basic 200 OK JSON response.
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Hello from list_files Lambda! Environment is active.',
            'files': []
        })
    }
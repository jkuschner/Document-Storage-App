# lambda_functions/list_files/handler.py
import json

def lambda_handler(event, context):
    """
    A hello world function to confirm basic execution
    """
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from list_files!',
            'count': 0,
            'files': []
        })
    }
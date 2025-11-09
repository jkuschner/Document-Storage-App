import json
import os
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
#dynamodb = boto3.resource('dynamodb')
#FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
#files_table = dynamodb.Table(FILES_TABLE_NAME)


def lambda_handler(event, context):
    """
    Lists all files for a user by querying DynamoDB.
    """

    dynamodb = boto3.resource('dynamodb')
    FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
    files_table = dynamodb.Table(FILES_TABLE_NAME)

    try:
        # Extract userId from request
        # TODO: In production, get this from Cognito authorizer claims
        # For now, check query parameters or use a default
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId', 'test-user')
        
        # Query DynamoDB for user's files
        response = files_table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        
        files = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'files': files,
                'count': len(files)
            })
        }
        
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Failed to list files',
                'message': str(e)
            })
        }
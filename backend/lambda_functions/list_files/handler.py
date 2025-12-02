import json
import os
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
files_table = dynamodb.Table(FILES_TABLE_NAME)


def lambda_handler(event, context):
    """
    Lists all files for a user by querying DynamoDB.
    """
    try:
        # Extract userId from request
        # 🔒 SECURE FIX: Get userId from JWT token (Cognito authorizer)
        try:
            user_id = event['requestContext']['authorizer']['claims']['sub']
        except (KeyError, TypeError):
            # If the Authorizer fails, the API Gateway *should* block this, 
            # but this is a defensive fallback to ensure no unauthorized access.
            return {
                'statusCode': 401,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Unauthorized: Missing JWT claim'})
            }

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
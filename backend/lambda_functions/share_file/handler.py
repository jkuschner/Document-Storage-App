import json
import os
import boto3
import uuid
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')

FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
SHARED_LINKS_TABLE_NAME = os.environ.get('SHARED_LINKS_TABLE_NAME', 'SharedLinksTable-dev')

files_table = dynamodb.Table(FILES_TABLE_NAME)
shared_links_table = dynamodb.Table(SHARED_LINKS_TABLE_NAME)


def lambda_handler(event, context):
    """
    Creates a shareable link for a file.
    """
    try:
        # Get fileId from path parameters
        path_params = event.get('pathParameters', {})
        file_id = path_params.get('fileId')
        
        # Get userId from query params (TODO: from Cognito)
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId', 'test-user')
        
        # Parse request body for expiration
        body = json.loads(event.get('body', '{}'))
        expiration_hours = body.get('expirationHours', 24)
        
        if not file_id:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'fileId is required'})
            }
        
        # Verify file exists
        response = files_table.get_item(
            Key={'userId': user_id, 'fileId': file_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'File not found'})
            }
        
        # Generate share token
        share_token = str(uuid.uuid4())
        expiration_time = datetime.utcnow() + timedelta(hours=expiration_hours)
        
        # Store share link in DynamoDB
        shared_links_table.put_item(
            Item={
                'shareToken': share_token,
                'fileId': file_id,
                'userId': user_id,
                'createdAt': datetime.utcnow().isoformat(),
                'expiresAt': int(expiration_time.timestamp())  # TTL in epoch seconds
            }
        )
        
        # Generate share URL (TODO: use actual domain)
        share_url = f"https://your-app-domain.com/shared/{share_token}"
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'shareUrl': share_url,
                'shareToken': share_token,
                'expiresAt': expiration_time.isoformat(),
                'message': 'Share link created successfully'
            })
        }
        
    except Exception as e:
        print(f"Error creating share link: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
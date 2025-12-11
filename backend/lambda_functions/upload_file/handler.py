import json
import os
import boto3
import uuid
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

FILE_BUCKET_NAME = os.environ.get('FILE_BUCKET_NAME', 'file-storage-dev')
FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
files_table = dynamodb.Table(FILES_TABLE_NAME)


def lambda_handler(event, context):
    """
    Generates a presigned URL for file upload and creates DynamoDB entry.
    """
    try:
        # 🔒 SECURE FIX: Get userId from JWT token (Cognito authorizer)
        try:
            # The 'sub' claim holds the verified User ID
            user_id = event['requestContext']['authorizer']['claims']['sub']
        except (KeyError, TypeError):
            # If the token is missing/invalid (API Gateway should mostly prevent this)
            return {
                'statusCode': 401,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Unauthorized: Missing JWT claim'})
            }

        # Parse request body (now that we have the secured user_id)
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('fileName')
        content_type = body.get('contentType', 'application/octet-stream')
        file_size = body.get('size')
        
        if not file_name:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'fileName is required'})
            }
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        s3_key = f"{user_id}/{file_id}/{file_name}"
        
        # Generate presigned URL for upload
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': FILE_BUCKET_NAME,
                'Key': s3_key,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        # Create DynamoDB entry
        item = {
            'userId': user_id,
            'fileId': file_id,
            'fileName': file_name,
            's3Key': s3_key,
            'contentType': content_type,
            'uploadDate': datetime.utcnow().isoformat(),
            'status': 'pending'
        }

        # Add size if provided
        if file_size is not None:
            item['size'] = file_size

        files_table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'fileId': file_id,
                'message': 'Upload URL generated successfully'
            })
        }
        
    except Exception as e:
        print(f"Error generating upload URL: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
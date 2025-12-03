import json
import os
import boto3

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

FILE_BUCKET_NAME = os.environ.get('FILE_BUCKET_NAME', 'file-storage-dev')
FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
files_table = dynamodb.Table(FILES_TABLE_NAME)


def lambda_handler(event, context):
    """
    Deletes a file from S3 and removes metadata from DynamoDB.
    """
    try:
        # Get fileId from path parameters
        path_params = event.get('pathParameters', {})
        file_id = path_params.get('fileId')

        # Get userId from JWT token (Cognito authorizer)
        try:
            user_id = event['requestContext']['authorizer']['claims']['sub']
        except (KeyError, TypeError):
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Unauthorized: Missing authentication'})
            }
        
        if not file_id:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'fileId is required'})
            }
        
        # Get file metadata from DynamoDB
        response = files_table.get_item(
            Key={'userId': user_id, 'fileId': file_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'File not found'})
            }
        
        file_item = response['Item']

        # Verify user owns this file
        if file_item.get('userId') != user_id:
            return {
                'statusCode': 403,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Access denied. You do not have permission to delete this file.'})
            }

        s3_key = file_item['s3Key']

        # Delete from S3
        s3_client.delete_object(
            Bucket=FILE_BUCKET_NAME,
            Key=s3_key
        )
        
        # Delete from DynamoDB
        files_table.delete_item(
            Key={'userId': user_id, 'fileId': file_id}
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'File deleted successfully',
                'fileId': file_id
            })
        }
        
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
import json
import os
import boto3

def lambda_handler(event, context,dynamodb_resource = None):
    """
    Deletes a file from S3 and removes metadata from DynamoDB.
    """
    #s3_client = boto3.client('s3')
    #dynamodb = boto3.resource('dynamodb')

    FILE_BUCKET_NAME = os.environ.get("FILE_BUCKET_NAME", "file-storage-dev")
    FILES_TABLE_NAME = os.environ.get("FILES_TABLE_NAME", "files-dev")
    REGION = "us-west-2"

    s3_client = boto3.client("s3", region_name=REGION)
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    files_table = dynamodb.Table(FILES_TABLE_NAME)

    try:
        # Get fileId from path parameters
        path_params = event.get('pathParameters', {})
        file_id = path_params.get('fileId')
        
        # Get userId from query params (TODO: from Cognito)
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId', 'test-user')
        
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
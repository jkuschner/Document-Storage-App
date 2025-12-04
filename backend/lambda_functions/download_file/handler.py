import json
import os
import boto3

#s3_client = boto3.client('s3')
#dynamodb = boto3.resource('dynamodb')

#FILE_BUCKET_NAME = os.environ.get('FILE_BUCKET_NAME', 'file-storage-dev')
#FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
#files_table = dynamodb.Table(FILES_TABLE_NAME)


def lambda_handler(event, context):
    """
    Generates a presigned URL for file download.
    """
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
                'body': json.dumps({'error': 'Access denied. You do not have permission to download this file.'})
            }

        s3_key = file_item['s3Key']

        # Generate presigned URL for download
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': FILE_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'downloadUrl': download_url,
                'fileName': file_item['fileName'],
                'fileId': file_id
            })
        }
        
    except Exception as e:
        print(f"Error generating download URL: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
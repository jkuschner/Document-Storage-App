# lambda functions/delete_file/handler.py
import json
import os
import boto3

S3_CLIENT = boto3.client('s3')
BUCKET_NAME = os.environ.get('FILE_BUCKET_NAME', 'test-dummy-bucket')

def lambda_handler(event, context):
    """
    Deletes a specified file from the S3 bucket.
    Expects 'filename' in the query string parameters.
    """
    try:
        file_name = event.get('queryStringParameter', {}).get('filename')
        if not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing filename query parameter.'
                })
            }

        S3_CLIENT.delete_object(
            Bucket=BUCKET_NAME,
            Key=file_name
        )

        return {
            'statusCode': 204,
            'body': json.dumps({
                'message': f'File {file_name} deleted successfully.'
            })
        }

    except Exception as e:
        print(f"Error deleting file: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error while deleting file.',
                'error': str(e)
            })
        }
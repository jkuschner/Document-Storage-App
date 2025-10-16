# lambda_functions/list_files/index.py
import json
import os
import boto3

S3_CLIENT = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'test-dummy-bucket')

def lambda_handler(event, context):
    """
    Lists files in the configured S3 bucket.
    """
    try:
        # Call the S3 API to list objects in bucket
        response = S3_CLIENT.list_objects_v2(Bucket=BUCKET_NAME)

        # Exctract file keys (filenames) from the response
        file_keys = [
            item['Key']
            for item in response.get('Contents', [])
        ]

        # return successful response with file list
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': f'Successfully listed {len(file_keys)} files.',
                'files': file_keys
            })
        }

    except Exception as e:
        print(f"Error listing files: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error while listing files.',
                'error': str(e)
            })
        }
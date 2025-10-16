# lambda_functions/download_file/handler.py
import json
import os
import boto3
import base64
from botocore.exceptions import ClientError

S3_CLIENT = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'test-dummy-bucket')

def lambda_handler(event, context):
    """
    Downloads a specific file from S3 bucket.
    expects 'filename' in the query string parameters
    """
    try:
        file_name = event.get('queryStringParameters', {}).get('filename')
        
        if not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing filename query parameter.'})
            }

        # Get the object from S3
        response = S3_CLIENT.get_object(
            Bucket=BUCKET_NAME,
            Key=file_name
        )

        file_content = response['Body'].read()

        # Encode content for API Gateway Binary Handling
        # content must be base64 encoded and flag set to true for API Gateway
        # to correctly handle binary data (images, .zip, PDFs, etc...)
        encoded_content = base64.b64encode(file_content).decode('utf-8')

        return {
            'statusCode': 200,
            'headers': {
                # This header is crucial for the browser to download the file
                'Content-Disposition': f'attachment; filename="{file_name}"', 
                'Content-Type': response.get('ContentType', 
                                             'application/octet-stream')
            },
            'body': encoded_content,
            # This flag tells API Gateway to decode the base64 body before sending
            'isBase64Encoded': True 
        }

    except ClientError as e:
        # Handle the common case where the file is not found (404)
        if e.response['Error']['Code'] == 'NoSuchKey':
            return {
                'statusCode': 404,
                'body': json.dumps({'message': f'File {file_name} not found.'})
            }
        
        # Handle other S3-related errors
        print(f"S3 Client Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error on S3 operation.',
                'error': str(e)
            })
        }
            
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Unexpected internal server error.',
                'error': str(e)
            })
        }
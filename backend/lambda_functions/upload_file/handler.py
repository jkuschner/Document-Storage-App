# lambda_functions/upload_file/handler.py
import json
import os
import base64
import boto3

S3_CLIENT = boto3.client('s3')
BUCKET_NAME = os.environ.get('FILE_BUCKET_NAME', 'test-dummy-bucket')

def lambda_handler(event, context):
    """
    Handles file uploads by decoding the Base64 body and saving it to S3.
    Expects 'filename' in the query string parameters.
    """
    try:
        # Get filename from query string parameters
        file_name = event.get('queryStringParameters', {}).get('filename')
        if not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing filename query parameter.'
                    })
            }

        # get base64 encoded body
        encoded_body = event.get('body')
        if not encoded_body:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing request body.'})
            }

        # decode the body
        file_content = base64.b64decode(encoded_body)

        # upload decoded content to S3
        S3_CLIENT.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=file_content
        )

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': f'File {file_name} uploaded successfully'
            })
        }
    
    except Exception as e:
        print(f"Error uploading file: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error while uploading file.',
                'error': str(e)
            })
        }
# lambda_functions/upload_file/handler.py
import json
import os
import boto3

S3_CLIENT = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'test-dummy-bucket')

def lambda_handler(event, context):
    """
    Handles file uploads by returning a presigned PUT URL that allows the client
    to upload their file directly to S3
    """
    try:
        # Get metadata from the request body
        request_body = json.loads(event.get('body', '{}'))
        file_name = request_body.get('filename')
        content_type = request_body.get('contentType', 'application/octet-stream')

        if not file_name:
            return {
                'statusCode': 400, 
                'body': json.dumps({'message': 'Missing filename.'})
            }

        # Generate the PUT presigned URL
        upload_url = S3_CLIENT.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET_NAME, 
                'Key': file_name,
                # Crucial: Tells S3 what Content-Type to expect from the client upload
                'ContentType': content_type 
            },
            ExpiresIn=3600 
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pre-signed upload URL generated successfully.',
                'uploadUrl': upload_url,
                'fileKey': file_name
            })
        }

    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error.',
                'error': str(e)
            })
        }
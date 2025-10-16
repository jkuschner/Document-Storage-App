# lambda_functions/share_file/index.py
import json
import os
import boto3

# Initialize S3 client and get bucket name from environment
S3_CLIENT = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'test-dummy-bucket')

def lambda_handler(event, context):
    """
    Generates a presigned URL for secure, temporary access to a file.
    Expects 'filename' in the query string parameters.
    """
    try:
        file_name = event.get('queryStringParameters', {}).get('filename')
        
        if not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing filename query parameter.'})
            }
        
        # generate presigned URL
        # ClientMethod='get_object' specifies URL is for downloading/viewing
        # ExpiresIn=3600 sets link expiration time to 1 hour(3600 sec)
        url = S3_CLIENT.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_name},
            ExpiresIn=3600
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Presigned URL generated for {file_name}. Expires in 1 hour.',
                'url': url
            })
        }
    
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error while sharing file.',
                'error': str(e)
            })
        }
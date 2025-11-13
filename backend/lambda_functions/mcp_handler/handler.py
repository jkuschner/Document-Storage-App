import json
import os
import boto3
from PyPDF2 import PdfReader
from io import BytesIO
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Get environment variables
FILES_TABLE_NAME = os.environ['FILES_TABLE_NAME']
FILE_BUCKET_NAME = os.environ['FILE_BUCKET_NAME']

table = dynamodb.Table(FILES_TABLE_NAME)


def lambda_handler(event, context):
    """
    MCP Handler - Implements Model Context Protocol endpoints
    
    Handles:
    - resources/list: Query DynamoDB for user's files
    - resources/read: Fetch file from S3 and extract text (PDF support)
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        logger.info(f"MCP Handler invoked with action: {action}")
        
        if action == 'resources/list':
            return handle_resources_list(body)
        elif action == 'resources/read':
            return handle_resources_read(body)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid action',
                    'message': f'Action must be "resources/list" or "resources/read", got: {action}'
                })
            }
    
    except Exception as e:
        logger.error(f"Error in MCP handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def handle_resources_list(body):
    """
    List all files for a user from DynamoDB
    
    Expected body: {"action": "resources/list", "userId": "user123"}
    Returns: {"resources": [{"id": "...", "name": "...", "uri": "..."}]}
    """
    try:
        # Get userId from body (in production, extract from JWT token)
        user_id = body.get('userId', 'test-user')
        
        logger.info(f"Listing resources for user: {user_id}")
        
        # Query DynamoDB for user's files
        response = table.scan(
            FilterExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        # Format resources for MCP protocol
        resources = []
        for item in response.get('Items', []):
            resources.append({
                'id': item.get('fileId'),
                'name': item.get('fileName'),
                'uri': f"s3://{FILE_BUCKET_NAME}/{item.get('s3Key')}",
                'mimeType': item.get('contentType', 'application/octet-stream'),
                'size': item.get('fileSize', 0)
            })
        
        logger.info(f"Found {len(resources)} resources for user {user_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'resources': resources
            })
        }
    
    except Exception as e:
        logger.error(f"Error listing resources: {str(e)}", exc_info=True)
        raise


def handle_resources_read(body):
    """
    Read file content from S3 and extract text if PDF
    
    Expected body: {"action": "resources/read", "resource_id": "file123", "userId": "user123"}
    Returns: {"content": "file content as text"}
    """
    try:
        resource_id = body.get('resource_id')
        user_id = body.get('userId', 'test-user')
        
        if not resource_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing resource_id',
                    'message': 'resource_id is required for resources/read action'
                })
            }
        
        logger.info(f"Reading resource {resource_id} for user {user_id}")
        
        # Get file metadata from DynamoDB (table has composite key: userId + fileId)
        response = table.get_item(
            Key={
                'userId': user_id,
                'fileId': resource_id
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'File not found',
                    'message': f'Resource {resource_id} not found'
                })
            }
        
        item = response['Item']
        s3_key = item.get('s3Key')
        file_name = item.get('fileName')
        
        # Verify user owns this file
        if item.get('userId') != user_id:
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Access denied',
                    'message': 'You do not have permission to access this file'
                })
            }
        
        # Get file from S3
        logger.info(f"Fetching file from S3: {s3_key}")
        s3_response = s3.get_object(Bucket=FILE_BUCKET_NAME, Key=s3_key)
        content = s3_response['Body'].read()
        
        # Extract text if PDF
        if file_name.lower().endswith('.pdf'):
            logger.info("Extracting text from PDF")
            try:
                pdf_reader = PdfReader(BytesIO(content))
                text_content = ''
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + '\n'
                content = text_content.encode('utf-8')
            except Exception as pdf_error:
                logger.error(f"PDF extraction failed: {str(pdf_error)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'PDF extraction failed',
                        'message': f'Could not extract text from PDF: {str(pdf_error)}'
                    })
                }
        
        # Decode content (handle binary files gracefully)
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            # For binary files, return base64 encoded
            import base64
            content_str = base64.b64encode(content).decode('utf-8')
            logger.info("Content encoded as base64 (binary file)")
        
        logger.info(f"Successfully read resource {resource_id}, size: {len(content_str)} chars")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'content': content_str,
                'fileName': file_name,
                'mimeType': item.get('contentType', 'application/octet-stream')
            })
        }
    
    except s3.exceptions.NoSuchKey:
        logger.error(f"S3 key not found: {s3_key}")
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'File not found in storage',
                'message': f'S3 object not found: {s3_key}'
            })
        }
    except Exception as e:
        logger.error(f"Error reading resource: {str(e)}", exc_info=True)
        raise

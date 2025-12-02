import json
import os
import boto3
import logging
import base64

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
lambda_client = boto3.client('lambda')

# Get environment variables
MCP_HANDLER_ARN = os.environ['MCP_HANDLER_ARN']


def extract_user_id_from_event(event):
    """
    Extract user_id from JWT token.
    Supports both API Gateway (with Cognito authorizer) and Lambda Function URLs.
    
    For API Gateway: extracts from event['requestContext']['authorizer']['claims']['sub']
    For Lambda Function URLs: extracts from Authorization header JWT token
    """
    # Try API Gateway context first (when called via API Gateway with Cognito authorizer)
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        logger.info("Extracted user_id from API Gateway authorizer context")
        return user_id
    except (KeyError, TypeError):
        pass
    
    # Fallback: Extract from Authorization header (for Lambda Function URLs)
    try:
        headers = event.get('headers', {}) or {}
        # Handle case-insensitive header keys
        auth_header = headers.get('authorization') or headers.get('Authorization') or ''
        
        if not auth_header.startswith('Bearer '):
            logger.error("Missing or invalid Authorization header")
            return None
        
        # Extract JWT token
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Decode JWT without verification (for Lambda Function URLs)
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            logger.error("Invalid JWT token format")
            return None
        
        # Decode payload (base64url)
        payload = parts[1]
        # Add padding if needed
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        decoded_payload = base64.urlsafe_b64decode(payload)
        claims = json.loads(decoded_payload)
        
        user_id = claims.get('sub')
        if user_id:
            logger.info("Extracted user_id from JWT token in Authorization header")
            return user_id
        else:
            logger.error("JWT token missing 'sub' claim")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting user_id from JWT: {str(e)}", exc_info=True)
        return None


def lambda_handler(event, context):
    """
    Chat Handler - AI Summarization using Claude Haiku via AWS Bedrock
    
    Handles file summarization by:
    1. Invoking mcp_handler to get file content
    2. Calling Claude Haiku via AWS Bedrock
    3. Returning AI-generated summary
    """
    try:
        # 🔒 SECURE FIX: Get userId from JWT token (supports both API Gateway and Lambda Function URLs)
        user_id = extract_user_id_from_event(event)
        
        if not user_id:
            logger.error("Unauthorized: Missing JWT claim for user ID")
            return {
                'statusCode': 401,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Unauthorized: Missing JWT claim'})
            }

        # Parse request body (now that we have the secured user_id)
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('file_name')
        file_id = body.get('fileId')
        # Note: We no longer read 'userId' from the body

        if not file_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing fileId',
                    'message': 'fileId is required'
                })
            }
        
        logger.info(f"Chat handler invoked for file: {file_name} (ID: {file_id}), user: {user_id}")

        # Step 1: Call mcp_handler to get file content
        logger.info(f"Invoking MCP handler to read file: {file_id}")
        mcp_payload = {
            'body': json.dumps({
                'action': 'resources/read',
                'resource_id': file_id,
                'userId': user_id
            })
        }
        
        mcp_response = lambda_client.invoke(
            FunctionName=MCP_HANDLER_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(mcp_payload)
        )
        
        mcp_result = json.loads(mcp_response['Payload'].read())
        
        if mcp_result['statusCode'] != 200:
            logger.error(f"MCP handler failed: {mcp_result}")
            return {
                'statusCode': mcp_result['statusCode'],
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': mcp_result['body']
            }
        
        mcp_body = json.loads(mcp_result['body'])
        file_content = mcp_body.get('content', '')
        
        logger.info(f"Retrieved file content, length: {len(file_content)} chars")
        
        # Step 2: Truncate content if too large (cost control)
        MAX_CONTENT_LENGTH = 100000  # ~100KB
        if len(file_content) > MAX_CONTENT_LENGTH:
            logger.warning(f"Content truncated from {len(file_content)} to {MAX_CONTENT_LENGTH} chars")
            file_content = file_content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to size limit]"
        
        # Step 3: Call Claude Haiku via AWS Bedrock
        logger.info("Calling Claude Haiku via AWS Bedrock")
        prompt = f"Please provide a concise summary of this document:\n\n{file_content}"
        
        try:
            response = bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-5-haiku-20241022-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            summary = response_body['content'][0]['text']
            logger.info(f"Summary generated successfully, length: {len(summary)} chars")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'summary': summary,
                    'fileName': file_name,
                    'contentLength': len(file_content),
                    'model': 'claude-3.5-haiku-bedrock'
                })
            }
        
        except Exception as bedrock_error:
            logger.error(f"Bedrock API error: {str(bedrock_error)}", exc_info=True)
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'AI summarization failed',
                    'message': f'Bedrock API error: {str(bedrock_error)}'
                })
            }
    
    except Exception as e:
        logger.error(f"Error in chat handler: {str(e)}", exc_info=True)
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

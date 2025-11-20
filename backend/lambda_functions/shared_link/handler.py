import json
import os
import time
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

SHARED_LINKS_TABLE = os.environ.get('SHARED_LINKS_TABLE')
FILE_BUCKET = os.environ.get('FILE_BUCKET')

if not SHARED_LINKS_TABLE or not FILE_BUCKET:
    raise RuntimeError('Shared link lambda missing required environment variables')

shared_links_table = dynamodb.Table(SHARED_LINKS_TABLE)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle GET /shared/{linkId} - resolve shared link and return download URL.
    """
    try:
        link_id = (event.get('pathParameters') or {}).get('linkId')
        if not link_id:
            return _response(400, {'error': 'Missing linkId parameter'})

        try:
            response = shared_links_table.get_item(Key={'linkId': link_id})
        except ClientError as err:
            print(f"DynamoDB error retrieving link {link_id}: {err}")
            return _response(500, {'error': 'Database error'})

        share_record = response.get('Item')
        if not share_record:
            return _response(404, {'error': 'Share link not found'})

        current_time = int(time.time())
        expires_at = share_record.get('expiresAt')
        if expires_at and expires_at <= current_time:
            return _response(404, {'error': 'Share link has expired'})

        s3_key = share_record.get('s3Key')
        file_name = share_record.get('fileName', 'download')
        if not s3_key:
            return _response(500, {'error': 'Invalid share record'})

        try:
            download_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': FILE_BUCKET,
                    'Key': s3_key,
                    'ResponseContentDisposition': f'attachment; filename="{file_name}"',
                },
                ExpiresIn=300,
            )
        except ClientError as err:
            print(f"S3 presigned URL generation failed for {s3_key}: {err}")
            return _response(500, {'error': 'Failed to generate download URL'})

        return _response(
            200,
            {
                'fileName': file_name,
                'downloadUrl': download_url,
                'expiresAt': expires_at,
            },
        )

    except Exception as exc:
        print(f"Unexpected error resolving shared link: {exc}")
        return _response(500, {'error': 'Internal server error'})


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
        },
        'body': json.dumps(body),
    }


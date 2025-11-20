import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import boto3

dynamodb = boto3.resource('dynamodb')

FILES_TABLE_NAME = os.environ.get('FILES_TABLE_NAME', 'files-dev')
SHARED_LINKS_TABLE_NAME = os.environ.get('SHARED_LINKS_TABLE_NAME', 'SharedLinksTable-dev')

files_table = dynamodb.Table(FILES_TABLE_NAME)
shared_links_table = dynamodb.Table(SHARED_LINKS_TABLE_NAME)


def lambda_handler(event, context):
    """
    Creates a shareable link for a file owned by the authenticated user.
    """
    try:
        user_id = _get_user_id(event)
        if not user_id:
            return _response(401, {'error': 'Unauthorized'})

        file_id = (event.get('pathParameters') or {}).get('fileId')
        if not file_id:
            return _response(400, {'error': 'fileId is required'})

        body = json.loads(event.get('body') or '{}')
        expiration_hours = _parse_expiration_hours(body.get('expirationHours'))

        file_item = files_table.get_item(
            Key={'userId': user_id, 'fileId': file_id}
        ).get('Item')

        if not file_item:
            return _response(404, {'error': 'File not found'})

        link_id = secrets.token_urlsafe(18)
        expiration_time = datetime.utcnow() + timedelta(hours=expiration_hours)
        expires_at = int(expiration_time.timestamp())

        shared_links_table.put_item(
            Item={
                'shareToken': link_id,
                'linkId': link_id,
                'fileId': file_id,
                'userId': user_id,
                's3Key': file_item['s3Key'],
                'fileName': file_item['fileName'],
                'createdAt': datetime.utcnow().isoformat(),
                'expiresAt': expires_at,
            }
        )

        share_base_url = os.environ.get('SHARE_BASE_URL')
        if not share_base_url:
            raise RuntimeError('SHARE_BASE_URL environment variable not set')

        share_url = f"{share_base_url}/shared/{link_id}"
        return _response(
            200,
            {
                'shareUrl': share_url,
                'expiresAt': expiration_time.isoformat() + 'Z',
            }
        )

    except Exception as exc:
        print(f"Error creating share link: {exc}")
        return _response(500, {'error': 'Internal server error'})


def _get_user_id(event: dict) -> Optional[str]:
    return (
        event.get('requestContext', {})
        .get('authorizer', {})
        .get('claims', {})
        .get('sub')
    )


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


def _parse_expiration_hours(raw_value) -> int:
    default_hours = 24
    try:
        value = int(raw_value) if raw_value is not None else default_hours
    except (TypeError, ValueError):
        value = default_hours
    return _clamp(value, 1, 168)


def _response(status_code: int, body: dict) -> dict:
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        },
        'body': json.dumps(body),
    }
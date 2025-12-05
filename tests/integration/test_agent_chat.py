import json
import os
import uuid
import base64
import requests

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "integration_config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

CHAT_URL = config["chat_url"]
API_BASE = config["api_base_url"]
TEST_USER = config["test_user"]

def make_fake_jwt(sub="test-user"):
    """
    Create a simple unsigned JWT with {"sub": sub}
    AWS Lambda URL flow does NOT verify the signature, so should work.
    """
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "none"}).encode()
    ).rstrip(b"=")

    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": sub}).encode()
    ).rstrip(b"=")

    # Signature can be anything because signature isn't verified
    return f"{header.decode()}.{payload.decode()}.signature"

def test_chat_summarization_flow():
    """
    Full integration test:
    1. Upload test file
    2. Call chat handler (Lambda URL)
    3. Verify summary is returned
    """

    jwt_token = make_fake_jwt(TEST_USER)
    headers = {"Authorization": f"Bearer {jwt_token}"}

    # Create test file
    filename = f"summary-test-{uuid.uuid4()}.txt"
    upload_url = f"{API_BASE}/upload"

    upload_payload = {
        "fileName": filename,
        "contentType": "text/plain",
        "userId": TEST_USER
    }

    # Step 1: Request upload URL
    upload_resp = requests.post(upload_url, json=upload_payload, headers=headers)
    assert upload_resp.status_code == 200

    upload_body = upload_resp.json()
    file_id = upload_body["fileId"]
    presigned = upload_body["uploadUrl"]

    # Step 2: Upload content
    content = b"Integration test AI summary content. This is a small test document."
    put = requests.put(presigned, data=content)
    assert put.status_code in [200, 204], f"Presigned PUT failed: {put.status_code}"

    # Step 3: Call chat handler
    chat_payload = {
        "fileId": file_id,
        "file_name": filename,
        "userId": TEST_USER
    }

    #resp = requests.post(CHAT_URL, json={"body": json.dumps(chat_payload)})
    resp = requests.post(
        CHAT_URL,
        json={"body": json.dumps(chat_payload)},
        headers=headers,
    )
    assert resp.status_code == 200, f"Chat handler returned {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "summary" in data
    assert len(data["summary"]) > 0
    assert data["model"] == "claude-3.5-haiku-bedrock"
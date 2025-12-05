import json
import os
import uuid
import requests
import jwt

# Load integration configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "integration_config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

API_BASE = config["api_base_url"]
TEST_USER = config["test_user"]

TEST_JWT = jwt.encode({"sub": TEST_USER}, "dummy-secret", algorithm="HS256")
AUTH_HEADER = {"Authorization": f"Bearer {TEST_JWT}"}


def test_file_operations_end_to_end():
    """
    End-to-end test of file upload → list → delete using the deployed API Gateway.
    """

    file_name = f"itest-{uuid.uuid4()}.txt"

    # 1. Create upload request
    upload_url = f"{API_BASE}/upload"
    upload_payload = {
        "fileName": file_name,
        "contentType": "text/plain",
        "userId": TEST_USER
    }

    upload_resp = requests.post(upload_url, json=upload_payload)
    assert upload_resp.status_code == 200

    upload_body = upload_resp.json()
    assert "uploadUrl" in upload_body
    assert "fileId" in upload_body
    file_id = upload_body["fileId"]

    # 2. Upload file content to S3 pre-signed URL
    put_resp = requests.put(upload_body["uploadUrl"], data=b"Hello Integration Test")
    assert put_resp.status_code in [200, 204]

    # 3. List files
    list_url = f"{API_BASE}/list?userId={TEST_USER}"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200

    files = list_resp.json()["files"]
    assert any(f["fileId"] == file_id for f in files)

    # 4. Delete file
    delete_url = f"{API_BASE}/delete/{file_id}?userId={TEST_USER}"
    delete_resp = requests.delete(delete_url)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"].lower().startswith("file deleted")

    # 5. Verify deletion
    list_after = requests.get(list_url)
    files_after = list_after.json()["files"]
    assert not any(f["fileId"] == file_id for f in files_after)

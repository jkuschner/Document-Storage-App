import json
import os
import requests
import jwt

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "integration_config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

MCP_URL = config["mcp_url"]
TEST_USER = config["test_user"]

TEST_JWT = jwt.encode({"sub": TEST_USER}, "dummy-secret", algorithm="HS256")
AUTH_HEADER = {"Authorization": f"Bearer {TEST_JWT}"}


def test_mcp_list_resources():
    """
    Calls the MCP handler directly using Lambda Function URL
    to list user resources.
    """

    payload = {
        "body": json.dumps({
            "action": "resources/list",
            "userId": TEST_USER
        })
    }

    resp = requests.post(MCP_URL, json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert "resources" in body
    assert isinstance(body["resources"], list)


def test_mcp_read_missing_resource():
    """
    Tests reading a fileId that does not exist.
    Should return a 404-style error.
    """

    payload = {
        "body": json.dumps({
            "action": "resources/read",
            "resource_id": "non-existent-id-123",
            "userId": TEST_USER
        })
    }

    resp = requests.post(MCP_URL, json=payload)

    # MCP handler should not crash — it should report a clean error
    assert resp.status_code in [400, 404]

    data = resp.json()
    assert "error" in data or "message" in data

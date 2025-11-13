┌─────────────────────────────────────────────────────────────┐
│                         USER / BROWSER                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├──────────────────┐
                              ▼                  ▼
                    ┌──────────────┐   ┌──────────────────┐
                    │  CloudFront  │   │   API Gateway    │
                    │   (CDN)      │   │                  │
                    └──────────────┘   └──────────────────┘
                              │                  │
                              ▼                  ▼
                    ┌──────────────┐   ┌──────────────────┐
                    │  S3 Bucket   │   │  Lambda Functions│
                    │  (Frontend)  │   │  - upload_file   │
                    └──────────────┘   │  - download_file │
                                       │  - list_files    │
                    ┌──────────────┐   │  - delete_file   │
                    │ AWS Cognito  │   │  - share_file    │
                    │   (Auth)     │◄──┤  - mcp_handler   │
                    └──────────────┘   │  - chat_handler  │
                                       └──────────────────┘
                                                 │
                                       ┌─────────┴─────────┐
                                       ▼                   ▼
                              ┌──────────────┐   ┌──────────────┐
                              │  DynamoDB    │   │  S3 Bucket   │
                              │  (Metadata)  │   │  (Files)     │
                              └──────────────┘   └──────────────┘

DATA FLOW - Upload File:
1. User authenticates via Cognito
2. Frontend requests upload URL from API Gateway
3. Lambda generates S3 pre-signed URL
4. User uploads file directly to S3
5. Lambda stores metadata in DynamoDB

DATA FLOW - List Files:
1. User authenticates via Cognito
2. Frontend calls API Gateway /list-files
3. Lambda queries DynamoDB by userId
4. Returns file metadata to user

## AWS Bedrock Integration

The system integrates AWS Bedrock for AI-powered file analysis:

┌─────────────────────────────────────────────────────────┐
│              AI SUMMARIZATION FLOW                       │
└─────────────────────────────────────────────────────────┘

User → API Gateway → chat_handler Lambda
                          │
                          ├──→ Invokes mcp_handler Lambda
                          │      │
                          │      ├──→ Query DynamoDB (userId + fileId)
                          │      │
                          │      └──→ Fetch from S3 (extract PDF text if needed)
                          │
                          ├──→ Receive file content
                          │
                          └──→ Call AWS Bedrock (Claude 3.5 Haiku)
                                   │
                                   └──→ Generate AI summary
                                         │
                                         └──→ Return to user

**Key Features:**
- **Model**: Claude 3.5 Haiku (cost-optimized)
- **Cost**: ~$0.80/$4 per 1M tokens (input/output)
- **PDF Support**: Automatic text extraction using PyPDF2
- **Lambda-to-Lambda**: chat_handler invokes mcp_handler internally

## MCP (Model Context Protocol) Implementation

The system implements MCP protocol endpoints for standardized AI model interaction:

**Supported Actions:**

1. **resources/list**
   - Lists all files for a user
   - Queries DynamoDB by userId
   - Returns array of resources with id, name, uri, mimeType, size

2. **resources/read**
   - Reads file content from S3
   - Extracts text from PDFs automatically
   - Returns file content as text or base64 for binary files

**Request Format:**
```json
{
  "action": "resources/list" | "resources/read",
  "userId": "string",
  "resource_id": "string" // Only for resources/read
}
```

**Response Format:**
```json
// resources/list
{
  "resources": [
    {
      "id": "file-uuid",
      "name": "document.pdf",
      "uri": "s3://bucket/key",
      "mimeType": "application/pdf",
      "size": 1024
    }
  ]
}

// resources/read
{
  "content": "extracted text content",
  "fileName": "document.pdf",
  "mimeType": "application/pdf"
}
```
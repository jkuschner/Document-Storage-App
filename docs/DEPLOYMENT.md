# Document Storage App - Deployment Guide

## Overview
This document provides deployment information for the Document Storage App infrastructure deployed on AWS using CloudFormation.

## Deployed Stacks

### 1. Infrastructure Stack (`dev-infrastructure-stack`)
**Purpose**: Core AWS resources (S3 bucket and DynamoDB tables)
**Template**: `infrastructure/cloudformation/infrastructure.yml`

**Resources Created**:
- S3 Bucket: `file-storage-dev-{AWS_ACCOUNT_ID}`
- DynamoDB Table: `files-dev` (for file metadata)
- DynamoDB Table: `SharedLinksTable-dev` (for sharing functionality)

**Key Outputs**:
- `FileStorageBucketName`: S3 bucket name for file storage
- `FilesTableName`: DynamoDB table name for file metadata
- `SharedLinksTableName`: DynamoDB table name for shared links

### 2. Authentication Stack (`dev-auth-stack`)
**Purpose**: User authentication and authorization
**Template**: `infrastructure/cloudformation/auth.yml`

**Resources Created**:
- Cognito User Pool: `file-storage-users-dev`
- Cognito User Pool Client: `file-storage-client-dev`
- Cognito Identity Pool: `file_storage_identity_dev`

**Key Outputs**:
- `UserPoolId`: Cognito User Pool ID
- `UserPoolClientId`: Cognito User Pool Client ID
- `IdentityPoolId`: Cognito Identity Pool ID

### 3. Backend Stack (`production-backend-stack`)
**Purpose**: Lambda functions and API Gateway
**Template**: `infrastructure/cloudformation/backend.yml`

**Resources Created**:
- **7 Lambda Functions:**
  - `file-storage-upload-file-dev` - Handle file uploads
  - `file-storage-list-files-dev` - List user's files
  - `file-storage-download-file-dev` - Generate download URLs
  - `file-storage-delete-file-dev` - Delete files
  - `file-storage-share-file-dev` - Create share links
  - `file-storage-mcp-handler-dev` - MCP protocol (resources/list, resources/read)
  - `file-storage-chat-handler-dev` - AI summarization via Bedrock
- API Gateway: `file-storage-api-dev`
- IAM Role: `file-storage-lambda-role-dev` (with Bedrock permissions)

**API Endpoints**:
- `POST /files` - Upload file
- `GET /files` - List files
- `GET /files/{fileId}` - Download file
- `DELETE /files/{fileId}` - Delete file
- `POST /files/{fileId}/share` - Share file
- `POST /mcp` - MCP protocol handler (resources/list, resources/read)
- `POST /chat` - AI file summarization (Claude 3.5 Haiku via Bedrock)

**Key Outputs**:
- `ApiEndpoint`: API Gateway URL (e.g., `https://{api-id}.execute-api.us-west-2.amazonaws.com/dev`)

### 4. Monitoring Stack (`file-storage-monitoring-dev`)
**Purpose**: CloudWatch monitoring and alerting
**Template**: `infrastructure/cloudformation/monitoring.yml`

**Resources Created**:
- SNS Topic: `file-storage-alarms-dev`
- CloudWatch Alarms for all Lambda functions
- CloudWatch Dashboard: `file-storage-dashboard-dev`

**Key Outputs**:
- `DashboardURL`: CloudWatch Dashboard URL
- `AlarmTopicArn`: SNS Topic ARN for notifications

### 5. Frontend Stack (`production-frontend-stack`)
**Purpose**: Static website hosting
**Template**: `infrastructure/cloudformation/frontend.yml`

**Resources Created**:
- S3 Bucket: Private bucket for hosting
- CloudFront Distribution: CDN for the frontend

**Key Outputs**:
- `CloudFrontURL`: CloudFront distribution URL
- `BucketName`: S3 bucket name for hosting

## Prerequisites

### AWS Account Setup
- AWS CLI configured with appropriate credentials
- Sufficient IAM permissions for CloudFormation, Lambda, S3, DynamoDB, API Gateway, Cognito, and Bedrock

### AWS Bedrock Access (Required for AI Features)
1. Navigate to AWS Console → Bedrock → Model Access
2. Submit Anthropic use case details form
3. Wait for approval (~10-15 minutes, usually instant)
4. Verify Claude 3.5 Haiku model is enabled

**Use Case Form Example:**
- **Category**: Education/Research
- **Description**: Document storage system for university capstone project. Uses Claude Haiku to generate summaries of uploaded documents (PDFs, text files) for quick content understanding.
- **Expected Usage**: Low volume, educational testing (~100 API calls/month)

### Lambda Packaging
Lambda functions must be packaged with dependencies before deployment:

```bash
# Package all Lambda functions
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name dev-infrastructure-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`LambdaCodeBucketName`].OutputValue' \
  --output text \
  --region us-west-2)

./scripts/package-lambdas.sh $BUCKET_NAME dev
```

## Deployment Instructions

### Automatic Deployment (Recommended)
The infrastructure is automatically deployed via GitHub Actions when changes are pushed to the `main` branch in the `infrastructure/` directory.

**Prerequisites:**
- AWS credentials configured as GitHub Secrets:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`

### Manual Deployment
If you need to deploy manually, use the following commands in order:

```bash
# 1. Deploy Infrastructure (S3, DynamoDB)
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/infrastructure.yml \
  --stack-name dev-infrastructure-stack \
  --parameter-overrides Environment=dev

# 2. Deploy Authentication (Cognito)
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/auth.yml \
  --stack-name dev-auth-stack \
  --parameter-overrides Environment=dev

# 3. Deploy Backend (Lambda, API Gateway)
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/backend.yml \
  --stack-name production-backend-stack \
  --parameter-overrides Environment=dev \
  --capabilities CAPABILITY_NAMED_IAM

# 4. Deploy Monitoring (CloudWatch)
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/monitoring.yml \
  --stack-name file-storage-monitoring-dev \
  --parameter-overrides Environment=dev AlarmEmail=your-email@example.com

# 5. Deploy Frontend (S3, CloudFront)
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/frontend.yml \
  --stack-name production-frontend-stack
```

## Important URLs and IDs

After deployment, you'll need these values for frontend configuration:

### API Gateway
- **API URL**: Check the `ApiEndpoint` output from `production-backend-stack`
- **Example**: `https://abc123def4.execute-api.us-west-2.amazonaws.com/dev`

### Authentication (for frontend)
- **User Pool ID**: Check the `UserPoolId` output from `dev-auth-stack`
- **User Pool Client ID**: Check the `UserPoolClientId` output from `dev-auth-stack`
- **Identity Pool ID**: Check the `IdentityPoolId` output from `dev-auth-stack`

### Frontend
- **CloudFront URL**: Check the `CloudFrontURL` output from `production-frontend-stack`

## Testing the Deployment

### Test MCP Endpoints

**1. Test resources/list (List all files)**

```bash
API_URL=$(aws cloudformation describe-stacks \
  --stack-name production-backend-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text \
  --region us-west-2)

curl -X POST ${API_URL}/mcp \
  -H "Content-Type: application/json" \
  -d '{"action": "resources/list", "userId": "test-user"}'

# Expected response:
# {"resources": [{"id": "...", "name": "...", "uri": "s3://...", "mimeType": "...", "size": 0}]}
```

**2. Test resources/read (Read file content)**

```bash
curl -X POST ${API_URL}/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "action": "resources/read",
    "resource_id": "YOUR_FILE_ID",
    "userId": "test-user"
  }'

# Expected response:
# {"content": "file text content...", "fileName": "...", "mimeType": "..."}
```

### Test AI Summarization

**Generate AI summary of a file**

```bash
curl -X POST ${API_URL}/chat \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "YOUR_FILE_ID",
    "userId": "test-user"
  }'

# Expected response:
# {
#   "summary": "AI-generated summary here...",
#   "fileName": "...",
#   "contentLength": 1234,
#   "model": "claude-3.5-haiku-bedrock"
# }
```

**Upload a test file for summarization:**

```bash
# Create test document
echo "This is a test document with multiple paragraphs for AI summarization testing." > test.txt

# Upload to S3 (requires file metadata in DynamoDB first)
# Use the upload_file Lambda function through API Gateway
```

## Environment Configuration

All stacks are currently configured for the `dev` environment. To deploy to production:

1. Change the `Environment` parameter from `dev` to `prod` in all deployment commands
2. Update stack names to use `prod` instead of `dev`
3. Update the alarm email address in the monitoring stack

## Troubleshooting

### Common Issues
1. **Stack deployment fails**: Check AWS CloudFormation console for detailed error messages
2. **Lambda functions not working**: Verify IAM permissions and environment variables
3. **API Gateway not accessible**: Check CORS configuration and Lambda permissions
4. **Monitoring alarms not working**: Verify SNS topic subscription and email confirmation

### Useful Commands
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name <stack-name>

# View stack outputs
aws cloudformation describe-stacks --stack-name <stack-name> --query 'Stacks[0].Outputs'

# Delete a stack (if needed)
aws cloudformation delete-stack --stack-name <stack-name>
```

## Cost Estimates (Dev Environment)

### Monthly Costs (Approximate)

| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 1M invocations, 512MB avg | $0.50 |
| **API Gateway** | 1M requests | $3.50 |
| **DynamoDB** | Pay-per-request, 1M reads | $0.25 |
| **S3** | 10GB storage, 1GB transfer | $0.35 |
| **CloudWatch** | Logs, dashboard, 9 alarms | $5.00 |
| **Bedrock (Claude Haiku)** | 100 summarizations (~200K tokens) | $1.00 |
| **Cognito** | 1000 active users | Free tier |
| **CloudFront** | 10GB data transfer | Free tier |

**Total Estimated Cost:** ~$10-12/month

### Production Cost Optimizations
- Use Reserved Capacity for DynamoDB if traffic is predictable
- Enable S3 Intelligent-Tiering for infrequently accessed files
- Use CloudFront caching to reduce origin requests
- Monitor Bedrock usage to stay within budget

### Free Tier Benefits (First 12 Months)
- Lambda: 1M requests/month free
- API Gateway: 1M requests/month free
- S3: 5GB storage free
- DynamoDB: 25GB storage + 200M requests free
- CloudWatch: 10 custom metrics free

**First-year cost can be as low as $2-3/month within free tier limits.**

## Next Steps

1. **Frontend Integration**: Update `frontend/src/aws-exports.ts` with the actual values from stack outputs
2. **Lambda Implementation**: Replace placeholder Lambda code with actual business logic
3. **Authentication**: Integrate Cognito authentication in the frontend
4. **Testing**: Test all API endpoints and file operations
5. **Production Deployment**: Deploy to production environment when ready

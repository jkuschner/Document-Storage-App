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
- 5 Lambda Functions:
  - `file-storage-upload-file-dev`
  - `file-storage-list-files-dev`
  - `file-storage-download-file-dev`
  - `file-storage-delete-file-dev`
  - `file-storage-share-file-dev`
- API Gateway: `file-storage-api-dev`
- IAM Role: `file-storage-lambda-role-dev`

**API Endpoints**:
- `POST /files` - Upload file
- `GET /files` - List files
- `GET /files/{fileId}` - Download file
- `DELETE /files/{fileId}` - Delete file
- `POST /files/{fileId}/share` - Share file

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

## Deployment Instructions

### Automatic Deployment (Recommended)
The infrastructure is automatically deployed via GitHub Actions when changes are pushed to the `main` branch in the `infrastructure/` directory.

**Prerequisites**:
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

## Next Steps

1. **Frontend Integration**: Update `frontend/src/aws-exports.ts` with the actual values from stack outputs
2. **Lambda Implementation**: Replace placeholder Lambda code with actual business logic
3. **Authentication**: Integrate Cognito authentication in the frontend
4. **Testing**: Test all API endpoints and file operations
5. **Production Deployment**: Deploy to production environment when ready

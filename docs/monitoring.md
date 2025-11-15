# Monitoring Guide

## Dashboard
**Name:** `file-storage-dashboard-dev`  
**Link:** https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=file-storage-dashboard-dev

**Metrics:**
- Lambda: Invocations, Errors, Duration (7 functions)
- API Gateway: Requests, 4XX/5XX errors, Latency

## Alarms

**Lambda Errors (7):** Threshold 5 errors / 5min (1 error / 5min for MCP functions)
- `file-storage-upload-lambda-errors-dev`
- `file-storage-list-lambda-errors-dev`
- `file-storage-download-lambda-errors-dev`
- `file-storage-delete-lambda-errors-dev`
- `file-storage-share-lambda-errors-dev`
- `file-storage-mcp-handler-lambda-errors-dev`
- `file-storage-chat-handler-lambda-errors-dev`

**API Gateway (2):**
- `file-storage-api-5xx-errors-dev` - 10 errors / 5min
- `file-storage-api-high-latency-dev` - 2000ms average / 10min

**All alarms notify:** SNS topic `file-storage-alarms-dev`

## Subscribe to Alerts
```bash
# Get SNS topic ARN
aws sns list-topics --region us-west-2 | grep file-storage-alarms

# Subscribe to notifications
aws sns subscribe \
  --topic-arn  \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --region us-west-2
```

Confirm via email link.

## CloudWatch Logs

**Log Groups:**
- `/aws/lambda/file-storage-dev-backend-upload-file`
- `/aws/lambda/file-storage-dev-backend-list-files`
- `/aws/lambda/file-storage-dev-backend-download-file`
- `/aws/lambda/file-storage-dev-backend-delete-file`
- `/aws/lambda/file-storage-dev-backend-share-file`
- `/aws/lambda/file-storage-dev-backend-mcp-handler`
- `/aws/lambda/file-storage-dev-backend-chat-handler`

**Tail logs:**
```bash
aws logs tail /aws/lambda/file-storage-dev-backend- --follow --region us-west-2
```

## Troubleshooting

### Lambda Errors
1. Check logs: `aws logs tail /aws/lambda/file-storage-dev-backend-<function-name> --follow`
2. Common errors:
   - `AccessDeniedException` → IAM permissions
   - `ResourceNotFoundException` → Missing DynamoDB/S3 resource
   - `Timeout` → Function too slow, check duration metrics
3. Verify env vars: `aws lambda get-function-configuration --function-name <function-name>`

### API 5XX Errors
1. Check Lambda error alarms (5XX = Lambda failure)
2. Test endpoint: `curl <API_GATEWAY_URL>/files?userId=test-user`
3. Review Lambda logs for the failing function

### Authentication Errors

**Symptoms:**
- API returning 401 Unauthorized
- Users unable to access endpoints despite being logged in

**Diagnosis:**

1. **Check API Gateway 4XX errors:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 4XXError \
  --dimensions Name=ApiName,Value=file-storage-api-dev \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

2. **Filter CloudWatch logs for auth failures:**
```bash
aws logs filter-log-events \
  --log-group-name API-Gateway-Execution-Logs_<API-ID>/dev \
  --filter-pattern "UnauthorizedException" \
  --start-time $(date -d '1 hour ago' +%s)000
```

3. **Verify token validity:**
```bash
# Decode token to check expiration (requires jq)
echo $TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq .exp

# Compare to current time
date +%s
```

**Common Causes:**
- Expired token (tokens valid for 1 hour)
- Invalid token format (missing "Bearer " prefix)
- Wrong User Pool (token from different Cognito pool)
- Client not configured with correct auth flows

### High Latency
1. Check Lambda duration in dashboard
2. Review slow operations in logs (DynamoDB queries, S3)
3. Consider increasing Lambda memory or adding DynamoDB indexes

## Quick Commands
```bash
# Check alarm status
aws cloudwatch describe-alarms --alarm-name-prefix "file-storage" --region us-west-2

# View dashboard
aws cloudwatch get-dashboard --dashboard-name file-storage-dashboard-dev --region us-west-2

# Test API (get API URL from stack outputs)
export API_URL=$(aws cloudformation describe-stacks \
  --stack-name file-storage-dev-backend \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)
curl $API_URL/files?userId=test-user

# Search logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/file-storage-dev-backend-upload-file \
  --filter-pattern "ERROR" \
  --region us-west-2
```

## Cost Estimate
- Dashboard: $3/month
- Alarms (9): $0.90/month
- Logs: ~$0.50/GB ingested
- **Total dev environment:** ~$5-10/month

---

**Stack:** `infrastructure/cloudformation/monitoring.yml`  
**Last Updated:** November 3, 2025
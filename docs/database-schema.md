# DynamoDB Schema

## Files Table (files-dev)

**Primary Key:**
- PK: `userId` (String)
- SK: `fileId` (String)

**Attributes (Currently Implemented):**
- fileName (String) - Original file name
- s3Key (String) - Full S3 object path
- contentType (String) - MIME type (e.g., image/png)
- uploadDate (String) - ISO 8601 timestamp
- status (String) - Upload status: "pending" or "complete"

**Attributes (Future Enhancement):**
- fileSize (Number) - Size in bytes
- lastModified (String) - ISO 8601 timestamp
- sharedWith (List) - Array of userIds with access
- folderPath (String) - Virtual folder path (e.g., /docs/work)
- tags (List) - User-defined tags

**GSI: fileId-index**
- PK: fileId
- Projection: ALL
- Use case: Direct file lookup for sharing (without knowing userId)

**Access Patterns:**
1. Get all user files: Query by userId
2. Get specific file: Query userId + fileId
3. Lookup by fileId: Query fileId-index (used for shared file access)

**Billing:** PAY_PER_REQUEST

---

## SharedLinks Table (SharedLinksTable-dev)

**Primary Key:**
- PK: `shareToken` (String) - UUID v4

**Attributes (Currently Implemented):**
- fileId (String) - Reference to file being shared
- userId (String) - User who created the share link
- createdAt (String) - ISO 8601 timestamp
- expiresAt (Number) - Unix epoch timestamp (TTL enabled)

**Attributes (Future Enhancement):**
- accessCount (Number) - Number of times link was accessed
- maxAccess (Number) - Maximum allowed accesses (null = unlimited)

**Time-to-Live (TTL):**
- Enabled on `expiresAt` attribute
- DynamoDB automatically deletes expired share links

**Access Patterns:**
1. Get shared file info: Get by shareToken
2. Verify link not expired: Check expiresAt > current time
3. Track usage: Increment accessCount (future)

**Billing:** PAY_PER_REQUEST

---

## Users Table (Not Implemented - Future)

**Primary Key:**
- PK: `userId` (String)

**Attributes:**
- email (String)
- storageQuota (Number) - Bytes
- storageUsed (Number) - Bytes
- createdAt (Number) - Unix timestamp

**Note:** User authentication currently handled entirely by Cognito. This table would be added if we need additional user profile data beyond what Cognito provides.

---

## Design Notes

**Schema Validation:** Last validated November 6, 2025 - Compatible with all Lambda functions 

**Why Separate Tables:**
- Files table: High read/write volume, user-specific queries
- SharedLinks table: Different access patterns, needs TTL for expiration
- Users table: Low volume, simple lookups (not yet needed)

**DynamoDB Best Practices Applied:**
- Pay-per-request billing (unpredictable traffic patterns)
- Composite keys for efficient user-based queries
- GSI for file sharing without scanning entire table
- TTL for automatic cleanup of expired shares
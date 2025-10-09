# DynamoDB Schema

## Files Table

**Primary Key:**
- PK: `userId` (String)
- SK: `fileId` (String)

**Attributes:**
- fileName (String)
- s3Key (String) - path in S3
- fileSize (Number) - bytes
- contentType (String) - MIME type
- uploadDate (Number) - timestamp
- sharedWith (List) - array of userIds
- folderPath (String) - optional

**GSI: fileId-index**
- PK: fileId
- Use case: Direct file lookup for sharing

**Access Patterns:**
1. Get all user files: Query by userId
2. Get specific file: Query userId + fileId
3. Lookup by fileId: Query fileId-index

---

## Users Table (Optional)

**Primary Key:**
- PK: `userId` (String)

**Attributes:**
- email (String)
- storageQuota (Number)
- storageUsed (Number)
- createdAt (Number)

---

## SharedLinks Table

**Primary Key:**
- PK: `shareToken` (String)

**Attributes:**
- fileId (String)
- ownerId (String)
- expiresAt (Number) - TTL enabled
- createdAt (Number)

**Access:** Get by shareToken → retrieve fileId
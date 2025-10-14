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
                    │   (Auth)     │◄──┤                  │
                    └──────────────┘   └──────────────────┘
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
#!/bin/bash
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./package-lambdas.sh <s3-bucket-name> <environment>"
    exit 1
fi

BUCKET_NAME="$1"
ENVIRONMENT="$2"
FUNCTIONS_DIR="backend/lambda_functions"
BUILD_DIR="build/lambda-packages"
FUNCTIONS=("upload_file" "list_files" "download_file" "delete_file" "share_file" "shared_link" "mcp_handler" "chat_handler")

echo "Packaging Lambda functions for deployment.."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

for FUNCTION in "${FUNCTIONS[@]}"; do
    echo "Processing $FUNCTION..."
    FUNCTION_DIR="$FUNCTIONS_DIR/$FUNCTION"
    TEMP_DIR="$BUILD_DIR/$FUNCTION"
    mkdir -p "$TEMP_DIR"
    
    if [ ! -f "$FUNCTION_DIR/handler.py" ]; then
        echo "   Warning: $FUNCTION_DIR/handler.py not found, skipping..."
        continue
    fi
    cp "$FUNCTION_DIR/handler.py" "$TEMP_DIR/"
    
    if [ -f "$FUNCTION_DIR/requirements.txt" ] && [ -s "$FUNCTION_DIR/requirements.txt" ]; then
        echo "   Installing dependencies..."
        pip install -r "$FUNCTION_DIR/requirements.txt" -t "$TEMP_DIR/" --quiet --upgrade
    fi
    
    cd "$TEMP_DIR"
    zip -r "../$FUNCTION.zip" . -q
    cd - > /dev/null
    
    S3_KEY="lambda-functions/$FUNCTION/$ENVIRONMENT/$FUNCTION.zip"
    aws s3 cp "$BUILD_DIR/$FUNCTION.zip" "s3://$BUCKET_NAME/$S3_KEY" --quiet
    echo "   $FUNCTION deployed to s3://$BUCKET_NAME/$S3_KEY"
done

echo ""
echo "All Lambda functions packaged and uploaded!great"

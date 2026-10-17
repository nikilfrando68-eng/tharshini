#!/usr/bin/env bash
# AWS SAM Deployment Script for Campus Club Management Portal
set -e

STACK_NAME=${1:-"campus-club-portal"}
REGION=${2:-"us-east-1"}

echo "=========================================================="
echo " Campus Club Management Portal - AWS Serverless Deployment"
echo "=========================================================="

command -v sam >/dev/null 2>&1 || { echo >&2 "Error: AWS SAM CLI is required. Aborting."; exit 1; }
command -v aws >/dev/null 2>&1 || { echo >&2 "Error: AWS CLI is required. Aborting."; exit 1; }

echo "[1/4] Building AWS SAM application..."
sam build --template-file backend/template.yaml

echo "[2/4] Deploying CloudFormation Stack ($STACK_NAME)..."
sam deploy \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --resolve-s3 \
    --no-confirm-changeset

echo "[3/4] Retrieving Stack Outputs..."
FRONTEND_BUCKET=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='FrontendS3Bucket'].OutputValue" --output text)
CLOUDFRONT_URL=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue" --output text)

echo " Frontend S3 Bucket: $FRONTEND_BUCKET"
echo " CloudFront URL:     $CLOUDFRONT_URL"

echo "[4/4] Syncing Frontend Assets to Amazon S3..."
aws s3 sync frontend/ "s3://$FRONTEND_BUCKET" --delete

echo "=========================================================="
echo " Deployment Complete!"
echo " Portal URL: $CLOUDFRONT_URL"
echo "=========================================================="

# AWS SAM Deployment Script for Campus Club Management Portal
# Automates SAM Build, Deploy, S3 Frontend Upload, and CloudFront Invalidation

param (
    [string]$StackName = "campus-club-portal",
    [string]$Region = "us-east-1"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Campus Club Management Portal - AWS Serverless Deployment" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check SAM CLI
if (-not (Get-Command sam -ErrorAction SilentlyContinue)) {
    Write-Error "AWS SAM CLI is required. Please install SAM CLI and ensure AWS credentials are configured."
    exit 1
}

Write-Host "[1/4] Building AWS SAM application..." -ForegroundColor Yellow
sam build --template-file backend/template.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Error "SAM build failed."
    exit 1
}

Write-Host "[2/4] Deploying CloudFormation Stack ($StackName)..." -ForegroundColor Yellow
sam deploy `
    --stack-name $StackName `
    --region $Region `
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND `
    --resolve-s3 `
    --no-confirm-changeset

if ($LASTEXITCODE -ne 0) {
    Write-Error "SAM deployment failed."
    exit 1
}

Write-Host "[3/4] Retrieving Stack Outputs..." -ForegroundColor Yellow
$outputs = aws cloudformation describe-stacks --stack-name $StackName --region $Region --query "Stacks[0].Outputs" --output json | ConvertFrom-Json

$frontendBucket = ($outputs | Where-Object { $_.OutputKey -eq "FrontendS3Bucket" }).OutputValue
$cloudFrontUrl = ($outputs | Where-Object { $_.OutputKey -eq "CloudFrontUrl" }).OutputValue
$apiEndpoint = ($outputs | Where-Object { $_.OutputKey -eq "ApiEndpoint" }).OutputValue

Write-Host " API Gateway Endpoint: $apiEndpoint" -ForegroundColor Green
Write-Host " CloudFront URL:        $cloudFrontUrl" -ForegroundColor Green
Write-Host " Frontend S3 Bucket:    $frontendBucket" -ForegroundColor Green

Write-Host "[4/4] Syncing Frontend Assets to Amazon S3..." -ForegroundColor Yellow
aws s3 sync frontend/ "s3://$frontendBucket" --delete

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host " Open your portal at: $cloudFrontUrl" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

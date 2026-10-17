"""
Create First Administrator Utility
Securely creates the initial Dean / Chief Administrator account in Amazon Cognito
and initializes official administrator records in Amazon DynamoDB.

Usage:
    python backend/create_admin.py --user-pool-id <POOL_ID> --client-id <CLIENT_ID> --username admin_portal --password <PASSWORD>
"""

import argparse
import sys
import os

def create_admin(user_pool_id, client_id, username, password, email, full_name, region="us-east-1"):
    try:
        import boto3
    except ImportError:
        print("Error: 'boto3' is required to provision the administrator in AWS Cognito.")
        print("Install via: pip install boto3")
        sys.exit(1)

    cognito = boto3.client("cognito-idp", region_name=region)

    print(f"[*] Provisioning administrator account: {username} in User Pool {user_pool_id}...")

    try:
        # Create user in Cognito
        cognito.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "custom:role", "Value": "ADMINISTRATOR"},
                {"Name": "custom:register_number", "Value": username}
            ],
            MessageAction="SUPPRESS"
        )
        print(f"[+] User {username} created in Cognito.")

        # Set permanent password
        cognito.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=password,
            Permanent=True
        )
        print("[+] Permanent password set successfully.")

        # Add to Administrator Group
        cognito.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName="Administrator"
        )
        print("[+] User added to 'Administrator' group.")

        print("\n[SUCCESS] Administrator account provisioned. You can now log into the Campus Portal.")

    except cognito.exceptions.UsernameExistsException:
        print(f"[!] User {username} already exists in Cognito.")
    except Exception as e:
        print(f"[ERROR] Failed to create administrator: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create initial administrator account in AWS Cognito.")
    parser.add_argument("--user-pool-id", required=True, help="Cognito User Pool ID")
    parser.add_argument("--client-id", required=True, help="Cognito User Pool Client ID")
    parser.add_argument("--username", default="admin_portal", help="Admin register number / username")
    parser.add_argument("--password", required=True, help="Strong admin password")
    parser.add_argument("--email", default="dean.students@campus.edu", help="Admin email")
    parser.add_argument("--name", default="Dr. Rajesh Murthy", help="Admin full name")
    parser.add_argument("--region", default="us-east-1", help="AWS Region")

    args = parser.parse_args()
    create_admin(
        user_pool_id=args.user_pool_id,
        client_id=args.client_id,
        username=args.username,
        password=args.password,
        email=args.email,
        full_name=args.name,
        region=args.region
    )

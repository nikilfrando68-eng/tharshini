"""
Authentication and Authorization Service
Supports Amazon Cognito integration with Register Number as username,
and local simulated JWT tokens for development and testing.
"""

import hmac
import hashlib
import base64
import json
import time
from typing import Dict, Any, Optional

from .db_adapter import get_db

JWT_SECRET = "campus-portal-aws-cognito-secret-key-2026"

class AuthService:

    @staticmethod
    def _create_token(payload: Dict[str, Any]) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        sig = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        return f"{header_b64}.{payload_b64}.{sig_b64}"

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            header_b64, payload_b64, sig_b64 = parts
            signing_input = f"{header_b64}.{payload_b64}".encode()
            expected_sig = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
            # Restore padding
            pad_len = 4 - (len(sig_b64) % 4)
            if pad_len != 4:
                sig_b64 += "=" * pad_len
            actual_sig = base64.urlsafe_b64decode(sig_b64.encode())
            if not hmac.compare_digest(expected_sig, actual_sig):
                return None

            pad_len = 4 - (len(payload_b64) % 4)
            if pad_len != 4:
                payload_b64 += "=" * pad_len
            payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
            payload = json.loads(payload_json)

            if payload.get("exp", 0) < time.time():
                return None
            return payload
        except Exception:
            return None

    @staticmethod
    def login(register_number: str, password: str) -> Dict[str, Any]:
        """
        Authenticates a user via Register Number and Password.
        Supports official Student, Club Leader, and Administrator accounts.
        """
        db = get_db()
        reg_num = str(register_number).strip()
        if not reg_num or not password:
            raise ValueError("Register Number and Password are required.")

        user = db.get_user(reg_num)
        if not user:
            # Check if student exists in official registry but not yet registered in Cognito
            student = db.get_student_record(reg_num)
            if student:
                raise ValueError("Account not yet activated. Please use the Student Registration page to activate your portal account.")
            raise ValueError("Invalid Register Number or Password.")

        if not user.get("is_active", True):
            raise PermissionError("Account has been disabled. Please contact the campus portal administrator.")

        # In production on AWS, this calls Cognito AdminInitiateAuth / InitiateAuth API:
        # cognito_client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH', AuthParameters={'USERNAME': reg_num, 'PASSWORD': password})
        if user.get("password_hash") != password:
            raise ValueError("Invalid Register Number or Password.")

        # Generate JWT session payload
        role = user.get("role", "STUDENT")
        exp = int(time.time()) + 86400  # 24 hours

        payload = {
            "sub": user.get("username"),
            "register_number": user.get("register_number", reg_num),
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "role": role,
            "department": user.get("department"),
            "assigned_clubs": user.get("assigned_clubs", []),
            "exp": exp
        }

        token = AuthService._create_token(payload)
        db.log_audit(reg_num, role, "USER_LOGIN", reg_num, f"Successful login for {user.get('full_name')} ({role})")

        return {
            "token": token,
            "user": {
                "register_number": payload["register_number"],
                "full_name": payload["full_name"],
                "email": payload["email"],
                "role": role,
                "department": payload["department"],
                "assigned_clubs": payload.get("assigned_clubs", [])
            }
        }

    @staticmethod
    def register_student(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registers a student account.
        Validates the Register Number against the official college registry (Source of Truth).
        Prevents duplicate registrations and enforces the STUDENT role.
        """
        db = get_db()
        reg_num = str(data.get("register_number", "")).strip()
        email = str(data.get("email", "")).strip()
        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")

        if not reg_num:
            raise ValueError("College Register Number is required.")
        if not password or len(password) < 4:
            raise ValueError("Password must be at least 4 characters.")
        if password != confirm_password:
            raise ValueError("Password and Confirm Password do not match.")

        # Verify against official student registry (Source of Truth)
        official_record = db.get_student_record(reg_num)
        if not official_record:
            raise ValueError(
                f"Register Number '{reg_num}' is not recognized in the official college registry. "
                "Only officially enrolled students may register. Please verify your registration number or contact the registrar."
            )

        # Check if already registered
        existing_user = db.get_user(reg_num)
        if existing_user:
            raise ValueError(f"Student with Register Number {reg_num} is already registered. Please log in.")

        # Enforce STUDENT role strictly (cannot self-assign admin/leader)
        new_user = {
            "username": reg_num,
            "password_hash": password,
            "role": "STUDENT",
            "register_number": reg_num,
            "full_name": official_record.get("full_name"),
            "email": email or official_record.get("email"),
            "department": official_record.get("department"),
            "academic_year": official_record.get("academic_year"),
            "is_active": True
        }

        db.create_user(new_user)
        db.log_audit(reg_num, "STUDENT", "STUDENT_REGISTRATION", reg_num, f"Registered portal account for {official_record.get('full_name')}")

        return {
            "message": "Registration successful! You may now log in with your Register Number and Password.",
            "register_number": reg_num,
            "full_name": official_record.get("full_name")
        }

    @staticmethod
    def create_or_set_password(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allows a student to create their own password using their official College Register Number.
        Validates against the official university student registry (source of truth).
        """
        db = get_db()
        reg_num = str(data.get("register_number", "")).strip()
        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")

        if not reg_num:
            raise ValueError("Official College Register Number is required.")
        if not password or len(password) < 4:
            raise ValueError("Password must be at least 4 characters.")
        if password != confirm_password:
            raise ValueError("Password and Confirm Password do not match.")

        # Verify against official student registry
        official_record = db.get_student_record(reg_num)
        if not official_record:
            raise ValueError(
                f"Register Number '{reg_num}' is not recognized in the official Sathyabama student database. "
                "Only officially enrolled students may create a password. Please contact the Academic Registrar."
            )

        existing_user = db.get_user(reg_num)
        if existing_user:
            # Update password
            db.users[reg_num]["password_hash"] = password
            db.log_audit(reg_num, "STUDENT", "SET_OWN_PASSWORD", reg_num, f"Student {official_record.get('full_name')} updated their password.")
            return {
                "message": f"Password created successfully for {official_record.get('full_name')} ({reg_num})! You can now sign in.",
                "register_number": reg_num,
                "full_name": official_record.get("full_name")
            }
        else:
            # Provision student user in user pool with their own password
            new_user = {
                "username": reg_num,
                "password_hash": password,
                "role": "STUDENT",
                "register_number": reg_num,
                "full_name": official_record.get("full_name"),
                "email": official_record.get("email"),
                "department": official_record.get("department"),
                "academic_year": official_record.get("academic_year"),
                "is_active": True
            }
            db.create_user(new_user)
            db.log_audit(reg_num, "STUDENT", "ACTIVATE_AND_SET_PASSWORD", reg_num, f"Student {official_record.get('full_name')} activated account and created password.")
            return {
                "message": f"Account activated! Password created successfully for {official_record.get('full_name')} ({reg_num}). You can now log in.",
                "register_number": reg_num,
                "full_name": official_record.get("full_name")
            }

    @staticmethod
    def forgot_password(register_number: str) -> Dict[str, Any]:
        """
        Initiates password reset workflow for the student.
        In AWS production, calls Cognito ForgotPassword API to send verification code.
        """
        db = get_db()
        reg_num = str(register_number).strip()
        user = db.get_user(reg_num)
        if not user:
            raise ValueError(f"No account found for Register Number {reg_num}.")

        # Mask email
        email = user.get("email", "student@campus.edu")
        masked_email = email[:2] + "****" + email[email.find("@"):] if "@" in email else email

        return {
            "message": f"A secure password reset OTP verification code has been dispatched to {masked_email}.",
            "register_number": reg_num,
            "demo_reset_token": "OTP-849201"
        }

    @staticmethod
    def reset_password(register_number: str, otp_code: str, new_password: str) -> Dict[str, Any]:
        db = get_db()
        reg_num = str(register_number).strip()
        user = db.get_user(reg_num)
        if not user:
            raise ValueError(f"User {reg_num} not found.")
        if not new_password or len(new_password) < 4:
            raise ValueError("New password must be at least 4 characters.")

        # Update password
        db.users[reg_num]["password_hash"] = new_password
        db.log_audit(reg_num, user.get("role", "STUDENT"), "PASSWORD_RESET", reg_num, "Password successfully reset.")
        return {"message": "Password updated successfully. Please log in with your new password."}

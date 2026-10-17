"""
AWS Lambda Master Handler
Dispatches API Gateway proxy integration requests to appropriate services.
Implements CORS, security header validation, JWT role verification, and error formatting.
"""

import json
from typing import Dict, Any, Optional

from .auth_service import AuthService
from .club_service import ClubService
from .student_service import StudentService
from .application_service import ApplicationService
from .rule_service import RuleService
from .event_service import EventService
from .admin_service import AdminService

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}

def create_response(status_code: int, data: Any) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(data, default=str)
    }

def get_auth_user(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    headers = event.get("headers") or {}
    # Case-insensitive header check
    auth_header = None
    for k, v in headers.items():
        if k.lower() == "authorization":
            auth_header = v
            break

    if not auth_header:
        return None

    parts = auth_header.split(" ")
    token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else auth_header
    return AuthService.verify_token(token)

def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Main entry point for AWS Lambda / API Gateway.
    """
    http_method = event.get("httpMethod", "GET").upper()
    path = event.get("path", "").rstrip("/")
    # Support path resolution if base prefix e.g. /prod or /api
    if not path.startswith("/api"):
        path = f"/api{path}" if not path.startswith("/") else f"/api{path}"

    # Handle CORS preflight
    if http_method == "OPTIONS":
        return create_response(200, {"message": "CORS preflight OK"})

    # Parse JSON body
    body = {}
    raw_body = event.get("body")
    if raw_body:
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except Exception:
            return create_response(400, {"error": "Invalid JSON body payload."})

    query = event.get("queryStringParameters") or {}

    try:
        # ==========================================
        # PUBLIC AUTH ROUTES (No Token Required)
        # ==========================================
        if path == "/api/auth/login" and http_method == "POST":
            res = AuthService.login(body.get("register_number"), body.get("password"))
            return create_response(200, res)

        if path == "/api/auth/create-password" and http_method == "POST":
            res = AuthService.create_or_set_password(body)
            return create_response(200, res)

        if path == "/api/auth/register" and http_method == "POST":
            res = AuthService.register_student(body)
            return create_response(201, res)

        if path == "/api/auth/forgot-password" and http_method == "POST":
            res = AuthService.forgot_password(body.get("register_number"))
            return create_response(200, res)

        if path == "/api/auth/reset-password" and http_method == "POST":
            res = AuthService.reset_password(
                body.get("register_number"),
                body.get("otp_code"),
                body.get("new_password")
            )
            return create_response(200, res)

        # Public club discovery
        if path == "/api/clubs" and http_method == "GET":
            category = query.get("category")
            search = query.get("search")
            clubs = ClubService.list_clubs(category, search)
            return create_response(200, {"clubs": clubs})

        if path.startswith("/api/clubs/") and http_method == "GET":
            club_id = path.split("/api/clubs/")[1]
            club = ClubService.get_club(club_id)
            if not club:
                return create_response(404, {"error": f"Club {club_id} not found."})
            return create_response(200, {"club": club})

        # Public event listing
        if path == "/api/events" and http_method == "GET":
            club_id = query.get("club_id")
            events = EventService.list_events(club_id)
            return create_response(200, {"events": events})

        # ==========================================
        # PROTECTED ROUTES (Token Required)
        # ==========================================
        user = get_auth_user(event)
        if not user:
            return create_response(401, {"error": "Unauthorized: Valid Bearer Token required."})

        # --- Student Endpoints ---
        if path == "/api/student/profile" and http_method == "GET":
            reg_num = user.get("register_number")
            profile = StudentService.get_profile(reg_num, user)
            return create_response(200, {"profile": profile})

        if path == "/api/student/dashboard" and http_method == "GET":
            reg_num = user.get("register_number")
            summary = StudentService.get_dashboard_summary(reg_num, user)
            return create_response(200, summary)

        if path.startswith("/api/student/eligibility/") and http_method == "GET":
            club_id = path.split("/api/student/eligibility/")[1]
            reg_num = user.get("register_number")
            result = StudentService.check_club_eligibility(reg_num, club_id, user)
            return create_response(200, result)

        if path == "/api/student/apply" and http_method == "POST":
            reg_num = user.get("register_number")
            club_id = body.get("club_id")
            app = ApplicationService.submit_application(reg_num, club_id, user)
            return create_response(201, {"message": "Application submitted successfully!", "application": app})

        if path == "/api/student/applications" and http_method == "GET":
            apps = ApplicationService.list_applications(user)
            return create_response(200, {"applications": apps})

        if path.startswith("/api/student/applications/") and path.endswith("/cancel") and http_method == "POST":
            app_id = path.split("/api/student/applications/")[1].replace("/cancel", "")
            cancelled = ApplicationService.cancel_application(app_id, user)
            return create_response(200, {"message": "Application cancelled successfully.", "application": cancelled})

        if path == "/api/student/memberships" and http_method == "GET":
            from .db_adapter import get_db
            db = get_db()
            mems = db.list_memberships(student_id=user.get("register_number"))
            return create_response(200, {"memberships": mems})

        # --- Event Registration & Creation ---
        if path.startswith("/api/events/") and path.endswith("/register") and http_method == "POST":
            event_id = path.split("/api/events/")[1].replace("/register", "")
            reg = EventService.register_student(event_id, user)
            return create_response(201, {"message": "Event registration confirmed!", "registration": reg})

        if path == "/api/events/my-registrations" and http_method == "GET":
            regs = EventService.list_my_registrations(user)
            return create_response(200, {"registrations": regs})

        if path == "/api/events" and http_method == "POST":
            created_evt = EventService.create_event(body, user)
            return create_response(201, {"message": "Event created successfully!", "event": created_evt})

        # --- Applications (Review & Leader/Admin Listing) ---
        if path == "/api/applications" and http_method == "GET":
            club_id = query.get("club_id")
            apps = ApplicationService.list_applications(user, club_id)
            return create_response(200, {"applications": apps})

        if path.startswith("/api/applications/") and path.endswith("/review") and http_method == "POST":
            app_id = path.split("/api/applications/")[1].replace("/review", "")
            updated = ApplicationService.review_application(
                app_id,
                body.get("status"),
                body.get("remarks", ""),
                user
            )
            return create_response(200, {"message": f"Application status updated to {body.get('status')}.", "application": updated})

        # --- Eligibility Rules (Admin) ---
        if path.startswith("/api/rules/") and path.endswith("/publish") and http_method == "POST":
            club_id = path.split("/api/rules/")[1].replace("/publish", "")
            published = RuleService.publish_new_rule(club_id, body, user)
            return create_response(201, {"message": f"Rule {published['version']} published successfully!", "rule": published})

        if path.startswith("/api/rules/") and http_method == "GET":
            club_id = path.split("/api/rules/")[1]
            active = RuleService.get_active_rule(club_id)
            history = RuleService.list_rule_history(club_id)
            return create_response(200, {"active_rule": active, "history": history})

        # --- Administrator Operations ---
        if path == "/api/admin/metrics" and http_method == "GET":
            metrics = AdminService.get_dashboard_metrics(user)
            return create_response(200, metrics)

        if path == "/api/admin/registry" and http_method == "GET":
            registry = AdminService.list_registry(user)
            return create_response(200, {"registry": registry})

        if path == "/api/admin/registry" and http_method == "POST":
            added = AdminService.add_student_record(body, user)
            return create_response(201, {"message": "Student added to official registry.", "student": added})

        if path.startswith("/api/admin/registry/") and http_method == "PUT":
            reg_num = path.split("/api/admin/registry/")[1]
            updated = AdminService.update_student_record(reg_num, body, user)
            return create_response(200, {"message": f"Official record for {reg_num} updated.", "student": updated})

        if path == "/api/admin/audit-logs" and http_method == "GET":
            limit = int(query.get("limit", 50))
            logs = AdminService.list_audit_logs(user, limit)
            return create_response(200, {"audit_logs": logs})

        if path == "/api/admin/export-report" and http_method == "GET":
            report = AdminService.export_report(user)
            return create_response(200, report)

        # Update Club (Admin)
        if path.startswith("/api/clubs/") and http_method == "PUT":
            saved = ClubService.save_club(body, user)
            return create_response(200, {"message": "Club updated successfully.", "club": saved})

        return create_response(404, {"error": f"API route not found: {http_method} {path}"})

    except ValueError as ve:
        return create_response(400, {"error": str(ve)})
    except KeyError as ke:
        return create_response(404, {"error": str(ke).strip('\"\'')})
    except PermissionError as pe:
        return create_response(403, {"error": str(pe)})
    except Exception as e:
        return create_response(500, {"error": f"Internal Server Error: {str(e)}"})

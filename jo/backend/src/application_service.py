"""
Application Service
Manages student club membership applications, server-side eligibility enforcement,
capacity limits, duplicate prevention, and club leader / admin review workflows.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .db_adapter import get_db
from .eligibility_engine import EligibilityEngine

class ApplicationService:

    @staticmethod
    def submit_application(register_number: str, club_id: str, requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submits a club application with STRICT backend eligibility verification.
        Never trusts client-side status.
        """
        # Security checks
        req_role = requesting_user.get("role")
        req_reg = requesting_user.get("register_number")
        if req_role != "STUDENT" or req_reg != register_number:
            raise PermissionError("Only the authenticated student can submit their own club application.")

        db = get_db()
        profile = db.get_student_record(register_number)
        if not profile:
            raise KeyError(f"Student record for Register Number {register_number} not found.")

        club = db.get_club(club_id)
        if not club:
            raise KeyError(f"Club '{club_id}' does not exist.")

        # Re-run automated eligibility verification strictly on backend
        active_rule = db.get_active_rule(club_id) or {}
        eval_result = EligibilityEngine.evaluate(profile, active_rule, club)

        if not eval_result["is_eligible"]:
            reasons = "; ".join(eval_result["failed_reasons"])
            raise ValueError(f"Application rejected: You do not satisfy the eligibility requirements for {club.get('name')}. Reasons: {reasons}")

        # Check club capacity
        if club.get("current_members_count", 0) >= club.get("capacity", 50):
            raise ValueError(f"Application rejected: {club.get('name')} is currently at full capacity ({club.get('capacity')} members).")

        # Prepare application record with immutable rule version snapshot
        app_data = {
            "student_id": register_number,
            "register_number": register_number,
            "student_name": profile.get("full_name"),
            "student_department": profile.get("department"),
            "academic_year": profile.get("academic_year"),
            "club_id": club_id,
            "club_name": club.get("name"),
            "rule_version": eval_result["rule_version"],
            "criteria_results": {c["criterion"]: {"passed": c["passed"], "actual": c["actual"]} for c in eval_result["criteria_breakdown"]},
            "evaluation_status": eval_result["status"]
        }

        created = db.create_application(app_data)
        db.log_audit(
            register_number,
            "STUDENT",
            "SUBMIT_APPLICATION",
            f"{club_id}:{created['application_id']}",
            f"Submitted application for {club.get('name')} under rule {eval_result['rule_version']}"
        )
        return created

    @staticmethod
    def list_applications(requesting_user: Dict[str, Any], club_id: Optional[str] = None) -> List[Dict[str, Any]]:
        db = get_db()
        role = requesting_user.get("role")
        reg_num = requesting_user.get("register_number")

        if role == "STUDENT":
            return db.list_applications(student_id=reg_num, club_id=club_id)

        if role == "CLUB_LEADER":
            assigned = requesting_user.get("assigned_clubs", [])
            if club_id and club_id not in assigned:
                raise PermissionError(f"Access denied: You are not assigned as leader for club '{club_id}'.")
            all_apps = db.list_applications(club_id=club_id)
            return [a for a in all_apps if a.get("club_id") in assigned]

        if role == "ADMINISTRATOR":
            return db.list_applications(club_id=club_id)

        return []

    @staticmethod
    def review_application(application_id: str, new_status: str, remarks: str, requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Approves or Rejects an application.
        Authorized roles: ADMINISTRATOR, or CLUB_LEADER for their assigned club.
        """
        role = requesting_user.get("role")
        reviewer_id = requesting_user.get("register_number") or requesting_user.get("sub", "ADMIN")

        if role not in ["ADMINISTRATOR", "CLUB_LEADER"]:
            raise PermissionError("Only club leaders and administrators can review membership applications.")

        if new_status not in ["APPROVED", "REJECTED"]:
            raise ValueError("Application review status must be either 'APPROVED' or 'REJECTED'.")

        db = get_db()
        app = db.get_application(application_id)
        if not app:
            raise KeyError(f"Application {application_id} not found.")

        # If Club Leader, verify assignment
        if role == "CLUB_LEADER":
            assigned = requesting_user.get("assigned_clubs", [])
            if app.get("club_id") not in assigned:
                raise PermissionError("Security violation: You can only review applications for clubs assigned to you.")

        updated = db.update_application_status(application_id, new_status, reviewer_id, remarks)
        db.log_audit(
            reviewer_id,
            role,
            f"REVIEW_APPLICATION_{new_status}",
            f"{app.get('club_id')}:{application_id}",
            f"Set application status to {new_status}. Remarks: {remarks}"
        )
        return updated

    @staticmethod
    def cancel_application(application_id: str, requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        reg_num = requesting_user.get("register_number")
        db = get_db()
        cancelled = db.cancel_application(application_id, reg_num)
        db.log_audit(
            reg_num,
            "STUDENT",
            "CANCEL_APPLICATION",
            application_id,
            "Student cancelled pending application."
        )
        return cancelled

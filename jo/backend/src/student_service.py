"""
Student Service
Handles student profiles, dashboard metrics, and automated eligibility evaluation queries.
Enforces security: Students cannot modify official scores or access other students' records.
"""

from typing import Dict, Any, List, Optional
from .db_adapter import get_db
from .eligibility_engine import EligibilityEngine

class StudentService:

    @staticmethod
    def get_profile(register_number: str, requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves official student profile from the registry.
        Enforces access control: Students can only access their own profile.
        """
        req_role = requesting_user.get("role")
        req_reg = requesting_user.get("register_number")

        if req_role == "STUDENT" and req_reg != register_number:
            raise PermissionError("Access denied: You are not authorized to view another student's profile.")

        db = get_db()
        record = db.get_student_record(register_number)
        if not record:
            raise KeyError(f"Student record for Register Number {register_number} not found.")

        # Return a copy to ensure immutability
        return dict(record)

    @staticmethod
    def get_dashboard_summary(register_number: str, requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        profile = StudentService.get_profile(register_number, requesting_user)
        db = get_db()

        # Memberships
        memberships = db.list_memberships(student_id=register_number)
        joined_club_ids = {m["club_id"] for m in memberships}

        # Applications
        applications = db.list_applications(student_id=register_number)
        pending_apps = [a for a in applications if a.get("status") == "PENDING_APPROVAL"]

        # Events
        all_events = db.list_events()
        registered_events = db.list_student_event_registrations(register_number)

        # Run eligibility across all clubs
        clubs = db.list_clubs()
        eligible_clubs_count = 0
        clubs_eligibility = []

        for club in clubs:
            cid = club.get("club_id")
            rule = db.get_active_rule(cid) or {}
            eval_res = EligibilityEngine.evaluate(profile, rule, club)

            # Determine composite status
            is_member = cid in joined_club_ids
            has_pending = any(a.get("club_id") == cid and a.get("status") == "PENDING_APPROVAL" for a in applications)

            if is_member:
                display_status = "Approved"
            elif has_pending:
                display_status = "Application Pending Approval"
            elif eval_res["status"] == "ELIGIBLE_TO_APPLY":
                display_status = "Eligible to Apply"
                eligible_clubs_count += 1
            elif eval_res["status"] == "PENDING_VERIFICATION":
                display_status = "Pending Verification"
            else:
                display_status = "Not Eligible"

            clubs_eligibility.append({
                "club_id": cid,
                "club_name": club.get("name"),
                "category": club.get("category"),
                "capacity": club.get("capacity"),
                "current_members_count": club.get("current_members_count"),
                "is_eligible": eval_res["is_eligible"],
                "eligibility_status": eval_res["status"],
                "display_status": display_status,
                "failed_reasons": eval_res["failed_reasons"],
                "rule_version": eval_res["rule_version"]
            })

        return {
            "profile": profile,
            "metrics": {
                "verified_cgpa": profile.get("cgpa"),
                "aptitude_score": profile.get("aptitude_score"),
                "programming_score": profile.get("programming_score"),
                "verification_status": profile.get("verification_status"),
                "total_eligible_clubs": eligible_clubs_count,
                "joined_clubs_count": len(memberships),
                "pending_applications_count": len(pending_apps),
                "registered_events_count": len(registered_events),
                "total_upcoming_events": len(all_events)
            },
            "memberships": memberships,
            "recent_applications": applications[:5],
            "clubs_eligibility": clubs_eligibility,
            "upcoming_events": all_events[:4]
        }

    @staticmethod
    def check_club_eligibility(register_number: str, club_id: str, requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs real-time automated eligibility evaluation for a specific club.
        """
        profile = StudentService.get_profile(register_number, requesting_user)
        db = get_db()
        club = db.get_club(club_id)
        if not club:
            raise KeyError(f"Club {club_id} not found.")

        rule = db.get_active_rule(club_id) or {}
        eval_result = EligibilityEngine.evaluate(profile, rule, club)

        # Check existing application / membership status
        apps = db.list_applications(student_id=register_number, club_id=club_id)
        memberships = db.list_memberships(student_id=register_number, club_id=club_id)

        user_app_status = None
        if memberships:
            user_app_status = "APPROVED"
        elif apps:
            user_app_status = apps[0].get("status")

        eval_result["user_application_status"] = user_app_status
        eval_result["club_capacity"] = club.get("capacity")
        eval_result["current_members_count"] = club.get("current_members_count")
        eval_result["capacity_full"] = (club.get("current_members_count", 0) >= club.get("capacity", 50))

        return eval_result

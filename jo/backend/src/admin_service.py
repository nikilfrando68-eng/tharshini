"""
Administrator Service
Manages college-wide portal analytics, student registry source of truth,
audit log reviews, and administrative reporting.
"""

from typing import Dict, Any, List
from .db_adapter import get_db

class AdminService:

    @staticmethod
    def _verify_admin(requesting_user: Dict[str, Any]):
        if requesting_user.get("role") != "ADMINISTRATOR":
            raise PermissionError("Access denied: Administrator privileges required.")

    @staticmethod
    def get_dashboard_metrics(requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        AdminService._verify_admin(requesting_user)
        db = get_db()

        students = db.list_all_students()
        clubs = db.list_clubs()
        applications = db.list_applications()
        memberships = db.list_memberships()
        events = db.list_events()
        audit_logs = db.list_audit_logs(limit=10)

        pending_verifications = [s for s in students if s.get("verification_status") == "PENDING_VERIFICATION"]
        verified_students = [s for s in students if s.get("verification_status") == "VERIFIED"]

        pending_apps = [a for a in applications if a.get("status") == "PENDING_APPROVAL"]
        approved_apps = [a for a in applications if a.get("status") == "APPROVED"]
        rejected_apps = [a for a in applications if a.get("status") == "REJECTED"]

        # Club capacity and fill stats
        club_stats = []
        for c in clubs:
            cap = c.get("capacity", 50)
            curr = c.get("current_members_count", 0)
            pct = round((curr / cap * 100), 1) if cap > 0 else 0
            club_stats.append({
                "club_id": c.get("club_id"),
                "name": c.get("name"),
                "category": c.get("category"),
                "leader_name": c.get("leader_name"),
                "capacity": cap,
                "current_members_count": curr,
                "fill_percentage": pct
            })

        return {
            "metrics": {
                "total_students": len(students),
                "total_clubs": len(clubs),
                "verified_students_count": len(verified_students),
                "pending_verifications_count": len(pending_verifications),
                "pending_applications_count": len(pending_apps),
                "approved_memberships_count": len(approved_apps),
                "rejected_applications_count": len(rejected_apps),
                "total_upcoming_events": len(events)
            },
            "club_stats": club_stats,
            "recent_applications": applications[:8],
            "recent_audit_logs": audit_logs,
            "pending_verification_students": pending_verifications
        }

    @staticmethod
    def list_registry(requesting_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        AdminService._verify_admin(requesting_user)
        db = get_db()
        return db.list_all_students()

    @staticmethod
    def update_student_record(register_number: str, updates: Dict[str, Any], requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        AdminService._verify_admin(requesting_user)
        db = get_db()
        updated = db.update_student_registry(register_number, updates)
        db.log_audit(
            requesting_user.get("register_number", "ADMIN"),
            "ADMINISTRATOR",
            "UPDATE_STUDENT_REGISTRY",
            register_number,
            f"Updated student record for {register_number}: {list(updates.keys())}"
        )
        return updated

    @staticmethod
    def add_student_record(student_data: Dict[str, Any], requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        AdminService._verify_admin(requesting_user)
        db = get_db()
        created = db.add_student_to_registry(student_data)
        db.log_audit(
            requesting_user.get("register_number", "ADMIN"),
            "ADMINISTRATOR",
            "ADD_STUDENT_REGISTRY",
            created.get("register_number", ""),
            f"Added new student {created.get('full_name')} to registry."
        )
        return created

    @staticmethod
    def list_audit_logs(requesting_user: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        AdminService._verify_admin(requesting_user)
        db = get_db()
        return db.list_audit_logs(limit=limit)

    @staticmethod
    def export_report(requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        AdminService._verify_admin(requesting_user)
        db = get_db()
        metrics = AdminService.get_dashboard_metrics(requesting_user)
        return {
            "report_title": "Campus Club Management & Eligibility Verification Comprehensive Report",
            "generated_at": db.audit_logs[0]["timestamp"] if db.audit_logs else "",
            "campus_analytics": metrics["metrics"],
            "club_capacities": metrics["club_stats"],
            "total_applications_recorded": len(db.applications),
            "total_memberships_active": len(db.memberships)
        }

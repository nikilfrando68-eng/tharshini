"""
Eligibility Rule Management Service
Manages club criteria configuration, versioning, and publishing by administrators.
Ensures historical eligibility decisions remain intact upon rule changes.
"""

from typing import Dict, Any, List
from .db_adapter import get_db

class RuleService:

    @staticmethod
    def get_active_rule(club_id: str) -> Dict[str, Any]:
        db = get_db()
        rule = db.get_active_rule(club_id)
        if not rule:
            raise KeyError(f"No active eligibility rules configured for club {club_id}.")
        return rule

    @staticmethod
    def list_rule_history(club_id: str) -> List[Dict[str, Any]]:
        db = get_db()
        return db.list_rule_history(club_id)

    @staticmethod
    def publish_new_rule(club_id: str, rule_data: Dict[str, Any], requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publishes a new eligibility rule version.
        Only ADMINISTRATOR role is authorized.
        """
        if requesting_user.get("role") != "ADMINISTRATOR":
            raise PermissionError("Access denied: Only college administrators can configure and publish eligibility rules.")

        db = get_db()
        club = db.get_club(club_id)
        if not club:
            raise KeyError(f"Club {club_id} not found.")

        # Cleanse and cast data
        cleaned = {
            "min_cgpa": float(rule_data["min_cgpa"]) if rule_data.get("min_cgpa") not in [None, ""] else None,
            "min_aptitude_score": int(rule_data["min_aptitude_score"]) if rule_data.get("min_aptitude_score") not in [None, ""] else None,
            "min_programming_score": int(rule_data["min_programming_score"]) if rule_data.get("min_programming_score") not in [None, ""] else None,
            "allowed_departments": rule_data.get("allowed_departments", ["*"]),
            "allowed_academic_years": rule_data.get("allowed_academic_years", ["*"]),
            "required_courses": rule_data.get("required_courses", []),
            "required_certifications": rule_data.get("required_certifications", []),
            "min_attendance_percentage": float(rule_data["min_attendance_percentage"]) if rule_data.get("min_attendance_percentage") not in [None, ""] else None,
            "required_skill_assessments": rule_data.get("required_skill_assessments", {}),
            "remarks": rule_data.get("remarks", "Updated eligibility criteria")
        }

        published = db.publish_new_rule(club_id, cleaned, requesting_user.get("register_number", "ADMIN"))
        db.log_audit(
            requesting_user.get("register_number", "ADMIN"),
            "ADMINISTRATOR",
            "PUBLISH_ELIGIBILITY_RULE",
            f"{club_id}:{published['version']}",
            f"Published rule {published['version']} for {club.get('name')}. {cleaned['remarks']}"
        )
        return published

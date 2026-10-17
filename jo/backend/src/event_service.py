"""
Event Management Service
Handles campus club events, workshops, hackathons, participant capacity limits,
and duplicate registration prevention.
"""

from typing import Dict, Any, List, Optional
from .db_adapter import get_db

class EventService:

    @staticmethod
    def list_events(club_id: Optional[str] = None) -> List[Dict[str, Any]]:
        db = get_db()
        return db.list_events(club_id=club_id)

    @staticmethod
    def get_event(event_id: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        return db.get_event(event_id)

    @staticmethod
    def register_student(event_id: str, requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        reg_num = requesting_user.get("register_number")
        if not reg_num:
            raise ValueError("Student Register Number required.")

        db = get_db()
        profile = db.get_student_record(reg_num) or requesting_user
        registered = db.register_for_event(event_id, profile)

        db.log_audit(
            reg_num,
            "STUDENT",
            "REGISTER_EVENT",
            event_id,
            f"Registered for event {registered.get('event_title')}"
        )
        return registered

    @staticmethod
    def list_my_registrations(requesting_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        reg_num = requesting_user.get("register_number")
        db = get_db()
        return db.list_student_event_registrations(reg_num)

    @staticmethod
    def create_event(event_data: Dict[str, Any], requesting_user: Dict[str, Any]) -> Dict[str, Any]:
        role = requesting_user.get("role")
        creator_id = requesting_user.get("register_number", "USER")

        if role not in ["ADMINISTRATOR", "CLUB_LEADER"]:
            raise PermissionError("Only club leaders and administrators can create events.")

        club_id = event_data.get("club_id")
        if not club_id:
            raise ValueError("Club ID is required.")

        if role == "CLUB_LEADER":
            assigned = requesting_user.get("assigned_clubs", [])
            if club_id not in assigned:
                raise PermissionError("You can only create events for clubs you are officially assigned to lead.")

        db = get_db()
        club = db.get_club(club_id)
        if not club:
            raise KeyError(f"Club {club_id} not found.")

        event_data["club_name"] = club.get("name")
        created = db.create_event(event_data, creator_id)

        db.log_audit(
            creator_id,
            role,
            "CREATE_EVENT",
            created["event_id"],
            f"Created event '{created.get('title')}' for {club.get('name')}"
        )
        return created

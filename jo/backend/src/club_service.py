"""
Club Service
Handles club discovery, catalog exploration, and administrator club management.
"""

from typing import Dict, Any, List, Optional
from .db_adapter import get_db

class ClubService:

    @staticmethod
    def list_clubs(category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        db = get_db()
        clubs = db.list_clubs()
        filtered = []
        for c in clubs:
            if category and category.lower() != "all" and c.get("category", "").lower() != category.lower():
                continue
            if search:
                term = search.lower()
                name_match = term in c.get("name", "").lower()
                desc_match = term in c.get("description", "").lower()
                tag_match = any(term in t.lower() for t in c.get("tags", []))
                if not (name_match or desc_match or tag_match):
                    continue
            filtered.append(c)
        return filtered

    @staticmethod
    def get_club(club_id: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        club = db.get_club(club_id)
        if not club:
            return None
        # Include active rule summary
        active_rule = db.get_active_rule(club_id)
        club_data = dict(club)
        club_data["active_rule"] = active_rule
        return club_data

    @staticmethod
    def save_club(club_data: Dict[str, Any], actor: Dict[str, Any]) -> Dict[str, Any]:
        if actor.get("role") != "ADMINISTRATOR":
            raise PermissionError("Only portal administrators can create or update clubs.")
        db = get_db()
        saved = db.save_club(club_data)
        db.log_audit(
            actor.get("register_number", "ADMIN"),
            "ADMINISTRATOR",
            "UPDATE_CLUB",
            saved.get("club_id", ""),
            f"Updated club details for {saved.get('name')}"
        )
        return saved

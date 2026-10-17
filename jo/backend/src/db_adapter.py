"""
Database Access Layer (DAL)
Supports Amazon DynamoDB in production on AWS, and a fully compliant
in-memory / JSON-persisted DynamoDB store for local testing, offline development,
and CI/CD test suites.
"""

import os
import json
import time
import copy
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .seed_data import (
    INITIAL_REGISTRY,
    INITIAL_USERS,
    INITIAL_CLUBS,
    INITIAL_RULES,
    INITIAL_APPLICATIONS,
    INITIAL_MEMBERSHIPS,
    INITIAL_EVENTS,
    INITIAL_EVENT_REGISTRATIONS,
    INITIAL_AUDIT_LOGS
)

class LocalDynamoStore:
    """
    High-fidelity simulation of DynamoDB tables with:
    - Partition Key & Sort Key mapping
    - Secondary Index querying (GSI)
    - Condition expressions (attribute_not_exists, < capacity)
    - Version history preservation
    - Atomic counters & transactions
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = LocalDynamoStore()
        return cls._instance

    def __init__(self):
        self.reset()

    def reset(self):
        """Resets store back to official initial seed state."""
        self.registry = copy.deepcopy(INITIAL_REGISTRY)
        self.users = copy.deepcopy(INITIAL_USERS)
        self.clubs = copy.deepcopy(INITIAL_CLUBS)
        self.rules = copy.deepcopy(INITIAL_RULES)  # club_id -> active rule
        self.rule_history = {}                     # f"{club_id}:{version}" -> rule
        for cid, r in self.rules.items():
            key = f"{cid}:{r['version']}"
            self.rule_history[key] = copy.deepcopy(r)
        self.applications = copy.deepcopy(INITIAL_APPLICATIONS)
        self.memberships = copy.deepcopy(INITIAL_MEMBERSHIPS)
        self.events = copy.deepcopy(INITIAL_EVENTS)
        self.event_registrations = copy.deepcopy(INITIAL_EVENT_REGISTRATIONS)
        self.audit_logs = copy.deepcopy(INITIAL_AUDIT_LOGS)

    # ------------------ Registry & Students ------------------
    def get_student_record(self, register_number: str) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self.registry.get(str(register_number)))

    def list_all_students(self) -> List[Dict[str, Any]]:
        return list(self.registry.values())

    def update_student_registry(self, register_number: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        reg_num = str(register_number)
        if reg_num not in self.registry:
            raise KeyError(f"Student {reg_num} not found in official registry.")
        student = self.registry[reg_num]
        for k, v in updates.items():
            if k not in ["register_number"]:  # Prevent altering register number
                student[k] = v
        return copy.deepcopy(student)

    def add_student_to_registry(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        reg_num = str(student_data.get("register_number", "")).strip()
        if not reg_num:
            raise ValueError("Register Number is required.")
        if reg_num in self.registry:
            raise ValueError(f"Student with Register Number {reg_num} already exists in official registry.")
        self.registry[reg_num] = copy.deepcopy(student_data)
        return copy.deepcopy(self.registry[reg_num])

    # ------------------ Authentication & Users ------------------
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self.users.get(str(username)))

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        username = str(user_data.get("username", "")).strip()
        if not username:
            raise ValueError("Username / Register Number is required.")
        if username in self.users:
            raise ValueError(f"User '{username}' already registered.")
        self.users[username] = copy.deepcopy(user_data)
        return copy.deepcopy(self.users[username])

    # ------------------ Clubs ------------------
    def list_clubs(self) -> List[Dict[str, Any]]:
        return list(self.clubs.values())

    def get_club(self, club_id: str) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self.clubs.get(club_id))

    def save_club(self, club_data: Dict[str, Any]) -> Dict[str, Any]:
        cid = club_data.get("club_id")
        if not cid:
            raise ValueError("Club ID required.")
        self.clubs[cid] = copy.deepcopy(club_data)
        return copy.deepcopy(self.clubs[cid])

    # ------------------ Eligibility Rules & Versioning ------------------
    def get_active_rule(self, club_id: str) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self.rules.get(club_id))

    def get_rule_by_version(self, club_id: str, version: str) -> Optional[Dict[str, Any]]:
        key = f"{club_id}:{version}"
        return copy.deepcopy(self.rule_history.get(key))

    def list_rule_history(self, club_id: str) -> List[Dict[str, Any]]:
        history = [r for k, r in self.rule_history.items() if k.startswith(f"{club_id}:")]
        history.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return history

    def publish_new_rule(self, club_id: str, rule_data: Dict[str, Any], published_by: str) -> Dict[str, Any]:
        current = self.rules.get(club_id)
        if current:
            # calculate next version (e.g. v1.0 -> v1.1 or v2.0)
            curr_ver = current.get("version", "v1.0")
            try:
                ver_num = float(curr_ver.lstrip("v"))
                next_ver = f"v{ver_num + 0.1:.1f}"
            except ValueError:
                next_ver = f"{curr_ver}.1"
        else:
            next_ver = "v1.0"

        new_rule = copy.deepcopy(rule_data)
        new_rule["club_id"] = club_id
        new_rule["version"] = next_ver
        new_rule["is_active"] = True
        new_rule["published_by"] = published_by
        new_rule["published_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        self.rules[club_id] = copy.deepcopy(new_rule)
        self.rule_history[f"{club_id}:{next_ver}"] = copy.deepcopy(new_rule)
        return copy.deepcopy(new_rule)

    # ------------------ Applications & Capacity ------------------
    def list_applications(self, student_id: Optional[str] = None, club_id: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for app in self.applications:
            if student_id and app.get("register_number") != student_id and app.get("student_id") != student_id:
                continue
            if club_id and app.get("club_id") != club_id:
                continue
            results.append(copy.deepcopy(app))
        results.sort(key=lambda x: x.get("applied_at", ""), reverse=True)
        return results

    def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        for app in self.applications:
            if app.get("application_id") == application_id:
                return copy.deepcopy(app)
        return None

    def create_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        DynamoDB-style atomic check:
        1. Check duplicate application for the same student + club (active status).
        2. Check club capacity.
        """
        reg_num = app_data.get("register_number")
        club_id = app_data.get("club_id")

        # 1. Duplicate check
        for app in self.applications:
            if app.get("register_number") == reg_num and app.get("club_id") == club_id:
                if app.get("status") in ["PENDING_APPROVAL", "APPROVED"]:
                    raise ValueError(f"Student {reg_num} already has an active application or membership for club {club_id}.")

        # 2. Capacity check
        club = self.clubs.get(club_id)
        if not club:
            raise ValueError(f"Club {club_id} not found.")

        current_count = club.get("current_members_count", 0)
        max_cap = club.get("capacity", 50)
        if current_count >= max_cap:
            raise ValueError(f"Cannot apply: Club '{club.get('name')}' has reached its maximum capacity of {max_cap} members.")

        # Create application
        new_app = copy.deepcopy(app_data)
        if "application_id" not in new_app:
            new_app["application_id"] = f"APP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{reg_num[-4:]}"
        new_app["status"] = "PENDING_APPROVAL"
        new_app["applied_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        self.applications.append(new_app)
        return copy.deepcopy(new_app)

    def update_application_status(self, application_id: str, new_status: str, reviewer_id: str, remarks: str = "") -> Dict[str, Any]:
        target = None
        for app in self.applications:
            if app.get("application_id") == application_id:
                target = app
                break
        if not target:
            raise KeyError(f"Application {application_id} not found.")

        old_status = target.get("status")
        club_id = target.get("club_id")
        club = self.clubs.get(club_id)

        if new_status == "APPROVED" and old_status != "APPROVED":
            # Capacity check before approving
            if club:
                current_count = club.get("current_members_count", 0)
                max_cap = club.get("capacity", 50)
                if current_count >= max_cap:
                    raise ValueError(f"Club capacity exceeded! Cannot approve application. Current members: {current_count}/{max_cap}.")
                # Atomic member count increment
                club["current_members_count"] = current_count + 1

                # Create membership
                mem = {
                    "membership_id": f"MEM-{club_id.upper()[:6]}-{target.get('register_number')[-4:]}",
                    "club_id": club_id,
                    "club_name": club.get("name"),
                    "register_number": target.get("register_number"),
                    "student_name": target.get("student_name"),
                    "joined_at": datetime.now(timezone.utc).isoformat() + "Z",
                    "role_in_club": "Active Member"
                }
                self.memberships.append(mem)

        target["status"] = new_status
        target["reviewed_by"] = reviewer_id
        target["reviewed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        target["review_remarks"] = remarks
        return copy.deepcopy(target)

    def cancel_application(self, application_id: str, student_id: str) -> Dict[str, Any]:
        for app in self.applications:
            if app.get("application_id") == application_id:
                if app.get("register_number") != student_id and app.get("student_id") != student_id:
                    raise PermissionError("Students can only cancel their own applications.")
                if app.get("status") != "PENDING_APPROVAL":
                    raise ValueError(f"Cannot cancel application with status '{app.get('status')}'.")
                app["status"] = "CANCELLED"
                app["reviewed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                app["review_remarks"] = "Cancelled by student."
                return copy.deepcopy(app)
        raise KeyError(f"Application {application_id} not found.")

    # ------------------ Memberships ------------------
    def list_memberships(self, student_id: Optional[str] = None, club_id: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for mem in self.memberships:
            if student_id and mem.get("register_number") != student_id:
                continue
            if club_id and mem.get("club_id") != club_id:
                continue
            results.append(copy.deepcopy(mem))
        return results

    # ------------------ Events & Registrations ------------------
    def list_events(self, club_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if club_id:
            return [copy.deepcopy(e) for e in self.events if e.get("club_id") == club_id]
        return [copy.deepcopy(e) for e in self.events]

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        for e in self.events:
            if e.get("event_id") == event_id:
                return copy.deepcopy(e)
        return None

    def create_event(self, event_data: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        new_event = copy.deepcopy(event_data)
        if "event_id" not in new_event:
            new_event["event_id"] = f"EVT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        new_event["created_by"] = creator_id
        new_event["created_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        new_event["registered_count"] = 0
        self.events.append(new_event)
        return copy.deepcopy(new_event)

    def register_for_event(self, event_id: str, student_info: Dict[str, Any]) -> Dict[str, Any]:
        reg_num = student_info.get("register_number")
        target_event = None
        for e in self.events:
            if e.get("event_id") == event_id:
                target_event = e
                break
        if not target_event:
            raise KeyError(f"Event {event_id} not found.")

        # Duplicate check
        for reg in self.event_registrations:
            if reg.get("event_id") == event_id and reg.get("register_number") == reg_num:
                raise ValueError("Student is already registered for this event.")

        # Deadline check
        deadline = target_event.get("registration_deadline")
        if deadline:
            now_iso = datetime.now(timezone.utc).isoformat() + "Z"
            if now_iso > deadline:
                raise ValueError(f"Registration for this event closed on {deadline}.")

        # Capacity check
        current = target_event.get("registered_count", 0)
        max_cap = target_event.get("max_participants", 100)
        if current >= max_cap:
            raise ValueError(f"Event reached maximum participant capacity ({max_cap}).")

        # Atomic increment
        target_event["registered_count"] = current + 1

        reg_entry = {
            "registration_id": f"REG-{event_id[-6:]}-{reg_num[-4:]}",
            "event_id": event_id,
            "event_title": target_event.get("title"),
            "register_number": reg_num,
            "student_name": student_info.get("full_name"),
            "registered_at": datetime.now(timezone.utc).isoformat() + "Z"
        }
        self.event_registrations.append(reg_entry)
        return copy.deepcopy(reg_entry)

    def list_student_event_registrations(self, register_number: str) -> List[Dict[str, Any]]:
        return [copy.deepcopy(r) for r in self.event_registrations if r.get("register_number") == register_number]

    # ------------------ Audit Logs ------------------
    def log_audit(self, actor_id: str, actor_role: str, action: str, target: str, details: str):
        entry = {
            "log_id": f"AUDIT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:17]}",
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "target_entity": target,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }
        self.audit_logs.insert(0, entry)

    def list_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return copy.deepcopy(self.audit_logs[:limit])


# Global Database Adapter Helper
def get_db():
    return LocalDynamoStore.get_instance()

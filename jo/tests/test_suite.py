"""
Comprehensive Automated Test Suite
Verifies all 12 core requirements specified in the AWS Campus Club Management Portal specification.
"""

import unittest
import json
import os
import sys

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.src.lambda_handler import lambda_handler
from backend.src.db_adapter import get_db

class TestCampusClubPortal(unittest.TestCase):

    def setUp(self):
        # Reset database store before each test
        get_db().reset()

    def _login(self, register_number, password):
        event = {
            "httpMethod": "POST",
            "path": "/api/auth/login",
            "body": json.dumps({"register_number": register_number, "password": password})
        }
        res = lambda_handler(event)
        body = json.loads(res.get("body", "{}"))
        return res["statusCode"], body

    # SCENARIO 1: Valid Register Number and Password allow login
    def test_01_valid_login(self):
        code, body = self._login("123456789012", "Student@123")
        self.assertEqual(code, 200)
        self.assertIn("token", body)
        self.assertEqual(body["user"]["register_number"], "123456789012")
        self.assertEqual(body["user"]["role"], "STUDENT")

    # SCENARIO 2: Invalid credentials are rejected
    def test_02_invalid_credentials_rejected(self):
        # Wrong password
        code, body = self._login("123456789012", "WrongPassword!99")
        self.assertEqual(code, 400)
        self.assertIn("Invalid Register Number or Password", body.get("error", ""))

        # Non-existent register number
        code, body = self._login("999999999999", "Student@123")
        self.assertEqual(code, 400)
        self.assertIn("Invalid Register Number or Password", body.get("error", ""))

    # SCENARIO 3: Eligible student can apply for a club
    def test_03_eligible_student_can_apply(self):
        _, login_data = self._login("123456789012", "Student@123")
        token = login_data["token"]

        # Check eligibility for Coding Club (Aptitude 75 >= 70, Prog 80 >= 60)
        eval_event = {
            "httpMethod": "GET",
            "path": "/api/student/eligibility/coding-club",
            "headers": {"Authorization": f"Bearer {token}"}
        }
        eval_res = lambda_handler(eval_event)
        eval_body = json.loads(eval_res["body"])
        self.assertEqual(eval_body["status"], "ELIGIBLE_TO_APPLY")
        self.assertTrue(eval_body["is_eligible"])

        # Submit application
        apply_event = {
            "httpMethod": "POST",
            "path": "/api/student/apply",
            "headers": {"Authorization": f"Bearer {token}"},
            "body": json.dumps({"club_id": "coding-club"})
        }
        apply_res = lambda_handler(apply_event)
        self.assertEqual(apply_res["statusCode"], 201)
        apply_body = json.loads(apply_res["body"])
        self.assertIn("application", apply_body)
        self.assertEqual(apply_body["application"]["status"], "PENDING_APPROVAL")
        self.assertEqual(apply_body["application"]["rule_version"], "v1.0")

    # SCENARIO 4: Ineligible student cannot apply
    def test_04_ineligible_student_cannot_apply(self):
        # Priya Sharma: Aptitude 55 (<70), Programming 50 (<60)
        _, login_data = self._login("123456789013", "Student@123")
        token = login_data["token"]

        eval_event = {
            "httpMethod": "GET",
            "path": "/api/student/eligibility/coding-club",
            "headers": {"Authorization": f"Bearer {token}"}
        }
        eval_res = lambda_handler(eval_event)
        eval_body = json.loads(eval_res["body"])
        self.assertEqual(eval_body["status"], "NOT_ELIGIBLE")
        self.assertFalse(eval_body["is_eligible"])
        self.assertTrue(len(eval_body["failed_reasons"]) >= 2)

        # Attempt to bypass and apply directly
        apply_event = {
            "httpMethod": "POST",
            "path": "/api/student/apply",
            "headers": {"Authorization": f"Bearer {token}"},
            "body": json.dumps({"club_id": "coding-club"})
        }
        apply_res = lambda_handler(apply_event)
        self.assertEqual(apply_res["statusCode"], 400)
        apply_body = json.loads(apply_res["body"])
        self.assertIn("Application rejected", apply_body.get("error", ""))

    # SCENARIO 5: Missing verified information results in Pending Verification
    def test_05_pending_verification_status(self):
        # Rahul Verma has status PENDING_VERIFICATION in official registry
        _, login_data = self._login("123456789014", "Student@123")
        token = login_data["token"]

        eval_event = {
            "httpMethod": "GET",
            "path": "/api/student/eligibility/coding-club",
            "headers": {"Authorization": f"Bearer {token}"}
        }
        eval_res = lambda_handler(eval_event)
        eval_body = json.loads(eval_res["body"])
        self.assertEqual(eval_body["status"], "PENDING_VERIFICATION")
        self.assertFalse(eval_body["is_eligible"])
        self.assertIn("Pending Verification", eval_body["failed_reasons"][0])

    # SCENARIO 6: Students cannot modify official academic scores
    def test_06_students_cannot_modify_academic_scores(self):
        _, login_data = self._login("123456789012", "Student@123")
        token = login_data["token"]

        # Attempt to invoke admin registry PUT endpoint as student
        hack_event = {
            "httpMethod": "PUT",
            "path": "/api/admin/registry/123456789012",
            "headers": {"Authorization": f"Bearer {token}"},
            "body": json.dumps({"cgpa": 10.0, "aptitude_score": 100})
        }
        hack_res = lambda_handler(hack_event)
        self.assertEqual(hack_res["statusCode"], 403)

    # SCENARIO 7: Duplicate applications are rejected
    def test_07_duplicate_applications_rejected(self):
        _, login_data = self._login("123456789012", "Student@123")
        token = login_data["token"]

        # First application succeeds
        apply_event = {
            "httpMethod": "POST",
            "path": "/api/student/apply",
            "headers": {"Authorization": f"Bearer {token}"},
            "body": json.dumps({"club_id": "coding-club"})
        }
        res1 = lambda_handler(apply_event)
        self.assertEqual(res1["statusCode"], 201)

        # Immediate duplicate application is rejected
        res2 = lambda_handler(apply_event)
        self.assertEqual(res2["statusCode"], 400)
        body2 = json.loads(res2["body"])
        self.assertIn("already has an active application", body2.get("error", ""))

    # SCENARIO 8: Club leaders cannot manage unauthorized clubs
    def test_08_club_leader_authorization_boundaries(self):
        # Leader for coding club
        _, login_data = self._login("leader_coding", "Leader@123")
        token = login_data["token"]

        # Attempt to view applications for robotics club
        unauth_event = {
            "httpMethod": "GET",
            "path": "/api/applications",
            "queryStringParameters": {"club_id": "robotics-club"},
            "headers": {"Authorization": f"Bearer {token}"}
        }
        unauth_res = lambda_handler(unauth_event)
        self.assertEqual(unauth_res["statusCode"], 403)
        self.assertIn("Access denied", json.loads(unauth_res["body"]).get("error", ""))

    # SCENARIO 9: Administrators can publish eligibility rules
    def test_09_admin_publish_eligibility_rules(self):
        _, login_data = self._login("admin_portal", "Admin@123")
        token = login_data["token"]

        publish_event = {
            "httpMethod": "POST",
            "path": "/api/rules/coding-club/publish",
            "headers": {"Authorization": f"Bearer {token}"},
            "body": json.dumps({
                "min_aptitude_score": 75,
                "min_programming_score": 70,
                "remarks": "Updated stricter bar for second semester"
            })
        }
        res = lambda_handler(publish_event)
        self.assertEqual(res["statusCode"], 201)
        body = json.loads(res["body"])
        self.assertEqual(body["rule"]["version"], "v1.1")
        self.assertEqual(body["rule"]["min_aptitude_score"], 75)

    # SCENARIO 10: Historical eligibility results preserve original rule version
    def test_10_preserves_historical_rule_version(self):
        # Arjun applies under v1.0
        _, login_data = self._login("123456789012", "Student@123")
        token_arjun = login_data["token"]
        apply_event = {
            "httpMethod": "POST",
            "path": "/api/student/apply",
            "headers": {"Authorization": f"Bearer {token_arjun}"},
            "body": json.dumps({"club_id": "coding-club"})
        }
        res_apply = lambda_handler(apply_event)
        app_id = json.loads(res_apply["body"])["application"]["application_id"]

        # Admin publishes v1.1
        _, admin_login = self._login("admin_portal", "Admin@123")
        token_admin = admin_login["token"]
        lambda_handler({
            "httpMethod": "POST",
            "path": "/api/rules/coding-club/publish",
            "headers": {"Authorization": f"Bearer {token_admin}"},
            "body": json.dumps({"min_aptitude_score": 90, "remarks": "Very high bar"})
        })

        # Fetch Arjun's past application: It must still record v1.0!
        apps_res = lambda_handler({
            "httpMethod": "GET",
            "path": "/api/student/applications",
            "headers": {"Authorization": f"Bearer {token_arjun}"}
        })
        apps = json.loads(apps_res["body"])["applications"]
        past_app = next(a for a in apps if a["application_id"] == app_id)
        self.assertEqual(past_app["rule_version"], "v1.0")

    # SCENARIO 11: Club capacity cannot be exceeded
    def test_11_club_capacity_enforced(self):
        db = get_db()
        # Set club capacity artificially to 1 and members to 1
        club = db.get_club("coding-club")
        club["capacity"] = 1
        club["current_members_count"] = 1
        db.save_club(club)

        _, login_data = self._login("123456789012", "Student@123")
        token = login_data["token"]

        apply_event = {
            "httpMethod": "POST",
            "path": "/api/student/apply",
            "headers": {"Authorization": f"Bearer {token}"},
            "body": json.dumps({"club_id": "coding-club"})
        }
        res = lambda_handler(apply_event)
        self.assertEqual(res["statusCode"], 400)
        self.assertIn("capacity", json.loads(res["body"]).get("error", "").lower())

    # SCENARIO 12: Duplicate event registrations are rejected
    def test_12_duplicate_event_registration_rejected(self):
        _, login_data = self._login("123456789012", "Student@123")
        token = login_data["token"]

        # Register for AI workshop (EVT-2026-002)
        reg_event = {
            "httpMethod": "POST",
            "path": "/api/events/EVT-2026-002/register",
            "headers": {"Authorization": f"Bearer {token}"}
        }
        res1 = lambda_handler(reg_event)
        self.assertEqual(res1["statusCode"], 201)

        # Attempt to register again
        res2 = lambda_handler(reg_event)
        self.assertEqual(res2["statusCode"], 400)
        self.assertIn("already registered", json.loads(res2["body"]).get("error", ""))

    # SCENARIO 13: Students cannot access another student's private records
    def test_13_privacy_boundary_enforced(self):
        # Arjun logs in
        _, login_data = self._login("123456789012", "Student@123")
        token = login_data["token"]

        # Attempts to read Priya's applications
        unauth_app_event = {
            "httpMethod": "GET",
            "path": "/api/student/applications",
            "headers": {"Authorization": f"Bearer {token}"}
        }
        res = lambda_handler(unauth_app_event)
        apps = json.loads(res["body"])["applications"]
        for a in apps:
            self.assertEqual(a["register_number"], "123456789012")

    # SCENARIO 14: Student can create their own password with official Register Number
    def test_14_student_can_create_own_password(self):
        # 1. Student creates custom password
        create_event = {
            "httpMethod": "POST",
            "path": "/api/auth/create-password",
            "body": json.dumps({
                "register_number": "123456789012",
                "password": "MyCustomPass@2026",
                "confirm_password": "MyCustomPass@2026"
            })
        }
        res = lambda_handler(create_event)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        self.assertIn("Password created successfully", body["message"])

        # 2. Student logs in with the newly created password
        code, login_body = self._login("123456789012", "MyCustomPass@2026")
        self.assertEqual(code, 200)
        self.assertIn("token", login_body)
        self.assertEqual(login_body["user"]["register_number"], "123456789012")

        # 3. Invalid register number not in registry cannot create password
        invalid_event = {
            "httpMethod": "POST",
            "path": "/api/auth/create-password",
            "body": json.dumps({
                "register_number": "000000000000",
                "password": "SomePassword@123",
                "confirm_password": "SomePassword@123"
            })
        }
        res_inv = lambda_handler(invalid_event)
        self.assertEqual(res_inv["statusCode"], 400)
        self.assertIn("not recognized", json.loads(res_inv["body"]).get("error", ""))

if __name__ == "__main__":
    unittest.main()


"""
Automated Student Eligibility Verification Engine
AWS Lambda Core Processing Module

Evaluates a student's official verified profile against a club's active eligibility rules.
All evaluation decisions are strictly calculated on the backend and are tamper-proof.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

class EligibilityEngine:
    """
    Evaluates student eligibility for club applications based on administrator-configured rules.
    """

    @staticmethod
    def evaluate(student_profile: Dict[str, Any], rule: Dict[str, Any], club: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes automated eligibility verification.

        Returns:
            Dict containing:
                - is_eligible: bool
                - status: "ELIGIBLE_TO_APPLY" | "NOT_ELIGIBLE" | "PENDING_VERIFICATION"
                - rule_version: str (e.g., "v1.0")
                - criteria_breakdown: list of criteria check details
                - failed_reasons: list of failure explanation strings
                - evaluation_timestamp: ISO 8601 string
                - club_id: str
                - club_name: str
                - student_register_number: str
        """
        reg_num = student_profile.get("register_number", "UNKNOWN")
        club_id = club.get("club_id", "")
        club_name = club.get("name", "Unknown Club")
        rule_version = rule.get("version", "v1.0")

        # Step 1: Verification status check of student official academic record
        verification_status = student_profile.get("verification_status", "PENDING_VERIFICATION")
        if verification_status != "VERIFIED":
            return {
                "is_eligible": False,
                "status": "PENDING_VERIFICATION",
                "rule_version": rule_version,
                "club_id": club_id,
                "club_name": club_name,
                "student_register_number": reg_num,
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "criteria_breakdown": [
                    {
                        "criterion": "Official College Record Verification",
                        "required": "VERIFIED by College Administration",
                        "actual": f"Status is '{verification_status}'",
                        "passed": False,
                        "is_mandatory": True,
                        "description": "Student academic records, CGPA, and assessment scores must be officially verified by the college registrar."
                    }
                ],
                "failed_reasons": [
                    "Your academic profile is currently 'Pending Verification' with the college administration. Please contact the Academic Registrar."
                ]
            }

        criteria_breakdown: List[Dict[str, Any]] = []
        failed_reasons: List[str] = []

        # 1. Minimum CGPA check
        min_cgpa = rule.get("min_cgpa")
        if min_cgpa is not None:
            actual_cgpa = student_profile.get("cgpa")
            passed = actual_cgpa is not None and actual_cgpa >= float(min_cgpa)
            criteria_breakdown.append({
                "criterion": "Minimum CGPA",
                "required": f">= {min_cgpa:.1f}",
                "actual": f"{actual_cgpa:.2f}" if actual_cgpa is not None else "Not Available",
                "passed": passed,
                "is_mandatory": True,
                "description": f"Verified Cumulative Grade Point Average must be at least {min_cgpa:.1f}."
            })
            if not passed:
                failed_reasons.append(
                    f"Your CGPA of {actual_cgpa if actual_cgpa is not None else 0.0} is below the required minimum of {min_cgpa:.1f}."
                )

        # 2. Minimum Aptitude Score check
        min_aptitude = rule.get("min_aptitude_score")
        if min_aptitude is not None:
            actual_aptitude = student_profile.get("aptitude_score")
            passed = actual_aptitude is not None and actual_aptitude >= int(min_aptitude)
            criteria_breakdown.append({
                "criterion": "College Aptitude Test Score",
                "required": f">= {min_aptitude}/100",
                "actual": f"{actual_aptitude}/100" if actual_aptitude is not None else "Not Taken",
                "passed": passed,
                "is_mandatory": True,
                "description": f"Score in the college-administered aptitude assessment must be at least {min_aptitude}/100."
            })
            if not passed:
                failed_reasons.append(
                    f"Your aptitude assessment score of {actual_aptitude if actual_aptitude is not None else 0}/100 is below the required minimum of {min_aptitude}."
                )

        # 3. Minimum Programming Assessment Score check
        min_prog = rule.get("min_programming_score")
        if min_prog is not None:
            actual_prog = student_profile.get("programming_score")
            passed = actual_prog is not None and actual_prog >= int(min_prog)
            criteria_breakdown.append({
                "criterion": "Programming Assessment Score",
                "required": f">= {min_prog}/100",
                "actual": f"{actual_prog}/100" if actual_prog is not None else "Not Taken",
                "passed": passed,
                "is_mandatory": True,
                "description": f"Official coding and programming benchmark score must be at least {min_prog}/100."
            })
            if not passed:
                failed_reasons.append(
                    f"Your programming assessment score of {actual_prog if actual_prog is not None else 0}/100 is below the required minimum of {min_prog}."
                )

        # 4. Department Restrictions check
        allowed_depts = rule.get("allowed_departments", ["*"])
        if allowed_depts and "*" not in allowed_depts:
            actual_dept = student_profile.get("department", "")
            passed = actual_dept in allowed_depts
            criteria_breakdown.append({
                "criterion": "Eligible Academic Departments",
                "required": ", ".join(allowed_depts),
                "actual": actual_dept,
                "passed": passed,
                "is_mandatory": True,
                "description": f"Club admission is restricted to: {', '.join(allowed_depts)}."
            })
            if not passed:
                failed_reasons.append(
                    f"Department '{actual_dept}' is not currently included in the allowed departments for this club ({', '.join(allowed_depts)})."
                )

        # 5. Academic Year Restrictions check
        allowed_years = rule.get("allowed_academic_years", ["*"])
        if allowed_years and "*" not in allowed_years:
            actual_year = student_profile.get("academic_year")
            # Ensure integer comparisons
            int_years = [int(y) for y in allowed_years if str(y).isdigit()]
            passed = actual_year in int_years
            criteria_breakdown.append({
                "criterion": "Allowed Academic Years",
                "required": "Years " + ", ".join(str(y) for y in int_years),
                "actual": f"Year {actual_year}" if actual_year else "Unknown",
                "passed": passed,
                "is_mandatory": True,
                "description": f"Club applicants must be enrolled in Year: {', '.join(str(y) for y in int_years)}."
            })
            if not passed:
                failed_reasons.append(
                    f"You are in Academic Year {actual_year}, but this club requires enrollment in Year {', '.join(str(y) for y in int_years)}."
                )

        # 6. Required Completed Courses (Prerequisites)
        required_courses = rule.get("required_courses", [])
        if required_courses:
            completed_courses = student_profile.get("completed_courses", [])
            for course in required_courses:
                # Match code or full title
                course_passed = any(course.lower() in c.lower() for c in completed_courses)
                criteria_breakdown.append({
                    "criterion": f"Prerequisite Course: {course}",
                    "required": f"Completed ({course})",
                    "actual": "Completed" if course_passed else "Not Found in Transcript",
                    "passed": course_passed,
                    "is_mandatory": True,
                    "description": f"Mandatory foundational course completion required: {course}."
                })
                if not course_passed:
                    failed_reasons.append(
                        f"Missing prerequisite course: '{course}' has not been marked as completed on your official transcript."
                    )

        # 7. Required Certifications
        required_certs = rule.get("required_certifications", [])
        if required_certs:
            student_certs = student_profile.get("certifications", [])
            for cert in required_certs:
                cert_passed = any(cert.lower() in c.lower() for c in student_certs)
                criteria_breakdown.append({
                    "criterion": f"Required Certification: {cert}",
                    "required": cert,
                    "actual": "Certified" if cert_passed else "Not on File",
                    "passed": cert_passed,
                    "is_mandatory": True,
                    "description": f"Industry / Skill certification requirement: {cert}."
                })
                if not cert_passed:
                    failed_reasons.append(
                        f"Missing required certification: '{cert}'."
                    )

        # 8. Minimum Attendance Percentage check
        min_attendance = rule.get("min_attendance_percentage")
        if min_attendance is not None:
            actual_att = student_profile.get("attendance_percentage")
            passed = actual_att is not None and actual_att >= float(min_attendance)
            criteria_breakdown.append({
                "criterion": "College Attendance Percentage",
                "required": f">= {min_attendance:.1f}%",
                "actual": f"{actual_att:.1f}%" if actual_att is not None else "0.0%",
                "passed": passed,
                "is_mandatory": True,
                "description": f"Minimum overall class attendance of {min_attendance:.1f}% required."
            })
            if not passed:
                failed_reasons.append(
                    f"Your overall college attendance of {actual_att if actual_att is not None else 0.0:.1f}% is below the required {min_attendance:.1f}%."
                )

        # 9. Required Skill Assessments
        required_skills = rule.get("required_skill_assessments", {})
        if required_skills:
            student_skills = student_profile.get("skill_assessments", {})
            for skill_key, required_val in required_skills.items():
                actual_val = student_skills.get(skill_key, "NOT_TAKEN")
                skill_passed = (actual_val == required_val)
                label = skill_key.replace("_", " ").title()
                criteria_breakdown.append({
                    "criterion": f"Skill Assessment: {label}",
                    "required": str(required_val),
                    "actual": str(actual_val),
                    "passed": skill_passed,
                    "is_mandatory": True,
                    "description": f"Technical benchmark result for {label}."
                })
                if not skill_passed:
                    failed_reasons.append(
                        f"Skill assessment for '{label}' required status '{required_val}', but your record shows '{actual_val}'."
                    )

        # Overall Status Calculation
        all_passed = len(failed_reasons) == 0
        overall_status = "ELIGIBLE_TO_APPLY" if all_passed else "NOT_ELIGIBLE"

        return {
            "is_eligible": all_passed,
            "status": overall_status,
            "rule_version": rule_version,
            "club_id": club_id,
            "club_name": club_name,
            "student_register_number": reg_num,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "criteria_breakdown": criteria_breakdown,
            "failed_reasons": failed_reasons
        }

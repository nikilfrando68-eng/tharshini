/**
 * Campus Club Management Portal - Global Frontend Configuration
 */

const CONFIG = {
  // Base API URL (relative for local server, or can point to API Gateway in production)
  API_BASE_URL: window.location.origin + "/api",

  // Demo Credentials for effortless grading & evaluation
  DEMO_USERS: {
    SIST_STUDENT: {
      name: "SIST Student (Reg: 44111327 / Pass: 2006)",
      register_number: "44111327",
      password: "2006",
      role: "STUDENT",
      highlights: "Reg No: 44111327 | Pass: 2006 | CGPA: 8.5 | Verified"
    },
    ELIGIBLE_STUDENT: {
      name: "Arjun Kumar (Eligible for Technical Clubs)",
      register_number: "123456789012",
      password: "Student@123",
      role: "STUDENT",
      highlights: "CGPA: 8.2 | Aptitude: 75 | Prog: 80 | Verified"
    },
    INELIGIBLE_STUDENT: {
      name: "Priya Sharma (Ineligible for Coding/AI)",
      register_number: "123456789013",
      password: "Student@123",
      role: "STUDENT",
      highlights: "CGPA: 6.8 | Aptitude: 55 (<70) | Prog: 50 (<60)"
    },
    PENDING_STUDENT: {
      name: "Rahul Verma (Pending Verification)",
      register_number: "123456789014",
      password: "Student@123",
      role: "STUDENT",
      highlights: "Official Academic Record: PENDING_VERIFICATION"
    },
    CLUB_LEADER: {
      name: "Priya Nair (Leader - Coding Club)",
      register_number: "leader_coding",
      password: "Leader@123",
      role: "CLUB_LEADER",
      highlights: "Assigned Club: Coding Club"
    },
    ADMIN: {
      name: "Dr. Rajesh Murthy (Dean & Chief Admin)",
      register_number: "admin_portal",
      password: "Admin@123",
      role: "ADMINISTRATOR",
      highlights: "Full Campus Access & Rule Publishing"
    }
  }
};

"""
Seed Data for Campus Club Management Portal
Contains official student registry, clubs, published eligibility rules (v1.0),
pre-configured user credentials, initial applications, memberships, and events.
"""

INITIAL_REGISTRY = {
    "44111327": {
        "register_number": "44111327",
        "full_name": "Arjun Kumar (SIST Student)",
        "email": "44111327@sathyabama.ac.in",
        "department": "Computer Science and Engineering",
        "academic_year": 3,
        "cgpa": 8.5,
        "aptitude_score": 80,
        "programming_score": 85,
        "completed_courses": [
            "CS101 - Intro to Programming",
            "CS201 - Data Structures & Algorithms",
            "EC101 - Basic Electronics"
        ],
        "certifications": ["AWS Certified Cloud Practitioner"],
        "attendance_percentage": 92.0,
        "skill_assessments": {
            "robotics_basics": "PASSED",
            "web_dev": "PASSED"
        },
        "verification_status": "VERIFIED"
    },
    "123456789012": {
        "register_number": "123456789012",
        "full_name": "Arjun Kumar",
        "email": "arjun.kumar@campus.edu",
        "department": "Computer Science and Engineering",
        "academic_year": 3,
        "cgpa": 8.2,
        "aptitude_score": 75,
        "programming_score": 80,
        "completed_courses": [
            "CS101 - Intro to Programming",
            "CS201 - Data Structures & Algorithms",
            "EC101 - Basic Electronics"
        ],
        "certifications": ["AWS Certified Cloud Practitioner"],
        "attendance_percentage": 89.5,
        "skill_assessments": {
            "robotics_basics": "PASSED",
            "web_dev": "PASSED"
        },
        "verification_status": "VERIFIED"
    },
    "123456789013": {
        "register_number": "123456789013",
        "full_name": "Priya Sharma",
        "email": "priya.sharma@campus.edu",
        "department": "Electronics and Communication",
        "academic_year": 2,
        "cgpa": 6.8,
        "aptitude_score": 55,
        "programming_score": 50,
        "completed_courses": [
            "EC101 - Basic Electronics"
        ],
        "certifications": [],
        "attendance_percentage": 82.0,
        "skill_assessments": {
            "robotics_basics": "PENDING"
        },
        "verification_status": "VERIFIED"
    },
    "123456789014": {
        "register_number": "123456789014",
        "full_name": "Rahul Verma",
        "email": "rahul.verma@campus.edu",
        "department": "Mechanical Engineering",
        "academic_year": 1,
        "cgpa": 7.9,
        "aptitude_score": 72,
        "programming_score": 65,
        "completed_courses": [
            "ME101 - Engineering Mechanics"
        ],
        "certifications": [],
        "attendance_percentage": 91.0,
        "skill_assessments": {},
        "verification_status": "PENDING_VERIFICATION"
    },
    "123456789015": {
        "register_number": "123456789015",
        "full_name": "Sneha Patel",
        "email": "sneha.patel@campus.edu",
        "department": "Information Technology",
        "academic_year": 4,
        "cgpa": 9.1,
        "aptitude_score": 90,
        "programming_score": 92,
        "completed_courses": [
            "CS101 - Intro to Programming",
            "CS201 - Data Structures & Algorithms",
            "IT301 - Cloud Computing"
        ],
        "certifications": ["AWS Certified Solutions Architect", "Python Certified Developer"],
        "attendance_percentage": 94.0,
        "skill_assessments": {
            "web_dev": "PASSED",
            "ai_foundations": "PASSED"
        },
        "verification_status": "VERIFIED"
    }
}

INITIAL_USERS = {
    # Students
    "44111327": {
        "username": "44111327",
        "password_hash": "2006",
        "role": "STUDENT",
        "register_number": "44111327",
        "full_name": "Arjun Kumar (SIST Student)",
        "email": "44111327@sathyabama.ac.in",
        "department": "Computer Science and Engineering",
        "is_active": True
    },
    "123456789012": {
        "username": "123456789012",
        "password_hash": "Student@123",  # In production, managed by Cognito User Pool
        "role": "STUDENT",
        "register_number": "123456789012",
        "full_name": "Arjun Kumar",
        "email": "arjun.kumar@campus.edu",
        "department": "Computer Science and Engineering",
        "is_active": True
    },
    "123456789013": {
        "username": "123456789013",
        "password_hash": "Student@123",
        "role": "STUDENT",
        "register_number": "123456789013",
        "full_name": "Priya Sharma",
        "email": "priya.sharma@campus.edu",
        "department": "Electronics and Communication",
        "is_active": True
    },
    "123456789014": {
        "username": "123456789014",
        "password_hash": "Student@123",
        "role": "STUDENT",
        "register_number": "123456789014",
        "full_name": "Rahul Verma",
        "email": "rahul.verma@campus.edu",
        "department": "Mechanical Engineering",
        "is_active": True
    },
    "123456789015": {
        "username": "123456789015",
        "password_hash": "Student@123",
        "role": "STUDENT",
        "register_number": "123456789015",
        "full_name": "Sneha Patel",
        "email": "sneha.patel@campus.edu",
        "department": "Information Technology",
        "is_active": True
    },
    # Club Leaders
    "leader_coding": {
        "username": "leader_coding",
        "password_hash": "Leader@123",
        "role": "CLUB_LEADER",
        "register_number": "LEAD-CODING-01",
        "full_name": "Priya Nair",
        "email": "priya.nair@campus.edu",
        "department": "Computer Science and Engineering",
        "assigned_clubs": ["coding-club"],
        "is_active": True
    },
    "leader_robotics": {
        "username": "leader_robotics",
        "password_hash": "Leader@123",
        "role": "CLUB_LEADER",
        "register_number": "LEAD-ROBOT-02",
        "full_name": "Vikram Sethi",
        "email": "vikram.sethi@campus.edu",
        "department": "Electronics and Communication",
        "assigned_clubs": ["robotics-club"],
        "is_active": True
    },
    # Administrator
    "admin_portal": {
        "username": "admin_portal",
        "password_hash": "Admin@123",
        "role": "ADMINISTRATOR",
        "register_number": "ADMIN-001",
        "full_name": "Dr. Rajesh Murthy",
        "email": "dean.students@campus.edu",
        "department": "Administration / Dean of Student Affairs",
        "is_active": True
    }
}

INITIAL_CLUBS = {
    "coding-club": {
        "club_id": "coding-club",
        "name": "Coding Club",
        "category": "Technical",
        "description": "Fostering competitive programming, software architecture, open source contributions, and hackathon training.",
        "faculty_coordinator": "Dr. Anita Rao (CSE Dept)",
        "leader_id": "leader_coding",
        "leader_name": "Priya Nair",
        "capacity": 50,
        "current_members_count": 32,
        "meeting_schedule": "Wednesdays & Saturdays, 5:00 PM - 7:00 PM",
        "venue": "Turing Computer Lab 3",
        "icon": "bi-code-slash",
        "banner_color": "#4f46e5",
        "tags": ["Algorithms", "Python", "Web Dev", "Hackathons"]
    },
    "ai-ml-club": {
        "club_id": "ai-ml-club",
        "name": "Artificial Intelligence Club",
        "category": "Technical",
        "description": "Exploring modern machine learning, deep neural networks, computer vision, and generative AI systems with AWS cloud integration.",
        "faculty_coordinator": "Prof. S. Narayanan (Data Science)",
        "leader_id": "leader_aiml",
        "leader_name": "Karthik Raman",
        "capacity": 40,
        "current_members_count": 28,
        "meeting_schedule": "Tuesdays & Fridays, 4:30 PM - 6:30 PM",
        "venue": "AI Center of Excellence, Hall B",
        "icon": "bi-cpu",
        "banner_color": "#7c3aed",
        "tags": ["Machine Learning", "Deep Learning", "PyTorch", "AWS SageMaker"]
    },
    "robotics-club": {
        "club_id": "robotics-club",
        "name": "Robotics Club",
        "category": "Engineering & Hardware",
        "description": "Designing autonomous mobile robots, IoT automation systems, embedded electronics, and competing in national rover challenges.",
        "faculty_coordinator": "Dr. K. Balaji (ECE / Mechatronics)",
        "leader_id": "leader_robotics",
        "leader_name": "Vikram Sethi",
        "capacity": 35,
        "current_members_count": 20,
        "meeting_schedule": "Mondays & Thursdays, 5:00 PM - 7:30 PM",
        "venue": "Robotics & Microcontroller Workshop",
        "icon": "bi-robot",
        "banner_color": "#0284c7",
        "tags": ["Arduino", "ROS", "Embedded Systems", "Drones"]
    },
    "cybersecurity-club": {
        "club_id": "cybersecurity-club",
        "name": "Cybersecurity Club",
        "category": "Technical & Security",
        "description": "Dedicated to ethical hacking, reverse engineering, CTF competitions, digital forensics, and cloud infrastructure security.",
        "faculty_coordinator": "Prof. Meenakshi Sundaram (InfoSec)",
        "leader_id": "leader_cyber",
        "leader_name": "Ananya Sen",
        "capacity": 30,
        "current_members_count": 22,
        "meeting_schedule": "Fridays, 5:00 PM - 8:00 PM",
        "venue": "Cyber Defense Sandbox Lab",
        "icon": "bi-shield-lock",
        "banner_color": "#0d9488",
        "tags": ["Ethical Hacking", "CTF", "Cryptography", "Network Security"]
    },
    "cultural-club": {
        "club_id": "cultural-club",
        "name": "Cultural Club",
        "category": "Arts & Culture",
        "description": "Promoting theatrical drama, fine arts, collegiate dance troupes, and orchestrating the annual campus cultural festival.",
        "faculty_coordinator": "Dr. V. Saraswathi (Humanities)",
        "leader_id": "leader_cultural",
        "leader_name": "Divya Iyer",
        "capacity": 100,
        "current_members_count": 64,
        "meeting_schedule": "Saturdays, 2:00 PM - 6:00 PM",
        "venue": "Campus Open Air Amphitheatre",
        "icon": "bi-palette",
        "banner_color": "#e11d48",
        "tags": ["Dance", "Dramatics", "Fine Arts", "Festivals"]
    },
    "photography-club": {
        "club_id": "photography-club",
        "name": "Photography Club",
        "category": "Media & Creative",
        "description": "Mastering DSLR cinematography, photojournalism, visual storytelling, and digital post-production for campus media.",
        "faculty_coordinator": "Prof. David Miller (Visual Media)",
        "leader_id": "leader_photo",
        "leader_name": "Rohan Bose",
        "capacity": 45,
        "current_members_count": 29,
        "meeting_schedule": "Sundays, 9:00 AM - 12:00 PM",
        "venue": "Media Studio & Darkroom",
        "icon": "bi-camera",
        "banner_color": "#d97706",
        "tags": ["Photography", "Cinematography", "Lightroom", "Media"]
    },
    "sports-club": {
        "club_id": "sports-club",
        "name": "Sports Club",
        "category": "Athletics",
        "description": "Coordinating inter-university athletics, basketball, football, badminton tournaments, and fitness conditioning programs.",
        "faculty_coordinator": "Coach R. Subramanian (Physical Education)",
        "leader_id": "leader_sports",
        "leader_name": "Sanjay Das",
        "capacity": 80,
        "current_members_count": 55,
        "meeting_schedule": "Daily Practice, 6:00 AM - 8:00 AM",
        "venue": "Main Sports Complex & Track",
        "icon": "bi-trophy",
        "banner_color": "#16a34a",
        "tags": ["Athletics", "Football", "Basketball", "Fitness"]
    },
    "music-club": {
        "club_id": "music-club",
        "name": "Music Club",
        "category": "Performing Arts",
        "description": "Bringing together vocalists, classical musicians, rock bands, and digital music producers for concerts and recordings.",
        "faculty_coordinator": "Dr. Gayatri Venkat (Fine Arts)",
        "leader_id": "leader_music",
        "leader_name": "Meera Krishnan",
        "capacity": 50,
        "current_members_count": 38,
        "meeting_schedule": "Tuesdays & Thursdays, 5:30 PM - 7:30 PM",
        "venue": "Acoustic Music Studio",
        "icon": "bi-music-note-beamed",
        "banner_color": "#9333ea",
        "tags": ["Classical", "Rock Band", "Vocals", "Acoustic"]
    },
    "entrepreneurship-club": {
        "club_id": "entrepreneurship-club",
        "name": "Entrepreneurship Club",
        "category": "Business & Innovation",
        "description": "Incubating student startups, venture pitch sessions, angel investor networking, and business model prototyping.",
        "faculty_coordinator": "Prof. Anand Joshi (Management Studies)",
        "leader_id": "leader_ecell",
        "leader_name": "Aditya Singhal",
        "capacity": 40,
        "current_members_count": 25,
        "meeting_schedule": "Fridays, 4:00 PM - 6:00 PM",
        "venue": "Campus Incubation Hub, Room 102",
        "icon": "bi-lightbulb",
        "banner_color": "#ea580c",
        "tags": ["Startups", "Venture Capital", "Pitching", "Innovation"]
    }
}

INITIAL_RULES = {
    "coding-club": {
        "club_id": "coding-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": None,
        "min_aptitude_score": 70,
        "min_programming_score": 60,
        "allowed_departments": ["*"],
        "allowed_academic_years": ["*"],
        "required_courses": [],
        "required_certifications": [],
        "min_attendance_percentage": None,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "Official criteria for 2026-27: Aptitude >= 70, Programming >= 60"
    },
    "ai-ml-club": {
        "club_id": "ai-ml-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": 7.5,
        "min_aptitude_score": None,
        "min_programming_score": 65,
        "allowed_departments": ["*"],
        "allowed_academic_years": ["*"],
        "required_courses": ["CS201 - Data Structures & Algorithms"],
        "required_certifications": [],
        "min_attendance_percentage": None,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "AI Club: CGPA >= 7.5, Programming >= 65, Prerequisite CS201"
    },
    "robotics-club": {
        "club_id": "robotics-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": None,
        "min_aptitude_score": None,
        "min_programming_score": None,
        "allowed_departments": ["*"],
        "allowed_academic_years": ["*"],
        "required_courses": ["EC101 - Basic Electronics"],
        "required_certifications": [],
        "min_attendance_percentage": None,
        "required_skill_assessments": {"robotics_basics": "PASSED"},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "Robotics: Basic Electronics prerequisite + robotics assessment passed"
    },
    "cybersecurity-club": {
        "club_id": "cybersecurity-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": 7.0,
        "min_aptitude_score": None,
        "min_programming_score": 70,
        "allowed_departments": [
            "Computer Science and Engineering",
            "Information Technology",
            "Electronics and Communication"
        ],
        "allowed_academic_years": ["*"],
        "required_courses": [],
        "required_certifications": [],
        "min_attendance_percentage": None,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "Cybersecurity: CSE/IT/ECE only, CGPA >= 7.0, Programming >= 70"
    },
    "cultural-club": {
        "club_id": "cultural-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": None,
        "min_aptitude_score": None,
        "min_programming_score": None,
        "allowed_departments": ["*"],
        "allowed_academic_years": ["*"],
        "required_courses": [],
        "required_certifications": [],
        "min_attendance_percentage": 75.0,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "Cultural Club: Minimum 75% attendance in college classes"
    },
    "photography-club": {
        "club_id": "photography-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": None,
        "min_aptitude_score": None,
        "min_programming_score": None,
        "allowed_departments": ["*"],
        "allowed_academic_years": ["*"],
        "required_courses": [],
        "required_certifications": [],
        "min_attendance_percentage": 70.0,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "Photography: Open to all departments and years, 70% min attendance"
    },
    "sports-club": {
        "club_id": "sports-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": None,
        "min_aptitude_score": None,
        "min_programming_score": None,
        "allowed_departments": ["*"],
        "allowed_academic_years": ["*"],
        "required_courses": [],
        "required_certifications": [],
        "min_attendance_percentage": 75.0,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "Sports: Active academic standing and 75% attendance"
    },
    "music-club": {
        "club_id": "music-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": None,
        "min_aptitude_score": None,
        "min_programming_score": None,
        "allowed_departments": ["*"],
        "allowed_academic_years": ["*"],
        "required_courses": [],
        "required_certifications": [],
        "min_attendance_percentage": 65.0,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "Music: Open to all passionate musicians with 65% attendance"
    },
    "entrepreneurship-club": {
        "club_id": "entrepreneurship-club",
        "version": "v1.0",
        "is_active": True,
        "min_cgpa": 7.0,
        "min_aptitude_score": None,
        "min_programming_score": None,
        "allowed_departments": ["*"],
        "allowed_academic_years": [2, 3, 4],
        "required_courses": [],
        "required_certifications": [],
        "min_attendance_percentage": None,
        "required_skill_assessments": {},
        "published_by": "admin_portal",
        "published_at": "2026-08-01T10:00:00Z",
        "remarks": "E-Club: CGPA >= 7.0 and 2nd, 3rd, or 4th year standing"
    }
}

INITIAL_APPLICATIONS = [
    {
        "application_id": "APP-2026-0001",
        "student_id": "123456789015",
        "register_number": "123456789015",
        "student_name": "Sneha Patel",
        "student_department": "Information Technology",
        "club_id": "coding-club",
        "club_name": "Coding Club",
        "status": "APPROVED",
        "rule_version": "v1.0",
        "criteria_results": {
            "min_aptitude_score": {"passed": True, "required": 70, "actual": 90},
            "min_programming_score": {"passed": True, "required": 60, "actual": 92}
        },
        "evaluation_status": "ELIGIBLE_TO_APPLY",
        "applied_at": "2026-08-10T14:30:00Z",
        "reviewed_by": "leader_coding",
        "reviewed_at": "2026-08-11T10:00:00Z",
        "review_remarks": "Outstanding competitive coding track record."
    }
]

INITIAL_MEMBERSHIPS = [
    {
        "membership_id": "MEM-CODING-001",
        "club_id": "coding-club",
        "club_name": "Coding Club",
        "register_number": "123456789015",
        "student_name": "Sneha Patel",
        "joined_at": "2026-08-11T10:00:00Z",
        "role_in_club": "Core Member"
    }
]

INITIAL_EVENTS = [
    {
        "event_id": "EVT-2026-001",
        "club_id": "coding-club",
        "club_name": "Coding Club",
        "title": "CodeSprint 2026: 24-Hour Annual Campus Hackathon",
        "description": "Build innovative AI & Cloud solutions solving real university campus challenges. Great prizes and industry mentor reviews.",
        "event_date": "2026-11-15",
        "start_time": "09:00 AM",
        "venue": "Campus Innovation Center, Auditorium",
        "registration_deadline": "2026-11-10T23:59:59Z",
        "max_participants": 120,
        "registered_count": 48,
        "category": "Hackathon",
        "created_by": "leader_coding",
        "created_at": "2026-10-01T12:00:00Z"
    },
    {
        "event_id": "EVT-2026-002",
        "club_id": "ai-ml-club",
        "club_name": "Artificial Intelligence Club",
        "title": "Deep Dive into AWS SageMaker & Generative AI",
        "description": "Hands-on masterclass deploying Large Language Models and fine-tuning computer vision algorithms on AWS Cloud.",
        "event_date": "2026-11-20",
        "start_time": "02:00 PM",
        "venue": "Turing Lab 1 & Virtual Stream",
        "registration_deadline": "2026-11-18T18:00:00Z",
        "max_participants": 80,
        "registered_count": 65,
        "category": "Technical Workshop",
        "created_by": "leader_aiml",
        "created_at": "2026-10-05T09:30:00Z"
    },
    {
        "event_id": "EVT-2026-003",
        "club_id": "robotics-club",
        "club_name": "Robotics Club",
        "title": "Autonomous Mars Rover Showcase & Obstacle Course",
        "description": "Watch our student-built rovers navigate complex obstacle terrains with computer vision and LIDAR sensors.",
        "event_date": "2026-11-25",
        "start_time": "03:30 PM",
        "venue": "Outdoor Quadrangle & Robotics Arena",
        "registration_deadline": "2026-11-24T12:00:00Z",
        "max_participants": 150,
        "registered_count": 92,
        "category": "Exhibition",
        "created_by": "leader_robotics",
        "created_at": "2026-10-08T15:00:00Z"
    },
    {
        "event_id": "EVT-2026-004",
        "club_id": "cultural-club",
        "club_name": "Cultural Club",
        "title": "Vibrance 2026: Inter-Collegiate Cultural Extravaganza",
        "description": "Three days of dance, drama, fashion, musical acts, and food stalls from universities across the region.",
        "event_date": "2026-12-05",
        "start_time": "10:00 AM",
        "venue": "Main University Stadium",
        "registration_deadline": "2026-12-01T23:59:59Z",
        "max_participants": 500,
        "registered_count": 310,
        "category": "Festival",
        "created_by": "leader_cultural",
        "created_at": "2026-10-10T11:00:00Z"
    }
]

INITIAL_EVENT_REGISTRATIONS = [
    {
        "registration_id": "REG-EVT-001-01",
        "event_id": "EVT-2026-001",
        "event_title": "CodeSprint 2026: 24-Hour Annual Campus Hackathon",
        "register_number": "123456789012",
        "student_name": "Arjun Kumar",
        "registered_at": "2026-10-02T10:15:00Z"
    }
]

INITIAL_AUDIT_LOGS = [
    {
        "log_id": "AUDIT-001",
        "actor_id": "admin_portal",
        "actor_role": "ADMINISTRATOR",
        "action": "PUBLISH_ELIGIBILITY_RULE",
        "target_entity": "coding-club:v1.0",
        "details": "Published initial eligibility criteria version 1.0 for Coding Club",
        "timestamp": "2026-08-01T10:00:00Z"
    },
    {
        "log_id": "AUDIT-002",
        "actor_id": "admin_portal",
        "actor_role": "ADMINISTRATOR",
        "action": "IMPORT_STUDENT_REGISTRY",
        "target_entity": "REGISTRY",
        "details": "Imported official university academic and assessment database",
        "timestamp": "2026-08-01T09:00:00Z"
    }
]

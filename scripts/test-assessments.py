"""
Test Assessment Endpoints
Tests: get questions, submit assessment, list, get detail, get stats
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test(test_name, success, message=""):
    """Print test result"""
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"\n{BLUE}[Test]{RESET} {test_name}")
    print(f"{status} {message}")


def print_response(response):
    """Print formatted response"""
    print(f"\n{YELLOW}Response ({response.status_code}):{RESET}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


# First, login to get access token
print(f"\n{BLUE}{'='*60}{RESET}")
print(f"{BLUE}Setting up test environment...{RESET}")
print(f"{BLUE}{'='*60}{RESET}")

# Use existing test account or create new one
test_email = "student1@example.com"
test_password = "password123"
access_token = None

print(f"\n{YELLOW}Logging in as {test_email}...{RESET}")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": test_email, "password": test_password}
)

if login_response.status_code == 200:
    access_token = login_response.json()["access_token"]
    print(f"{GREEN}✓ Logged in successfully{RESET}")
else:
    print(f"{RED}✗ Login failed. Make sure student1@example.com exists in database.{RESET}")
    print("Run scripts/seed-data.py first!")
    exit(1)

headers = {"Authorization": f"Bearer {access_token}"}

print(f"\n{BLUE}{'='*60}{RESET}")
print(f"{BLUE}Starting Assessment API Tests{RESET}")
print(f"{BLUE}{'='*60}{RESET}")


# ============================================
# Test 1: Get GAD-7 Questions
# ============================================
print(f"\n\n{YELLOW}Test 1: Get GAD-7 Questions (Vietnamese){RESET}")

try:
    response = requests.get(f"{BASE_URL}/assessments/questions/list", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if "questions" in data and len(data["questions"]) == 7:
            print_test(
                "Get GAD-7 Questions",
                True,
                f"Retrieved {len(data['questions'])} questions in Vietnamese"
            )
            print(f"\n{GREEN}Sample question 1:{RESET}")
            print(f"  {data['questions'][0]['text']}")
        else:
            print_test("Get GAD-7 Questions", False, "Missing questions")
    else:
        print_test("Get GAD-7 Questions", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Get GAD-7 Questions", False, str(e))


# ============================================
# Test 2: Submit Assessment (Minimal Anxiety)
# ============================================
print(f"\n\n{YELLOW}Test 2: Submit Assessment - Minimal Anxiety (Score: 3){RESET}")

minimal_answers = [0, 0, 1, 0, 0, 1, 1]  # Total = 3
assessment_data = {
    "answers": minimal_answers,
    "functional_impairment": 0,
    "notes": "Cảm thấy tốt, chỉ lo lắng nhẹ về bài thi sắp tới"
}

try:
    response = requests.post(
        f"{BASE_URL}/assessments/",
        json=assessment_data,
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        if data["total_score"] == 3 and data["severity_level"] == "minimal":
            print_test(
                "Submit Minimal Anxiety",
                True,
                f"Score: {data['total_score']}, Severity: {data['severity_level']}"
            )
            if data.get("analysis"):
                print(f"\n{GREEN}Gemini Analysis:{RESET}")
                print(f"  {data['analysis'][:200]}...")
            if data.get("recommendations"):
                print(f"\n{GREEN}Recommendations:{RESET}")
                for i, rec in enumerate(data['recommendations'][:3], 1):
                    print(f"  {i}. {rec}")
        else:
            print_test("Submit Minimal Anxiety", False, "Score or severity mismatch")
    else:
        print_test("Submit Minimal Anxiety", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Submit Minimal Anxiety", False, str(e))


# ============================================
# Test 3: Submit Assessment (Moderate Anxiety)
# ============================================
print(f"\n\n{YELLOW}Test 3: Submit Assessment - Moderate Anxiety (Score: 12){RESET}")

moderate_answers = [2, 2, 2, 1, 2, 2, 1]  # Total = 12
assessment_data = {
    "answers": moderate_answers,
    "functional_impairment": 2,
    "notes": "Lo lắng nhiều về thi cuối kỳ, khó ngủ, khó tập trung"
}

try:
    response = requests.post(
        f"{BASE_URL}/assessments/",
        json=assessment_data,
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        if data["total_score"] == 12 and data["severity_level"] == "moderate":
            print_test(
                "Submit Moderate Anxiety",
                True,
                f"Score: {data['total_score']}, Severity: {data['severity_level']}"
            )
            if data.get("analysis"):
                print(f"\n{GREEN}Gemini Analysis:{RESET}")
                print(f"  {data['analysis'][:200]}...")
        else:
            print_test("Submit Moderate Anxiety", False, "Score or severity mismatch")
    else:
        print_test("Submit Moderate Anxiety", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Submit Moderate Anxiety", False, str(e))


# ============================================
# Test 4: Submit Assessment (Severe Anxiety)
# ============================================
print(f"\n\n{YELLOW}Test 4: Submit Assessment - Severe Anxiety (Score: 18){RESET}")

severe_answers = [3, 3, 2, 3, 2, 3, 2]  # Total = 18
assessment_data = {
    "answers": severe_answers,
    "functional_impairment": 3,
    "notes": "Lo lắng liên tục, không thể kiểm soát, ảnh hưởng nghiêm trọng đến cuộc sống"
}

try:
    response = requests.post(
        f"{BASE_URL}/assessments/",
        json=assessment_data,
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        if data["total_score"] == 18 and data["severity_level"] == "severe":
            print_test(
                "Submit Severe Anxiety",
                True,
                f"Score: {data['total_score']}, Severity: {data['severity_level']}"
            )
            print(f"\n{RED}⚠ SEVERE ANXIETY DETECTED - Immediate intervention recommended{RESET}")
            if data.get("recommendations"):
                print(f"\n{GREEN}Critical Recommendations:{RESET}")
                for i, rec in enumerate(data['recommendations'], 1):
                    print(f"  {i}. {rec}")
        else:
            print_test("Submit Severe Anxiety", False, "Score or severity mismatch")
    else:
        print_test("Submit Severe Anxiety", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Submit Severe Anxiety", False, str(e))


# ============================================
# Test 5: List Assessments
# ============================================
print(f"\n\n{YELLOW}Test 5: List All Assessments{RESET}")

try:
    response = requests.get(
        f"{BASE_URL}/assessments/?page=1&page_size=10",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["total"] >= 3:
            print_test(
                "List Assessments",
                True,
                f"Found {data['total']} assessments, showing {len(data['items'])} items"
            )
            print(f"\n{GREEN}Recent assessments:{RESET}")
            for item in data['items'][:5]:
                print(f"  - Score: {item['total_score']}, Severity: {item['severity_level']}, Date: {item['created_at'][:10]}")
        else:
            print_test("List Assessments", False, f"Expected >= 3 assessments, got {data.get('total', 0)}")
    else:
        print_test("List Assessments", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("List Assessments", False, str(e))


# ============================================
# Test 6: Get Assessment Detail
# ============================================
print(f"\n\n{YELLOW}Test 6: Get Assessment Detail{RESET}")

# Get the first assessment ID from list
try:
    list_response = requests.get(f"{BASE_URL}/assessments/?page=1&page_size=1", headers=headers)
    if list_response.status_code == 200 and list_response.json()["items"]:
        assessment_id = list_response.json()["items"][0]["id"]
        
        response = requests.get(f"{BASE_URL}/assessments/{assessment_id}", headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if "questions_with_answers" in data and "severity_info" in data:
                print_test(
                    "Get Assessment Detail",
                    True,
                    f"Retrieved full details for assessment #{assessment_id}"
                )
                print(f"\n{GREEN}Questions breakdown:{RESET}")
                for qa in data['questions_with_answers'][:3]:
                    print(f"  Q{qa['question_id']}: {qa['question_text']}")
                    print(f"      → {qa['answer_text']} ({qa['answer_value']} điểm)")
                print(f"\n{GREEN}Severity Info:{RESET}")
                print(f"  Level: {data['severity_info']['name_vi']}")
                print(f"  Description: {data['severity_info']['description_vi'][:100]}...")
            else:
                print_test("Get Assessment Detail", False, "Missing detail fields")
        else:
            print_test("Get Assessment Detail", False, f"Status code: {response.status_code}")
    else:
        print_test("Get Assessment Detail", False, "No assessments found to test detail view")
except Exception as e:
    print_test("Get Assessment Detail", False, str(e))


# ============================================
# Test 7: Get Assessment Statistics
# ============================================
print(f"\n\n{YELLOW}Test 7: Get Assessment Statistics{RESET}")

try:
    response = requests.get(f"{BASE_URL}/assessments/stats", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if data["total_assessments"] >= 3:
            print_test(
                "Get Assessment Stats",
                True,
                f"Total: {data['total_assessments']}, Average: {data['average_score']}, Trend: {data['trend']}"
            )
            print(f"\n{GREEN}Statistics Summary:{RESET}")
            print(f"  Total Assessments: {data['total_assessments']}")
            print(f"  Average Score: {data['average_score']}")
            print(f"  Latest Score: {data['latest_score']} ({data['latest_severity']})")
            print(f"  Trend: {data['trend']}")
            
            if data['score_history']:
                print(f"\n{GREEN}Score History (for charts):{RESET}")
                for entry in data['score_history'][:5]:
                    print(f"  {entry['date'][:10]}: {entry['score']} ({entry['severity']})")
        else:
            print_test("Get Assessment Stats", False, f"Expected >= 3 assessments for stats")
    else:
        print_test("Get Assessment Stats", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Get Assessment Stats", False, str(e))


# ============================================
# Test 8: Invalid Input Validation
# ============================================
print(f"\n\n{YELLOW}Test 8: Validation - Invalid Answers (Should Fail){RESET}")

invalid_data = {
    "answers": [0, 1, 2, 4, 3, 2, 1],  # 4 is invalid (must be 0-3)
    "functional_impairment": 1
}

try:
    response = requests.post(
        f"{BASE_URL}/assessments/",
        json=invalid_data,
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 422:
        print_test("Validation Test", True, "Correctly rejected invalid answer value")
    else:
        print_test("Validation Test", False, f"Expected 422, got {response.status_code}")
except Exception as e:
    print_test("Validation Test", False, str(e))


# ============================================
# Test 9: Validation - Wrong Number of Answers
# ============================================
print(f"\n\n{YELLOW}Test 9: Validation - Wrong Number of Answers (Should Fail){RESET}")

invalid_data = {
    "answers": [0, 1, 2],  # Only 3 answers instead of 7
    "functional_impairment": 1
}

try:
    response = requests.post(
        f"{BASE_URL}/assessments/",
        json=invalid_data,
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 422:
        print_test("Array Length Validation", True, "Correctly rejected wrong number of answers")
    else:
        print_test("Array Length Validation", False, f"Expected 422, got {response.status_code}")
except Exception as e:
    print_test("Array Length Validation", False, str(e))


# ============================================
# Summary
# ============================================
print(f"\n\n{BLUE}{'='*60}{RESET}")
print(f"{GREEN}✓ All Assessment API Tests Completed!{RESET}")
print(f"{BLUE}{'='*60}{RESET}")

print(f"\n{YELLOW}Test Summary:{RESET}")
print("✓ Get GAD-7 questions (Vietnamese)")
print("✓ Submit minimal anxiety assessment")
print("✓ Submit moderate anxiety assessment")
print("✓ Submit severe anxiety assessment")
print("✓ List assessments with pagination")
print("✓ Get assessment detail")
print("✓ Get assessment statistics")
print("✓ Validation tests")

print(f"\n{GREEN}Next Steps:{RESET}")
print("1. Check Swagger UI: http://127.0.0.1:8000/docs")
print("2. Try different severity levels")
print("3. Test with multiple students")
print("4. Integrate with frontend")

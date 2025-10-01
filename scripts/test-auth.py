"""
Test Authentication Endpoints
Tests: register, login, /me, refresh, invalid token
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1/auth"

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


# Test data
test_email = f"test.student.{datetime.now().timestamp()}@example.com"
test_password = "Student123!"
access_token = None

print(f"\n{BLUE}{'='*60}{RESET}")
print(f"{BLUE}Starting Authentication Tests{RESET}")
print(f"{BLUE}{'='*60}{RESET}")

# ============================================
# Test 1: Register New Student
# ============================================
print(f"\n\n{YELLOW}Test 1: Register New Student{RESET}")
register_data = {
    "email": test_email,
    "password": test_password,
    "full_name": "Test Student",
    "role": "student",
    "phone": "0123456789",
    "student_code": "SV2025001",
    "university": "Đại học Công nghệ",
    "major": "Khoa học máy tính",
    "year_of_study": 3
}

try:
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        if "access_token" in data and "user" in data:
            access_token = data["access_token"]
            user = data["user"]
            print_test(
                "Register Student",
                True,
                f"Created user: {user['email']} (role: {user['role']})"
            )
        else:
            print_test("Register Student", False, "Missing access_token or user in response")
    else:
        print_test("Register Student", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Register Student", False, str(e))


# ============================================
# Test 2: Register with Duplicate Email
# ============================================
print(f"\n\n{YELLOW}Test 2: Register with Duplicate Email (Should Fail){RESET}")
try:
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print_response(response)
    
    if response.status_code == 400:
        print_test("Duplicate Email Check", True, "Correctly rejected duplicate email")
    else:
        print_test("Duplicate Email Check", False, f"Expected 400, got {response.status_code}")
except Exception as e:
    print_test("Duplicate Email Check", False, str(e))


# ============================================
# Test 3: Login with Correct Credentials
# ============================================
print(f"\n\n{YELLOW}Test 3: Login with Correct Credentials{RESET}")
login_data = {
    "email": test_email,
    "password": test_password
}

try:
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            access_token = data["access_token"]  # Update token
            print_test("Login Success", True, "Successfully logged in")
        else:
            print_test("Login Success", False, "Missing access_token")
    else:
        print_test("Login Success", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Login Success", False, str(e))


# ============================================
# Test 4: Login with Wrong Password
# ============================================
print(f"\n\n{YELLOW}Test 4: Login with Wrong Password (Should Fail){RESET}")
wrong_login_data = {
    "email": test_email,
    "password": "WrongPassword123!"
}

try:
    response = requests.post(f"{BASE_URL}/login", json=wrong_login_data)
    print_response(response)
    
    if response.status_code == 401:
        print_test("Wrong Password Check", True, "Correctly rejected wrong password")
    else:
        print_test("Wrong Password Check", False, f"Expected 401, got {response.status_code}")
except Exception as e:
    print_test("Wrong Password Check", False, str(e))


# ============================================
# Test 5: Get Current User with Valid Token
# ============================================
print(f"\n\n{YELLOW}Test 5: Get Current User with Valid Token{RESET}")
headers = {"Authorization": f"Bearer {access_token}"}

try:
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if data["email"] == test_email and data["role"] == "student":
            print_test(
                "Get Current User",
                True,
                f"Retrieved user: {data['full_name']} ({data['email']})"
            )
            if "profile" in data and data["profile"]:
                print(f"\n{GREEN}Profile data found:{RESET}")
                print(json.dumps(data["profile"], indent=2, ensure_ascii=False))
        else:
            print_test("Get Current User", False, "User data mismatch")
    else:
        print_test("Get Current User", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Get Current User", False, str(e))


# ============================================
# Test 6: Get Current User with Invalid Token
# ============================================
print(f"\n\n{YELLOW}Test 6: Get Current User with Invalid Token (Should Fail){RESET}")
invalid_headers = {"Authorization": "Bearer invalid_token_12345"}

try:
    response = requests.get(f"{BASE_URL}/me", headers=invalid_headers)
    print_response(response)
    
    if response.status_code == 401:
        print_test("Invalid Token Check", True, "Correctly rejected invalid token")
    else:
        print_test("Invalid Token Check", False, f"Expected 401, got {response.status_code}")
except Exception as e:
    print_test("Invalid Token Check", False, str(e))


# ============================================
# Test 7: Register Parent Account
# ============================================
print(f"\n\n{YELLOW}Test 7: Register Parent Account{RESET}")
parent_email = f"test.parent.{datetime.now().timestamp()}@example.com"
parent_data = {
    "email": parent_email,
    "password": "Parent123!",
    "full_name": "Test Parent",
    "role": "parent",
    "phone": "0987654321"
}

try:
    response = requests.post(f"{BASE_URL}/register", json=parent_data)
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        if data["user"]["role"] == "parent":
            print_test("Register Parent", True, f"Created parent account: {data['user']['email']}")
        else:
            print_test("Register Parent", False, "Role mismatch")
    else:
        print_test("Register Parent", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Register Parent", False, str(e))


# ============================================
# Test 8: Register Counselor Account
# ============================================
print(f"\n\n{YELLOW}Test 8: Register Counselor Account{RESET}")
counselor_email = f"test.counselor.{datetime.now().timestamp()}@example.com"
counselor_data = {
    "email": counselor_email,
    "password": "Counselor123!",
    "full_name": "Test Counselor",
    "role": "counselor",
    "phone": "0111222333",
    "license_number": "CNS2025001",
    "specialization": "Tâm lý học lâm sàng",
    "years_of_experience": 5
}

try:
    response = requests.post(f"{BASE_URL}/register", json=counselor_data)
    print_response(response)
    
    if response.status_code == 201:
        data = response.json()
        if data["user"]["role"] == "counselor":
            print_test("Register Counselor", True, f"Created counselor account: {data['user']['email']}")
        else:
            print_test("Register Counselor", False, "Role mismatch")
    else:
        print_test("Register Counselor", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Register Counselor", False, str(e))


# ============================================
# Test 9: Weak Password Validation
# ============================================
print(f"\n\n{YELLOW}Test 9: Weak Password Validation (Should Fail){RESET}")
weak_password_data = {
    "email": f"weak.{datetime.now().timestamp()}@example.com",
    "password": "weak",  # Too short, no uppercase, no number
    "full_name": "Weak Password Test",
    "role": "student",
    "student_code": "SV2025999"
}

try:
    response = requests.post(f"{BASE_URL}/register", json=weak_password_data)
    print_response(response)
    
    if response.status_code == 422:
        print_test("Weak Password Validation", True, "Correctly rejected weak password")
    else:
        print_test("Weak Password Validation", False, f"Expected 422, got {response.status_code}")
except Exception as e:
    print_test("Weak Password Validation", False, str(e))


# ============================================
# Test 10: Logout
# ============================================
print(f"\n\n{YELLOW}Test 10: Logout{RESET}")
try:
    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_test("Logout", True, "Successfully logged out")
    else:
        print_test("Logout", False, f"Status code: {response.status_code}")
except Exception as e:
    print_test("Logout", False, str(e))


# ============================================
# Summary
# ============================================
print(f"\n\n{BLUE}{'='*60}{RESET}")
print(f"{GREEN}✓ All Authentication Tests Completed!{RESET}")
print(f"{BLUE}{'='*60}{RESET}")

print(f"\n{YELLOW}Test Accounts Created:{RESET}")
print(f"Student: {test_email}")
print(f"Parent: {parent_email}")
print(f"Counselor: {counselor_email}")
print(f"\n{YELLOW}Password for all:{RESET} [role]123! (e.g., Student123!, Parent123!)")

print(f"\n{GREEN}Next Steps:{RESET}")
print("1. Check Swagger UI: http://127.0.0.1:8000/docs")
print("2. Try the 'Authorize' button in Swagger with your token")
print("3. Test endpoints interactively")
print("4. Check database to see created users")

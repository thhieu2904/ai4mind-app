"""
Quick test - Submit one assessment
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "student1@example.com", "password": "password123"}
)

if login_response.status_code != 200:
    print("Login failed!")
    exit(1)

access_token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}

# Submit minimal anxiety assessment
print("\nSubmitting assessment...")
assessment_data = {
    "answers": [0, 0, 1, 0, 0, 1, 1],  # Total = 3
    "functional_impairment": 0,
    "notes": "Test assessment"
}

response = requests.post(
    f"{BASE_URL}/assessments/",
    json=assessment_data,
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json() if response.status_code != 500 else response.text, indent=2, ensure_ascii=False)}")

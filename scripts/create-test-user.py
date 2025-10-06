"""
Create a test student account for AI Chat testing
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def create_test_student():
    """Create test student account"""
    
    print("\n" + "="*60)
    print("  👤 CREATE TEST STUDENT ACCOUNT")
    print("="*60)
    
    # Test user data
    test_data = {
        "email": "test.aichat@ai4mind.com",
        "password": "TestAIChat123!",
        "full_name": "Test AI Chat Student",
        "role": "student",
        "date_of_birth": "2005-01-15",
        "gender": "Nam",
        "phone": "0987654321",
        "education_level": "Đại học",
        "grade": "2",
        "university": "ĐH Bách Khoa",
        "major": "Công nghệ thông tin"
    }
    
    print("\n📝 Creating account with:")
    print(f"   Email: {test_data['email']}")
    print(f"   Password: {test_data['password']}")
    print(f"   Role: {test_data['role']}")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=test_data
    )
    
    if response.status_code == 201:
        result = response.json()
        print("\n✅ Account created successfully!")
        print(f"   Token: {result['access_token'][:30]}...")
        
        print("\n" + "="*60)
        print("  ✅ SUCCESS! Use these credentials:")
        print("="*60)
        print(f"\nEmail:    {test_data['email']}")
        print(f"Password: {test_data['password']}")
        print("\n📝 Update in scripts/quick-test-ai-chat.py:")
        print(f'   TEST_EMAIL = "{test_data["email"]}"')
        print(f'   TEST_PASSWORD = "{test_data["password"]}"')
        print("\nThen run:")
        print("   python scripts/quick-test-ai-chat.py")
        print("="*60)
        
    elif response.status_code == 400:
        error = response.json()
        if "already registered" in str(error):
            print("\n✅ Account already exists!")
            print(f"   Email: {test_data['email']}")
            print(f"   Password: {test_data['password']}")
            print("\n   You can use these credentials for testing.")
        else:
            print(f"\n❌ Registration failed: {error}")
    else:
        print(f"\n❌ Registration failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    try:
        create_test_student()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend!")
        print("   Make sure backend is running:")
        print("   cd ai-service && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()

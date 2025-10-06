"""
Test assessments list endpoint to check if filtering works
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_list_assessments():
    """Test GET /api/v1/assessments/ with authentication"""
    
    # Step 1: Login to get token
    print("=== Step 1: Login ===")
    login_data = {
        "email": "thhieu2904das@gmail.com",
        "password": "Hieu02032001"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login successful!")
    print(f"Token: {access_token[:50]}...")
    
    # Step 2: Get assessments list
    print("\n=== Step 2: Get Assessments List ===")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/assessments/",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )
    
    if response.status_code != 200:
        print(f"❌ Get assessments failed: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    print(f"✅ Get assessments successful!")
    print(f"\nTotal assessments: {data['total']}")
    print(f"Page: {data['page']}/{data['total_pages']}")
    print(f"Items returned: {len(data['items'])}")
    
    print("\n=== Assessment Items ===")
    for item in data['items']:
        print(f"\nID: {item['id']}")
        print(f"  Student ID: {item['student_id']}")
        print(f"  Score: {item['total_score']}")
        print(f"  Severity: {item['severity_level']}")
        print(f"  Created: {item['created_at']}")
    
    # Step 3: Get stats for comparison
    print("\n=== Step 3: Get Stats for Comparison ===")
    response = requests.get(
        f"{BASE_URL}/api/v1/assessments/stats",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Stats endpoint:")
        print(f"  Total assessments: {stats['total_assessments']}")
        print(f"  Latest score: {stats['latest_score']}")
        print(f"  Average score: {stats['average_score']}")
        
        # Compare
        if data['total'] != stats['total_assessments']:
            print(f"\n⚠️  WARNING: Mismatch detected!")
            print(f"  List endpoint says: {data['total']} assessments")
            print(f"  Stats endpoint says: {stats['total_assessments']} assessments")
            print(f"  → Filtering bug confirmed! Backend not applying student_id filter.")
        else:
            print(f"\n✅ Counts match! Filtering working correctly.")
    else:
        print(f"❌ Get stats failed: {response.status_code}")

if __name__ == "__main__":
    test_list_assessments()

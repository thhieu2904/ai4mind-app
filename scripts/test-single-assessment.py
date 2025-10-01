"""
Test single assessment submission with Gemini analysis
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Login
print("=" * 60)
print("Login as student1...")
print("=" * 60)

login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "student1@example.com",
        "password": "Student123@"
    },
    headers={"Content-Type": "application/json"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Logged in successfully\n")

# Submit ONE assessment - moderate anxiety
print("=" * 60)
print("Submitting 1 Assessment (Moderate Anxiety - Score 12)")
print("=" * 60)

assessment_data = {
    "answers": [2, 2, 2, 1, 2, 2, 1],  # Score: 12
    "functional_impairment": 2,
    "notes": "Test Gemini AI integration - should get real analysis"
}

print(f"\n📊 Sending assessment: {json.dumps(assessment_data, indent=2)}")
print(f"\n🤖 Calling Gemini API for analysis...")

response = requests.post(
    f"{BASE_URL}/assessments/",
    json=assessment_data,
    headers=headers
)

print(f"\n📥 Response Status: {response.status_code}")

if response.status_code == 201:
    result = response.json()
    print("\n✅ SUCCESS! Assessment created\n")
    print("=" * 60)
    print("ANALYSIS (from Gemini):")
    print("=" * 60)
    print(result['analysis'])
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION:")
    print("=" * 60)
    
    # Check if it's fallback text
    fallback_text = "Điểm số của bạn cho thấy mức độ lo âu trung bình. Các triệu chứng này có thể ảnh hưởng đến cuộc sống hàng ngày của bạn."
    
    if result['analysis'] == fallback_text:
        print("⚠️  WARNING: Using FALLBACK text (Gemini API not called)")
        print("Possible reasons:")
        print("  - Rate limit hit (15 requests/minute)")
        print("  - API key issue")
        print("  - Network error")
    else:
        print("✅ SUCCESS: Got REAL Gemini AI analysis!")
        print(f"✅ Analysis length: {len(result['analysis'])} chars")
        print(f"✅ Recommendations count: {len(result['recommendations'])}")
        
        # Check for structured format markers
        if "PHÂN TÍCH:" in result['analysis'] or len(result['analysis']) > 200:
            print("✅ Analysis appears to be from Gemini AI (detailed content)")
        else:
            print("⚠️  Analysis is short - might still be fallback")
            
else:
    print(f"\n❌ FAILED: {response.status_code}")
    print(response.text)

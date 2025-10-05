"""
Quick test script for export endpoint
Run: python test_export.py
"""
import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000"
# Replace with a valid token from your browser localStorage
ACCESS_TOKEN = "your_token_here"

def test_export():
    """Test the export endpoint"""
    print("🧪 Testing Export Endpoint...")
    print(f"URL: {BASE_URL}/api/v1/export/user-data\n")
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/export/user-data",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Save file
            filename = "test_export.xlsx"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"\n✅ SUCCESS! File saved as: {filename}")
            print(f"📊 Please open {filename} to verify the data")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Is it running?")
        print("Start backend: cd ai-service && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    if ACCESS_TOKEN == "your_token_here":
        print("⚠️  Please update ACCESS_TOKEN in test_export.py")
        print("\nHow to get token:")
        print("1. Login to the app in browser")
        print("2. Open DevTools (F12) → Console")
        print("3. Run: localStorage.getItem('access_token')")
        print("4. Copy the token and paste it in this script\n")
        sys.exit(1)
    
    test_export()

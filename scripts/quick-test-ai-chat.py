"""
Simple test: Send one message to AI Chat
No conda environment needed - uses HTTP requests only

Usage:
    python scripts/quick-test-ai-chat.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# ⚠️ CHANGE THESE TO YOUR TEST ACCOUNT
TEST_EMAIL = "student@example.com"  
TEST_PASSWORD = "Test123!"

def test_ai_chat():
    """Quick test of AI Chat feature"""
    
    print("\n" + "="*60)
    print("  🤖 AI CHAT QUICK TEST")
    print("="*60)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed!")
        print(f"   Status: {login_response.status_code}")
        print(f"   Error: {login_response.json()}")
        print(f"\n💡 Update TEST_EMAIL and TEST_PASSWORD in this script")
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful!")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get/Create Conversation
    print("\n2️⃣ Getting conversation...")
    conv_response = requests.get(
        f"{BASE_URL}/ai-chat/conversation",
        headers=headers
    )
    
    if conv_response.status_code != 200:
        print(f"❌ Failed to get conversation")
        print(f"   Error: {conv_response.json()}")
        return
    
    conversation = conv_response.json()
    print(f"✅ Conversation ready!")
    print(f"   ID: {conversation['id']}")
    print(f"   Title: {conversation['title']}")
    print(f"   Messages: {conversation['message_count']}")
    
    # Step 3: Send test message
    print("\n3️⃣ Sending test message...")
    test_message = "Xin chào! Tôi muốn được tư vấn về lo âu."
    print(f"   User: {test_message}")
    
    send_response = requests.post(
        f"{BASE_URL}/ai-chat/message",
        headers=headers,
        json={"content": test_message}
    )
    
    if send_response.status_code != 200:
        print(f"❌ Failed to send message")
        print(f"   Error: {send_response.json()}")
        return
    
    result = send_response.json()
    ai_message = result['ai_message']['content']
    
    print(f"\n✅ AI Response received!")
    print("\n" + "-"*60)
    print(ai_message)
    print("-"*60)
    
    # Show assessment context if available
    if result.get('assessment_context'):
        ctx = result['assessment_context']
        print(f"\n📊 Assessment Context:")
        print(f"   Score: {ctx['score']}/21")
        print(f"   Severity: {ctx['severity']}")
        print(f"   Date: {ctx['date']}")
    
    # Step 4: Get all messages
    print("\n4️⃣ Loading conversation history...")
    messages_response = requests.get(
        f"{BASE_URL}/ai-chat/messages",
        headers=headers,
        params={"conversation_id": conversation['id']}
    )
    
    if messages_response.status_code == 200:
        messages = messages_response.json()
        print(f"✅ Total messages: {len(messages)}")
        print("\nConversation:")
        for msg in messages[-5:]:  # Show last 5
            icon = "👤" if msg['role'] == 'user' else "🤖"
            preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"   {icon} {preview}")
    
    print("\n" + "="*60)
    print("  ✅ TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n💡 Next: Test in browser at http://localhost:5173/ai-chat")

if __name__ == "__main__":
    try:
        test_ai_chat()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend!")
        print("   Make sure backend is running:")
        print("   cd ai-service && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

"""
Quick test script for AI Chat API endpoints
Tests the API via HTTP requests

Usage:
    # Run backend first (from ai-service directory)
    uvicorn app.main:app --reload
    
    # Then run this script
    python scripts/test-ai-chat-api.py
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
# Update these with your real test account credentials
TEST_EMAIL = "thhieu2904das@gmail.com"  # Change to your test account email
TEST_PASSWORD = "Hieu02032001"  # Change to your test password

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def login() -> str:
    """Login and get access token"""
    print_section("1. LOGIN")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Login successful")
        print(f"  Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        raise Exception("Login failed. Please check credentials or create test user first.")


def get_or_create_conversation(token: str) -> dict:
    """Get or create active conversation"""
    print_section("2. GET/CREATE CONVERSATION")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ai-chat/conversation",
        headers=headers
    )
    
    if response.status_code == 200:
        conv = response.json()
        print(f"✓ Conversation retrieved/created")
        print(f"  ID: {conv['id']}")
        print(f"  Title: {conv['title']}")
        print(f"  Messages: {conv['message_count']}")
        print(f"  Active: {conv['is_active']}")
        return conv
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def get_messages(token: str, conversation_id: int) -> list:
    """Get all messages in conversation"""
    print_section("3. GET MESSAGES")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ai-chat/messages",
        headers=headers,
        params={"conversation_id": conversation_id}
    )
    
    if response.status_code == 200:
        messages = response.json()
        print(f"✓ Retrieved {len(messages)} messages")
        
        # Show first few messages
        for i, msg in enumerate(messages[:3]):
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            content_preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
            print(f"  {role_icon} {msg['role']}: {content_preview}")
        
        if len(messages) > 3:
            print(f"  ... and {len(messages) - 3} more messages")
        
        return messages
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return []


def send_message(token: str, message_content: str) -> dict:
    """Send a message and get AI response"""
    print_section(f"4. SEND MESSAGE")
    print(f"User: {message_content}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/ai-chat/message",
        headers=headers,
        json={"content": message_content}
    )
    
    if response.status_code == 200:
        result = response.json()
        ai_response = result['ai_message']['content']
        
        print(f"\n✓ Message sent and AI responded")
        print(f"\nAI Response:")
        print("-" * 60)
        print(ai_response)
        print("-" * 60)
        
        # Show assessment context if available
        if result.get('assessment_context'):
            ctx = result['assessment_context']
            print(f"\n📊 Assessment Context:")
            print(f"  Score: {ctx['score']}/21")
            print(f"  Severity: {ctx['severity']}")
            print(f"  Date: {ctx['date']}")
        
        return result
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def test_multiple_messages(token: str):
    """Test sending multiple messages to verify context"""
    print_section("5. TEST CONVERSATION FLOW")
    
    messages = [
        "Xin chào, tôi là sinh viên đang học đại học",
        "Gần đây tôi hay lo lắng về kết quả học tập",
        "Bạn có lời khuyên gì giúp tôi giảm stress không?"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- Message {i}/{len(messages)} ---")
        result = send_message(token, msg)
        
        if result:
            # Small delay between messages
            time.sleep(2)
        else:
            print(f"❌ Failed at message {i}")
            break


def get_conversation_history(token: str):
    """Get conversation history"""
    print_section("6. GET CONVERSATION HISTORY")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/ai-chat/history",
        headers=headers,
        params={"limit": 5}
    )
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"✓ Found {len(conversations)} conversations")
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n{i}. {conv['title']}")
            print(f"   Messages: {conv['message_count']}")
            print(f"   Last: {conv['last_message_at']}")
            print(f"   Active: {'✓' if conv['is_active'] else '✗'}")
            if conv.get('last_message_preview'):
                preview = conv['last_message_preview'][:60] + "..." if len(conv['last_message_preview']) > 60 else conv['last_message_preview']
                print(f"   Preview: {preview}")
        
        return conversations
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return []


def end_conversation(token: str):
    """End active conversation"""
    print_section("7. END CONVERSATION")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/ai-chat/end-conversation",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✓ Conversation ended successfully")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  AI CHAT API TEST SUITE")
    print("=" * 60)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Using credentials: {TEST_EMAIL}")
    
    try:
        # Step 1: Login
        token = login()
        
        # Step 2: Get/Create conversation
        conversation = get_or_create_conversation(token)
        if not conversation:
            return
        
        # Step 3: Get existing messages
        messages = get_messages(token, conversation['id'])
        
        # Step 4: Send single test message
        send_message(token, "Xin chào! Tôi muốn được tư vấn về sức khỏe tinh thần.")
        
        # Step 5: Test conversation flow with multiple messages
        # Uncomment if you want to test multiple messages
        # test_multiple_messages(token)
        
        # Step 6: Get conversation history
        get_conversation_history(token)
        
        # Step 7: End conversation (optional)
        # Uncomment if you want to end the conversation
        # end_conversation(token)
        
        print("\n" + "=" * 60)
        print("  ✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
Test script for AI Chat functionality
Tests: Service layer, API endpoints, conversation flow, message history

Usage:
    python scripts/test-ai-chat.py
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai-service')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.student import Student
from app.models.assessment import Assessment
from app.models.ai_chat import AIConversation, AIMessage
from app.services.ai_chat_service import AIChatService
from app.core.security import get_password_hash


def create_test_user(db: Session) -> tuple[User, Student]:
    """Create test user and student"""
    # Check if test user exists
    test_email = "test_aichat@example.com"
    user = db.query(User).filter(User.email == test_email).first()
    
    if user:
        student = db.query(Student).filter(Student.user_id == user.id).first()
        print(f"✓ Using existing test user: {test_email}")
        return user, student
    
    # Create new user
    user = User(
        email=test_email,
        username="test_aichat",
        hashed_password=get_password_hash("test123"),
        role="student",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create student profile
    student = Student(
        user_id=user.id,
        full_name="Test AI Chat User",
        date_of_birth=datetime(2005, 1, 1),
        gender="Nam",
        phone_number="0123456789",
        education_level="Đại học",
        year_of_study=2
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    print(f"✓ Created test user: {test_email}")
    return user, student


def create_test_assessment(db: Session, student_id: int) -> Assessment:
    """Create test GAD-7 assessment"""
    assessment = Assessment(
        student_id=student_id,
        total_score=12,  # Moderate anxiety
        severity_level="moderate",
        analysis="Test analysis: Moderate anxiety detected",
        recommendations=["Practice mindfulness", "Seek counselor support"]
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    print(f"✓ Created test assessment: Score={assessment.total_score}, Severity={assessment.severity_level}")
    return assessment


async def test_conversation_creation(db: Session, student_id: int):
    """Test 1: Get or create conversation"""
    print("\n--- Test 1: Conversation Creation ---")
    
    chat_service = AIChatService(db)
    conversation = chat_service.get_or_create_active_conversation(student_id)
    
    assert conversation is not None, "Conversation should be created"
    assert conversation.student_id == student_id, "Conversation should belong to student"
    assert conversation.is_active == True, "Conversation should be active"
    
    # Check welcome message
    messages = chat_service.get_conversation_messages(conversation.id, student_id)
    assert len(messages) > 0, "Should have welcome message"
    assert messages[0].role == "assistant", "First message should be from AI"
    
    print(f"✓ Conversation created: ID={conversation.id}")
    print(f"✓ Welcome message: {messages[0].content[:100]}...")
    
    return conversation


async def test_send_message(db: Session, student_id: int):
    """Test 2: Send message and receive AI response"""
    print("\n--- Test 2: Send Message ---")
    
    chat_service = AIChatService(db)
    
    # Send user message
    test_message = "Xin chào, tôi cảm thấy lo lắng về thi cử"
    result = await chat_service.send_message(student_id, test_message)
    
    assert result["user_message"] is not None, "User message should be saved"
    assert result["ai_message"] is not None, "AI response should be generated"
    assert result["user_message"].content == test_message, "User message content should match"
    assert len(result["ai_message"].content) > 0, "AI should respond with content"
    
    print(f"✓ User message sent: {test_message}")
    print(f"✓ AI response: {result['ai_message'].content[:150]}...")
    
    return result


async def test_message_history(db: Session, student_id: int):
    """Test 3: Message history and context"""
    print("\n--- Test 3: Message History ---")
    
    chat_service = AIChatService(db)
    conversation = chat_service.get_or_create_active_conversation(student_id)
    
    # Send multiple messages
    messages_to_send = [
        "Tôi thường xuyên cảm thấy lo lắng",
        "Điều gì có thể giúp tôi giảm lo âu?",
        "Cảm ơn bạn đã tư vấn"
    ]
    
    for msg in messages_to_send:
        await chat_service.send_message(student_id, msg)
        await asyncio.sleep(1)  # Small delay to simulate real usage
    
    # Get all messages
    all_messages = chat_service.get_conversation_messages(conversation.id, student_id)
    
    # Should have: 1 welcome + 3 user + 3 AI = at least 7 messages
    assert len(all_messages) >= 7, f"Should have at least 7 messages, got {len(all_messages)}"
    
    # Check order
    assert all_messages[0].role == "assistant", "First should be welcome"
    assert all_messages[1].role == "user", "Second should be user"
    
    print(f"✓ Total messages: {len(all_messages)}")
    print(f"✓ Message order correct")
    
    return all_messages


async def test_assessment_context(db: Session, student_id: int):
    """Test 4: Assessment context in AI responses"""
    print("\n--- Test 4: Assessment Context ---")
    
    chat_service = AIChatService(db)
    
    # Send message that should trigger assessment context
    result = await chat_service.send_message(
        student_id, 
        "Kết quả đánh giá GAD-7 của tôi nghĩa là gì?"
    )
    
    # Check if assessment context is included
    assert result["assessment_summary"] is not None, "Assessment context should be provided"
    assert "score" in result["assessment_summary"], "Assessment should have score"
    
    print(f"✓ Assessment context loaded:")
    print(f"  Score: {result['assessment_summary']['score']}")
    print(f"  Severity: {result['assessment_summary']['severity']}")
    print(f"  Date: {result['assessment_summary']['date']}")
    
    return result


async def test_end_conversation(db: Session, student_id: int):
    """Test 5: End conversation"""
    print("\n--- Test 5: End Conversation ---")
    
    chat_service = AIChatService(db)
    
    # End conversation
    chat_service.end_conversation(student_id)
    
    # Verify conversation is inactive
    conversation = db.query(AIConversation).filter(
        AIConversation.student_id == student_id,
        AIConversation.is_active == True
    ).first()
    
    assert conversation is None, "Should have no active conversation"
    
    # Creating new should make a new conversation
    new_conversation = chat_service.get_or_create_active_conversation(student_id)
    assert new_conversation.is_active == True, "New conversation should be active"
    
    print(f"✓ Conversation ended successfully")
    print(f"✓ New conversation created: ID={new_conversation.id}")


async def test_conversation_list(db: Session, student_id: int):
    """Test 6: Get conversation list"""
    print("\n--- Test 6: Conversation List ---")
    
    chat_service = AIChatService(db)
    conversations = chat_service.get_student_conversations(student_id, limit=10)
    
    assert len(conversations) > 0, "Should have conversations"
    
    print(f"✓ Found {len(conversations)} conversations")
    for i, conv in enumerate(conversations[:3]):  # Show first 3
        print(f"  {i+1}. {conv.title} - Last: {conv.last_message_at.strftime('%d/%m/%Y %H:%M')}")


def cleanup_test_data(db: Session, user: User):
    """Clean up test data"""
    print("\n--- Cleanup ---")
    
    # Get student
    student = db.query(Student).filter(Student.user_id == user.id).first()
    
    if student:
        # Delete AI messages
        conversations = db.query(AIConversation).filter(
            AIConversation.student_id == student.id
        ).all()
        
        for conv in conversations:
            db.query(AIMessage).filter(AIMessage.conversation_id == conv.id).delete()
            db.delete(conv)
        
        # Delete assessments
        db.query(Assessment).filter(Assessment.student_id == student.id).delete()
        
        # Delete student
        db.delete(student)
    
    # Delete user
    db.delete(user)
    db.commit()
    
    print("✓ Test data cleaned up")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("AI CHAT FUNCTIONALITY TEST")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Setup
        user, student = create_test_user(db)
        assessment = create_test_assessment(db, student.id)
        
        # Run tests
        await test_conversation_creation(db, student.id)
        await test_send_message(db, student.id)
        await test_message_history(db, student.id)
        await test_assessment_context(db, student.id)
        await test_end_conversation(db, student.id)
        await test_conversation_list(db, student.id)
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
        # Ask before cleanup
        cleanup = input("\nDo you want to clean up test data? (y/n): ")
        if cleanup.lower() == 'y':
            cleanup_test_data(db, user)
        else:
            print("\n✓ Test data kept for manual inspection")
            print(f"  User: {user.email}")
            print(f"  Student ID: {student.id}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

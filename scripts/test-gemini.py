"""
Test Gemini API integration
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-service"))

from app.services.gemini_service import gemini_service


async def test_simple_chat():
    """Test simple chat"""
    print("\n" + "="*60)
    print("TEST 1: Simple Chat")
    print("="*60)
    
    message = "Xin chào! Bạn có thể giúp tôi như thế nào?"
    print(f"📤 User: {message}")
    
    try:
        response = await gemini_service.chat(message)
        print(f"🤖 Gemini: {response}")
        print("✅ Test passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_conversation_with_history():
    """Test chat with conversation history"""
    print("\n" + "="*60)
    print("TEST 2: Chat with History")
    print("="*60)
    
    history = [
        {"role": "user", "content": "Tôi là sinh viên năm 3 và đang cảm thấy stress"},
        {"role": "assistant", "content": "Chào bạn! Tôi hiểu stress học tập có thể ảnh hưởng nhiều. Bạn có thể chia sẻ cụ thể hơn về những gì đang khiến bạn stress không?"}
    ]
    
    new_message = "Tôi có quá nhiều deadline và không biết bắt đầu từ đâu"
    
    print("📜 Previous conversation:")
    for msg in history:
        role = "User" if msg["role"] == "user" else "Gemini"
        print(f"   {role}: {msg['content'][:60]}...")
    
    print(f"\n📤 User (new): {new_message}")
    
    try:
        response = await gemini_service.chat(new_message, history)
        print(f"🤖 Gemini: {response}")
        print("✅ Test passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_gad7_analysis():
    """Test GAD-7 assessment analysis"""
    print("\n" + "="*60)
    print("TEST 3: GAD-7 Analysis")
    print("="*60)
    
    # Moderate anxiety example (score = 12)
    answers = {
        1: 2,  # Cảm thấy lo lắng - Hơn một nửa số ngày
        2: 1,  # Không thể ngừng lo lắng - Vài ngày
        3: 2,  # Lo lắng quá nhiều - Hơn một nửa số ngày
        4: 2,  # Khó thư giãn - Hơn một nửa số ngày
        5: 1,  # Bồn chồn - Vài ngày
        6: 2,  # Dễ cáu gắt - Hơn một nửa số ngày
        7: 2   # Cảm thấy sợ hãi - Hơn một nửa số ngày
    }
    total_score = sum(answers.values())  # 12
    
    print(f"📊 GAD-7 Score: {total_score}/21")
    print("📝 Answers:")
    for q_id, score in answers.items():
        print(f"   Question {q_id}: {score}")
    
    try:
        result = await gemini_service.analyze_gad7(answers, total_score)
        print("\n🔍 Analysis:")
        print(result["analysis"])
        print("\n💡 Recommendations:")
        print(result["recommendations"])
        print("\n✅ Test passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_conversation_title():
    """Test conversation title generation"""
    print("\n" + "="*60)
    print("TEST 4: Generate Conversation Title")
    print("="*60)
    
    first_message = "Tôi đang cảm thấy rất lo lắng về kỳ thi cuối kỳ sắp tới và không biết làm sao để chuẩn bị tốt"
    print(f"📤 First message: {first_message}")
    
    try:
        title = await gemini_service.generate_conversation_title(first_message)
        print(f"📌 Generated title: {title}")
        print("✅ Test passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def main():
    """Run all tests"""
    print("="*60)
    print("🧪 AI4Mind - Gemini API Integration Tests")
    print("="*60)
    
    # Check API key
    from app.core.config import settings
    if not settings.GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in .env")
        print("   Please add your Gemini API key to .env file")
        return
    
    print(f"✅ Gemini API Key: {settings.GEMINI_API_KEY[:20]}...")
    print(f"✅ Model: {settings.GEMINI_MODEL}")
    
    # Run tests
    await test_simple_chat()
    await test_conversation_with_history()
    await test_gad7_analysis()
    await test_conversation_title()
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

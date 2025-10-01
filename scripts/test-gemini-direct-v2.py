"""
Direct test Gemini API với GAD-7 data
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-service'))

from app.services.gemini_service import gemini_service

async def test_gemini():
    """Test Gemini API directly"""
    print("=" * 60)
    print("Testing Gemini API for GAD-7 Analysis")
    print("=" * 60)
    
    # Test data: moderate anxiety (score 12)
    answers = {
        1: 2,  # Cảm thấy lo lắng: Hơn một nửa số ngày
        2: 2,  # Không thể kiểm soát: Hơn một nửa số ngày  
        3: 2,  # Lo lắng quá nhiều: Hơn một nửa số ngày
        4: 1,  # Khó thư giãn: Vài ngày
        5: 2,  # Bồn chồn: Hơn một nửa số ngày
        6: 2,  # Dễ khó chịu: Hơn một nửa số ngày
        7: 1   # Sợ hãi: Vài ngày
    }
    total_score = 12
    
    print(f"\n📊 Input:")
    print(f"   Total Score: {total_score}/21")
    print(f"   Severity: moderate anxiety")
    
    try:
        print("\n🤖 Calling Gemini API...")
        result = await gemini_service.analyze_gad7(answers=answers, total_score=total_score)
        
        print("\n✅ SUCCESS!")
        print("\n📝 Analysis:")
        print(f"   {result['analysis']}")
        
        print("\n💡 Recommendations:")
        recommendations = result['recommendations']
        if isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print(f"   {recommendations}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())

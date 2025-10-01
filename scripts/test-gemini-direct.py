"""
Direct test - Import and test GeminiService
"""
import sys
sys.path.append("D:\\job\\ai4mind-app\\ai-service")

from app.services.gemini_service import GeminiService

gemini = GeminiService()

# Test data
answers = [
    {"question": "Cảm thấy lo lắng", "answer": "Không có gì", "score": 0},
    {"question": "Không thể kiểm soát", "answer": "Không có gì", "score": 0},
    {"question": "Lo lắng quá nhiều", "answer": "Vài ngày", "score": 1},
    {"question": "Khó thư giãn", "answer": "Không có gì", "score": 0},
    {"question": "Bồn chồn", "answer": "Không có gì", "score": 0},
    {"question": "Dễ khó chịu", "answer": "Vài ngày", "score": 1},
    {"question": "Sợ hãi", "answer": "Vài ngày", "score": 1}
]

print("Testing Gemini GAD-7 analysis...")
try:
    result = gemini.analyze_gad7(answers, score=3)
    print("\n✓ Success!")
    print(f"\nAnalysis: {result.get('analysis', '')[:200]}...")
    print(f"\nRecommendations ({len(result.get('recommendations', []))}):")
    for i, rec in enumerate(result.get('recommendations', [])[:3], 1):
        print(f"  {i}. {rec}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

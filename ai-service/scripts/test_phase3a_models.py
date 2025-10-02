"""
Test script for Phase 3a: Gender field and Voice Analysis models
Tests:
1. Student model with gender field
2. Voice Analysis model relationships
3. Database connectivity
4. Schema validation
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import json

# Import models and schemas
from app.core.config import settings
from app.models import Base, User, Student, VoiceAnalysis
from app.schemas import StudentCreate, GenderEnum, VoiceAnalysisResponse

# Setup database
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def test_database_connection():
    """Test 1: Database connection"""
    print("\n" + "="*60)
    print("TEST 1: Database Connection")
    print("="*60)
    
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version[:50]}...")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_student_gender_field():
    """Test 2: Student model with gender field"""
    print("\n" + "="*60)
    print("TEST 2: Student Model - Gender Field")
    print("="*60)
    
    try:
        db = SessionLocal()
        
        # Check if gender column exists in database
        result = db.execute(text("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'students' AND column_name = 'gender'
        """))
        gender_col = result.fetchone()
        
        if gender_col:
            print(f"✅ Gender column exists in database:")
            print(f"   - Column: {gender_col[0]}")
            print(f"   - Type: {gender_col[1]}")
            print(f"   - Default: {gender_col[2]}")
        else:
            print("❌ Gender column NOT found in students table")
            db.close()
            return False
        
        # Check gender constraint
        result = db.execute(text("""
            SELECT constraint_name, check_clause
            FROM information_schema.check_constraints
            WHERE constraint_name LIKE '%gender%'
        """))
        constraint = result.fetchone()
        
        if constraint:
            print(f"✅ Gender check constraint exists:")
            print(f"   - Name: {constraint[0]}")
            print(f"   - Check: {constraint[1]}")
        
        # Test GenderEnum schema
        print("\n✅ GenderEnum values:")
        for gender in GenderEnum:
            print(f"   - {gender.value}")
        
        # Test StudentCreate schema with gender
        student_data = StudentCreate(
            student_code="TEST001",
            gender=GenderEnum.FEMALE,
            university="Test University"
        )
        print(f"\n✅ StudentCreate schema validated:")
        print(f"   - Student code: {student_data.student_code}")
        print(f"   - Gender: {student_data.gender.value}")
        print(f"   - University: {student_data.university}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_voice_analysis_model():
    """Test 3: VoiceAnalysis model structure"""
    print("\n" + "="*60)
    print("TEST 3: VoiceAnalysis Model")
    print("="*60)
    
    try:
        db = SessionLocal()
        
        # Check if voice_analyses table exists
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'voice_analyses'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        if columns:
            print(f"✅ voice_analyses table exists with {len(columns)} columns:")
            
            # Check critical columns
            critical_cols = ['id', 'student_id', 'assessment_id', 'audio_file_path', 
                           'gender_used', 'audio_features', 'detected_emotions',
                           'normalized_features', 'processing_status', 'created_at']
            
            found_cols = [col[0] for col in columns]
            
            for col_name in critical_cols:
                if col_name in found_cols:
                    col_info = [c for c in columns if c[0] == col_name][0]
                    print(f"   ✓ {col_info[0]:25} {col_info[1]:20} nullable={col_info[2]}")
                else:
                    print(f"   ✗ {col_name:25} MISSING")
        else:
            print("❌ voice_analyses table NOT found")
            db.close()
            return False
        
        # Test relationships
        print("\n✅ Checking model relationships...")
        
        # Check Student -> VoiceAnalysis relationship
        if hasattr(Student, 'voice_analyses'):
            print("   ✓ Student.voice_analyses relationship exists")
        else:
            print("   ✗ Student.voice_analyses relationship MISSING")
        
        # Check VoiceAnalysis -> Student relationship  
        if hasattr(VoiceAnalysis, 'student'):
            print("   ✓ VoiceAnalysis.student relationship exists")
        else:
            print("   ✗ VoiceAnalysis.student relationship MISSING")
        
        # Check VoiceAnalysis -> Assessment relationship
        if hasattr(VoiceAnalysis, 'assessment'):
            print("   ✓ VoiceAnalysis.assessment relationship exists")
        else:
            print("   ✗ VoiceAnalysis.assessment relationship MISSING")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_voice_analysis_schemas():
    """Test 4: VoiceAnalysis Pydantic schemas"""
    print("\n" + "="*60)
    print("TEST 4: VoiceAnalysis Schemas")
    print("="*60)
    
    try:
        from app.schemas import (
            AudioFeatures, EmotionScores, TextAnalysis, 
            PsychologicalMarkers, NormalizedFeatures,
            VoiceAnalysisCreate, VoiceAnalysisResponse
        )
        
        # Test AudioFeatures
        audio_features = AudioFeatures(
            pitch_mean=210.5,
            pitch_std=45.2,
            energy_mean=0.65,
            speech_rate="fast",
            pause_count=12,
            voice_stability=0.45
        )
        print("✅ AudioFeatures schema validated:")
        print(f"   - Pitch mean: {audio_features.pitch_mean} Hz")
        print(f"   - Speech rate: {audio_features.speech_rate}")
        print(f"   - Voice stability: {audio_features.voice_stability}")
        
        # Test EmotionScores
        emotion_scores = EmotionScores(
            anxiety=0.75,
            sadness=0.60,
            anger=0.10,
            neutral=0.20
        )
        print("\n✅ EmotionScores schema validated:")
        print(f"   - Anxiety: {emotion_scores.anxiety}")
        print(f"   - Sadness: {emotion_scores.sadness}")
        print(f"   - Dominant: anxiety (0.75)")
        
        # Test NormalizedFeatures
        normalized = NormalizedFeatures(
            pitch_z_score=1.5,
            pitch_deviation=1.5,
            pitch_variability=0.25,
            energy_relative=0.68,
            gender_baseline="female"
        )
        print("\n✅ NormalizedFeatures schema validated:")
        print(f"   - Pitch Z-score: {normalized.pitch_z_score}")
        print(f"   - Gender baseline: {normalized.gender_baseline}")
        print(f"   - Pitch deviation: {normalized.pitch_deviation} SD")
        
        # Test PsychologicalMarkers
        psych_markers = PsychologicalMarkers(
            negative_words=15,
            positive_words=3,
            self_reference=8,
            uncertainty=6
        )
        print("\n✅ PsychologicalMarkers schema validated:")
        print(f"   - Negative words: {psych_markers.negative_words}")
        print(f"   - Positive words: {psych_markers.positive_words}")
        print(f"   - Self-reference: {psych_markers.self_reference}")
        
        print("\n✅ All schemas validated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 3A: GENDER FIELD & VOICE ANALYSIS MODELS - TEST SUITE")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {settings.DATABASE_URL[:50]}...")
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Student Gender Field", test_student_gender_field()))
    results.append(("VoiceAnalysis Model", test_voice_analysis_model()))
    results.append(("VoiceAnalysis Schemas", test_voice_analysis_schemas()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Gender field successfully added to Student model")
        print("✅ VoiceAnalysis model ready for use")
        print("✅ All schemas validated")
        print("\n📋 Next steps:")
        print("   1. Implement voice-service microservice")
        print("   2. Add audio processing with librosa")
        print("   3. Integrate Whisper for speech-to-text")
        print("   4. Build emotion detection with gender normalization")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        print("Please fix the issues before proceeding.")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

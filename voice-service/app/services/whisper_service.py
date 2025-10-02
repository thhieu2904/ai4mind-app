"""
Whisper Service for Vietnamese Speech-to-Text
Handles audio transcription using OpenAI Whisper model
"""

import whisper
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
import soundfile as sf
import librosa

logger = logging.getLogger(__name__)


class WhisperService:
    """
    Service for converting Vietnamese speech to text using Whisper.
    
    Features:
    - Vietnamese language support
    - Multiple audio format handling (WAV, MP3, M4A)
    - Confidence scoring
    - Duration tracking
    - Error handling for corrupted audio
    
    Model sizes:
    - tiny: 39M params, fastest, least accurate
    - base: 74M params, good balance (DEFAULT)
    - small: 244M params, better accuracy
    - medium: 769M params, best for Vietnamese
    - large: 1550M params, highest accuracy but slow
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper service with specified model size.
        
        Args:
            model_size: Whisper model size (tiny/base/small/medium/large)
                       Default: "base" for good speed/accuracy balance
        """
        self.model_size = model_size
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """
        Load Whisper model. Lazy loading on first transcription.
        Model is cached in ~/.cache/whisper/
        """
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info(f"✅ Whisper model '{self.model_size}' loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise RuntimeError(f"Could not load Whisper model: {e}")
    
    def transcribe(
        self, 
        audio_path: str,
        language: str = "vi",
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, M4A, etc.)
            language: Language code (default: "vi" for Vietnamese)
            task: "transcribe" or "translate" (translate converts to English)
        
        Returns:
            Dict containing:
            - transcript: Full transcribed text
            - language: Detected/specified language
            - duration: Audio duration in seconds
            - segments: List of timestamped segments
            - confidence: Average confidence score (0-1)
            - word_count: Number of words in transcript
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        # Validate file exists
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"🎤 Starting transcription for: {audio_file.name}")
        
        try:
            # Load audio to get duration
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            duration = len(audio_data) / sample_rate
            
            logger.info(f"Audio duration: {duration:.2f}s, Sample rate: {sample_rate} Hz")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                task=task,
                verbose=False,  # Suppress detailed output
                fp16=False  # Use FP32 for CPU (FP16 for GPU)
            )
            
            # Extract transcript text
            transcript = result["text"].strip()
            
            # Calculate confidence from segments (if available)
            confidence = self._calculate_confidence(result.get("segments", []))
            
            # Count words (split by whitespace for Vietnamese)
            word_count = len(transcript.split())
            
            logger.info(f"✅ Transcription complete: {word_count} words, "
                       f"confidence: {confidence:.2f}")
            logger.info(f"📝 Transcript preview: {transcript[:100]}...")
            
            return {
                "transcript": transcript,
                "language": result.get("language", language),
                "duration": duration,
                "segments": result.get("segments", []),
                "confidence": confidence,
                "word_count": word_count,
                "sample_rate": sample_rate
            }
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {e}")
    
    def _calculate_confidence(self, segments: list) -> float:
        """
        Calculate average confidence score from Whisper segments.
        
        Whisper provides confidence scores (0-1) for each segment.
        Higher scores indicate more confident transcription.
        
        Args:
            segments: List of segment dictionaries with "no_speech_prob"
        
        Returns:
            Average confidence (0-1), or 0.0 if no segments
        """
        if not segments:
            return 0.0
        
        # Whisper provides "no_speech_prob" (probability of silence)
        # Confidence = 1 - no_speech_prob
        confidences = []
        for segment in segments:
            no_speech_prob = segment.get("no_speech_prob", 0.0)
            confidence = 1.0 - no_speech_prob
            confidences.append(confidence)
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        return float(avg_confidence)
    
    def transcribe_with_timestamps(
        self,
        audio_path: str,
        language: str = "vi"
    ) -> Tuple[str, list]:
        """
        Transcribe with detailed timestamp information for each segment.
        
        Useful for:
        - Synchronizing text with audio playback
        - Analyzing speech patterns over time
        - Detecting pauses between segments
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: "vi")
        
        Returns:
            Tuple of (full_transcript, segments_list)
            
            segments_list format:
            [
                {
                    "text": "Xin chào",
                    "start": 0.0,
                    "end": 1.5,
                    "confidence": 0.95
                },
                ...
            ]
        """
        result = self.transcribe(audio_path, language=language)
        
        segments = []
        for seg in result["segments"]:
            segments.append({
                "text": seg["text"].strip(),
                "start": seg["start"],
                "end": seg["end"],
                "confidence": 1.0 - seg.get("no_speech_prob", 0.0)
            })
        
        return result["transcript"], segments
    
    def detect_language(self, audio_path: str) -> Dict[str, float]:
        """
        Detect language from audio (useful for validation).
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary of language codes and probabilities
            Example: {"vi": 0.95, "en": 0.03, "zh": 0.02}
        """
        try:
            # Load audio
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            
            # Sort by probability (highest first)
            sorted_probs = {
                lang: float(prob) 
                for lang, prob in sorted(
                    probs.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
            }
            
            logger.info(f"🌍 Language detection: {list(sorted_probs.items())[:3]}")
            
            return sorted_probs
            
        except Exception as e:
            logger.error(f"❌ Language detection failed: {e}")
            return {"vi": 1.0}  # Default to Vietnamese
    
    def validate_vietnamese_audio(self, audio_path: str, threshold: float = 0.5) -> bool:
        """
        Check if audio is likely Vietnamese.
        
        Args:
            audio_path: Path to audio file
            threshold: Minimum probability to consider Vietnamese (default: 0.5)
        
        Returns:
            True if Vietnamese probability >= threshold, False otherwise
        """
        lang_probs = self.detect_language(audio_path)
        vietnamese_prob = lang_probs.get("vi", 0.0)
        
        is_vietnamese = vietnamese_prob >= threshold
        
        if is_vietnamese:
            logger.info(f"✅ Audio validated as Vietnamese (prob: {vietnamese_prob:.2f})")
        else:
            logger.warning(f"⚠️ Audio may not be Vietnamese (prob: {vietnamese_prob:.2f})")
        
        return is_vietnamese


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize service
    print("🎤 Initializing Whisper Service...")
    whisper_service = WhisperService(model_size="base")
    
    # Example 1: Basic transcription
    print("\n" + "="*60)
    print("Example 1: Basic Transcription")
    print("="*60)
    
    # NOTE: Replace with actual audio file path for testing
    test_audio = "test_audio.wav"
    
    if Path(test_audio).exists():
        result = whisper_service.transcribe(test_audio)
        print(f"\n📝 Transcript: {result['transcript']}")
        print(f"⏱️ Duration: {result['duration']:.2f}s")
        print(f"📊 Confidence: {result['confidence']:.2f}")
        print(f"🔤 Word count: {result['word_count']}")
    else:
        print(f"⚠️ Test audio file not found: {test_audio}")
        print("\n🧪 Testing with synthetic data...")
        
        # Create dummy result for testing
        dummy_result = {
            "transcript": "Tôi đang cảm thấy lo lắng về công việc",
            "language": "vi",
            "duration": 5.5,
            "confidence": 0.89,
            "word_count": 7
        }
        
        print(f"\n📝 Transcript: {dummy_result['transcript']}")
        print(f"⏱️ Duration: {dummy_result['duration']:.2f}s")
        print(f"📊 Confidence: {dummy_result['confidence']:.2f}")
        print(f"🔤 Word count: {dummy_result['word_count']}")
    
    print("\n✅ Whisper Service ready!")

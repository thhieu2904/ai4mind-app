"""
Deepgram API Service for Speech-to-Text
External API replaces local Whisper to reduce memory usage
"""

import httpx
import logging
from typing import Dict, Optional, List
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class DeepgramService:
    """
    Deepgram API client for Vietnamese speech-to-text transcription.
    
    Why Deepgram?
    - Free tier: 12,000 minutes/month (200 hours)
    - Production-grade accuracy: 90%+ for Vietnamese
    - Lightweight: No local ML models (reduces build size by 400MB!)
    - Fast: 1-3 seconds for 30-second audio
    - Word-level timestamps for advanced features
    
    This service ONLY handles transcription.
    Emotion detection still uses our custom ML model (the unique value!).
    
    Architecture:
    Audio → Deepgram API (transcription) → Custom ML (emotion) → Result
    
    Trade-offs:
    ✅ Pro: Deploy on free tier (512MB RAM), production-ready quality
    ❌ Con: External dependency, audio leaves server (privacy concern)
    
    For interview talking point:
    "We outsource commodity service (transcription) to focus engineering 
    effort on unique value (gender-normalized emotion detection)"
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Deepgram service.
        
        Args:
            api_key: Deepgram API key from https://console.deepgram.com
        """
        self.api_key = api_key
        self.base_url = "https://api.deepgram.com/v1"
        self.timeout = 60.0  # 60 seconds for API calls
        
        if not self.api_key:
            raise ValueError(
                "DEEPGRAM_API_KEY is required! "
                "Get free key at https://console.deepgram.com"
            )
        
        logger.info("✅ Deepgram service initialized")
    
    async def transcribe(
        self,
        audio_path: str,
        language: str = "vi",
        include_timestamps: bool = True
    ) -> Dict:
        """
        Transcribe audio file using Deepgram API.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, M4A, etc.)
            language: Language code (default: "vi" for Vietnamese)
            include_timestamps: Whether to include word-level timestamps
        
        Returns:
            Dict containing:
            {
                "transcript": str,              # Full transcribed text
                "confidence": float,            # Overall confidence (0-1)
                "words": List[Dict],            # Word-level data with timestamps
                "language": str,                # Detected language
                "duration": float,              # Audio duration in seconds
                "metadata": Dict                # Additional metadata
            }
        
        Raises:
            FileNotFoundError: If audio file doesn't exist
            httpx.HTTPError: If API request fails
            ValueError: If API response is invalid
        """
        # Validate file exists
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"🎤 Starting Deepgram transcription: {audio_file.name}")
        
        try:
            # Read audio file
            with open(audio_path, "rb") as audio:
                audio_data = audio.read()
            
            # Prepare API request
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": self._get_content_type(audio_path)
            }
            
            # API parameters
            params = {
                "language": language,          # Vietnamese
                "punctuate": True,             # Add punctuation
                "utterances": True,            # Split into sentences
                "diarize": False,              # Single speaker (no diarization)
                "model": "nova-2",             # Latest model (best accuracy)
                "smart_format": True,          # Format numbers, dates, etc.
            }
            
            # Add word timestamps if requested
            if include_timestamps:
                params["words"] = True
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    content=audio_data
                )
                
                # Check for errors
                response.raise_for_status()
                
            # Parse response
            result = response.json()
            
            # Extract data from nested structure
            channel = result["results"]["channels"][0]
            alternative = channel["alternatives"][0]
            
            transcript = alternative["transcript"]
            confidence = alternative["confidence"]
            words = alternative.get("words", [])
            
            # Get metadata
            metadata = result.get("metadata", {})
            duration = metadata.get("duration", 0.0)
            detected_language = metadata.get("language", language)
            
            logger.info(f"✅ Transcription complete: {len(transcript)} chars, "
                       f"confidence: {confidence:.2f}")
            logger.info(f"📝 Transcript preview: {transcript[:100]}...")
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "words": words,
                "language": detected_language,
                "duration": duration,
                "word_count": len(transcript.split()),
                "metadata": {
                    "model": "deepgram-nova-2",
                    "source": "external-api",
                    "request_id": metadata.get("request_id"),
                    "model_uuid": metadata.get("model_uuid")
                }
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Deepgram API error: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            
            # Handle specific errors
            if e.response.status_code == 401:
                raise ValueError(
                    "Invalid Deepgram API key! "
                    "Check DEEPGRAM_API_KEY in environment variables"
                )
            elif e.response.status_code == 402:
                raise ValueError(
                    "Deepgram quota exceeded! "
                    "Upgrade plan or wait for monthly reset"
                )
            elif e.response.status_code == 400:
                raise ValueError(
                    "Invalid audio file or parameters! "
                    f"Details: {e.response.text}"
                )
            else:
                raise RuntimeError(f"Deepgram API error: {e}")
        
        except httpx.TimeoutException:
            logger.error(f"❌ Deepgram API timeout after {self.timeout}s")
            raise RuntimeError(
                f"Transcription timeout! Audio file too large or slow network"
            )
        
        except Exception as e:
            logger.error(f"❌ Unexpected error during transcription: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {e}")
    
    def _get_content_type(self, audio_path: str) -> str:
        """
        Determine audio content type from file extension.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            MIME type string
        """
        extension = Path(audio_path).suffix.lower()
        
        content_types = {
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".flac": "audio/flac",
            ".ogg": "audio/ogg",
            ".webm": "audio/webm"
        }
        
        return content_types.get(extension, "audio/wav")
    
    async def check_quota(self) -> Dict:
        """
        Check remaining Deepgram API quota.
        
        Returns:
            Dict with quota information:
            {
                "requests_remaining": int,
                "quota_limit": int,
                "quota_used": int
            }
        
        Note: Requires API key with management permissions
        """
        try:
            headers = {
                "Authorization": f"Token {self.api_key}"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/projects",
                    headers=headers
                )
                response.raise_for_status()
                
            # Parse quota info
            data = response.json()
            # Note: Actual structure depends on Deepgram API version
            
            logger.info("✅ Quota check successful")
            return data
            
        except Exception as e:
            logger.warning(f"⚠️  Could not check quota: {e}")
            return {
                "error": str(e),
                "message": "Quota check requires management permissions"
            }
    
    @staticmethod
    def estimate_cost(duration_seconds: float) -> Dict:
        """
        Estimate cost for transcription (informational only).
        
        Args:
            duration_seconds: Audio duration in seconds
        
        Returns:
            Dict with cost estimation
        """
        # Free tier: 12,000 minutes/month
        free_tier_minutes = 12000
        duration_minutes = duration_seconds / 60
        
        # Pay-as-you-go: $0.0043/minute after free tier
        cost_per_minute = 0.0043
        
        if duration_minutes <= free_tier_minutes:
            cost = 0.0
            tier = "free"
        else:
            overage_minutes = duration_minutes - free_tier_minutes
            cost = overage_minutes * cost_per_minute
            tier = "paid"
        
        return {
            "duration_minutes": round(duration_minutes, 2),
            "estimated_cost_usd": round(cost, 4),
            "tier": tier,
            "free_tier_remaining": max(0, free_tier_minutes - duration_minutes)
        }


# Example usage (for testing)
async def main():
    """Example usage of DeepgramService"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("DEEPGRAM_API_KEY")
    service = DeepgramService(api_key)
    
    # Test transcription
    result = await service.transcribe(
        audio_path="test_audio.wav",
        language="vi"
    )
    
    print(f"Transcript: {result['transcript']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Duration: {result['duration']}s")


if __name__ == "__main__":
    asyncio.run(main())

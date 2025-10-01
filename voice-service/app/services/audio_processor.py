"""
Audio Processing Service

Extracts audio features using librosa for emotion detection.
"""
import librosa
import numpy as np
from typing import Dict, Optional, Tuple
import soundfile as sf
from pathlib import Path

from app.core.constants import SPEECH_RATE_THRESHOLDS


class AudioProcessor:
    """
    Processes audio files to extract features for emotion analysis.
    
    Features extracted:
    - Pitch (F0): fundamental frequency
    - Energy/Intensity: RMS energy
    - Speech rate: syllables per second
    - Pauses: silence detection
    - Voice stability: pitch variance
    - MFCCs: mel-frequency cepstral coefficients (optional)
    """
    
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio processor.
        
        Args:
            sample_rate: Target sample rate for processing
        """
        self.sample_rate = sample_rate
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file.
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio, sr = librosa.load(file_path, sr=self.sample_rate)
            return audio, sr
        except Exception as e:
            raise ValueError(f"Failed to load audio file: {str(e)}")
    
    def extract_pitch(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Extract pitch features using librosa.pyin().
        
        Args:
            audio: Audio signal
            sr: Sample rate
        
        Returns:
            Dictionary with pitch statistics
        """
        # Extract pitch using probabilistic YIN algorithm
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),  # ~65 Hz
            fmax=librosa.note_to_hz('C7'),  # ~2093 Hz
            sr=sr
        )
        
        # Remove NaN values (unvoiced parts)
        f0_clean = f0[~np.isnan(f0)]
        
        if len(f0_clean) == 0:
            return {
                "pitch_mean": 0.0,
                "pitch_std": 0.0,
                "pitch_min": 0.0,
                "pitch_max": 0.0,
                "pitch_range": 0.0,
                "voiced_ratio": 0.0
            }
        
        return {
            "pitch_mean": float(np.mean(f0_clean)),
            "pitch_std": float(np.std(f0_clean)),
            "pitch_min": float(np.min(f0_clean)),
            "pitch_max": float(np.max(f0_clean)),
            "pitch_range": float(np.max(f0_clean) - np.min(f0_clean)),
            "voiced_ratio": float(np.sum(voiced_flag) / len(voiced_flag))
        }
    
    def extract_energy(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract energy/intensity features using RMS.
        
        Args:
            audio: Audio signal
        
        Returns:
            Dictionary with energy statistics
        """
        # Root Mean Square energy
        rms = librosa.feature.rms(y=audio)[0]
        
        return {
            "energy_mean": float(np.mean(rms)),
            "energy_std": float(np.std(rms)),
            "energy_max": float(np.max(rms)),
            "energy_min": float(np.min(rms))
        }
    
    def calculate_speech_rate(
        self,
        audio: np.ndarray,
        sr: int
    ) -> Dict[str, any]:
        """
        Estimate speech rate using onset detection.
        
        Args:
            audio: Audio signal
            sr: Sample rate
        
        Returns:
            Dictionary with speech rate info
        """
        # Detect onsets (roughly corresponds to syllables)
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        onsets = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            units='time'
        )
        
        # Calculate duration
        duration = librosa.get_duration(y=audio, sr=sr)
        
        # Syllables per second
        if duration > 0:
            syllables_per_sec = len(onsets) / duration
        else:
            syllables_per_sec = 0
        
        # Categorize speech rate
        if syllables_per_sec < SPEECH_RATE_THRESHOLDS["slow"]:
            rate_category = "slow"
        elif syllables_per_sec > SPEECH_RATE_THRESHOLDS["fast"]:
            rate_category = "fast"
        else:
            rate_category = "normal"
        
        return {
            "syllables_per_second": float(syllables_per_sec),
            "speech_rate": rate_category,
            "onset_count": len(onsets),
            "duration_seconds": float(duration)
        }
    
    def detect_pauses(
        self,
        audio: np.ndarray,
        sr: int,
        threshold: float = 0.02
    ) -> Dict[str, any]:
        """
        Detect pauses/silences in speech.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            threshold: Energy threshold for silence
        
        Returns:
            Dictionary with pause information
        """
        # Calculate frame-wise energy
        rms = librosa.feature.rms(y=audio)[0]
        
        # Find silent frames
        silent_frames = rms < threshold
        
        # Count pause segments
        pause_count = 0
        in_pause = False
        
        for is_silent in silent_frames:
            if is_silent and not in_pause:
                pause_count += 1
                in_pause = True
            elif not is_silent:
                in_pause = False
        
        # Calculate total pause duration
        frame_duration = len(audio) / sr / len(rms)
        pause_duration = np.sum(silent_frames) * frame_duration
        
        return {
            "pause_count": pause_count,
            "pause_duration_seconds": float(pause_duration),
            "pause_ratio": float(np.sum(silent_frames) / len(silent_frames))
        }
    
    def calculate_voice_stability(self, pitch_std: float, pitch_mean: float) -> float:
        """
        Calculate voice stability score.
        
        Args:
            pitch_std: Standard deviation of pitch
            pitch_mean: Mean pitch
        
        Returns:
            Stability score (0-1), where 1 is very stable
        """
        if pitch_mean == 0:
            return 0.0
        
        # Coefficient of variation
        cv = pitch_std / pitch_mean
        
        # Convert to stability score (inverse of CV, capped at 1)
        stability = 1.0 / (1.0 + cv)
        
        return float(stability)
    
    def extract_mfccs(
        self,
        audio: np.ndarray,
        sr: int,
        n_mfcc: int = 13
    ) -> Dict[str, list]:
        """
        Extract MFCCs (Mel-Frequency Cepstral Coefficients).
        
        Args:
            audio: Audio signal
            sr: Sample rate
            n_mfcc: Number of MFCCs to extract
        
        Returns:
            Dictionary with MFCC statistics
        """
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        
        return {
            "mfcc_mean": [float(x) for x in np.mean(mfccs, axis=1)],
            "mfcc_std": [float(x) for x in np.std(mfccs, axis=1)]
        }
    
    def process_audio_file(
        self,
        file_path: str,
        extract_mfcc: bool = False
    ) -> Dict:
        """
        Extract all audio features from file.
        
        Args:
            file_path: Path to audio file
            extract_mfcc: Whether to extract MFCCs (optional, expensive)
        
        Returns:
            Dictionary with all extracted features
        """
        # Load audio
        audio, sr = self.load_audio(file_path)
        
        # Extract features
        pitch_features = self.extract_pitch(audio, sr)
        energy_features = self.extract_energy(audio)
        speech_rate_features = self.calculate_speech_rate(audio, sr)
        pause_features = self.detect_pauses(audio, sr)
        
        # Calculate voice stability
        voice_stability = self.calculate_voice_stability(
            pitch_features["pitch_std"],
            pitch_features["pitch_mean"]
        )
        
        # Combine all features
        features = {
            **pitch_features,
            **energy_features,
            **speech_rate_features,
            **pause_features,
            "voice_stability": voice_stability
        }
        
        # Optionally extract MFCCs
        if extract_mfcc:
            mfcc_features = self.extract_mfccs(audio, sr)
            features.update(mfcc_features)
        
        return features
    
    def get_audio_duration(self, file_path: str) -> float:
        """
        Get audio file duration in seconds.
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Duration in seconds
        """
        audio, sr = self.load_audio(file_path)
        return float(librosa.get_duration(y=audio, sr=sr))
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get audio file size in bytes.
        
        Args:
            file_path: Path to audio file
        
        Returns:
            File size in bytes
        """
        return Path(file_path).stat().st_size


# Example usage
if __name__ == "__main__":
    processor = AudioProcessor()
    
    # Example: Process a sample audio file (replace with actual file)
    print("\n=== Audio Processor Test ===")
    print("Note: Need actual audio file to test")
    print("\nFeatures that will be extracted:")
    print("  • Pitch (mean, std, min, max, range)")
    print("  • Energy (mean, std, max, min)")
    print("  • Speech rate (syllables/sec, category)")
    print("  • Pauses (count, duration, ratio)")
    print("  • Voice stability (0-1 score)")
    print("  • MFCCs (optional)")

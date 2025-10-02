"""
Emotion Classifier for Voice Analysis
Detects anxiety, sadness, anger from normalized audio features
"""

import numpy as np
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmotionScore:
    """Represents emotion detection result"""
    emotion: str
    confidence: float
    intensity: str  # low, moderate, high, severe
    contributing_factors: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "emotion": self.emotion,
            "confidence": round(self.confidence, 3),
            "intensity": self.intensity,
            "contributing_factors": self.contributing_factors
        }


class EmotionClassifier:
    """
    Hybrid rule-based emotion classifier using normalized audio features.
    
    Detection Strategy:
    1. Use gender-normalized Z-scores (not raw values!)
    2. Combine multiple features (pitch, energy, speech rate, pauses)
    3. Weight features based on research (pitch > energy > temporal)
    4. Apply thresholds calibrated for Vietnamese speakers
    
    Emotions Detected:
    - Anxiety: High pitch Z-score, fast speech, short pauses
    - Sadness: Low energy, slow speech, low pitch variability
    - Anger: High energy + pitch, fast speech, high intensity
    - Neutral: All features within normal range
    
    Key Insight:
    Using Z-scores instead of raw values prevents gender bias!
    Female 220 Hz → Z=0.22 (normal) vs Male 220 Hz → Z=2.25 (severe)
    """
    
    def __init__(self):
        """Initialize emotion classifier with thresholds"""
        
        # Z-score thresholds (standard deviations from mean)
        self.thresholds = {
            # Pitch Z-score thresholds
            "pitch_z_high": 1.5,      # High pitch (anxiety, anger)
            "pitch_z_low": -1.5,      # Low pitch (sadness, calm)
            "pitch_z_severe": 2.0,    # Severe deviation
            
            # Energy thresholds (relative to baseline)
            "energy_high": 1.3,       # High energy (anger, excitement)
            "energy_low": 0.7,        # Low energy (sadness, fatigue)
            
            # Speech rate thresholds (syllables/second)
            "speech_rate_fast": 4.5,  # Fast speech (anxiety, anger)
            "speech_rate_slow": 2.5,  # Slow speech (sadness, fatigue)
            
            # Pause characteristics
            "pause_ratio_high": 0.3,  # Many pauses (anxiety, hesitation)
            "pause_ratio_low": 0.1,   # Few pauses (anger, fluent)
            
            # Voice stability (0-1)
            "stability_low": 0.4,     # Unstable voice (anxiety, emotion)
            "stability_high": 0.7,    # Stable voice (calm, controlled)
            
            # Pitch variability (normalized std)
            "variability_high": 0.25, # High variation (emotional)
            "variability_low": 0.10,  # Low variation (monotone)
        }
        
        # Feature weights for emotion scoring
        self.feature_weights = {
            "pitch_z": 0.35,          # Pitch most important
            "energy": 0.25,           # Energy second
            "speech_rate": 0.20,      # Speech rate third
            "pauses": 0.10,           # Pauses contribute
            "stability": 0.10,        # Voice stability
        }
        
        logger.info("✅ Emotion Classifier initialized with gender-aware thresholds")
    
    def classify(self, normalized_features: Dict, transcript: str = "") -> Dict:
        """
        Classify emotions from normalized audio features.
        
        Args:
            normalized_features: Output from GenderNormalizer.normalize_all_features()
                Required keys:
                - pitch_z_score: Normalized pitch
                - pitch_deviation: Absolute deviation
                - pitch_variability: Normalized std
                - energy_relative: Energy relative to baseline
                - speech_rate: Syllables per second
                - pause_ratio: Proportion of silence
                - voice_stability: Stability score (0-1)
                
            transcript: Optional text transcript for context
        
        Returns:
            Dict containing:
            - primary_emotion: Main detected emotion
            - emotion_scores: List of EmotionScore objects
            - confidence: Overall confidence (0-1)
            - summary: Human-readable summary
        """
        logger.info("🧠 Starting emotion classification...")
        
        # Detect each emotion
        anxiety_score = self._detect_anxiety(normalized_features)
        sadness_score = self._detect_sadness(normalized_features)
        anger_score = self._detect_anger(normalized_features)
        neutral_score = self._detect_neutral(normalized_features)
        
        # Collect all emotion scores
        emotion_scores = [
            anxiety_score,
            sadness_score,
            anger_score,
            neutral_score
        ]
        
        # Sort by confidence (highest first)
        emotion_scores.sort(key=lambda x: x.confidence, reverse=True)
        
        # Primary emotion is highest confidence
        primary_emotion = emotion_scores[0]
        
        # Overall confidence (max confidence among all emotions)
        overall_confidence = primary_emotion.confidence
        
        # Generate summary
        summary = self._generate_summary(primary_emotion, emotion_scores)
        
        logger.info(f"✅ Primary emotion: {primary_emotion.emotion} "
                   f"({primary_emotion.intensity}, conf: {overall_confidence:.2f})")
        
        return {
            "primary_emotion": primary_emotion.emotion,
            "intensity": primary_emotion.intensity,
            "confidence": overall_confidence,
            "emotion_scores": [score.to_dict() for score in emotion_scores],
            "summary": summary,
            "contributing_factors": primary_emotion.contributing_factors
        }
    
    def _detect_anxiety(self, features: Dict) -> EmotionScore:
        """
        Detect anxiety from normalized features.
        
        Anxiety Indicators:
        - High pitch Z-score (voice tension)
        - Fast speech rate (nervousness)
        - Many pauses (hesitation)
        - Low voice stability (trembling)
        - High pitch variability (unsteady)
        """
        factors = []
        score = 0.0
        
        pitch_z = features.get("pitch_z_score", 0.0)
        speech_rate = features.get("speech_rate", 3.0)
        pause_ratio = features.get("pause_ratio", 0.15)
        stability = features.get("voice_stability", 0.5)
        variability = features.get("pitch_variability", 0.15)
        
        # High pitch Z-score (most important for anxiety)
        if pitch_z > self.thresholds["pitch_z_high"]:
            contribution = (pitch_z - self.thresholds["pitch_z_high"]) * 0.4
            score += contribution * self.feature_weights["pitch_z"]
            factors.append(f"High pitch (Z={pitch_z:.2f})")
        
        # Fast speech rate
        if speech_rate > self.thresholds["speech_rate_fast"]:
            contribution = (speech_rate - self.thresholds["speech_rate_fast"]) / 2.0
            score += contribution * self.feature_weights["speech_rate"]
            factors.append(f"Fast speech ({speech_rate:.2f} syl/s)")
        
        # Many pauses (hesitation)
        if pause_ratio > self.thresholds["pause_ratio_high"]:
            contribution = (pause_ratio - self.thresholds["pause_ratio_high"]) * 2.0
            score += contribution * self.feature_weights["pauses"]
            factors.append(f"Frequent pauses ({pause_ratio:.1%})")
        
        # Low voice stability (trembling)
        if stability < self.thresholds["stability_low"]:
            contribution = (self.thresholds["stability_low"] - stability) * 1.5
            score += contribution * self.feature_weights["stability"]
            factors.append(f"Unstable voice (stability={stability:.2f})")
        
        # High pitch variability
        if variability > self.thresholds["variability_high"]:
            contribution = (variability - self.thresholds["variability_high"]) * 2.0
            score += contribution * self.feature_weights["pitch_z"]
            factors.append(f"High pitch variation ({variability:.2f})")
        
        # Normalize score to 0-1
        confidence = min(score, 1.0)
        
        # Determine intensity
        intensity = self._get_intensity(confidence)
        
        if not factors:
            factors = ["No anxiety indicators"]
        
        return EmotionScore(
            emotion="anxiety",
            confidence=confidence,
            intensity=intensity,
            contributing_factors=factors
        )
    
    def _detect_sadness(self, features: Dict) -> EmotionScore:
        """
        Detect sadness from normalized features.
        
        Sadness Indicators:
        - Low energy (fatigue, low motivation)
        - Slow speech rate (lack of energy)
        - Low pitch variability (monotone)
        - Normal or low pitch Z-score
        - High voice stability (controlled but flat)
        """
        factors = []
        score = 0.0
        
        energy = features.get("energy_relative", 1.0)
        speech_rate = features.get("speech_rate", 3.0)
        variability = features.get("pitch_variability", 0.15)
        pitch_z = features.get("pitch_z_score", 0.0)
        
        # Low energy (most important for sadness)
        if energy < self.thresholds["energy_low"]:
            contribution = (self.thresholds["energy_low"] - energy) * 1.5
            score += contribution * self.feature_weights["energy"]
            factors.append(f"Low energy (rel={energy:.2f})")
        
        # Slow speech rate
        if speech_rate < self.thresholds["speech_rate_slow"]:
            contribution = (self.thresholds["speech_rate_slow"] - speech_rate) / 2.0
            score += contribution * self.feature_weights["speech_rate"]
            factors.append(f"Slow speech ({speech_rate:.2f} syl/s)")
        
        # Low pitch variability (monotone)
        if variability < self.thresholds["variability_low"]:
            contribution = (self.thresholds["variability_low"] - variability) * 3.0
            score += contribution * self.feature_weights["pitch_z"]
            factors.append(f"Monotone voice (var={variability:.2f})")
        
        # Low pitch Z-score (but not too low)
        if -1.0 < pitch_z < 0.5:
            contribution = 0.2  # Mild contribution
            score += contribution * self.feature_weights["pitch_z"]
            factors.append(f"Subdued pitch (Z={pitch_z:.2f})")
        
        # Normalize score
        confidence = min(score, 1.0)
        
        intensity = self._get_intensity(confidence)
        
        if not factors:
            factors = ["No sadness indicators"]
        
        return EmotionScore(
            emotion="sadness",
            confidence=confidence,
            intensity=intensity,
            contributing_factors=factors
        )
    
    def _detect_anger(self, features: Dict) -> EmotionScore:
        """
        Detect anger from normalized features.
        
        Anger Indicators:
        - High energy (loud voice)
        - High pitch Z-score (tension)
        - Fast speech rate (agitation)
        - Few pauses (aggressive, continuous)
        - High pitch variability (emotional)
        """
        factors = []
        score = 0.0
        
        energy = features.get("energy_relative", 1.0)
        pitch_z = features.get("pitch_z_score", 0.0)
        speech_rate = features.get("speech_rate", 3.0)
        pause_ratio = features.get("pause_ratio", 0.15)
        variability = features.get("pitch_variability", 0.15)
        
        # High energy (most important for anger)
        if energy > self.thresholds["energy_high"]:
            contribution = (energy - self.thresholds["energy_high"]) * 1.2
            score += contribution * self.feature_weights["energy"]
            factors.append(f"High energy (rel={energy:.2f})")
        
        # High pitch Z-score
        if pitch_z > self.thresholds["pitch_z_high"]:
            contribution = (pitch_z - self.thresholds["pitch_z_high"]) * 0.3
            score += contribution * self.feature_weights["pitch_z"]
            factors.append(f"Elevated pitch (Z={pitch_z:.2f})")
        
        # Fast speech rate
        if speech_rate > self.thresholds["speech_rate_fast"]:
            contribution = (speech_rate - self.thresholds["speech_rate_fast"]) / 3.0
            score += contribution * self.feature_weights["speech_rate"]
            factors.append(f"Fast speech ({speech_rate:.2f} syl/s)")
        
        # Few pauses (aggressive, continuous)
        if pause_ratio < self.thresholds["pause_ratio_low"]:
            contribution = (self.thresholds["pause_ratio_low"] - pause_ratio) * 1.5
            score += contribution * self.feature_weights["pauses"]
            factors.append(f"Few pauses ({pause_ratio:.1%})")
        
        # High variability
        if variability > self.thresholds["variability_high"]:
            contribution = (variability - self.thresholds["variability_high"]) * 1.5
            score += contribution * self.feature_weights["pitch_z"]
            factors.append(f"High intensity (var={variability:.2f})")
        
        # Normalize score
        confidence = min(score, 1.0)
        
        intensity = self._get_intensity(confidence)
        
        if not factors:
            factors = ["No anger indicators"]
        
        return EmotionScore(
            emotion="anger",
            confidence=confidence,
            intensity=intensity,
            contributing_factors=factors
        )
    
    def _detect_neutral(self, features: Dict) -> EmotionScore:
        """
        Detect neutral/calm state (all features within normal range).
        """
        factors = []
        
        pitch_z = abs(features.get("pitch_z_score", 0.0))
        energy = features.get("energy_relative", 1.0)
        speech_rate = features.get("speech_rate", 3.0)
        stability = features.get("voice_stability", 0.5)
        
        # Count how many features are within normal range
        normal_count = 0
        total_features = 4
        
        # Pitch within ±1 SD
        if pitch_z < 1.0:
            normal_count += 1
            factors.append(f"Normal pitch (Z={pitch_z:.2f})")
        
        # Energy within 0.8-1.2x baseline
        if 0.8 <= energy <= 1.2:
            normal_count += 1
            factors.append(f"Normal energy (rel={energy:.2f})")
        
        # Speech rate within normal range
        if 2.5 <= speech_rate <= 4.5:
            normal_count += 1
            factors.append(f"Normal speech rate ({speech_rate:.2f} syl/s)")
        
        # Voice stability high
        if stability > 0.5:
            normal_count += 1
            factors.append(f"Stable voice ({stability:.2f})")
        
        # Confidence based on proportion of normal features
        confidence = normal_count / total_features
        
        intensity = "balanced" if confidence > 0.7 else "mild"
        
        if not factors:
            factors = ["Some emotional indicators present"]
        
        return EmotionScore(
            emotion="neutral",
            confidence=confidence,
            intensity=intensity,
            contributing_factors=factors
        )
    
    def _get_intensity(self, confidence: float) -> str:
        """
        Map confidence to intensity label.
        
        Args:
            confidence: Confidence score (0-1)
        
        Returns:
            Intensity label: low, moderate, high, severe
        """
        if confidence < 0.3:
            return "low"
        elif confidence < 0.5:
            return "moderate"
        elif confidence < 0.7:
            return "high"
        else:
            return "severe"
    
    def _generate_summary(
        self, 
        primary: EmotionScore, 
        all_scores: List[EmotionScore]
    ) -> str:
        """
        Generate human-readable summary of emotion analysis.
        """
        summary_parts = []
        
        # Primary emotion
        summary_parts.append(
            f"Primary emotion: {primary.emotion.upper()} "
            f"({primary.intensity} intensity, {primary.confidence:.0%} confidence)"
        )
        
        # Contributing factors
        if primary.contributing_factors:
            summary_parts.append(
                f"Key indicators: {', '.join(primary.contributing_factors[:3])}"
            )
        
        # Secondary emotions (if confidence > 0.3)
        secondary = [s for s in all_scores[1:] if s.confidence > 0.3]
        if secondary:
            secondary_names = [f"{s.emotion} ({s.confidence:.0%})" for s in secondary]
            summary_parts.append(f"Secondary: {', '.join(secondary_names)}")
        
        return " | ".join(summary_parts)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🧠 Testing Emotion Classifier with Gender-Normalized Features\n")
    print("="*70)
    
    classifier = EmotionClassifier()
    
    # Test Case 1: Anxious female voice
    print("\nTest 1: Anxious Female Voice")
    print("-" * 70)
    anxious_features = {
        "pitch_z_score": 1.8,       # High pitch for her gender
        "pitch_deviation": 1.8,
        "pitch_variability": 0.28,  # High variation
        "energy_relative": 1.1,     # Slightly elevated
        "speech_rate": 5.2,         # Fast speech
        "pause_ratio": 0.35,        # Many pauses
        "voice_stability": 0.35     # Unstable
    }
    
    result = classifier.classify(anxious_features)
    print(f"Primary: {result['primary_emotion']} ({result['intensity']})")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Summary: {result['summary']}")
    
    # Test Case 2: Sad male voice
    print("\n\nTest 2: Sad Male Voice")
    print("-" * 70)
    sad_features = {
        "pitch_z_score": -0.3,      # Slightly low
        "pitch_deviation": 0.3,
        "pitch_variability": 0.08,  # Monotone
        "energy_relative": 0.6,     # Low energy
        "speech_rate": 2.1,         # Slow speech
        "pause_ratio": 0.20,
        "voice_stability": 0.65     # Stable but flat
    }
    
    result = classifier.classify(sad_features)
    print(f"Primary: {result['primary_emotion']} ({result['intensity']})")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Summary: {result['summary']}")
    
    # Test Case 3: Neutral voice
    print("\n\nTest 3: Neutral Voice")
    print("-" * 70)
    neutral_features = {
        "pitch_z_score": 0.1,       # Near baseline
        "pitch_deviation": 0.1,
        "pitch_variability": 0.15,  # Normal
        "energy_relative": 1.0,     # Baseline
        "speech_rate": 3.5,         # Normal
        "pause_ratio": 0.15,        # Normal
        "voice_stability": 0.70     # Stable
    }
    
    result = classifier.classify(neutral_features)
    print(f"Primary: {result['primary_emotion']} ({result['intensity']})")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Summary: {result['summary']}")
    
    print("\n" + "="*70)
    print("✅ Emotion Classifier ready!")

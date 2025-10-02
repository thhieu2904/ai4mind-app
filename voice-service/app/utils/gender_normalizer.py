"""
Gender-Aware Audio Feature Normalizer

Normalizes audio features based on gender-specific baselines to avoid bias in emotion detection.
"""
from typing import Dict, Optional
from app.core.constants import GENDER_BASELINES


class GenderNormalizer:
    """
    Normalizes audio features using gender-specific baselines.
    
    Example:
        Female voice at 220 Hz (calm) → Without normalization: flagged as "anxious"
        Female voice at 220 Hz (calm) → With normalization: z_score = 0.22 → "calm" ✅
    """
    
    def __init__(self):
        self.baselines = GENDER_BASELINES
    
    def normalize_pitch(
        self,
        pitch_mean: float,
        pitch_std: float,
        gender: str = "prefer_not_to_say"
    ) -> Dict[str, float]:
        """
        Normalize pitch features based on gender baseline.
        
        Args:
            pitch_mean: Average pitch in Hz
            pitch_std: Standard deviation of pitch
            gender: 'male', 'female', 'other', 'prefer_not_to_say'
        
        Returns:
            Dictionary with normalized features:
            - pitch_z_score: Z-score normalized pitch
            - pitch_deviation: Absolute deviation from normal
            - pitch_variability: Coefficient of variation
        """
        # Get baseline for gender
        baseline = self.baselines.get(gender, self.baselines["prefer_not_to_say"])
        
        # Calculate z-score (how many standard deviations from mean)
        pitch_z_score = (pitch_mean - baseline["pitch_mean"]) / baseline["pitch_std"]
        
        # Absolute deviation (easier to interpret)
        pitch_deviation = abs(pitch_z_score)
        
        # Coefficient of variation (normalized variability)
        pitch_variability = pitch_std / pitch_mean if pitch_mean > 0 else 0
        
        return {
            "pitch_z_score": round(pitch_z_score, 3),
            "pitch_deviation": round(pitch_deviation, 3),
            "pitch_variability": round(pitch_variability, 3),
            "gender_baseline": gender,
            "baseline_pitch_mean": baseline["pitch_mean"],
            "baseline_pitch_std": baseline["pitch_std"]
        }
    
    def normalize_energy(
        self,
        energy_mean: float,
        energy_max: float
    ) -> Dict[str, float]:
        """
        Normalize energy features (less gender-dependent).
        
        Args:
            energy_mean: Average energy
            energy_max: Maximum energy
        
        Returns:
            Dictionary with normalized energy features
        """
        # Relative energy (0-1 scale)
        energy_relative = energy_mean / energy_max if energy_max > 0 else 0
        
        return {
            "energy_relative": round(energy_relative, 3)
        }
    
    def normalize_all_features(
        self,
        raw_features: Dict,
        gender: str = "prefer_not_to_say"
    ) -> Dict:
        """
        Normalize all audio features.
        
        Args:
            raw_features: Dictionary of raw audio features
            gender: Gender for normalization
        
        Returns:
            Dictionary with all normalized features
        """
        normalized = {}
        
        # Normalize pitch
        if "pitch_mean" in raw_features and "pitch_std" in raw_features:
            pitch_norm = self.normalize_pitch(
                raw_features["pitch_mean"],
                raw_features["pitch_std"],
                gender
            )
            normalized.update(pitch_norm)
        
        # Normalize energy
        if "energy_mean" in raw_features and "energy_max" in raw_features:
            energy_norm = self.normalize_energy(
                raw_features["energy_mean"],
                raw_features["energy_max"]
            )
            normalized.update(energy_norm)
        
        # Copy and rename gender-independent features
        # Use syllables_per_second (float) instead of speech_rate (string category)
        if "syllables_per_second" in raw_features:
            normalized["speech_rate"] = raw_features["syllables_per_second"]
        
        if "pause_count" in raw_features:
            normalized["pause_count"] = raw_features["pause_count"]
            
        if "voice_stability" in raw_features:
            normalized["voice_stability"] = raw_features["voice_stability"]
        
        # Add pause_ratio (required by NormalizedFeatures)
        if "pause_ratio" in raw_features:
            normalized["pause_ratio"] = raw_features["pause_ratio"]
        else:
            normalized["pause_ratio"] = 0.0  # Default if missing
        
        # Calculate severity (simple heuristic based on features)
        severity_score = 0.0
        if "pitch_z_score" in normalized:
            severity_score += abs(normalized["pitch_z_score"]) * 0.3
        if "energy_relative" in normalized:
            severity_score += abs(normalized.get("energy_relative", 0)) * 0.2
        if "voice_stability" in normalized:
            # Low stability = high severity
            severity_score += (1.0 - normalized["voice_stability"]) * 0.5
        
        # Convert score to category
        if severity_score < 0.3:
            severity_category = "normal"
        elif severity_score < 0.5:
            severity_category = "mild"
        elif severity_score < 0.7:
            severity_category = "moderate"
        else:
            severity_category = "severe"
        
        normalized["severity"] = severity_category
        
        return normalized
    
    def is_within_normal_range(
        self,
        pitch_mean: float,
        gender: str
    ) -> bool:
        """
        Check if pitch is within normal range for gender.
        
        Args:
            pitch_mean: Average pitch in Hz
            gender: Gender category
        
        Returns:
            True if within normal range, False otherwise
        """
        baseline = self.baselines.get(gender, self.baselines["prefer_not_to_say"])
        
        return baseline["pitch_min"] <= pitch_mean <= baseline["pitch_max"]
    
    def calculate_deviation_severity(
        self,
        pitch_z_score: float
    ) -> str:
        """
        Categorize pitch deviation severity.
        
        Args:
            pitch_z_score: Z-score of pitch
        
        Returns:
            'normal', 'mild', 'moderate', or 'severe'
        """
        abs_z = abs(pitch_z_score)
        
        if abs_z < 1.0:
            return "normal"      # Within 1 SD
        elif abs_z < 1.5:
            return "mild"        # 1-1.5 SD
        elif abs_z < 2.0:
            return "moderate"    # 1.5-2 SD
        else:
            return "severe"      # > 2 SD


# Example usage
if __name__ == "__main__":
    normalizer = GenderNormalizer()
    
    # Example 1: Female voice (calm)
    print("\n=== Example 1: Female Calm Voice ===")
    female_calm = normalizer.normalize_pitch(
        pitch_mean=220,  # Hz
        pitch_std=40,
        gender="female"
    )
    print(f"Raw pitch: 220 Hz")
    print(f"Z-score: {female_calm['pitch_z_score']} (close to 0 = normal)")
    print(f"Deviation: {female_calm['pitch_deviation']} SD")
    print(f"Severity: {normalizer.calculate_deviation_severity(female_calm['pitch_z_score'])}")
    
    # Example 2: Female anxious voice
    print("\n=== Example 2: Female Anxious Voice ===")
    female_anxious = normalizer.normalize_pitch(
        pitch_mean=280,  # Higher pitch
        pitch_std=60,    # More variation
        gender="female"
    )
    print(f"Raw pitch: 280 Hz")
    print(f"Z-score: {female_anxious['pitch_z_score']} (positive = higher than normal)")
    print(f"Deviation: {female_anxious['pitch_deviation']} SD")
    print(f"Variability: {female_anxious['pitch_variability']}")
    print(f"Severity: {normalizer.calculate_deviation_severity(female_anxious['pitch_z_score'])}")
    
    # Example 3: Male calm voice (same absolute pitch as female anxious!)
    print("\n=== Example 3: Male Calm Voice (220 Hz) ===")
    male_calm = normalizer.normalize_pitch(
        pitch_mean=220,  # Same as female anxious in raw terms
        pitch_std=35,
        gender="male"
    )
    print(f"Raw pitch: 220 Hz (SAME as female example 1!)")
    print(f"Z-score: {male_calm['pitch_z_score']} (HIGH for male)")
    print(f"Deviation: {male_calm['pitch_deviation']} SD")
    print(f"Severity: {normalizer.calculate_deviation_severity(male_calm['pitch_z_score'])}")
    print("\n⚠️  Without normalization, this would be misclassified!")

"""
Text Analyzer for Vietnamese Language
Analyzes transcribed text for psychological markers and sentiment
"""

import re
import logging
from typing import Dict, List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """
    Vietnamese text analyzer for psychological markers.
    
    Features:
    - Keyword detection (anxiety, sadness, anger)
    - Sentiment analysis (-1 to +1 scale)
    - Psychological markers (self-reference, uncertainty, negation)
    - Word frequency analysis
    - Text statistics
    
    Vietnamese Language Support:
    - Accent-insensitive matching
    - Common Vietnamese phrases
    - Cultural context awareness
    """
    
    def __init__(self):
        """Initialize text analyzer with Vietnamese keywords"""
        
        # Load keywords from constants
        from ..core.constants import (
            ANXIETY_KEYWORDS,
            SADNESS_KEYWORDS,
            ANGER_KEYWORDS,
            POSITIVE_KEYWORDS,
            SELF_REFERENCE,
            UNCERTAINTY_KEYWORDS
        )
        
        self.anxiety_keywords = ANXIETY_KEYWORDS
        self.sadness_keywords = SADNESS_KEYWORDS
        self.anger_keywords = ANGER_KEYWORDS
        self.positive_keywords = POSITIVE_KEYWORDS
        self.self_reference = SELF_REFERENCE
        self.uncertainty_keywords = UNCERTAINTY_KEYWORDS
        
        # Additional psychological markers
        self.negation_words = [
            "không", "chẳng", "chả", "đừng", "đừng có",
            "không bao giờ", "chưa bao giờ", "chẳng bao giờ"
        ]
        
        self.intensity_words = [
            "rất", "quá", "cực kỳ", "vô cùng", "hết sức",
            "đặc biệt", "vô cùng tận", "cực"
        ]
        
        logger.info("✅ Text Analyzer initialized with Vietnamese keywords")
    
    def analyze(self, text: str) -> Dict:
        """
        Comprehensive text analysis for psychological markers.
        
        Args:
            text: Vietnamese text (transcript from Whisper)
        
        Returns:
            Dict containing:
            - sentiment: Overall sentiment score (-1 to +1)
            - emotion_keywords: Detected emotion keywords with counts
            - psychological_markers: Self-reference, uncertainty, negation
            - text_stats: Word count, sentence count, etc.
            - dominant_emotion: Most prominent emotion from text
            - summary: Human-readable summary
        """
        if not text or not text.strip():
            return self._empty_result()
        
        text = text.strip()
        logger.info(f"📝 Analyzing text: {len(text)} chars, preview: {text[:50]}...")
        
        # Normalize text (lowercase, remove extra whitespace)
        normalized_text = self._normalize_text(text)
        
        # Detect emotion keywords
        emotion_keywords = self._detect_emotion_keywords(normalized_text)
        
        # Calculate sentiment
        sentiment = self._calculate_sentiment(emotion_keywords)
        
        # Detect psychological markers
        markers = self._detect_psychological_markers(normalized_text)
        
        # Calculate text statistics
        stats = self._calculate_text_stats(text)
        
        # Determine dominant emotion
        dominant_emotion = self._get_dominant_emotion(emotion_keywords)
        
        # Generate summary
        summary = self._generate_summary(
            sentiment, emotion_keywords, markers, dominant_emotion
        )
        
        logger.info(f"✅ Analysis complete: sentiment={sentiment:.2f}, "
                   f"emotion={dominant_emotion}")
        
        return {
            "sentiment": sentiment,
            "emotion_keywords": emotion_keywords,
            "psychological_markers": markers,
            "text_stats": stats,
            "dominant_emotion": dominant_emotion,
            "summary": summary
        }
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize Vietnamese text for analysis.
        
        - Convert to lowercase
        - Remove extra whitespace
        - Preserve Vietnamese accents (important for meaning!)
        """
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _detect_emotion_keywords(self, text: str) -> Dict:
        """
        Detect and count emotion keywords in text.
        
        Returns:
            Dict with emotion categories and counts:
            {
                "anxiety": {"count": 3, "keywords": ["lo lắng", "căng thẳng"]},
                "sadness": {"count": 1, "keywords": ["buồn"]},
                ...
            }
        """
        results = {}
        
        # Anxiety keywords
        anxiety_found = self._find_keywords(text, self.anxiety_keywords)
        results["anxiety"] = {
            "count": len(anxiety_found),
            "keywords": anxiety_found
        }
        
        # Sadness keywords
        sadness_found = self._find_keywords(text, self.sadness_keywords)
        results["sadness"] = {
            "count": len(sadness_found),
            "keywords": sadness_found
        }
        
        # Anger keywords
        anger_found = self._find_keywords(text, self.anger_keywords)
        results["anger"] = {
            "count": len(anger_found),
            "keywords": anger_found
        }
        
        # Positive keywords
        positive_found = self._find_keywords(text, self.positive_keywords)
        results["positive"] = {
            "count": len(positive_found),
            "keywords": positive_found
        }
        
        return results
    
    def _find_keywords(self, text: str, keyword_list: List[str]) -> List[str]:
        """
        Find all occurrences of keywords in text.
        
        Uses word boundary matching to avoid false positives.
        Example: "lo" should not match "xin chào" (chào contains "o")
        """
        found = []
        
        for keyword in keyword_list:
            # Use word boundary for single words
            if ' ' not in keyword:
                pattern = r'\b' + re.escape(keyword) + r'\b'
            else:
                # For phrases, just escape special chars
                pattern = re.escape(keyword)
            
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return found
    
    def _calculate_sentiment(self, emotion_keywords: Dict) -> float:
        """
        Calculate overall sentiment score from emotion keywords.
        
        Sentiment scale:
        -1.0: Very negative (sadness, anger)
         0.0: Neutral
        +1.0: Very positive
        
        Formula:
        sentiment = (positive - negative) / total
        where negative = anxiety + sadness + anger
        """
        positive_count = emotion_keywords["positive"]["count"]
        anxiety_count = emotion_keywords["anxiety"]["count"]
        sadness_count = emotion_keywords["sadness"]["count"]
        anger_count = emotion_keywords["anger"]["count"]
        
        negative_count = anxiety_count + sadness_count + anger_count
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return 0.0  # Neutral if no emotion keywords
        
        # Calculate sentiment
        sentiment = (positive_count - negative_count) / total_count
        
        # Clamp to [-1, 1]
        sentiment = max(-1.0, min(1.0, sentiment))
        
        return sentiment
    
    def _detect_psychological_markers(self, text: str) -> Dict:
        """
        Detect psychological markers in text.
        
        Markers:
        - Self-reference: "tôi", "mình", "em" (focus on self)
        - Uncertainty: "có lẽ", "chắc là", "không chắc" (indecision)
        - Negation: "không", "chẳng", "đừng" (negative framing)
        - Intensity: "rất", "quá", "cực kỳ" (strong emotions)
        
        High self-reference + uncertainty → possible anxiety
        High negation → possible depression
        High intensity → strong emotions
        """
        # Self-reference count
        self_ref_found = self._find_keywords(text, self.self_reference)
        self_ref_count = len(self_ref_found)
        
        # Uncertainty count
        uncertainty_found = self._find_keywords(text, self.uncertainty_keywords)
        uncertainty_count = len(uncertainty_found)
        
        # Negation count
        negation_found = self._find_keywords(text, self.negation_words)
        negation_count = len(negation_found)
        
        # Intensity count
        intensity_found = self._find_keywords(text, self.intensity_words)
        intensity_count = len(intensity_found)
        
        # Calculate word count for normalization
        word_count = len(text.split())
        
        # Normalize by word count (per 100 words)
        normalize_factor = max(word_count / 100, 1.0)
        
        return {
            "self_reference": {
                "count": self_ref_count,
                "normalized": round(self_ref_count / normalize_factor, 2),
                "keywords": self_ref_found[:5]  # First 5 examples
            },
            "uncertainty": {
                "count": uncertainty_count,
                "normalized": round(uncertainty_count / normalize_factor, 2),
                "keywords": uncertainty_found[:5]
            },
            "negation": {
                "count": negation_count,
                "normalized": round(negation_count / normalize_factor, 2),
                "keywords": negation_found[:5]
            },
            "intensity": {
                "count": intensity_count,
                "normalized": round(intensity_count / normalize_factor, 2),
                "keywords": intensity_found[:5]
            }
        }
    
    def _calculate_text_stats(self, text: str) -> Dict:
        """
        Calculate basic text statistics.
        """
        # Word count
        words = text.split()
        word_count = len(words)
        
        # Sentence count (approximate using punctuation)
        sentences = re.split(r'[.!?。！？]', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Character count
        char_count = len(text)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Average sentence length (words per sentence)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "char_count": char_count,
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2)
        }
    
    def _get_dominant_emotion(self, emotion_keywords: Dict) -> str:
        """
        Determine dominant emotion from keyword counts.
        
        Returns:
            "anxiety", "sadness", "anger", "positive", or "neutral"
        """
        counts = {
            "anxiety": emotion_keywords["anxiety"]["count"],
            "sadness": emotion_keywords["sadness"]["count"],
            "anger": emotion_keywords["anger"]["count"],
            "positive": emotion_keywords["positive"]["count"]
        }
        
        # Find emotion with highest count
        max_emotion = max(counts, key=counts.get)
        max_count = counts[max_emotion]
        
        # If no keywords found, return neutral
        if max_count == 0:
            return "neutral"
        
        return max_emotion
    
    def _generate_summary(
        self,
        sentiment: float,
        emotion_keywords: Dict,
        markers: Dict,
        dominant_emotion: str
    ) -> str:
        """
        Generate human-readable summary of text analysis.
        """
        parts = []
        
        # Sentiment description
        if sentiment > 0.3:
            sentiment_desc = "positive"
        elif sentiment < -0.3:
            sentiment_desc = "negative"
        else:
            sentiment_desc = "neutral"
        
        parts.append(f"Sentiment: {sentiment_desc} ({sentiment:.2f})")
        
        # Dominant emotion
        if dominant_emotion != "neutral":
            count = emotion_keywords[dominant_emotion]["count"]
            parts.append(f"Dominant emotion: {dominant_emotion} ({count} keywords)")
        
        # Psychological markers (if significant)
        high_markers = []
        if markers["self_reference"]["normalized"] > 5.0:
            high_markers.append("high self-focus")
        if markers["uncertainty"]["normalized"] > 3.0:
            high_markers.append("uncertainty")
        if markers["negation"]["normalized"] > 4.0:
            high_markers.append("negative framing")
        if markers["intensity"]["normalized"] > 3.0:
            high_markers.append("intense language")
        
        if high_markers:
            parts.append(f"Markers: {', '.join(high_markers)}")
        
        return " | ".join(parts)
    
    def _empty_result(self) -> Dict:
        """Return empty result for invalid input"""
        return {
            "sentiment": 0.0,
            "emotion_keywords": {
                "anxiety": {"count": 0, "keywords": []},
                "sadness": {"count": 0, "keywords": []},
                "anger": {"count": 0, "keywords": []},
                "positive": {"count": 0, "keywords": []}
            },
            "psychological_markers": {
                "self_reference": {"count": 0, "normalized": 0.0, "keywords": []},
                "uncertainty": {"count": 0, "normalized": 0.0, "keywords": []},
                "negation": {"count": 0, "normalized": 0.0, "keywords": []},
                "intensity": {"count": 0, "normalized": 0.0, "keywords": []}
            },
            "text_stats": {
                "word_count": 0,
                "sentence_count": 0,
                "char_count": 0,
                "avg_word_length": 0.0,
                "avg_sentence_length": 0.0
            },
            "dominant_emotion": "neutral",
            "summary": "No text to analyze"
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("📝 Testing Vietnamese Text Analyzer\n")
    print("="*70)
    
    analyzer = TextAnalyzer()
    
    # Test Case 1: Anxious text
    print("\nTest 1: Anxious Text")
    print("-" * 70)
    anxious_text = """
    Tôi đang rất lo lắng về công việc. Tôi không chắc mình có thể 
    hoàn thành được không. Áp lực quá lớn và tôi cảm thấy căng thẳng.
    Có lẽ tôi không đủ khả năng.
    """
    
    result = analyzer.analyze(anxious_text)
    print(f"Sentiment: {result['sentiment']:.2f}")
    print(f"Dominant: {result['dominant_emotion']}")
    print(f"Anxiety keywords: {result['emotion_keywords']['anxiety']['count']}")
    print(f"Self-reference: {result['psychological_markers']['self_reference']['count']}")
    print(f"Uncertainty: {result['psychological_markers']['uncertainty']['count']}")
    print(f"Summary: {result['summary']}")
    
    # Test Case 2: Sad text
    print("\n\nTest 2: Sad Text")
    print("-" * 70)
    sad_text = """
    Em cảm thấy buồn và mệt mỏi. Không có gì thú vị cả. 
    Mọi thứ đều vô nghĩa. Em chỉ muốn một mình.
    """
    
    result = analyzer.analyze(sad_text)
    print(f"Sentiment: {result['sentiment']:.2f}")
    print(f"Dominant: {result['dominant_emotion']}")
    print(f"Sadness keywords: {result['emotion_keywords']['sadness']['count']}")
    print(f"Negation: {result['psychological_markers']['negation']['count']}")
    print(f"Summary: {result['summary']}")
    
    # Test Case 3: Positive text
    print("\n\nTest 3: Positive Text")
    print("-" * 70)
    positive_text = """
    Hôm nay tôi cảm thấy tốt hơn nhiều. Công việc suôn sẻ và 
    tôi rất vui. Mọi thứ đang dần ổn định.
    """
    
    result = analyzer.analyze(positive_text)
    print(f"Sentiment: {result['sentiment']:.2f}")
    print(f"Dominant: {result['dominant_emotion']}")
    print(f"Positive keywords: {result['emotion_keywords']['positive']['count']}")
    print(f"Summary: {result['summary']}")
    
    print("\n" + "="*70)
    print("✅ Text Analyzer ready!")

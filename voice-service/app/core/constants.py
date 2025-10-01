"""
Voice Analysis Constants
"""
from typing import Dict, List, Any


# Gender-specific audio baselines (from research)
GENDER_BASELINES: Dict[str, Dict[str, float]] = {
    "male": {
        "pitch_mean": 130,  # Hz
        "pitch_std": 40,
        "pitch_min": 85,
        "pitch_max": 180,
        "formant_f1": 730,
        "formant_f2": 1090
    },
    "female": {
        "pitch_mean": 210,  # Hz
        "pitch_std": 45,
        "pitch_min": 165,
        "pitch_max": 255,
        "formant_f1": 850,
        "formant_f2": 2050
    },
    "other": {
        "pitch_mean": 170,
        "pitch_std": 50,
        "pitch_min": 85,
        "pitch_max": 255,
        "formant_f1": 790,
        "formant_f2": 1570
    },
    "prefer_not_to_say": {
        "pitch_mean": 170,
        "pitch_std": 50,
        "pitch_min": 85,
        "pitch_max": 255,
        "formant_f1": 790,
        "formant_f2": 1570
    }
}


# Vietnamese recording prompts
VOICE_PROMPTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "text": "Hãy chia sẻ về cảm xúc của bạn trong tuần qua. Bạn đang cảm thấy thế nào?",
        "duration_seconds": 60,
        "category": "general",
        "language": "vi"
    },
    {
        "id": 2,
        "text": "Gần đây có điều gì khiến bạn lo lắng không? Hãy kể về nó.",
        "duration_seconds": 45,
        "category": "anxiety_focused",
        "language": "vi"
    },
    {
        "id": 3,
        "text": "Kể về một ngày gần đây của bạn, từ khi thức dậy đến khi đi ngủ.",
        "duration_seconds": 60,
        "category": "daily_routine",
        "language": "vi"
    },
    {
        "id": 4,
        "text": "Nếu bạn phải mô tả tâm trạng hiện tại bằng một màu sắc, đó sẽ là màu gì và tại sao?",
        "duration_seconds": 45,
        "category": "metaphorical",
        "language": "vi"
    },
    {
        "id": 5,
        "text": "Điều gì đang khiến bạn căng thẳng nhất trong thời gian này?",
        "duration_seconds": 45,
        "category": "stress_focused",
        "language": "vi"
    }
]


# Vietnamese anxiety-related keywords
ANXIETY_KEYWORDS: List[str] = [
    "lo lắng", "lo", "lắng", "sợ", "sợ hãi", "hãi", "căng thẳng", "căng", "thẳng",
    "stress", "áp lực", "áp", "lực", "hoảng", "hoảng loạn", "bồn chồn",
    "không yên", "không an", "bất an", "lo âu", "âu", "lo nghĩ", "nghĩ ngợi",
    "đánh trống ngực", "tim đập", "run", "rung", "sợ sệt", "e sợ"
]


# Sadness keywords
SADNESS_KEYWORDS: List[str] = [
    "buồn", "buồn bã", "bã", "chán", "chán nản", "nản", "tuyệt vọng",
    "vọng", "trầm", "trầm cảm", "cảm", "tủi", "tủi thân", "thương", "thương cảm",
    "u", "u buồn", "sầu", "sầu muộn", "muộn", "khóc", "nước mắt",
    "đau", "đau khổ", "khổ", "cô đơn", "đơn", "cô", "lẻ loi"
]


# Anger keywords
ANGER_KEYWORDS: List[str] = [
    "tức", "tức giận", "giận", "bực", "bực bội", "bội", "khó chịu",
    "chịu", "cáu", "cáu kỉnh", "kỉnh", "nổi", "nổi giận", "phẫn",
    "phẫn nộ", "nộ", "điên", "điên tiết", "tiết", "gắt", "hung", "hăng"
]


# Positive keywords
POSITIVE_KEYWORDS: List[str] = [
    "vui", "vui vẻ", "vẻ", "hạnh phúc", "phúc", "hạnh", "tốt", "tuyệt",
    "tuyệt vời", "vời", "thoải mái", "thoải", "mái", "yên", "yên tâm",
    "bình", "bình an", "an", "ổn", "ok", "okay", "tích cực", "cực",
    "vui sướng", "sướng", "phấn", "phấn khởi", "khởi"
]


# Self-reference words
SELF_REFERENCE: List[str] = [
    "tôi", "em", "mình", "con", "cháu", "ta"
]


# Uncertainty words
UNCERTAINTY_KEYWORDS: List[str] = [
    "có thể", "chắc", "không chắc", "chắc là", "có lẽ", "lẽ", "có",
    "hình như", "như", "có vẻ", "vẻ như", "dường như", "dường",
    "chắc hẳn", "hẳn", "giống như", "giống"
]


# Speech rate thresholds (syllables per second)
SPEECH_RATE_THRESHOLDS = {
    "slow": 2.5,      # < 2.5 syllables/sec
    "normal_min": 2.5,
    "normal_max": 4.5,
    "fast": 4.5       # > 4.5 syllables/sec
}


# Emotion detection thresholds
EMOTION_THRESHOLDS = {
    "pitch_deviation_high": 1.5,     # Z-score > 1.5 SD
    "pitch_deviation_low": -1.0,     # Z-score < -1.0 SD
    "energy_low": 0.3,                # Energy < 0.3
    "pause_count_high": 15,           # > 15 pauses in 60s
    "pitch_variability_high": 0.25,   # CV > 0.25
}


# Supported audio formats
SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]


# Whisper language code
WHISPER_LANGUAGE = "vi"  # Vietnamese

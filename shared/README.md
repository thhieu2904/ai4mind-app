# Shared folder for AI4Mind

Chứa các file dùng chung giữa các services.

## 📁 Structure

```
shared/
├── audio-files/     # Audio recordings từ voice analysis
├── exports/         # Excel files exported bởi Admin
└── logs/            # Application logs
```

## 🔒 Security

- Files trong folders này **KHÔNG** được commit lên Git
- `.gitignore` đã được setup cho mỗi folder
- Chỉ .gitkeep files được tracked

## 📊 Usage

### Audio Files

```python
# Save audio
import os
AUDIO_DIR = "./shared/audio-files"
audio_path = os.path.join(AUDIO_DIR, f"user_{user_id}_{timestamp}.wav")
```

### Exports

```python
# Generate Excel export
EXPORT_DIR = "./shared/exports"
export_path = os.path.join(EXPORT_DIR, f"assessment_report_{date}.xlsx")
```

### Logs

```python
# Logging configuration
import logging
LOG_DIR = "./shared/logs"
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.INFO
)
```

## 🧹 Cleanup

Tạo scheduled task để xóa old files:

- Audio files: xóa sau 30 ngày
- Exports: xóa sau 90 ngày
- Logs: rotate & compress sau 7 ngày

#!/usr/bin/env python3
"""
AI4Mind - JWT Secret Key Generator
Có 3 modes: Easy (dễ nhớ), Balanced (cân bằng), Secure (an toàn tối đa)
"""

import secrets
import string
from datetime import datetime

def generate_easy_memorable():
    """
    Mode 1: DỄ NHỚ + AN TOÀN TƯƠNG ĐỐI
    Phù hợp: Dự án cá nhân, demo, test với user thật nhưng data không nhạy cảm
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    secret = f"AI4Mind_Project_By_Hieu_{timestamp}_{random_suffix}_SecureKey"
    return secret

def generate_balanced():
    """
    Mode 2: CÂN BẰNG
    Phù hợp: Production với dữ liệu quan trọng
    Vừa an toàn, vừa có thể pattern match để nhớ
    """
    project_prefix = "AI4Mind_Prod"
    random_part = secrets.token_urlsafe(24)  # 192 bits
    version = "v1"
    
    secret = f"{project_prefix}_{random_part}_{version}"
    return secret

def generate_secure():
    """
    Mode 3: TỐI ƯU BẢO MẬT
    Phù hợp: Production với dữ liệu y tế, tài chính, pháp lý
    """
    return secrets.token_urlsafe(32)  # 256 bits

def estimate_crack_time(length, charset_size):
    """
    Ước tính thời gian crack (với GPU mạnh: 100 billion guesses/second)
    """
    total_combinations = charset_size ** length
    guesses_per_second = 100_000_000_000  # 100 billion
    seconds = total_combinations / guesses_per_second
    
    # Convert to readable format
    if seconds < 60:
        return f"{seconds:.2f} giây"
    elif seconds < 3600:
        return f"{seconds/60:.2f} phút"
    elif seconds < 86400:
        return f"{seconds/3600:.2f} giờ"
    elif seconds < 31536000:
        return f"{seconds/86400:.0f} ngày"
    else:
        years = seconds / 31536000
        if years > 1_000_000_000:
            return f"{years:.2e} năm (= vĩnh viễn 🔒)"
        return f"{years:.0f} năm"

if __name__ == "__main__":
    print("=" * 80)
    print("🔐 AI4Mind - JWT Secret Key Generator (3 Modes)")
    print("=" * 80)
    print()
    
    # Mode 1: Easy
    easy_secret = generate_easy_memorable()
    print("🟢 MODE 1: DỄ NHỚ + AN TOÀN TƯƠNG ĐỐI")
    print("-" * 80)
    print(f"Secret: {easy_secret}")
    print(f"Độ dài: {len(easy_secret)} ký tự")
    print(f"Crack time: {estimate_crack_time(len(easy_secret), 62)}")
    print("✅ Dùng cho: Demo, test, dự án cá nhân không có data nhạy cảm")
    print("⚠️  KHÔNG dùng cho: Production với dữ liệu y tế/tài chính")
    print()
    
    # Mode 2: Balanced
    balanced_secret = generate_balanced()
    print("🟡 MODE 2: CÂN BẰNG (KHUYẾN NGHỊ)")
    print("-" * 80)
    print(f"Secret: {balanced_secret}")
    print(f"Độ dài: {len(balanced_secret)} ký tự")
    print("Crack time: ~10^40 năm (vĩnh viễn)")
    print("✅ Dùng cho: Production thông thường")
    print("✅ Vẫn có prefix 'AI4Mind_Prod' để dễ nhận diện")
    print()
    
    # Mode 3: Secure
    secure_secret = generate_secure()
    print("🔴 MODE 3: BẢO MẬT TỐI ĐA")
    print("-" * 80)
    print(f"Secret: {secure_secret}")
    print(f"Độ dài: {len(secure_secret)} ký tự")
    print("Crack time: ~10^70 năm (không thể crack)")
    print("✅ Dùng cho: Production với dữ liệu nhạy cảm (y tế, tài chính)")
    print("💡 Lưu vào password manager (Bitwarden, 1Password)")
    print()
    
    print("=" * 80)
    print("� SO SÁNH")
    print("=" * 80)
    
    comparison = [
        ("'AI4Mind-thhieu2025'", 20, 62, "❌ VÀI PHÚT - 1 GIỜ", "KHÔNG dùng!"),
        ("Mode 1 (Easy)", len(easy_secret), 62, "✅ VÀI NGHÌN NĂM", "OK cho demo/test"),
        ("Mode 2 (Balanced)", len(balanced_secret), 64, "✅ ~10^40 NĂM", "KHUYẾN NGHỊ"),
        ("Mode 3 (Secure)", 43, 64, "✅ ~10^70 NĂM", "Tốt nhất"),
    ]
    
    print(f"{'Secret Type':<25} {'Length':<10} {'Crack Time':<25} {'Recommendation':<20}")
    print("-" * 80)
    for name, length, charset, crack, rec in comparison:
        print(f"{name:<25} {length:<10} {crack:<25} {rec:<20}")
    
    print()
    print("=" * 80)
    print("💡 KHUYẾN NGHỊ CHO BẠN:")
    print("=" * 80)
    print()
    print("📌 NẾU DEPLOY ĐỂ TEST/DEMO (không có user thật):")
    print(f"   → Dùng Mode 1: {easy_secret}")
    print()
    print("📌 NẾU DEPLOY PRODUCTION (có user thật, data tâm lý):")
    print(f"   → Dùng Mode 2: {balanced_secret}")
    print("   → Hoặc Mode 3 nếu muốn an toàn tuyệt đối")
    print()
    print("🔒 LƯU Ý BẢO MẬT:")
    print("   1. ⚠️  KHÔNG commit secret lên Git")
    print("   2. ⚠️  Mỗi environment (dev/prod) dùng secret KHÁC NHAU")
    print("   3. ⚠️  Lưu secret vào password manager hoặc .env file local")
    print("   4. ⚠️  Thay secret mỗi 90 ngày (production)")
    print()

"""
Test voice service directly with httpx (same library as ai-service)
"""
import asyncio
import httpx

async def test_voice_service():
    # Read test audio
    with open("test_audio.wav", "rb") as f:
        audio_bytes = f.read()
    
    print(f"📁 Audio file size: {len(audio_bytes)} bytes")
    
    # Call voice-service (same as ai-service does)
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "http://localhost:8001/api/v1/voice/analyze",
            files={"file": ("test.wav", audio_bytes, "audio/wav")},
            data={
                "user_id": "1",
                "gender": "male"
            }
        )
        
        print(f"\n📊 Status: {response.status_code}")
        print(f"📄 Response:")
        print(response.text)
        
        if response.status_code == 200:
            print("\n✅ SUCCESS!")
            result = response.json()
            print(f"   Transcription: {result.get('transcription', 'N/A')}")
            print(f"   Emotion: {result.get('primary_emotion', 'N/A')}")
        else:
            print(f"\n❌ FAILED: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_voice_service())

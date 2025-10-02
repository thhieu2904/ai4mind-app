import asyncio
import httpx

async def test():
    with open("test_audio.wav", "rb") as f:
        audio_bytes = f.read()
    
    # Exactly like ai-service
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "http://localhost:8001/api/v1/voice/analyze",
            files={"file": ("test.wav", audio_bytes)},
            data={
                "user_id": "1",
                "gender": "male"
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")

asyncio.run(test())

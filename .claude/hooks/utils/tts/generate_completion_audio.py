#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "openai",
#     "openai[voice_helpers]",
#     "python-dotenv",
#     "pyttsx3",
# ]
# ///

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Stop messages to generate
STOP_MESSAGES = [
    "Work complete!",
    "All done!",
    "Task finished!",
    "Job complete!",
    "Ready for next task!",
    "Mission accomplished!",
    "Success!",
    "Finished!",
    "Complete!",
    "Done and dusted!"
]

NOTIFICATION_MESSAGES = [
    "Your agent needs your input",
    "Waiting for your response",
    "Please provide input",
    "Agent waiting",
    "Your attention needed"
]

async def generate_with_openai(text: str, output_path: Path):
    """Generate audio using OpenAI TTS"""
    try:
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False
            
        openai = AsyncOpenAI(api_key=api_key)
        
        print(f"🎙️ Generating with OpenAI: {text}")
        
        response = await openai.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
            response_format="wav"
        )
        
        # Save the audio file
        with open(output_path, "wb") as f:
            f.write(response.content)
            
        return True
        
    except Exception as e:
        print(f"❌ OpenAI TTS failed: {e}")
        return False

def generate_with_pyttsx3(text: str, output_path: Path):
    """Generate audio using pyttsx3"""
    try:
        import pyttsx3
        
        print(f"🎙️ Generating with pyttsx3: {text}")
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 0.8)
        
        # Save to file
        engine.save_to_file(text, str(output_path))
        engine.runAndWait()
        
        return True
        
    except Exception as e:
        print(f"❌ pyttsx3 TTS failed: {e}")
        return False

async def generate_audio_files():
    """Generate all completion and notification audio files"""
    
    # Create audio directory
    script_dir = Path(__file__).parent.parent.parent
    audio_dir = script_dir / "utils" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎵 Generating Stop Audio Files")
    print("=" * 40)
    print(f"📁 Output directory: {audio_dir}")
    
    # Determine which TTS to use
    use_openai = os.getenv("OPENAI_API_KEY") is not None
    
    # Generate stop messages
    print("\n📢 Generating stop messages...")
    for i, message in enumerate(STOP_MESSAGES, 1):
        filename = f"stop_{i:02d}.wav"
        output_path = audio_dir / filename
        
        success = False
        if use_openai:
            success = await generate_with_openai(message, output_path)
        
        if not success:
            success = generate_with_pyttsx3(message, output_path)
            
        if success:
            print(f"✅ Generated: {filename}")
        else:
            print(f"❌ Failed: {filename}")
    
    # Generate notification messages
    print("\n🔔 Generating notification messages...")
    for i, message in enumerate(NOTIFICATION_MESSAGES, 1):
        filename = f"notification_{i:02d}.wav"
        output_path = audio_dir / filename
        
        success = False
        if use_openai:
            success = await generate_with_openai(message, output_path)
        
        if not success:
            success = generate_with_pyttsx3(message, output_path)
            
        if success:
            print(f"✅ Generated: {filename}")
        else:
            print(f"❌ Failed: {filename}")
    
    # Generate engineer-specific notification (if name available)
    engineer_name = os.getenv('ENGINEER_NAME', '').strip()
    if engineer_name:
        message = f"{engineer_name}, your agent needs your input"
        filename = "notification_engineer.wav"
        output_path = audio_dir / filename
        
        success = False
        if use_openai:
            success = await generate_with_openai(message, output_path)
        
        if not success:
            success = generate_with_pyttsx3(message, output_path)
            
        if success:
            print(f"✅ Generated: {filename}")
        else:
            print(f"❌ Failed: {filename}")
    
    print(f"\n🎉 Audio generation complete!")
    print(f"📁 Files saved to: {audio_dir}")

if __name__ == "__main__":
    asyncio.run(generate_audio_files()) 
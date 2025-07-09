#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pygame",
# ]
# ///

import os
import sys
import platform
import subprocess
import random
from pathlib import Path

def get_audio_dir():
    """Get the audio directory path"""
    script_dir = Path(__file__).parent
    return script_dir

def play_audio_file(file_path: Path):
    """Play an audio file using pygame (cross-platform)"""
    if not file_path.exists():
        return False
    
    try:
        import pygame
        
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Load and play the sound
        sound = pygame.mixer.Sound(str(file_path))
        sound.play()
        
        # Wait for the sound to finish
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
        
        pygame.mixer.quit()
        return True
        
    except Exception as e:
        # Fallback to system commands
        system = platform.system().lower()
        
        try:
            if system == "windows":
                subprocess.run([
                    "cmd", "/c", f'start /wait "" "{file_path}"'
                ], 
                timeout=10,
                capture_output=True
                )
                return True
            elif system == "darwin":  # macOS
                subprocess.run([
                    "afplay", str(file_path)
                ], 
                timeout=10
                )
                return True
            elif system == "linux":
                # Try common Linux audio players
                players = ["aplay", "paplay", "play"]
                for player in players:
                    try:
                        subprocess.run([
                            player, str(file_path)
                        ], 
                        timeout=10, 
                        check=True
                        )
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                return False
            else:
                return False
        except Exception:
            return False

def play_stop_audio():
    """Play a random stop audio file"""
    audio_dir = get_audio_dir()
    
    # Get all stop audio files
    stop_files = list(audio_dir.glob("stop_*.wav"))
    
    if not stop_files:
        return False
    
    # Pick a random stop audio
    audio_file = random.choice(stop_files)
    return play_audio_file(audio_file)

def play_notification_audio():
    """Play a notification audio file"""
    audio_dir = get_audio_dir()
    engineer_name = os.getenv('ENGINEER_NAME', '').strip()
    
    # Try engineer-specific notification first (30% chance)
    if engineer_name and random.random() < 0.3:
        engineer_file = audio_dir / "notification_engineer.wav"
        if engineer_file.exists():
            return play_audio_file(engineer_file)
    
    # Fall back to general notification files
    notification_files = list(audio_dir.glob("notification_*.wav"))
    # Remove engineer-specific file from general list
    notification_files = [f for f in notification_files if f.name != "notification_engineer.wav"]
    
    if not notification_files:
        return False
    
    # Pick a random notification audio
    audio_file = random.choice(notification_files)
    return play_audio_file(audio_file)

def main():
    """Command line interface for audio player"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python audio_player.py stop          # Play random stop sound")
        print("  python audio_player.py notification  # Play notification sound")
        print("  python audio_player.py <filename>    # Play specific audio file")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "stop":
        success = play_stop_audio()
        if success:
            print("🔊 Played stop audio")
        else:
            print("❌ Failed to play stop audio")
    elif command == "notification":
        success = play_notification_audio()
        if success:
            print("🔔 Played notification audio")
        else:
            print("❌ Failed to play notification audio")
    else:
        # Try to play specific file
        audio_dir = get_audio_dir()
        file_path = audio_dir / command
        
        # Add .wav extension if not present
        if not file_path.suffix:
            file_path = file_path.with_suffix(".wav")
        
        success = play_audio_file(file_path)
        if success:
            print(f"🔊 Played: {file_path.name}")
        else:
            print(f"❌ Failed to play: {file_path.name}")

if __name__ == "__main__":
    main() 
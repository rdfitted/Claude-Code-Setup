#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "elevenlabs",
#     "python-dotenv",
# ]
# ///

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Skip marker file path - if this exists, skip TTS and clean up
SKIP_MARKER = Path(__file__).parent / ".skip_endhook"

# Voice IDs
DEFAULT_VOICE = "DLsHlh26Ugcm6ELvS0qi"  # Rachel - used by Stop hook
SKILL_VOICE = "OCIdyYxzVR7iuL9fyP9f"    # Voice for /tts skill

# Model IDs
DEFAULT_MODEL = "eleven_flash_v2_5"     # Fast, low-latency for Stop hook
SKILL_MODEL = "eleven_v3"               # Most expressive for /tts skill

def main():
    """
    ElevenLabs Turbo v2.5 TTS Script

    Uses ElevenLabs' Turbo v2.5 model for fast, high-quality text-to-speech.
    Accepts optional text prompt as command-line argument.

    Usage:
    - ./eleven_turbo_tts.py                         # Uses default text and voice
    - ./eleven_turbo_tts.py "Your custom text"      # Uses provided text
    - ./eleven_turbo_tts.py --voice ID "text"       # Uses specified voice

    Features:
    - Fast generation (optimized for real-time use)
    - High-quality voice synthesis
    - Stable production model
    - Cost-effective for high-volume usage
    - Supports skip marker to prevent double-speaking with /tts skill
    - Supports --voice flag to use different voices
    """

    # Parse arguments
    parser = argparse.ArgumentParser(description="ElevenLabs TTS")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Voice ID to use")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID to use")
    parser.add_argument("text", nargs="*", help="Text to speak")
    args = parser.parse_args()

    # Check for skip marker (set by /tts skill to prevent Stop hook from speaking)
    if SKIP_MARKER.exists():
        SKIP_MARKER.unlink()  # Clean up the marker
        print("Skipping TTS (already spoke via /tts skill)")
        return

    # Load environment variables
    load_dotenv("C:/Users/USERNAME/env")

    # Get API key from environment
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in environment variables")
        print("Please add your ElevenLabs API key to .env file:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        sys.exit(1)

    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import play

        # Initialize client
        elevenlabs = ElevenLabs(api_key=api_key)

        print("ElevenLabs Turbo v2.5 TTS")
        print("=" * 40)

        # Get text from arguments or use default
        text = " ".join(args.text) if args.text else "Claude Code session completed successfully."
        voice_id = args.voice
        model_id = args.model

        print(f"Text: {text}")
        print(f"Voice: {voice_id}")
        print(f"Model: {model_id}")
        print("Generating and playing...")

        try:
            # Generate and play audio directly
            audio = elevenlabs.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model_id,
                output_format="mp3_44100_128",
            )
            
            play(audio)
            print("Playback complete!")
            
        except Exception as e:
            print(f"Error: {e}")
        
        
    except ImportError:
        print("Error: elevenlabs package not installed")
        print("This script uses UV to auto-install dependencies.")
        print("Make sure UV is installed: https://docs.astral.sh/uv/")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
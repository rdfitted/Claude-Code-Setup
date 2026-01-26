---
description: Speak text aloud using ElevenLabs TTS (skips the Stop hook TTS)
argument-hint: <text to speak>
allowed-tools: [Bash]
---

# TTS Skill

Speak custom text using ElevenLabs text-to-speech.

## Instructions

1. **Extract the text** from the user's input: `$ARGUMENTS`

2. **Run the TTS command FIRST** with the user's text (using skill voice and model):
   ```bash
   uv run C:\Users\USERNAME\.claude\hooks\utils\tts\elevenlabs_tts.py --voice OCIdyYxzVR7iuL9fyP9f --model eleven_v3 "<USER_TEXT>"
   ```

3. **Create skip marker AFTER TTS completes** to prevent the Stop hook from also speaking:
   ```bash
   echo skip > C:\Users\USERNAME\.claude\hooks\utils\tts\.skip_endhook
   ```

4. **Report success** to the user with a brief confirmation.

## Example

User: `/tts Hello, this is a test of the text to speech system`

Action:
1. Run: `uv run C:\Users\USERNAME\.claude\hooks\utils\tts\elevenlabs_tts.py --voice OCIdyYxzVR7iuL9fyP9f --model eleven_v3 "Hello, this is a test of the text to speech system"`
2. Create skip marker file
3. Respond: "Spoke: Hello, this is a test..."

## Notes

- The skip marker prevents double-speaking (once from this skill, once from the Stop hook)
- The marker file is automatically cleaned up by the Stop hook after it checks for it

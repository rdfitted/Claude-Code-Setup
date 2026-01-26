---
name: speak
description: Speak text by invoking the TTS workflow; use when the user says "speak" or wants audio output.
---

# Speak

## Overview

Use this skill to forward text to the TTS workflow.

## Inputs

- Text to speak

## Workflow

1. Run the TTS workflow with the provided text.
2. If TTS is unavailable, return the text and note the limitation.

## Output

- Spoken text or a fallback note.

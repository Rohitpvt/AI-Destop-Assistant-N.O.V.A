# Project Audit: NOVA Desktop Voice Assistant

This document provides a comprehensive audit of the current NOVA codebase and outlines a roadmap for modernization towards an advanced, AI-driven assistant.

## 1. Current Architecture Summary

- **Main Entry Point**: `NOVA/nova.py`
- **Command Handling Flow**:
    - Queries are received via `takecommand()` (Speech-to-Text) or manual input.
    - Queries are routed through `process_query(query)` using a series of `if-elif` statements.
- **Voice Input Flow**: Uses `speech_recognition` (Google Web Speech API) with a local microphone.
- **Text/Test Mode Flow**: Triggered via `--test` flag. Decouples logic from hardware requirements using `force_text=True`.
- **Text-to-Speech (TTS) Flow**: Uses `pyttsx3` for offline cross-platform TTS.
- **Feature Functions**: Discrete functions (e.g., `screenshot()`, `play_music()`) handle specific tasks.
- **Config Usage**: `NOVA/config.py` centralizes paths, app mappings, and defaults.
- **Logging Usage**: `nova_test.log` tracks commands, features, and success/failure status.
- **Backward Compatibility**: `Jarvis/jarvis.py` exists as a redirect script to guide users to the new path.

## 2. Reusable Components for "Tony-Stark" Style NOVA

| Component | Classification | Reasoning |
| :--- | :--- | :--- |
| **Speech Recognition** | Reuse after cleanup | Basic Google API is okay for now, but needs better error handling and local whisper fallback. |
| **Text-to-Speech** | Replace later | `pyttsx3` is functional but sounds robotic. Future NOVA needs neural TTS (e.g., ElevenLabs or local Coqui). |
| **App Launching** | Reuse as-is | The `os.startfile` approach with config mapping is robust and simple. |
| **Website Opening** | Reuse as-is | `webbrowser` module is the standard way to handle this. |
| **Search Commands** | Reuse after cleanup | Wikipedia and Google Search logic works, but needs better parser/LLM summarization. |
| **Screenshot/Notes** | Reuse as-is | Basic utility functions that work reliably. |
| **Command Routing** | Replace later | `if-elif` is brittle. Needs an LLM-based intent classifier or a dynamic plugin router. |
| **Test Mode** | Reuse as-is | The `--test` architecture is essential for CI/CD and remote dev. |
| **Config System** | Reuse after cleanup | Switch from `config.py` to `config.yaml` or `.env` for better portability. |
| **Logging System** | Reuse as-is | Standard Python logging is sufficient for a local assistant. |

## 3. Weak Points & Limitations

- **Brittle Matching**: Current command parsing is keyword-based (e.g., "wikipedia" must be in the string). It fails on natural variations like "Tell me about...".
- **No LLM Brain**: The assistant cannot hold a conversation or reason about complex requests.
- **Zero Memory**: Each command is isolated; the assistant doesn't remember your name or previous actions across sessions.
- **Lack of Awareness**: No ability to "see" the screen or understand the context of the user's current window.
- **Single-Step Only**: Cannot perform tasks like "Find the latest email from John and summarize it."
- **Hardware Dependency**: Hard failure or silent fallback if PyAudio/Mic is missing (partially mitigated by Test Mode).
- **Robotic Persona**: Lacks the dynamic, helpful personality expected of a high-end assistant.

## 4. Phased Refactoring Plan

### Phase 1: Clean Command Router
- **Goal**: Transition from `if-elif` to a dictionary-based or regex-based router.
- **Risk**: Low.
- **Benefit**: Easier to add features without bloating `process_query`.

### Phase 2: Modularization
- **Goal**: Move features into a `features/` directory (e.g., `features/media.py`, `features/web.py`).
- **Risk**: Medium (import path issues).
- **Benefit**: Cleaner code, easier testing, and independent development of features.

### Phase 3: Modern Config & Logging
- **Goal**: Implement `.env` for secrets and `YAML` for complex configurations.
- **Risk**: Low.
- **Benefit**: Security (no hardcoded API keys) and flexibility.

### Phase 4: Long-Term Memory
- **Goal**: Integrate a local SQLite database or JSON-based memory store.
- **Risk**: Medium.
- **Benefit**: Personalization (remembering user preferences, names, and history).

### Phase 5: LLM Integration (The "Brain")
- **Goal**: Replace keyword matching with an LLM (Local Llama/Gemma or OpenAI API).
- **Risk**: High (latency, cost, complexity).
- **Benefit**: True natural language understanding and reasoning.

### Phase 6: Screen Awareness
- **Goal**: Add OCR (Optical Character Recognition) or VLM (Vision Language Model) capabilities.
- **Risk**: High (privacy, resource heavy).
- **Benefit**: The assistant can see what you are working on and offer contextual help.

## 5. Recommended Future Architecture

```text
NOVA/
  nova.py           # Entry point (Minimal)
  config.py         # Config loader
  core/
    router.py       # Intent classifier (LLM/Regex)
    speech.py       # STT/TTS engine
    logger.py       # Unified logging
  features/
    media.py        # Music, screenshots
    browser.py      # Search, websites
    system.py       # App launching, power
  brain/
    llm.py          # LLM client / Local model loader
    memory.py       # SQLite/Vector store interface
  tests/            # Automated test suite
```

## 6. Audit Conclusions

NOVA is currently in a **transitional state**. Phase 1 (Clean Command Router) and Phase 2 (Modularization) are **COMPLETED**. The assistant now has a clean, modular structure, separating core services (Speech, TTS, Logging) from feature implementations.

### Completed Progress:
- [x] Phase 1: Clean command router (extracted to `core/router.py`)
- [x] Phase 2: Separate features into modules (extracted to `features/`)
- [x] Phase 3: Improve config and logging (Environment variables, rotating logs)
- [x] Phase 4: Long-Term Memory (SQLite interaction history and preferences)
- [x] Phase 5: AI Brain (NVIDIA LLM intent classification and chat)
- [x] Phase 6: Screen Awareness (Capture, OCR, and Analysis)
- [x] Phase 7: System Monitoring & Safe Automation (psutil, pyautogui, confirmations)
- [x] Phase 8: Advanced Skills & Integration (Screen-to-note, Memory-to-note, Session logging)

---
*Audit performed on: 2026-05-14*

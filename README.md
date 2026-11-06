# 🌸 Cute JARVIS — Premium AI Desktop Voice Assistant

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?logo=windows)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52?logo=qt)](https://www.qt.io/)
[![TTS](https://img.shields.io/badge/TTS-Microsoft%20Edge%20Neural-0078D7?logo=microsoftedge)](https://github.com/rany2/edge-tts)
[![LLM](https://img.shields.io/badge/AI-OpenAI%20GPT--4o-00A67E?logo=openai)](https://openai.com/)

A production-quality, futuristic **Cute JARVIS AI Voice Assistant** desktop application tailored for Windows 10 and 11. Built with **PySide6 (Qt6)**, **OpenAI GPT-4o**, **Microsoft Edge Neural TTS**, **SpeechRecognition**, and **SQLite**.

Featuring an adorable animated female AI avatar, reactive circular audio waveforms, real-time speech interaction in both **English and Hindi**, persistent conversation history, and a rich cyberpunk-pastel aesthetic.

---

## ✨ Key Features

* **🌸 Cute Animated Female AI Avatar**:
  * Stylized anime-tech cyber face with breathing floating motion, periodic natural eye blinks, rosy glowing cheeks, and animated speaking lips.
  * Interactive: Click the avatar to start listening or interrupt speech.
* **🌊 Circular Reactive Audio Waveform**:
  * Dynamic concentric neon rings and radial audio equalizer bars that respond to your voice and assistant speech.
  * 4 distinct animated states:
    * `IDLE`: Serene floating breathing halo and orbital particles.
    * `LISTENING`: Pulsing electric cyan audio wave.
    * `THINKING`: Mystic violet swirling vortex rings.
    * `SPEAKING`: Bouncing cute pink and cyan audio equalizer bars synchronized with playback.
* **🌐 Dual-Language Support (English & Hindi)**:
  * **English**: Sweet, playful, witty persona powered by `en-US-AnaNeural` or `en-US-JennyNeural`.
  * **Hindi / Hinglish**: Expressive, respectful, conversational Hindi (`Ji Sir, bilkul!`) powered by `hi-IN-SwaraNeural`.
  * Instant one-click toggle or automatic language detection.
* **🎙 Reliable Speech-to-Text (STT)**:
  * Ambient room noise calibration (`adjust_for_ambient_noise`) with configurable silence energy thresholds.
  * Robust fallback: If no microphone is detected, the app functions seamlessly in text chat mode.
* **🔊 Edge-TTS (Zero-Cost Neural Audio)**:
  * Ultra-clear, natural neural speech synthesis with customizable pitch (`+5Hz`) and speed rate.
  * Local audio caching (`data/cache/audio/`) for instantaneous common responses.
* **💾 Local SQLite History**:
  * Write-Ahead Logging (WAL) enabled for rapid, non-blocking message reads and writes.
  * Full session history, timestamped message bubbles, and one-click feed clearing.
* **⚙️ Built-in Settings Modal**:
  * Live configuration of OpenAI API Key, Model (`gpt-4o-mini`, `gpt-4o`), Voice profiles, Pitch/Rate sliders, and Mic sensitivity.
  * Never hardcodes secret keys.
* **🛡 Offline Persona Fallback**:
  * If no OpenAI API key is supplied, Cute JARVIS still runs offline, providing charming greetings, time, date, identity, and friendly prompts to configure your key.

---

## 🎨 Visual Design Palette

Designed with a premium futuristic dark navy aesthetic with cyber purple and neon cyan/pink accents:

| Element | Color Hex | Description |
| :--- | :--- | :--- |
| **Cosmic Base** | `#0A0D18` | Ultra-deep space navy background |
| **Surface Card** | `#11162B` | Elevated frosted card container |
| **Neon Cyan** | `#00F0FF` | Primary action and listening accent |
| **Violet Purple** | `#8A4DFF` | Futuristic thinking energy & borders |
| **Cute Anime Pink** | `#FF5CA8` | Vocal waves, assistant badge & cheeks |

---

## 📁 Project Architecture

```plaintext
Cute-JARVIS-AI-Assistant/
├── config/                      # Strongly typed settings & theme constants
│   ├── constants.py             # Voice catalogs, theme palette, status enums
│   └── settings.py              # Pydantic BaseSettings loading from .env
├── core/                        # Core utilities & event management
│   ├── event_bus.py             # PySide6 Qt Signal dispatcher
│   ├── exceptions.py            # Typed exception hierarchy
│   └── logger.py                # Rotating file & console logging
├── services/                    # Reusable backend services
│   ├── audio_player.py          # Pygame mixer audio playback with RMS levels
│   ├── llm_service.py           # OpenAI API client + streaming + offline fallback
│   ├── prompt_service.py        # Bilingual "Cute JARVIS" prompt engineering
│   ├── stt_service.py           # Microphone capture & speech-to-text
│   └── tts_service.py           # Microsoft Edge-TTS with audio caching
├── storage/                     # SQLite persistence layer
│   ├── database.py              # Thread-safe SQLite connection (WAL mode)
│   ├── models.py                # Dataclasses for ChatMessage & Preference
│   └── repository.py            # CRUD operations for messages & preferences
├── ui/                          # PySide6 presentation layer
│   ├── components/
│   │   ├── avatar_waveform.py   # Animated AI avatar & circular waveform widget
│   │   ├── chat_bubble.py       # User & Assistant conversation bubbles
│   │   ├── control_bar.py       # Mic button, input box, voice & language picker
│   │   ├── conversation_panel.py# Scrollable chat feed with sample prompt chips
│   │   ├── settings_dialog.py   # Settings modal (API keys, voice modulation)
│   │   └── status_bar.py        # Top bar with state pills & service health
│   ├── styles/
│   │   ├── colors.py            # Palette definitions
│   │   └── qss_templates.py     # Master application QSS styling
│   └── main_window.py           # Master dashboard window
├── workers/                     # Multi-threaded execution
│   ├── text_worker.py           # Background thread for typed queries
│   └── voice_worker.py          # Background thread for voice listening pipeline
├── .env.example                 # Environment variable template
├── .gitignore                   # Git exclusions
├── requirements.txt             # Project dependencies
└── run.py                       # Application entry point
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* **Windows 10 / 11**
* **Python 3.10+** (Tested on Python 3.12)
* Working microphone and speakers / headphones

### 2. Installation
Clone or navigate to the project directory:

```bash
cd "Cute JARVIS AI Assistant"
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

*(Note: On Windows, PyAudio provides binary wheels for Python 3.10-3.12 automatically).*

### 3. Environment Configuration
Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Open `.env` and add your OpenAI API Key (optional on launch, can also be entered inside the app UI):

```env
OPENAI_API_KEY=sk-proj-your_actual_key_here
OPENAI_MODEL=gpt-4o-mini
USER_NAME=Sir
DEFAULT_LANGUAGE=en-US
```

### 4. Launch the Assistant
Run the application bootloader:

```bash
python run.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Enter` (in text box) | Send text query |
| `Ctrl + ,` | Open Settings Dialog |
| `Ctrl + L` | Toggle Language (English ⮂ Hindi) |
| `Ctrl + M` | Mute / Unmute Voice Audio |

---

## 🛠 Troubleshooting

* **Microphone not detected**:
  * Check that your microphone is plugged in and set as default in Windows Sound Settings.
  * The app will notify you in the status bar (`● MIC: No Device`), and you can continue using text input.
* **Invalid or Missing OpenAI API Key**:
  * Click the ⚙️ icon in the top header or press `Ctrl + ,` to open the Settings modal and paste your OpenAI key.
  * Without an API key, Cute JARVIS operates in **Offline Fallback Mode**, answering greetings, time, and system commands.
* **PyAudio wheel installation error**:
  * Run `pip install pipwin && pipwin install pyaudio`.

---

## 📜 License
MIT License. Built with love for advanced desktop AI experiences.

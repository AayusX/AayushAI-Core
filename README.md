# AayushAI-Core

> A personal AI assistant at two scales: a browser voice assistant powered by
> **Google Gemini**, and a desktop "AGI" with neural-style memory, voice output,
> and system tools.

This repository bundles two companion projects:

| # | Project | Where | What it is |
| - | ------- | ----- | ---------- |
| 1 | **AayusX Instant Voice Assistant** | `index.html` | Single-file web chat UI calling **Gemini 2.5 Flash** with grounded Google search and source citations |
| 2 | **AayushAGI** | `AayushAI-Core/AayushAGI/` | Password-protected Python personal assistant with a GUI + CLI, memory system, voice output, and system automation |

## 1. Web Voice Assistant (`index.html`)

- 💬 Chat UI with push-to-talk button and animated waveform
- 🔎 **Gemini 2.5 Flash** with `google_search` grounding — answers cite sources
- ⏳ Thinking dots, exponential-backoff retries, error banners
- 📱 Touch + mouse friendly

### Run it

Open `index.html` in a browser, or deploy the repo to GitHub Pages
(`.github/workflows/static.yml` does this automatically).

> ⚠️ **Note:** the mic button currently streams a simulated query (no speech
> transcription yet) and the Gemini API key is embedded in the page. For
> production use, move the key to a backend proxy or environment variable.

## 2. AayushAGI — Desktop Assistant (`AayushAI-Core/AayushAGI/`)

- 🔐 Encrypted, password-protected startup; encrypted data at rest
- 🧠 Memory system — conversational, semantic, & episodic layers + `neural_weights.json`
- 💬 Personalized greetings based on your profile (name, profession, interests)
- ⏰ Reminders, journal with emotion detection, notes, calculator
- 📺 YouTube playback, web search, jokes, file opening
- 🖥️ System status, cleanup, file organization, network diagnostics, security scan
- 🔊 Voice output (pyttsx3) and edge sounds; optional speech recognition
- 🌙 Dark-themed tkinter GUI + terminal interface

### Run it

```bash
cd AayushAI-Core/AayushAGI
pip install -r requirements.txt
bash start_aayush.sh        # or: python main.py  (CLI) / python gui_main.py  (GUI)
python test_system.py       # smoke test
```

See the [detailed AayushAGI README](AayushAI-Core/AayushAGI/README.md) (362
lines) for architecture, commands, data layout, and roadmap.

## Tech Stack

| Component | Technology |
| --------- | ---------- |
| Web assistant | HTML/JS + Tailwind (CDN), **Gemini REST API** (`gemini-2.5-flash`, grounded) |
| Desktop AGI | Python 3.8+, tkinter, pyttsx3, psutil, cryptography, requests, beautifulsoup4 |
| Deploy | GitHub Pages Actions workflow |

## Project Structure

```
├── index.html                     — web voice assistant (single-file app)
├── .github/workflows/static.yml   — GitHub Pages deployment
└── AayushAI-Core/
    ├── AayushAGI/                 — desktop assistant (main.py, gui_main.py, brain.py, utils/, data/)
    ├── requirements.txt           — core desktop deps
    └── full_requirements.txt      — environment pip-freeze dump (~350 packages)
```

## License

See the LICENSE file in this repository.
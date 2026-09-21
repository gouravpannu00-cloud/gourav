# Voice Assistant

A modern, interactive web-based Voice Assistant built with Python, Flask, HTML, CSS, and JavaScript. It supports speech-to-text, command processing, text-to-speech, note-taking, and command history — all with a polished dark-themed dashboard.

## Features

- **Voice Input**: Click the microphone or press Space to speak commands
- **Speech-to-Text**: Uses the browser's Web Speech API
- **Voice Output**: Text-to-speech responses via pyttsx3
- **Command Engine**: Time, date, jokes, calculator, web search, website opener, notes, history
- **Notes**: Save, view, and delete notes
- **Command History**: Automatic logging of all commands
- **Quick Actions**: One-click buttons for common commands
- **Dark/Light Theme**: Toggle between themes with persistence
- **Assistant Status**: Real-time state display (READY, LISTENING, PROCESSING, SPEAKING, ERROR)
- **Statistics**: Commands today, notes saved, total commands
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Animated UI**: Microphone pulse, waveform, message animations, toast notifications

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| Database | SQLite |
| Voice Input | Web Speech API (Browser) |
| Voice Output | pyttsx3 |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Styling | CSS Variables, Glassmorphism, CSS Animations |

## Architecture

```
Voice/
├── app.py                     # Flask backend (routes, commands, database)
├── database/
│   └── voice_assistant.db     # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css          # All frontend styles + themes
│   └── js/
│       └── app.js             # Frontend logic + speech + UI
├── templates/
│   └── index.html             # Single-page dashboard
├── requirements.txt
└── README.md
```

## Installation

1. Clone or download the project.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and go to:
   ```
   http://localhost:5000
   ```

## Database Schema

### notes
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| note | TEXT | Note content |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

### command_history
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| command | TEXT | User's spoken/text command |
| response | TEXT | Assistant's response |
| command_type | TEXT | Category of command |
| timestamp | TIMESTAMP | When command was executed |

### settings
| Column | Type | Description |
|--------|------|-------------|
| key | TEXT | Setting name (primary key) |
| value | TEXT | Setting value |

## Supported Voice Commands

| Command Example | Action |
|-----------------|--------|
| "What time is it?" / "Time" | Tells current time |
| "What is today's date?" / "Date" | Tells current date |
| "Tell me a joke" / "Joke" | Tells a programming joke |
| "Calculate 25 times 4" | Performs math calculation |
| "Search for Python tutorials" | Opens Google search |
| "Open google.com" | Opens a website |
| "Save note: Buy groceries" | Saves a note |
| "Show my notes" | Lists saved notes |
| "Delete note" | Deletes most recent note |
| "Show command history" | Lists recent commands |
| "Clear history" | Clears command history |
| "Who are you?" | Assistant introduction |
| "Help" / "What can you do?" | Lists capabilities |
| "Thank you" / "Thanks" | Polite response |
| "Goodbye" / "Bye" | Closing message |
| "How are you?" / "Status" | System status |

## Screenshots

> Add screenshots here after running the app.

## Known Limitations

- Speech recognition requires Chrome, Edge, or Safari (Web Speech API)
- Microphone access requires HTTPS or localhost
- Text-to-speech quality depends on the system's default TTS engine
- Some commands require an internet connection (web search, website opening)
- Calculator supports basic arithmetic only
- No user authentication (single-user local demo)

## Future Improvements

- Wikipedia integration for knowledge queries
- Weather API integration
- YouTube search
- Multi-user support
- Voice customization (voice selection, speed)
- Export notes to file
- Command suggestions/autocomplete
- Wake word detection

## How to Explain This Project in an Internship Interview

### Why Python?
Python was chosen for the backend because it has excellent libraries for voice processing (`SpeechRecognition`, `pyttsx3`) and a lightweight web framework (Flask) that is perfect for building REST APIs quickly. Python's readability also makes the command engine easy to explain and extend.

### Why JavaScript?
JavaScript handles all frontend interactivity: the Web Speech API for speech-to-text, DOM manipulation for the chat interface, theme toggling, and async communication with the Flask backend via `fetch()`. Using vanilla JS keeps the project simple and avoids build tools.

### Why SQLite?
SQLite is built into Python, requires no server setup, and is perfect for a single-user local application. It stores notes and command history persistently with zero configuration.

### How Voice Recognition Works
The browser's native `webkitSpeechRecognition` API captures audio from the microphone, sends it to the browser's speech engine, and returns a text transcript. This transcript is sent to the Flask backend via a POST request.

### How Frontend Communicates with Backend
The frontend uses `fetch()` to send JSON payloads to REST endpoints (`/api/process`, `/api/notes`, `/api/history`, `/api/stats`, `/api/tts`). The backend returns JSON responses, and the frontend updates the UI dynamically without page reloads.

### How Commands Are Processed
When text arrives at `/api/process`, the `handle_command()` function uses keyword matching and regex to classify the intent. Each command returns a structured response with text, type, optional action, and status. This makes it easy to add new commands without changing the API contract.

### How Data Is Stored
All data is stored in a local SQLite database (`database/voice_assistant.db`). The `notes` table stores user notes. The `command_history` table logs every command with timestamp and type. Parameterized SQL queries prevent SQL injection.

### How Errors Are Handled
The backend wraps command processing in try/except blocks and returns user-friendly JSON error messages. The frontend handles network failures, speech recognition errors, and unknown commands with toast notifications and visual state changes (ERROR state on the microphone). Raw Python exceptions are never exposed to the user.

## License

This project is created for educational/internship demonstration purposes.

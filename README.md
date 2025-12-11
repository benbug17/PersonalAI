# Voice-First Learning Assistant

A Python-only voice learning assistant built with Streamlit. Uses speech recognition, LLM chat, and text-to-speech for a complete voice interaction experience.

## Features

- **Voice Input**: Record questions using your microphone
- **Speech Recognition**: Automatic transcription using Whisper (with speech_recognition fallback)
- **AI Assistant**: Powered by Groq's llama-3.1-8b-instant model
- **Voice Output**: Text-to-speech responses using gTTS
- **User Authentication**: Secure login with bcrypt password hashing
- **Conversation History**: SQLite database stores all interactions
- **TTS Caching**: Hash-based caching to avoid regenerating identical audio

## Tech Stack

- **UI**: Streamlit + audio-recorder-streamlit
- **ASR**: OpenAI Whisper (primary), speech_recognition (fallback)
- **LLM**: Groq API with llama-3.1-8b-instant
- **TTS**: gTTS (Google Text-to-Speech)
- **Database**: SQLite with bcrypt for password security
- **Language**: 100% Python

## Prerequisites

- Python 3.8 or higher
- ffmpeg (required for audio processing)

### Installing ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd <project-directory>
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_actual_api_key_here
```

Get your Groq API key from: https://console.groq.com/keys

## Running the Application

Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage

1. **Create an Account**: Register with a username and password on the first run
2. **Login**: Use your credentials to access the assistant
3. **Record a Question**: Click the microphone button and speak your question
4. **Listen to Response**: The assistant will transcribe, process, and respond with both text and audio
5. **View History**: Check previous conversations in the history section

## Project Structure

```
.
├── streamlit_app.py      # Main Streamlit application (entry point)
├── db.py                 # SQLite database and user authentication
├── groq_client.py        # Groq LLM client wrapper
├── asr.py                # Speech recognition (Whisper + fallback)
├── tts.py                # Text-to-speech with caching
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── app.db               # SQLite database (created on first run)
└── tts_cache/           # TTS audio cache directory (created automatically)
```

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)

### Models

- **ASR**: Whisper "base" model (good balance of speed and accuracy)
- **LLM**: llama-3.1-8b-instant via Groq
- **TTS**: gTTS with English language

## Troubleshooting

### Audio Recording Issues

If the audio recorder doesn't appear or work:
- Ensure your browser has microphone permissions
- Try a different browser (Chrome/Edge work best)
- Check that ffmpeg is installed and in PATH

### Transcription Failures

If Whisper fails to load:
- The app will automatically fall back to speech_recognition
- Ensure you have a stable internet connection (for speech_recognition)
- Check that audio files are in a supported format

### Groq API Errors

If you see "Failed to get response":
- Verify your GROQ_API_KEY is set correctly in .env
- Check your API key is valid at https://console.groq.com/keys
- Ensure you have API credits/quota remaining

### Database Issues

If login/registration fails:
- Delete `app.db` and restart the app to recreate the database
- Check file permissions in the project directory

## Development

### Adding New Features

The modular structure makes it easy to extend:

- **New ASR providers**: Add functions to `asr.py`
- **Different LLMs**: Modify `groq_client.py`
- **Alternative TTS**: Update `tts.py`
- **UI changes**: Edit `streamlit_app.py`

### Database Schema

**users table:**
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Bcrypt-hashed password
- `created_at`: Timestamp

**history table:**
- `id`: Primary key
- `user_id`: Foreign key to users
- `user_query`: User's question
- `assistant_response`: LLM's response
- `created_at`: Timestamp

## Notes

- First Whisper transcription may take longer as the model downloads
- TTS cache grows over time; use "Clear Cache" button in the sidebar
- All audio processing happens server-side for better reliability
- Session data is stored in Streamlit's session state

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure environment variables are set correctly
4. Check Groq API status and quotas

"""
Text-to-Speech (TTS) module for voice learning assistant.
Uses gTTS with hash-based caching to avoid regenerating identical audio.
"""

import os
import hashlib
from typing import Optional
from gtts import gTTS


# Cache directory for TTS audio files
TTS_CACHE_DIR = "tts_cache"


def ensure_cache_dir():
    """
    Ensure the TTS cache directory exists.
    """
    if not os.path.exists(TTS_CACHE_DIR):
        os.makedirs(TTS_CACHE_DIR)


def get_text_hash(text: str) -> str:
    """
    Generate a hash for the given text.
    Used for cache file naming.

    Args:
        text: Text to hash

    Returns:
        SHA256 hash of the text
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def text_to_speech(text: str, language: str = 'en', slow: bool = False) -> Optional[str]:
    """
    Convert text to speech and save as MP3.
    Uses hash-based caching to avoid regenerating identical audio.

    Args:
        text: Text to convert to speech
        language: Language code (default: 'en')
        slow: Whether to use slower speech rate (default: False)

    Returns:
        Path to the generated/cached MP3 file, or None if generation fails
    """
    if not text or not text.strip():
        return None

    ensure_cache_dir()

    # Generate cache filename based on text hash
    text_hash = get_text_hash(text)
    cache_filename = f"{text_hash}.mp3"
    cache_path = os.path.join(TTS_CACHE_DIR, cache_filename)

    # Return cached file if it exists
    if os.path.exists(cache_path):
        return cache_path

    try:
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=language, slow=slow)

        # Save to cache
        tts.save(cache_path)

        return cache_path

    except Exception as e:
        print(f"TTS generation error: {e}")
        return None


def text_to_speech_bytes(text: str, language: str = 'en', slow: bool = False) -> Optional[bytes]:
    """
    Convert text to speech and return as bytes.

    Args:
        text: Text to convert to speech
        language: Language code (default: 'en')
        slow: Whether to use slower speech rate (default: False)

    Returns:
        Audio data as bytes, or None if generation fails
    """
    audio_path = text_to_speech(text, language, slow)

    if not audio_path or not os.path.exists(audio_path):
        return None

    try:
        with open(audio_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading audio file: {e}")
        return None


def clear_cache(max_files: Optional[int] = None):
    """
    Clear the TTS cache directory.

    Args:
        max_files: If provided, only clear if cache has more than this many files
    """
    if not os.path.exists(TTS_CACHE_DIR):
        return

    try:
        files = [f for f in os.listdir(TTS_CACHE_DIR) if f.endswith('.mp3')]

        # Check if we should clear based on max_files
        if max_files is not None and len(files) <= max_files:
            return

        # Remove all cached files
        for filename in files:
            file_path = os.path.join(TTS_CACHE_DIR, filename)
            os.remove(file_path)

        print(f"Cleared {len(files)} cached audio files")

    except Exception as e:
        print(f"Error clearing cache: {e}")


def get_cache_stats() -> dict:
    """
    Get statistics about the TTS cache.

    Returns:
        Dictionary with cache statistics (file_count, total_size_mb)
    """
    if not os.path.exists(TTS_CACHE_DIR):
        return {'file_count': 0, 'total_size_mb': 0.0}

    try:
        files = [f for f in os.listdir(TTS_CACHE_DIR) if f.endswith('.mp3')]
        total_size = sum(
            os.path.getsize(os.path.join(TTS_CACHE_DIR, f))
            for f in files
        )

        return {
            'file_count': len(files),
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }

    except Exception as e:
        print(f"Error getting cache stats: {e}")
        return {'file_count': 0, 'total_size_mb': 0.0}

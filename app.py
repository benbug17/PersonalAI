import streamlit as st
import os
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder

# Import custom modules
import db
import groq_client
import asr
import tts

# Load environment variables
load_dotenv()


def init_session_state():
    """
    Initialize Streamlit session state variables.
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    # user-specific last-question/response (only set for logged-in user)
    if 'last_transcript' not in st.session_state:
        st.session_state.last_transcript = None
    if 'last_response' not in st.session_state:
        st.session_state.last_response = None
    if 'audio_path' not in st.session_state:
        st.session_state.audio_path = None


def _load_user_last_conversation_into_session(user_id):
    """
    Helper: load the single most recent conversation for this user (if any)
    into session_state.last_transcript/last_response/audio_path.
    Falls back gracefully if db returns nothing or errors.
    """
    try:
        if not user_id:
            return
        # Try to get the most recent entry for this specific user
        history = db.get_user_history(user_id, limit=1)  # should return list of dicts
        if history and len(history) > 0:
            item = history[0]
            st.session_state.last_transcript = item.get('query')
            st.session_state.last_response = item.get('response')
            # If you stored a tts path in DB, you can fetch it here; otherwise leave None
            st.session_state.audio_path = item.get('audio_path') if 'audio_path' in item else None
    except Exception as e:
        # Avoid crashing the app if DB call fails; just don't prefill session values
        st.warning("Could not load previous conversation from DB.")
        # Optionally log e somewhere


def login_page():
    """
    Display login/registration page.
    """
    st.title("🎓 Voice Learning Assistant")
    st.markdown("### Welcome! Please login or create an account.")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_button"):
            if login_username and login_password:
                user_id = db.authenticate_user(login_username, login_password)

                if user_id:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_id
                    st.session_state.username = login_username

                    # Load this user's last conversation into session_state
                    _load_user_last_conversation_into_session(user_id)

                    st.success(f"Welcome back, {login_username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")

    with tab2:
        st.subheader("Create Account")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")

        if st.button("Register", key="register_button"):
            if reg_username and reg_password and reg_password_confirm:
                if reg_password != reg_password_confirm:
                    st.error("Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    user_id = db.create_user(reg_username, reg_password)

                    if user_id:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists")
            else:
                st.warning("Please fill in all fields")


def main_app():
    """
    Main application interface for authenticated users.
    """
    # Sidebar
    with st.sidebar:
        st.title(f"👋 {st.session_state.username}")

        if st.button("Logout"):
            # Clear user-related session state on logout
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.last_transcript = None
            st.session_state.last_response = None
            st.session_state.audio_path = None
            st.rerun()

        st.divider()

        # Cache stats
        cache_stats = tts.get_cache_stats()
        st.caption(f"TTS Cache: {cache_stats['file_count']} files ({cache_stats['total_size_mb']} MB)")

        if st.button("Clear Cache"):
            tts.clear_cache()
            st.success("Cache cleared!")
            st.rerun()

    # Main content
    st.title("🎓 Voice Learning Assistant")
    st.markdown("The Name's Rancho. Ask me anything by recording your voice!")

    # Check for Groq API key
    if not os.getenv("GROQ_API_KEY"):
        st.error("⚠️ GROQ_API_KEY not found in environment variables. Please set it in your .env file.")
        st.stop()

    # If we have an authenticated user but no last_transcript in session,
    # attempt to load their most recent conversation.
    if st.session_state.authenticated and not st.session_state.last_transcript:
        _load_user_last_conversation_into_session(st.session_state.user_id)

    # Voice input section
    st.subheader("🎤 Record Your Question")

    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_name="microphone",
        icon_size="1x",
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        with st.spinner("Transcribing your question..."):
            transcript = asr.transcribe_audio(audio_bytes)

        if transcript:
            st.session_state.last_transcript = transcript
            st.success(f"**You said:** {transcript}")

            with st.spinner("Thinking..."):
                response = groq_client.get_learning_assistant_response(transcript)

            if response:
                st.session_state.last_response = response

                # Save to history (ensure we save under current user_id)
                try:
                    db.save_conversation(
                        st.session_state.user_id,
                        transcript,
                        response,
                        # optionally include audio_path if your DB schema supports it
                    )
                except Exception:
                    # avoid crashing; warn the user
                    st.warning("Could not save conversation to history.")

                st.markdown("### 🤖 Assistant's Response")
                st.markdown(response)

                # Generate TTS
                with st.spinner("Generating audio response..."):
                    audio_path = tts.text_to_speech(response)

                if audio_path:
                    st.session_state.audio_path = audio_path

                    # Play audio response (file path or bytes)
                    # If audio_path is bytes-like, st.audio accepts it too. If it's a path, check existence.
                    try:
                        if isinstance(audio_path, (bytes, bytearray)):
                            st.audio(audio_path)
                        else:
                            if os.path.exists(audio_path):
                                st.audio(audio_path)
                            else:
                                st.warning("Generated audio file not found.")
                    except Exception:
                        st.warning("Could not play generated audio.")
                else:
                    st.error("Failed to generate audio response")

            else:
                st.error("Failed to get response from assistant. Please check your GROQ_API_KEY.")
        else:
            st.error("Failed to transcribe audio. Please try again.")

    # Display previous result if exists for the currently authenticated user only
    elif st.session_state.authenticated and st.session_state.last_transcript and st.session_state.last_response:
        st.info(f"**Previous question:** {st.session_state.last_transcript}")
        st.markdown("Just ask to learn")
        st.markdown(st.session_state.last_response)

        if st.session_state.audio_path:
            try:
                if isinstance(st.session_state.audio_path, (bytes, bytearray)):
                    st.audio(st.session_state.audio_path)
                else:
                    if os.path.exists(st.session_state.audio_path):
                        st.audio(st.session_state.audio_path)
            except Exception:
                # don't crash if audio can't be played
                pass

    # History section (user-specific)
    st.divider()
    st.subheader("📚 Conversation History")

    try:
        history = db.get_user_history(st.session_state.user_id, limit=10)
    except Exception:
        history = []

    if history:
        for item in history:
            q = item.get('query', '')
            summary_title = f"Q: {q[:80]}..." if len(q) > 80 else f"Q: {q}"
            with st.expander(summary_title):
                st.markdown(f"**You:** {q}")
                st.markdown(f"**Assistant:** {item.get('response', '')}")
                st.caption(f"🕒 {item.get('timestamp', '')}")
    else:
        st.info("No conversation history yet. Start by asking a question!")


def main():
    """
    Main entry point for the Streamlit app.
    """
    # Configure page
    st.set_page_config(
        page_title="Voice Learning Assistant",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize database
    db.init_db()

    # Initialize session state
    init_session_state()

    # Show appropriate page based on authentication
    if st.session_state.authenticated:
        main_app()
    else:
        login_page()


if __name__ == "__main__":
    main()
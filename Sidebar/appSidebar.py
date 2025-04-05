from io import BytesIO
from pathlib import Path
from webbrowser import open as openURL

from pandas import DataFrame
from Audio_gen.generate_audio import generate_audio
import time
from streamlit import button, columns, download_button, fragment, metric, rerun, session_state, sidebar, write, audio, expander,link_button, text_area
def start_timer():
    if not session_state.running:
        session_state.running = True
        session_state.start_time = time.time() - session_state.elapsed_time
def stop_timer():
    if session_state.running:
        session_state.running = False
        session_state.elapsed_time = time.time() - session_state.start_time
def reset_timer():
    session_state.running = False
    session_state.start_time = None
    session_state.elapsed_time = 0
class AppSidebar:
    def __init__(self):
        """Initialize the Sidebar class."""
        self.user_input = None
        self.front_text = None
        self.back_text = None
    def get_user_input(self):
        """Get user input for either text area or Verbformen search based on the toggle."""
        with expander("🗣️ Text to Speech", expanded=session_state.flashcards_df is None):
            self.user_input = text_area(
                label="⇒ ä - ö - ü - ß",
                placeholder="Text ...",
                key="user_input",
                height=68
            )
            if self.user_input.strip():
                try:
                    audio_path = Path(f"cached_audios/{self.user_input.strip()}.mp3")
                    if not audio_path.exists():
                        audio_path = generate_audio(self.user_input.strip())
                    with open(audio_path, "rb") as audio_file:
                        audio(audio_file, format="audio/mp3", autoplay=True)
                except Exception as e:
                    write(f"Error generating audio: {str(e)}")
    @fragment(run_every=0.4)
    def timer(self):
        if 'running' not in session_state:
            session_state.running = False
        if 'start_time' not in session_state:
            session_state.start_time = None
        if 'elapsed_time' not in session_state:
            session_state.elapsed_time = 0
        if session_state.running:
            session_state.elapsed_time = time.time() - session_state.start_time
        elapsed_minutes = int(session_state.elapsed_time // 60)
        elapsed_seconds = int(session_state.elapsed_time % 60)
        metric(
                    label="Timer:",
                    value=f"{elapsed_minutes} min",
                    delta=f"{elapsed_seconds} s",
                    help="Minutes:Seconds",
                    label_visibility="collapsed",
                )
        col1, col2 = columns(2, gap="small")
        icon = "❚❚" if session_state.running else "▶"
        with col1:
            if button(label=icon, use_container_width=True):
                if not session_state.running:
                    start_timer()
                else:
                    stop_timer()
                    rerun()
        with col2:
            if button("⏹", use_container_width=True, disabled=session_state.elapsed_time==0 or session_state.running):
                reset_timer()
    def download_results(self):
        with expander("Download", expanded=False, icon="📥"):
            buffer = BytesIO()
            DataFrame([[r[1], r[2], r[0]] for r in session_state.Results if not r[3]], columns=["Source", "Target", "index"]).to_excel(buffer, index=False, engine='xlsxwriter')
            download_button("💹 xlsx", buffer.getvalue(), f"Results_{session_state.uploaded_file_data.name.split('.')[0]}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
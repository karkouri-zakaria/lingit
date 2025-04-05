from streamlit import audio, button, columns, dialog, expander, markdown, metric, rerun, session_state, set_page_config, sidebar, tabs, toast, write
from Answers.colorize import colorize_noun
from Sidebar.appSidebar import AppSidebar
from Answers.answers import save_results
from Audio_gen.generate_audio import generate_audio, generate_audios
from pathlib import Path
from time import sleep
from mutagen.mp3 import MP3
from Quiz_tab.init import init_session_state
def main():
    set_page_config(page_title="Lingua", page_icon="🐦", layout="centered", initial_sidebar_state="expanded")
    init_session_state()
    sidebar_manager = AppSidebar()
    if session_state.uploaded_file_data is None:
        from Files.Upload import file_upload_dialog
        if sidebar.button("Upload", icon="📂", use_container_width=True):
            file_upload_dialog()
    else:
        if sidebar.button("Clear", icon="🗑️", use_container_width=True):
            session_state.flashcards_df = None
            session_state.uploaded_file_data = None
            session_state.success_value = False
            rerun()
    if "flashcards_df" not in session_state or session_state.flashcards_df is None:
        from Files.Handle_file_upload import Handle_file_upload
        session_state.flashcards_df = Handle_file_upload(session_state.uploaded_file_data, session_state.success_value)
        if session_state.flashcards_df is not None:
            session_state.flashcards_df = session_state.flashcards_df.iloc[::-1].reset_index(drop=True)
            session_state.original_flashcards_df = session_state.flashcards_df.copy()
            try:
                generate_audios(session_state.flashcards_df)
            except Exception as e:
                toast(f"Error generating audio files: {e}", icon="🔊")
    if session_state.flashcards_df is not None:
        with sidebar:
            left_button, right_button = columns([1,1], gap="small")
            current_index = session_state.flashcard_index if session_state.flashcard_index < len(session_state.flashcards_df ) else 0
            flashcard = session_state.flashcards_df.iloc[current_index]
            total_flashcards = len(session_state.flashcards_df)
            with left_button:
                if button("✖", key="wrong_button", use_container_width=True, type="primary" if any(result[0] == flashcard['Source'] and not result[2] for result in session_state.Results) else "secondary") and not session_state.show_wrongs:
                    session_state.Results = [result for result in session_state.Results if result[1] != flashcard['Source']]
                    session_state.Results.append([int(current_index)+1, flashcard['Source'], flashcard['Target'], False])
                    session_state.flashcard_index = (current_index + 1) % total_flashcards
                    save_results()
                    markdown(f"{colorize_noun(flashcard)}", unsafe_allow_html=True)
                    audio_path = Path(f"cached_audios/{flashcard['Target']}.mp3")
                    if not audio_path.exists():
                        audio_path = generate_audio(flashcard["Target"])
                    with open(audio_path, "rb") as audio_file:
                        audio(audio_file, format="audio/mp3", autoplay=True)
                    sleep(MP3(audio_path).info.length + 1)
                    rerun()
            with right_button:
                if button("✔", key="correct_button", use_container_width=True, type="  " if any(result[0] == flashcard['Source'] and result[2] for result in session_state.Results) else "secondary") and not session_state.show_wrongs:
                    session_state.Results = [result for result in session_state.Results if result[1] != flashcard['Source']]
                    session_state.Results.append([int(current_index)+1, flashcard['Source'], flashcard['Target'], True])
                    session_state.flashcard_index = (current_index + 1) % total_flashcards
                    markdown(f"{colorize_noun(flashcard)}", unsafe_allow_html=True)
                    audio_path = Path(f"cached_audios/{flashcard['Target']}.mp3")
                    if not audio_path.exists():
                        audio_path = generate_audio(flashcard["Target"])
                    with open(audio_path, "rb") as audio_file:
                        audio(audio_file, format="audio/mp3", autoplay=True)
                    sleep(MP3(audio_path).info.length + 1)
                    rerun()
            with left_button:
                if button("⮜", key="prev_button", use_container_width=True, type="primary"):
                    session_state.flashcard_index = (current_index - 1) % total_flashcards
                    rerun()
            with right_button:
                if button("⮞", key="next_button", use_container_width=True, type="primary"):
                    session_state.flashcard_index = (current_index + 1) % total_flashcards
                    write(session_state.flashcard_index)
                    rerun()
            if session_state.flip_list and len(session_state.flashcards_df) > 1:
                session_state.flashcards_df = session_state.flashcards_df.iloc[::-1].reset_index(drop=True)
            with expander("Settings", expanded=False, icon="⚙️"):
                left_button, middle, right_button = columns(3, gap="small")
                if right_button.button("🪣", on_click=lambda: session_state.Results.clear(), disabled=len(session_state.Results) == 0, use_container_width=True):
                    save_results()
                if middle.button("🤦🏼", type="primary" if session_state.show_wrongs else "secondary", disabled=not any(result[3] == False for result in session_state.Results), use_container_width=True):
                        session_state.show_wrongs = not session_state.show_wrongs
                        rerun()
                if left_button.button("ℹ️", key="reset_index", disabled=session_state.flashcard_index == 0 , use_container_width=True):
                    session_state.flashcard_index = 0
                    rerun()
                col1, col2 = columns(2)
                session_state.auto_continue = col1.toggle("⏩", key="auto", value=session_state.auto_continue, help="Automatically continue to the next flashcard after answering")
                session_state.Show_all_anwsers = col1.toggle("🔠", key="show", value=session_state.Show_all_anwsers, help="Show all answers")
                session_state.shuffle_enabled = col2.toggle("🔀", key="shuffle", value=session_state.shuffle_enabled, help="Randomize the flashcards order")
                session_state.flip_list = col2.toggle("🔄", key="flip", value=session_state.flip_list, help="Flip the flashcards order")
            sidebar_manager.get_user_input()
        session_state.flashcards_df = session_state.flashcards_df.iloc[[i for i, result in enumerate(session_state.Results) if not result[3]]] if session_state.show_wrongs else session_state.original_flashcards_df.copy()            
        quiz_tab, all_cards = tabs(["🎮 **Quiz**", f"📓 **{session_state.uploaded_file_data.name if not session_state.flashcards_df is None else "All cards"}**"])
        with quiz_tab:
            from Quiz_tab.Quiz import Quiz
            Quiz(session_state.flashcards_df)
            with sidebar:
                if session_state.flashcards_df is not None: 
                    with sidebar.expander("Timer", icon="⏱️"):
                        sidebar_manager.timer()
                    sidebar_manager.download_results()
                    page_input = sidebar.number_input("Page :", min_value=1, max_value=len(session_state.flashcards_df), step=1, value=session_state.flashcard_index+1, key="page_input")
                    if session_state.flashcard_index != page_input - 1:
                        session_state.flashcard_index = page_input - 1
                        rerun()
        with all_cards:
            from Flashcards.Viewer import viewer_table
            viewer_table(sidebar_manager, session_state.flashcards_df)
    else:
        sidebar_manager.get_user_input()
if __name__ == "__main__":
    main()
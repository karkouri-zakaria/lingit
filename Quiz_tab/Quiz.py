from streamlit import audio, columns, container, data_editor, expander, fragment, markdown, popover, rerun, session_state, slider, write
from mutagen.mp3 import MP3
from pathlib import Path
from time import sleep
from Quiz_tab.init import init_session_state
@fragment
def Quiz(flashcards_df):
    init_session_state()
    if flashcards_df is not None:
        if not flashcards_df.empty:
            if session_state.shuffle_enabled and not session_state.shuffled:
                session_state.original_flashcards_df = flashcards_df.copy()
                session_state.flashcards_df = flashcards_df.sample(frac=1).reset_index(drop=True)
                session_state.flashcard_index = 0
                session_state.shuffled = True
            elif not session_state.shuffle_enabled and session_state.shuffled:
                session_state.flashcards_df = session_state.original_flashcards_df.copy()
                session_state.flashcard_index = 0
                session_state.shuffled = False
            flashcards_df = session_state.flashcards_df
            current_index = session_state.flashcard_index if session_state.flashcard_index < len(flashcards_df) else 0
            total_flashcards = len(flashcards_df)
            flashcard = flashcards_df.iloc[current_index]
            if total_flashcards > 1:
                new_index = slider("**Flashcards :**", min_value=1, max_value=total_flashcards, value=current_index + 1, format="%d") - 1
                if new_index != session_state.flashcard_index:
                    session_state.flashcard_index = new_index
                    rerun()
            else:
                session_state.current_index = 1
            with container(border=True):
                col1, col2 = columns([1, 1], gap="small", vertical_alignment="top")
                col1.markdown(f"#### ⇒ {flashcard['Source']}")
                with col2.expander("Answer :", expanded=session_state.Show_all_anwsers):
                    from Answers.colorize import colorize_noun
                    markdown(f"{colorize_noun(flashcard)}", unsafe_allow_html=True)
                    try:
                        audio_path = Path(f"cached_audios/{flashcard['Target']}.mp3")
                        if not audio_path.exists():
                            from Audio_gen.generate_audio import generate_audio
                            audio_path = generate_audio(flashcard["Target"])
                        with open(audio_path, "rb") as audio_file:
                            audio(audio_file, format="audio/mp3", autoplay=session_state.Show_all_anwsers)
                    except Exception as e:
                        write(f"Error generating audio: {str(e)}")
                    if session_state.auto_continue and session_state.Show_all_anwsers:
                        delay = slider("Continue Speed", min_value=0.25, max_value=3.0, value=1.0, step=0.25)
                        sleep(MP3(audio_path).info.length + 2/delay)
                        session_state.flashcard_index = (current_index + 1) % total_flashcards
                        rerun()
                if not session_state.Show_all_anwsers:
                    from Answers.answers import check_answer
                    check_answer(flashcard, current_index, total_flashcards)
            if not session_state.Show_all_anwsers and not session_state.show_wrongs:
                with expander(
                    f"✌🏼 {len(session_state.Results)} / {total_flashcards} |"
                    f"👍🏼 {((wval := sum(r[3] == True for r in session_state.Results)) / (l := len(session_state.Results) or 1) * 100):.1f}% - {wval} |"
                    f"👎🏼 {((wval := sum(r[3] == False for r in session_state.Results)) / l * 100):.1f}% - {wval}", expanded=True):
                    if len([r for r in session_state.Results if r[3] == False]) > 0: data_editor([{'Source : Target': f"{r[0]} - {r[1]} : {r[2]}"} for r in session_state.Results if r[3] == False][::-1], hide_index=True, use_container_width=True)
                    with popover(f"👉🏼 Missing ({total_flashcards - len(session_state.Results)})"):
                        write(" | ".join([str(i + 1) for i, flashcard in flashcards_df.iterrows() if not any(result[1] == flashcard['Source'] for result in session_state.Results)]))
        else:
            _, message_col, _ = columns([1, 2, 1], gap="small")
            with message_col:
                markdown("⚠️ No flashcards available. Please upload a valid file.")
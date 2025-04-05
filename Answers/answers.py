from csv import writer
from pathlib import Path
from time import sleep
from Answers.colorize import colorize_noun
from Audio_gen.generate_audio import generate_audio
from mutagen.mp3 import MP3
from streamlit import audio, cache_data, error, fragment, info, markdown, rerun, session_state, success, text_input, warning, write
def save_results():
    with open(Path(f"./Results/Results_{session_state.uploaded_file_data.name[:-5]}.csv"), 'w', newline='', encoding='utf-8-sig') as f:
        writer(f).writerows([["Source", "Target", "index"]] + [[r[1], r[2], r[0]] for r in session_state.Results if not r[3]])
@cache_data
def normalize_german(text):
    return text.translate(str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'}))
@fragment
def check_answer(flashcard, current_index, total_flashcards):    
    answer = text_input(
        "Type your answer here:",
        key=f"answer_input_{current_index}",
    )
    if answer:
        correct_answer = normalize_german(flashcard['Target'])
        user_answer = normalize_german(answer.lower())
        for sep in ["·", "\u00B7"]:
            correct_answer = correct_answer.replace(sep, "")
            user_answer = user_answer.replace(sep, "")
        feedback = ""
        mistakes_found = False
        if len(user_answer) > len(correct_answer):
                warning("Your answer is too long. Please try again.")
                mistakes_found = True
        else:
            for i in range(len(correct_answer)):            
                if i < len(user_answer):
                    if user_answer[i].lower() == correct_answer[i].lower():
                        feedback += f"<span style='color: green;'>{correct_answer[i]}</span>"
                    elif not correct_answer[i].isalpha():
                        feedback += f"<span style='color: yellow;'>{correct_answer[i]}</span>"
                        mistakes_found = True
                    else:
                        feedback += f"<span style='color: red;'>{user_answer[i]}</span>"
                        mistakes_found = True
                elif correct_answer[i] in [" ", "\xa0"]:
                    feedback += f"<span style='color: red;'>&#160;</span>"
                elif not correct_answer[i].isalpha():
                        feedback += f"<span style='color: yellow;'>{correct_answer[i]}</span>"
                        mistakes_found = True
                elif not mistakes_found:
                    feedback += f"<span style='color: yellow;'>&lowbar;</span>"
                else :
                    feedback += f"<span style='color: red;'>&lowbar;</span>"
                    mistakes_found = True
            if user_answer.lower() == correct_answer.lower() and not mistakes_found:
                    markdown(f"⇒ {colorize_noun(flashcard)}", unsafe_allow_html=True)
                    success("✅ That's 100% correct:")
                    try:
                        audio_path = Path(f"cached_audios/{flashcard['Target']}.mp3")
                        if not audio_path.exists():
                            audio_path = generate_audio(flashcard["Target"])
                        with open(audio_path, "rb") as audio_file:
                            audio(audio_file, format="audio/mp3", autoplay=True)
                        if session_state.auto_continue:
                            sleep(MP3(audio_path).info.length + 2)
                            if not session_state.show_wrongs:
                                session_state.Results = [result for result in session_state.Results if result[1] != flashcard['Source']]
                                session_state.Results.append([int(current_index)+1, flashcard['Source'], flashcard['Target'], True])
                            session_state.flashcard_index = (current_index + 1) % total_flashcards
                            rerun()
                    except Exception as e:
                        write(f"Error generating audio: {str(e)}")
            elif mistakes_found:
                markdown(f">    {feedback}", unsafe_allow_html=True)
                articles = {"das", "der", "die", "(das)", "(der)", "(die)"}
                if articles & set(flashcard['Target'].split()):
                        write("Articles: ", ", ".join(articles & set(flashcard['Target'].split())))
                error(f"❌ **Try again.** Here's your input with mistakes highlighted:")
            else:
                info("👍🏼 Correct continue ...")
                markdown(f"{feedback}", unsafe_allow_html=True)
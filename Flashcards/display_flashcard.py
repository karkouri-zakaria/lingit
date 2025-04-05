from streamlit import audio, cache_data, columns, container, markdown, write
from Answers.colorize import colorize_noun
from Audio_gen.generate_audio import generate_audio
import pandas as pd
cache_data()
def display_flashcard(index, flashcard):
    """Display a single flashcard with its audio."""
    with container(border=True):
        ind, Eng, Deu, Aud = columns([1, 4, 3, 2])
        ind.write(f"> {index + 1}")
        Eng.write(f"> {flashcard['Source']}")
        Deu.markdown(f"> {colorize_noun(flashcard)}", unsafe_allow_html=True)
        try:
            audio_file = generate_audio(flashcard['Target'])  
            with open(audio_file, "rb") as audio_data:
                Aud.audio(audio_data, format="audio/mp3", autoplay=False)
        except Exception as e:
            write(f"Error: {str(e)}")

from Sidebar.appSidebar import AppSidebar
from Flashcards.display_flashcards import display_flashcards
from pandas import DataFrame
from streamlit import error
def viewer_table(_sidebar_manager: AppSidebar, flashcards_df: DataFrame):
    if flashcards_df is not None:
        try:
            display_flashcards(flashcards_df)
        except Exception as e:
            error(f"Error parsing the file: {e}", icon="🚫")

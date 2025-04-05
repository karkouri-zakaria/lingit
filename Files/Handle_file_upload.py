from pandas import read_csv, read_excel
from streamlit import error, session_state, toast
def Handle_file_upload(uploaded_file, success_value):
    """Handle file upload and processing."""
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()
        try:
            if ext == "xlsx":
                df = read_excel(uploaded_file)
            elif ext == "csv":
                df = read_csv(uploaded_file)
            else:
                error(f"Unsupported file type: {ext}", icon="🚫")
                return None
            if df.shape[1] < 2:
                error("The file must have at least two columns.", icon="🚫")
                return None
            df = df.iloc[:, :2]
            if success_value:
                toast("File uploaded successfully!", icon="✅")
                session_state.success_value = False
            return df
        except Exception as e:
            error(f"Error processing file: {e}", icon="🚫")
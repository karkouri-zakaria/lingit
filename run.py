from os import chdir, devnull, path, system
from subprocess import check_call, CalledProcessError
from sys import executable
if __name__ == "__main__":
    chdir(path.dirname(path.abspath(__file__)))
    try:
        check_call([executable, "-m", "pip", "install", "streamlit", "-r", "requirements.txt"], stdout=open(devnull, 'w'), stderr=open(devnull, 'w'))
    except CalledProcessError:
        print("Error installing dependencies.")
    if path.exists("main.py"):
        system("python -m streamlit run main.py --server.enableStaticServing=false")
    else:
        print("Error: 'main.py' not found.")

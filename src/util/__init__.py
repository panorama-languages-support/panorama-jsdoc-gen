import sys
import os

def resource_path(relative_path: str) -> str:
    ''' Get absolute path to resource, works for dev and for PyInstaller '''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path:str = sys._MEIPASS
    except Exception:
        base_path:str = os.environ.get('_MEIPASS2', os.path.abspath('.'))

    return os.path.join(base_path, relative_path)

import re
import os
import sys

def sanitize_filename(filename: str) -> str:
    """파일명으로 사용할 수 없는 문자를 제거합니다."""
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '', filename)
    if len(filename) > 200:
        filename = filename[:200]
    return filename.strip()

def format_time(seconds: int) -> str:
    """초 단위 시간을 MM:SS 또는 HH:MM:SS 형식으로 변환합니다."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    return f"{int(m):02d}:{int(s):02d}"

def get_default_download_path() -> str:
    """기본 다운로드 경로(사용자 다운로드 폴더)를 반환합니다."""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

def resource_path(relative_path: str) -> str:
    """PyInstaller 빌드 시 리소스 절대 경로를 반환합니다."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

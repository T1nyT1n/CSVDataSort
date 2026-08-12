from pathlib import Path

def open_utf8(path: Path, mode: str):
    return open(path, mode, newline='', encoding='utf-8')

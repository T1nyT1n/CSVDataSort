# TODO: make logging for UI

def debug(message: str):
    print(f'\033[90m[DEBUG]\033[0m {message}')

def log(message: str):
    print(f'\033[96m[LOG]\033[0m {message}')

def success(message: str):
    print(f'\033[92m[SUCCESS]\033[0m {message}')

def error(message: str):
    print(f'\033[91m[ERROR]\033[0m {message}')


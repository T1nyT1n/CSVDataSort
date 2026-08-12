# TODO: make logging for UI
def log(message: str):
    print(f'\033[96m[LOG]\033[0m {message}')

def error(message: str):
    print(f'\033[91m[ERROR]\033[0m {message}')

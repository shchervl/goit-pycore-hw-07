from colorama import Style

from config import BOT_ERROR_COLOR, IDENT


def get_record_or_raise(book, name: str, not_found_msg: str = None):
    username = name.capitalize()
    record = book.find(username)
    if record is None:
        raise KeyError(not_found_msg or f"Contact '{username}' doesn't exist.")
    return username, record


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.strip().lower(), args


def print_error(message):
    print(f"{IDENT}{BOT_ERROR_COLOR}{message}{Style.RESET_ALL}")
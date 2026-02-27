"""
Contact Management Bot

A command-line bot for managing contacts with phone numbers and birthdays.
"""

import readline  # noqa: F401 — enables arrow keys and history in input()
from colorama import Style
from handlers.utils import parse_input, print_error
from models.commands import _COMMANDS
from models.address_book import AddressBook
from config import IDENT, BOT_COLOR, BOT_ERROR_COLOR


def main():
    book = AddressBook()
    print(f"{BOT_COLOR}Welcome to the assistant bot!{Style.RESET_ALL}")

    try:
        while True:
            user_input = input("Enter a command: ").strip()
            cmd, args = parse_input(user_input)

            if cmd in ["close", "exit"]:
                print(f"{BOT_COLOR}Good bye!{Style.RESET_ALL}")
                break
            elif cmd in _COMMANDS:
                result = _COMMANDS[cmd](args, book)
                if result:
                    print(result)
            elif cmd:
                print_error("Invalid command. Type 'help' to see available commands.")
    except KeyboardInterrupt:
        print(f"\n{BOT_COLOR}Good bye!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

"""
Contact Management Bot

A command-line bot for managing contacts with phone numbers and birthdays.
"""

import functools
import readline  #noqa: F401 — enables arrow keys and history in input()
from colorama import Fore, Style
from tabulate import tabulate
from models.errors import UsageError
from models.models import AddressBook, Record

IDENT = " "
BOT_COLOR = Fore.YELLOW
BOT_ERROR_COLOR = Fore.RED
HELP_MAIN_TEXT = Fore.LIGHTGREEN_EX

ERR_NAME_AND_PHONE = "Give me name and phone please."
ERR_NAME_AND_BIRTHDAY = "Give me name and birthday please."
ERR_NAME_ONLY = "Give me a name please."


# Populated automatically by @command — no manual maintenance needed
_COMMAND_REGISTRY: dict = {}
COMMANDS_USAGE: dict = {}


def command(name: str, usage: str = None):
    """Register a handler as a bot command and optionally record its usage hint.

    Stamps func._cmd_name on the wrapped function so @input_error can locate
    the hint without a separate lookup map.
    """
    def decorator(func):
        _COMMAND_REGISTRY[name] = func
        if usage:
            COMMANDS_USAGE[name] = (
                f"{HELP_MAIN_TEXT}{BOT_COLOR}'{usage}'{Style.RESET_ALL}"
            )
        func._cmd_name = name
        return func
    return decorator


def input_error(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            cmd_name = getattr(inner, "_cmd_name", None)
            hint = (
                f"\n{COMMANDS_USAGE[cmd_name]}"
                if (isinstance(e, UsageError) and cmd_name and cmd_name in COMMANDS_USAGE)
                else ""
            )
            return f"{IDENT}{BOT_ERROR_COLOR}{e.args[0]}{Style.RESET_ALL}" + hint
    return inner


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.strip().lower(), args


def print_error(message):
    print(f"{IDENT}{BOT_ERROR_COLOR}{message}{Style.RESET_ALL}")


def print_dict_as_list(dictionary: dict, headers: list):
    if not dictionary:
        print_error("There are no records yet.")
        return
    print(tabulate(dictionary.items(), headers=headers, tablefmt="rounded_outline"))


def get_record_or_raise(book, name: str, not_found_msg: str = None):
    username = name.capitalize()
    record = book.find(username)
    if record is None:
        raise KeyError(not_found_msg or f"Contact '{username}' doesn't exist.")
    return username, record


@command("hello")
@input_error
def hello_cmd(args, book):
    return f"{IDENT}{BOT_COLOR}How can I help you?{Style.RESET_ALL}"


@command("add", usage="add <name> <phone>  –  add a contact with phone.")
@input_error
def add_contact(args, book):
    if len(args) != 2:
        raise UsageError(ERR_NAME_AND_PHONE)
    name, phone = args
    username = name.capitalize()
    record = book.find(username)
    if record is None:
        record = Record(username)
        record.add_phone(phone)
        book.add_record(record)
        return f"{IDENT}{BOT_COLOR}Contact added.{Style.RESET_ALL}"
    record.add_phone(phone)
    return f"{IDENT}{BOT_COLOR}Phone added to existing contact.{Style.RESET_ALL}"


@command("change", usage="change <name> <phone>  –  update a contact's phone.")
@input_error
def update_contact(args, book):
    if len(args) != 2:
        raise UsageError(ERR_NAME_AND_PHONE)
    name, phone = args
    username, record = get_record_or_raise(book, name)
    record.set_phone(phone)
    return f"{IDENT}{BOT_COLOR}Contact updated.{Style.RESET_ALL}"


@command("phone", usage="phone <name>  –  get the phone of a contact.")
@input_error
def get_users_phone(args, book):
    if not args:
        raise UsageError(ERR_NAME_ONLY)
    username, record = get_record_or_raise(book, args[0])
    return BOT_COLOR + tabulate(
        [(username, "; ".join(p.value for p in record.phones))],
        headers=["Name", "Phone(s)"],
        tablefmt="rounded_outline",
    ) + Style.RESET_ALL


@command("all", usage="all  –  list all contacts.")
@input_error
def all_contacts(args, book):
    if not book.data:
        return f"{IDENT}{BOT_ERROR_COLOR}No contacts yet.{Style.RESET_ALL}"
    data = [
        (
            r.name.value,
            "; ".join(p.value for p in r.phones) or "—",
            str(r.birthday) if r.birthday else "—",
        )
        for r in book.data.values()
    ]
    return BOT_COLOR + tabulate(data, headers=["Name", "Phone(s)", "Birthday"], tablefmt="rounded_outline") + Style.RESET_ALL


@command("add-birthday", usage="add-birthday <name> <DD.MM.YYYY>  –  add a birthday to a contact.")
@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise UsageError(ERR_NAME_AND_BIRTHDAY)
    name, birthday_str = args
    username, record = get_record_or_raise(
        book, name,
        not_found_msg=f"Contact '{name.capitalize()}' not found. Add the contact first.",
    )
    record.add_birthday(birthday_str)
    return f"{IDENT}{BOT_COLOR}Birthday added.{Style.RESET_ALL}"


@command("show-birthday", usage="show-birthday <name>  –  show a contact's birthday.")
@input_error
def show_birthday(args, book):
    if not args:
        raise UsageError(ERR_NAME_ONLY)
    username, record = get_record_or_raise(book, args[0])
    if record.birthday is None:
        return f"{IDENT}{BOT_COLOR}{username} has no birthday set.{Style.RESET_ALL}"
    return f"{IDENT}{BOT_COLOR}{username}'s birthday is {record.birthday}.{Style.RESET_ALL}"


@command("birthdays", usage="birthdays  –  show contacts with birthdays in the next week.")
@input_error
def birthdays_cmd(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return f"{IDENT}{BOT_COLOR}No birthdays in the next week.{Style.RESET_ALL}"
    data = [(u["name"], u["birthday"], u["congratulation_date"]) for u in upcoming]
    return BOT_COLOR + tabulate(data, headers=["Name", "Birthday", "Congratulate on"], tablefmt="rounded_outline") + Style.RESET_ALL


@command("help")
@input_error
def help_cmd(args, book):
    print_dict_as_list(COMMANDS_USAGE, ["Command", "Usage"])


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
            elif cmd in _COMMAND_REGISTRY:
                result = _COMMAND_REGISTRY[cmd](args, book)
                if result:
                    print(result)
            elif cmd:
                print_error("Invalid command. Type 'help' to see available commands.")
    except KeyboardInterrupt:
        print(f"\n{BOT_COLOR}Good bye!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

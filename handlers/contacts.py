from colorama import Style
from tabulate import tabulate
from models.commands import command
from models.errors import UsageError
from models.address_book import Record
from config import (
    IDENT, BOT_COLOR, BOT_ERROR_COLOR,
    ERR_NAME_AND_PHONE, ERR_NAME_ONLY,
)
from handlers.utils import get_record_or_raise


@command("add", usage="add <name> <phone> - add a contact with phone.")
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


@command("change", usage="change <name> <phone> - update a contact's phone.")
def update_contact(args, book):
    if len(args) != 2:
        raise UsageError(ERR_NAME_AND_PHONE)
    name, phone = args
    username, record = get_record_or_raise(book, name)
    record.set_phone(phone)
    return f"{IDENT}{BOT_COLOR}Contact updated.{Style.RESET_ALL}"


@command("phone", usage="phone <name> - get the phone of a contact.")
def get_users_phone(args, book):
    if not args:
        raise UsageError(ERR_NAME_ONLY)
    username, record = get_record_or_raise(book, args[0])
    return BOT_COLOR + tabulate(
        [(username, "\n".join(p.value for p in record.phones))],
        headers=["Name", "Phone(s)"],
        tablefmt="rounded_grid",
    ) + Style.RESET_ALL


@command("all", usage="all - list all contacts.")
def all_contacts(args, book):
    if not book.data:
        return f"{IDENT}{BOT_ERROR_COLOR}No contacts yet.{Style.RESET_ALL}"
    data = [
        (
            r.name.value,
            "\n".join(p.value for p in r.phones) or "—",
            str(r.birthday) if r.birthday else "—",
        )
        for r in book.data.values()
    ]
    return BOT_COLOR + tabulate(
        data,
        headers=["Name", "Phone(s)", "Birthday"],
        tablefmt="rounded_grid",
    ) + Style.RESET_ALL

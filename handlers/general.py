from colorama import Style
from tabulate import tabulate
from models.commands import command, _COMMANDS
from config import IDENT, BOT_COLOR


@command("hello")
def hello_cmd(args, book):
    return f"{IDENT}{BOT_COLOR}How can I help you?{Style.RESET_ALL}"


@command("help")
def help_cmd(args, book):
    rows = [(c.name, c.usage) for c in _COMMANDS.values() if c.usage]
    if rows:
        print(BOT_COLOR + tabulate(rows, headers=["Command", "Usage"], tablefmt="rounded_grid") + Style.RESET_ALL)

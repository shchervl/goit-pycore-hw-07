from colorama import Fore, Style
from models.errors import UsageError

# Populated automatically by @command — no manual maintenance needed
_COMMANDS: dict[str, "Command"] = {}


class Command:
    """A registered bot command that wraps a handler with error handling."""

    def __init__(self, name: str, handler, usage: str = None):
        self.name = name
        self.usage = usage
        self._handler = handler

    def __call__(self, args, book):
        try:
            return self._handler(args, book)
        except (ValueError, KeyError, IndexError) as e:
            hint = (
                f"\n{Fore.YELLOW}'{self.usage}'{Style.RESET_ALL}"
                if isinstance(e, UsageError) and self.usage
                else ""
            )
            return f" {Fore.RED}{e.args[0]}{Style.RESET_ALL}" + hint


def command(name: str, usage: str = None):
    """Register a handler as a bot command.

    Registration happens at import time — the moment the module containing
    the decorated function is imported, the command is added to _COMMANDS.
    For example, importing handlers.contacts immediately registers "add",
    "change", "phone", and "all" before any user input is processed.

    To add a new command, create a handler with @command(...) and import
    its module in handlers/__init__.py.
    """

    def decorator(func):
        _COMMANDS[name] = Command(name, func, usage)
        return func

    return decorator

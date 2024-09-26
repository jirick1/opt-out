# main.py

import os
import sys
import argparse
import importlib
import pkgutil

# Import shared classes and constants
from shared import (
    CHAT_DATABASE_PATH,
    OPT_OUT_FILE_PATH,
    SEND_MESSAGE_SCPT,
    OptedOutManager,
    DatabaseHandler,
    PhoneNumberProcessor,
    MessageSender,
)


def load_option_modules(options_dir):
    modules = {}
    package_name = "options"  # Adjust if options_dir has a different package name
    for finder, name, ispkg in pkgutil.iter_modules([options_dir]):
        full_module_name = f"{package_name}.{name}"
        module = importlib.import_module(full_module_name)
        modules[name] = module
    return modules


def main():
    parser = argparse.ArgumentParser(description="Spam Message Unsubscriber Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Load option modules
    options_dir = os.path.join(os.path.dirname(__file__), "options")
    modules = load_option_modules(options_dir)

    # Shared objects
    shared_objects = {
        "opted_out_manager": OptedOutManager(OPT_OUT_FILE_PATH),
        "db_handler": DatabaseHandler(CHAT_DATABASE_PATH),
        "phone_processor": PhoneNumberProcessor(),
        "sender": MessageSender(SEND_MESSAGE_SCPT),
    }

    # Register commands
    for module in modules.values():
        module.register_command(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_usage()
        sys.exit(1)

    # Dispatch to the selected command
    command_func = getattr(args, "func", None)
    if command_func:
        command_func(args, shared_objects)
        # Save opted-out numbers if modified
        shared_objects["opted_out_manager"].save_opted_out_numbers()
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()

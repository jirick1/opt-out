# options/bulk_unsubscribe.py

import os
import time


def register_command(subparsers):
    parser = subparsers.add_parser(
        "bulk_unsubscribe",
        help="Bulk unsubscribe using numbers from a file",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Path to the spam numbers file (default: spam_numbers.txt)",
    )
    parser.set_defaults(func=execute_command)


def execute_command(args, shared_objects):
    opted_out_manager = shared_objects["opted_out_manager"]
    phone_processor = shared_objects["phone_processor"]
    sender = shared_objects["sender"]

    file_path = args.file or shared_objects["SPAM_NUMBERS_FILE"]

    def load_spam_list_file(file_path: str):
        """Load the list of phone numbers from the specified file."""
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return set()
        with open(file_path, "r") as file:
            return set([line.strip() for line in file if line.strip()])

    phone_numbers = load_spam_list_file(file_path)
    for phone_number in phone_numbers:
        phone_number = phone_processor.clean_phone_number(phone_number)
        if not opted_out_manager.is_number_opted_out(phone_number):
            print(f"Sending STOP to {phone_number}")
            sender.send_stop_message(phone_number)
            opted_out_manager.add_number(phone_number)
            time.sleep(0.1)  # Add a delay to prevent spamming

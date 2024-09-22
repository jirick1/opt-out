import os
import re
import sqlite3
import sys
import time
import argparse

CHAT_DATABASE_PATH = "~/Library/Messages/chat.db"
OPT_OUT_FILE_PATH = ".opted_out_list.txt"
SEND_MESSAGE_SCPT = "sendMessage.scpt"
DELETE_MESSAGE_SCRPT = "deleteMessage.scrpt"


def load_opted_out_list():
    """Load the list of phone numbers that have already been sent a STOP message."""
    if not os.path.exists(OPT_OUT_FILE_PATH):
        return set()

    with open(OPT_OUT_FILE_PATH, "r") as file:
        opted_out_numbers = set(line.strip() for line in file)

    return opted_out_numbers


def save_opted_out_list(opted_out_numbers):
    """Save the list of phone numbers that have been opted out."""
    with open(OPT_OUT_FILE_PATH, "w") as file:
        for number in opted_out_numbers:
            file.write(f"{number}\n")


def generate_4_digit_numbers():
    """Generate all 4-digit numbers from 0000 to 9999"""
    numbers = [f"{i:04}" for i in range(10000)]
    return numbers


def append_numbers_to_phone(phone_number: str, numbers: list[str]):
    """Create a list of phone numbers by appending each
    4-digit number to the original phone number."""
    phone_number_list = [phone_number + number for number in numbers]
    return phone_number_list


def send_stop_message(phone_number: str):
    """Calls the osascript to send the "STOP" message"""
    script_path = os.path.join(os.path.dirname(__file__), SEND_MESSAGE_SCPT)
    message = "STOP"
    os.system(f'osascript {script_path} {phone_number} "{message}"')


def unsubscribe_by_phone_number(phone_number: str, opted_out_numbers: set):
    """Unsubscribe the phone number if not already opted out"""
    print(f"Purging by number: {phone_number}")
    four_digit_numbers = generate_4_digit_numbers()
    phone_number_list = append_numbers_to_phone(phone_number, four_digit_numbers)

    for phone_number_with_digits in phone_number_list:
        if phone_number_with_digits not in opted_out_numbers:
            print(f"Sending STOP to {phone_number_with_digits}")
            send_stop_message(phone_number_with_digits)
            opted_out_numbers.add(phone_number_with_digits)  # Add to opted-out list
            time.sleep(0.1)  # Add a 100ms delay to prevent spamming


def get_spam_messages():
    """Get all spam messages."""
    chat_db_path = os.path.expanduser(CHAT_DATABASE_PATH)
    conn = None
    cursor = None

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(chat_db_path)
        cursor = conn.cursor()

        # SQL query to get the last 100 messages containing "spam: <number>"
        query = """
        SELECT message.text 
        FROM message
        WHERE message.text LIKE '%spam: %'
        ORDER BY message.date DESC
        LIMIT 100;
        """

        cursor.execute(query)
        messages = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
        messages = []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return messages


def extract_phone_number_and_modify(messages):
    phone_numbers = []
    for message in messages:
        text = message[0]

        if "spam: " in text:
            try:
                phone_number = text.split("spam: ")[1]
                phone_number = re.sub(r"\D", "", phone_number)
                modified_phone_number = phone_number[:-4]
                phone_numbers.append(modified_phone_number)
            except IndexError:
                continue
    return phone_numbers


def internal_unsubscribe(opted_out_numbers: list[str]):
    """Unsubscribing by numbers db by spam: <number>."""
    spam_messages = get_spam_messages()
    modified_phone_numbers = extract_phone_number_and_modify(spam_messages)

    four_digit_numbers = generate_4_digit_numbers()
    phone_number_list = [
        phone + digits
        for phone in modified_phone_numbers
        for digits in four_digit_numbers
    ]

    for phone_number in phone_number_list:
        if phone_number not in opted_out_numbers:
            print(f"Sending STOP to {phone_number}")
            send_stop_message(phone_number)
            opted_out_numbers.add(phone_number)
            time.sleep(0.1)  # Add a 100ms delay to prevent spamming
    print("unsubscribed Finished.")


def internal_cleanup():
    """Delete all messages from chat.db where message.text is exactly 'STOP'."""
    chat_db_path = os.path.expanduser(CHAT_DATABASE_PATH)
    conn = None
    cursor = None

    try:
        conn = sqlite3.connect(chat_db_path)
        cursor = conn.cursor()

        query = """
        DELETE FROM message
        WHERE text = 'STOP';
        """

        cursor.execute(query)
        conn.commit()  # Commit the changes to the database

        print(f"Deleted {cursor.rowcount} messages with text exactly 'STOP'.")

    except sqlite3.Error as e:
        print(f"SQLite error occurred during internal cleanup: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="Spam Message Unsubscriber Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Option 1: unsubscribe by numbers db by spam: <number>
    subparsers.add_parser(
        "unsubscribe", help="Unsubscribe by numbers db by spam: <number>"
    )

    # Option 2: purge by number
    parser_purge = subparsers.add_parser("purge", help="Purge by phone number")
    parser_purge.add_argument("phone_number", help="Phone number to purge")

    # Option 3: clean up database
    subparsers.add_parser("cleanup", help="Clean up database (stubbed function)")

    args = parser.parse_args()

    if not args.command:
        parser.print_usage()
        sys.exit(1)

    opted_out_numbers = load_opted_out_list()

    if args.command == "unsubscribe":
        internal_unsubscribe(opted_out_numbers)
    elif args.command == "purge":
        unsubscribe_by_phone_number(args.phone_number, opted_out_numbers)
    elif args.command == "cleanup":
        internal_cleanup()

    # Save the opted-out numbers after the operation
    save_opted_out_list(opted_out_numbers)


if __name__ == "__main__":
    main()

import os
import re
import sqlite3
import sys
import time
import argparse

CHAT_DATABASE_PATH = "~/Library/Messages/chat.db"
OPT_OUT_FILE_PATH = ".opted_out_list.txt"
SEND_MESSAGE_SCPT = "sendMessage.scpt"


class OptedOutManager:
    """Handles the loading and saving of opted-out numbers."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.opted_out_numbers = self.load_opted_out_list()

    def load_opted_out_list(self):
        """Load the list of phone numbers that have already been sent a STOP message."""
        if not os.path.exists(self.file_path):
            return set()
        with open(self.file_path, "r") as file:
            return set(line.strip() for line in file)

    def save_opted_out_list(self):
        """Save the list of phone numbers that have been opted out."""
        with open(self.file_path, "w") as file:
            for number in self.opted_out_numbers:
                file.write(f"{number}\n")

    def add_opted_out(self, phone_number):
        """Add a phone number to the opted-out list."""
        self.opted_out_numbers.add(phone_number)

    def is_opted_out(self, phone_number):
        """Check if a phone number is already in the opted-out list."""
        return phone_number in self.opted_out_numbers


class PhoneNumberProcessor:
    """Handles phone number generation and formatting."""

    @staticmethod
    def generate_4_digit_numbers():
        """Generate all 4-digit numbers from 0000 to 9999"""
        return [f"{i:04}" for i in range(10000)]

    @staticmethod
    def append_numbers_to_phone(phone_number: str, numbers: list[str]):
        """Create a list of phone numbers by appending each
        4-digit number to the original phone number."""
        return [phone_number + number for number in numbers]


class MessageSender:
    """Handles sending messages using osascript."""

    def __init__(self, script_path):
        self.script_path = script_path

    def send_stop_message(self, phone_number: str):
        """Calls the osascript to send the "STOP" message."""
        message = "STOP"
        os.system(f'osascript {self.script_path} {phone_number} "{message}"')


class DatabaseHandler:
    """Handles database operations."""

    def __init__(self, db_path):
        self.db_path = os.path.expanduser(db_path)

    def execute_query(self, query, params=None):
        """Executes a query and returns the results."""
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def execute_delete(self, query, params=None):
        """Executes a delete query and returns the number of affected rows."""
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


class MessageProcessor:
    """Processes spam messages and performs unsubscribe operations."""

    def __init__(
        self,
        db_handler: DatabaseHandler,
        phone_processor: PhoneNumberProcessor,
        sender: MessageSender,
    ):
        self.db_handler = db_handler
        self.phone_processor = phone_processor
        self.sender = sender

    def get_spam_messages(self):
        """Get all spam messages."""
        query = """
        SELECT message.text 
        FROM message
        WHERE message.text LIKE '%spam: %'
        ORDER BY message.date DESC
        LIMIT 100;
        """
        return self.db_handler.execute_query(query)

    def extract_phone_number_and_modify(self, messages):
        """Extract and format phone numbers from spam messages."""
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

    def unsubscribe_by_spam_db(self, opted_out_manager: OptedOutManager):
        """Unsubscribes by numbers found in spam messages."""
        messages = self.get_spam_messages()
        modified_phone_numbers = self.extract_phone_number_and_modify(messages)
        four_digit_numbers = self.phone_processor.generate_4_digit_numbers()

        for phone_number in modified_phone_numbers:
            phone_number_list = self.phone_processor.append_numbers_to_phone(
                phone_number, four_digit_numbers
            )
            for full_phone_number in phone_number_list:
                if not opted_out_manager.is_opted_out(full_phone_number):
                    print(f"Sending STOP to {full_phone_number}")
                    self.sender.send_stop_message(full_phone_number)
                    opted_out_manager.add_opted_out(full_phone_number)
                    time.sleep(0.1)  # Add a delay to prevent spamming


def internal_cleanup(db_handler: DatabaseHandler):
    """Delete all messages from chat.db where message.text is exactly 'STOP'."""
    query = """
    DELETE FROM message
    WHERE text = 'STOP';
    """
    deleted_count = db_handler.execute_delete(query)
    print(f"Deleted {deleted_count} messages with text exactly 'STOP'.")


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
    subparsers.add_parser("cleanup", help="Clean up database")

    args = parser.parse_args()

    if not args.command:
        parser.print_usage()
        sys.exit(1)

    opted_out_manager = OptedOutManager(OPT_OUT_FILE_PATH)
    db_handler = DatabaseHandler(CHAT_DATABASE_PATH)
    phone_processor = PhoneNumberProcessor()
    sender = MessageSender(SEND_MESSAGE_SCPT)
    message_processor = MessageProcessor(db_handler, phone_processor, sender)

    if args.command == "unsubscribe":
        message_processor.unsubscribe_by_spam_db(opted_out_manager)
    elif args.command == "purge":
        message_processor.unsubscribe_by_spam_db(opted_out_manager)
    elif args.command == "cleanup":
        internal_cleanup(db_handler)

    opted_out_manager.save_opted_out_list()


if __name__ == "__main__":
    main()

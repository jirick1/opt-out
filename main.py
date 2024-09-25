import os
import re
import sqlite3
import sys
import time
import argparse

CHAT_DATABASE_PATH = "~/Library/Messages/chat.db"
OPT_OUT_FILE_PATH = "spam_list/opted_out_list.txt"
SPAM_NUMBERS_FILE = "spam_list/spam_numbers.txt"
SEND_MESSAGE_SCPT = "apple_scripts/sendMessage.scpt"


class OptedOutManager:
    """Handles the loading and saving of opted-out numbers."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.opted_out_numbers = self.load_opted_out_numbers()

    def load_opted_out_numbers(self):
        """Load the list of phone numbers that have already been sent a STOP message."""
        if not os.path.exists(self.file_path):
            return set()
        with open(self.file_path, "r") as file:
            return set(line.strip() for line in file)

    def save_opted_out_numbers(self):
        """Save the list of phone numbers that have been opted out,
        sorted in ascending order."""
        with open(self.file_path, "w") as file:
            for number in sorted(self.opted_out_numbers):
                file.write(f"{number}\n")

    def add_number(self, phone_number):
        """Add a phone number to the opted-out list."""
        self.opted_out_numbers.add(phone_number)

    def is_number_opted_out(self, phone_number):
        """Check if a phone number is already in the opted-out list."""
        return phone_number in self.opted_out_numbers


class PhoneNumberProcessor:
    """Handles phone number generation and formatting."""

    @staticmethod
    def generate_four_digit_suffixes():
        """Generate all 4-digit numbers from 0000 to 9999."""
        return [f"{i:04}" for i in range(10000)]

    @staticmethod
    def append_suffixes_to_phone_number(phone_number: str, suffixes: list[str]):
        """Create a list of phone numbers by appending each suffix
        to the original phone number."""
        return [phone_number + suffix for suffix in suffixes]

    @staticmethod
    def clean_phone_number(phone_number: str):
        """Clean and format the phone number."""
        phone_number = re.sub(r"\D", "", phone_number)  # Remove non-digit characters
        if phone_number.startswith("1") and len(phone_number) == 11:
            phone_number = phone_number[1:]  # Remove leading '1' if it's a country code
        return phone_number


class MessageSender:
    """Handles sending messages using osascript."""

    def __init__(self, script_path):
        self.script_path = script_path

    def send_stop_message(self, phone_number: str):
        """Calls the osascript to send the 'STOP' message."""
        message = "STOP"
        os.system(f'osascript {self.script_path} {phone_number} "{message}"')


class DatabaseHandler:
    """Handles database operations."""

    def __init__(self, db_path):
        self.db_path = os.path.expanduser(db_path)

    def execute_query(self, query, params=None):
        """Execute a query and return the results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or [])
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
            return []

    def execute_delete(self, query, params=None):
        """Execute a delete query and return the number of affected rows."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or [])
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
            return 0

    def get_last_messages_with_phone_numbers(self, limit=100):
        """Retrieve the last N messages along with their associated phone numbers."""
        query = """
        SELECT message.text, handle.id AS phone_number
        FROM message
        JOIN handle ON message.handle_id = handle.ROWID
        ORDER BY message.date DESC
        LIMIT ?;
        """
        return self.execute_query(query, (limit,))


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
        """Retrieve spam messages containing 'spam: <number>'."""
        query = """
        SELECT message.text 
        FROM message
        WHERE message.text LIKE '%spam: %'
        ORDER BY message.date DESC
        LIMIT 100;
        """
        return self.db_handler.execute_query(query)

    def extract_phone_numbers_from_messages(self, messages):
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

    def unsubscribe_numbers(
        self, phone_numbers: list[str], opted_out_manager: OptedOutManager
    ):
        """Unsubscribe a list of phone numbers."""
        print(f"Total number to unsubscribe from: {len(phone_numbers)}")
        four_digit_suffixes = self.phone_processor.generate_four_digit_suffixes()

        for phone_number in phone_numbers:
            full_phone_numbers = self.phone_processor.append_suffixes_to_phone_number(
                phone_number, four_digit_suffixes
            )
            for full_phone_number in full_phone_numbers:
                if not opted_out_manager.is_number_opted_out(full_phone_number):
                    print(f"Sending STOP to {full_phone_number}")
                    self.sender.send_stop_message(full_phone_number)
                    opted_out_manager.add_number(full_phone_number)
                    time.sleep(0.1)  # Add a delay to prevent spamming

    def unsubscribe_from_spam_messages(self, opted_out_manager: OptedOutManager):
        """Unsubscribe numbers extracted from spam messages."""
        messages = self.get_spam_messages()
        phone_numbers = self.extract_phone_numbers_from_messages(messages)
        self.unsubscribe_numbers(phone_numbers, opted_out_manager)

    def unsubscribe_specific_phone_number(
        self, phone_number: str, opted_out_manager: OptedOutManager
    ):
        """Unsubscribe a specific phone number."""
        self.unsubscribe_numbers([phone_number], opted_out_manager)

    def bulk_unsubscribe_from_file(
        self, file_path: str, opted_out_manager: OptedOutManager
    ):
        """Unsubscribe numbers from a file."""

        def load_spam_list_file(file_path: str):
            """Load the list of phone numbers that have
            already been sent a STOP message."""

            if not os.path.exists(file_path):
                print(
                    f"File {file_path} does not exist. \
                      \nLoading default {SPAM_NUMBERS_FILE} \n"
                )
            if not file_path or not os.path.exists(file_path):
                file_path = SPAM_NUMBERS_FILE
            with open(file_path, "r") as file:
                return set([line.strip() for line in file if line.strip()])

        phone_numbers = load_spam_list_file(file_path)
        for phone_number in phone_numbers:
            if not opted_out_manager.is_number_opted_out(phone_number):
                print(f"Sending STOP to {phone_number}")
                self.sender.send_stop_message(phone_number)
                opted_out_manager.add_number(phone_number)
                time.sleep(0.1)  # Add a delay to prevent spamming

    def unsubscribe_political_messages(self, opted_out_manager: OptedOutManager):
        """Unsubscribe numbers from messages containing
        'Text STOP to quit' and political buzz words."""
        # Get the last 100 messages with phone numbers
        messages = self.db_handler.get_last_messages_with_phone_numbers(limit=100)

        # Target phrases
        target_phrase = "Text STOP to quit"
        buzz_words = ["Democrats", "congressman", "campaign"]

        # Initialize the model
        try:
            from sentence_transformers import SentenceTransformer, util  # type: ignore
        except ImportError:
            print(
                "sentence-transformers library not installed. Please \
                  install it with 'pip install sentence-transformers'"
            )
            return

        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Compute embedding for the target phrase
        target_embedding = model.encode(target_phrase, convert_to_tensor=True)

        for message_text, phone_number in messages:
            if not message_text or not phone_number:
                continue  # Skip if any of the fields are None

            # Clean the phone number
            phone_number = self.phone_processor.clean_phone_number(phone_number)

            # Compute embedding for the message
            message_embedding = model.encode(message_text, convert_to_tensor=True)

            # Compute similarity with the target phrase
            sim_target = util.pytorch_cos_sim(message_embedding, target_embedding)

            # Define threshold
            target_threshold = 0.6  # Adjust as needed

            if sim_target.item() >= target_threshold:
                # Check if any buzz word is in the message text
                if any(
                    buzz_word.lower() in message_text.lower()
                    for buzz_word in buzz_words
                ):
                    # This message matches the criteria
                    if not opted_out_manager.is_number_opted_out(phone_number):
                        print(
                            f"Sending STOP to {phone_number} \
                              for message: {message_text}"
                        )
                        self.sender.send_stop_message(phone_number)
                        opted_out_manager.add_number(phone_number)
                        time.sleep(0.1)  # Add a delay to prevent spamming


def clean_up_database(db_handler: DatabaseHandler):
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

    # Option 1: Unsubscribe by numbers found in spam messages
    subparsers.add_parser(
        "unsubscribe", help="Unsubscribe using numbers found in spam messages"
    )

    # Option 2: Purge by phone number
    parser_purge = subparsers.add_parser("purge", help="Purge by phone number")
    parser_purge.add_argument("phone_number", help="Phone number to purge")

    # Option 3: Clean up database
    subparsers.add_parser(
        "cleanup", help="Clean up database by removing 'STOP' messages"
    )

    # Option 4: Bulk unsubscribe from file
    parser_bulk = subparsers.add_parser(
        "bulk_unsubscribe",
        help="Bulk unsubscribe using numbers from spam_numbers.txt",
    )
    parser_bulk.add_argument(
        "--file",
        default=SPAM_NUMBERS_FILE,
        help="Path to the spam numbers file (default: spam_numbers.txt)",
    )

    # Option 5: Unsubscribe political messages
    subparsers.add_parser(
        "unsubscribe_political",
        help="Unsubscribe numbers from messages containing \
          'Text STOP to quit' and political buzz words",
    )

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
        message_processor.unsubscribe_from_spam_messages(opted_out_manager)
    elif args.command == "purge":
        phone_number = args.phone_number
        message_processor.unsubscribe_specific_phone_number(
            phone_number, opted_out_manager
        )
    elif args.command == "cleanup":
        clean_up_database(db_handler)
    elif args.command == "bulk_unsubscribe":
        message_processor.bulk_unsubscribe_from_file(args.file, opted_out_manager)
    elif args.command == "unsubscribe_political":
        message_processor.unsubscribe_political_messages(opted_out_manager)

    opted_out_manager.save_opted_out_numbers()


if __name__ == "__main__":
    main()

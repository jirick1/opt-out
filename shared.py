# shared.py

import os
import re
import sqlite3

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
        SELECT m.text, m.attributedBody, h.id AS phone_number
        FROM message m
        JOIN handle h ON m.handle_id = h.ROWID
        WHERE m.service = 'SMS' AND h.country = 'us'
        ORDER BY m.date DESC
        LIMIT ?;
        """
        return self.execute_query(query, (limit,))

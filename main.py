import os
import re
import sqlite3
import sys
import time

CHAT_DATABASE_PATH = "~/Library/Messages/chat.db"
OPT_OUT_FILE_PATH = ".opted_out_list.txt"


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
    script_path = os.path.join(os.path.dirname(__file__), "sendMessage.scpt")
    message = "STOP"
    os.system(f'osascript {script_path} {phone_number} "{message}"')


def unsubscribe_by_phone_number(phone_number: str, opted_out_numbers: set):
    """Unsubscribe the phone number if not already opted out"""
    four_digit_numbers = generate_4_digit_numbers()
    phone_number_list = append_numbers_to_phone(phone_number, four_digit_numbers)

    for phone_number_with_digits in phone_number_list:
        if phone_number_with_digits not in opted_out_numbers:
            send_stop_message(phone_number_with_digits)
            opted_out_numbers.add(phone_number_with_digits)  # Add to opted-out list
            time.sleep(0.3)  # Add a 300ms delay to prevent spamming


def main():
    opted_out_numbers = load_opted_out_list()

    if len(sys.argv) == 2:
        phone_number = sys.argv[1]
        unsubscribe_by_phone_number(phone_number, opted_out_numbers)
    else:
        print("Unsubscribing by chat.db")
        spam_messages = get_spam_messages()
        modified_phone_numbers = extract_phone_number_and_modify(spam_messages)

        # Generate all 4-digit numbers
        four_digit_numbers = generate_4_digit_numbers()

        # Create a new list by appending each 4-digit \
        # number to each modified phone number
        phone_number_list = [
            phone + digits
            for phone in modified_phone_numbers
            for digits in four_digit_numbers
        ]

        # Loop through the new list of phone numbers and send the STOP message
        for phone_number in phone_number_list:
            if phone_number not in opted_out_numbers:
                print(f"Sending STOP to {phone_number}")
                send_stop_message(phone_number)
                opted_out_numbers.add(phone_number)  # Add to opted-out list
                time.sleep(0.1)  # Add a 300ms delay to prevent spamming

    # Save the opted-out numbers after the operation
    save_opted_out_list(opted_out_numbers)


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


if __name__ == "__main__":
    main()

import os
import sqlite3
import sys
import time


def generate_4_digit_numbers():
    """Generate all 4-digit numbers from 0000 to 9999"""
    numbers = [f"{i:04}" for i in range(10000)]
    return numbers


def append_numbers_to_phone(phone_number, numbers):
    """Create a list of phone numbers by appending each
    4-digit number to the original phone number."""
    phone_number_list = [phone_number + number for number in numbers]
    return phone_number_list


def send_stop_message(phone_number):
    """Calls the osascript to send the "STOP" message"""
    script_path = os.path.join(os.path.dirname(__file__), "sendMessage.scpt")
    message = "STOP"
    os.system(f'osascript {script_path} {phone_number} "{message}"')


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <phone_number>")
        sys.exit(1)

    phone_number = sys.argv[1]
    four_digit_numbers = generate_4_digit_numbers()
    phone_number_list = append_numbers_to_phone(phone_number, four_digit_numbers)

    for phone_number_with_digits in phone_number_list:
        send_stop_message(phone_number_with_digits)
        time.sleep(0.3)  # Add a 300ms delay to prevent spamming


def get_last_message_from_phone(phone_number):
    # Path to the chat database
    chat_db_path = os.path.expanduser("~/Library/Messages/chat.db")

    # Connect to the SQLite database
    conn = sqlite3.connect(chat_db_path)
    cursor = conn.cursor()

    # Query to get the last message from the specified phone number
    query = """
      SELECT text FROM message
      JOIN handle ON message.handle_id = handle.ROWID
      WHERE handle.id = ?
      ORDER BY message.date DESC
      LIMIT 1;
    """

    # Execute the query with the provided phone number
    cursor.execute(query, (phone_number,))
    last_message = cursor.fetchone()

    # Close the database connection
    conn.close()

    # Return the last message if found, otherwise return None
    if last_message:
        return last_message[0]
    else:
        return None


if __name__ == "__main__":
    # main()
    get_last_message_from_phone("17188772233")

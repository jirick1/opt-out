# options/unsubscribe.py

import time


def register_command(subparsers):
    parser = subparsers.add_parser(
        "unsubscribe",
        help="Unsubscribe using numbers found in spam messages",
    )
    parser.set_defaults(func=execute_command)


def execute_command(args, shared_objects):
    opted_out_manager = shared_objects["opted_out_manager"]
    db_handler = shared_objects["db_handler"]
    phone_processor = shared_objects["phone_processor"]
    sender = shared_objects["sender"]

    def get_spam_messages():
        """Retrieve spam messages containing 'spam: <number>'."""
        query = """
        SELECT message.text 
        FROM message
        WHERE message.text LIKE '%spam: %'
        ORDER BY message.date DESC
        LIMIT 100;
        """
        return db_handler.execute_query(query)

    def extract_phone_numbers_from_messages(messages):
        """Extract and format phone numbers from spam messages."""
        phone_numbers = []
        for message in messages:
            text = message[0]
            if "spam: " in text:
                try:
                    phone_number = text.split("spam: ")[1]
                    phone_number = phone_processor.clean_phone_number(phone_number)
                    modified_phone_number = phone_number[:-4]
                    phone_numbers.append(modified_phone_number)
                except IndexError:
                    continue
        return phone_numbers

    def unsubscribe_numbers(phone_numbers):
        """Unsubscribe a list of phone numbers."""
        print(f"Total number to unsubscribe from: {len(phone_numbers)}")
        four_digit_suffixes = phone_processor.generate_four_digit_suffixes()

        for phone_number in phone_numbers:
            full_phone_numbers = phone_processor.append_suffixes_to_phone_number(
                phone_number, four_digit_suffixes
            )
            for full_phone_number in full_phone_numbers:
                if not opted_out_manager.is_number_opted_out(full_phone_number):
                    print(f"Sending STOP to {full_phone_number}")
                    sender.send_stop_message(full_phone_number)
                    opted_out_manager.add_number(full_phone_number)
                    time.sleep(0.1)  # Add a delay to prevent spamming

    messages = get_spam_messages()
    phone_numbers = extract_phone_numbers_from_messages(messages)
    unsubscribe_numbers(phone_numbers)

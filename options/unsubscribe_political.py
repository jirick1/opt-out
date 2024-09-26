# options/unsubscribe_political.py

import time


def register_command(subparsers):
    parser = subparsers.add_parser(
        "unsubscribe_political",
        help="Unsubscribe numbers from messages containing \
          'Text STOP to quit' and political buzz words",
    )
    parser.set_defaults(func=execute_command)


def execute_command(args, shared_objects):
    opted_out_manager = shared_objects["opted_out_manager"]
    db_handler = shared_objects["db_handler"]
    phone_processor = shared_objects["phone_processor"]
    sender = shared_objects["sender"]

    # Import sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer, util  # type: ignore
    except ImportError:
        print(
            "sentence-transformers library not installed. \
              Please install it with 'pip install sentence-transformers'"
        )
        return

    def unsubscribe_political_messages():
        """Unsubscribe numbers from messages containing \
          'Text STOP to quit' and political buzz words."""
        # Get the last 100 messages with phone numbers
        messages = db_handler.get_last_messages_with_phone_numbers(limit=100)

        # Target phrases
        target_phrase = "Text STOP to quit"
        buzz_words = ["Democrats", "congressman", "campaign"]

        # Initialize the model
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Compute embedding for the target phrase
        target_embedding = model.encode(target_phrase, convert_to_tensor=True)

        for message_text, phone_number in messages:
            if not message_text or not phone_number:
                continue  # Skip if any of the fields are None

            # Clean the phone number
            phone_number = phone_processor.clean_phone_number(phone_number)

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
                        sender.send_stop_message(phone_number)
                        opted_out_manager.add_number(phone_number)
                        time.sleep(0.1)  # Add a delay to prevent spamming

    unsubscribe_political_messages()

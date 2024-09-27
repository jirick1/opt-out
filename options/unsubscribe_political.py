# options/unsubscribe_political.py

import time
import re
import ftfy


def decode_nsattributedstring(blob_data):
    """Sanitize text."""
    strings = re.findall(rb"[\x09-\x0D\x20-\x7E]{1,}", blob_data)
    decoded_strings = [s.decode("utf-8", errors="ignore") for s in strings]
    combined_text = " ".join(decoded_strings)
    unwanted_patterns = [
        r"\bstreamtyped\b",
        r"\bNSMutableAttributedString\b",
        r"\bNSAttributedString\b",
        r"\bNSObject\b",
        r"\bNSMutableString\b",
        r"\bNSString\b",
        r"\bNSDictionary\b",
        r"\b__kIMFileTransferGUIDAttributeName\b",
        r"\b__kIMMessagePartAttributeName\b",
        r"\bNSNumber\b",
        r"\bNSValue\b",
        r"\b__kIMDataDetectedAttributeName\b",
        r"\bNSData\b",
        r"\bbplist00\b",
        r"X\$versionY\$archiverT\$topX\$objects",
        r"\bNSKeyedArchiver\b",
        r"WversionYdd-result",
        r"\$\%\&,-\.259U\$null",
        r"RMSV\$classRARQTQPRSRRVN",
        r"NS\.rangeval\.length_",
        r"NS\.rangeval\.locationZNS\.special",
        r"Z\$classnameX\$classesWNSValue",
        r"XNSObject_",
        r"ZNS\.objects",
        r"WNSArray",
        r"DDScannerResult",
        r"__kIMLinkAttributeName",
        r"NSURL",
        r"ED73A1BF-04C9-4526-93C2-0830BFF907A4",
        r"\[564c\]",
        r"\[565c\]",
        r"\bI N V\b",
        r"\bI P U\b",
        r"'\\\(\*\)Z\$classnameX\$classesW",  # Escaped special characters
        # Add any other unwanted patterns here
    ]
    combined_pattern = "|".join(unwanted_patterns)
    cleaned_text = re.sub(combined_pattern, "", combined_text)
    cleaned_text = cleaned_text.strip()
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    cleaned_text = ftfy.fix_text(cleaned_text)
    return cleaned_text


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

    def unsubscribe_political_messages():
        """Unsubscribe numbers from messages containing \
          'Text STOP to quit' and political buzz words."""

        messages = db_handler.get_last_messages_with_phone_numbers(limit=100)

        buzz_words = ["Democrats", "congressman", "campaign", "DSCC"]
        for message_text, message_body, phone_number in messages:
            text = message_body or message_text
            if not text or not phone_number:
                continue
            try:
                text = decode_nsattributedstring(text)
            except Exception:
                text = None

            if not text or not text.strip():
                continue

            phone_number = phone_processor.clean_phone_number(phone_number)
            print(f"clean number: {phone_number}")
            if any(buzz_word.lower() in text.lower() for buzz_word in buzz_words):
                if not opted_out_manager.is_number_opted_out(phone_number):
                    print(
                        f"Sending STOP to {phone_number} \
                          for message: {message_text}"
                    )
                    sender.send_stop_message(phone_number)
                    opted_out_manager.add_number(phone_number)
                    time.sleep(0.1)  # Add a delay to prevent spamming

    unsubscribe_political_messages()

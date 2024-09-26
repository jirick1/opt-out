# options/purge.py


def register_command(subparsers):
    parser = subparsers.add_parser(
        "purge",
        help="Purge by phone number",
    )
    parser.add_argument("phone_number", help="Phone number to purge")
    parser.set_defaults(func=execute_command)


def execute_command(args, shared_objects):
    phone_number = args.phone_number
    opted_out_manager = shared_objects["opted_out_manager"]
    phone_processor = shared_objects["phone_processor"]
    sender = shared_objects["sender"]

    phone_number = phone_processor.clean_phone_number(phone_number)
    if not opted_out_manager.is_number_opted_out(phone_number):
        print(f"Sending STOP to {phone_number}")
        sender.send_stop_message(phone_number)
        opted_out_manager.add_number(phone_number)

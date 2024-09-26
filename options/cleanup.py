# options/cleanup.py


def register_command(subparsers):
    parser = subparsers.add_parser(
        "cleanup",
        help="Clean up database by removing 'STOP' messages",
    )
    parser.set_defaults(func=execute_command)


def execute_command(args, shared_objects):
    db_handler = shared_objects["db_handler"]

    def clean_up_database(db_handler):
        """Delete all messages from chat.db where message.text is exactly 'STOP'."""
        query = """
        DELETE FROM message
        WHERE text = 'STOP';
        """
        deleted_count = db_handler.execute_delete(query)
        print(f"Deleted {deleted_count} messages with text exactly 'STOP'.")

    clean_up_database(db_handler)

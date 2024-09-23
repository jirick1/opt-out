# Spam Message Unsubscriber Tool

This Python script automates the process of unsubscribing from spam messages by sending "STOP" messages to phone numbers extracted from your Messages database (chat.db). It can also purge specific phone numbers and clean up your database by removing "STOP" messages.

## Table of Contents

- [Requirements](#Requirements)
- [Setup](#setup)
- [Usage](#usage)
  - [Available Commands](#available-commands)
    - [unsubscribe](#unsubscribe)
    - [purge](#purge)
    - [cleanup](#cleanup)
    - [bulk_unsubscribe](#bulk_unsubscribe)

# Requirements

- Python 3.x
- macOS with the Messages app
- AppleScript capability (osascript)

# Setup

```
# Terminal

git clone https://github.com/jirick1/opt-out.git
cd opt-out
make setup
source . ./venv/bin/activate
```

# Usage

```
# Terminal

python main.py [command] [options]
```

## Available Commands

- unsubscribe: Unsubscribe using numbers found in spam messages.
- bulk_unsubscribe:
- purge: Purge by phone number.
- cleanup: Clean up the database by removing 'STOP' messages.

### unsubscribe

Unsubscribes from spam messages by extracting phone numbers from messages containing "spam: <number>" in your Messages database. Sends a "STOP" message to each number (including all possible 4-digit extensions). Keeps track of numbers already messaged to avoid duplicates.

#### Description:

- Scans the last 100 messages in your chat.db for messages containing "spam: <number>".
- Extracts the base phone numbers and appends all possible 4-digit suffixes (0000 to 9999).
- Sends a "STOP" message to each generated phone number that hasn't already been contacted.
- Updates the `opted_out_list.txt` file with the new numbers, sorted in ascending order.

#### Usage:

```
# Terminal

python main.py unsubscribe

```

### bulk_unsubscribe

Bulk unsubscribe from spam messages by reading a list of phone numbers from a file. This command sends a "STOP" message to each phone number listed in the specified file. If a phone number is already in the `opted_out_list.txt`, it will be ignored to prevent duplicate messages. After unsubscribing, the `opted_out_list.txt` file is updated with the new numbers.

#### Description:

- Reads phone numbers from the specified file (one per line).
- Sends a "STOP" message to each phone number that hasn't already been contacted.
- Updates the `opted_out_list.txt` file with the new numbers, sorted in ascending order.

#### Usage:

```
# Terminal

python main.py bulk_unsubscribe [--file <path_to_file>]

```

#### Arguments:

- file: (Optional) Path to the file containing the list of phone numbers to unsubscribe. Defaults to `spam_numbers.txt` if not specified.

### purge

Purges a specific phone number by sending a "STOP" message to it and all its possible 4-digit extensions.

#### Description:

- Sends a "STOP" message to each phone number that hasn't already been contacted.
- Updates the `opted_out_list.txt` file with the new numbers, sorted in ascending order.

#### Usage:

```
# Terminal

python main.py purge +1234567890
```

#### Arguments:

- phone_number: The base phone number to purge (without the 4-digit suffix).

### cleanup

Cleans up your Messages database by deleting all messages where the text is exactly 'STOP'.

#### Description:

- Deletes messages from the chat.db where message.text is exactly 'STOP'.
- Warning: Modifying the chat.db directly can be risky. Always back up your database before running cleanup operations.

#### Usage:

```
# Terminal

python main.py cleanup
```

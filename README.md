# Spam Message Unsubscriber Tool

This Python script automates the process of unsubscribing from spam messages by sending "STOP" messages to phone numbers extracted from your Messages database (chat.db). It can also purge specific phone numbers and clean up your database by removing "STOP" messages.

## Table of Contents

- Requirements
- Setup
- Usage
  - Available Commands
    - unsubscribe
    - purge
    - cleanup
- Example Commands

# Requirements

- Python 3.x
- macOS with the Messages app
- AppleScript capability (osascript)

# Setup

1. Clone or Download the Repository:

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
- purge: Purge by phone number.
- cleanup: Clean up the database by removing 'STOP' messages.

### unsubscribe

Unsubscribes from spam messages by extracting phone numbers from messages containing "spam: <number>" in your Messages database. Sends a "STOP" message to each number (including all possible 4-digit extensions). Keeps track of numbers already messaged to avoid duplicates.

#### Usage:

```
# Terminal

python main.py unsubscribe

```

#### Description:

- Scans the last 100 messages in your chat.db for messages containing "spam: <number>".
- Extracts the base phone numbers and appends all possible 4-digit suffixes (0000 to 9999).
- Sends a "STOP" message to each generated phone number that hasn't already been contacted.
- Updates the .opted_out_list.txt file with the new numbers, sorted in ascending order.

### purge

Purges a specific phone number by sending a "STOP" message to it and all its possible 4-digit extensions.

#### Usage:

```
# Terminal

python main.py purge <phone_number>
```

#### Arguments:

- <phone_number>: The base phone number to purge (without the 4-digit suffix).

#### Description:

- Appends all possible 4-digit suffixes to the provided phone number.
- Sends a "STOP" message to each generated phone number that hasn't already been contacted.
- Updates the .opted_out_list.txt file with the new numbers, sorted in ascending order.

#### Example:

```
# Terminal

python main.py purge +1234567890
```

### cleanup

Cleans up your Messages database by deleting all messages where the text is exactly 'STOP'.

#### Usage:

```
# Terminal

python main.py cleanup
```

#### Description:

- Deletes messages from the chat.db where message.text is exactly 'STOP'.
- Warning: Modifying the chat.db directly can be risky. Always back up your database before running cleanup operations.

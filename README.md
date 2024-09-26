# Spam Message Unsubscriber Tool

This Python script automates the process of unsubscribing from spam messages by sending "STOP" messages to phone numbers extracted from your Messages database (chat.db). It can also purge specific phone numbers and clean up your database by removing "STOP" messages.

## Table of Contents

- [Requirements](#Requirements)
- [Setup](#setup)
- [Usage](#usage)

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

usage: main.py [-h] {bulk_unsubscribe,cleanup,purge,unsubscribe,unsubscribe_political} ...

Spam Message Unsubscriber Tool

positional arguments:
  {bulk_unsubscribe,cleanup,purge,unsubscribe,unsubscribe_political}
                        Available commands
    bulk_unsubscribe    Bulk unsubscribe using numbers from a file
    cleanup             Clean up database by removing 'STOP' messages
    purge               Purge by phone number
    unsubscribe         Unsubscribe using numbers found in spam messages
    unsubscribe_political
                        Unsubscribe numbers from messages containing 'Text STOP to quit' and political buzz words

options:
  -h, --help            show this help message and exit
```

https://github.com/user-attachments/assets/62e966a5-5490-43e3-bb9b-d471af7a49f5

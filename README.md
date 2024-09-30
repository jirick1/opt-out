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

## Install Cron Job

```
make install
```

To create a cron job that runs the `unsubscribe_political` command every 3 hours, use the following command:

This will:

- Check if the virtual environment is set up.
- Add a cron job that executes the `unsubscribe_political` command every 3 hours.
- If the cron job is already installed, it will display `Already installed`.

## Uninstall Cron Job

```
make uninstall
```

To remove the cron job, use the following command:

This will:

- Check if the virtual environment is set up.
- Remove the existing cron job for the `unsubscribe_political` command.
- If the cron job is not found, it will display `No cron job found for unsubscribe_political`.

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

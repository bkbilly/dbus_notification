# DBus Notification

[![PyPI](https://img.shields.io/pypi/v/dbus-notification.svg)](https://pypi.python.org/pypi/dbus-notification)
![Python versions](https://img.shields.io/pypi/pyversions/dbus-notification.svg)
![License](https://img.shields.io/pypi/l/dbus-notification.svg)


This library provides a simple interface for creating and displaying desktop notifications with custom buttons. Please note that some features might have varying levels of support across different Linux distributions.


## Features:

 * Send notifications with custom titles, messages, and images
 * Include clickable buttons for user interaction
 * Control notification urgency, timeout, and sound
**Note:** Some features might have limited support depending on your desktop environment.


## Requirements

DBus Notification has minimal system dependencies:
* Python 3.7 or later
* `dasdbus` library

## Installation

Install the library using pip:

```bash
pip install dbus-notification
```

## Usage

This library offers two primary usage approaches:

### Command-Line Interaction

If you prefer a quick way to view information or control playback, you can potentially execute the dbus-notification script directly, though this doesn't support button actions. For more extensive programmatic control, I would recommend using the library within your Python code.

### Programmatic Control

Import the DBusNotification class from your Python code:

```python
import time
from dbus_notification import DBusNotification

def callback(notification_type, notification):
    if notification_type == "closed":
        print(f"Notification {notification["id"]} has closed.")
    elif notification_type == "button":
        print(f"Notification {notification["id"]} has clicked on the button {notification["button"]}.")

DBusNotification(appname="dbus_notification", callback=callback).send(
    title="test",
    message="this is a test message",
    logo="logo.png",
    image="myimage.png",
    sound="message-new-instant",
    actions=["Test Button"],
    urgency=1,
    timeout=100,
)

# Keep the app running
while True:
    time.sleep(1)
```

## Future Features

 * Support for notification categories
 * Resident or transient notification options
 * Ability to specify notification position on the screen

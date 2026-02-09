# DBus Notification

[![PyPI](https://img.shields.io/pypi/v/dbus-notification.svg)](https://pypi.python.org/pypi/dbus-notification)
![Python versions](https://img.shields.io/pypi/pyversions/dbus-notification.svg)
![License](https://img.shields.io/pypi/l/dbus-notification.svg)


This library provides a simple interface for creating and displaying desktop notifications with custom buttons using DBus.


## Features:

 * **Send notifications** with custom titles, messages, and images
 * **Interactive Buttons**: Include clickable buttons that trigger callbacks
 * **Urgency & Sounds**: Control urgency levels (0, 1, or 2) and trigger system sounds or file-based alerts
 * **Management**: Replace, close, or clear all notifications sent by the application
 * **Unique Tracking**: Use `uniqueid` to update specific notifications without managing raw notification IDs
**Note:** Some features might have limited support depending on your desktop environment.


## Requirements

DBus Notification has minimal system dependencies:
* Python 3.7 or later
* `jeepney` library

## Installation

Install the library using pip:

```bash
pip install dbus-notification
```

## Usage

### Command-Line Interaction

You can send quick notifications directly from your terminal using the following flags:
| Flag | Description |
| --- | --- |
| `-t`, `--title` | The bold heading of the notification. |
| `-m`, `--message` | The body text of the notification. |
| `-l`, `--logo` | Path to a small icon/logo. |
| `-i`, `--image` | Path to a large image preview. |
| `-s`, `--sound` | System sound name (e.g., `message-new-instant`) or full file path. |
| `-u`, `--urgency` | `0` (Low), `1` (Normal), or `2` (Critical). |
| `-c`, `--timeout` | Milliseconds until the notification expires (`-1` for default). |


Example:

```bash
dbus-notification -t "Hello" -m "This is a test" -u 1
```

### Programmatic Control

The `DBusNotification` class allows for advanced interaction and button callbacks.

```python
import time
from dbus_notification import DBusNotification

def callback(notification_type, notification):
    if notification_type == "closed":
        print(f"Notification {notification["id"]} has closed.")
    elif notification_type == "button":
        print(f"Notification {notification["id"]} has clicked on the button {notification["button"]}.")

dbus_app = DBusNotification(appname="dbus_notification", callback=callback)

notification_id = dbus_app.send(
    title="Initial Message",
    message="This message will be replaced in 3 seconds.",
    logo="logo.png",
    image="myimage.png",
    sound="message-new-instant",
    actions=["Test Button"],
    urgency=1,
    timeout=5000, # 5 seconds
    uniqueid="test_notification",
)
time.sleep(3)

notification_id = dbus_app.send(
    title="Updated Message",
    message="This is the new message body.",
    uniqueid="test_notification",
)
time.sleep(3)
dbus_app.close(notification_id)

dbus_app.send(title="N2", message="A second notification.")
dbus_app.send(title="N3", message="A third notification.")
time.sleep(3)

dbus_app.close_all()
```

## Future Features

 * Support for notification categories
 * Resident or transient notification options
 * Ability to specify notification position on the screen

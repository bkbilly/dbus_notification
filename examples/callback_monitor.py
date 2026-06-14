"""Long-running callback monitor for dbus_notification."""
import signal
import sys
import time
from pathlib import Path
from threading import Event

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dbus_notification import DBusNotification


stop_event = Event()


def callback(notification_type, notification):
    """Print notification callbacks."""
    print(f"{notification_type}: {notification}", flush=True)


def stop(_signum, _frame):
    """Stop the monitor."""
    stop_event.set()


def main():
    """Run the callback monitor."""
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    dbus_app = DBusNotification(appname="dbus_notification_monitor", callback=callback)
    notification_id = dbus_app.send(
        title="DBus notification callback monitor",
        message="Click a button or close this notification to check callbacks.",
        actions=["Acknowledge", "Dismiss"],
        timeout=0,
        uniqueid="callback-monitor",
    )
    print(f"Notification sent with ID {notification_id}. Press Ctrl+C to stop.", flush=True)

    while not stop_event.wait(30):
        notification_id = dbus_app.send(
            title="DBus notification callback monitor",
            message="Still running. Click a button or close this notification.",
            actions=["Acknowledge", "Dismiss"],
            timeout=0,
            uniqueid="callback-monitor",
        )
        print(f"Notification refreshed with ID {notification_id}.", flush=True)

    dbus_app.close("callback-monitor")


if __name__ == "__main__":
    main()

"""Create notifications with unique IDs and close them one by one."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dbus_notification import DBusNotification


def main():
    """Send ten notifications, then close them one at a time."""
    dbus_app = DBusNotification(appname="dbus_notification_unique_close")
    unique_ids = [f"unique-notification-{number}" for number in range(1, 11)]

    for number, uniqueid in enumerate(unique_ids, start=1):
        notification_id = dbus_app.send(
            title=f"Unique notification {number}",
            message=f"This notification has unique ID: {uniqueid}",
            timeout=0,
            uniqueid=uniqueid,
        )
        print(f"Sent {uniqueid} as notification ID {notification_id}.", flush=True)

    time.sleep(1)

    for uniqueid in unique_ids:
        dbus_app.close(uniqueid)
        print(f"Closed {uniqueid}.", flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()

"""https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html"""

import time
import logging
import threading
from gi.repository import GLib
from dasbus.connection import SessionMessageBus
from dasbus.loop import EventLoop

logger = logging.getLogger("dbus_notification")
logging.basicConfig(level=logging.ERROR)


class DBusNotification():
    """Uses DBus to send notifications"""

    def __init__(self, appname="dbus_notification", callback=None):
        self.appname = appname
        self.callback = callback

        bus = SessionMessageBus()
        self.proxy = bus.get_proxy(
            service_name="org.freedesktop.Notifications",
            object_path="/org/freedesktop/Notifications",
        )
        if callback is not None:
            self.proxy.NotificationClosed.connect(self.callback_closed)
            self.proxy.ActionInvoked.connect(self.callback_button)
            loop = EventLoop()
            threading.Thread(target=loop.run, daemon=True).start()

    def send(self,
            title="",
            message="",
            logo="",
            image=None,
            sound=None,
            actions=[],
            urgency=None,
            timeout=-1,
            notifyid=0):

        hints = {}
        if urgency is not None:
            hints["urgency"] = GLib.Variant("i", urgency)
        if image is not None:
            hints["image-path"] = GLib.Variant("s", image)
        if sound is not None:
            if  "/" in sound:
                hints["sound-file"] = GLib.Variant("s", sound)
            else:
                hints["sound-name"] = GLib.Variant("s", sound)
        actions = [num for num in actions for _ in range(2)]

        notification_id = self.proxy.Notify(
            self.appname, notifyid, logo, title, message, actions, hints, timeout
        )
        logger.debug("The notification {} was sent.".format(notification_id))

    def callback_closed(self, notification_id, reason):
        logger.debug(f"{notification_id}: The notification closed because of {reason}.")
        self.callback("closed", notification_id, reason)

    def callback_button(self, notification_id, reason):
        logger.debug(f"{notification_id}: The notification button {reason} was clicked.")
        self.callback("button", notification_id, reason)
